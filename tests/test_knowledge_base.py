"""
知识库功能测试脚本
测试知识检索、RAG增强等功能
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.knowledge_search_tool import (
    search_travel_knowledge,
    search_destination_guide,
    search_seasonal_info
)
from tools.init_knowledge import initialize_knowledge_base, add_custom_knowledge


def test_knowledge_initialization():
    """测试知识库初始化"""
    print("="*60)
    print("测试1: 知识库初始化")
    print("="*60)
    
    success = initialize_knowledge_base()
    
    if success:
        print("✅ 知识库初始化成功\n")
    else:
        print("❌ 知识库初始化失败\n")
    
    return success


def test_destination_search():
    """测试目的地攻略搜索"""
    print("="*60)
    print("测试2: 目的地攻略搜索")
    print("="*60)
    
    from langchain.tools import ToolRuntime
    from coze_coding_utils.runtime_ctx.context import new_context
    
    ctx = new_context(method="test")
    runtime = ToolRuntime(context=ctx)
    
    # 搜索东京攻略
    result = search_destination_guide("东京", runtime)
    print("东京攻略搜索结果：\n")
    print(result[:500] + "...\n")  # 显示前500字符
    
    return len(result) > 0


def test_seasonal_search():
    """测试季节信息搜索"""
    print("="*60)
    print("测试3: 季节信息搜索")
    print("="*60)
    
    from langchain.tools import ToolRuntime
    from coze_coding_utils.runtime_ctx.context import new_context
    
    ctx = new_context(method="test")
    runtime = ToolRuntime(context=ctx)
    
    # 搜索东京春季信息
    result = search_seasonal_info("东京", "春季", runtime)
    print("东京春季信息搜索结果：\n")
    print(result[:500] + "...\n")
    
    return len(result) > 0


def test_knowledge_search():
    """测试知识库搜索"""
    print("="*60)
    print("测试4: 知识库搜索")
    print("="*60)
    
    from langchain.tools import ToolRuntime
    from coze_coding_utils.runtime_ctx.context import new_context
    
    ctx = new_context(method="test")
    runtime = ToolRuntime(context=ctx)
    
    # 搜索东京美食
    result = search_travel_knowledge("东京美食推荐", runtime)
    print("东京美食推荐搜索结果：\n")
    print(result[:500] + "...\n")
    
    return len(result) > 0


def test_custom_knowledge():
    """测试添加自定义知识"""
    print("="*60)
    print("测试5: 添加自定义知识")
    print("="*60)
    
    custom_content = """
    大理旅游攻略
    
    【最佳游览时间】
    春季（3-4月）：春暖花开，苍山洱海风光迷人
    秋季（10-11月）：秋高气爽，是最佳旅游季节
    
    【必游景点】
    大理古城：南诏古国文化，保存完好的古城风貌
    洱海：高原明珠，环海骑行体验绝佳
    苍山：十九峰十八溪，自然风光壮丽
    双廊古镇：文艺小镇，适合休闲度假
    崇圣寺三塔：大理标志性建筑
    
    【美食推荐】
    大理砂锅鱼：洱海鱼烹制，鲜嫩可口
    酸辣鱼：酸辣开胃，当地特色
    乳扇：大理特色乳制品，甜而不腻
    白族三道茶：一苦二甜三回味，体验白族文化
    
    【交通建议】
    大理机场：有直飞主要城市的航班
    大理火车站：昆明到大理动车2小时
    租车自驾：环洱海自驾是最佳体验方式
    """
    
    doc_id = add_custom_knowledge(custom_content, "大理")
    
    if doc_id:
        print(f"✅ 成功添加大理攻略，文档ID: {doc_id}\n")
        
        # 验证搜索
        from langchain.tools import ToolRuntime
        from coze_coding_utils.runtime_ctx.context import new_context
        
        ctx = new_context(method="test")
        runtime = ToolRuntime(context=ctx)
        
        result = search_travel_knowledge("大理旅游攻略", runtime)
        print("验证搜索结果：\n")
        print(result[:500] + "...\n")
        
        return "大理" in result
    else:
        print("❌ 添加自定义知识失败\n")
        return False


def test_agent_with_knowledge():
    """测试Agent使用知识库"""
    print("="*60)
    print("测试6: Agent集成知识库")
    print("="*60)
    
    try:
        from agents.itinerary_agent import build_itinerary_agent
        from langchain_core.messages import HumanMessage
        
        # 构建Agent
        agent = build_itinerary_agent()
        
        print("✅ Agent构建成功")
        print("Agent已集成以下知识库工具：")
        print("  - search_destination_guide: 目的地攻略搜索")
        print("  - search_seasonal_info: 季节信息搜索")
        print("  - search_travel_knowledge: 知识库搜索")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent构建失败: {str(e)}\n")
        return False


def main():
    """运行所有测试"""
    print("\n🧪 开始知识库功能测试\n")
    
    results = []
    
    # 测试1: 知识库初始化
    results.append(("知识库初始化", test_knowledge_initialization()))
    
    # 测试2-6: 功能测试
    results.append(("目的地攻略搜索", test_destination_search()))
    results.append(("季节信息搜索", test_seasonal_search()))
    results.append(("知识库搜索", test_knowledge_search()))
    results.append(("自定义知识添加", test_custom_knowledge()))
    results.append(("Agent集成", test_agent_with_knowledge()))
    
    # 汇总结果
    print("="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！知识库功能正常工作。")
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查配置和网络连接。")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
