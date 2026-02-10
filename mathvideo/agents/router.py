# -*- coding: utf-8 -*-
"""
任务类型路由器

根据用户输入（文本 + 图片描述）判断任务类型，决定后续使用哪种 Pipeline 模式。
这是整个 Pipeline 的第一步，在 Planner 之前执行。

支持的任务类型:
- knowledge: 知识点讲解（如"勾股定理"、"二次方程"）
- geometry: 几何构造/作图题（如"如图，△ABC 是等边三角形…"）
- problem: 应用/计算题（如"某水池以每秒2L注水…求…"）
- proof: 证明推导题（如"证明: 正方形对角线互相垂直"）
"""
import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from mathvideo.llm_client import get_llm
from mathvideo.agents.prompts import ROUTER_PROMPT


# 合法的任务类型集合
VALID_TASK_TYPES = {"knowledge", "geometry", "problem", "proof"}

# 默认任务类型（分类失败时使用）
DEFAULT_TASK_TYPE = "knowledge"


def classify_task(prompt: str, image_context: Optional[str] = None) -> str:
    """
    根据用户输入判断任务类型

    通过 LLM 理解用户的真实意图，而非简单的关键词匹配。
    LLM 会综合考虑文本内容、图片描述、用户的明确指令等信息。

    参数:
        prompt (str): 用户输入的文本（可能是知识点、题目描述、或明确指令）
        image_context (str, 可选): 图片的文字描述（由视觉模型生成）

    返回:
        str: 任务类型标识，取值为 "knowledge" / "geometry" / "problem" / "proof"
    """
    # 使用低温度确保分类结果稳定一致
    llm = get_llm(temperature=0.1, max_tokens=1024)  # 分类任务只需短输出
    prompt_template = ChatPromptTemplate.from_template(ROUTER_PROMPT)
    chain = prompt_template | llm | StrOutputParser()

    print("🔀 正在分析任务类型...")
    try:
        result = chain.invoke({
            "input_text": prompt.strip() or "用户仅提供了图片",
            "image_context": image_context or "无",
        })

        # 从 LLM 输出中提取任务类型（容错处理）
        task_type = _parse_task_type(result)
        print(f"📋 任务类型: {task_type}")
        return task_type
    except Exception as e:
        print(f"⚠️ 任务分类失败: {e}，使用默认类型 '{DEFAULT_TASK_TYPE}'")
        return DEFAULT_TASK_TYPE


def _parse_task_type(raw_output: str) -> str:
    """
    从 LLM 输出中提取任务类型（容错解析）

    LLM 可能返回纯文本、JSON、或带有额外解释的文本。
    本函数尝试多种方式提取合法的任务类型标识。

    参数:
        raw_output (str): LLM 的原始输出文本

    返回:
        str: 标准化的任务类型标识
    """
    text = raw_output.strip().lower()

    # 方式1: 直接匹配（LLM 返回的就是类型名）
    if text in VALID_TASK_TYPES:
        return text

    # 方式2: 尝试 JSON 解析（LLM 可能返回 {"task_type": "geometry"}）
    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        if isinstance(data, dict):
            for key in ("task_type", "type", "category"):
                if data.get(key, "").lower() in VALID_TASK_TYPES:
                    return data[key].lower()
    except (json.JSONDecodeError, AttributeError):
        pass

    # 方式3: 在文本中搜索任务类型关键词（LLM 可能返回 "类型是 geometry"）
    for task_type in VALID_TASK_TYPES:
        if task_type in text:
            return task_type

    # 方式4: 中文关键词映射
    cn_mapping = {
        "知识点": "knowledge", "讲解": "knowledge", "概念": "knowledge",
        "几何": "geometry", "作图": "geometry", "构造": "geometry",
        "应用": "problem", "计算": "problem", "求解": "problem",
        "证明": "proof", "推导": "proof", "论证": "proof",
    }
    for cn_key, en_type in cn_mapping.items():
        if cn_key in text:
            return en_type

    # 所有方式都失败，返回默认类型
    print(f"⚠️ 无法从 LLM 输出中识别任务类型: '{raw_output}'，使用默认类型")
    return DEFAULT_TASK_TYPE


def get_section_mode(task_type: str) -> str:
    """
    根据任务类型返回 Section 生成模式

    参数:
        task_type (str): 任务类型标识

    返回:
        str: Section 生成模式
            - "independent": 各 Section 独立生成（知识点讲解、应用题）
            - "sequential": 各 Section 递进生成，后续 Section 依赖前序代码（几何构造、证明推导）
    """
    if task_type in ("geometry", "proof"):
        return "sequential"
    return "independent"
