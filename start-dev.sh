#!/bin/bash
# MathVideo 开发环境启动脚本
# 同时启动后端 (FastAPI) 和前端 (Next.js)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MathVideo 开发环境启动脚本${NC}"
echo "=================================="

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 conda 环境
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}⚠️  未检测到 conda，请确保已激活正确的 Python 环境${NC}"
else
    echo -e "${GREEN}✓ 检测到 conda${NC}"
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未检测到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Node.js $(node -v)${NC}"
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 未检测到 npm${NC}"
    exit 1
fi

# 安装后端依赖（如果需要）
echo -e "\n${BLUE}📦 检查后端依赖...${NC}"
pip install -q fastapi uvicorn python-multipart websockets 2>/dev/null || {
    echo -e "${YELLOW}⚠️  安装后端依赖失败，请手动运行: pip install -r backend/requirements.txt${NC}"
}

# 安装前端依赖（如果需要）
echo -e "\n${BLUE}📦 检查前端依赖...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo "首次运行，安装前端依赖..."
    cd frontend
    npm install
    cd ..
else
    echo -e "${GREEN}✓ 前端依赖已安装${NC}"
fi

# 创建 output 目录（如果不存在）
mkdir -p output

# 启动函数
start_backend() {
    echo -e "\n${BLUE}🔧 启动后端服务器 (http://localhost:8000)...${NC}"
    cd "$SCRIPT_DIR"
    python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
}

start_frontend() {
    echo -e "\n${BLUE}🎨 启动前端开发服务器 (http://localhost:3000)...${NC}"
    cd "$SCRIPT_DIR/frontend"
    npm run dev
}

# 根据参数决定启动哪个服务
case "${1:-all}" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    tauri)
        echo -e "\n${BLUE}🖥️  启动 Tauri 桌面开发模式...${NC}"
        echo -e "${YELLOW}💡 请在另一终端运行: ./start-dev.sh backend${NC}\n"
        cd "$SCRIPT_DIR/frontend"
        npm run tauri:dev
        ;;
    all)
        echo -e "\n${GREEN}💡 提示: 请在两个终端分别运行:${NC}"
        echo -e "   终端 1: ${YELLOW}./start-dev.sh backend${NC}"
        echo -e "   终端 2: ${YELLOW}./start-dev.sh frontend${NC}"
        echo ""
        echo -e "${GREEN}💡 Tauri 桌面模式:${NC}"
        echo -e "   终端 1: ${YELLOW}./start-dev.sh backend${NC}"
        echo -e "   终端 2: ${YELLOW}./start-dev.sh tauri${NC}"
        echo ""
        echo -e "${BLUE}现在启动后端服务器...${NC}"
        start_backend
        ;;
    *)
        echo "用法: $0 [backend|frontend|tauri|all]"
        exit 1
        ;;
esac
