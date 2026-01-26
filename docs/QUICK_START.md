# 🚀 快速启动指南

## 一分钟启动后端API

### 1. 启动服务（Linux/Mac）

```bash
# 使用启动脚本（推荐）
cd /workspace/projects
chmod +x scripts/start_api.sh
./scripts/start_api.sh
```

### 2. 启动服务（Windows）

```bash
cd /workspace/projects
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 验证服务

```bash
curl http://localhost:8000/
```

预期返回：
```json
{
  "name": "旅行规划Agent API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 在Lovable中集成前端

### 方式1：复制React组件

1. 将 `docs/TravelPlanner.tsx` 复制到你的Lovable项目
2. 安装依赖：
   ```bash
   npm install react-markdown
   ```
3. 在页面中使用：
   ```jsx
   import TravelPlanner from './components/TravelPlanner';
   
   export default function Page() {
     return <TravelPlanner />;
   }
   ```

### 方式2：使用REST API

```javascript
// 简单调用示例
async function planItinerary(userInput) {
  const response = await fetch('http://localhost:8000/api/v1/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput })
  });
  
  const data = await response.json();
  return data.data.itinerary;
}
```

### 方式3：使用流式输出

```javascript
// 流式调用示例
async function planItineraryStream(userInput) {
  const response = await fetch('http://localhost:8000/api/v1/plan/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const text = decoder.decode(value);
    // 处理流式数据...
  }
}
```

---

## 测试API

### 使用curl测试

```bash
# 测试行程规划
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想去东京旅游，计划3天，喜欢历史文化和美食"
  }'
```

### 使用Postman测试

1. 创建POST请求
2. URL: `http://localhost:8000/api/v1/plan`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "user_input": "我想去东京旅游，计划3天，喜欢历史文化和美食"
   }
   ```
5. 发送请求

---

## Docker部署（可选）

### 构建镜像

```bash
docker build -t travel-agent-api .
```

### 运行容器

```bash
docker run -d -p 8000:8000 --name travel-api travel-agent-api
```

### 使用Docker Compose

```bash
docker-compose up -d
```

---

## 环境变量配置

创建 `.env` 文件：

```bash
# API配置
API_HOST=0.0.0.0
API_PORT=8000

# Coze集成
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn

# 数据库（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
```

---

## 常见问题

### Q: 端口8000被占用？

```bash
# 使用其他端口
python -m uvicorn src.api.main:app --port 8001
```

### Q: CORS跨域问题？

修改 `src/api/main.py` 中的 `allow_origins`：

```python
allow_origins=["https://your-domain.com"]  # 替换为你的域名
```

### Q: 如何查看日志？

```bash
# 日志输出到控制台，直接查看
# 或使用tail实时查看
tail -f /app/work/logs/bypass/app.log
```

---

## 下一步

- 📖 阅读 [详细集成文档](./FRONTEND_INTEGRATION.md)
- 🎨 自定义前端样式
- 🔐 配置生产环境部署
- 📊 集成监控和日志

---

## 技术支持

如有问题，请查看：
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [项目文档](./README.md)
- GitHub Issues（如有）
