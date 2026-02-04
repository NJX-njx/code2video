# 直接使用 requests 调用 Anthropic API
# 绕过 SDK 的 API 版本问题
import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import List, Optional, Any
# 从配置模块导入 Claude API 的配置信息
from mathvideo.config import CLAUDE_API_KEY, CLAUDE_MODEL_NAME


class ClaudeDirectChat(BaseChatModel):
    """
    直接使用 requests 调用 Anthropic API 的 LangChain 兼容聊天模型
    使用稳定的 API 版本 2023-06-01
    """
    
    model: str = CLAUDE_MODEL_NAME
    temperature: float = 0.7
    max_tokens: int = 8192
    api_key: str = CLAUDE_API_KEY
    api_url: str = "https://api.anthropic.com/v1/messages"
    api_version: str = "2023-06-01"
    
    def __init__(self, temperature: float = 0.7, max_tokens: int = 8192, **kwargs):
        super().__init__(**kwargs)
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @property
    def _llm_type(self) -> str:
        return "claude-direct"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> ChatResult:
        """调用 Claude API 生成回复"""
        # 将 LangChain 消息转换为 Anthropic 格式
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg.type == "system":
                system_message = msg.content
            elif msg.type == "human":
                anthropic_messages.append({"role": "user", "content": msg.content})
            elif msg.type == "ai":
                anthropic_messages.append({"role": "assistant", "content": msg.content})
        
        # 构建请求头
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json"
        }
        
        # 构建请求体
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": anthropic_messages,
        }
        
        if system_message:
            data["system"] = system_message
        
        if stop:
            data["stop_sequences"] = stop
        
        # 发送请求
        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        result = response.json()
        
        # 提取文本内容
        content = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        
        # 返回 LangChain 格式
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )


def get_llm(temperature=0.7):
    """
    创建并返回一个配置好的 Claude 聊天模型实例
    
    功能说明：
    本函数封装了Claude API的初始化逻辑，提供了一个统一的接口来创建LLM客户端。
    直接使用 requests 调用 API 以获得更好的兼容性。
    
    参数:
        temperature (float, 可选): 控制模型输出的随机性和创造性
            - 范围: 0.0 到 1.0
            - 较低值 (0.0-0.3): 输出更确定、更保守，适合代码生成和事实性任务
            - 中等值 (0.5-0.7): 平衡创造性和准确性，适合一般对话和内容生成
            - 较高值 (0.8-1.0): 输出更随机、更有创造性，适合创意写作
            - 默认值: 0.7（平衡模式）
    
    返回:
        ClaudeDirectChat: 配置好的聊天模型实例，可用于调用Claude API
    
    使用示例:
        # 创建默认配置的LLM（temperature=0.7）
        llm = get_llm()
        
        # 创建低温度LLM（适合代码生成）
        llm = get_llm(temperature=0.2)
        
        # 创建高温度LLM（适合创意内容）
        llm = get_llm(temperature=0.9)
    
    注意事项:
        - 需要确保CLAUDE_API_KEY和CLAUDE_MODEL_NAME在config.py中正确配置
        - max_tokens设置为8192，Claude支持更大的输出
        - 如果遇到API调用失败，请检查网络连接和API密钥是否有效
    """
    return ClaudeDirectChat(temperature=temperature, max_tokens=8192)
