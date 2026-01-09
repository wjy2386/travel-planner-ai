"""
酒店/票务API工具 - 实时查询库存和价格
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def search_hotels(
    runtime: ToolRuntime,
    city: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 2,
    room_type: str = "",
    budget: str = ""
) -> str:
    """
    搜索指定城市的酒店，获取实时库存和价格信息。
    
    Args:
        runtime: 运行时上下文
        city: 城市名称，例如："东京"、"京都"、"大阪"
        check_in_date: 入住日期，格式：YYYY-MM-DD，例如："2025-04-01"
        check_out_date: 退房日期，格式：YYYY-MM-DD，例如："2025-04-05"
        guests: 客人数量，默认2人
        room_type: 房间类型偏好，例如："商务"、"家庭"、"豪华"、"经济型"
        budget: 预算范围，例如："500-1000元"、"1000-2000元"
        
    Returns:
        酒店搜索结果，包括：
        - 酒店名称
        - 位置
        - 价格
        - 评分
        - 可用性
        - 设施
        - 附近交通
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.hotel")
        client = SearchClient(ctx=ctx)
        
        # 构建搜索查询
        query_parts = [city, "酒店", check_in_date, f"{guests}人"]
        
        if room_type:
            query_parts.append(room_type)
        
        if budget:
            query_parts.append(f"预算{budget}")
        
        query = " ".join(query_parts)
        
        # 搜索多个酒店预订平台
        queries = [
            query,
            f"{city}{check_in_date}住宿推荐",
            f"{city}{check_in_date}Booking.com",
        ]
        
        all_results = []
        for search_query in queries:
            response = client.web_search(query=search_query, count=3, need_summary=True)
            
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
            return f"未找到{city}{check_in_date}至{check_out_date}的酒店信息，请尝试其他日期或调整搜索条件。"
        
        # 格式化输出
        result = f"# {city} 酒店 ({check_in_date} 至 {check_out_date}, {guests}人)\n\n"
        
        if room_type:
            result += f"**房间类型**: {room_type}\n"
        
        if budget:
            result += f"**预算**: {budget}\n"
        
        result += "\n## 搜索结果\n\n"
        result += "\n".join(all_results[:10])  # 限制返回数量
        
        # 添加实用建议
        result += "\n\n---\n**实用建议**：\n"
        result += "- 建议提前预订，特别是在樱花季、红叶季等旺季\n"
        result += "- 建议选择交通便利的酒店，靠近地铁站或JR站\n"
        result += "- 确认酒店是否提供免费Wi-Fi和早餐\n"
        result += "- 注意取消政策，建议选择可免费取消的房型\n"
        
        return result
        
    except Exception as e:
        return f"搜索酒店失败: {str(e)}"


@tool
def search_tickets(
    runtime: ToolRuntime,
    attraction_name: str,
    city: str,
    visit_date: str,
    visitors: int = 2,
    ticket_type: str = ""
) -> str:
    """
    搜索景点门票、交通票务等信息。
    
    Args:
        runtime: 运行时上下文
        attraction_name: 景点名称，例如："迪士尼乐园"、"环球影城"、"浅草寺"
        city: 城市名称，例如："东京"、"大阪"、"京都"
        visit_date: 参观日期，格式：YYYY-MM-DD，例如："2025-04-01"
        visitors: 参观人数，默认2人
        ticket_type: 票务类型，例如："快速通行证"、"一日票"、"两日票"
        
    Returns:
        票务搜索结果，包括：
        - 票务类型和价格
        - 可用性
        - 购买渠道
        - 预约要求
        - 入场时间限制
        - 优惠政策
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.ticket")
        client = SearchClient(ctx=ctx)
        
        # 构建搜索查询
        query_parts = [city, attraction_name, visit_date, "门票", f"{visitors}人"]
        
        if ticket_type:
            query_parts.append(ticket_type)
        
        query = " ".join(query_parts)
        
        # 搜索多个票务平台
        queries = [
            query,
            f"{city}{attraction_name}门票价格",
            f"{city}{attraction_name}官方网站",
            f"{city}{attraction_name}Klook",
        ]
        
        all_results = []
        for search_query in queries:
            response = client.web_search(query=search_query, count=3, need_summary=True)
            
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
            return f"未找到{city}{attraction_name}{visit_date}的票务信息，请尝试其他日期或景点。"
        
        # 格式化输出
        result = f"# {city}{attraction_name} 票务信息 ({visit_date}, {visitors}人)\n\n"
        
        if ticket_type:
            result += f"**票务类型**: {ticket_type}\n"
        
        result += "\n## 搜索结果\n\n"
        result += "\n".join(all_results[:10])  # 限制返回数量
        
        # 添加实用建议
        result += "\n\n---\n**实用建议**：\n"
        result += "- 热门景点建议提前预订，特别是周末和节假日\n"
        result += "- 建议通过官方渠道或正规票务平台购买，避免黄牛\n"
        result += "- 确认票务是否支持改期或退款\n"
        result += "- 保存电子票或预约确认邮件，入场时可能需要出示\n"
        
        return result
        
    except Exception as e:
        return f"搜索票务失败: {str(e)}"
