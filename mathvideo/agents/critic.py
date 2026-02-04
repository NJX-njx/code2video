import base64
import json
from openai import OpenAI
from mathvideo.agents.prompts import CRITIC_PROMPT
from mathvideo.config import (
    USE_VISUAL_FEEDBACK,
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_VISION_MODEL_NAME,
)

class VisualCritic:
    """
    视觉评估器：使用 Gemini 3 Pro 对渲染的视频帧进行分析和反馈。
    Gemini 支持多模态输入，可以直接分析图片内容。
    """
    def __init__(self):
        self.enabled = USE_VISUAL_FEEDBACK and bool(GEMINI_API_KEY)
        self.client = None
        if self.enabled:
            self.client = OpenAI(
                base_url=GEMINI_BASE_URL,
                api_key=GEMINI_API_KEY,
                timeout=120
            )

    def _call_gemini_vision(self, messages_content):
        """
        调用 Gemini API 进行视觉分析（OpenAI 兼容接口）。
        """
        response = self.client.chat.completions.create(
            model=GEMINI_VISION_MODEL_NAME,
            messages=[{"role": "user", "content": messages_content}],
            max_tokens=1024
        )
        return response.choices[0].message.content

    def critique(self, video_path, storyboard_section):
        """
        Analyze the video (or frames from it) and return feedback.
        使用 Gemini 3 Pro 进行视觉分析。
        """
        if not self.enabled:
            if USE_VISUAL_FEEDBACK and not GEMINI_API_KEY:
                print("   ⚠️ GEMINI_API_KEY 未设置，跳过视觉分析。")
            return None

        print(f"🧐 Critiquing video: {video_path}")
        
        # 1. Extract Multiple Frames (every 1 second)
        import subprocess
        import glob
        import os
        
        frames_dir = os.path.join(os.path.dirname(video_path), "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Clear old frames
        for f in glob.glob(os.path.join(frames_dir, "frame_*.png")):
            os.remove(f)
            
        try:
            # Extract frames: 1 frame per second, scaled to 320px width to reduce payload size
            # 缩小图片尺寸可以减少 token 消耗并加快响应速度
            image_pattern = os.path.join(frames_dir, "frame_%03d.png")
            subprocess.run([
                "ffmpeg", "-i", video_path, 
                "-vf", "fps=1.0,scale=320:-1", 
                image_pattern, "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # 2. Collect up to 4 frames (Start, Middle, Middle, End)
            frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
            
            # Logic to pick representative frames (max 4 to save tokens and time)
            if len(frame_files) > 4:
                # Pick first, last, and equidistant middle ones
                indices = [0, len(frame_files)//3, 2*len(frame_files)//3, len(frame_files)-1]
                selected_frames = [frame_files[i] for i in indices]
            else:
                selected_frames = frame_files

            if not selected_frames:
                print("   ⚠️ No frames extracted for critique.")
                return None

            # 3. 构建 Gemini Vision API 的消息格式（OpenAI 兼容）
            messages_content = [
                {"type": "text", "text": CRITIC_PROMPT}
            ]

            for img_path in selected_frames:
                with open(img_path, "rb") as image_file:
                    b64_data = base64.b64encode(image_file.read()).decode("utf-8")
                    messages_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_data}"
                        }
                    })

            # 4. 调用 Gemini Vision API
            content = self._call_gemini_vision(messages_content)
            
            # Parse JSON
            content = content.replace("```json", "").replace("```", "").strip()
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}")+1]

            feedback = json.loads(content)
            
            if feedback.get("has_issues"):
                print(f"   ⚠️ Issues found: {feedback['issues']}")
                return feedback['suggestion']
            else:
                print("   ✅ Visual check passed.")
                return None
                
        except Exception as e:
            print(f"   Visual critique failed (soft fail): {e}")
            return None
