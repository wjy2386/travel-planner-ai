# 旅行规划 AI Agent - 项目交付文档

## 📋 项目概述

这是一个基于 LangChain + LangGraph 的多 Agent 旅行规划系统，支持国内游、入境游、出境游的个性化行程规划，集成了知识库、实时信息查询和商业转化能力。

---

## 🎯 核心功能

### 1. 多 Agent 协同系统
- **Orchestrator Agent**: 协调多个 Agent 的工作流
- **Itinerary Agent**: 生成详细旅行方案（温度0.6）
- **Validation Agent**: 校验方案可行性（温度0.3）
- **Delivery Agent**: 对客输出与商业转化（温度0.7）

### 2. 智能方案生成
- ✅ 基于用户需求的个性化行程规划
- ✅ 支持自由行/包车两种出行方式
- ✅ 实时价格查询（禁止使用固定价格）
- ✅ 点到点距离与行车时间计算
- ✅ 精准住宿推荐（基于预算和出行方式）

### 3. 知识库集成
- ✅ 目的地知识采集系统
- ✅ 结构化数据提取（严格遵循 Schema）
- ✅ 语义搜索与检索
- ✅ 智能知识推荐

### 4. Web 服务接口
- ✅ RESTful API
- ✅ SSE 流式输出
- ✅ WebSocket 实时通信

### 5. 产品经理模式
- ✅ 8条内部判断规则
- ✅ 风险评估与自动降级
- ✅ 用户层级识别
- ✅ Fallback 方案生成

---

## 🛠 技术栈

### 后端
- Python 3.9+
- LangChain 1.0
- LangGraph 1.0
- FastAPI
- Uvicorn
- SQLAlchemy 2.0
- PostgreSQL
- coze-coding-dev-sdk

### AI 模型
- doubao-seed-1-6-251015（主模型）
- doubao-embedding-v2（向量嵌入）

### 依赖库
- requests
- BeautifulSoup
- html2text

---

## 📁 项目结构

```
/workspace/projects/
├── config/                    # 配置文件
│   ├── agent_llm_config.json  # 主 Agent 配置
│   ├── orchestrator_config.json
│   ├── itinerary_config.json
│   ├── validation_config.json
│   ├── delivery_config.json
│   └── product_manager_config.json
├── src/
│   ├── agents/                # Agent 实现
│   │   ├── agent.py          # 单一 Agent 模式（向后兼容）
│   │   ├── orchestrator.py   # 协调 Agent
│   │   ├── itinerary.py      # 行程规划 Agent
│   │   ├── validation.py     # 校验 Agent
│   │   └── delivery.py       # 交付 Agent
│   ├── tools/                 # 工具定义
│   │   ├── web_search_tool.py
│   │   ├── distance_calculator.py
│   │   ├── hotel_search.py
│   │   ├── user_tier_detector.py
│   │   └── risk_assessment.py
│   ├── storage/               # 存储层
│   │   ├── database/
│   │   │   ├── db.py         # 数据库连接
│   │   │   └── models.py     # 数据模型
│   │   └── memory/
│   │       └── memory_saver.py  # 短期记忆
│   └── main.py               # 启动入口
├── tests/                     # 测试文件
├── assets/                    # 资源文件
├── scripts/                   # 脚本
├── requirements.txt           # 依赖
├── Dockerfile                 # Docker 配置
├── docker-compose.yml         # Docker Compose
└── README.md                  # 项目说明
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（已排除在 git 外）：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/travel_planner

# API Key
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=https://your-base-url

# 知识库配置
KNOWLEDGE_BASE_ID=your_knowledge_base_id
```

### 3. 启动数据库

```bash
# 使用 Docker Compose
docker-compose up -d

# 或手动启动 PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15
```

### 4. 初始化数据库

```bash
python scripts/init_db.py
```

### 5. 启动服务

```bash
# 单一 Agent 模式
python src/main.py --mode single

# 多 Agent 协同模式
python src/main.py --mode multi

# Web 服务
python src/main.py --mode web --port 8000
```

---

## 🌐 API 接口

### RESTful API

#### 生成旅行方案

```http
POST /api/v1/itinerary/generate
Content-Type: application/json

{
  "destination": "云南",
  "duration": 7,
  "travel_style": "自由行",
  "budget": 10000,
  "participants": [
    {"type": "adult", "count": 2},
    {"type": "child", "count": 1, "age": 6}
  ],
  "preferences": ["自然", "美食", "亲子活动"],
  "conversation_history": []
}
```

**响应**：

```json
{
  "status": "success",
  "data": {
    "itinerary_id": "it_123456",
    "plan": "...详细行程...",
    "estimated_cost": 8500,
    "validation": {
      "feasible": true,
      "warnings": []
    }
  }
}
```

### SSE 流式输出

```http
GET /api/v1/itinerary/generate/stream?destination=云南&duration=7
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/itinerary');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

ws.send(JSON.stringify({
  type: "generate_itinerary",
  payload: {
    destination: "云南",
    duration: 7
  }
}));
```

---

## 🔧 配置说明

### Agent 配置

每个 Agent 都有独立的配置文件，例如 `config/itinerary_config.json`：

```json
{
  "config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.6,
    "top_p": 0.85,
    "max_completion_tokens": 40000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "你是专业的行程规划专家...",
  "tools": [
    "web_search_tool",
    "distance_calculator",
    "hotel_search"
  ]
}
```

### 数据库配置

已优化连接池，防止连接被强制终止：

```python
# src/storage/database/db.py

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)
```

---

## 🧪 测试

### 运行单元测试

```bash
pytest tests/
```

### 集成测试

```bash
pytest tests/integration/
```

### 手动测试

使用 `test_run` 工具：

```python
from src.agents.orchestrator import build_agent

agent = build_agent()
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "帮我规划一个7天云南行程，一家三口，孩子6岁"
    }]
})
```

---

## 📊 数据库模型

### 核心表

| 表名 | 说明 |
|------|------|
| users | 用户信息 |
| itineraries | 行程方案 |
 itinerary_items | 行程详情 |
| knowledge_entries | 知识库条目 |
| chat_sessions | 对话会话 |

---

## 🎨 前端集成

### React 示例

```typescript
// src/components/ItineraryGenerator.tsx

import React, { useState } from 'react';

export const ItineraryGenerator = () => {
  const [destination, setDestination] = useState('');
  const [duration, setDuration] = useState(7);
  const [itinerary, setItinerary] = useState('');

  const generateItinerary = async () => {
    const response = await fetch('/api/v1/itinerary/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ destination, duration })
    });
    const data = await response.json();
    setItinerary(data.data.plan);
  };

  return (
    <div>
      <input
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
        placeholder="输入目的地"
      />
      <button onClick={generateItinerary}>生成行程</button>
      <div>{itinerary}</div>
    </div>
  );
};
```

---

## 🔒 安全注意事项

1. **敏感信息**
   - `.env` 文件已排除在 git 外
   - 不要提交 API Key、数据库密码等

2. **数据验证**
   - 所有输入都经过 Validation Agent 校验
   - 使用参数化查询防止 SQL 注入

3. **错误处理**
   - 所有工具调用都有错误处理和重试机制
   - 错误信息不泄露敏感数据

---

## 🐛 已知问题

1. **模型格式一致性**
   - 模型有时不严格按照要求的 Markdown 格式输出
   - 建议采用后处理或 JSON 输出再转换的方式

2. **数据库连接**
   - 长时间运行可能出现连接被终止
   - 已优化连接池配置，建议定期重启服务

---

## 📈 未来优化方向

1. **多语言支持**
   - 支持英、日、韩、法、德等语言（服务入境游）

2. **知识库扩展**
   - 建立全球目的地知识库
   - 自动化知识采集流程

3. **资源整合**
   - 对接酒店、机票、门票供应商
   - 实现一键预订

4. **AI 产品经理模式**
   - 8条内部判断规则深度集成
   - 自动风险评估与降级

---

## 👥 联系方式

如有问题，请联系：
- 项目负责人：[你的名字]
- 邮箱：[你的邮箱]
- GitHub: [你的仓库链接]

---

## 📄 许可证

[MIT License]

---

**交付日期**: 2025-01-XX
**版本**: v1.0.0
