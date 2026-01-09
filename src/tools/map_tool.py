"""
地图API工具 - 校验地理位置、计算距离和交通时间
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def get_distance_and_time(
    runtime: ToolRuntime,
    origin: str,
    destination: str,
    mode: str = "transit"
) -> str:
    """
    计算两个地点之间的距离和交通时间。
    
    Args:
        runtime: 运行时上下文
        origin: 出发地，例如："浅草寺"、"东京站"、"新宿"
        destination: 目的地，例如："皇居"、"秋叶原"、"东京迪士尼"
        mode: 交通方式，可选："transit"（公共交通，默认）、"driving"（驾车）、"walking"（步行）
        
    Returns:
        距离和交通时间信息，包括：
        - 直线距离
        - 实际交通距离
        - 预计交通时间
        - 推荐交通方式
        - 路线概况
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.map")
        client = SearchClient(ctx=ctx)
        
        # 构建搜索查询
        mode_text = {
            "transit": "公共交通",
            "driving": "驾车",
            "walking": "步行"
        }.get(mode, "公共交通")
        
        query = f"{origin}到{destination}{mode_text}距离交通时间"
        
        # 搜索Google Maps、Yahoo!路線等
        response = client.web_search(query=query, count=5, need_summary=True)
        
        result_parts = [f"# {origin} → {destination} 交通信息\n"]
        
        # 如果有AI摘要，优先返回
        if response.summary:
            result_parts.append(f"【AI摘要】\n{response.summary}\n")
        
        # 返回搜索结果
        if response.web_items:
            result_parts.append(f"找到 {len(response.web_items)} 条路线信息：\n")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   内容: {item.snippet[:200]}...\n"
                )
        else:
            return f"未找到{origin}到{destination}的交通信息，请尝试更具体的地名。"
        
        # 添加实用建议
        result_parts.append("\n---\n**实用建议**：\n")
        result_parts.append(f"- 首次出行建议查看实时路况和公共交通时刻表\n")
        result_parts.append(f"- 高峰期（7:00-9:00，17:00-19:00）交通时间可能增加30-50%\n")
        
        if mode == "transit":
            result_parts.append(f"- 使用Suica/Pasmo卡乘坐公共交通更加便利\n")
        elif mode == "walking":
            result_parts.append(f"- 步行时建议使用地图导航避免迷路\n")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"计算交通时间失败: {str(e)}"


@tool
def check_location_validity(
    runtime: ToolRuntime,
    location: str,
    city: str
) -> str:
    """
    验证指定位置是否存在于目标城市，并获取基本信息。
    
    Args:
        runtime: 运行时上下文
        location: 位置名称，例如："浅草寺"、"秋叶原"、"东京塔"
        city: 城市名称，例如："东京"、"京都"、"大阪"
        
    Returns:
        位置验证信息，包括：
        - 是否存在
        - 具体地址
        - 开放时间（如果是景点/商店）
        - 入场费用（如果是景点）
        - 附近交通
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.location")
        client = SearchClient(ctx=ctx)
        
        # 搜索位置信息
        query = f"{city}{location}"
        response = client.web_search(query=query, count=5, need_summary=True)
        
        result_parts = [f"# {city}{location} 信息验证\n"]
        
        # 如果有AI摘要，优先返回
        if response.summary:
            result_parts.append(f"【AI摘要】\n{response.summary}\n")
        
        # 返回搜索结果
        if response.web_items:
            result_parts.append(f"找到 {len(response.web_items)} 条相关信息：\n")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   内容: {item.snippet[:200]}...\n"
                )
            
            result_parts.append("\n---\n**验证结果**：✅ 位置存在\n")
            result_parts.append(f"建议查看详细信息获取准确的开放时间和入场费用。")
        else:
            result_parts.append("\n---\n**验证结果**：❌ 未找到该位置\n")
            result_parts.append(f"可能原因：\n")
            result_parts.append(f"- 位置名称不完整或不准确\n")
            result_parts.append(f"- 该位置不在{city}市内\n")
            result_parts.append(f"- 建议使用更具体的名称或尝试搜索附近地标")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"验证位置失败: {str(e)}"


@tool
def find_nearby_locations(
    runtime: ToolRuntime,
    base_location: str,
    location_type: str,
    city: str = "东京",
    radius: str = "1km"
) -> str:
    """
    查找指定位置附近的特定类型地点。
    
    Args:
        runtime: 运行时上下文
        base_location: 基准位置，例如："浅草寺"、"东京站"
        location_type: 地点类型，例如："餐厅"、"酒店"、"地铁站"、"便利店"
        city: 城市名称，默认"东京"
        radius: 搜索半径，例如："1km"、"500m"，默认"1km"
        
    Returns:
        附近地点列表，包括：
        - 地点名称
        - 距离
        - 评分（如有）
        - 简介
    """
    try:
        # 创建搜索客户端
        ctx = new_context(method="search.nearby")
        client = SearchClient(ctx=ctx)
        
        # 搜索附近地点
        query = f"{city}{base_location}附近{radius}{location_type}"
        response = client.web_search(query=query, count=5, need_summary=True)
        
        result_parts = [f"# {base_location} 附近 {radius} {location_type}\n"]
        
        # 如果有AI摘要，优先返回
        if response.summary:
            result_parts.append(f"【AI摘要】\n{response.summary}\n")
        
        # 返回搜索结果
        if response.web_items:
            result_parts.append(f"找到 {len(response.web_items)} 个{location_type}：\n")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   内容: {item.snippet[:200]}...\n"
                )
        else:
            result_parts.append(f"未找到{base_location}附近{radius}的{location_type}。")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"查找附近地点失败: {str(e)}"
