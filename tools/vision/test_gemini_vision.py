#!/usr/bin/env python3
"""测试 Gemini Vision API"""
import base64
import os
import subprocess
import sys
from pathlib import Path
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from mathvideo.config import GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_VISION_MODEL_NAME

if not GEMINI_API_KEY:
    raise SystemExit("Missing GEMINI_API_KEY. Set it in your .env or environment.")

client = OpenAI(
    base_url=GEMINI_BASE_URL,
    api_key=GEMINI_API_KEY,
    timeout=60  # 增加超时时间
)

# 用已存在的视频帧测试，缩小尺寸
os.makedirs('/tmp/test_frames', exist_ok=True)
subprocess.run(['ffmpeg', '-i', 'output/勾股定理/media/videos/section_1/480p15/Section1Scene.mp4', 
                '-vf', 'fps=1,scale=320:-1', '-frames:v', '1', '/tmp/test_frames/frame_small.png', '-y'],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
frame_path = '/tmp/test_frames/frame_small.png'

# 检查文件大小
file_size = os.path.getsize(frame_path)
print(f'Using frame: {frame_path} (size: {file_size} bytes)')

with open(frame_path, 'rb') as f:
    b64_data = base64.b64encode(f.read()).decode('utf-8')

print(f'Base64 data length: {len(b64_data)} chars')
print('Sending request to Gemini Vision API...')

response = client.chat.completions.create(
    model=GEMINI_VISION_MODEL_NAME,
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': 'Describe what you see in this image briefly.'},
            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64_data}'}}
        ]
    }],
    max_tokens=200
)

print(f'Vision Response: {response.choices[0].message.content}')
