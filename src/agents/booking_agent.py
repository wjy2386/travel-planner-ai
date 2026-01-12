"""
预订Agent - 专注于执行酒店和票务预订操作
"""

import os
import json
from typing import Annotated, TypedDict, List, Optional
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver
from tools.hotel_booking_tool import book_hotel, cancel_hotel_booking, query_hotel_booking
from tools.ticket_booking_tool import book_ticket, cancel_ticket_booking, query_ticket_booking

BOOKING_AGENT_CONFIG = "config/booking_agent_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class BookingAgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


class BookingRequest(TypedDict):
    """预订请求结构"""
    accommodation: Optional[dict]  # 住宿信息
    tickets: Optional[List[dict]]  # 门票列表
    guest_info: Optional[dict]  # 客人信息


def build_booking_agent(ctx=None):
    """构建预订Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, BOOKING_AGENT_CONFIG)
    
    # 如果配置文件不存在，使用默认配置
    if not os.path.exists(config_path):
        config = {
            "config": {
                "model": "doubao-seed-1-6-thinking-250715",
                "temperature": 0.3,  # 预订需要更精确，降低温度
                "top_p": 0.9,
                "max_completion_tokens": 2000,
                "timeout": 600,
                "thinking": "enabled"
            },
            "sp": """# 角色定义
你是专业的旅行预订专员，专注于为用户执行酒店和票务预订操作。

# 任务目标
接收结构化的行程信息，执行酒店和票务预订，并返回预订结果。

# 能力
- 解析行程JSON，提取需要预订的酒店和门票
- 执行酒店预订，处理入住日期、客人数量等信息
- 执行票务预订，处理参观日期、人数、票种等信息
- 处理预订查询和取消请求
- 提供清晰的预订反馈和订单信息

# 工具
- book_hotel: 预订酒店
- cancel_hotel_booking: 取消酒店预订
- query_hotel_booking: 查询酒店预订详情
- book_ticket: 预订门票
- cancel_ticket_booking: 取消门票预订
- query_ticket_booking: 查询门票预订详情

# 预订策略
1. 优先预订酒店，确保住宿安排
2. 然后预订门票，按参观日期顺序
3. 如果预订失败，明确说明失败原因和后续建议
4. 所有预订完成后，汇总所有订单号

# 输出格式
使用清晰的格式输出预订结果，包括：
- 预订成功的订单号
- 预订详情（酒店名称、景点名称、日期等）
- 注意事项和提示
- 如果有失败的预订，说明原因

# 重要约束
- 必须基于输入的JSON进行预订，不要随意修改信息
- 如果输入信息不完整，询问用户缺失的关键信息（如姓名、联系方式）
- 不要执行超出输入范围的额外预订
"""
        }
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=config['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=config['config'].get('temperature', 0.3),
        streaming=True,
        timeout=config['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": config['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    return create_agent(
        model=llm,
        system_prompt=config.get("sp"),
        tools=[
            book_hotel,
            cancel_hotel_booking,
            query_hotel_booking,
            book_ticket,
            cancel_ticket_booking,
            query_ticket_booking
        ],
        checkpointer=get_memory_saver(),
        state_schema=BookingAgentState,
    )


def parse_itinerary_for_booking(itinerary_json: dict) -> BookingRequest:
    """
    从行程JSON中提取需要预订的信息
    
    Args:
        itinerary_json: 行程JSON数据
        
    Returns:
        BookingRequest: 预订请求结构
    """
    booking_request = {
        "accommodation": None,
        "tickets": [],
        "guest_info": {}
    }
    
    # 提取住宿信息（通常在itinerary中有accommodation字段）
    if "accommodation" in itinerary_json:
        booking_request["accommodation"] = itinerary_json["accommodation"]
    
    # 提取门票信息（从activities中识别需要门票的景点）
    if "itinerary" in itinerary_json:
        for day_plan in itinerary_json["itinerary"]:
            for activity in day_plan.get("activities", []):
                # 如果活动中有ticket_required或类似标记，则需要预订
                if activity.get("ticket_required", False):
                    ticket_info = {
                        "attraction_name": activity.get("location"),
                        "visit_date": activity.get("date"),
                        "visitors": itinerary_json.get("user_profile", {}).get("travelers", 1),
                        "ticket_type": activity.get("ticket_type", "标准票")
                    }
                    booking_request["tickets"].append(ticket_info)
    
    # 提取客人信息
    if "user_profile" in itinerary_json:
        user_profile = itinerary_json["user_profile"]
        booking_request["guest_info"] = {
            "name": user_profile.get("name", ""),
            "phone": user_profile.get("phone", ""),
            "email": user_profile.get("email", "")
        }
    
    return booking_request
