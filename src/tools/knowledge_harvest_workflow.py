"""
知识采集工作流 - 完整的5步流程

Step 1: 官网入口识别
Step 2: 页面读取
Step 3: 结构化解析
Step 4: 校验 & 入库
Step 5: 索引（待实现）
"""

import json
import time
from typing import Dict, Any, List, Optional
from tools.page_reader_tool import extract_webpage_content, discover_website_structure
from agents.knowledge_harvester_agent import build_harvester_agent, parse_with_schema
from storage.knowledge_validator import validate_data
from storage.knowledge_storage import KnowledgeStorage


class KnowledgeHarvestWorkflow:
    """知识采集工作流"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化工作流
        
        Args:
            database_url: 数据库连接URL
        """
        self.storage = KnowledgeStorage(database_url)
        self.agent = build_harvester_agent()
    
    def run_single_url(
        self,
        url: str,
        schema_type: str,
        destination: str = ""
    ) -> Dict[str, Any]:
        """
        采集单个URL的知识
        
        Args:
            url: 网页URL
            schema_type: Schema类型（attraction/accommodation/restaurant/transport/activity）
            destination: 目的地名称
        
        Returns:
            采集结果
        """
        print(f"\n{'='*60}")
        print(f"开始采集: {url}")
        print(f"Schema类型: {schema_type}")
        print(f"目的地: {destination}")
        print(f"{'='*60}")
        
        result = {
            "url": url,
            "schema_type": schema_type,
            "destination": destination,
            "status": "success",
            "steps": []
        }
        
        # Step 1: 页面读取
        print("\n[Step 1] 页面读取...")
        try:
            tool_result = extract_webpage_content.func(url, None)
            if "skip" in tool_result:
                result["status"] = "failed"
                result["error"] = "页面读取失败"
                return result
            
            content_data = json.loads(tool_result)
            page_content = content_data.get("content", "")
            metadata = content_data.get("metadata", {})
            
            print(f"  ✓ 提取到 {len(page_content)} 字符的内容")
            print(f"  ✓ 标题: {metadata.get('title', '')}")
            print(f"  ✓ 发布机构: {metadata.get('publisher', '')}")
            
            result["steps"].append({
                "step": 1,
                "name": "页面读取",
                "status": "success",
                "content_length": len(page_content)
            })
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"页面读取异常: {str(e)}"
            return result
        
        # Step 2: 结构化解析
        print("\n[Step 2] 结构化解析...")
        try:
            parsed_data = parse_with_schema(self.agent, url, schema_type, page_content)
            
            if parsed_data.get("status") == "skip":
                result["status"] = "failed"
                result["error"] = f"解析跳过: {parsed_data.get('reason', '')}"
                return result
            
            print(f"  ✓ 解析成功")
            print(f"  ✓ 名称: {parsed_data.get('name', '')}")
            print(f"  ✓ 描述: {parsed_data.get('description', '')[:50]}...")
            
            # 补充destination（如果未提供）
            if not parsed_data.get('destination'):
                parsed_data['destination'] = destination
            
            result["steps"].append({
                "step": 2,
                "name": "结构化解析",
                "status": "success",
                "parsed_name": parsed_data.get('name', '')
            })
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"解析异常: {str(e)}"
            return result
        
        # Step 3: 数据校验
        print("\n[Step 3] 数据校验...")
        try:
            is_valid, errors, needs_review = validate_data(parsed_data)
            
            if is_valid:
                print(f"  ✓ 校验通过")
            else:
                print(f"  ⚠ 校验发现 {len(errors)} 个问题:")
                for error in errors:
                    print(f"    - {error}")
            
            if needs_review:
                print(f"  ⚠ 标记为需要人工审核")
            
            result["steps"].append({
                "step": 3,
                "name": "数据校验",
                "status": "success" if is_valid else "warning",
                "is_valid": is_valid,
                "errors_count": len(errors),
                "needs_review": needs_review
            })
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"校验异常: {str(e)}"
            return result
        
        # Step 4: 入库
        print("\n[Step 4] 入库...")
        try:
            save_result = self.storage.save(parsed_data, needs_review, errors)
            
            if save_result["status"] == "created":
                print(f"  ✓ 创建新记录")
                print(f"  ✓ 文档ID: {save_result['doc_id']}")
            elif save_result["status"] == "updated":
                print(f"  ✓ 更新现有记录")
                print(f"  ✓ 文档ID: {save_result['doc_id']}")
                print(f"  ✓ 版本: {save_result['version']}")
            else:
                print(f"  ✗ 入库失败: {save_result.get('error', '')}")
                result["status"] = "failed"
                result["error"] = save_result.get('error', '')
                return result
            
            result["steps"].append({
                "step": 4,
                "name": "入库",
                "status": save_result["status"],
                "doc_id": save_result.get("doc_id"),
                "version": save_result.get("version")
            })
            
            result["doc_id"] = save_result.get("doc_id")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"入库异常: {str(e)}"
            return result
        
        # 完成
        print(f"\n{'='*60}")
        print(f"采集完成: {parsed_data.get('name', '')}")
        print(f"{'='*60}")
        
        return result
    
    def run_batch(
        self,
        tasks: List[Dict[str, str]],
        delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        批量采集
        
        Args:
            tasks: 任务列表，每个任务包含url、schema_type、destination
            delay: 每个任务之间的延迟（秒）
        
        Returns:
            采集结果列表
        """
        print(f"\n{'█'*60}")
        print(f"批量知识采集")
        print(f"{'█'*60}")
        print(f"任务数量: {len(tasks)}")
        print(f"延迟间隔: {delay}秒")
        
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n\n{'█'*60}")
            print(f"任务 {i}/{len(tasks)}")
            print(f"{'█'*60}")
            
            result = self.run_single_url(
                url=task["url"],
                schema_type=task["schema_type"],
                destination=task.get("destination", "")
            )
            
            results.append(result)
            
            # 延迟
            if i < len(tasks):
                print(f"\n等待 {delay} 秒后继续...")
                time.sleep(delay)
        
        # 统计
        self._print_statistics(results)
        
        return results
    
    def discover_and_harvest(
        self,
        base_url: str,
        schema_type: str,
        destination: str,
        max_urls: int = 20
    ) -> List[Dict[str, Any]]:
        """
        自动发现并采集
        
        Args:
            base_url: 网站首页URL
            schema_type: Schema类型
            destination: 目的地名称
            max_urls: 最大采集数量
        
        Returns:
            采集结果列表
        """
        print(f"\n{'█'*60}")
        print(f"自动发现并采集")
        print(f"{'█'*60}")
        print(f"基础URL: {base_url}")
        print(f"Schema类型: {schema_type}")
        print(f"目的地: {destination}")
        print(f"最大数量: {max_urls}")
        
        # Step 1: 发现网站结构
        print("\n[Step 1] 发现网站结构...")
        try:
            structure_result = discover_website_structure.func(base_url, None)
            if "skip" in structure_result:
                print(f"  ✗ 网站结构发现失败")
                return []
            
            structure_data = json.loads(structure_result)
            nav_urls = structure_data.get("navigation_urls", [])
            
            print(f"  ✓ 发现 {len(nav_urls)} 个导航链接")
            
        except Exception as e:
            print(f"  ✗ 发现异常: {str(e)}")
            return []
        
        # Step 2: 构建任务列表
        tasks = []
        for url_info in nav_urls[:max_urls]:
            tasks.append({
                "url": url_info["url"],
                "schema_type": schema_type,
                "destination": destination
            })
        
        # Step 3: 批量采集
        results = self.run_batch(tasks, delay=2.0)
        
        return results
    
    def _print_statistics(self, results: List[Dict[str, Any]]) -> None:
        """打印统计信息"""
        print(f"\n\n{'█'*60}")
        print(f"采集统计")
        print(f"{'█'*60}")
        
        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "failed")
        
        print(f"总任务数: {total}")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        print(f"成功率: {success/total*100:.1f}%" if total > 0 else "成功率: 0%")
        
        if failed > 0:
            print(f"\n失败任务:")
            for i, result in enumerate(results, 1):
                if result["status"] == "failed":
                    print(f"  {i}. {result['url']}")
                    print(f"     原因: {result.get('error', 'Unknown')}")


# 使用示例
def example_usage():
    """使用示例"""
    
    # 初始化工作流
    workflow = KnowledgeHarvestWorkflow()
    
    # 示例1: 采集单个景点
    print("\n" + "="*60)
    print("示例1: 采集单个景点")
    print("="*60)
    
    result = workflow.run_single_url(
        url="https://www.gotokyo.org/jp/spot/evt41/index.html",
        schema_type="attraction",
        destination="东京"
    )
    
    # 示例2: 批量采集
    print("\n" + "="*60)
    print("示例2: 批量采集")
    print("="*60)
    
    tasks = [
        {"url": "https://www.kinkakuji.or.jp/", "schema_type": "attraction", "destination": "京都"},
        {"url": "https://www.kiyomizuyera.or.jp/", "schema_type": "attraction", "destination": "京都"}
    ]
    
    results = workflow.run_batch(tasks, delay=3.0)
    
    # 示例3: 自动发现并采集
    # print("\n" + "="*60)
    # print("示例3: 自动发现并采集")
    # print("="*60)
    # 
    # results = workflow.discover_and_harvest(
    #     base_url="https://kyoto.travel/",
    #     schema_type="attraction",
    #     destination="京都",
    #     max_urls=10
    # )


if __name__ == "__main__":
    example_usage()
