"""
WebSocket实时通信支持

提供WebSocket连接，用于实时推送Agent状态和生成结果
适合需要双向通信的场景
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import logging

# 导入多Agent系统
from agents.multi_agent import multi_agent_system

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储所有活跃连接
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """接受新连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"[WebSocket] 客户端 {client_id} 已连接，当前连接数: {len(self.active_connections)}")
        
        # 发送欢迎消息
        await self.send_personal_message({
            "type": "connected",
            "message": f"WebSocket连接成功，客户端ID: {client_id}"
        }, client_id)
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"[WebSocket] 客户端 {client_id} 已断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"[WebSocket] 发送消息给 {client_id} 失败: {str(e)}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"[WebSocket] 广播消息给 {client_id} 失败: {str(e)}")
                disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_state_update(self, client_id: str):
        """发送状态更新"""
        state = multi_agent_system.get_state()
        await self.send_personal_message({
            "type": "state_update",
            "data": state
        }, client_id)


# 创建全局连接管理器实例
manager = ConnectionManager()


async def handle_itinerary_generation(websocket: WebSocket, client_id: str, user_input: str):
    """
    处理行程生成请求（WebSocket版本）
    
    实时推送生成进度和结果
    """
    try:
        # 发送开始事件
        await manager.send_personal_message({
            "type": "start",
            "message": "开始规划行程...",
            "stage": "analysis"
        }, client_id)
        
        # 模拟进度更新（实际中应该从Agent获取实时状态）
        stages = ["analysis", "planning", "validation", "delivery"]
        for i, stage in enumerate(stages):
            # 发送阶段更新
            await manager.send_personal_message({
                "type": "stage_update",
                "stage": stage,
                "progress": int((i + 1) / len(stages) * 100)
            }, client_id)
            
            # 短暂延迟，模拟处理时间
            await asyncio.sleep(0.5)
        
        # 实际调用Agent生成行程
        from agents.multi_agent import invoke_multi_agent_sync
        result = invoke_multi_agent_sync(user_input, {"configurable": {"thread_id": client_id}})
        
        # 发送完成事件
        await manager.send_personal_message({
            "type": "complete",
            "message": "行程规划完成",
            "data": result
        }, client_id)
        
    except Exception as e:
        logger.error(f"[WebSocket] 行程生成失败: {str(e)}", exc_info=True)
        await manager.send_personal_message({
            "type": "error",
            "error": str(e)
        }, client_id)
