import base64
import os
from typing import List, Optional

import requests

from mathvideo.config import GEMINI_API_KEY, GEMINI_VISION_MODEL_NAME, GEMINI_NATIVE_BASE_URL


def _guess_mime_type(data_url_header: Optional[str], file_path: Optional[str]) -> str:
    if data_url_header:
        # data:image/png;base64
        if data_url_header.startswith("data:"):
            return data_url_header.split(";")[0].replace("data:", "") or "image/png"
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if ext == ".webp":
            return "image/webp"
        if ext == ".gif":
            return "image/gif"
    return "image/png"


def messages_content_to_parts(messages_content: List[dict]) -> List[dict]:
    """
    将 OpenAI 兼容的 messages_content 转为 Gemini 原生 parts.
    支持 type=text / image_url(data URL) 结构。
    """
    parts: List[dict] = []
    for item in messages_content:
        if item.get("type") == "text":
            text = item.get("text", "")
            if text:
                parts.append({"text": text})
        elif item.get("type") == "image_url":
            image_url = item.get("image_url", {}).get("url", "")
            if not image_url.startswith("data:"):
                continue
            header, b64_data = image_url.split(",", 1)
            mime = _guess_mime_type(header, None)
            parts.append({
                "inlineData": {
                    "mimeType": mime,
                    "data": b64_data,
                }
            })
    return parts


def file_to_inline_part(file_path: str) -> Optional[dict]:
    try:
        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        mime = _guess_mime_type(None, file_path)
        return {
            "inlineData": {
                "mimeType": mime,
                "data": b64_data,
            }
        }
    except Exception:
        return None


def generate_content_from_parts(
    parts: List[dict],
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
) -> Optional[str]:
    """
    调用 Gemini 原生 API (generateContent)，返回拼接后的文本内容。
    """
    api_key = api_key or GEMINI_API_KEY
    model = model or GEMINI_VISION_MODEL_NAME
    if not api_key:
        return None
    if not parts:
        return None

    url = f"{GEMINI_NATIVE_BASE_URL}/models/{model}:generateContent"
    params = {"key": api_key}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ]
    }

    response = requests.post(url, params=params, json=payload, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:200]}")
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        return None
    content = candidates[0].get("content", {})
    parts_out = content.get("parts") or []
    texts = [p.get("text", "") for p in parts_out if p.get("text")]
    text = "".join(texts).strip()
    return text or None
