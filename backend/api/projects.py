# -*- coding: utf-8 -*-
"""
项目管理 API

提供项目列表、详情、删除等功能。
"""
import os
import json
import shutil
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 项目输出目录（相对于项目根目录）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")


class ProjectInfo(BaseModel):
    """项目信息模型"""
    slug: str
    topic: str
    created_at: Optional[str] = None
    sections_count: int = 0
    has_videos: bool = False
    storyboard: Optional[dict] = None


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    projects: List[ProjectInfo]
    total: int


def get_project_info(slug: str) -> Optional[ProjectInfo]:
    """
    获取单个项目的详细信息
    
    参数:
        slug: 项目的目录名（URL友好格式）
    
    返回:
        ProjectInfo 对象，如果项目不存在则返回 None
    """
    project_dir = os.path.join(OUTPUT_DIR, slug)
    
    if not os.path.isdir(project_dir):
        return None
    
    # 读取 storyboard.json 获取项目信息
    storyboard_path = os.path.join(project_dir, "storyboard.json")
    topic = slug  # 默认使用目录名作为主题
    sections_count = 0
    storyboard = None
    
    if os.path.exists(storyboard_path):
        try:
            with open(storyboard_path, "r", encoding="utf-8") as f:
                storyboard = json.load(f)
                topic = storyboard.get("topic", slug)
                sections_count = len(storyboard.get("sections", []))
        except (json.JSONDecodeError, IOError):
            pass
    
    # 检查是否有生成的视频
    videos_dir = os.path.join(project_dir, "media", "videos")
    has_videos = os.path.exists(videos_dir) and any(
        f.endswith(".mp4") for root, dirs, files in os.walk(videos_dir) for f in files
    )
    
    # 获取创建时间（使用目录的修改时间）
    created_at = datetime.fromtimestamp(os.path.getmtime(project_dir)).isoformat()
    
    return ProjectInfo(
        slug=slug,
        topic=topic,
        created_at=created_at,
        sections_count=sections_count,
        has_videos=has_videos,
        storyboard=storyboard
    )


@router.get("/", response_model=ProjectListResponse)
async def list_projects():
    """
    获取所有项目列表
    
    返回:
        包含所有项目信息的列表
    """
    if not os.path.exists(OUTPUT_DIR):
        return ProjectListResponse(projects=[], total=0)
    
    projects = []
    for name in os.listdir(OUTPUT_DIR):
        project_info = get_project_info(name)
        if project_info:
            projects.append(project_info)
    
    # 按创建时间倒序排列（最新的在前）
    projects.sort(key=lambda p: p.created_at or "", reverse=True)
    
    return ProjectListResponse(projects=projects, total=len(projects))


@router.get("/{slug}", response_model=ProjectInfo)
async def get_project(slug: str):
    """
    获取单个项目详情
    
    参数:
        slug: 项目标识符
    
    返回:
        项目详细信息
    """
    project_info = get_project_info(slug)
    
    if not project_info:
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    return project_info


@router.get("/{slug}/storyboard")
async def get_storyboard(slug: str):
    """
    获取项目的 Storyboard JSON
    
    参数:
        slug: 项目标识符
    
    返回:
        Storyboard JSON 数据
    """
    storyboard_path = os.path.join(OUTPUT_DIR, slug, "storyboard.json")
    
    if not os.path.exists(storyboard_path):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 的 Storyboard 不存在")
    
    try:
        with open(storyboard_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"读取 Storyboard 失败: {str(e)}")


@router.put("/{slug}/storyboard")
async def update_storyboard(slug: str, storyboard: dict):
    """
    更新项目的 Storyboard JSON
    
    参数:
        slug: 项目标识符
        storyboard: 新的 Storyboard 数据
    
    返回:
        更新后的 Storyboard
    """
    storyboard_path = os.path.join(OUTPUT_DIR, slug, "storyboard.json")
    project_dir = os.path.join(OUTPUT_DIR, slug)
    
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    try:
        with open(storyboard_path, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, indent=2, ensure_ascii=False)
        return {"message": "Storyboard 更新成功", "storyboard": storyboard}
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"保存 Storyboard 失败: {str(e)}")


@router.get("/{slug}/videos")
async def list_videos(slug: str):
    """
    获取项目的所有视频文件列表
    
    参数:
        slug: 项目标识符
    
    返回:
        视频文件路径列表
    """
    videos_dir = os.path.join(OUTPUT_DIR, slug, "media", "videos")
    
    if not os.path.exists(videos_dir):
        return {"videos": []}
    
    videos = []
    for root, dirs, files in os.walk(videos_dir):
        for f in files:
            if f.endswith(".mp4"):
                # 构建相对于 output 目录的路径
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, OUTPUT_DIR)
                url_path = rel_path.replace(os.sep, "/")
                # 提取 section 信息
                parts = rel_path.split(os.sep)
                section_name = parts[2] if len(parts) > 2 else "unknown"
                videos.append({
                    "name": f,
                    "section": section_name,
                    "path": f"/static/{url_path}",
                    "full_path": rel_path
                })
    
    # 按 section 名称排序
    videos.sort(key=lambda v: v["section"])
    
    return {"videos": videos}


@router.get("/{slug}/scripts")
async def list_scripts(slug: str):
    """
    获取项目的所有脚本文件列表
    
    参数:
        slug: 项目标识符
    
    返回:
        脚本文件信息列表
    """
    scripts_dir = os.path.join(OUTPUT_DIR, slug, "scripts")
    
    if not os.path.exists(scripts_dir):
        return {"scripts": []}
    
    scripts = []
    for f in os.listdir(scripts_dir):
        if f.endswith(".py") and not f.startswith("__"):
            script_path = os.path.join(scripts_dir, f)
            with open(script_path, "r", encoding="utf-8") as file:
                content = file.read()
            scripts.append({
                "name": f,
                "path": f"{slug}/scripts/{f}",
                "content": content
            })
    
    scripts.sort(key=lambda s: s["name"])
    
    return {"scripts": scripts}


@router.delete("/{slug}")
async def delete_project(slug: str):
    """
    删除项目
    
    参数:
        slug: 项目标识符
    
    返回:
        删除结果
    """
    project_dir = os.path.join(OUTPUT_DIR, slug)
    
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail=f"项目 '{slug}' 不存在")
    
    try:
        shutil.rmtree(project_dir)
        return {"message": f"项目 '{slug}' 已删除"}
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")
