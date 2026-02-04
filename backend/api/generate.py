# -*- coding: utf-8 -*-
"""
视频生成 API

提供视频生成功能，支持 WebSocket 实时日志推送。
"""
import os
import sys
import json
import re
import asyncio
import subprocess
from typing import Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# 存储活跃的 WebSocket 连接
active_connections: dict[str, list[WebSocket]] = {}


class GenerateRequest(BaseModel):
    """生成请求模型"""
    topic: str
    render: bool = True


class GenerateResponse(BaseModel):
    """生成响应模型"""
    success: bool
    message: str
    slug: Optional[str] = None
    task_id: Optional[str] = None


def slugify(value: str) -> str:
    """
    将字符串规范化为 URL 友好格式
    
    参数:
        value: 原始字符串
    
    返回:
        URL 友好的字符串
    """
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


async def broadcast_log(task_id: str, message: str, level: str = "info"):
    """
    向所有订阅该任务的 WebSocket 客户端广播日志
    
    参数:
        task_id: 任务 ID
        message: 日志消息
        level: 日志级别 (info, success, error, warning)
    """
    if task_id in active_connections:
        log_data = json.dumps({
            "type": "log",
            "level": level,
            "message": message
        })
        disconnected = []
        for ws in active_connections[task_id]:
            try:
                await ws.send_text(log_data)
            except Exception:
                disconnected.append(ws)
        # 移除断开的连接
        for ws in disconnected:
            active_connections[task_id].remove(ws)


async def broadcast_status(task_id: str, status: str, data: dict = None):
    """
    向所有订阅该任务的 WebSocket 客户端广播状态更新
    
    参数:
        task_id: 任务 ID
        status: 状态 (running, completed, failed)
        data: 附加数据
    """
    if task_id in active_connections:
        status_data = json.dumps({
            "type": "status",
            "status": status,
            "data": data or {}
        })
        disconnected = []
        for ws in active_connections[task_id]:
            try:
                await ws.send_text(status_data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            active_connections[task_id].remove(ws)


async def run_generation(task_id: str, topic: str, render: bool):
    """
    异步执行视频生成流程
    
    参数:
        task_id: 任务 ID（即项目 slug）
        topic: 数学主题
        render: 是否渲染视频
    """
    try:
        await broadcast_status(task_id, "running")
        await broadcast_log(task_id, f"🚀 开始生成项目: {topic}")
        
        # 构建命令（使用包入口，避免依赖根目录脚本）
        cmd = [sys.executable, "-m", "mathvideo", topic]
        if render:
            cmd.append("--render")
        
        await broadcast_log(task_id, f"📂 输出目录: output/{task_id}")
        
        # 使用 subprocess 执行，实时读取输出
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = PROJECT_ROOT + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=PROJECT_ROOT,
            env=env
        )
        
        # 实时读取输出并广播
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            decoded_line = line.decode("utf-8").strip()
            if decoded_line:
                # 根据内容判断日志级别
                level = "info"
                if "✅" in decoded_line or "✨" in decoded_line:
                    level = "success"
                elif "❌" in decoded_line:
                    level = "error"
                elif "⚠️" in decoded_line:
                    level = "warning"
                elif "🔧" in decoded_line or "🔄" in decoded_line:
                    level = "info"
                
                await broadcast_log(task_id, decoded_line, level)
        
        # 等待进程结束
        await process.wait()
        
        if process.returncode == 0:
            await broadcast_log(task_id, "✅ 项目生成完成!", "success")
            await broadcast_status(task_id, "completed", {"slug": task_id})
        else:
            await broadcast_log(task_id, f"❌ 生成过程出错，退出码: {process.returncode}", "error")
            await broadcast_status(task_id, "failed", {"error": f"退出码: {process.returncode}"})
            
    except Exception as e:
        await broadcast_log(task_id, f"❌ 发生异常: {str(e)}", "error")
        await broadcast_status(task_id, "failed", {"error": str(e)})


@router.post("/", response_model=GenerateResponse)
async def start_generation(request: GenerateRequest):
    """
    启动视频生成任务
    
    参数:
        request: 包含 topic 和 render 选项的请求体
    
    返回:
        任务信息，包括 task_id（用于 WebSocket 订阅）
    """
    topic = request.topic.strip()
    
    if not topic:
        raise HTTPException(status_code=400, detail="主题不能为空")
    
    # 生成任务 ID（同时也是项目 slug）
    task_id = slugify(topic)
    
    # 初始化 WebSocket 连接列表
    if task_id not in active_connections:
        active_connections[task_id] = []
    
    # 异步启动生成任务
    asyncio.create_task(run_generation(task_id, topic, request.render))
    
    return GenerateResponse(
        success=True,
        message=f"生成任务已启动: {topic}",
        slug=task_id,
        task_id=task_id
    )


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket 端点，用于接收实时生成日志
    
    参数:
        websocket: WebSocket 连接
        task_id: 任务 ID
    """
    await websocket.accept()
    
    # 注册连接
    if task_id not in active_connections:
        active_connections[task_id] = []
    active_connections[task_id].append(websocket)
    
    try:
        # 发送欢迎消息
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"已连接到任务 {task_id}"
        }))
        
        # 保持连接，等待客户端断开
        while True:
            try:
                # 接收客户端消息（心跳等）
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # 发送心跳
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        pass
    finally:
        # 移除连接
        if task_id in active_connections and websocket in active_connections[task_id]:
            active_connections[task_id].remove(websocket)


@router.post("/{slug}/section/{section_id}")
async def regenerate_section(slug: str, section_id: str):
    """
    重新生成单个章节
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        重新生成的结果
    """
    project_dir = os.path.join(OUTPUT_DIR, slug)
    storyboard_path = os.path.join(project_dir, "storyboard.json")
    
    if not os.path.exists(storyboard_path):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    # 读取 storyboard
    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    
    # 查找指定章节
    section = None
    for s in storyboard.get("sections", []):
        if s.get("id") == section_id:
            section = s
            break
    
    if not section:
        raise HTTPException(status_code=404, detail=f"章节 '{section_id}' 不存在")
    
    # TODO: 调用 coder 重新生成该章节
    # 这里需要导入并使用 mathvideo.agents.coder
    
    return {"message": f"章节 '{section_id}' 重新生成功能待实现", "section": section}
