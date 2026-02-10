import hashlib
import os
import re
from typing import Optional


def slugify(value: str) -> str:
    """
    将字符串规范化为文件系统友好格式。
    保留中文字符、英文字母和数字，移除其它特殊字符。
    """
    value = str(value).strip()
    # 保留中文(\u4e00-\u9fff)、字母(\w)、数字、空格和连字符
    value = re.sub(r"[^\u4e00-\u9fff\w\s-]", "", value)
    # 将连续空格/连字符替换为单个连字符
    value = re.sub(r"[-\s]+", "-", value).strip("-_")
    return value


def make_slug(value: str, max_length: int = 40, extra: Optional[str] = None) -> str:
    """
    为任意输入生成可控长度、人类可读的 slug。

    - 保留中文字符，确保文件夹名有意义
    - 当输入过长时截断并附加短哈希，避免路径过长
    - 可通过 extra 增加区分度（例如图片文件名）
    """
    base = slugify(value) or "project"
    basis = value if extra is None else f"{value}|{extra}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:6]
    suffix = f"-{digest}"

    max_base_len = max(1, max_length - len(suffix))
    if len(base) > max_base_len:
        base = base[:max_base_len].rstrip("-") or "project"

    return f"{base}{suffix}"


def rename_project_dir(old_dir: str, new_slug: str) -> str:
    """
    将项目目录重命名为更有意义的名称（基于 LLM 生成的 topic）。

    如果目标目录已存在或重命名失败，返回原路径。

    参数:
        old_dir: 当前项目目录的完整路径
        new_slug: 新的 slug 名称

    返回:
        str: 重命名后的目录路径（或失败时返回原路径）
    """
    parent = os.path.dirname(old_dir)
    new_dir = os.path.join(parent, new_slug)

    # 如果新旧路径相同，无需操作
    if os.path.normpath(old_dir) == os.path.normpath(new_dir):
        return old_dir

    # 如果目标已存在，不覆盖
    if os.path.exists(new_dir):
        return old_dir

    try:
        os.rename(old_dir, new_dir)
        return new_dir
    except OSError as e:
        print(f"⚠️ 目录重命名失败: {e}，保留原名")
        return old_dir
