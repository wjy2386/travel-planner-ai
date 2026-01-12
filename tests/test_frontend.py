"""
前端功能测试脚本

测试前端页面的各个组件和API端点
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import asyncio
import json
from fastapi.testclient import TestClient

# 导入main模块
from main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


def test_root_endpoint(client):
    """测试根端点返回前端页面"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "AI旅行规划助手" in response.text


def test_static_files(client):
    """测试静态文件服务"""
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")
    
    response = client.get("/static/app.js")
    assert response.status_code == 200
    # FastAPI返回text/javascript，这也是正确的MIME类型
    assert "javascript" in response.headers.get("content-type", "")


def test_chat_endpoint(client):
    """测试聊天API端点"""
    payload = {
        "message": "你好",
        "session_id": "test_session_123"
    }
    
    response = client.post("/api/chat", json=payload)
    
    # 检查响应状态
    assert response.status_code == 200
    
    # 检查响应格式
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert "run_id" in data
    assert "status" in data
    
    # 检查返回的session_id是否正确
    assert data["session_id"] == "test_session_123"
    
    # 检查响应内容
    print(f"\nAI Response: {data['response']}")
    print(f"Status: {data['status']}")
    print(f"Current Agent: {data.get('current_agent', 'N/A')}")


def test_chat_endpoint_with_empty_message(client):
    """测试空消息的处理"""
    payload = {
        "message": "",
        "session_id": "test_session_empty"
    }
    
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "response" in data


def test_chat_endpoint_conversation_flow(client):
    """测试对话流程 - 模拟多轮对话"""
    session_id = "test_session_flow"
    
    # 第一轮：用户发起旅行请求
    print("\n=== 第一轮：发起旅行请求 ===")
    payload1 = {
        "message": "我想去东京旅行4天，喜欢历史文化，预算中等",
        "session_id": session_id
    }
    response1 = client.post("/api/chat", json=payload1)
    assert response1.status_code == 200
    data1 = response1.json()
    print(f"Response 1: {data1['response'][:200]}...")
    print(f"Stage: {data1['status']}")
    
    # 第二轮：用户确认预订
    print("\n=== 第二轮：确认预订 ===")
    payload2 = {
        "message": "是的，请帮我预订酒店和门票",
        "session_id": session_id
    }
    response2 = client.post("/api/chat", json=payload2)
    assert response2.status_code == 200
    data2 = response2.json()
    print(f"Response 2: {data2['response'][:200]}...")
    print(f"Stage: {data2['status']}")


def test_health_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
