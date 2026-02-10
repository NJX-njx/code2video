# -*- coding: utf-8 -*-
"""
Refiner API

提供视觉反馈和代码优化功能。
"""
import os
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mathvideo.agents.critic import VisualCritic
from mathvideo.agents.coder import refine_code

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


class RefineRequest(BaseModel):
    """优化请求模型"""
    section_id: str
    custom_suggestion: Optional[str] = None


class RefineResponse(BaseModel):
    """优化响应模型"""
    success: bool
    message: str
    suggestion: Optional[str] = None
    refined: bool = False


class CritiqueResponse(BaseModel):
    """视觉分析响应模型"""
    success: bool
    has_issues: bool
    suggestion: Optional[str] = None
    video_path: Optional[str] = None


def find_video_for_section(slug: str, section_id: str) -> Optional[str]:
    """
    查找指定章节的视频文件路径
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        视频文件的完整路径，如果不存在则返回 None
    """
    videos_dir = os.path.join(OUTPUT_DIR, slug, "media", "videos", section_id)
    
    if not os.path.exists(videos_dir):
        return None
    
    # 查找 480p15 目录下的视频
    quality_dir = os.path.join(videos_dir, "480p15")
    if os.path.exists(quality_dir):
        for f in os.listdir(quality_dir):
            if f.endswith(".mp4"):
                return os.path.join(quality_dir, f)
    
    # 如果没有 480p15，尝试其他质量目录
    for quality in os.listdir(videos_dir):
        quality_path = os.path.join(videos_dir, quality)
        if os.path.isdir(quality_path):
            for f in os.listdir(quality_path):
                if f.endswith(".mp4"):
                    return os.path.join(quality_path, f)
    
    return None


def get_script_path(slug: str, section_id: str) -> Optional[str]:
    """
    获取指定章节的脚本文件路径
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        脚本文件路径，如果不存在则返回 None
    """
    script_path = os.path.join(OUTPUT_DIR, slug, "scripts", f"{section_id}.py")
    return script_path if os.path.exists(script_path) else None


@router.post("/{slug}/critique/{section_id}", response_model=CritiqueResponse)
async def critique_section(slug: str, section_id: str):
    """
    对指定章节进行视觉分析
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        视觉分析结果，包括是否有问题和改进建议
    """
    # 查找视频文件
    video_path = find_video_for_section(slug, section_id)
    
    if not video_path:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到章节 '{section_id}' 的视频文件"
        )
    
    # 读取 storyboard 获取章节信息
    storyboard_path = os.path.join(OUTPUT_DIR, slug, "storyboard.json")
    if not os.path.exists(storyboard_path):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    
    section = None
    for s in storyboard.get("sections", []):
        if s.get("id") == section_id:
            section = s
            break
    
    if not section:
        raise HTTPException(status_code=404, detail=f"章节 '{section_id}' 不存在")
    
    try:
        # 执行视觉分析
        critic = VisualCritic()
        suggestion = critic.critique(video_path, section)
        
        return CritiqueResponse(
            success=True,
            has_issues=bool(suggestion),
            suggestion=suggestion,
            video_path=os.path.relpath(video_path, OUTPUT_DIR)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视觉分析失败: {str(e)}")


@router.post("/{slug}/refine", response_model=RefineResponse)
async def refine_section(slug: str, request: RefineRequest):
    """
    根据建议优化指定章节的代码
    
    参数:
        slug: 项目标识符
        request: 包含 section_id 和可选的自定义建议
    
    返回:
        优化结果
    """
    section_id = request.section_id
    
    # 获取脚本路径
    script_path = get_script_path(slug, section_id)
    
    if not script_path:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到章节 '{section_id}' 的脚本文件"
        )
    
    # 如果没有提供自定义建议，先进行视觉分析
    suggestion = request.custom_suggestion
    
    if not suggestion:
        video_path = find_video_for_section(slug, section_id)
        if video_path:
            # 读取 storyboard
            storyboard_path = os.path.join(OUTPUT_DIR, slug, "storyboard.json")
            with open(storyboard_path, "r", encoding="utf-8") as f:
                storyboard = json.load(f)
            
            section = None
            for s in storyboard.get("sections", []):
                if s.get("id") == section_id:
                    section = s
                    break
            
            if section:
                try:
                    critic = VisualCritic()
                    suggestion = critic.critique(video_path, section)
                except Exception:
                    pass
    
    if not suggestion:
        return RefineResponse(
            success=True,
            message="视觉检查通过，无需优化",
            suggestion=None,
            refined=False
        )
    
    try:
        # 读取当前代码
        with open(script_path, "r", encoding="utf-8") as f:
            current_code = f.read()
        
        # 调用优化函数
        refined_code = refine_code(current_code, suggestion)
        
        if refined_code:
            # 保存优化后的代码
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(refined_code)
            
            return RefineResponse(
                success=True,
                message="代码优化完成",
                suggestion=suggestion,
                refined=True
            )
        else:
            return RefineResponse(
                success=False,
                message="优化代码生成失败",
                suggestion=suggestion,
                refined=False
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代码优化失败: {str(e)}")


@router.post("/{slug}/render/{section_id}")
async def render_section(slug: str, section_id: str):
    """
    重新渲染指定章节
    
    参数:
        slug: 项目标识符
        section_id: 章节 ID
    
    返回:
        渲染结果
    """
    script_path = get_script_path(slug, section_id)
    
    if not script_path:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到章节 '{section_id}' 的脚本文件"
        )
    
    # 从脚本中提取类名
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    import re
    class_match = re.search(r'class\s+(\w+)\s*\([^)]*\)\s*:', content)
    if not class_match:
        raise HTTPException(status_code=400, detail="无法从脚本中提取场景类名")
    
    class_name = class_match.group(1)
    media_dir = os.path.join(OUTPUT_DIR, slug, "media")
    
    # 执行渲染（使用与 generate.py 一致的环境检测）
    import sys
    # 查找正确的 Python 可执行文件
    if sys.platform == "win32":
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
    python_exe = venv_python if os.path.isfile(venv_python) else sys.executable
    
    cmd = [
        python_exe, "-m", "manim", "-ql",
        "--media_dir", media_dir,
        script_path, class_name
    ]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    
    try:
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_ROOT,
            env=env
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"章节 '{section_id}' 渲染成功",
                "class_name": class_name
            }
        else:
            return {
                "success": False,
                "message": f"渲染失败",
                "error": stderr.decode("utf-8")[-500:]  # 只返回最后500字符
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"渲染执行失败: {str(e)}")
