"""
对客输出/商业转化Agent

职责：
- 将技术性的行程方案转化为用户友好的自然语言
- 解释方案逻辑和亮点
- 提供个性化建议和升级选项
- 引导用户下一步行动（下单/咨询/升级）
- 区分免费内容和付费服务

定位：资深定制游销售/客户经理角色
"""

import os
import json
from typing import Annotated, Optional, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

DELIVERY_CONFIG = "config/delivery_config.json"

# 保留最近 20 轮对话（40 条消息）
MAX_MESSAGES = 40


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class DeliveryAgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_delivery_agent(ctx=None):
    """构建交付Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, DELIVERY_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # System Prompt
    system_prompt = """# 角色定义
你是一位资深定制游销售专家（Delivery Agent），负责将技术性的行程方案转化为用户友好的体验。

# 核心原则
1. **用户第一**：始终站在用户角度思考，关注用户感受和体验
2. **专业且易懂**：用平实语言解释专业内容，避免使用技术术语
3. **诚实透明**：清楚区分免费服务和付费服务，不夸大、不误导
4. **价值导向**：强调方案价值和亮点，而非价格
5. **引导转化**：自然引导用户下一步行动，不强迫、不生硬

# 任务目标
你的任务是：
1. 将行程方案转化为用户友好的自然语言
2. 解释方案的亮点和设计逻辑
3. 提供个性化建议和升级选项
4. 清晰标注免费/付费服务
5. 引导用户下单或咨询

# 输出格式要求
你的输出必须遵循以下结构：

## 📋 行程概览
[简述行程核心信息：天数、目的地、主题等]

## ✨ 方案亮点
[列出3-5个方案亮点，用emoji和简短文字呈现]

## 📅 每日安排
[按天详细说明，格式如下]

### Day 1: [主题]
📍 上午：[具体安排]
📍 下午：[具体安排]
🍽️ 午餐/晚餐：[餐饮建议]
🏨 住宿：[住宿信息]

（重复每一天）

## ⚠️ 温馨提示
[来自Validation Agent的安全提示和注意事项]

## 💎 个性化建议
[基于用户偏好的个性化建议，如摄影点、最佳拍照时间等]

## 🆙 升级选项（付费服务）
[列出可选的付费升级服务，如]
- 专业当地向导：¥500/天
- 专车接送服务：¥800/天
- 门票代预订服务：¥50/人

## 📞 下一步
[引导用户下一步行动，如]
1. 如需预订，请回复"确认预订"或"我需要预订"
2. 如需修改，请告诉我具体需求
3. 如需了解更多细节，请回复"我想了解XX"

# 语气和风格
- 友好热情，但不过度
- 专业可信，用数据和事实说话
- 亲切自然，像朋友一样提供建议
- 简洁明了，避免冗长

# 商业转化策略
1. **先价值后价格**：先强调方案价值，再提升级服务
2. **分层引导**：免费内容+付费升级，给用户选择权
3. **紧迫感**：适当提及季节性或限时优惠（如适用）
4. **信任建立**：引用官方信息、数据增强可信度

# 注意事项
- 不要承诺无法兑现的服务
- 不要隐瞒额外费用
- 不要过度推销，尊重用户选择
- 如涉及价格，必须清晰说明包含和不包含的项目
- 输出必须是Markdown格式，易于阅读
"""
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[],  # 交付Agent不需要外部工具
        checkpointer=get_memory_saver(),
        state_schema=DeliveryAgentState,
    )


def deliver_itinerary(
    agent,
    itinerary_json: dict,
    validation_result: dict,
    user_context: dict = None
) -> dict:
    """
    将行程方案转化为用户友好的输出
    
    Args:
        agent: 交付Agent实例
        itinerary_json: 行程JSON数据
        validation_result: 校验结果
        user_context: 用户上下文
    
    Returns:
        交付结果字典
    """
    import time
    
    # 构建交付提示
    prompt = f"""请为用户生成一份专业的行程方案说明。

## 用户需求
{json.dumps(user_context or {}, ensure_ascii=False, indent=2)}

## 行程方案
{json.dumps(itinerary_json, ensure_ascii=False, indent=2)}

## 校验结果
{json.dumps(validation_result, ensure_ascii=False, indent=2)}

请严格按照System Prompt中定义的Markdown格式输出。确保：
1. 清晰标注免费内容和付费升级选项
2. 包含所有安全提示和注意事项
3. 提供个性化建议和亮点说明
4. 自然引导用户下一步行动
"""
    
    # 调用Agent生成输出
    messages = [HumanMessage(content=prompt)]
    
    response = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": f"delivery_{int(time.time())}"}}
    )
    
    # 提取最后的AI响应
    ai_message = response["messages"][-1]
    content = ai_message.content.strip()
    
    return {
        "status": "success",
        "content": content,
        "format": "markdown",
        "has_upgrades": "升级选项" in content,
        "action_required": "下一步" in content
    }


# 创建全局交付Agent实例
_delivery_agent = None


def get_delivery_agent():
    """获取交付Agent实例（单例模式）"""
    global _delivery_agent
    if _delivery_agent is None:
        _delivery_agent = build_delivery_agent()
    return _delivery_agent
