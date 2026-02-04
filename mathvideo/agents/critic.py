import json
import base64
import requests
from mathvideo.agents.prompts import CRITIC_PROMPT
from mathvideo.config import USE_VISUAL_FEEDBACK, CLAUDE_API_KEY, CLAUDE_MODEL_NAME

class VisualCritic:
    """
    视觉评估器：使用 Claude Opus 4.5 Vision 对渲染的视频帧进行分析和反馈。
    Claude 支持多模态输入，可以直接分析图片内容。
    """
    def __init__(self):
        pass

    def _call_claude_vision(self, messages_content):
        """
        直接调用 Claude API 进行视觉分析。
        使用 HTTP 请求而非 SDK，以确保兼容性。
        """
        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": CLAUDE_MODEL_NAME,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": messages_content
                }
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()

    def critique(self, video_path, storyboard_section):
        """
        Analyze the video (or frames from it) and return feedback.
        使用 Claude Opus 4.5 进行视觉分析。
        """
        if not USE_VISUAL_FEEDBACK:
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

            # 3. 构建 Claude Vision API 的消息格式
            # Claude 使用不同于 OpenAI 的图片格式
            messages_content = [
                {"type": "text", "text": CRITIC_PROMPT}
            ]
            
            for img_path in selected_frames:
                with open(img_path, "rb") as image_file:
                    b64_data = base64.b64encode(image_file.read()).decode('utf-8')
                    messages_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": b64_data
                        }
                    })

            # 4. 调用 Claude Vision API
            response = self._call_claude_vision(messages_content)
            content = response["content"][0]["text"]
            
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
