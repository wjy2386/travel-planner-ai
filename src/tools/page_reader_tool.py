"""
页面读取工具 - 从网页提取正文内容

职责：
- 打开页面
- 提取正文（去广告、去footer等噪音）
- 输出纯文本 + 元信息
- 不做总结，不做结构化
"""

import re
from typing import Dict, Any, Optional
from langchain.tools import tool, ToolRuntime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import html2text


@tool
def extract_webpage_content(url: str, runtime: ToolRuntime = None) -> str:
    """
    从网页提取正文内容
    
    严格按照"只提取，不总结"原则，返回纯净的网页文本内容。
    
    职责：
    - 打开指定URL
    - 提取网页正文（去除广告、导航栏、footer等噪音）
    - 返回纯文本内容
    - 输出包含元信息（标题、URL、发布机构等）
    
    Args:
        url: 要提取的网页URL
        runtime: ToolRuntime上下文
    
    Returns:
        JSON格式的字符串，包含网页内容和元信息
    """
    try:
        # 1. 获取网页内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # 2. 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. 提取元信息
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # 提取description meta
        description = soup.find('meta', attrs={'name': 'description'})
        description_text = description.get('content', '') if description else ""
        
        # 提取发布机构（从URL或HTML推断）
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        publisher = domain
        
        # 尝试从HTML中提取更准确的发布机构
        org_tag = soup.find('meta', attrs={'name': 'organization'})
        if org_tag:
            publisher = org_tag.get('content', publisher)
        
        # 4. 去除噪音元素
        noise_selectors = [
            'script', 'style', 'nav', 'header', 'footer',
            'aside', '.advertisement', '.ads', '.sidebar',
            '.cookie-banner', '.popup', '.modal', 'iframe'
        ]
        
        for selector in noise_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # 5. 提取主要内容
        # 优先提取文章内容、主内容区域
        content_selectors = [
            'article', 'main', '.content', '.article-body',
            '.post-content', '.entry-content', '#main-content',
            '[role="main"]', '.text-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element
                break
        
        # 如果没有找到主要内容区域，使用body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return '{"status": "skip", "reason": "无法提取网页内容"}'
        
        # 6. 转换为纯文本
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0  # 不自动换行
        
        raw_text = h.handle(str(main_content))
        
        # 7. 清理文本
        # 移除多余空白行
        cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', raw_text)
        cleaned_text = cleaned_text.strip()
        
        # 限制文本长度（避免过大）
        max_length = 100000  # 10万字符
        if len(cleaned_text) > max_length:
            cleaned_text = cleaned_text[:max_length] + "\n\n[内容已截断...]"
        
        # 8. 检查是否有有效内容
        if len(cleaned_text) < 100:
            return '{"status": "skip", "reason": "提取的内容过少，可能不是有效页面"}'
        
        # 9. 构建返回结果
        result = {
            "status": "success",
            "metadata": {
                "url": url,
                "title": title_text,
                "description": description_text,
                "publisher": publisher,
                "domain": domain,
                "content_length": len(cleaned_text)
            },
            "content": cleaned_text
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except requests.RequestException as e:
        return f'{{"status": "skip", "reason": "网络请求失败: {str(e)}"}}'
    except Exception as e:
        return f'{{"status": "skip", "reason": "内容提取失败: {str(e)}"}}'


@tool
def discover_website_structure(url: str, runtime: ToolRuntime = None) -> str:
    """
    发现网站结构，识别官网入口和导航结构
    
    职责：
    - 找官方入口
    - 找sitemap/导航结构
    - 输出可抓取URL列表
    
    Args:
        url: 网站首页URL
        runtime: ToolRuntime上下文
    
    Returns:
        JSON格式的字符串，包含网站结构信息
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取导航链接
        nav_urls = []
        
        # 查找导航栏
        nav_selectors = ['nav', '.nav', '.navigation', '.menu', '[role="navigation"]']
        
        for selector in nav_selectors:
            nav_element = soup.select_one(selector)
            if nav_element:
                links = nav_element.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # 确保href是字符串
                    if not isinstance(href, str):
                        continue
                    
                    # 补全相对URL
                    if href.startswith('/'):
                        parsed_url = urlparse(url)
                        href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                    elif not href.startswith('http'):
                        continue
                    
                    # 过滤掉非同域链接
                    if urlparse(href).netloc != urlparse(url).netloc:
                        continue
                    
                    nav_urls.append({
                        "url": href,
                        "text": text,
                        "category": "navigation"
                    })
        
        # 查找sitemap
        sitemap_urls = []
        sitemap_link = soup.find('link', rel='sitemap')
        if sitemap_link:
            sitemap_urls.append(sitemap_link['href'])
        
        # 尝试常见的sitemap路径
        common_sitemap_paths = ['/sitemap.xml', '/sitemap_index.xml']
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in common_sitemap_paths:
            try:
                sitemap_response = requests.get(base_url + path, timeout=10)
                if sitemap_response.status_code == 200:
                    sitemap_urls.append(base_url + path)
            except:
                pass
        
        # 限制返回的URL数量
        nav_urls = nav_urls[:50]
        
        result = {
            "status": "success",
            "base_url": url,
            "domain": urlparse(url).netloc,
            "navigation_urls": nav_urls,
            "sitemap_urls": sitemap_urls,
            "total_urls": len(nav_urls)
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f'{{"status": "skip", "reason": "网站结构发现失败: {str(e)}"}}'
