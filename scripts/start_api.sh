#!/bin/bash

# FastAPI后端服务启动脚本

set -e

echo "========================================"
echo "  旅行规划Agent API - 启动脚本"
echo "========================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)
echo "📁 项目目录: $PROJECT_DIR"

# 设置Python路径
export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
echo "🔧 PYTHONPATH: $PYTHONPATH"

# 检查依赖
echo "📦 检查依赖..."
pip install fastapi uvicorn websockets python-multipart -q

# 启动选项
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-true}

echo ""
echo "========================================"
echo "  配置信息"
echo "========================================"
echo "🌐 Host: $HOST"
echo "🚪 Port: $PORT"
echo "👥 Workers: $WORKERS"
echo "🔄 Reload: $RELOAD"
echo "========================================"
echo ""

# 启动FastAPI服务
echo "🚀 启动FastAPI服务..."
echo ""

if [ "$RELOAD" = "true" ]; then
    # 开发模式（支持热重载）
    python -m uvicorn src.api.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload
else
    # 生产模式
    python -m uvicorn src.api.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS"
fi
