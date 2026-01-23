"""
多Agent系统入口 - 生产级旅行操作系统

架构：
Orchestrator（总控）
    ↓
Itinerary Planning Agent（行程规划）
    ↓
Validation Agent（可行性校验）
    ↓
Delivery Agent（对客输出/商业转化）

职责：
- 提供统一的对外接口
- 管理多Agent协作流程
- 处理错误和重试
- 保持向后兼容性
"""

import asyncio
import logging
from typing import Optional
from agents.coordinator import orchestrator, TravelOrchestrator

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiAgentSystem:
    """
    多Agent系统 - 旅行操作系统
    
    这是生产级的多Agent架构，实现了：
    1. 清晰的职责分离（每个Agent只做一件事）
    2. 标准化的数据交互（通过JSON）
    3. 完整的错误处理和重试机制
    4. 向后兼容原有接口
    """
    
    def __init__(self):
        """初始化多Agent系统"""
        self.orchestrator = orchestrator
    
    async def run(self, user_input: str, config: dict = None) -> str:
        """
        运行多Agent系统
        
        执行完整流程：
        1. 意图分析
        2. 行程规划
        3. 可行性校验（可能重试）
        4. 用户友好输出
        
        Args:
            user_input: 用户输入（自然语言）
            config: 配置信息（用于checkpoint、记忆等）
            
        Returns:
            处理结果（Markdown格式）
        """
        try:
            logger.info(f"[MultiAgent] 开始处理用户请求: {user_input[:50]}...")
            result = await self.orchestrator.process_user_request(user_input, config)
            logger.info("[MultiAgent] 处理完成")
            return result
            
        except Exception as e:
            logger.error(f"[MultiAgent] 系统异常: {str(e)}", exc_info=True)
            return f"❌ 系统异常: {str(e)}"
    
    def get_state(self) -> dict:
        """获取当前系统状态"""
        return self.orchestrator.get_state()
    
    def reset(self):
        """重置系统状态"""
        self.orchestrator.reset()
        logger.info("[MultiAgent] 系统状态已重置")
    
    @staticmethod
    def create_new_system() -> TravelOrchestrator:
        """
        创建新的系统实例（用于并发场景）
        
        Returns:
            新的TravelOrchestrator实例
        """
        return TravelOrchestrator()


# 创建全局多Agent系统实例
multi_agent_system = MultiAgentSystem()


# 兼容原有接口
def build_multi_agent(ctx=None):
    """
    构建多Agent系统（兼容原有接口）
    
    Args:
        ctx: 上下文（可选，用于传递headers等）
    
    Returns:
        MultiAgentSystem实例
    """
    return multi_agent_system


async def invoke_multi_agent(user_input: str, config: dict = None) -> str:
    """
    调用多Agent系统（简化接口）
    
    Args:
        user_input: 用户输入
        config: 配置信息
    
    Returns:
        处理结果
    """
    return await multi_agent_system.run(user_input, config)


# 同步接口（用于非async场景）
def invoke_multi_agent_sync(user_input: str, config: dict = None) -> str:
    """
    同步调用多Agent系统
    
    Args:
        user_input: 用户输入
        config: 配置信息
    
    Returns:
        处理结果
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(multi_agent_system.run(user_input, config))
    except RuntimeError:
        # 如果没有事件循环，创建一个
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(multi_agent_system.run(user_input, config))
        finally:
            loop.close()


# 导出所有Agent构建函数（用于单独测试或独立使用）
from agents.itinerary_agent import build_itinerary_agent
from agents.validation_agent import build_validation_agent, validate_itinerary
from agents.delivery_agent import build_delivery_agent, deliver_itinerary
from agents.knowledge_harvester_agent import build_harvester_agent, parse_with_schema
from agents.coordinator import TravelOrchestrator


__all__ = [
    # 系统入口
    "MultiAgentSystem",
    "multi_agent_system",
    "build_multi_agent",
    "invoke_multi_agent",
    "invoke_multi_agent_sync",
    
    # Agent构建函数
    "build_itinerary_agent",
    "build_validation_agent",
    "build_delivery_agent",
    "build_harvester_agent",
    "TravelOrchestrator",
    
    # 核心功能函数
    "validate_itinerary",
    "deliver_itinerary",
    "parse_with_schema"
]
