# ⚡ Lovable 快速启动指南（5分钟上手）

## 🎯 目标

在 **5 分钟内**完成 Lovable 前端与后端的对接。

---

## 📋 步骤概览

1. ✅ 启动后端（1分钟）
2. ✅ 创建 Lovable 项目（1分钟）
3. ✅ 复制代码（2分钟）
4. ✅ 测试运行（1分钟）

---

## 第 1 步：启动后端（1分钟）

### 在沙箱环境中启动

```bash
cd /workspace/projects
python src/main.py -m http -p 5000
```

### 验证后端运行

```bash
curl http://localhost:5000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "测试", "session_id": "test123"}'
```

**预期响应**：
```json
{
  "response": "你好！...",
  "session_id": "test123",
  "run_id": "...",
  "status": "completed",
  "current_agent": "..."
}
```

---

## 第 2 步：创建 Lovable 项目（1分钟）

### 2.1 访问 Lovable

访问：https://lovable.dev

### 2.2 创建新项目

1. 点击 **"New Project"**
2. 选择 **"Blank Project"**
3. 填写：
   - **Project Name**: `Travel Planner AI`
   - 点击 **"Create"**

### 2.3 配置环境变量

在 Lovable 编辑器左侧面板：

1. 找到 **"Environment Variables"**
2. 添加：
   ```
   VITE_API_BASE_URL = http://localhost:5000
   ```

---

## 第 3 步：复制代码（2分钟）

### 3.1 复制主应用代码

在 Lovable 编辑器中，打开 `App.tsx`，复制以下代码：

```typescript
// App.tsx

import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:5000';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'system',
      content: '你好！我是你的AI旅行规划助手。请告诉我你想去哪里旅行？',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}`);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // 添加用户消息
    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 发送到后端
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      // 添加助手消息
      const assistantMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        id: `error_${Date.now()}`,
        role: 'system',
        content: '抱歉，发生了错误。请稍后重试。',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    { label: '🗼 东京4日游', message: '我想去东京旅行4天，喜欢历史文化，预算中等' },
    { label: '🗼 巴黎3日游', message: '我想去巴黎旅行3天，喜欢艺术和美食' },
    { label: '🏔️ 大理5日游', message: '我想去云南大理旅行5天，喜欢自然风光' },
  ];

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f9fafb' }}>
      {/* 头部 */}
      <div style={{
        padding: '16px',
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
      }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          ✈️ AI旅行规划助手
        </h1>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' }}>
          多Agent协作系统 - 行程规划与预订
        </p>
      </div>

      {/* 消息列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
      }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '8px',
                backgroundColor: msg.role === 'user' ? '#3b82f6' : 
                                 msg.role === 'system' ? '#e5e7eb' : 'white',
                color: msg.role === 'user' ? 'white' : '#1f2937',
                border: msg.role === 'assistant' ? '1px solid #e5e7eb' : 'none',
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ textAlign: 'center', padding: '8px' }}>
            <div style={{ color: '#6b7280' }}>AI 正在思考...</div>
          </div>
        )}
      </div>

      {/* 快捷操作 */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: '#f9fafb',
        borderTop: '1px solid #e5e7eb',
      }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => {
                setInput(action.message);
                setTimeout(() => sendMessage(), 100);
              }}
              disabled={isLoading}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid #d1d5db',
                backgroundColor: 'white',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
              }}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* 输入框 */}
      <div style={{
        padding: '16px',
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的旅行需求..."
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              fontSize: '14px',
              resize: 'none',
            }}
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            style={{
              padding: '0 24px',
              borderRadius: '8px',
              backgroundColor: !input.trim() || isLoading ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              cursor: !input.trim() || isLoading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            发送
          </button>
        </div>
        <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
          按 Enter 发送，Shift+Enter 换行
        </p>
      </div>
    </div>
  );
}
```

### 3.2 保存并预览

点击右上角的 **"Preview"** 按钮。

---

## 第 4 步：测试运行（1分钟）

### 4.1 测试基本功能

1. **在输入框输入**：`我想去云南旅行7天`
2. **点击"发送"按钮**
3. **等待 AI 响应**

### 4.2 测试快捷操作

点击 **"🗼 东京4日游"** 按钮，查看自动填充并发送。

### 4.3 查看网络请求

在浏览器开发者工具中：
1. 打开 **Network** 标签
2. 查看 `/api/chat` 请求
3. 确认请求成功（状态码 200）

---

## 🎉 完成！

恭喜！你已经成功完成 Lovable 与后端的集成！

---

## 📊 验收清单

- ✅ 后端运行在 `http://localhost:5000`
- ✅ Lovable 项目创建成功
- ✅ 环境变量配置正确
- ✅ 代码复制到 `App.tsx`
- ✅ 前端预览正常
- ✅ 发送消息成功
- ✅ 接收到 AI 响应

---

## 🚀 下一步

### 进阶功能

1. **添加 Markdown 渲染**
2. **实现 SSE 流式输出**
3. **添加行程卡片展示**
4. **集成地图显示**
5. **添加用户认证**

### 部署上线

参考完整指南：`docs/LOVABLE_INTEGRATION_GUIDE.md`

---

## ⚠️ 常见问题

### 问题 1：CORS 错误

**症状**：浏览器控制台显示 `CORS policy` 错误

**解决**：在后端添加 CORS 支持

在 `src/main.py` 中添加：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 2：无法连接后端

**症状**：前端提示 "Failed to fetch"

**解决**：
1. 确认后端正在运行
2. 检查 `VITE_API_BASE_URL` 配置
3. 尝试在浏览器中访问 `http://localhost:5000`

### 问题 3：Lovable 预览白屏

**症状**：预览页面空白

**解决**：
1. 检查代码语法错误
2. 查看 Lovable 控制台错误信息
3. 确认所有依赖已安装

---

## 📞 需要帮助？

如果遇到问题：
1. 检查后端日志：`/app/work/logs/bypass/app.log`
2. 查看浏览器控制台
3. 参考：`docs/LOVABLE_INTEGRATION_GUIDE.md`

祝你开发顺利！🚀
