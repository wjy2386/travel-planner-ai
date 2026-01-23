"""
目的地知识采集 Agent

职责：
- 从网页内容中提取结构化数据
- 严格按照Schema输出JSON
- 不做内容创作，只做信息提取
"""

import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver
from tools.page_reader_tool import extract_webpage_content, discover_website_structure
from storage.knowledge_schemas import (
    AttractionSchema, AccommodationSchema, RestaurantSchema,
    TransportSchema, ActivitySchema, get_schema_by_type
)

HARVESTER_CONFIG = "config/knowledge_harvester_config.json"

# 保留最近 10 轮对话（20 条消息）
MAX_MESSAGES = 20


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class HarvesterAgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_harvester_agent(ctx=None):
    """构建知识采集Agent"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, HARVESTER_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.3),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=[
            extract_webpage_content,
            discover_website_structure
        ],
        checkpointer=get_memory_saver(),
        state_schema=HarvesterAgentState,
    )


def parse_with_schema(agent, url: str, schema_type: str, page_content: str = None):
    """
    使用Agent和指定Schema解析网页内容
    
    Args:
        agent: 知识采集Agent实例
        url: 网页URL
        schema_type: Schema类型（attraction/accommodation/restaurant/transport/activity）
        page_content: 网页内容（如果已提取，可直接传入）
    
    Returns:
        解析后的结构化数据（字典格式）
    """
    import time
    from datetime import datetime
    
    # 如果没有提供网页内容，先提取
    if not page_content:
        # 模拟调用工具
        tool_result = extract_webpage_content.func(url, None)
        if "skip" in tool_result:
            return {"status": "skip", "reason": "网页内容提取失败"}
        
        content_data = json.loads(tool_result)
        page_content = content_data.get("content", "")
        metadata = content_data.get("metadata", {})
    else:
        metadata = {}
    
    # 构建解析提示
    schema_example = get_schema_example(schema_type)
    
    prompt = f"""请从以下网页内容中提取{schema_type}信息，并严格按照Schema输出JSON。

网页URL: {url}
网页标题: {metadata.get('title', '')}
发布机构: {metadata.get('publisher', '')}

Schema示例：
{schema_example}

网页内容：
{page_content}

请严格按照Schema输出JSON，不要包含任何解释性文字。如果内容不包含有效信息，返回：
{{"status": "skip", "reason": "no usable data"}}
"""
    
    # 调用Agent进行解析
    messages = [
        HumanMessage(content=prompt)
    ]
    
    # 创建临时Agent实例（不使用记忆）
    temp_agent = build_harvester_agent()
    
    response = temp_agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": f"harvester_{int(time.time())}"}}
    )
    
    # 提取最后的AI响应
    ai_message = response["messages"][-1]
    content = ai_message.content
    
    try:
        # 解析JSON
        parsed_data = json.loads(content)
        
        # 如果是skip状态，直接返回
        if parsed_data.get("status") == "skip":
            return parsed_data
        
        # 验证数据
        schema_class = get_schema_by_type(schema_type)
        if not schema_class:
            return {"status": "skip", "reason": f"未知的Schema类型: {schema_type}"}
        
        # 创建Schema实例
        schema_obj = schema_class(**parsed_data)
        
        # 补充source信息
        from storage.knowledge_schemas import Source
        if not schema_obj.source:
            schema_obj.source = Source(
                url=url,
                publisher=metadata.get('publisher', urlparse(url).netloc),
                crawl_date=datetime.now().isoformat()
            )
        
        # 验证数据完整性
        is_valid, errors = schema_obj.validate()
        if not is_valid:
            return {
                "status": "skip",
                "reason": f"数据验证失败: {', '.join(errors)}",
                "needs_review": True,
                "data": parsed_data
            }
        
        return schema_obj.to_dict()
        
    except json.JSONDecodeError as e:
        return {"status": "skip", "reason": f"JSON解析失败: {str(e)}"}
    except Exception as e:
        return {"status": "skip", "reason": f"解析失败: {str(e)}"}


def get_schema_example(schema_type: str) -> str:
    """获取Schema示例"""
    examples = {
        "attraction": """{
  "type": "attraction",
  "name": "浅草寺",
  "destination": "东京",
  "description": "东京最古老的寺庙",
  "location": {
    "address": "东京都台东区浅草2-3-1",
    "lat": null,
    "lng": null
  },
  "opening_hours": "6:00-17:00",
  "recommended_duration": "1-2小时",
  "best_season": ["春季", "秋季"],
  "ticket_info": "免费参观",
  "official_tips": ["建议上午9点前到达避开人流"],
  "source": {
    "url": "https://example.com",
    "publisher": "东京都台东区",
    "crawl_date": "2024-01-01T00:00:00"
  }
}""",
        "accommodation": """{
  "type": "accommodation",
  "name": "浅草华盛顿酒店",
  "destination": "东京",
  "category": "酒店",
  "location": {
    "address": "东京都台东区浅草2-16-2",
    "lat": null,
    "lng": null
  },
  "room_types": ["标准双人房", "家庭房"],
  "check_in_out": "15:00-11:00",
  "transport_access": "浅草站步行5分钟",
  "official_description": "交通便利的商务酒店",
  "source": {
    "url": "https://example.com",
    "publisher": "华盛顿酒店",
    "crawl_date": "2024-01-01T00:00:00"
  }
}""",
        "restaurant": """{
  "type": "restaurant",
  "name": "寿司大 浅草店",
  "destination": "东京",
  "category": "日式料理",
  "cuisine": "江户前寿司",
  "location": {
    "address": "东京都台东区浅草1-3-1",
    "lat": null,
    "lng": null
  },
  "opening_hours": "8:00-21:00",
  "special_dishes": ["金枪鱼大脂寿司", "海胆军舰"],
  "reservation_info": "建议提前10点取号",
  "official_description": "米其林推荐的寿司店",
  "source": {
    "url": "https://example.com",
    "publisher": "寿司大",
    "crawl_date": "2024-01-01T00:00:00"
  }
}""",
        "transport": """{
  "type": "transport",
  "name": "东京Metro地铁",
  "destination": "东京",
  "transport_type": "地铁",
  "route_info": "覆盖东京主要区域",
  "schedule": "5:00-24:00",
  "fare_info": "根据距离计费",
  "access_info": "可在各车站购买车票",
  "official_description": "东京主要交通方式",
  "source": {
    "url": "https://example.com",
    "publisher": "东京Metro",
    "crawl_date": "2024-01-01T00:00:00"
  }
}""",
        "activity": """{
  "type": "activity",
  "name": "隅田川花火大会",
  "destination": "东京",
  "category": "节日庆典",
  "date_range": "7月最后一个周六",
  "location": {
    "address": "东京都隅田川沿岸",
    "lat": null,
    "lng": null
  },
  "official_description": "东京著名的夏季花火大会",
  "official_tips": ["建议提前2小时到达"],
  "source": {
    "url": "https://example.com",
    "publisher": "隅田川花火大会执行委员会",
    "crawl_date": "2024-01-01T00:00:00"
  }
}"""
    }
    
    return examples.get(schema_type, examples["attraction"])


from urllib.parse import urlparse
