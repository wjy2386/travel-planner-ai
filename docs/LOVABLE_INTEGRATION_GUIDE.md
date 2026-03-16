# 🚀 Lovable 集成完整指南

## 📋 目录

1. [项目概览](#项目概览)
2. [前置准备](#前置准备)
3. [Lovable 项目创建](#lovable-项目创建)
4. [前端架构设计](#前端架构设计)
5. [API 集成详解](#api-集成详解)
6. [组件开发](#组件开发)
7. [状态管理](#状态管理)
8. [部署方案](#部署方案)
9. [测试与调试](#测试与调试)

---

## 项目概览

### 后端 API 接口

| 端点 | 方法 | 说明 | 用途 |
|------|------|------|------|
| `/api/chat` | POST | 聊天接口 | 同步对话 |
| `/run` | POST | 同步运行 | 完整行程生成 |
| `/stream_run` | POST | 流式运行 | SSE 实时响应 |
| `/` | GET | 前端页面 | Web 界面 |

### 技术栈

- **前端**：React + TypeScript + Tailwind CSS
- **后端**：FastAPI + LangGraph + LangChain
- **通信**：RESTful API + SSE（Server-Sent Events）
- **部署**：Vercel（前端）+ Railway/Fly.io（后端）

---

## 前置准备

### 1. 环境要求

- Node.js 18+
- Python 3.9+
- Git
- Lovable 账号（https://lovable.dev）

### 2. 启动后端服务

```bash
cd /workspace/projects
python src/main.py -m http -p 5000
```

验证后端运行：
```bash
curl http://localhost:5000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "测试", "session_id": "test123"}'
```

---

## Lovable 项目创建

### 步骤 1：创建新项目

1. 访问 Lovable：https://lovable.dev
2. 点击 **"New Project"**
3. 选择 **"Blank Project"**
4. 填写项目信息：
   - **Project Name**: `Travel Planner AI`
   - **Description**: `AI-powered travel planning assistant with multi-agent orchestration`

### 步骤 2：配置项目

在 Lovable 编辑器中，配置以下内容：

#### 2.1 安装依赖

在 Lovable 的 **Dependencies** 面板添加：

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.300.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

#### 2.2 配置环境变量

在 **Environment Variables** 面板添加：

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_NAME=Travel Planner AI
```

---

## 前端架构设计

### 目录结构

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   └── Skeleton.tsx
│   ├── Chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── ChatInput.tsx
│   │   └── QuickActions.tsx
│   ├── Itinerary/
│   │   ├── ItineraryCard.tsx
│   │   ├── DaySchedule.tsx
│   │   ├── ActivityItem.tsx
│   │   └── BudgetSummary.tsx
│   └── Layout/
│       ├── Header.tsx
│       ├── Footer.tsx
│       └── Sidebar.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useSSE.ts
│   └── useLocalStorage.ts
├── services/
│   ├── api.ts
│   └── sse.ts
├── types/
│   ├── chat.ts
│   ├── itinerary.ts
│   └── api.ts
├── utils/
│   ├── cn.ts
│   └── markdown.ts
├── App.tsx
└── main.tsx
```

---

## API 集成详解

### 1. 创建 API 服务

在 `src/services/api.ts` 中：

```typescript
// src/services/api.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  run_id: string;
  status: string;
  current_agent: string;
}

export interface RunRequest {
  destination: string;
  duration: number;
  travel_style: '自由行' | '包车';
  budget?: number;
  participants: Array<{
    type: 'adult' | 'child';
    count: number;
    age?: number;
  }>;
  preferences: string[];
}

export interface RunResponse {
  run_id: string;
  result: any;
  status: string;
}

/**
 * 聊天接口 - 同步对话
 */
export async function chat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 同步运行 - 完整行程生成
 */
export async function run(request: RunRequest): Promise<RunResponse> {
  const response = await fetch(`${API_BASE_URL}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Run API error: ${response.statusText}`);
  }

  return response.json();
}
```

### 2. 创建 SSE 服务

在 `src/services/sse.ts` 中：

```typescript
// src/services/sse.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface SSEMessage {
  type: 'message' | 'error' | 'end';
  data: any;
}

/**
 * 流式运行 - SSE 实时响应
 */
export function createSSEConnection(
  request: any,
  onMessage: (message: SSEMessage) => void,
  onError: (error: Error) => void,
  onComplete: () => void
): () => void {
  const eventSource = new EventSource(
    `${API_BASE_URL}/stream_run?${new URLSearchParams(request)}`
  );

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage({
        type: 'message',
        data,
      });
    } catch (error) {
      onMessage({
        type: 'error',
        data: { message: 'Failed to parse message' },
      });
    }
  };

  eventSource.onerror = (error) => {
    onError(new Error('SSE connection error'));
    eventSource.close();
  };

  // 返回清理函数
  return () => {
    eventSource.close();
  };
}
```

---

## 组件开发

### 1. 聊天容器组件

在 `src/components/Chat/ChatContainer.tsx` 中：

```typescript
// src/components/Chat/ChatContainer.tsx

import React, { useState, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { QuickActions } from './QuickActions';
import { useChat } from '../../hooks/useChat';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: '你好！我是你的AI旅行规划助手。请告诉我你想去哪里旅行？',
      timestamp: new Date(),
    },
  ]);
  
  const { sendMessage, isLoading } = useChat();
  const [sessionId] = useState(() => `session_${Date.now()}`);

  const handleSendMessage = async (message: string) => {
    // 添加用户消息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // 发送到后端
    try {
      const response = await sendMessage({
        message,
        session_id: sessionId,
      });

      // 添加助手消息
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleQuickAction = (message: string) => {
    handleSendMessage(message);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && (
          <div className="flex justify-center">
            <div className="animate-pulse text-gray-500">
              AI 正在思考...
            </div>
          </div>
        )}
      </div>

      {/* 快捷操作 */}
      <QuickActions onAction={handleQuickAction} />

      {/* 输入框 */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
```

### 2. 消息气泡组件

在 `src/components/Chat/MessageBubble.tsx` 中：

```typescript
// src/components/Chat/MessageBubble.tsx

import React from 'react';
import { cn } from '../../utils/cn';

interface MessageBubbleProps {
  message: {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
  };
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div
      className={cn(
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[70%] rounded-lg px-4 py-2 shadow-sm',
          isUser
            ? 'bg-blue-500 text-white'
            : isSystem
            ? 'bg-gray-200 text-gray-800'
            : 'bg-white text-gray-800 border border-gray-200'
        )}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div
          className={cn(
            'text-xs mt-1',
            isUser ? 'text-blue-100' : 'text-gray-500'
          )}
        >
          {message.timestamp.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
```

### 3. 输入框组件

在 `src/components/Chat/ChatInput.tsx` 中：

```typescript
// src/components/Chat/ChatInput.tsx

import React, { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '../ui/Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <div className="flex gap-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的旅行需求..."
          className="flex-1 resize-none rounded-lg border border-gray-300 p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
          rows={2}
          disabled={disabled}
        />
        <Button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          className="px-6"
        >
          <Send className="h-4 w-4 mr-2" />
          发送
        </Button>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        按 Enter 发送，Shift+Enter 换行
      </p>
    </div>
  );
}
```

### 4. 快捷操作组件

在 `src/components/Chat/QuickActions.tsx` 中：

```typescript
// src/components/Chat/QuickActions.tsx

import React from 'react';
import { Plane, Mountain, Building } from 'lucide-react';
import { Button } from '../ui/Button';

interface QuickActionsProps {
  onAction: (message: string) => void;
}

const quickActions = [
  {
    icon: Plane,
    label: '东京4日游',
    message: '我想去东京旅行4天，喜欢历史文化，预算中等',
  },
  {
    icon: Building,
    label: '巴黎3日游',
    message: '我想去巴黎旅行3天，喜欢艺术和美食',
  },
  {
    icon: Mountain,
    label: '大理5日游',
    message: '我想去云南大理旅行5天，喜欢自然风光',
  },
];

export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <div className="border-t bg-gray-50 p-4">
      <p className="text-sm text-gray-600 mb-2">快捷操作：</p>
      <div className="flex gap-2">
        {quickActions.map((action) => (
          <Button
            key={action.label}
            variant="outline"
            size="sm"
            onClick={() => onAction(action.message)}
            className="flex items-center gap-2"
          >
            <action.icon className="h-4 w-4" />
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
```

---

## 状态管理

### 1. 创建 useChat Hook

在 `src/hooks/useChat.ts` 中：

```typescript
// src/hooks/useChat.ts

import { useState } from 'react';
import { chat, ChatRequest, ChatResponse } from '../services/api';

export function useChat() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await chat(request);
      setIsLoading(false);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      setIsLoading(false);
      throw error;
    }
  };

  return {
    sendMessage,
    isLoading,
    error,
  };
}
```

### 2. 创建 useSSE Hook

在 `src/hooks/useSSE.ts` 中：

```typescript
// src/hooks/useSSE.ts

import { useState, useEffect, useRef } from 'react';
import { createSSEConnection, SSEMessage } from '../services/sse';

export function useSSE(request: any) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    const cleanup = createSSEConnection(
      request,
      (message) => {
        setMessages((prev) => [...prev, message]);
      },
      (err) => {
        setError(err);
        setIsConnected(false);
      },
      () => {
        setIsConnected(false);
      }
    );

    cleanupRef.current = cleanup;
    setIsConnected(true);

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [request]);

  return {
    messages,
    error,
    isConnected,
  };
}
```

---

## 部署方案

### 方案 1：Vercel（推荐）

#### 步骤 1：准备项目

在项目根目录创建 `vercel.json`：

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "react",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "http://your-backend-url:5000/api/$1"
    }
  ]
}
```

#### 步骤 2：部署到 Vercel

1. 访问 Vercel：https://vercel.com
2. 点击 **"New Project"**
3. 导入你的 GitHub 仓库
4. 配置环境变量：
   ```
   VITE_API_BASE_URL=https://your-backend-url.railway.app
   ```
5. 点击 **"Deploy"**

#### 步骤 3：配置域名

在 Vercel 项目设置中：
- 添加自定义域名（如 `travel-planner.yourdomain.com`）
- 配置 DNS 记录

---

### 方案 2：Railway（后端部署）

#### 步骤 1：创建 Railway 项目

1. 访问 Railway：https://railway.app
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 选择你的仓库

#### 步骤 2：配置环境变量

在 Railway 项目设置中添加：

```env
DATABASE_URL=postgresql://...
COZE_WORKLOAD_IDENTITY_API_KEY=your_key
COZE_INTEGRATION_MODEL_BASE_URL=https://...
```

#### 步骤 3：添加启动命令

在 `railway.toml` 中：

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python src/main.py -m http -p $PORT"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

---

### 方案 3：Docker 部署（全栈）

#### 步骤 1：创建 Docker Compose

在项目根目录创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://backend:5000

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/travel_planner
      - COZE_WORKLOAD_IDENTITY_API_KEY=${COZE_API_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: travel_planner
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 步骤 2：部署

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 测试与调试

### 1. 本地测试

#### 测试 API 连接

创建 `test-api.ts`：

```typescript
// test-api.ts

import { chat, run } from './src/services/api';

async function testAPI() {
  try {
    // 测试聊天接口
    const chatResponse = await chat({
      message: '测试消息',
      session_id: 'test_123',
    });
    console.log('Chat response:', chatResponse);

    // 测试运行接口
    const runResponse = await run({
      destination: '云南',
      duration: 7,
      travel_style: '自由行',
      budget: 10000,
      participants: [
        { type: 'adult', count: 2 },
        { type: 'child', count: 1, age: 6 },
      ],
      preferences: ['自然', '美食'],
    });
    console.log('Run response:', runResponse);
  } catch (error) {
    console.error('API test failed:', error);
  }
}

testAPI();
```

#### 测试 SSE 连接

创建 `test-sse.ts`：

```typescript
// test-sse.ts

import { createSSEConnection } from './src/services/sse';

const cleanup = createSSEConnection(
  { destination: '云南', duration: 7 },
  (message) => {
    console.log('Received message:', message);
  },
  (error) => {
    console.error('SSE error:', error);
  },
  () => {
    console.log('SSE connection closed');
  }
);

// 10秒后关闭连接
setTimeout(() => {
  cleanup();
}, 10000);
```

### 2. 前端测试

在浏览器控制台中测试：

```javascript
// 测试 API 连接
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '测试',
    session_id: 'test123'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🎯 完整示例：主应用

在 `src/App.tsx` 中：

```typescript
// src/App.tsx

import React from 'react';
import { ChatContainer } from './components/Chat/ChatContainer';
import { Header } from './components/Layout/Header';
import { Footer } from './components/Layout/Footer';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-1">
        <ChatContainer />
      </main>
      <Footer />
    </div>
  );
}

export default App;
```

---

## 📊 性能优化建议

### 1. 前端优化

- ✅ 使用 React.memo 优化组件渲染
- ✅ 使用虚拟滚动处理长消息列表
- ✅ 实现消息分页加载
- ✅ 使用 Web Workers 处理 Markdown 渲染

### 2. 网络优化

- ✅ 实现请求取消机制
- ✅ 添加请求重试逻辑
- ✅ 使用 CDN 加速静态资源
- ✅ 启用 Gzip 压缩

### 3. 用户体验

- ✅ 添加加载状态指示器
- ✅ 实现错误边界处理
- ✅ 添加离线缓存支持
- ✅ 优化移动端响应式设计

---

## 🎉 完成！

现在你已经完成了 Lovable 与项目的集成！

### 下一步

1. **在 Lovable 中创建项目**
2. **复制上述代码到对应文件**
3. **配置环境变量**
4. **启动开发服务器**
5. **测试功能**
6. **部署上线**

---

## 📞 需要帮助？

如果在集成过程中遇到问题：

1. **检查后端是否正常运行**
2. **验证 API 接口是否可访问**
3. **查看浏览器控制台错误信息**
4. **检查环境变量配置**

祝你开发顺利！🚀
