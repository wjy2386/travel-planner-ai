"""
检查知识库状态
"""

from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import new_context

def create_client():
    """创建知识库客户端"""
    ctx = new_context(method="check_knowledge_status")
    config = Config()
    return KnowledgeClient(config=config, ctx=ctx)


def check_knowledge_status():
    """检查知识库状态"""
    print("检查知识库状态...")
    
    client = create_client()
    
    # 尝试搜索所有数据集
    print("\n尝试搜索所有数据集（不指定table_names）...")
    response = client.search(
        query="东京",
        top_k=5,
        min_score=0.0
    )
    
    if response.code == 0:
        if response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for i, chunk in enumerate(response.chunks[:3], 1):
                print(f"\n结果 {i} (相关度: {chunk.score:.4f}):")
                print(f"文档ID: {chunk.doc_id}")
                print(f"内容摘要: {chunk.content[:200]}...")
        else:
            print(f"✗ 未找到任何结果")
            print(f"返回数据: {response.data}")
    else:
        print(f"✗ 搜索失败: {response.msg}")
    
    # 尝试指定不同的数据集名称
    print("\n\n尝试指定数据集名称...")
    dataset_names = [
        "travel_knowledge",
        "coze_doc_knowledge",
        "knowledge"
    ]
    
    for dataset in dataset_names:
        print(f"\n--- 搜索数据集: {dataset} ---")
        response = client.search(
            query="东京",
            table_names=[dataset],
            top_k=3,
            min_score=0.0
        )
        
        if response.code == 0 and response.chunks:
            print(f"✓ 找到 {len(response.chunks)} 条结果")
            for chunk in response.chunks[:2]:
                print(f"  - {chunk.content[:100]}...")
        else:
            print(f"✗ 未找到结果")


if __name__ == "__main__":
    check_knowledge_status()
