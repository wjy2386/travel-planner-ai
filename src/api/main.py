"""
FastAPI Web接口层

为Lovable前端提供RESTful API接口
支持同步/异步调用、流式输出、WebSocket实时通信
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

# 导入多Agent系统
from agents.multi_agent import multi_agent_system, invoke_multi_agent_sync

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="旅行规划Agent API",
    description="多Agent旅行规划系统的Web接口",
    version="1.0.0"
)

# 配置CORS（允许Lovable前端跨域调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class UserRequest(BaseModel):
    """用户请求模型"""
    user_input: str = Field(..., description="用户输入的自然语言需求", min_length=1, max_length=2000)
    config: Optional[Dict[str, Any]] = Field(default=None, description="配置信息（可选）")
    session_id: Optional[str] = Field(default=None, description="会话ID（用于记忆管理）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "我想去东京旅游，计划3天，喜欢历史文化和美食",
                "session_id": "user_12345"
            }
        }


class StreamRequest(BaseModel):
    """流式请求模型"""
    user_input: str = Field(..., description="用户输入", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None, description="会话ID")


class AgentState(BaseModel):
    """Agent状态模型"""
    stage: str
    user_input: str
    error_message: Optional[str] = None


class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ==================== 端点定义 ====================

@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "name": "旅行规划Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "plan": "/api/v1/plan",
            "plan_stream": "/api/v1/plan/stream",
            "state": "/api/v1/state",
            "reset": "/api/v1/reset"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/plan", response_model=ApiResponse)
async def create_itinerary(request: UserRequest):
    """
    创建旅行行程（同步调用）
    
    适合不需要流式输出的场景
    """
    try:
        logger.info(f"[API] 收到行程规划请求: {request.user_input[:50]}...")
        
        # 构建配置（包含会话ID）
        config = request.config or {}
        if request.session_id:
            config["configurable"] = config.get("configurable", {})
            config["configurable"]["thread_id"] = request.session_id
        
        # 调用多Agent系统（同步）
        result = invoke_multi_agent_sync(request.user_input, config)
        
        # 返回结果
        return ApiResponse(
            success=True,
            message="行程规划成功",
            data={
                "itinerary": result,
                "session_id": request.session_id,
                "stage": multi_agent_system.get_state().get("stage", "unknown")
            }
        )
        
    except Exception as e:
        logger.error(f"[API] 行程规划失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"行程规划失败: {str(e)}"
        )


@app.post("/api/v1/plan/stream")
async def create_itinerary_stream(request: StreamRequest):
    """
    创建旅行行程（流式输出）
    
    适合需要实时展示生成过程的场景
    返回Server-Sent Events (SSE)格式的流
    """
    async def generate_stream():
        """生成流式数据"""
        try:
            logger.info(f"[API] 收到流式行程规划请求: {request.user_input[:50]}...")
            
            # 构建配置
            config = {}
            if request.session_id:
                config["configurable"] = {"thread_id": request.session_id}
            
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'message': '开始规划行程...'}, ensure_ascii=False)}\n\n"
            
            # 发送状态更新事件
            state = multi_agent_system.get_state()
            yield f"data: {json.dumps({'type': 'stage', 'stage': state.get('stage')}, ensure_ascii=False)}\n\n"
            
            # 调用多Agent系统（异步）
            result = await multi_agent_system.run(request.user_input, config)
            
            # 发送进度事件
            yield f"data: {json.dumps({'type': 'progress', 'message': '行程规划完成，正在生成说明...'}, ensure_ascii=False)}\n\n"
            
            # 发送结果事件
            yield f"data: {json.dumps({'type': 'complete', 'data': result}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"[API] 流式行程规划失败: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/v1/state", response_model=ApiResponse)
async def get_agent_state():
    """获取当前Agent状态"""
    try:
        state = multi_agent_system.get_state()
        return ApiResponse(
            success=True,
            message="获取状态成功",
            data=state
        )
    except Exception as e:
        logger.error(f"[API] 获取状态失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取状态失败: {str(e)}"
        )


@app.post("/api/v1/reset", response_model=ApiResponse)
async def reset_system():
    """重置系统状态"""
    try:
        multi_agent_system.reset()
        return ApiResponse(
            success=True,
            message="系统状态已重置",
            data={"reset_at": datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"[API] 重置系统失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"重置系统失败: {str(e)}"
        )


@app.get("/api/v1/history")
async def get_conversation_history(session_id: Optional[str] = None):
    """
    获取对话历史（暂未实现，预留接口）
    
    TODO: 集成checkpointer的对话历史查询功能
    """
    return ApiResponse(
        success=True,
        message="对话历史功能待实现",
        data={
            "session_id": session_id,
            "message": "需要集成checkpointer的对话历史查询"
        }
    )


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": "请求失败",
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"[API] 未捕获的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== 启动脚本 ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("[API] 启动FastAPI服务器...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，代码改动自动重启
        log_level="info"
    )
