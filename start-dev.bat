@echo off
REM MathVideo 开发环境启动脚本 (Windows CMD 版本)
REM 同时启动后端 (FastAPI) 和前端 (Next.js)

setlocal enabledelayedexpansion

echo.
echo 🚀 MathVideo 开发环境启动脚本
echo ==================================

REM 获取脚本所在目录
cd /d "%~dp0"
set SCRIPT_DIR=%cd%

REM 检查 Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo ❌ 未检测到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo ✓ Node.js %NODE_VERSION%

REM 检查 npm
where npm >nul 2>nul
if errorlevel 1 (
    echo ❌ 未检测到 npm
    pause
    exit /b 1
)

REM 安装后端依赖
echo.
echo 📦 检查后端依赖...
pip install -q fastapi uvicorn python-multipart websockets >nul 2>&1
if errorlevel 1 (
    echo ⚠️  安装后端依赖失败，请手动运行: pip install -r backend/requirements.txt
)

REM 安装前端依赖
echo.
echo 📦 检查前端依赖...
if not exist "frontend\node_modules" (
    echo 首次运行，安装前端依赖...
    cd frontend
    call npm install
    cd ..
) else (
    echo ✓ 前端依赖已安装
)

REM 创建 output 目录
if not exist "output" mkdir output

REM 获取启动模式
set MODE=%1
if "!MODE!"=="" set MODE=all

REM 根据参数决定启动哪个服务
if /i "!MODE!"=="backend" (
    goto start_backend
) else if /i "!MODE!"=="frontend" (
    goto start_frontend
) else if /i "!MODE!"=="all" (
    goto start_all
) else (
    echo 用法: start-dev.bat [backend^|frontend^|all]
    pause
    exit /b 1
)

:start_backend
echo.
echo 🔧 启动后端服务器 (http://localhost:8000)...
cd /d "%SCRIPT_DIR%"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
goto end

:start_frontend
echo.
echo 🎨 启动前端开发服务器 (http://localhost:3000)...
cd /d "%SCRIPT_DIR%\frontend"
call npm run dev
goto end

:start_all
echo.
echo 💡 提示: 请在两个终端分别运行:
echo    CMD 1: start-dev.bat backend
echo    CMD 2: start-dev.bat frontend
echo.
echo 或者使用以下命令在后台启动后端:
echo    start /B python -m uvicorn backend.main:app --reload --port 8000
echo    cd frontend && npm run dev
echo.
echo 现在启动后端服务器...
cd /d "%SCRIPT_DIR%"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
goto end

:end
pause
endlocal
