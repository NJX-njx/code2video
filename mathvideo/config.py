# 导入操作系统相关功能，用于环境变量读取
import os
# 导入 dotenv 模块，用于从 .env 文件加载环境变量
from dotenv import load_dotenv

# 自动加载项目根目录下的 .env 文件
# 这样用户只需要创建 .env 文件并填入 API Key，无需手动设置环境变量
load_dotenv()

# ============================================================================
# Claude API 配置模块 (Anthropic)
# ============================================================================
# 本模块包含 Anthropic Claude API 的配置信息
# 使用 Claude Opus 4.5 作为主要的大语言模型

# Claude API密钥
# 用于身份验证，访问 Anthropic API 服务时必须提供
# 从环境变量读取，请设置 CLAUDE_API_KEY 环境变量
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Claude API的基础URL
# 这是 Anthropic 的官方 API 服务端点地址
CLAUDE_BASE_URL = "https://api.anthropic.com/v1"

# 使用的 Claude 模型名称
# "claude-opus-4-5-20251101" 是 Claude Opus 4.5 的完整版本名称
# 该模型支持超长上下文输入和高质量的代码生成
CLAUDE_MODEL_NAME = os.getenv("CLAUDE_MODEL_NAME", "claude-opus-4-5-20251101")

# ============================================================================
# Google Gemini Vision API 配置 (用于视觉反馈)
# ============================================================================
# 使用 Google Gemini 3 Pro 作为视觉大模型进行视频帧分析
# 从环境变量读取，请设置 GEMINI_API_KEY 环境变量
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini API 基础 URL (使用 OpenAI 兼容接口)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# 使用的视觉模型名称
# "gemini-2.0-flash" 经测试可用，支持多模态视觉分析且响应速度快
GEMINI_VISION_MODEL_NAME = "gemini-2.0-flash"

# ============================================================================
# 资产与功能配置
# ============================================================================

# IconFinder API Key (用于下载图标)
# 从环境变量读取，请设置 ICONFINDER_API_KEY 环境变量
ICONFINDER_API_KEY = os.getenv("ICONFINDER_API_KEY", "")

# 是否启用资产增强功能
USE_ASSETS = True

# 是否启用视觉反馈（High-end feature）
# 已验证 Gemini API 可用，启用视觉反馈以获得自动代码改进建议
USE_VISUAL_FEEDBACK = True

# 视频尺寸配置
FRAME_HEIGHT = 8.0
FRAME_WIDTH = 14.22
