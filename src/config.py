# 导入操作系统相关功能，用于环境变量读取
import os

# ============================================================================
# Kimi API 配置模块
# ============================================================================
# 本模块包含Kimi AI API的配置信息
# 这些配置用于连接百度AI Studio的Kimi大语言模型服务

# Kimi API密钥
# 用于身份验证，访问Kimi API服务时必须提供
# 从环境变量读取，请设置 KIMI_API_KEY 环境变量
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")

# Kimi API的基础URL
# 这是百度AI Studio的LLM API服务端点地址
# 所有API请求都将发送到此基础URL
KIMI_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"

# 使用的Kimi模型名称
# "kimi-k2-instruct" 是Kimi的指令调优版本，适合生成代码和结构化输出
# 该模型支持长文本输入和高质量的输出生成
KIMI_MODEL_NAME = "kimi-k2-instruct"

# ============================================================================
# Hugging Face Vision API 配置 (用于视觉反馈)
# ============================================================================
# 使用 Hugging Face Inference API 调用开源视觉大模型 (如 Qwen2-VL)
# 从环境变量读取，请设置 HF_API_KEY 环境变量
HF_API_KEY = os.getenv("HF_API_KEY", "")

# HF API 基础 URL (使用 openai 兼容接口)
HF_BASE_URL = "https://router.huggingface.co/v1"

# 使用的视觉模型名称
HF_VISION_MODEL_NAME = "Qwen/Qwen2.5-VL-72B-Instruct"

# ============================================================================
# 资产与功能配置
# ============================================================================

# IconFinder API Key (用于下载图标)
# 请在此处填入您的 IconFinder API Key
ICONFINDER_API_KEY = ""

# 是否启用资产增强功能
USE_ASSETS = True

# 是否启用视觉反馈（High-end feature）
USE_VISUAL_FEEDBACK = True

# 视频尺寸配置
FRAME_HEIGHT = 8.0
FRAME_WIDTH = 14.22

