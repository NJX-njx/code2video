#!/usr/bin/env python3
"""Extract up to 4 representative frames from a rendered video, resize them, and send to Gemini Vision for critique."""
import base64
import glob
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
    timeout=120
)

video_path = 'output/勾股定理/media/videos/section_1/480p15/Section1Scene.mp4'
frames_dir = '/tmp/test_frames_multi'
os.makedirs(frames_dir, exist_ok=True)

# Extract frames at 1 fps, scaled to width 320
subprocess.run([
    'ffmpeg', '-i', video_path,
    '-vf', 'fps=1,scale=320:-1',
    os.path.join(frames_dir, 'frame_%03d.png'), '-y'
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

frame_files = sorted(glob.glob(os.path.join(frames_dir, 'frame_*.png')))
if not frame_files:
    print('No frames extracted; aborting.')
    raise SystemExit(1)

# Pick up to 4 representative frames
if len(frame_files) > 4:
    indices = [0, len(frame_files)//3, 2*len(frame_files)//3, len(frame_files)-1]
    # ensure unique and in-range
    indices = sorted(list(dict.fromkeys([min(max(0, i), len(frame_files)-1) for i in indices])))
    selected = [frame_files[i] for i in indices]
else:
    selected = frame_files

print('Selected frames:')
for p in selected:
    print(' -', p, os.path.getsize(p), 'bytes')

image_contents = []
for p in selected:
    with open(p, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
        image_contents.append({
            'type': 'image_url',
            'image_url': {
                'url': f'data:image/png;base64,{b64}'
            }
        })

messages_payload = [
    {'type': 'text', 'text': '请对下面的图片帧进行简短的视觉反馈：描述主要可见元素、布局问题、颜色或可读性问题，给出 2-3 条改进建议（中文）。'},
    *image_contents
]

print('Sending request to Gemini with', len(image_contents), 'images...')
response = client.chat.completions.create(
    model=GEMINI_VISION_MODEL_NAME,
    messages=[{'role': 'user', 'content': messages_payload}],
    max_tokens=600
)

print('\n=== Gemini Vision Response ===')
print(response.choices[0].message.content)
print('=== End ===')
