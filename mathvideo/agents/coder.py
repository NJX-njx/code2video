# 导入正则表达式模块，用于清理生成的代码（移除markdown标记等）
import re
# 导入LangChain的聊天提示模板类，用于构建代码生成提示
from langchain_core.prompts import ChatPromptTemplate
# 导入LangChain的字符串输出解析器，用于提取LLM生成的代码文本
from langchain_core.output_parsers import StrOutputParser
# 从llm_client模块导入get_llm函数，用于创建LLM客户端
from mathvideo.llm_client import get_llm
# 从prompts模块导入代码生成和修复的提示模板
from mathvideo.agents.prompts import CODER_PROMPT, CODER_SEQUENTIAL_PROMPT, FIX_CODE_PROMPT, REFINE_CODE_PROMPT
from mathvideo.agents.skill_manager import load_skills

def generate_code(section_data: dict, previous_code: str = "", task_type: str = "knowledge"):
    """
    为特定章节生成Manim Python代码
    
    功能说明：
    本函数使用LLM根据章节的故事板数据生成完整的Manim动画代码。
    对于递进式任务（geometry/proof），会将前序 Section 的完整代码作为上下文传入。
    
    参数:
        section_data (dict): 章节数据字典
        previous_code (str): 前序 Section 的完整代码（仅递进模式使用）
        task_type (str): 任务类型，用于选择 Prompt 模板和加载 Skill
    
    返回:
        tuple: (code, class_name) 元组
    """
    # 创建LLM客户端实例
    # max_tokens=16384：代码生成任务需要充足的输出空间，避免代码被截断
    llm = get_llm(temperature=0.5, max_tokens=16384)
    
    # 根据任务类型和是否有前序代码选择 Prompt 模板
    is_sequential = (task_type in ("geometry", "proof")) and bool(previous_code)
    base_prompt = CODER_SEQUENTIAL_PROMPT if is_sequential else CODER_PROMPT
    
    # 加载对应类型的 Skill 并追加到 Prompt
    skills_text = load_skills(task_type)
    if skills_text:
        base_prompt = base_prompt + "\n" + skills_text
    
    prompt = ChatPromptTemplate.from_template(base_prompt)
    chain = prompt | llm | StrOutputParser()
    
    # 打印开始生成代码的信息
    mode_label = "递进模式" if is_sequential else "独立模式"
    print(f"Generating code for section: {section_data['title']} [{mode_label}]...")
    
    try:
        # 构建调用参数
        invoke_params = {
            "title": section_data['title'],
            "lecture_lines": section_data['lecture_lines'],
            "animations": section_data['animations'],
        }
        
        # 递进模式额外传入前序代码和对象信息
        if is_sequential:
            invoke_params["previous_code"] = previous_code
            invoke_params["inherited_objects"] = section_data.get("inherited_objects", [])
            invoke_params["new_objects"] = section_data.get("new_objects", [])
        
        # 调用处理链
        code = chain.invoke(invoke_params)
        
        # 清理代码：移除markdown代码块标记（```python和```）
        code = clean_code(code)
        
        # 确保类名唯一且正确
        # 虽然可以信任LLM生成的类名，但为了确保唯一性，我们基于章节ID重命名
        # 提示中要求生成"SectionScene"，但我们希望类名基于章节ID，如"Section1Scene"
        
        # 生成基于章节ID的类名
        # 例如："section_1" -> "Section1Scene"
        # 步骤：移除下划线 -> 首字母大写 -> 添加"Scene"后缀
        class_name = section_data['id'].replace("_", "").title() + "Scene"
        # 在代码中将"SectionScene"替换为新的类名
        code = code.replace("class SectionScene", f"class {class_name}")
        
        # 返回清理后的代码和类名
        return code, class_name
    except Exception as e:
        # 如果生成过程中出现任何异常，捕获并打印错误信息
        print(f"Error generating code: {e}")
        # 返回None表示生成失败
        return None, None

def fix_code(code: str, error_message: str):
    """
    根据错误信息修复生成的代码
    
    功能说明：
    本函数使用LLM分析代码错误并自动修复代码。
    这是自动错误修复机制的核心，当Manim渲染失败时会被调用。
    通过提供原始代码和错误信息，LLM可以识别问题并生成修复后的代码。
    
    参数:
        code (str): 出错的原始代码字符串
        error_message (str): 错误信息（通常来自Manim渲染的错误输出）
            包含错误类型、错误位置、错误描述等信息
    
    返回:
        str: 修复后的代码字符串，如果修复失败则为None
    
    工作流程:
        1. 创建LLM客户端（temperature=0.2，极低温度确保修复的准确性）
        2. 从修复提示模板创建聊天提示模板
        3. 构建处理链：提示 -> LLM -> 字符串解析器
        4. 调用LLM，传入原始代码和错误信息
        5. 清理修复后的代码（移除markdown标记）
        6. 返回修复后的代码
    
    错误修复策略:
        - LLM会分析错误信息，识别问题类型（语法错误、API错误、逻辑错误等）
        - 根据错误类型应用相应的修复策略
        - 保持代码的整体结构和类名不变
        - 只修复导致错误的部分
    
    使用场景:
        - Manim渲染失败时的自动重试机制
        - 代码生成后的验证和修复
        - 提高代码生成的成功率
    
    注意:
        - 修复可能不会100%成功，可能需要多次尝试
        - 如果修复失败，返回None，调用者需要处理
    """
    # 创建LLM客户端实例
    # temperature=0.2：极低温度，确保修复的准确性和一致性
    # 代码修复需要精确性，所以使用极低温度
    # max_tokens=16384：修复后的代码可能与原始代码等长，需要足够空间
    llm = get_llm(temperature=0.2, max_tokens=16384)
    # 从代码修复提示模板创建聊天提示模板
    # FIX_CODE_PROMPT包含错误修复的详细指令和格式要求
    prompt = ChatPromptTemplate.from_template(FIX_CODE_PROMPT)
    # 构建处理链：提示模板 -> LLM -> 字符串解析器
    # 使用管道操作符（|）连接各个处理步骤
    chain = prompt | llm | StrOutputParser()
    
    # 打印开始修复代码的信息
    print(f"🔧 Attempting to fix code...")
    
    try:
        # 调用处理链，传入原始代码和错误信息
        # invoke()方法会执行整个链：格式化提示 -> 调用LLM -> 提取字符串
        fixed_code = chain.invoke({
            "code": code,  # 原始代码
            "error": error_message  # 错误信息
        })
        
        # 清理修复后的代码：移除markdown代码块标记
        return clean_code(fixed_code)
    except Exception as e:
        # 如果修复过程中出现任何异常，捕获并打印错误信息
        print(f"Error fixing code: {e}")
        # 返回None表示修复失败
        return None

def refine_code(code: str, feedback: str):
    """
    根据视觉反馈优化代码
    
    功能说明：
    本函数使用LLM根据视觉批评agent提供的反馈来改进代码。
    主要用于解决布局问题（如重叠、越界）和视觉美感问题。
    
    参数:
        code (str): 原始Manim代码
        feedback (str): 具体的优化建议或问题描述
        
    返回:
        str: 优化后的代码字符串，如果失败则返回None
    """
    # 创建LLM客户端
    # temperature=0.3：适中的温度，允许一点灵活性来调整布局，但保持逻辑
    # max_tokens=16384：优化后的代码需要完整输出
    llm = get_llm(temperature=0.3, max_tokens=16384)
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_template(REFINE_CODE_PROMPT)
    
    # 构建链
    chain = prompt | llm | StrOutputParser()
    
    print(f"✨ Refining code based on specific feedback...")
    
    try:
        # 调用LLM
        refined_code = chain.invoke({
            "code": code,
            "feedback": feedback
        })
        
        # 清理并返回代码
        return clean_code(refined_code)
    except Exception as e:
        print(f"Error refining code: {e}")
        return None

def clean_code(code_str):
    """
    清理代码字符串，移除markdown代码块标记
    
    功能说明：
    LLM生成的代码可能包含markdown格式的代码块标记（```python和```）。
    本函数移除这些标记，提取纯Python代码。
    
    参数:
        code_str (str): 可能包含markdown标记的代码字符串
    
    返回:
        str: 清理后的纯代码字符串（去除首尾空白）
    
    处理逻辑:
        1. 如果包含"```python"，提取python代码块中的内容
        2. 否则如果包含"```"，提取第一个代码块中的内容
        3. 去除首尾空白字符
    
    使用示例:
        code = "```python\\nprint('hello')\\n```"
        clean = clean_code(code)  # 返回: "print('hello')"
    """
    # 检查是否包含Python代码块标记
    if "```python" in code_str:
        # 提取```python和```之间的内容
        # split("```python")[1]：获取第一个标记后的部分
        # split("```")[0]：获取第二个标记前的内容
        code_str = code_str.split("```python")[1].split("```")[0]
    # 如果没有Python标记，检查是否有通用代码块标记
    elif "```" in code_str:
        # 提取第一个```和第二个```之间的内容
        code_str = code_str.split("```")[1].split("```")[0]
    # 去除首尾的空白字符（空格、换行符等）并返回
    return code_str.strip()
