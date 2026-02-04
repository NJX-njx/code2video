import hashlib
import re
from typing import Optional


def slugify(value: str) -> str:
    """
    将字符串规范化为 URL 友好格式
    """
    value = str(value)
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def make_slug(value: str, max_length: int = 40, extra: Optional[str] = None) -> str:
    """
    为任意输入生成可控长度的 slug。

    - 当输入过长时，会截断并附加短哈希，避免路径过长
    - 可通过 extra 增加区分度（例如图片文件名）
    """
    base = slugify(value)
    if not base:
        base = "project"

    basis = value if extra is None else f"{value}|{extra}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:8]

    if len(base) <= max_length:
        return base

    # 预留 1 个分隔符和 8 位哈希
    prefix_len = max(1, max_length - 9)
    prefix = base[:prefix_len].rstrip("-") or "project"
    return f"{prefix}-{digest}"
