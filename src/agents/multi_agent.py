"""
多Agent模式入口 - 使用协调器管理行程Agent和预订Agent
"""

from agents.coordinator import coordinator, TravelCoordinator
from typing import Optional


class MultiAgentSystem:
    """多Agent系统 - 提供统一的接口"""
    
    def __init__(self):
        """初始化多Agent系统"""
        self.coordinator = coordinator
    
    async def run(self, user_input: str, config: dict = None) -> str:
        """
        运行多Agent系统
        
        Args:
            user_input: 用户输入
            config: 配置信息
            
        Returns:
            处理结果
        """
        return await self.coordinator.process_user_request(user_input, config)
    
    def get_state(self) -> dict:
        """获取当前状态"""
        return self.coordinator.get_state()
    
    def reset(self):
        """重置系统状态"""
        self.coordinator.reset()
    
    @staticmethod
    def create_new_coordinator() -> TravelCoordinator:
        """创建新的协调器实例（用于并发场景）"""
        return TravelCoordinator()


# 创建全局多Agent系统实例
multi_agent_system = MultiAgentSystem()


# 兼容原有接口
def build_multi_agent(ctx=None):
    """构建多Agent系统（兼容原有接口）"""
    return multi_agent_system


async def invoke_multi_agent(user_input: str, config: dict = None) -> str:
    """调用多Agent系统（简化接口）"""
    return await multi_agent_system.run(user_input, config)
