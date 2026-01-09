"""
联网搜索工具 - 用于获取实时信息
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import List, Optional


@tool
def web_search_tool(
    runtime: ToolRuntime,
    query: str,
    search_type: str = "web",
    count: int = 5
) -> str:
    """
    执行网络搜索，获取实时信息。
    
    Args:
        runtime: 运行时上下文
        query: 搜索关键词，例如："东京4月1日天气"、"浅草寺开放时间"
        search_type: 搜索类型，可选："web"（基础搜索）、"web_summary"（含AI摘要）、"image"（图片搜索），默认为"web"
        count: 返回结果数量，默认为5
        
    Returns:
        搜索结果的文本描述，包含标题、来源、摘要等信息
    """
    try:
        # 创建上下文和客户端
        ctx = new_context(method="search.web")
        client = SearchClient(ctx=ctx)
        
        # 执行搜索
        if search_type == "web":
            response = client.web_search(query=query, count=count, need_summary=True)
        elif search_type == "web_summary":
            response = client.web_search_with_summary(query=query, count=count)
        elif search_type == "image":
            response = client.image_search(query=query, count=count)
        else:
            return f"不支持的搜索类型: {search_type}，可选值: web, web_summary, image"
        
        # 格式化返回结果
        result_parts = []
        
        # 如果有AI摘要，优先返回
        if response.summary:
            result_parts.append(f"【AI摘要】\n{response.summary}\n")
        
        # 返回搜索结果
        if response.web_items:
            result_parts.append(f"找到 {len(response.web_items)} 条相关结果：\n")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   URL: {item.url}\n"
                    f"   摘要: {item.snippet[:200]}...\n"
                )
        elif response.image_items:
            result_parts.append(f"找到 {len(response.image_items)} 张图片：\n")
            for i, item in enumerate(response.image_items, 1):
                result_parts.append(
                    f"{i}. {item.title or '无标题'}\n"
                    f"   来源: {item.site_name}\n"
                    f"   图片URL: {item.image.url}\n"
                    f"   尺寸: {item.image.width}x{item.image.height}\n"
                )
        else:
            return f"未找到相关结果，请尝试其他关键词"
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"搜索失败: {str(e)}"


# 使用示例（仅供参考，不会被调用）
if __name__ == "__main__":
    # 测试工具
    class MockRuntime:
        context = new_context(method="test")
    
    result = web_search_tool(
        query="东京4月1日天气",
        search_type="web",
        count=3,
        runtime=MockRuntime()
    )
    print(result)
