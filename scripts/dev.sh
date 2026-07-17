#!/bin/bash

# 开发服务器启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "启动系统架构设计师学习网站开发服务器..."
echo "项目根目录: $PROJECT_ROOT"

# 检查 web 目录是否存在
if [ ! -d "$PROJECT_ROOT/web" ]; then
    echo "错误: web 目录不存在"
    echo "请先运行阶段 7 创建 Web 项目"
    exit 1
fi

# 进入 web 目录
cd "$PROJECT_ROOT/web"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

# 启动开发服务器
echo "启动 Next.js 开发服务器..."
npm run dev