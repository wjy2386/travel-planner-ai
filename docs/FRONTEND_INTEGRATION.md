# 前端集成指南 - Lovable与多Agent系统

## 📋 目录
1. [架构概览](#架构概览)
2. [后端API部署](#后端api部署)
3. [前端集成方法](#前端集成方法)
4. [调用示例](#调用示例)
5. [最佳实践](#最佳实践)
6. [常见问题](#常见问题)

---

## 架构概览

```
┌─────────────────┐         HTTP/WebSocket         ┌──────────────────┐
│  Lovable前端    │ ────────────────────────────→ │  FastAPI后端     │
│  (React/Vue)    │                               │  (Python)        │
└────────┬────────┘                               └────────┬─────────┘
         │                                                 │
         │                                                 ↓
         │                                          ┌──────────────┐
         │                                          │ 多Agent系统   │
         │                                          │ (LangGraph)  │
         │                                          └──────────────┘
         │                                                 │
         │                                                 ↓
         │                                          ┌──────────────┐
         └────────────────────────────────────────→ │ 大模型服务   │
                                                    │ (豆包)       │
                                                    └──────────────┘
```

---

## 后端API部署

### 1. 安装依赖

```bash
pip install fastapi uvicorn websockets python-multipart
```

### 2. 启动FastAPI服务器

**开发模式（支持热重载）：**
```bash
cd /workspace/projects
PYTHONPATH=/workspace/projects/src python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式：**
```bash
cd /workspace/projects
PYTHONPATH=/workspace/projects/src python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 验证API是否正常运行

```bash
curl http://localhost:8000/
```

预期返回：
```json
{
  "name": "旅行规划Agent API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {...}
}
```

---

## 前端集成方法

### 方法1：RESTful API调用（推荐）

适合大多数场景，简单易用。

**API端点：**
- `POST /api/v1/plan` - 创建行程（同步）
- `POST /api/v1/plan/stream` - 创建行程（流式输出）
- `GET /api/v1/state` - 获取系统状态
- `POST /api/v1/reset` - 重置系统

### 方法2：WebSocket实时通信

适合需要实时展示生成进度的场景。

**WebSocket端点：**
- `WS /ws/{client_id}` - WebSocket连接

---

## 调用示例

### 1. 同步调用示例

**前端代码（JavaScript/TypeScript）：**

```typescript
// 发送行程规划请求
async function planItinerary(userInput: string, sessionId?: string) {
  const response = await fetch('http://localhost:8000/api/v1/plan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_input: userInput,
      session_id: sessionId || `session_${Date.now()}`
    })
  });

  const result = await response.json();

  if (result.success) {
    // 显示行程结果
    console.log('行程规划成功:', result.data.itinerary);
    return result.data.itinerary;
  } else {
    // 显示错误信息
    console.error('行程规划失败:', result.error);
    throw new Error(result.error);
  }
}

// 使用示例
planItinerary('我想去东京旅游，计划3天，喜欢历史文化和美食')
  .then(itinerary => {
    // 渲染行程
    document.getElementById('result').innerHTML = itinerary;
  })
  .catch(error => {
    console.error(error);
  });
```

**Lovable组件示例：**

```jsx
// ItineraryPlanner.jsx
import React, { useState } from 'react';

export default function ItineraryPlanner() {
  const [userInput, setUserInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePlan = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userInput,
          session_id: `user_${Date.now()}`
        })
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.data.itinerary);
      } else {
        setError(data.error || '规划失败');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">智能行程规划</h1>
      
      <textarea
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="告诉我你的旅行需求..."
        className="w-full p-4 border rounded-lg mb-4 h-32"
      />
      
      <button
        onClick={handlePlan}
        disabled={loading || !userInput}
        className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? '规划中...' : '开始规划'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 p-6 bg-gray-50 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">行程方案</h2>
          <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: result }} />
        </div>
      )}
    </div>
  );
}
```

### 2. 流式输出示例

**前端代码（JavaScript）：**

```javascript
// 流式接收行程规划结果
async function planItineraryStream(userInput: string) {
  const response = await fetch('http://localhost:8000/api/v1/plan/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // 保留未完成的行

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        switch (data.type) {
          case 'start':
            console.log('开始规划...');
            break;
          case 'stage':
            console.log(`当前阶段: ${data.stage}`);
            break;
          case 'progress':
            console.log(`进度: ${data.message}`);
            break;
          case 'complete':
            console.log('完成:', data.data);
            return data.data;
          case 'error':
            console.error('错误:', data.error);
            throw new Error(data.error);
        }
      }
    }
  }
}
```

**Lovable组件示例（带进度条）：**

```jsx
// ItineraryPlannerStream.jsx
import React, { useState, useEffect } from 'react';

export default function ItineraryPlannerStream() {
  const [userInput, setUserInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('');
  const [progress, setProgress] = useState(0);

  const handlePlan = async () => {
    setLoading(true);
    setStage('');
    setProgress(0);
    setResult('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/plan/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case 'start':
                setStage('开始规划...');
                break;
              case 'stage':
                setStage(getStageName(data.stage));
                setProgress(data.progress || 0);
                break;
              case 'complete':
                setResult(data.data);
                setProgress(100);
                break;
              case 'error':
                throw new Error(data.error);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStageName = (stage: string) => {
    const stageMap = {
      'analysis': '分析需求',
      'planning': '规划行程',
      'validation': '校验可行性',
      'delivery': '生成说明'
    };
    return stageMap[stage] || stage;
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">智能行程规划</h1>
      
      <textarea
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="告诉我你的旅行需求..."
        className="w-full p-4 border rounded-lg mb-4 h-32"
      />
      
      <button
        onClick={handlePlan}
        disabled={loading || !userInput}
        className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? '规划中...' : '开始规划'}
      </button>

      {loading && (
        <div className="mt-4">
          <div className="text-sm text-gray-600 mb-2">{stage}</div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {result && (
        <div className="mt-6 p-6 bg-gray-50 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">行程方案</h2>
          <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: result }} />
        </div>
      )}
    </div>
  );
}
```

### 3. WebSocket实时通信示例

```javascript
// WebSocket连接示例
function connectWebSocket(clientId) {
  const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

  ws.onopen = () => {
    console.log('WebSocket连接成功');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case 'connected':
        console.log(data.message);
        break;
      case 'state_update':
        console.log('状态更新:', data.data);
        break;
      case 'stage_update':
        console.log(`阶段更新: ${data.stage} (${data.progress}%)`);
        break;
      case 'complete':
        console.log('完成:', data.data);
        ws.close();
        break;
      case 'error':
        console.error('错误:', data.error);
        ws.close();
        break;
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket连接关闭');
  };

  return ws;
}

// 使用示例
const ws = connectWebSocket(`client_${Date.now()}`);

// 发送行程规划请求
setTimeout(() => {
  ws.send(JSON.stringify({
    action: 'plan_itinerary',
    user_input: '我想去东京旅游，计划3天'
  }));
}, 1000);
```

---

## 最佳实践

### 1. 错误处理

```javascript
try {
  const response = await fetch('http://localhost:8000/api/v1/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || '未知错误');
  }

  return data.data;
} catch (error) {
  console.error('API调用失败:', error);
  // 显示用户友好的错误提示
  alert('行程规划失败，请稍后重试');
}
```

### 2. 会话管理

```javascript
// 使用session_id保持上下文
let sessionId = localStorage.getItem('travel_session_id');

if (!sessionId) {
  sessionId = `session_${Date.now()}`;
  localStorage.setItem('travel_session_id', sessionId);
}

// 所有请求都携带session_id
fetch('http://localhost:8000/api/v1/plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_input: userInput,
    session_id: sessionId
  })
});
```

### 3. 加载状态

```jsx
// 显示加载动画
{loading && (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
    <span className="ml-4 text-gray-600">AI正在规划您的专属行程...</span>
  </div>
)}
```

### 4. 结果渲染（Markdown）

```bash
# 安装markdown渲染库
npm install react-markdown
```

```jsx
import ReactMarkdown from 'react-markdown';

<ReactMarkdown className="prose max-w-none">
  {result}
</ReactMarkdown>
```

---

## 常见问题

### Q1: 跨域问题怎么办？

**A:** FastAPI已经配置了CORS，如果仍有问题，修改`src/api/main.py`：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-lovable-app.com"],  # 替换为你的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q2: 如何部署到生产环境？

**A:** 推荐使用Docker + Nginx：

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Q3: 如何处理超时？

**A:** 前端设置超时时间：

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒超时

try {
  const response = await fetch('http://localhost:8000/api/v1/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput }),
    signal: controller.signal
  });
  clearTimeout(timeoutId);
  // 处理响应...
} catch (error) {
  if (error.name === 'AbortError') {
    alert('请求超时，请稍后重试');
  }
}
```

### Q4: 如何实现对话历史？

**A:** 使用session_id保持上下文：

```javascript
// 每次请求都使用相同的session_id
const sessionId = 'user_12345';

// 第一次请求
fetch('http://localhost:8000/api/v1/plan', {
  method: 'POST',
  body: JSON.stringify({
    user_input: '我想去东京旅游',
    session_id: sessionId
  })
});

// 第二次请求（基于上下文）
fetch('http://localhost:8000/api/v1/plan', {
  method: 'POST',
  body: JSON.stringify({
    user_input: '能不能加一个迪士尼的行程',
    session_id: sessionId
  })
});
```

---

## 总结

通过以上集成方案，你可以轻松将Lovable前端与多Agent后端连接起来：

1. ✅ 启动FastAPI后端服务
2. ✅ 在Lovable中创建React组件
3. ✅ 使用fetch调用API
4. ✅ 渲染Markdown格式的行程结果
5. ✅ 实现加载状态和错误处理

如有问题，请参考[FastAPI文档](https://fastapi.tiangolo.com/)或查看项目代码。
