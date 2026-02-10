# -*- coding: utf-8 -*-
"""
Skill 管理器

负责加载、组织和注入 Skill 到 LLM Prompt 中。
Skill 按任务类型分桶存储，避免不同场景的 Skill 互相干扰。

目录结构:
    mathvideo/skills/
    ├── common/           # 通用 Skill（所有类型共用）
    ├── geometry/         # 几何构造专用 Skill
    ├── knowledge/        # 知识点讲解专用 Skill
    ├── problem/          # 应用/计算题专用 Skill
    └── proof/            # 证明推导专用 Skill
"""
import os
import glob
from typing import List, Optional


# Skill 目录的根路径（相对于 mathvideo 包）
SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mathvideo", "skills")

# 如果从包内部调用，使用另一种路径计算方式
if not os.path.exists(SKILLS_DIR):
    SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
    SKILLS_DIR = os.path.abspath(SKILLS_DIR)


def load_skills(task_type: str, include_common: bool = True) -> str:
    """
    加载指定任务类型的所有 Skill，拼接为字符串

    会先加载 common/ 目录下的通用 Skill，再加载对应任务类型目录下的专用 Skill。

    参数:
        task_type (str): 任务类型（knowledge / geometry / problem / proof）
        include_common (bool): 是否包含通用 Skill，默认 True

    返回:
        str: 拼接后的 Skill 文本，可直接注入到 Prompt 中。
             如果没有任何 Skill，返回空字符串。
    """
    skill_texts = []

    # 加载通用 Skill
    if include_common:
        common_skills = _load_skills_from_dir(os.path.join(SKILLS_DIR, "common"))
        if common_skills:
            skill_texts.append("## 通用技巧\n" + common_skills)

    # 加载任务类型专用 Skill
    type_skills = _load_skills_from_dir(os.path.join(SKILLS_DIR, task_type))
    if type_skills:
        type_labels = {
            "geometry": "几何构造",
            "knowledge": "知识点讲解",
            "problem": "应用/计算题",
            "proof": "证明推导",
        }
        label = type_labels.get(task_type, task_type)
        skill_texts.append(f"## {label}专用技巧\n" + type_skills)

    if not skill_texts:
        return ""

    return "\n\n## 经验技巧库（请参考）\n\n" + "\n\n".join(skill_texts)


def _load_skills_from_dir(dir_path: str) -> str:
    """
    从指定目录加载所有 .md 和 .yaml 文件内容

    参数:
        dir_path (str): Skill 文件目录路径

    返回:
        str: 拼接后的 Skill 内容，如果目录不存在或为空则返回空字符串
    """
    if not os.path.isdir(dir_path):
        return ""

    skill_files = sorted(
        glob.glob(os.path.join(dir_path, "*.md"))
        + glob.glob(os.path.join(dir_path, "*.yaml"))
    )

    if not skill_files:
        return ""

    contents = []
    for filepath in skill_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    filename = os.path.basename(filepath)
                    contents.append(f"### {filename}\n{content}")
        except Exception as e:
            print(f"⚠️ 读取 Skill 文件失败: {filepath} ({e})")

    return "\n\n".join(contents)


def list_skills(task_type: Optional[str] = None) -> List[str]:
    """
    列出可用的 Skill 文件（用于调试/展示）

    参数:
        task_type (str, 可选): 仅列出指定类型的 Skill。为 None 时列出所有。

    返回:
        List[str]: Skill 文件路径列表
    """
    result = []
    if task_type:
        dirs = [os.path.join(SKILLS_DIR, "common"), os.path.join(SKILLS_DIR, task_type)]
    else:
        dirs = [os.path.join(SKILLS_DIR, d) for d in os.listdir(SKILLS_DIR)
                if os.path.isdir(os.path.join(SKILLS_DIR, d))]

    for d in dirs:
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith((".md", ".yaml")):
                    result.append(os.path.join(d, f))

    return result
