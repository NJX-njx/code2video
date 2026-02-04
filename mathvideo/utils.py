import hashlib
import re
from typing import Optional


def slugify(value: str) -> str:
    """
    将字符串规范化为 URL 友好格式（ASCII 优先，避免过长/难读路径）
    """
    value = str(value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.ASCII)
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def make_slug(value: str, max_length: int = 32, extra: Optional[str] = None) -> str:
    """
    为任意输入生成可控长度的 slug。

    - 当输入过长时，会截断并附加短哈希，避免路径过长
    - 可通过 extra 增加区分度（例如图片文件名）
    """
    base = slugify(value) or "project"
    basis = value if extra is None else f"{value}|{extra}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:8]
    suffix = f"-{digest}"

    max_base_len = max(1, max_length - len(suffix))
    if len(base) > max_base_len:
        base = base[:max_base_len].rstrip("-") or "project"

    return f"{base}{suffix}"
