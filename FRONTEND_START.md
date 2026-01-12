# AI旅行规划助手 - 快速启动指南

## 🚀 快速开始

### 1. 启动服务

```bash
cd /workspace/projects
python src/main.py -m http -p 5000
```

### 2. 访问前端

在浏览器中打开：
```
http://localhost:5000
```

### 3. 开始使用

在输入框中输入你的旅行需求，例如：
- "我想去东京旅行4天，喜欢历史文化，预算中等"
- 或点击快捷按钮快速开始

## 📚 详细文档

完整使用指南请查看：[docs/FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md)

## 🎯 功能特性

- ✅ 多Agent协作（行程Agent + 预订Agent）
- ✅ 实时对话交互
- ✅ Markdown格式响应
- ✅ 会话记忆功能
- ✅ 响应式设计
- ✅ 快捷操作按钮

## 🧪 运行测试

```bash
cd /workspace/projects
python -m pytest tests/test_frontend.py -v
```

## 📁 前端文件

- `static/index.html` - 主页面
- `static/style.css` - 样式文件
- `static/app.js` - JavaScript逻辑

---

**开发者**: AI Agent搭建专家
**最后更新**: 2026-01-12
