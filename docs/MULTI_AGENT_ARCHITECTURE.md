# 多Agent架构文档

## 📐 架构概览

本系统实现了从单一Agent向多Agent系统的演进，采用**层级协调式架构**，通过协调器（Coordinator）管理多个专业Agent的协作。

```
用户输入 → 协调器 → [行程Agent | 预订Agent] → 输出结果
```

---

## 🏗️ 系统组件

### 1. 行程Agent（ItineraryAgent）

**文件**: `src/agents/itinerary_agent.py`

**职责**:
- 理解用户旅行需求
- 生成结构化行程方案
- 提供实时信息查询（天气、交通、景点等）
- 管理用户历史和偏好

**工具**:
- `web_search_tool`: 联网搜索
- `user_memory_tool`: 用户记忆管理
- `weather_tool`: 天气查询
- `map_tool`: 地图服务
- `booking_tool`: 酒店和票务搜索（仅搜索，不预订）

**配置**: `config/agent_llm_config.json`
- 模型: doubao-seed-1-6-thinking-250715
- 温度: 0.7（创造性）
- 思考模式: enabled

---

### 2. 预订Agent（BookingAgent）

**文件**: `src/agents/booking_agent.py`

**职责**:
- 接收行程JSON
- 执行酒店预订
- 执行门票预订
- 处理预订查询和取消

**工具**:
- `book_hotel`: 预订酒店
- `cancel_hotel_booking`: 取消酒店预订
- `query_hotel_booking`: 查询酒店预订
- `book_ticket`: 预订门票
- `cancel_ticket_booking`: 取消门票预订
- `query_ticket_booking`: 查询门票预订

**配置**: `config/booking_agent_config.json`
- 模型: doubao-seed-1-6-thinking-250715
- 温度: 0.3（精确执行）
- 思考模式: enabled

---

### 3. 协调器（Coordinator）

**文件**: `src/agents/coordinator.py`

**职责**:
- 管理Agent协作流程
- 维护系统状态
- 决策Agent调用顺序
- 汇总各Agent结果

**状态机**:
```
collect_info → planning → booking → completed
     ↓
    error
```

**状态说明**:
- `collect_info`: 收集用户信息
- `planning`: 行程规划阶段
- `booking`: 预订执行阶段
- `completed`: 流程完成
- `error`: 错误状态

---

### 4. 多Agent系统入口

**文件**: `src/agents/multi_agent.py`

**接口**:
```python
class MultiAgentSystem:
    async def run(user_input: str, config: dict) -> str
    def get_state() -> dict
    def reset()
```

**使用示例**:
```python
from agents.multi_agent import multi_agent_system

result = await multi_agent_system.run(
    "规划东京3天旅行",
    config={"configurable": {"thread_id": "user-123"}}
)
```

---

## 📦 文件结构

```
src/
├── agents/
│   ├── agent.py                    # 单一Agent模式（向后兼容）
│   ├── itinerary_agent.py          # 行程Agent
│   ├── booking_agent.py            # 预订Agent
│   ├── coordinator.py              # 协调器
│   └── multi_agent.py             # 多Agent系统入口
├── tools/
│   ├── hotel_booking_tool.py       # 酒店预订工具
│   ├── ticket_booking_tool.py      # 门票预订工具
│   ├── weather_tool.py             # 天气工具
│   ├── map_tool.py                 # 地图工具
│   ├── user_memory_tool.py         # 用户记忆工具
│   └── web_search_tool.py          # 搜索工具
└── storage/
    └── database/                   # 数据库模型和存储

config/
├── agent_llm_config.json           # 行程Agent配置
└── booking_agent_config.json       # 预订Agent配置

tests/
└── test_multi_agent.py             # 多Agent测试

docs/
└── MULTI_AGENT_ARCHITECTURE.md     # 本文档
```

---

## 🔄 数据流

### 完整流程

```
1. 用户输入
   "规划东京3天旅行，喜欢美食"

2. 协调器接收
   状态: collect_info → planning

3. 调用行程Agent
   输入: 用户需求
   输出: 行程JSON
   {
     "user_profile": {...},
     "itinerary": [...],
     "ai_analysis": {...}
   }

4. 协调器解析行程JSON
   提取需要预订的酒店和门票

5. 用户确认
   "是的，请帮我预订"

6. 协调器状态
   planning → booking

7. 调用预订Agent
   输入: 预订请求
   输出: 订单号和预订结果

8. 协调器汇总
   状态: booking → completed

9. 返回最终结果
   - 行程方案
   - 预订确认
   - 订单号
   - 注意事项
```

---

## 🔧 技术细节

### Agent通信

**消息格式**: 使用 LangChain 的 `MessagesState`

**配置传递**:
```python
config = {
    "configurable": {
        "thread_id": "unique-thread-id"
    }
}
```

### 状态管理

**协调器状态**:
```python
class CoordinatorState(TypedDict):
    stage: Literal["collect_info", "planning", "booking", "completed", "error"]
    user_input: str
    itinerary_json: Optional[dict]
    booking_results: Optional[dict]
    current_agent: Optional[str]
    error_message: Optional[str]
```

**记忆管理**:
- 使用 LangGraph 的 `MemorySaver`
- 滑动窗口保留最近40条消息
- 支持跨轮对话

### 错误处理

**错误恢复机制**:
1. 单个Agent失败不影响其他Agent
2. 协调器捕获异常并记录
3. 返回清晰的错误信息给用户

**重试策略**:
- 预订失败：提示用户重试或联系客服
- 行程生成失败：重新询问用户需求

---

## 🚀 扩展性

### 添加新Agent

**步骤**:
1. 创建新的Agent文件（如 `src/agents/payment_agent.py`）
2. 定义Agent职责和工具
3. 在协调器中注册新Agent
4. 更新状态机（如果需要）

**示例**:
```python
# src/agents/payment_agent.py
def build_payment_agent(ctx=None):
    return create_agent(
        model=llm,
        system_prompt="你是支付专员...",
        tools=[process_payment, refund_payment]
    )

# src/agents/coordinator.py
def __init__(self):
    self.payment_agent = build_payment_agent()
    # ...
```

### 工具扩展

**添加新工具**:
1. 在 `src/tools/` 创建工具文件
2. 使用 `@tool` 装饰器
3. 在对应Agent中注册工具

---

## 📊 性能优化

### 当前性能

| 指标 | 单一Agent | 多Agent |
|------|----------|---------|
| 平均响应时间 | ~30s | ~45s |
| 代码复杂度 | 低 | 中 |
| 可维护性 | 中 | 高 |
| 扩展性 | 低 | 高 |

### 优化建议

1. **并行调用**: 对于独立的Agent，可以并行执行
   ```python
   # 并行调用行程和预订Agent
   itinerary_task = self.itinerary_agent.ainvoke(...)
   booking_task = self.booking_agent.ainvoke(...)
   await asyncio.gather(itinerary_task, booking_task)
   ```

2. **缓存策略**: 缓存常用查询结果（天气、景点信息）

3. **模型选择**: 不同Agent使用不同规模的模型
   - 行程Agent: 大模型（创造性）
   - 预订Agent: 中等模型（精确执行）

---

## 🧪 测试

### 测试文件

**文件**: `tests/test_multi_agent.py`

**测试用例**:
1. 多Agent协作流程
2. 预订Agent直接调用
3. 错误处理

**运行测试**:
```bash
python tests/test_multi_agent.py
```

### 预期输出

```
============================================================
🧪 测试多Agent协作流程
============================================================

✅ 行程规划完成
[行程方案...]

✅ 预订完成
[预订结果...]

📊 系统状态:
  - 阶段: completed
  - 当前Agent: booking_agent
  - 行程JSON: 已生成
  - 预订结果: 已完成
```

---

## 📝 最佳实践

### 1. 职责分离
- 每个Agent只负责一个领域
- 避免Agent功能重叠

### 2. 工具设计
- 工具应该原子化
- 提供清晰的错误信息

### 3. 配置管理
- 不同Agent使用独立配置
- 配置文件命名清晰

### 4. 状态管理
- 使用明确的状态机
- 记录状态转换日志

### 5. 错误处理
- 捕获所有异常
- 返回用户友好的错误信息

---

## 🔮 未来演进

### 阶段2：添加更多Agent
- **支付Agent**: 处理支付和退款
- **派单Agent**: 导游和司机派单
- **财务Agent**: 财务报表生成
- **运维Agent**: 系统监控和自动修复

### 阶段3：引入事件总线
- 使用消息队列（Kafka/RabbitMQ）
- 实现异步事件处理
- 支持分布式部署

### 阶段4：AI编排
- 使用 LangGraph 的 Subgraph
- 实现复杂的Agent编排逻辑
- 支持条件分支和循环

---

## 📚 参考资料

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Multi-Agent Systems Design](https://arxiv.org/abs/2308.03262)

---

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**文档版本**: v1.0
**最后更新**: 2025-01-12
**作者**: Coze Coding Team
