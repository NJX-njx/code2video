# MathVideo 开发环境启动脚本 (Windows 版本)
# 同时启动后端 (FastAPI) 和前端 (Next.js)

# 颜色定义
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[1;33m"
$BLUE = "`e[0;34m"
$NC = "`e[0m"

Write-Host "${BLUE}🚀 MathVideo 开发环境启动脚本${NC}"
Write-Host "=================================="

# 获取脚本所在目录
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# 检查 conda 环境
try {
    $condaCheck = conda info --json 2>$null
    Write-Host "${GREEN}✓ 检测到 conda${NC}"
}
catch {
    Write-Host "${YELLOW}⚠️  未检测到 conda，请确保已激活正确的 Python 环境${NC}"
}

# 检查 Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "${RED}❌ 未检测到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
}
else {
    $nodeVersion = node -v
    Write-Host "${GREEN}✓ Node.js $nodeVersion${NC}"
}

# 检查 npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "${RED}❌ 未检测到 npm${NC}"
    exit 1
}

# 安装后端依赖（如果需要）
Write-Host ""
Write-Host "${BLUE}📦 检查后端依赖...${NC}"
pip install -q fastapi uvicorn python-multipart websockets 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "${YELLOW}⚠️  安装后端依赖失败，请手动运行: pip install -r backend/requirements.txt${NC}"
}

# 安装前端依赖（如果需要）
Write-Host ""
Write-Host "${BLUE}📦 检查前端依赖...${NC}"
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "首次运行，安装前端依赖..."
    Push-Location frontend
    npm install
    Pop-Location
}
else {
    Write-Host "${GREEN}✓ 前端依赖已安装${NC}"
}

# 创建 output 目录（如果不存在）
if (-not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" -Force | Out-Null
}

# 启动后端函数
function Start-Backend {
    Write-Host ""
    Write-Host "${BLUE}🔧 启动后端服务器 (http://localhost:8000)...${NC}"
    Set-Location $SCRIPT_DIR
    python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
}

# 启动前端函数
function Start-Frontend {
    Write-Host ""
    Write-Host "${BLUE}🎨 启动前端开发服务器 (http://localhost:3000)...${NC}"
    Push-Location frontend
    npm run dev
    Pop-Location
}

# 启动 Tauri 桌面开发模式
function Start-Tauri {
    Write-Host ""
    Write-Host "${BLUE}🖥️  启动 Tauri 桌面开发模式...${NC}"
    Write-Host "${YELLOW}💡 Tauri 会自动启动前端，你只需手动启动后端：${NC}"
    Write-Host "   另开终端: ${YELLOW}.\start-dev.ps1 backend${NC}"
    Write-Host ""
    Push-Location frontend
    npm run tauri:dev
    Pop-Location
}

# 根据参数决定启动哪个服务
$mode = if ($args.Count -gt 0) { $args[0] } else { "all" }

switch ($mode) {
    "backend" {
        Start-Backend
    }
    "frontend" {
        Start-Frontend
    }
    "tauri" {
        Start-Tauri
    }
    "all" {
        Write-Host ""
        Write-Host "${GREEN}💡 提示: 请在两个终端分别运行:${NC}"
        Write-Host "   PowerShell 1: ${YELLOW}.\start-dev.ps1 backend${NC}"
        Write-Host "   PowerShell 2: ${YELLOW}.\start-dev.ps1 frontend${NC}"
        Write-Host ""
        Write-Host "${GREEN}💡 Tauri 桌面模式:${NC}"
        Write-Host "   PowerShell 1: ${YELLOW}.\start-dev.ps1 backend${NC}"
        Write-Host "   PowerShell 2: ${YELLOW}.\start-dev.ps1 tauri${NC}"
        Write-Host ""
        Write-Host "${BLUE}现在启动后端服务器...${NC}"
        Start-Backend
    }
    default {
        Write-Host "用法: .\start-dev.ps1 [backend|frontend|tauri|all]"
        exit 1
    }
}
