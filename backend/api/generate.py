# -*- coding: utf-8 -*-
"""
视频生成 API

提供视频生成功能，支持 WebSocket 实时日志推送。
"""
import os
import sys
import json
import asyncio
import shlex
from typing import Optional, List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
from mathvideo.utils import make_slug

router = APIRouter()

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# 存储活跃的 WebSocket 连接
active_connections: dict[str, list[WebSocket]] = {}


def _quote_arg(s: str) -> str:
    """
    跨平台安全引用 shell 参数。
    
    shlex.quote 在 Windows 上使用单引号包裹，但 cmd.exe 不认单引号，
    会导致参数中包含字面单引号字符。本函数在 Windows 上使用双引号包裹。
    """
    if sys.platform == "win32":
        # Windows cmd.exe 使用双引号；转义内部的双引号
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return shlex.quote(s)


def _detect_python_command() -> str:
    """
    自动检测可用的 Python 执行命令。
    
    优先级：
    1. 项目根目录下的 .venv 虚拟环境
    2. conda 环境 mathvideo
    3. 系统 Python
    """
    import shutil
    
    # 检查 .venv 虚拟环境
    if sys.platform == "win32":
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
    
    if os.path.isfile(venv_python):
        return f'"{venv_python}" -u'
    
    # 检查 conda
    conda_path = shutil.which("conda")
    if conda_path:
        return 'conda run -n mathvideo --no-capture-output python -u'
    
    # 回退到系统 Python
    return f'"{sys.executable}" -u'


class GenerateRequest(BaseModel):
    """生成请求模型（兼容旧字段）"""
    prompt: Optional[str] = None
    topic: Optional[str] = None
    render: bool = True


class GenerateResponse(BaseModel):
    """生成响应模型"""
    success: bool
    message: str
    slug: Optional[str] = None
    task_id: Optional[str] = None


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


async def _safe_broadcast(task_id: str, payload: str):
    """
    安全地向所有订阅该任务的 WebSocket 客户端发送消息。
    使用列表快照遍历，避免并发修改导致的异常。
    """
    connections = active_connections.get(task_id)
    if not connections:
        return
    # 取快照避免在遍历时被其他协程修改
    snapshot = list(connections)
    for ws in snapshot:
        try:
            await ws.send_text(payload)
        except Exception:
            # 移除断开的连接（安全检查）
            try:
                connections.remove(ws)
            except ValueError:
                pass


async def broadcast_log(task_id: str, message: str, level: str = "info"):
    """
    向所有订阅该任务的 WebSocket 客户端广播日志
    
    参数:
        task_id: 任务 ID
        message: 日志消息
        level: 日志级别 (info, success, error, warning)
    """
    log_data = json.dumps({
        "type": "log",
        "level": level,
        "message": message
    })
    await _safe_broadcast(task_id, log_data)


async def broadcast_status(task_id: str, status: str, data: dict = None):
    """
    向所有订阅该任务的 WebSocket 客户端广播状态更新
    
    参数:
        task_id: 任务 ID
        status: 状态 (running, completed, failed)
        data: 附加数据
    """
    status_data = json.dumps({
        "type": "status",
        "status": status,
        "data": data or {}
    })
    await _safe_broadcast(task_id, status_data)


async def run_generation(task_id: str, prompt: str, render: bool, image_paths: Optional[List[str]] = None):
    """
    异步执行视频生成流程
    
    参数:
        task_id: 任务 ID（即项目 slug）
        topic: 数学主题
        render: 是否渲染视频
    """
    try:
        # 等待 WebSocket 连接建立（最多等待 5 秒）
        # 这解决了前端收到响应后才建立 WebSocket 连接的竞态条件
        for _ in range(50):  # 50 * 100ms = 5 秒
            if task_id in active_connections and len(active_connections[task_id]) > 0:
                break
            await asyncio.sleep(0.1)
        
        # 额外等待一小段时间确保连接稳定
        await asyncio.sleep(0.2)
        
        await broadcast_status(task_id, "running")
        await broadcast_log(task_id, f"🚀 开始生成项目: {prompt or '（仅图片输入）'}")
        
        # 构建命令参数
        # 使用 _quote_arg 代替 shlex.quote，因为 shlex.quote 在 Windows 上
        # 使用单引号包裹，而 cmd.exe 不认单引号，导致参数包含字面单引号字符
        args = []
        if prompt:
            args.append(_quote_arg(prompt))
        
        # 传递 --output-dir 让 CLI 使用后端已准备好的目录（图片已保存在其中）
        # 这避免了 CLI 重新生成 slug 可能导致的路径不一致
        output_dir = os.path.join(OUTPUT_DIR, task_id)
        args.extend(["--output-dir", _quote_arg(output_dir)])
        
        for img_path in (image_paths or []):
            args.extend(["--image", _quote_arg(img_path)])
        if render:
            args.append("--render")
        
        args_str = " ".join(args)
        
        # 自动检测 Python 环境（优先 .venv，然后 conda，最后系统 Python）
        python_cmd = _detect_python_command()
        shell_cmd = f'{python_cmd} -m mathvideo {args_str}'
        
        await broadcast_log(task_id, f"📂 输出目录: output/{task_id}")
        
        # 使用 subprocess 执行，实时读取输出
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # 禁用 Python 输出缓冲
        env["PYTHONIOENCODING"] = "utf-8"  # 强制子进程使用 UTF-8 编码输出
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = PROJECT_ROOT + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
        
        process = await asyncio.create_subprocess_shell(
            shell_cmd,
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
            
            decoded_line = line.decode("utf-8", errors="replace").strip()
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
            # CLI 可能已将目录重命名为 AI 生成的名称，需要检测实际 slug
            actual_slug = _detect_renamed_slug(task_id)
            rendered = _detect_rendered_video(actual_slug, render)
            await broadcast_log(task_id, "✅ 项目生成完成!", "success")
            if render and not rendered:
                await broadcast_log(task_id, "⚠️ 未检测到渲染视频输出，请检查渲染日志", "warning")
            await broadcast_status(task_id, "completed", {
                "slug": actual_slug,
                "rendered": rendered,
            })
        else:
            await broadcast_log(task_id, f"❌ 生成过程出错，退出码: {process.returncode}", "error")
            await broadcast_status(task_id, "failed", {"error": f"退出码: {process.returncode}"})
            
    except Exception as e:
        await broadcast_log(task_id, f"❌ 发生异常: {str(e)}", "error")
        await broadcast_status(task_id, "failed", {"error": str(e)})
    finally:
        # 清理已完成任务的空连接列表，避免内存泄漏
        conns = active_connections.get(task_id)
        if conns is not None and len(conns) == 0:
            active_connections.pop(task_id, None)


def _detect_renamed_slug(task_id: str) -> str:
    """
    检测 CLI 是否已将项目目录重命名。
    
    通过在 output 目录中查找包含 task_id 哈希后缀的目录来精确匹配，
    避免并发生成时通过"最新修改时间"误匹配其他项目。
    
    参数:
        task_id: 原始任务 ID（slug）
    
    返回:
        str: 实际的 slug（可能是重命名后的）
    """
    task_dir = os.path.join(OUTPUT_DIR, task_id)
    if os.path.exists(task_dir):
        return task_id
    
    # 提取 task_id 的哈希部分（最后的 -xxxxxx）
    # 重命名后新 slug 的哈希可能不同，所以需要更稳健的检测
    # 策略：查找 storyboard.json 中 input_text 匹配的目录
    try:
        if not os.path.isdir(OUTPUT_DIR):
            return task_id
        candidates = []
        for d in os.listdir(OUTPUT_DIR):
            d_path = os.path.join(OUTPUT_DIR, d)
            if not os.path.isdir(d_path):
                continue
            # 检查 storyboard.json 是否存在
            sb_path = os.path.join(d_path, "storyboard.json")
            if os.path.exists(sb_path):
                candidates.append((d, os.path.getmtime(d_path)))
        
        if not candidates:
            return task_id
        
        # 取最近修改的目录（该任务刚完成，其目录应该是最新的）
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    except OSError:
        return task_id


def _detect_rendered_video(slug: str, requested: bool) -> bool:
    if not requested:
        return False

    base_dir = os.path.join(OUTPUT_DIR, slug)
    final_video = os.path.join(base_dir, "final_video.mp4")
    if os.path.exists(final_video):
        return True

    media_dir = os.path.join(base_dir, "media", "videos")
    if not os.path.isdir(media_dir):
        return False

    for root, _dirs, files in os.walk(media_dir):
        for name in files:
            if name.lower().endswith(".mp4"):
                return True
    return False


@router.post("", response_model=GenerateResponse)
@router.post("/", response_model=GenerateResponse, include_in_schema=False)
async def start_generation(request: Request):
    """
    启动视频生成任务
    
    支持带尾斜杠和不带尾斜杠两种 URL 模式，
    避免 Next.js 代理去掉尾斜杠后触发 FastAPI 的 307 重定向循环。
    
    参数:
        request: 包含 topic 和 render 选项的请求体
    
    返回:
        任务信息，包括 task_id（用于 WebSocket 订阅）
    """
    content_type = request.headers.get("content-type", "")
    prompt = ""
    render = True
    image_paths: List[str] = []
    image_names: List[str] = []

    if content_type.startswith("application/json"):
        data = await request.json()
        prompt = (data.get("prompt") or data.get("topic") or data.get("description") or "").strip()
        render = bool(data.get("render", True))
    else:
        form = await request.form()
        prompt = (form.get("prompt") or form.get("topic") or form.get("description") or "").strip()
        render = _parse_bool(form.get("render", True))

        files = []
        if hasattr(form, "getlist"):
            files = form.getlist("images") or form.getlist("image") or []
        # 保存输入图片到 output/<slug>/inputs
        if files:
            image_names = [getattr(f, "filename", "") for f in files]

    if not prompt and not image_names:
        raise HTTPException(status_code=400, detail="请输入文本或上传图片")

    # 生成任务 ID（同时也是项目 slug）
    extra = ",".join([n for n in image_names if n]) if image_names else None
    task_id = make_slug(prompt or "image-input", extra=extra)

    # 处理图片保存（multipart）
    if image_names:
        inputs_dir = os.path.join(OUTPUT_DIR, task_id, "inputs")
        os.makedirs(inputs_dir, exist_ok=True)
        # 获取 form 中的文件列表
        form_data = await request.form() if not content_type.startswith("application/json") else None
        if form_data:
            uploaded_files = form_data.getlist("images") or form_data.getlist("image") or []
            for idx, file in enumerate(uploaded_files, start=1):
                filename = os.path.basename(getattr(file, "filename", "")) or f"input_{idx}.png"
                target_path = os.path.join(inputs_dir, filename)
                try:
                    file_content = await file.read()
                    with open(target_path, "wb") as fp:
                        fp.write(file_content)
                    image_paths.append(target_path)
                except Exception:
                    continue
    
    # 初始化 WebSocket 连接列表
    if task_id not in active_connections:
        active_connections[task_id] = []
    
    # 异步启动生成任务
    asyncio.create_task(run_generation(task_id, prompt, render, image_paths=image_paths))
    
    return GenerateResponse(
        success=True,
        message=f"生成任务已启动: {prompt or '（仅图片输入）'}",
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
    重新生成并渲染单个章节
    
    调用 Coder Agent 重新生成代码，然后用 Manim 渲染。
    对于递进模式（geometry/proof），会读取前序 Section 代码作为上下文。
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        重新生成的结果
    """
    project_dir = os.path.join(OUTPUT_DIR, slug)
    storyboard_path = os.path.join(project_dir, "storyboard.json")
    scripts_dir = os.path.join(project_dir, "scripts")
    media_dir = os.path.join(project_dir, "media")
    
    if not os.path.exists(storyboard_path):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    # 读取 storyboard
    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    
    # 查找指定章节及其在列表中的位置
    sections = storyboard.get("sections", [])
    section = None
    section_index = -1
    for i, s in enumerate(sections):
        if s.get("id") == section_id:
            section = s
            section_index = i
            break
    
    if not section:
        raise HTTPException(status_code=404, detail=f"章节 '{section_id}' 不存在")
    
    task_type = storyboard.get("task_type", "knowledge")
    
    # 对于递进模式，读取前序 Section 的代码
    previous_code = ""
    if task_type in ("geometry", "proof") and section_index > 0:
        prev_section_id = sections[section_index - 1].get("id", "")
        prev_script = os.path.join(scripts_dir, f"{prev_section_id}.py")
        if os.path.exists(prev_script):
            with open(prev_script, "r", encoding="utf-8") as f:
                previous_code = f.read()
    
    try:
        # 调用 Coder 重新生成代码
        from mathvideo.agents.coder import generate_code
        code, class_name = generate_code(
            section,
            previous_code=previous_code,
            task_type=task_type,
        )
        
        if not code:
            raise HTTPException(status_code=500, detail="代码生成失败")
        
        # 保存代码
        os.makedirs(scripts_dir, exist_ok=True)
        script_path = os.path.join(scripts_dir, f"{section_id}.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # 渲染
        env = os.environ.copy()
        env["PYTHONPATH"] = PROJECT_ROOT
        cmd = [sys.executable, "-m", "manim", "-ql", "--media_dir", media_dir, script_path, class_name]
        
        render_result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_ROOT,
            env=env,
        )
        stdout, stderr = await render_result.communicate()
        
        if render_result.returncode == 0:
            return {
                "success": True,
                "message": f"章节 '{section_id}' 重新生成且渲染成功",
                "class_name": class_name,
                "section": section,
            }
        else:
            return {
                "success": False,
                "message": f"章节 '{section_id}' 代码已重新生成，但渲染失败",
                "error": stderr.decode("utf-8", errors="replace")[-500:] if stderr else "未知错误",
                "class_name": class_name,
                "section": section,
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败: {str(e)}")
