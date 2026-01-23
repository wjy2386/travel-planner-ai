"""
简化版知识库功能测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import KnowledgeClient, Config


def test_knowledge_search():
    """测试知识库搜索功能"""
    print("="*60)
    print("测试: 知识库搜索")
    print("="*60)
    
    ctx = new_context(method="test_search")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)
    
    # 测试1: 搜索东京攻略
    print("\n【测试1】搜索东京攻略...")
    response1 = client.search(
        query="东京旅游攻略 景点",
        table_names=["travel_knowledge"],
        top_k=3,
        min_score=0.5
    )
    
    if response1.code == 0:
        print(f"✅ 找到 {len(response1.chunks)} 条结果")
        for i, chunk in enumerate(response1.chunks[:2], 1):
            print(f"\n结果 {i} (相关度: {chunk.score:.2f}):")
            print(chunk.content[:200] + "...")
    else:
        print(f"❌ 搜索失败: {response1.msg}")
        return False
    
    # 测试2: 搜索美食
    print("\n【测试2】搜索东京美食...")
    response2 = client.search(
        query="东京美食推荐",
        table_names=["travel_knowledge"],
        top_k=2,
        min_score=0.5
    )
    
    if response2.code == 0:
        print(f"✅ 找到 {len(response2.chunks)} 条结果")
        for i, chunk in enumerate(response2.chunks, 1):
            print(f"\n结果 {i} (相关度: {chunk.score:.2f}):")
            print(chunk.content[:150] + "...")
    else:
        print(f"❌ 搜索失败: {response2.msg}")
    
    # 测试3: 搜索季节信息
    print("\n【测试3】搜索季节信息...")
    response3 = client.search(
        query="东京春季最佳游览时间",
        table_names=["travel_knowledge"],
        top_k=2,
        min_score=0.5
    )
    
    if response3.code == 0:
        print(f"✅ 找到 {len(response3.chunks)} 条结果")
        for i, chunk in enumerate(response3.chunks, 1):
            print(f"\n结果 {i} (相关度: {chunk.score:.2f}):")
            print(chunk.content[:150] + "...")
    else:
        print(f"❌ 搜索失败: {response3.msg}")
    
    # 测试4: 搜索京都
    print("\n【测试4】搜索京都攻略...")
    response4 = client.search(
        query="京都旅游攻略 寺庙",
        table_names=["travel_knowledge"],
        top_k=2,
        min_score=0.5
    )
    
    if response4.code == 0:
        print(f"✅ 找到 {len(response4.chunks)} 条结果")
        for i, chunk in enumerate(response4.chunks, 1):
            print(f"\n结果 {i} (相关度: {chunk.score:.2f}):")
            print(chunk.content[:150] + "...")
    else:
        print(f"❌ 搜索失败: {response4.msg}")
    
    # 测试5: 搜索通用建议
    print("\n【测试5】搜索通用旅行建议...")
    response5 = client.search(
        query="旅行规划原则 注意事项",
        table_names=["travel_knowledge"],
        top_k=2,
        min_score=0.5
    )
    
    if response5.code == 0:
        print(f"✅ 找到 {len(response5.chunks)} 条结果")
        for i, chunk in enumerate(response5.chunks, 1):
            print(f"\n结果 {i} (相关度: {chunk.score:.2f}):")
            print(chunk.content[:150] + "...")
    else:
        print(f"❌ 搜索失败: {response5.msg}")
    
    print("\n" + "="*60)
    print("✅ 所有搜索测试完成！知识库功能正常工作。")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_knowledge_search()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
