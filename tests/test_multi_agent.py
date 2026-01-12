"""
测试多Agent协作流程
"""

import asyncio
import sys
import os

# 添加项目路径到 PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from agents.multi_agent import multi_agent_system


async def test_multi_agent_workflow():
    """测试多Agent协作流程"""
    
    print("=" * 60)
    print("🧪 测试多Agent协作流程")
    print("=" * 60)
    print()
    
    # 配置（需要thread_id）
    config = {
        "configurable": {
            "thread_id": "test-thread-001"
        }
    }
    
    # 步骤1：用户发起请求
    print("📝 用户请求：规划东京3天旅行")
    user_request = "你好，我想规划一个东京3天2夜的旅行，从2025年4月5日开始，2个人，喜欢美食和购物。"
    
    print(f"用户输入: {user_request}\n")
    
    result = await multi_agent_system.run(user_request, config)
    
    print(f"🤖 Agent响应:\n{result}\n")
    print("-" * 60)
    print()
    
    # 步骤2：用户确认预订
    print("📝 用户确认：需要预订")
    confirm_request = "是的，请帮我预订酒店和门票"
    
    print(f"用户输入: {confirm_request}\n")
    
    result = await multi_agent_system.run(confirm_request, config)
    
    print(f"🤖 Agent响应:\n{result}\n")
    print("-" * 60)
    print()
    
    # 步骤3：查看系统状态
    state = multi_agent_system.get_state()
    print("📊 系统状态:")
    print(f"  - 阶段: {state['stage']}")
    print(f"  - 当前Agent: {state['current_agent']}")
    print(f"  - 行程JSON: {'已生成' if state['itinerary_json'] else '未生成'}")
    print(f"  - 预订结果: {'已完成' if state['booking_results'] else '未完成'}")
    print()
    
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


async def test_booking_agent_directly():
    """直接测试预订Agent"""
    print("\n")
    print("=" * 60)
    print("🧪 测试预订Agent（直接调用）")
    print("=" * 60)
    print()
    
    from agents.booking_agent import build_booking_agent
    
    booking_agent = build_booking_agent()
    
    booking_prompt = """请为以下行程执行预订操作：

1. 酒店预订
- 酒店: 浅草华盛顿酒店
- 城市: 东京
- 入住日期: 2025-04-05
- 退房日期: 2025-04-07
- 客人数: 2
- 房间类型: 双床房
- 客人姓名: 张三
- 联系电话: 13800000000

请使用相应的工具执行预订操作。"""
    
    from langchain_core.messages import HumanMessage
    
    # 配置（需要thread_id）
    config = {
        "configurable": {
            "thread_id": "test-thread-002"
        }
    }
    
    messages = [HumanMessage(content=booking_prompt)]
    result = await booking_agent.ainvoke({"messages": messages}, config=config)
    
    print(f"🤖 预订Agent响应:\n{result['messages'][-1].content}\n")
    print("=" * 60)
    print("✅ 预订Agent测试完成")
    print("=" * 60)


async def main():
    """主测试函数"""
    try:
        # 测试多Agent协作流程
        await test_multi_agent_workflow()
        
        # 测试预订Agent
        await test_booking_agent_directly()
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
