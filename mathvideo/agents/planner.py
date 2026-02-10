# 导入JSON处理模块，用于处理故事板数据结构（虽然本文件不直接使用，但保留以备将来扩展）
import base64
import json
import os
from typing import List, Optional
import requests
import json5

# 导入LangChain的聊天提示模板类，用于构建LLM提示
from langchain_core.prompts import ChatPromptTemplate
# 导入LangChain的JSON输出解析器，用于将LLM输出解析为JSON格式
from langchain_core.output_parsers import JsonOutputParser
# 从llm_client模块导入get_llm函数，用于创建LLM客户端
from mathvideo.llm_client import get_llm
# 从 prompts 模块导入故事板生成的各类型提示模板
from mathvideo.agents.prompts import (
    PLANNER_PROMPT,
    PLANNER_GEOMETRY_PROMPT,
    PLANNER_PROOF_PROMPT,
)
from mathvideo.agents.skill_manager import load_skills
from mathvideo.config import (
    GEMINI_API_KEY,
    CLAUDE_API_KEY,
    CLAUDE_BASE_URL,
    CLAUDE_MODEL_NAME,
)
from mathvideo.gemini_native import generate_content_from_parts, messages_content_to_parts


def _extract_json_block(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("```json", "").replace("```", "").strip()
    if "{" in cleaned and "}" in cleaned:
        cleaned = cleaned[cleaned.find("{"): cleaned.rfind("}") + 1]
    return cleaned


def _escape_inner_quotes(payload: str) -> str:
    """
    尝试修复字符串中的未转义双引号，避免 JSON 解析失败。
    """
    if not payload:
        return payload
    out = []
    in_str = False
    i = 0
    while i < len(payload):
        ch = payload[i]
        if ch == "\"" and (i == 0 or payload[i - 1] != "\\"):
            if in_str:
                # lookahead to decide if this is closing quote
                j = i + 1
                while j < len(payload) and payload[j].isspace():
                    j += 1
                if j < len(payload) and payload[j] in {",", "}", "]", ":"}:
                    in_str = False
                    out.append(ch)
                else:
                    out.append("\\\"")
            else:
                in_str = True
                out.append(ch)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _parse_storyboard_json(raw_text: str, llm=None) -> Optional[dict]:
    cleaned = _extract_json_block(raw_text)
    for loader in (json.loads, json5.loads):
        try:
            return loader(cleaned)
        except Exception:
            pass

    repaired = _escape_inner_quotes(cleaned)
    for loader in (json.loads, json5.loads):
        try:
            return loader(repaired)
        except Exception:
            pass

    # 最后尝试用模型修复
    if llm:
        try:
            fix_prompt = (
                "请修复下面的 JSON，使其严格合法，并只输出修复后的 JSON：\n"
                f"```json\n{cleaned}\n```"
            )
            fixed = llm.invoke(fix_prompt)
            fixed_text = getattr(fixed, "content", None) or str(fixed)
            fixed_cleaned = _extract_json_block(fixed_text)
            for loader in (json.loads, json5.loads):
                try:
                    return loader(fixed_cleaned)
                except Exception:
                    pass
        except Exception:
            pass
    return None

def _describe_images(image_paths: List[str]) -> Optional[str]:
    """
    使用 Gemini 视觉模型对输入图片进行简要描述，便于生成故事板。
    """
    if not image_paths:
        return None
    if not GEMINI_API_KEY and not CLAUDE_API_KEY:
        print("⚠️ GEMINI/CLAUDE API Key 未设置，跳过图片理解。")
        return None

    messages_content = [
        {
            "type": "text",
            "text": (
                "请描述这些图片中的数学内容或题意，提取关键概念、图形关系、已知/未知量。"
                "输出应简洁清晰（中文，100-200字），用于生成教学分镜。"
            ),
        }
    ]

    # 限制图片数量，避免 token 过高
    for img_path in image_paths[:3]:
        try:
            with open(img_path, "rb") as image_file:
                b64_data = base64.b64encode(image_file.read()).decode("utf-8")
                messages_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64_data}"
                    }
                })
        except Exception as e:
            print(f"⚠️ 读取图片失败: {img_path} ({e})")

    def _call_gemini():
        if not GEMINI_API_KEY:
            return None
        try:
            parts = messages_content_to_parts(messages_content)
            content = generate_content_from_parts(parts, timeout=120)
            if not content:
                print("⚠️ Gemini 返回空内容，尝试回退到 Claude。")
                return None
            return content.strip()
        except Exception as e:
            print(f"⚠️ Gemini 图片理解失败: {e}")
            return None

    def _call_claude():
        if not CLAUDE_API_KEY:
            return None

        def _to_claude_blocks(items):
            blocks = []
            for item in items:
                if item.get("type") == "text":
                    blocks.append({"type": "text", "text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    if not image_url.startswith("data:"):
                        continue
                    header, b64_data = image_url.split(",", 1)
                    media_type = header.split(";")[0].replace("data:", "")
                    blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_data,
                        },
                    })
            return blocks

        blocks = _to_claude_blocks(messages_content)
        if not blocks:
            return None

        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": CLAUDE_MODEL_NAME,
            "max_tokens": 512,
            "system": "请用中文简要描述图片中的数学内容或题意，提取关键概念、图形关系、已知/未知量，100-200字。",
            "messages": [{"role": "user", "content": blocks}],
        }
        try:
            response = requests.post(
                f"{CLAUDE_BASE_URL}/messages",
                headers=headers,
                json=payload,
                timeout=120,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Claude API error {response.status_code}: {response.text[:200]}")
            data = response.json()
            content_blocks = data.get("content", [])
            text = "".join(
                block.get("text", "") for block in content_blocks if block.get("type") == "text"
            )
            return text.strip() if text else None
        except Exception as e:
            print(f"⚠️ Claude 图片理解失败: {e}")
            return None

    content = _call_gemini()
    if not content and CLAUDE_API_KEY:
        print("🔁 切换到 Claude 进行图片理解。")
        content = _call_claude()
    return content


def generate_storyboard(prompt: str, image_paths: Optional[List[str]] = None, task_type: str = "knowledge"):
    """
    为给定的输入生成故事板JSON结构
    
    功能说明：
    本函数使用LLM将数学主题/问题/描述分解为结构化的故事板。
    根据任务类型选择不同的 Prompt 模板，生成匹配的分镜结构。
    
    参数:
        prompt (str): 用户输入文本
        image_paths (List[str], 可选): 输入图片路径列表
        task_type (str): 任务类型（knowledge/geometry/problem/proof）
    
    返回:
        dict: 故事板JSON结构，包含 task_type 字段
    """
    # 根据任务类型选择对应的 Prompt 模板
    prompt_map = {
        "knowledge": PLANNER_PROMPT,
        "geometry": PLANNER_GEOMETRY_PROMPT,
        "problem": PLANNER_PROMPT,       # 应用题复用通用模板
        "proof": PLANNER_PROOF_PROMPT,
    }
    selected_prompt = prompt_map.get(task_type, PLANNER_PROMPT)
    
    # 加载对应类型的 Skill 并追加到 Prompt 末尾
    skills_text = load_skills(task_type)
    if skills_text:
        selected_prompt = selected_prompt + "\n" + skills_text
    
    # 创建LLM客户端实例
    # max_tokens=16384：storyboard JSON 可能很长（多 section、详细描述），需要充足空间
    llm = get_llm(temperature=0.7, max_tokens=16384)
    # 从提示模板创建聊天提示模板
    prompt_template = ChatPromptTemplate.from_template(selected_prompt)
    # 构建处理链
    chain = prompt_template | llm | JsonOutputParser()
    
    # 打印开始生成故事板的信息
    print(f"Planning storyboard for: {prompt or '（仅图片输入）'} [type={task_type}]...")
    try:
        image_context = _describe_images(image_paths or []) if image_paths else None
        input_text = prompt.strip() if prompt else ""
        if not input_text and image_context:
            input_text = "用户仅提供了图片，请基于图像描述生成分镜。"

        payload = {
            "input_text": input_text,
            "image_context": image_context or "无",
        }

        # 调用处理链，传入输入文本与图像描述
        # invoke()方法会执行整个链：格式化提示 -> 调用LLM -> 解析JSON
        result = chain.invoke(payload)

        # 附加元信息，便于回溯
        result["input_text"] = prompt
        result["task_type"] = task_type  # 将任务类型存入 storyboard
        if image_context:
            result["image_context"] = image_context
        if image_paths:
            result["input_images"] = [os.path.basename(p) for p in image_paths]
        # 返回解析后的JSON结果（Python字典）
        return result
    except Exception as e:
        # 如果生成过程中出现任何异常，尝试回退解析
        print(f"Error generating storyboard: {e}")
        try:
            raw_prompt = selected_prompt.format(
                input_text=input_text,
                image_context=image_context or "无",
            )
            raw = llm.invoke(raw_prompt)
            raw_text = getattr(raw, "content", None) or str(raw)
            fixed = _parse_storyboard_json(raw_text, llm=llm)
            if fixed:
                fixed["input_text"] = prompt
                fixed["task_type"] = task_type
                if image_context:
                    fixed["image_context"] = image_context
                if image_paths:
                    fixed["input_images"] = [os.path.basename(p) for p in image_paths]
                return fixed
        except Exception:
            pass
        # 返回None表示生成失败
        return None
