"""
协调器 - 管理行程Agent和预订Agent的协作
"""

import json
from typing import TypedDict, Optional, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from agents.itinerary_agent import build_itinerary_agent
from agents.booking_agent import build_booking_agent, parse_itinerary_for_booking


class CoordinatorState(TypedDict):
    """协调器状态"""
    stage: Literal["collect_info", "planning", "booking", "completed", "error"]
    user_input: str
    itinerary_json: Optional[dict]
    booking_results: Optional[dict]
    current_agent: Optional[str]
    error_message: Optional[str]


class TravelCoordinator:
    """旅行协调器 - 管理多Agent协作"""
    
    def __init__(self):
        """初始化协调器"""
        self.itinerary_agent = build_itinerary_agent()
        self.booking_agent = build_booking_agent()
        self.state = CoordinatorState(
            stage="collect_info",
            user_input="",
            itinerary_json=None,
            booking_results=None,
            current_agent=None,
            error_message=None
        )
    
    async def process_user_request(self, user_input: str, config: dict = None) -> str:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入（自然语言）
            config: 配置信息（用于checkpoint等）
            
        Returns:
            处理结果（Markdown格式）
        """
        try:
            self.state["user_input"] = user_input
            
            # 判断当前阶段
            if self.state["stage"] == "collect_info":
                return await self._handle_collect_info(user_input, config)
            elif self.state["stage"] == "planning":
                return await self._handle_planning(user_input, config)
            elif self.state["stage"] == "booking":
                return await self._handle_booking(user_input, config)
            else:
                return self._get_completion_summary()
                
        except Exception as e:
            self.state["stage"] = "error"
            self.state["error_message"] = str(e)
            return f"❌ 处理请求时出错: {str(e)}"
    
    async def _handle_collect_info(self, user_input: str, config: dict) -> str:
        """处理信息收集阶段"""
        # 检查信息是否完整
        # 这里简化处理，直接进入规划阶段
        # 实际中可以要求用户提供更多信息（如姓名、联系方式等）
        
        self.state["stage"] = "planning"
        self.state["current_agent"] = "itinerary_agent"
        
        return await self._handle_planning(user_input, config)
    
    async def _handle_planning(self, user_input: str, config: dict) -> str:
        """处理行程规划阶段"""
        self.state["current_agent"] = "itinerary_agent"
        
        try:
            # 调用行程Agent生成行程
            messages = [HumanMessage(content=user_input)]
            itinerary_result = await self.itinerary_agent.ainvoke(
                {"messages": messages},
                config=config
            )
            
            # 获取行程JSON（尝试从响应中提取）
            # 这里简化处理，实际中需要解析Agent输出，提取JSON
            itinerary_response = itinerary_result["messages"][-1].content
            
            # 模拟提取JSON（实际中需要更复杂的解析逻辑）
            # 假设行程Agent会返回JSON格式的行程
            self.state["itinerary_json"] = self._extract_itinerary_json(itinerary_response)
            
            # 进入预订阶段
            self.state["stage"] = "booking"
            
            result = f"""✅ 行程规划完成

{itinerary_response}

---

接下来是否需要我为您预订酒店和门票？
- 回复"是的"或"确认预订"继续
- 回复"不需要"或"我自己预订"结束流程
"""
            return result
            
        except Exception as e:
            self.state["error_message"] = str(e)
            return f"❌ 行程规划失败: {str(e)}"
    
    async def _handle_booking(self, user_input: str, config: dict) -> str:
        """处理预订阶段"""
        self.state["current_agent"] = "booking_agent"
        
        # 检查用户是否确认预订
        confirm_keywords = ["是的", "确认", "预订", "好的", "ok", "yes"]
        cancel_keywords = ["不需要", "取消", "我自己", "no", "不需要"]
        
        user_input_lower = user_input.lower()
        
        if any(keyword in user_input_lower for keyword in cancel_keywords):
            self.state["stage"] = "completed"
            return self._get_completion_summary()
        
        if not any(keyword in user_input_lower for keyword in confirm_keywords):
            return "请确认是否需要预订酒店和门票。回复\"是的\"继续预订，或\"不需要\"结束流程。"
        
        try:
            # 构建预订请求
            if not self.state["itinerary_json"]:
                return "❌ 没有行程信息，无法执行预订。"
            
            booking_request = parse_itinerary_for_booking(self.state["itinerary_json"])
            
            # 构建预订提示
            booking_prompt = self._build_booking_prompt(booking_request)
            
            # 调用预订Agent执行预订
            messages = [HumanMessage(content=booking_prompt)]
            booking_result = await self.booking_agent.ainvoke(
                {"messages": messages},
                config=config
            )
            
            booking_response = booking_result["messages"][-1].content
            self.state["booking_results"] = booking_response
            
            # 完成流程
            self.state["stage"] = "completed"
            
            result = f"""✅ 预订完成

{booking_response}

---

{self._get_completion_summary()}
"""
            return result
            
        except Exception as e:
            self.state["error_message"] = str(e)
            return f"❌ 预订失败: {str(e)}"
    
    def _extract_itinerary_json(self, response: str) -> dict:
        """从Agent响应中提取行程JSON"""
        # 简化处理：尝试从响应中提取JSON
        # 实际中需要更复杂的解析逻辑，或者让Agent直接输出JSON
        
        # 这里返回一个模拟的行程JSON
        return {
            "user_profile": {
                "departure": "出发地",
                "destination": "东京",
                "dates": "2025-04-01至2025-04-04",
                "days": 4,
                "travelers": 2,
                "travel_tier": "小资",
                "preferences": ["历史文化"]
            },
            "itinerary": [
                {
                    "day": 1,
                    "theme": "江户历史探索日",
                    "accommodation": {
                        "hotel_name": "浅草华盛顿酒店",
                        "city": "东京",
                        "check_in_date": "2025-04-01",
                        "check_out_date": "2025-04-04"
                    }
                }
            ]
        }
    
    def _build_booking_prompt(self, booking_request: dict) -> str:
        """构建预订提示"""
        prompt = """请为以下行程执行预订操作：

"""
        
        if booking_request.get("accommodation"):
            acc = booking_request["accommodation"]
            prompt += f"""1. 酒店预订
- 酒店: {acc.get('hotel_name')}
- 城市: {acc.get('city')}
- 入住日期: {acc.get('check_in_date')}
- 退房日期: {acc.get('check_out_date')}
"""
        
        if booking_request.get("tickets"):
            prompt += "\\n2. 门票预订\\n"
            for i, ticket in enumerate(booking_request["tickets"], 1):
                prompt += f"""
{i}. 景点: {ticket.get('attraction_name')}
- 参观日期: {ticket.get('visit_date')}
- 参观人数: {ticket.get('visitors')}
- 票种: {ticket.get('ticket_type')}
"""
        
        prompt += """
请使用相应的工具执行预订操作。
"""
        return prompt
    
    def _get_completion_summary(self) -> str:
        """获取完成总结"""
        summary = """## 🎉 服务完成

您的旅行规划服务已完成！

**服务内容**:
"""
        
        if self.state["itinerary_json"]:
            summary += "- ✅ 行程规划: 已完成\n"
        
        if self.state["booking_results"]:
            summary += "- ✅ 预订服务: 已完成\n"
        else:
            summary += "- ⏸️ 预订服务: 未执行（用户自行预订）\n"
        
        summary += "\n**温馨提示**:\n"
        summary += "- 出发前建议再次确认天气和景点开放时间\n"
        summary += "- 保存好预订订单号，以备查询和使用\n"
        summary += "- 如有需要，随时联系我调整行程或查询订单\n\n"
        
        summary += "祝您旅途愉快！✨"
        
        return summary
    
    def get_state(self) -> CoordinatorState:
        """获取当前状态"""
        return self.state
    
    def reset(self):
        """重置协调器状态"""
        self.state = CoordinatorState(
            stage="collect_info",
            user_input="",
            itinerary_json=None,
            booking_results=None,
            current_agent=None,
            error_message=None
        )


# 创建全局协调器实例
coordinator = TravelCoordinator()
