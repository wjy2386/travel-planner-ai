# AI旅行规划助手 - 前端使用指南

## 概述

本系统提供了一个简洁的Web前端界面，用于与多Agent旅行规划系统进行交互。前端界面采用HTML+CSS+JavaScript构建，通过REST API与后端的多Agent系统（行程Agent + 预订Agent）通信。

## 技术架构

### 前端技术栈
- **HTML5**: 页面结构
- **CSS3**: 响应式设计，渐变背景，动画效果
- **JavaScript (ES6+)**: 前端逻辑，Fetch API
- **Marked.js**: Markdown渲染
- **Highlight.js**: 代码高亮

### 后端技术栈
- **FastAPI**: Web框架和REST API
- **LangGraph**: 多Agent状态管理
- **PostgreSQL**: 会话记忆存储

### 系统架构
```
用户浏览器
    ↓ (HTTP请求)
FastAPI Server (/api/chat)
    ↓
多Agent协调器 (TravelCoordinator)
    ↓
├─ 行程Agent (ItineraryAgent) → 行程规划
└─ 预订Agent (BookingAgent) → 酒店票务预订
```

## 功能特性

### 1. 聊天界面
- 实时对话交互
- Markdown格式的响应渲染
- 支持代码高亮
- 消息动画效果

### 2. 多Agent协作
- **行程Agent**: 负责规划旅行行程，查询景点、交通等信息
- **预订Agent**: 负责执行酒店和票务预订操作
- **协调器**: 管理多Agent的工作流程（信息收集 → 规划 → 预订 → 完成）

### 3. 状态管理
- 实时显示当前处理阶段
- 显示正在工作的Agent
- 会话记忆支持（PostgreSQL）

### 4. 快捷操作
- 预设旅行场景按钮
- 一键填充旅行需求
- 键盘快捷键（Enter发送，Shift+Enter换行）

## 快速开始

### 启动服务

```bash
# 方式1：使用main.py启动（开发模式）
cd /workspace/projects
python src/main.py -m http -p 5000

# 方式2：使用uvicorn直接启动
cd /workspace/projects
uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload
```

### 访问前端

启动服务后，在浏览器中打开：

```
http://localhost:5000
```

或

```
http://your-server-ip:5000
```

## API接口说明

### POST /api/chat

聊天接口，用于发送用户消息并获取AI响应。

**请求参数**:
```json
{
  "message": "我想去东京旅行4天，喜欢历史文化",
  "session_id": "unique_session_id"
}
```

**响应示例**:
```json
{
  "response": "✅ 行程规划完成\n\n你好！很高兴能为你规划旅行...",
  "session_id": "unique_session_id",
  "run_id": "run_id_value",
  "status": "booking",
  "current_agent": "itinerary_agent"
}
```

**状态说明**:
- `collect_info`: 信息收集阶段
- `planning`: 行程规划阶段
- `booking`: 预订阶段
- `completed`: 完成阶段
- `error`: 错误状态

## 使用示例

### 场景1：规划东京旅行

1. 在输入框中输入："我想去东京旅行4天，喜欢历史文化，预算中等"
2. 点击"发送"按钮
3. 系统将调用行程Agent规划行程
4. 系统询问是否需要预订
5. 回复"是的，请帮我预订"
6. 系统调用预订Agent执行预订
7. 获得最终的预订结果

### 场景2：使用快捷按钮

1. 点击"🗼 东京4日游"按钮
2. 输入框自动填充预设文本
3. 点击"发送"按钮开始交互

## 前端文件结构

```
static/
├── index.html          # 主页面
├── style.css           # 样式文件
└── app.js              # JavaScript逻辑
```

### index.html
- 定义页面结构
- 引入外部库（Marked.js, Highlight.js）
- 包含聊天容器、输入区域、状态栏等组件

### style.css
- 响应式布局
- 渐变背景设计
- 消息气泡样式
- 动画效果
- 加载状态样式

### app.js
- API调用逻辑
- 消息渲染（Markdown）
- 状态管理
- 会话管理

## 自定义配置

### 修改端口

编辑 `src/main.py` 或使用命令行参数：

```bash
python src/main.py -m http -p 8080
```

### 修改样式

编辑 `static/style.css` 文件，可以自定义：
- 颜色主题（修改CSS变量）
- 字体大小
- 布局间距
- 动画效果

### 添加新的快捷按钮

编辑 `static/index.html` 中的 `quick-actions` 部分：

```html
<button class="quick-btn" onclick="setInput('你的自定义文本')">
    🏖️ 自定义场景
</button>
```

## 测试

运行前端测试：

```bash
cd /workspace/projects
python -m pytest tests/test_frontend.py -v -s
```

测试内容包括：
- 根端点访问测试
- 静态文件服务测试
- 聊天API端点测试
- 对话流程测试
- 健康检查测试

## 注意事项

1. **数据库依赖**: 系统需要PostgreSQL数据库支持记忆功能，确保数据库连接配置正确
2. **环境变量**: 确保以下环境变量已设置：
   - `COZE_WORKSPACE_PATH`: 工作空间路径
   - `COZE_WORKLOAD_IDENTITY_API_KEY`: API密钥
   - `COZE_INTEGRATION_MODEL_BASE_URL`: 模型API地址
3. **超时设置**: 默认请求超时时间为15分钟（900秒），可在 `src/main.py` 中修改 `TIMEOUT_SECONDS` 常量
4. **并发支持**: 前端通过 `session_id` 支持多用户并发会话

## 常见问题

### Q1: 页面无法加载
A: 检查服务是否已启动，确认端口是否正确（默认5000）

### Q2: API调用失败
A: 检查后端日志，确认：
- 数据库连接是否正常
- API密钥是否配置正确
- 模型服务是否可用

### Q3: 消息显示异常
A: 确保Marked.js和Highlight.js库已正确加载，检查浏览器控制台是否有JavaScript错误

### Q4: 会话记忆不工作
A: 检查PostgreSQL数据库配置，确认 `thread_id` 是否正确传递

## 未来优化方向

1. **流式响应**: 实现SSE（Server-Sent Events）流式输出，提升用户体验
2. **更多快捷场景**: 添加更多预设旅行场景
3. **历史记录**: 显示对话历史记录
4. **导出功能**: 支持导出行程为PDF或Word文档
5. **地图集成**: 集成地图显示行程路线
6. **多语言支持**: 添加国际化支持

## 技术支持

如有问题，请查看：
- 项目文档: `/docs`
- 测试用例: `/tests/test_frontend.py`
- 后端日志: `/app/work/logs/bypass/app.log`

---

**开发者**: AI Agent搭建专家
**最后更新**: 2026-01-12
