# 目的地知识采集系统使用指南

## 概述

本系统实现了一个完整的"Destination Knowledge Harvester Agent"（目的地知识采集官），用于从官方网站批量采集结构化的旅行知识数据。

## 核心特点

1. **严格遵循Schema**：所有数据必须符合预定义的Schema结构
2. **只提取，不创作**：不发挥、不联想，只提取网页明确出现的信息
3. **可追溯性**：每条数据都包含来源URL、发布机构、抓取时间
4. **自动校验**：内置数据校验机制，标记需要人工审核的数据
5. **完整工作流**：5步流程，从发现到入库全自动

## 系统架构

### 5步工作流

```
Step 1: 官网入口识别 → 找到官方入口、sitemap、导航结构
Step 2: 页面读取 → 提取网页正文（去广告、去footer等噪音）
Step 3: 结构化解析 → 按照Schema提取结构化数据
Step 4: 校验 & 入库 → 自动校验、标记审核、存储到数据库
Step 5: 索引 → 结构化数据入SQL，描述字段入向量库
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Schema数据模型 | `src/storage/knowledge_schemas.py` | 定义5种Schema结构 |
| 页面读取工具 | `src/tools/page_reader_tool.py` | 提取网页正文 |
| 结构化解析Agent | `src/agents/knowledge_harvester_agent.py` | 按Schema提取数据 |
| 数据校验器 | `src/storage/knowledge_validator.py` | 校验数据完整性 |
| 数据存储 | `src/storage/knowledge_storage.py` | 存储到数据库 |
| 工作流编排 | `src/tools/knowledge_harvest_workflow.py` | 完整工作流 |

## Schema设计

### 1. 景点Schema (AttractionSchema)

```json
{
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
}
```

### 2. 住宿Schema (AccommodationSchema)

```json
{
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
}
```

### 3. 餐饮Schema (RestaurantSchema)

```json
{
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
}
```

### 4. 交通Schema (TransportSchema)

```json
{
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
}
```

### 5. 活动Schema (ActivitySchema)

```json
{
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
}
```

## 使用方法

### 1. 采集单个URL

```python
from tools.knowledge_harvest_workflow import KnowledgeHarvestWorkflow

# 初始化工作流
workflow = KnowledgeHarvestWorkflow(database_url="postgresql://user:pass@localhost/db")

# 采集单个景点
result = workflow.run_single_url(
    url="https://www.gotokyo.org/jp/spot/evt41/index.html",
    schema_type="attraction",
    destination="东京"
)

print(f"采集状态: {result['status']}")
print(f"文档ID: {result.get('doc_id')}")
```

### 2. 批量采集

```python
# 定义采集任务
tasks = [
    {"url": "https://www.kinkakuji.or.jp/", "schema_type": "attraction", "destination": "京都"},
    {"url": "https://www.kiyomizuyera.or.jp/", "schema_type": "attraction", "destination": "京都"},
    {"url": "https://example.com/hotel", "schema_type": "accommodation", "destination": "京都"}
]

# 批量采集（每个任务间隔2秒）
results = workflow.run_batch(tasks, delay=2.0)

# 查看结果
for result in results:
    print(f"{result['url']}: {result['status']}")
```

### 3. 自动发现并采集

```python
# 自动发现网站结构并采集
results = workflow.discover_and_harvest(
    base_url="https://kyoto.travel/",
    schema_type="attraction",
    destination="京都",
    max_urls=20
)
```

### 4. 查询数据

```python
# 按目的地查询
tokyo_attractions = workflow.storage.query_by_destination(
    destination="东京",
    schema_type="attraction"
)

# 按名称查询
sensoji = workflow.storage.query_by_name(
    name="浅草寺",
    destination="东京"
)

# 获取统计信息
stats = workflow.storage.get_statistics()
print(f"总记录数: {stats['total']}")
print(f"有效记录: {stats['valid']}")
print(f"待审核: {stats['pending_review']}")
```

### 5. 审核管理

```python
# 获取待审核记录
pending = workflow.storage.get_pending_review(limit=10)

# 审核通过
workflow.storage.approve_review(doc_id="...")

# 审核拒绝
workflow.storage.reject_review(doc_id="...", reason="数据不完整")
```

## System Prompt

知识采集Agent的System Prompt位于 `config/knowledge_harvester_config.json`：

```
你是一个【目的地知识采集 Agent】。

你的唯一目标是：
从权威、官方或半官方的网站中，采集与指定目的地相关的
【景点 / 住宿 / 餐饮 / 交通 / 活动】信息，
并严格按照给定的结构化 Schema 输出 JSON 数据。

【重要规则】
1. 你不是内容创作 Agent，不允许发挥、联想或补充常识。
2. 只允许提取网页中明确出现的信息。
3. 不确定的信息必须留空或标记为 null。
4. 每一条数据必须包含 source（来源 URL、发布机构、抓取时间）。
5. 禁止合并多个网页的信息到同一个字段。
6. 禁止使用非官方、非权威来源，除非被明确允许。
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | postgresql://postgres:postgres@localhost:5432/travel_knowledge |
| COZE_WORKSPACE_PATH | 工作目录路径 | /workspace/projects |
| COZE_WORKLOAD_IDENTITY_API_KEY | API密钥 | 从环境变量读取 |
| COZE_INTEGRATION_MODEL_BASE_URL | 模型基础URL | 从环境变量读取 |

### 模型配置

知识采集Agent使用低temperature（0.3）以确保数据提取的准确性和稳定性：

```json
{
  "config": {
    "model": "doubao-seed-1-6-thinking-250715",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  }
}
```

## 测试

运行测试套件：

```bash
python tests/test_knowledge_harvest.py
```

测试覆盖：
- ✓ Schema数据模型
- ✓ 页面内容提取
- ✓ Agent创建
- ✓ 数据校验器
- ✓ 工作流创建

## 数据库表结构

### knowledge_records 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| doc_id | String(64) | 文档唯一ID |
| schema_type | String(50) | Schema类型 |
| name | String(200) | 名称 |
| destination | String(100) | 目的地 |
| data | JSON | 结构化数据 |
| content_text | Text | 用于向量检索的文本 |
| source_url | String(500) | 来源URL |
| source_publisher | String(200) | 发布机构 |
| crawl_date | DateTime | 抓取时间 |
| is_valid | Boolean | 是否有效 |
| needs_review | Boolean | 是否需要审核 |
| review_errors | JSON | 审核错误信息 |
| version | Integer | 版本号 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 最佳实践

1. **从官方网站采集**：优先使用官方网站，保证数据权威性
2. **控制采集频率**：设置合理的延迟（1-3秒），避免对目标网站造成压力
3. **定期审核**：及时处理待审核数据，保证数据质量
4. **版本管理**：利用version字段追踪数据更新
5. **索引优化**：为常用查询字段创建索引

## 注意事项

1. **不包含价格和评分**：这是商业平台的坑，避免UGC污染
2. **只提取，不创作**：禁止发挥、联想，只提取明确出现的信息
3. **数据可追溯**：每条数据必须包含完整的source信息
4. **使用官方来源**：禁止使用非官方、非权威来源
5. **人工审核**：标记为needs_review的数据必须人工审核

## 使用场景

知识采集系统不直接服务终端用户，只服务以下三类Agent：

1. **行程生成Agent**：提供结构化的景点、住宿、餐饮数据
2. **销售/定制Agent**：提供官方描述和位置信息
3. **履约 & 校验Agent**：验证行程中信息的准确性

## 下一步优化

1. **Step 5: 索引**：实现描述字段的向量化，支持语义检索
2. **增量更新**：实现定时任务，自动更新已采集的数据
3. **质量监控**：建立数据质量评分机制
4. **批量导入**：支持从JSON/YAML文件批量导入
5. **可视化审核**：提供Web界面进行人工审核

## 总结

本知识采集系统实现了：

✅ 严格的Schema设计，确保数据结构一致
✅ 5步完整工作流，从发现到入库全自动化
✅ 自动校验机制，标记需要审核的数据
✅ 数据可追溯，每条数据都有完整来源
✅ 测试验证通过，所有组件正常工作

核心竞争力不在"生成"，而在"你能调什么、怎么调、调的是不是对的"。
