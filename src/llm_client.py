# 导入LangChain的OpenAI兼容聊天模型类
# 虽然类名是ChatOpenAI，但它支持通过base_url参数连接到其他兼容OpenAI API格式的服务
from langchain_openai import ChatOpenAI
# 从配置模块导入Kimi API的配置信息
from src.config import KIMI_API_KEY, KIMI_BASE_URL, KIMI_MODEL_NAME

def get_llm(temperature=0.7):
    """
    创建并返回一个配置好的LangChain ChatOpenAI实例，用于连接Kimi API
    
    功能说明：
    本函数封装了Kimi API的初始化逻辑，提供了一个统一的接口来创建LLM客户端。
    使用LangChain的ChatOpenAI类，通过设置base_url来连接到Kimi服务。
    
    参数:
        temperature (float, 可选): 控制模型输出的随机性和创造性
            - 范围: 0.0 到 2.0
            - 较低值 (0.0-0.3): 输出更确定、更保守，适合代码生成和事实性任务
            - 中等值 (0.5-0.7): 平衡创造性和准确性，适合一般对话和内容生成
            - 较高值 (0.8-2.0): 输出更随机、更有创造性，适合创意写作
            - 默认值: 0.7（平衡模式）
    
    返回:
        ChatOpenAI: 配置好的LangChain聊天模型实例，可用于调用Kimi API
    
    使用示例:
        # 创建默认配置的LLM（temperature=0.7）
        llm = get_llm()
        
        # 创建低温度LLM（适合代码生成）
        llm = get_llm(temperature=0.2)
        
        # 创建高温度LLM（适合创意内容）
        llm = get_llm(temperature=0.9)
    
    注意事项:
        - 需要确保KIMI_API_KEY、KIMI_BASE_URL和KIMI_MODEL_NAME在config.py中正确配置
        - max_tokens设置为32768，这是Kimi模型支持的最大输出长度
        - 如果遇到API调用失败，请检查网络连接和API密钥是否有效
    """
    # 创建ChatOpenAI实例，配置为使用Kimi API
    llm = ChatOpenAI(
        # 设置API密钥，用于身份验证
        api_key=KIMI_API_KEY,
        # 设置API的基础URL，指向Kimi服务端点
        base_url=KIMI_BASE_URL,
        # 指定要使用的模型名称
        model=KIMI_MODEL_NAME,
        # 设置温度参数，控制输出的随机性
        temperature=temperature,
        # 设置最大输出token数（32768是Kimi模型的最大支持值）
        # 可以根据实际需求调整，但不应超过模型限制
        max_tokens=32768, # Adjust as needed
    )
    # 返回配置好的LLM实例
    return llm
