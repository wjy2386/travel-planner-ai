"""
天气API工具 - 获取精准的天气预报和预警
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def get_weather_forecast(
    runtime: ToolRuntime,
    city: str,
    date: str
) -> str:
    """
    获取指定城市和日期的天气预报和预警信息。
    
    Args:
        runtime: 运行时上下文
        city: 城市名称，例如："东京"、"京都"、"大阪"
        date: 日期，格式：YYYY-MM-DD，例如："2025-04-01"
        
    Returns:
        天气预报信息，包括：
        - 气温（最低/最高）
        - 天气状况（晴/多云/雨/雪等）
        - 降雨概率
        - 风力风向
        - 空气质量
        - 极端天气预警（如有）
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.weather")
        client = SearchClient(ctx=ctx)
        
        # 搜索多个天气信息源
        queries = [
            f"{city}{date}天气预报",
            f"{city}{date}日本气象厅",
            f"{city}{date}Weather.com",
        ]
        
        all_results = []
        for query in queries:
            response = client.web_search(query=query, count=3, need_summary=True)
            
            # 优先返回AI摘要
            if response.summary:
                all_results.append(f"【AI摘要】{response.summary}")
            
            # 返回搜索结果
            if response.web_items:
                for item in response.web_items:
                    all_results.append(
                        f"- {item.title}\n"
                        f"  来源: {item.site_name}\n"
                        f"  内容: {item.snippet[:200]}..."
                    )
        
        if not all_results:
            return f"未找到{city}{date}的天气预报信息，请尝试其他日期或城市。"
        
        # 格式化输出
        result = f"# {city} {date} 天气预报\n\n"
        result += "\n".join(all_results[:10])  # 限制返回数量
        
        # 添加实用建议
        result += "\n\n---\n**实用建议**：\n"
        result += "- 出发前1-3天再次查询，以获取最新预报\n"
        result += "- 如遇极端天气，请及时调整行程\n"
        result += "- 建议下载当地气象厅APP或关注官方预警\n"
        
        return result
        
    except Exception as e:
        return f"获取天气预报失败: {str(e)}"


@tool
def get_weather_alerts(
    runtime: ToolRuntime,
    city: str,
    days: int = 7
) -> str:
    """
    获取指定城市未来几天的天气预警信息。
    
    Args:
        runtime: 运行时上下文
        city: 城市名称，例如："东京"、"京都"、"大阪"
        days: 查询未来几天的预警，默认7天
        
    Returns:
        天气预警信息，包括：
        - 极端天气预警（台风、暴雨、暴雪等）
        - 气温异常（高温、寒潮）
        - 预警级别（注意、警戒、特别警戒）
        - 预警时间范围
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.weather_alert")
        client = SearchClient(ctx=ctx)
        
        # 搜索天气预警
        query = f"{city}未来{days}天天气预警"
        response = client.web_search(query=query, count=5, need_summary=True)
        
        result_parts = []
        
        # 如果有AI摘要，优先返回
        if response.summary:
            result_parts.append(f"【AI摘要】\n{response.summary}\n")
        
        # 返回搜索结果
        if response.web_items:
            result_parts.append(f"找到 {len(response.web_items)} 条预警信息：\n")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   内容: {item.snippet[:200]}...\n"
                )
        else:
            result_parts.append(f"未来{days}天暂无天气预警信息。")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"获取天气预警失败: {str(e)}"
