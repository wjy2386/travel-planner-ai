"""
知识库搜索工具 - 实现RAG检索增强
"""

from typing import Optional
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import Context

# 初始化知识库客户端
def get_knowledge_client(ctx: Optional[Context] = None):
    """获取知识库客户端"""
    config = Config()
    # 如果没有传入ctx，创建一个最小化的Context
    if ctx is None:
        # 创建一个最小化的Context
        ctx = Context(run_id="unknown", space_id="unknown", project_id="unknown")
    return KnowledgeClient(config=config, ctx=ctx)


@tool
def search_travel_knowledge(query: str, runtime: ToolRuntime = None) -> str:
    """
    在旅行知识库中搜索相关信息，用于增强行程规划的专业性。
    
    何时使用：
    - 用户询问特定目的地的深度信息
    - 需要获取景点的专业建议和攻略
    - 需要了解目的地的文化背景、最佳游览时间等
    - 需要获取实用的旅行小贴士和注意事项
    
    Args:
        query: 搜索关键词，如"东京美食推荐"、"京都历史文化"、"巴黎最佳游览季节"等
        runtime: ToolRuntime上下文
    
    Returns:
        返回相关的知识库内容，按相关度排序
    """
    if runtime is None:
        from langchain.tools import ToolRuntime
        from coze_coding_utils.runtime_ctx.context import new_context
        runtime = ToolRuntime(context=new_context(method="knowledge_search"))
    
    ctx = runtime.context
    client = get_knowledge_client(ctx)
    
    try:
        # 搜索旅行知识库（不指定table_names，搜索所有数据集）
        response = client.search(
            query=query,
            top_k=5,
            min_score=0.6  # 相关度阈值0.6
        )
        
        if response.code != 0 or not response.chunks:
            return f"知识库中未找到关于'{query}'的相关信息。"
        
        # 格式化搜索结果
        results = []
        for i, chunk in enumerate(response.chunks, 1):
            results.append(f"【参考{i}】(相关度:{chunk.score:.2f})\n{chunk.content}")
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"知识库搜索失败: {str(e)}"


@tool
def search_destination_guide(destination: str, runtime: ToolRuntime = None) -> str:
    """
    搜索特定目的地的详细攻略指南，包含景点、美食、交通、住宿等信息。
    
    何时使用：
    - 开始规划新行程时，获取目的地的全面信息
    - 用户询问"X地有什么好玩的"
    - 需要了解目的地的特色和亮点
    
    Args:
        destination: 目的地名称，如"东京"、"京都"、"巴黎"等
        runtime: ToolRuntime上下文
    
    Returns:
        返回该目的地的详细攻略信息
    """
    if runtime is None:
        from langchain.tools import ToolRuntime
        from coze_coding_utils.runtime_ctx.context import new_context
        runtime = ToolRuntime(context=new_context(method="destination_guide"))
    
    ctx = runtime.context
    client = get_knowledge_client(ctx)
    
    try:
        # 构建搜索查询
        query = f"{destination}旅游攻略 景点 美食 交通 住宿"
        
        response = client.search(
            query=query,
            top_k=8,
            min_score=0.5
        )
        
        if response.code != 0 or not response.chunks:
            return f"知识库中暂无'{destination}'的详细攻略信息，建议结合联网搜索补充。"
        
        # 提取最相关的攻略信息
        results = []
        for chunk in response.chunks:
            results.append(chunk.content)
        
        # 按相关度排序后返回
        return f"\n\n{'='*50}\n".join(results)
        
    except Exception as e:
        return f"目的地攻略搜索失败: {str(e)}"


@tool
def search_seasonal_info(destination: str, season: Optional[str] = None, runtime: ToolRuntime = None) -> str:
    """
    搜索目的地的季节性信息，如最佳游览时间、天气特点、节日活动等。
    
    何时使用：
    - 规划行程时需要考虑季节因素
    - 用户询问"X地几月去最好"
    - 需要了解特定季节的特色活动或限制
    
    Args:
        destination: 目的地名称
        season: 可选，季节关键词，如"春季"、"夏季"、"冬季"等，不指定则搜索所有季节信息
        runtime: ToolRuntime上下文
    
    Returns:
        返回季节性建议和信息
    """
    if runtime is None:
        from langchain.tools import ToolRuntime
        from coze_coding_utils.runtime_ctx.context import new_context
        runtime = ToolRuntime(context=new_context(method="seasonal_search"))
    
    ctx = runtime.context
    client = get_knowledge_client(ctx)
    
    try:
        # 构建搜索查询
        if season:
            query = f"{destination}{season} 最佳游览时间 天气 特色活动"
        else:
            query = f"{destination}最佳旅游季节 天气 节日活动"
        
        response = client.search(
            query=query,
            top_k=5,
            min_score=0.6
        )
        
        if response.code != 0 or not response.chunks:
            return f"知识库中暂无'{destination}'的季节性信息。"
        
        # 格式化结果
        results = []
        for chunk in response.chunks:
            results.append(chunk.content)
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"季节信息搜索失败: {str(e)}"
