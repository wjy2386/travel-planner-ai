"""
体验风险评估工具
自动评估旅行体验的风险评分，提供fallback建议
"""

from langchain.tools import tool
from typing import Dict, List

@tool
def assess_experience_risk(
    experience_type: str,
    weather_dependency: str,  # "高" / "中" / "低"
    booking_required: bool,
    physical_demand: str,  # "高" / "中" / "低"
    location: str
) -> str:
    """
    评估体验的风险评分（0-100分）
    
    Args:
        experience_type: 体验类型（如"户外观景"、"室内博物馆"等）
        weather_dependency: 天气依赖度（高/中/低）
        booking_required: 是否需要预约
        physical_demand: 体力要求（高/中/低）
        location: 地点
        
    Returns:
        风险评估JSON字符串
    """
    import json
    
    # 基础风险计算
    base_score = 100
    
    # 天气影响（最关键因素）
    weather_impact = {
        "高": -35,
        "中": -15,
        "低": 0
    }
    base_score += weather_impact.get(weather_dependency, 0)
    
    # 预约风险
    if booking_required:
        base_score -= 10
    
    # 体力要求风险
    physical_impact = {
        "高": -10,
        "中": -5,
        "低": 0
    }
    base_score += physical_impact.get(physical_demand, 0)
    
    # 确保分数在0-100之间
    risk_score = max(0, min(100, base_score))
    
    # 确定风险等级
    if risk_score >= 90:
        risk_level = "低"
    elif risk_score >= 70:
        risk_level = "中"
    else:
        risk_level = "高"
    
    # 决定责任分级
    if risk_score >= 85:
        responsibility = "✅ 必达"
    elif risk_score >= 65:
        responsibility = "⚠️ 条件达成"
    else:
        responsibility = "💡 建议体验"
    
    # 生成缓解措施
    mitigation = []
    if weather_dependency == "高":
        mitigation.append("提前3天确认天气预报")
        mitigation.append("准备室内替代方案")
    if booking_required:
        mitigation.append("提前1个月预约")
    if physical_demand == "高":
        mitigation.append("提前准备体力训练")
        mitigation.append("准备急救包")
    
    # 生成fallback建议
    fallback_suggestions = {
        "户外观景": ["室内观景台", "博物馆", "城市漫步"],
        "徒步": ["缆车观光", "轻松散步", "咖啡厅休息"],
        "水上活动": ["陆地观光", "室内水上乐园", "美食体验"],
        "高空活动": ["地面观光", "室内体验", "文化探访"]
    }
    
    fallback = fallback_suggestions.get(experience_type, ["室内文化体验", "城市漫步", "特色美食"])
    
    assessment = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "responsibility": responsibility,
        "success_probability": f"{risk_score}%",
        "critical_dependencies": [
            f"天气依赖: {weather_dependency}",
            f"预约要求: {'是' if booking_required else '否'}",
            f"体力要求: {physical_demand}"
        ],
        "mitigation_measures": mitigation,
        "fallback_suggestions": fallback,
        "requires_buffer": weather_dependency == "高" or booking_required
    }
    
    return json.dumps(assessment, ensure_ascii=False, indent=2)

@tool
def generate_fallback_plan(
    original_experience: str,
    risk_factors: List[str]
) -> str:
    """
    为高风险体验生成fallback方案
    
    Args:
        original_experience: 原始体验名称
        risk_factors: 风险因素列表
        
    Returns:
        Fallback方案描述
    """
    # 根据风险类型生成不同的fallback方案
    fallback_map = {
        "天气": {
            "Plan A": "室内替代体验",
            "Plan B": "延期到备用日期",
            "Plan C": "调整行程顺序"
        },
        "预约": {
            "Plan A": "备用替代景点",
            "Plan B": "现场排队（如可能）",
            "Plan C": "提前联系旅行社加急"
        },
        "体力": {
            "Plan A": "简化版本",
            "Plan B": "使用交通工具辅助",
            "Plan C": "替换为轻松体验"
        }
    }
    
    result = f"""
【{original_experience} Fallback方案】
    
风险因素：{', '.join(risk_factors)}

推荐Fallback方案：
"""
    for risk in risk_factors:
        if "天气" in risk:
            result += f"\n- Plan A: {fallback_map['天气']['Plan A']}"
            result += f"\n- Plan B: {fallback_map['天气']['Plan B']}"
            result += f"\n- Plan C: {fallback_map['天气']['Plan C']}"
        elif "预约" in risk:
            result += f"\n- Plan A: {fallback_map['预约']['Plan A']}"
            result += f"\n- Plan B: {fallback_map['预约']['Plan B']}"
            result += f"\n- Plan C: {fallback_map['预约']['Plan C']}"
        elif "体力" in risk:
            result += f"\n- Plan A: {fallback_map['体力']['Plan A']}"
            result += f"\n- Plan B: {fallback_map['体力']['Plan B']}"
            result += f"\n- Plan C: {fallback_map['体力']['Plan C']}"
    
    return result

# 使用示例
"""
# 示例1：评估低风险体验（室内博物馆）
assess_experience_risk(
    experience_type="室内博物馆",
    weather_dependency="低",
    booking_required=False,
    physical_demand="低",
    location="东京"
)
# 返回: 风险评分90分，低风险，✅ 必达

# 示例2：评估高风险体验（高山云海观景）
assess_experience_risk(
    experience_type="户外观景",
    weather_dependency="高",
    booking_required=True,
    physical_demand="中",
    location="阿尔卑斯山"
)
# 返回: 风险评分65分，高风险，⚠️ 条件达成，需要fallback

# 示例3：生成fallback方案
generate_fallback_plan(
    original_experience="阿尔卑斯云海观景",
    risk_factors=["天气", "预约"]
)
# 返回: 详细的fallback方案（Plan A/B/C）
"""
