# 🔑 项目 API Key 配置说明

## 📋 概述

本项目使用多个 API Key 和配置，主要分为以下几类：

1. **模型服务 API Key**（必需）
2. **数据库配置**（可选）
3. **其他集成服务**（可选）

---

## 🎯 核心必需配置

### 1. 模型服务 API Key

**环境变量名称**：
- `COZE_WORKLOAD_IDENTITY_API_KEY`
- `COZE_INTEGRATION_MODEL_BASE_URL`

**获取方式**：

这些 API Key 来自 Coze 平台，有两种使用方式：

#### 方式 1：在 Coze 平台运行（推荐）

如果项目在 Coze 平台上运行，这些环境变量会**自动注入**，无需手动配置。

#### 方式 2：本地开发

如果需要在本地开发，需要：

1. **注册 Coze 账号**
   - 访问：https://www.coze.cn
   - 注册并登录

2. **创建项目**
   - 在 Coze 平台创建一个项目
   - 获取项目的 API Key

3. **设置环境变量**

创建 `.env` 文件（项目根目录）：

```env
# 模型服务配置（必需）
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn

# 其他必需环境变量
COZE_WORKLOAD_IDENTITY_CLIENT_ID=your_client_id
COZE_WORKLOAD_IDENTITY_CLIENT_SECRET=your_client_secret
COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT=https://api.coze.cn/.well-known/token
COZE_INTEGRATION_BASE_URL=https://integration.coze.cn
COZE_LOOP_BASE_URL=https://api.coze.cn
```

**⚠️ 重要**：`.env` 文件已添加到 `.gitignore`，不会被提交到 Git。

---

## 📊 当前环境变量列表

### 已配置的环境变量（自动注入）

以下是 Coze 平台自动注入的环境变量：

| 环境变量名称 | 说明 | 来源 |
|-------------|------|------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 模型服务 API Key | 自动注入 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 模型服务 Base URL | 自动注入 |
| `COZE_WORKLOAD_IDENTITY_CLIENT_ID` | 客户端 ID | 自动注入 |
| `COZE_WORKLOAD_IDENTITY_CLIENT_SECRET` | 客户端密钥 | 自动注入 |
| `COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT` | Token 端点 | 自动注入 |
| `COZE_INTEGRATION_BASE_URL` | 集成服务 Base URL | 自动注入 |
| `COZE_LOOP_BASE_URL` | Loop API Base URL | 自动注入 |
| `COZE_BUCKET_NAME` | 对象存储桶名 | 自动注入 |
| `COZE_BUCKET_ENDPOINT_URL` | 对象存储端点 | 自动注入 |

---

## 🗄️ 数据库配置（可选）

如果需要使用数据库功能，需要配置数据库连接。

### PostgreSQL 配置

在 `.env` 文件中添加：

```env
# 数据库配置（可选）
DATABASE_URL=postgresql://username:password@localhost:5432/travel_planner
```

**本地开发**：

```bash
# 使用 Docker 启动 PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=travel_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=travel_planner \
  -p 5432:5432 \
  postgres:15

# 设置环境变量
export DATABASE_URL=postgresql://travel_user:your_password@localhost:5432/travel_planner
```

---

## 🔧 如何查看当前 API Key

### 方法 1：在沙箱环境中查看

```bash
# 查看所有 COZE 相关环境变量
env | grep COZE

# 查看特定 API Key
echo $COZE_WORKLOAD_IDENTITY_API_KEY
```

### 方法 2：在代码中查看

查看以下文件中的使用方式：

```python
# src/agents/agent.py
api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
```

---

## 🚀 快速配置指南

### 场景 1：在 Coze 平台运行

**无需任何配置**，所有环境变量会自动注入。

### 场景 2：本地开发（无 Coze 账号）

如果你没有 Coze 账号，可以使用其他模型服务：

#### 使用 DeepSeek

```env
# .env 文件
DEEPSEEK_API_KEY=your_deepseek_api_key
```

修改 `src/agents/agent.py`：

```python
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
    streaming=True,
)
```

#### 使用 OpenAI

```env
# .env 文件
OPENAI_API_KEY=your_openai_api_key
```

修改 `src/agents/agent.py`：

```python
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    streaming=True,
)
```

---

## 🔐 安全注意事项

### ⚠️ 绝对禁止

1. **不要**将 API Key 硬编码在代码中
2. **不要**将 `.env` 文件提交到 Git
3. **不要**在公开场合分享 API Key

### ✅ 最佳实践

1. 使用环境变量存储敏感信息
2. 定期更换 API Key
3. 使用不同的 API Key 用于开发和生产环境
4. 限制 API Key 的权限范围

---

## 📝 配置文件示例

### 完整的 `.env` 示例

```env
# ============================================
# 模型服务配置（必需）
# ============================================
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn
COZE_WORKLOAD_IDENTITY_CLIENT_ID=your_client_id
COZE_WORKLOAD_IDENTITY_CLIENT_SECRET=your_client_secret
COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT=https://api.coze.cn/.well-known/token
COZE_INTEGRATION_BASE_URL=https://integration.coze.cn
COZE_LOOP_BASE_URL=https://api.coze.cn

# ============================================
# 数据库配置（可选）
# ============================================
DATABASE_URL=postgresql://user:password@localhost:5432/travel_planner

# ============================================
# 其他配置（可选）
# ============================================
COZE_BUCKET_NAME=bucket_name
COZE_BUCKET_ENDPOINT_URL=https://integration.coze.cn/coze-coding-s3proxy/v1

# ============================================
# 日志配置（可选）
# ============================================
LOG_LEVEL=INFO
```

---

## 🧪 测试 API Key 是否配置正确

### 测试脚本

创建 `test_api_key.py`：

```python
import os
import requests

def test_api_key():
    """测试 API Key 是否有效"""
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    if not api_key:
        print("❌ COZE_WORKLOAD_IDENTITY_API_KEY 未设置")
        return False
    
    if not base_url:
        print("❌ COZE_INTEGRATION_MODEL_BASE_URL 未设置")
        return False
    
    print(f"✅ API Key 已设置: {api_key[:20]}...")
    print(f"✅ Base URL 已设置: {base_url}")
    
    # 测试 API 调用（可选）
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-seed-1-6-251015",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API 调用成功")
            return True
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ API 调用测试跳过: {str(e)}")
        return True

if __name__ == "__main__":
    test_api_key()
```

运行测试：

```bash
python test_api_key.py
```

---

## 🎯 常见问题

### Q1: 如何获取 Coze API Key？

**A**: 
1. 访问 https://www.coze.cn
2. 注册并登录
3. 创建项目
4. 在项目设置中找到 API Key

### Q2: API Key 在哪里使用？

**A**: 在以下文件中使用：
- `src/agents/agent.py`
- `src/agents/itinerary_agent.py`
- `src/agents/validation_agent.py`
- `src/agents/delivery_agent.py`

### Q3: 可以使用其他模型服务吗？

**A**: 可以，参考上面的"场景 2：本地开发"部分。

### Q4: 如何保护 API Key？

**A**: 
1. 不要提交 `.env` 文件到 Git
2. 定期更换 API Key
3. 使用环境变量而非硬编码

---

## 📞 需要帮助？

如果遇到 API Key 配置问题：

1. 检查环境变量是否正确设置
2. 运行测试脚本验证
3. 查看 `/app/work/logs/bypass/app.log` 日志文件
4. 参考 `docs/QUICK_START.md`

---

**最后更新**: 2026-01-26
