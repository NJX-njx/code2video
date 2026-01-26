# 导入JSON处理模块，用于处理故事板数据结构（虽然本文件不直接使用，但保留以备将来扩展）
import json
# 导入LangChain的聊天提示模板类，用于构建LLM提示
from langchain_core.prompts import ChatPromptTemplate
# 导入LangChain的JSON输出解析器，用于将LLM输出解析为JSON格式
from langchain_core.output_parsers import JsonOutputParser
# 从llm_client模块导入get_llm函数，用于创建LLM客户端
from src.llm_client import get_llm
# 从prompts模块导入故事板生成的提示模板
from src.agents.prompts import PLANNER_PROMPT

def generate_storyboard(topic: str):
    """
    为给定的数学主题生成故事板JSON结构
    
    功能说明：
    本函数使用LLM（大语言模型）将数学主题分解为结构化的故事板。
    故事板包含多个章节，每个章节有标题、讲义笔记和对应的动画描述。
    这是视频生成流程的第一步，为后续的代码生成提供蓝图。
    
    参数:
        topic (str): 要讲解的数学主题
            示例："勾股定理"、"二次函数"、"微积分基础"等
    
    返回:
        dict: 故事板JSON结构，包含以下字段：
            {
                "topic": "主题名称",
                "sections": [
                    {
                        "id": "section_1",
                        "title": "章节标题",
                        "lecture_lines": ["笔记1", "笔记2", ...],
                        "animations": ["动画1", "动画2", ...]
                    },
                    ...
                ]
            }
        如果生成失败，返回None
    
    工作流程:
        1. 创建LLM客户端（temperature=0.7，平衡创造性和准确性）
        2. 从模板创建提示（包含主题信息）
        3. 构建处理链：提示 -> LLM -> JSON解析器
        4. 调用LLM生成故事板
        5. 解析并返回JSON结果
    
    错误处理:
        - 如果LLM调用失败，捕获异常并打印错误信息
        - 返回None表示生成失败，调用者需要检查返回值
    
    使用示例:
        storyboard = generate_storyboard("勾股定理")
        if storyboard:
            print(f"生成了{len(storyboard['sections'])}个章节")
            for section in storyboard['sections']:
                print(f"- {section['title']}")
    """
    # 创建LLM客户端实例
    # temperature=0.7：平衡模式，既有一定的创造性，又保持准确性
    llm = get_llm(temperature=0.7)
    # 从提示模板创建聊天提示模板
    # PLANNER_PROMPT包含故事板生成的详细指令和格式要求
    prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    # 构建处理链：提示模板 -> LLM -> JSON解析器
    # 使用管道操作符（|）连接各个处理步骤
    chain = prompt | llm | JsonOutputParser()
    
    # 打印开始生成故事板的信息
    print(f"Planning storyboard for: {topic}...")
    try:
        # 调用处理链，传入主题参数
        # invoke()方法会执行整个链：格式化提示 -> 调用LLM -> 解析JSON
        result = chain.invoke({"topic": topic})
        # 返回解析后的JSON结果（Python字典）
        return result
    except Exception as e:
        # 如果生成过程中出现任何异常，捕获并打印错误信息
        print(f"Error generating storyboard: {e}")
        # 返回None表示生成失败
        return None
