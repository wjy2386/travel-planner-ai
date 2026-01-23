"""
查找知识库中的数据集名称
"""

from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import new_context

def create_client():
    """创建知识库客户端"""
    ctx = new_context(method="find_dataset_names")
    config = Config()
    return KnowledgeClient(config=config, ctx=ctx)


def find_datasets():
    """尝试找出实际的数据集名称"""
    print("搜索知识库中可用的数据集...")
    
    client = create_client()
    
    # 先不指定数据集，搜索所有内容
    print("\n1. 搜索所有数据集（不指定table_names）...")
    response = client.search(
        query="东京",
        top_k=10,
        min_score=0.0
    )
    
    if response.code == 0 and response.chunks:
        print(f"✓ 找到 {len(response.chunks)} 条结果")
        
        # 收集所有文档ID
        doc_ids = set()
        for chunk in response.chunks:
            doc_ids.add(chunk.doc_id)
        
        print(f"  文档ID数量: {len(doc_ids)}")
        print(f"  前3个文档ID: {list(doc_ids)[:3]}")
        
        # 尝试不同的数据集名称
        print("\n2. 尝试常见的数据集名称...")
        possible_names = [
            "travel_knowledge",
            "coze_doc_knowledge",
            "knowledge",
            "default",
            "travel"
        ]
        
        for name in possible_names:
            print(f"\n--- 尝试数据集名称: '{name}' ---")
            response = client.search(
                query="东京",
                table_names=[name],
                top_k=5,
                min_score=0.0
            )
            
            if response.code == 0:
                if response.chunks:
                    print(f"  ✓ 找到 {len(response.chunks)} 条结果")
                    print(f"  示例内容: {response.chunks[0].content[:100]}...")
                else:
                    print(f"  ✗ 数据集存在但无结果")
            else:
                print(f"  ✗ 搜索失败: {response.msg}")
    else:
        print(f"✗ 未找到任何结果")


if __name__ == "__main__":
    find_datasets()
