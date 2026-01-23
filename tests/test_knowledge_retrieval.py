"""
知识库检索功能测试脚本

测试知识库的检索能力，验证：
1. 目的地攻略检索
2. 季节性信息检索
3. 特定主题检索
4. 多种查询场景
"""

from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import new_context

# 知识库名称
KNOWLEDGE_BASE_NAME = "travel_knowledge"


def create_client():
    """创建知识库客户端"""
    ctx = new_context(method="test_knowledge_retrieval")
    config = Config()
    return KnowledgeClient(config=config, ctx=ctx)


def test_destination_search():
    """测试目的地攻略检索"""
    print("="*60)
    print("测试1: 目的地攻略检索")
    print("="*60)
    
    client = create_client()
    
    destinations = ["东京", "京都", "巴黎"]
    
    for dest in destinations:
        print(f"\n--- 检索 {dest} 攻略 ---")
        query = f"{dest}旅游攻略 景点 美食 交通 住宿"
        
        response = client.search(
            query=query,
            table_names=[KNOWLEDGE_BASE_NAME],
            top_k=3,
            min_score=0.5
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for i, chunk in enumerate(response.chunks, 1):
                print(f"\n结果 {i} (相关度: {chunk.score:.4f}):")
                print(f"内容摘要: {chunk.content[:200]}...")
                print(f"文档ID: {chunk.doc_id}")
        else:
            print(f"✗ 未找到相关结果: {response.msg}")


def test_seasonal_search():
    """测试季节性信息检索"""
    print("\n" + "="*60)
    print("测试2: 季节性信息检索")
    print("="*60)
    
    client = create_client()
    
    test_queries = [
        "东京春季 最佳游览时间",
        "京都秋季 红叶 最佳时间",
        "巴黎冬季 旅游"
    ]
    
    for query in test_queries:
        print(f"\n--- 检索: {query} ---")
        
        response = client.search(
            query=query,
            table_names=[KNOWLEDGE_BASE_NAME],
            top_k=3,
            min_score=0.6
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for i, chunk in enumerate(response.chunks, 1):
                print(f"\n结果 {i} (相关度: {chunk.score:.4f}):")
                print(f"内容摘要: {chunk.content[:150]}...")
        else:
            print(f"✗ 未找到相关结果")


def test_topic_search():
    """测试特定主题检索"""
    print("\n" + "="*60)
    print("测试3: 特定主题检索")
    print("="*60)
    
    client = create_client()
    
    test_queries = [
        "东京美食推荐",
        "京都必游景点",
        "巴黎交通攻略",
        "浅草寺 参观建议",
        "东京塔 开放时间"
    ]
    
    for query in test_queries:
        print(f"\n--- 检索: {query} ---")
        
        response = client.search(
            query=query,
            table_names=[KNOWLEDGE_BASE_NAME],
            top_k=2,
            min_score=0.6
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for i, chunk in enumerate(response.chunks, 1):
                print(f"\n结果 {i} (相关度: {chunk.score:.4f}):")
                print(f"内容摘要: {chunk.content[:150]}...")
        else:
            print(f"✗ 未找到相关结果")


def test_practical_questions():
    """测试实用问题检索"""
    print("\n" + "="*60)
    print("测试4: 实用问题检索")
    print("="*60)
    
    client = create_client()
    
    test_queries = [
        "东京如何前往浅草寺",
        "京都住宿推荐 区域",
        "巴黎地铁使用方法",
        "日本旅行注意事项",
        "购买交通卡建议"
    ]
    
    for query in test_queries:
        print(f"\n--- 检索: {query} ---")
        
        response = client.search(
            query=query,
            table_names=[KNOWLEDGE_BASE_NAME],
            top_k=2,
            min_score=0.5
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            best_chunk = response.chunks[0]
            print(f"最佳匹配 (相关度: {best_chunk.score:.4f}):")
            print(f"内容: {best_chunk.content[:300]}...")
        else:
            print(f"✗ 未找到相关结果")


def test_multi_dialect():
    """测试多语言检索"""
    print("\n" + "="*60)
    print("测试5: 多语言检索")
    print("="*60)
    
    client = create_client()
    
    test_queries = [
        "Tokyo tourist attractions",
        "Kyoto temple visit",
        "Paris Eiffel Tower"
    ]
    
    for query in test_queries:
        print(f"\n--- 检索: {query} ---")
        
        response = client.search(
            query=query,
            table_names=[KNOWLEDGE_BASE_NAME],
            top_k=2,
            min_score=0.5
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for chunk in response.chunks:
                print(f"相关度: {chunk.score:.4f}, 内容: {chunk.content[:100]}...")
        else:
            print(f"✗ 未找到相关结果")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "█"*60)
    print("知识库检索功能测试套件")
    print("█"*60)
    
    try:
        test_destination_search()
        test_seasonal_search()
        test_topic_search()
        test_practical_questions()
        test_multi_dialect()
        
        print("\n" + "█"*60)
        print("所有测试完成")
        print("█"*60)
        
    except Exception as e:
        print(f"\n✗ 测试过程发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
