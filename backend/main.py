# -*- coding: utf-8 -*-
"""
FastAPI 后端主入口

提供 MathVideo 的 REST API 和 WebSocket 实时日志服务。
"""
import os
import sys

# 将项目根目录添加到 Python 路径，以便导入 mathvideo 模块
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.projects import router as projects_router
from backend.api.generate import router as generate_router
from backend.api.refiner import router as refiner_router

# 创建 FastAPI 应用实例
app = FastAPI(
    title="MathVideo API",
    description="自动化数学视频生成器后端 API",
    version="1.0.0"
)

# 配置 CORS，允许前端和 Tauri 桌面端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js 开发服务器
        "tauri://localhost",       # Tauri (macOS)
        "https://tauri.localhost", # Tauri (Windows/Linux)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(generate_router, prefix="/api/generate", tags=["Generate"])
app.include_router(refiner_router, prefix="/api/refiner", tags=["Refiner"])

# 静态文件服务：提供 output 目录下的媒体文件访问
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
if os.path.exists(output_dir):
    app.mount("/static", StaticFiles(directory=output_dir), name="static")


@app.get("/")
async def root():
    """根路由，返回 API 基本信息"""
    return {
        "name": "MathVideo API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
