"""
用户层级识别工具
自动识别高端用户需求，触发产品经理模式
"""

from langchain.tools import tool
from typing import Literal

# 高端用户关键词
PREMIUM_KEYWORDS = [
    "史诗", "诗篇", "传世",
    "体验结构",
    "独家", "私人", "定制",
    "奢华", "高端",
    "隐秘", "秘境",
    "极致", "独特",
    "一生必去", "顶配",
    "VIP", "专属"
]

@tool
def detect_user_tier(user_input: str) -> str:
    """
    检测用户层级，判断是否进入高端产品经理模式
    
    Args:
        user_input: 用户的自然语言输入
        
    Returns:
        "premium" - 高端用户（触发产品经理模式）
        "standard" - 标准用户
    """
    if not user_input:
        return "standard"
    
    # 转换为小写进行匹配
    user_input_lower = user_input.lower()
    
    # 统计匹配的关键词数量
    matched_keywords = [kw for kw in PREMIUM_KEYWORDS if kw.lower() in user_input_lower]
    
    # 触发条件：关键词数量 >= 2
    if len(matched_keywords) >= 2:
        return f"premium (matched: {matched_keywords})"
    
    return "standard"

@tool
def get_premium_mode_config() -> str:
    """
    获取高端模式配置
    
    Returns:
        高端模式的配置说明
    """
    return """
    【高端产品经理模式已激活】
    
    模式特征：
    - 体验更小众、更独特
    - 责任分级更严格（必达体验更多）
    - 风险评估更详细
    - 提供更多fallback方案
    - 对外语言更诗性
    - 推荐强体验版方案
    """

# 使用示例
"""
# 示例1：标准用户
detect_user_tier("我想去东京旅游3天")
# 返回: "standard"

# 示例2：高端用户
detect_user_tier("我想要一个史诗级的阿尔卑斯之旅，体验独特的秘境和定制服务")
# 返回: "premium (matched: ['史诗', '独特', '秘境', '定制'])"

# 示例3：接近高端
detect_user_tier("我想要一个高端的旅行体验")
# 返回: "standard" (只有1个关键词，未达到2个)
"""
