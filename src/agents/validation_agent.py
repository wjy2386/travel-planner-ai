"""
行程可行性校验Agent

职责：
- 校验行程时间合理性
- 检查景点开放性和季节适配性
- 评估单日负荷和风险
- 识别知识缺口
- 输出标准化的校验结果

定位：旅行社计调/风控角色
"""

import os
import json
from typing import Annotated, Optional
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

VALIDATION_CONFIG = "config/validation_config.json"

# 保留最近 10 轮对话（20 条消息）
MAX_MESSAGES = 20


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class ValidationAgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_validation_agent(ctx=None):
    """构建校验Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, VALIDATION_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.3),  # 低温度确保准确性
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=[],  # 校验Agent不需要外部工具
        checkpointer=get_memory_saver(),
        state_schema=ValidationAgentState,
    )


def validate_itinerary(agent, itinerary_json: dict, user_context: dict = None) -> dict:
    """
    校验行程可行性
    
    Args:
        agent: 校验Agent实例
        itinerary_json: 行程JSON数据
        user_context: 用户上下文（可选，包含用户偏好、体力水平等）
    
    Returns:
        校验结果字典
    """
    import time
    
    # 构建校验提示
    prompt = f"""请对以下行程进行可行性校验。

## 用户需求
{json.dumps(user_context or {}, ensure_ascii=False, indent=2)}

## 行程方案
{json.dumps(itinerary_json, ensure_ascii=False, indent=2)}

请严格按照System Prompt中定义的JSON格式输出校验结果。只输出JSON，不要包含任何其他文字。
"""
    
    # 调用Agent进行校验
    messages = [HumanMessage(content=prompt)]
    
    response = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": f"validation_{int(time.time())}"}}
    )
    
    # 提取最后的AI响应
    ai_message = response["messages"][-1]
    content = ai_message.content.strip()
    
    try:
        # 解析JSON
        validation_result = json.loads(content)
        return validation_result
        
    except json.JSONDecodeError as e:
        # 如果解析失败，返回默认的错误结果
        return {
            "status": "failed",
            "score": 0,
            "issues": [
                {
                    "type": "parse_error",
                    "severity": "high",
                    "description": f"校验结果解析失败: {str(e)}",
                    "suggestion": "请重新生成行程"
                }
            ],
            "knowledge_gaps": [],
            "safety_alerts": [],
            "summary": "校验系统异常，无法完成评估",
            "needs_adjustment": True,
            "raw_response": content
        }
    except Exception as e:
        return {
            "status": "failed",
            "score": 0,
            "issues": [
                {
                    "type": "system_error",
                    "severity": "high",
                    "description": f"校验系统异常: {str(e)}",
                    "suggestion": "请重试或联系技术支持"
                }
            ],
            "knowledge_gaps": [],
            "safety_alerts": [],
            "summary": "校验系统异常",
            "needs_adjustment": True
        }


# 创建全局校验Agent实例
_validation_agent = None


def get_validation_agent():
    """获取校验Agent实例（单例模式）"""
    global _validation_agent
    if _validation_agent is None:
        _validation_agent = build_validation_agent()
    return _validation_agent
