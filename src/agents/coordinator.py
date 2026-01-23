"""
总控Agent (Orchestrator Agent)

职责：
- 理解用户意图
- 决定调用哪些Agent
- 控制协调流程（规划→校验→交付）
- 处理校验失败和重试逻辑
- 不干具体工作（不写行程、不查资料、不跟客户聊细节）

定位：资深定制游项目经理角色
"""

import json
import logging
import re
from typing import TypedDict, Optional, Literal, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

# 导入各个Agent
from agents.itinerary_agent import build_itinerary_agent
from agents.validation_agent import build_validation_agent, validate_itinerary
from agents.delivery_agent import build_delivery_agent, deliver_itinerary

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinatorState(TypedDict):
    """协调器状态"""
    stage: Literal["analysis", "planning", "validation", "delivery", "completed", "error"]
    user_input: str
    user_context: Optional[dict]
    itinerary_json: Optional[dict]
    validation_result: Optional[dict]
    retry_count: int
    max_retries: int
    error_message: Optional[str]


class TravelOrchestrator:
    """旅行总控Agent - 管理多Agent协作流程"""
    
    def __init__(self):
        """初始化总控Agent"""
        self.itinerary_agent = build_itinerary_agent()
        self.validation_agent = build_validation_agent()
        self.delivery_agent = build_delivery_agent()
        
        self.state = CoordinatorState(
            stage="analysis",
            user_input="",
            user_context=None,
            itinerary_json=None,
            validation_result=None,
            retry_count=0,
            max_retries=3,
            error_message=None
        )
    
    def reset(self):
        """重置协调器状态"""
        self.state = CoordinatorState(
            stage="analysis",
            user_input="",
            user_context=None,
            itinerary_json=None,
            validation_result=None,
            retry_count=0,
            max_retries=3,
            error_message=None
        )
    
    async def process_user_request(self, user_input: str, config: dict = None) -> str:
        """
        处理用户请求（主流程）
        
        流程：
        1. Analysis - 理解用户意图，提取关键信息
        2. Planning - 调用Itinerary Agent生成行程草案
        3. Validation - 调用Validation Agent校验可行性
        4. 如果校验不通过 → 重新规划（最多重试3次）
        5. Delivery - 调用Delivery Agent生成用户友好输出
        
        Args:
            user_input: 用户输入（自然语言）
            config: 配置信息（用于checkpoint等）
            
        Returns:
            处理结果（Markdown格式）
        """
        try:
            self.state["user_input"] = user_input
            
            logger.info(f"[Orchestrator] 开始处理用户请求: {user_input[:50]}...")
            
            # Step 1: 意图分析
            logger.info("[Orchestrator] Step 1: 分析用户意图...")
            user_context = await self._analyze_intent(user_input)
            self.state["user_context"] = user_context
            
            if not user_context or user_context.get("status") == "error":
                error_msg = user_context.get("error", "无法理解您的需求，请重新描述") if user_context else "无法理解您的需求"
                self.state["stage"] = "error"
                self.state["error_message"] = error_msg
                return self._format_error_response(error_msg)
            
            # Step 2: 行程规划
            logger.info("[Orchestrator] Step 2: 调用行程规划Agent...")
            self.state["stage"] = "planning"
            itinerary_result = await self._plan_itinerary(user_input, user_context, config)
            
            if not itinerary_result:
                error_msg = "行程规划失败，请稍后重试"
                self.state["stage"] = "error"
                self.state["error_message"] = error_msg
                return self._format_error_response(error_msg)
            
            self.state["itinerary_json"] = itinerary_result
            
            # Step 3: 可行性校验（循环直到通过或达到最大重试次数）
            self.state["stage"] = "validation"
            self.state["retry_count"] = 0
            
            while self.state["retry_count"] < self.state["max_retries"]:
                logger.info(f"[Orchestrator] Step 3: 校验行程可行性 (尝试 {self.state['retry_count'] + 1}/{self.state['max_retries']})...")
                
                validation_result = await self._validate_itinerary(itinerary_result, user_context)
                self.state["validation_result"] = validation_result
                
                # 判断校验结果
                if validation_result.get("status") == "passed":
                    logger.info("[Orchestrator] 校验通过！")
                    break
                elif validation_result.get("status") == "warning":
                    logger.warning(f"[Orchestrator] 校验警告: {validation_result.get('summary', '')}")
                    # 警告级别可以继续，但需要调整
                    # 这里我们选择继续交付，但会在Delivery中标注警告
                    break
                else:
                    # 校验失败，需要重新规划
                    logger.warning(f"[Orchestrator] 校验失败: {validation_result.get('summary', '')}")
                    self.state["retry_count"] += 1
                    
                    if self.state["retry_count"] >= self.state["max_retries"]:
                        error_msg = "行程调整失败，已达到最大重试次数。请稍后重试或联系人工客服。"
                        self.state["stage"] = "error"
                        self.state["error_message"] = error_msg
                        return self._format_error_response(error_msg)
                    
                    # 重新规划
                    logger.info(f"[Orchestrator] 重新规划行程 (第 {self.state['retry_count']} 次)...")
                    itinerary_result = await self._replan_itinerary(
                        user_input,
                        user_context,
                        validation_result,
                        config
                    )
                    self.state["itinerary_json"] = itinerary_result
            
            # Step 4: 交付给用户
            logger.info("[Orchestrator] Step 4: 生成用户友好输出...")
            self.state["stage"] = "delivery"
            delivery_result = await self._deliver_itinerary(itinerary_result, validation_result, user_context)
            
            self.state["stage"] = "completed"
            logger.info("[Orchestrator] 处理完成！")
            
            return delivery_result
            
        except Exception as e:
            logger.error(f"[Orchestrator] 处理请求时出错: {str(e)}", exc_info=True)
            self.state["stage"] = "error"
            self.state["error_message"] = str(e)
            return self._format_error_response(str(e))
    
    async def _analyze_intent(self, user_input: str) -> dict:
        """
        分析用户意图，提取关键信息
        
        使用简单规则提取，避免调用额外的LLM
        
        Returns:
            用户上下文字典
        """
        try:
            user_context = {
                "status": "success",
                "destination": "",
                "days": 0,
                "dates": "",
                "travelers": 1,
                "preferences": [],
                "budget": "",
                "pace": "",
                "special_requirements": ""
            }
            
            # 提取目的地
            # 常见城市列表
            cities = ["东京", "京都", "大阪", "北海道", "富良野", "奈良", "横滨", "镰仓", "箱根", "名古屋", "福冈", "广岛", "冲绳", "首尔", "釜山", "济州", "曼谷", "清迈", "新加坡", "吉隆坡", "巴厘岛", "普吉岛", "伦敦", "巴黎", "罗马", "巴塞罗那", "纽约", "洛杉矶", "旧金山", "温哥华", "多伦多", "悉尼", "墨尔本"]
            for city in cities:
                if city in user_input:
                    user_context["destination"] = city
                    break
            
            # 提取天数
            day_match = re.search(r'(\d+)\s*[天日]', user_input)
            if day_match:
                user_context["days"] = int(day_match.group(1))
            
            # 提取人数
            person_match = re.search(r'(\d+)\s*[个人人]', user_input)
            if person_match:
                user_context["travelers"] = int(person_match.group(1))
            
            # 提取偏好
            preferences = []
            if "历史" in user_input or "文化" in user_input:
                preferences.append("历史文化")
            if "美食" in user_input or "吃" in user_input:
                preferences.append("美食")
            if "摄影" in user_input or "拍照" in user_input:
                preferences.append("摄影")
            if "购物" in user_input or "买" in user_input:
                preferences.append("购物")
            if "自然" in user_input or "风景" in user_input:
                preferences.append("自然风光")
            if "亲子" in user_input or "孩子" in user_input:
                preferences.append("亲子")
            if "浪漫" in user_input or "情侣" in user_input:
                preferences.append("浪漫")
            if "户外" in user_input or "运动" in user_input:
                preferences.append("户外运动")
            user_context["preferences"] = preferences
            
            # 提取节奏
            if "不赶" in user_input or "慢" in user_input or "宽松" in user_input:
                user_context["pace"] = "宽松"
            elif "紧凑" in user_input or "赶" in user_input:
                user_context["pace"] = "紧凑"
            else:
                user_context["pace"] = "适中"
            
            # 如果没有提取到目的地，默认为空（让Agent自己推断）
            if not user_context["destination"]:
                logger.warning("[Orchestrator] 未能提取目的地信息")
            
            logger.info(f"[Orchestrator] 提取到的用户上下文: {user_context}")
            return user_context
            
        except Exception as e:
            logger.error(f"[Orchestrator] 意图分析异常: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _plan_itinerary(self, user_input: str, user_context: dict, config: dict) -> dict:
        """
        调用行程规划Agent生成行程草案
        
        Returns:
            行程JSON
        """
        try:
            # 构建规划提示
            planning_prompt = f"""请根据以下需求规划旅行行程。

{json.dumps(user_context, ensure_ascii=False, indent=2)}

请生成结构化的行程方案，包含每天的景点、住宿、交通安排。"""
            
            # 调用行程Agent
            messages = [HumanMessage(content=planning_prompt)]
            
            # 构建config，确保包含thread_id
            agent_config = config or {}
            if "configurable" not in agent_config:
                agent_config["configurable"] = {}
            if "thread_id" not in agent_config["configurable"]:
                agent_config["configurable"]["thread_id"] = f"itinerary_{self.state['user_input'][:20]}"
            
            itinerary_response = await self.itinerary_agent.ainvoke(
                {"messages": messages},
                config=agent_config
            )
            
            # 提取行程JSON
            # 这里简化处理，实际中需要从Agent响应中提取JSON
            # 假设行程Agent会返回包含JSON的响应
            content = itinerary_response["messages"][-1].content
            
            # 尝试从响应中提取JSON
            itinerary_json = self._extract_itinerary_json(content)
            
            return itinerary_json
            
        except Exception as e:
            logger.error(f"[Orchestrator] 行程规划失败: {str(e)}", exc_info=True)
            return None
    
    async def _replan_itinerary(
        self,
        user_input: str,
        user_context: dict,
        validation_result: dict,
        config: dict
    ) -> dict:
        """
        根据校验反馈重新规划行程
        
        Args:
            validation_result: 校验结果，包含问题和建议
        
        Returns:
            调整后的行程JSON
        """
        try:
            # 构建重规划提示
            issues = validation_result.get("issues", [])
            suggestions = validation_result.get("suggestions", "")
            
            replan_prompt = f"""请根据以下反馈调整行程方案。

## 原始需求
{json.dumps(user_context, ensure_ascii=False, indent=2)}

## 校验反馈
**问题**:
{json.dumps(issues, ensure_ascii=False, indent=2)}

**建议**:
{suggestions}

请根据这些反馈调整行程，确保解决所有严重问题。"""
            
            # 调用行程Agent重新规划
            messages = [HumanMessage(content=replan_prompt)]
            
            # 构建config，确保包含thread_id
            agent_config = config or {}
            if "configurable" not in agent_config:
                agent_config["configurable"] = {}
            if "thread_id" not in agent_config["configurable"]:
                agent_config["configurable"]["thread_id"] = f"itinerary_replan_{self.state['retry_count']}"
            
            itinerary_response = await self.itinerary_agent.ainvoke(
                {"messages": messages},
                config=agent_config
            )
            
            # 提取行程JSON
            content = itinerary_response["messages"][-1].content
            itinerary_json = self._extract_itinerary_json(content)
            
            return itinerary_json
            
        except Exception as e:
            logger.error(f"[Orchestrator] 行程重规划失败: {str(e)}", exc_info=True)
            return None
    
    async def _validate_itinerary(self, itinerary_json: dict, user_context: dict) -> dict:
        """
        调用校验Agent校验行程可行性
        
        Returns:
            校验结果字典
        """
        try:
            validation_result = validate_itinerary(
                self.validation_agent,
                itinerary_json,
                user_context
            )
            return validation_result
            
        except Exception as e:
            logger.error(f"[Orchestrator] 行程校验失败: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "score": 0,
                "issues": [{"type": "system_error", "severity": "high", "description": str(e)}],
                "summary": "校验系统异常",
                "needs_adjustment": True
            }
    
    async def _deliver_itinerary(
        self,
        itinerary_json: dict,
        validation_result: dict,
        user_context: dict
    ) -> str:
        """
        调用交付Agent生成用户友好输出
        
        Returns:
            Markdown格式的行程说明
        """
        try:
            delivery_result = deliver_itinerary(
                self.delivery_agent,
                itinerary_json,
                validation_result,
                user_context
            )
            
            return delivery_result.get("content", "行程说明生成失败")
            
        except Exception as e:
            logger.error(f"[Orchestrator] 行程交付失败: {str(e)}", exc_info=True)
            return f"行程说明生成失败: {str(e)}"
    
    def _extract_itinerary_json(self, content: str) -> dict:
        """
        从Agent响应中提取行程JSON
        
        Args:
            content: Agent响应内容
        
        Returns:
            行程JSON字典
        """
        try:
            # 尝试直接解析JSON
            content = content.strip()
            
            # 移除可能的markdown代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError:
            # 如果解析失败，返回一个模拟的结构
            logger.warning("[Orchestrator] 无法提取行程JSON，返回模拟数据")
            return {
                "status": "draft",
                "message": "行程草案（未能解析为结构化数据）",
                "raw_content": content
            }
    
    def _format_error_response(self, error_msg: str) -> str:
        """格式化错误响应"""
        return f"""❌ 处理失败

{error_msg}

请稍后重试或联系人工客服。"""
    
    def get_state(self) -> dict:
        """获取当前状态"""
        return dict(self.state)


# 创建全局协调器实例
orchestrator = TravelOrchestrator()


# 兼容原有接口
coordinator = orchestrator
