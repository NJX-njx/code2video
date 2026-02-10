import base64
import json
import requests
from mathvideo.agents.prompts import CRITIC_PROMPT
from mathvideo.config import (
    USE_VISUAL_FEEDBACK,
    GEMINI_API_KEY,
    CLAUDE_API_KEY,
    CLAUDE_BASE_URL,
    CLAUDE_MODEL_NAME,
)
from mathvideo.gemini_native import generate_content_from_parts, messages_content_to_parts

class VisualCritic:
    """
    视觉评估器：使用 Gemini 3 Pro 对渲染的视频帧进行分析和反馈。
    Gemini 支持多模态输入，可以直接分析图片内容。
    """
    def __init__(self):
        self.gemini_enabled = USE_VISUAL_FEEDBACK and bool(GEMINI_API_KEY)
        self.claude_enabled = USE_VISUAL_FEEDBACK and bool(CLAUDE_API_KEY)
        self.enabled = self.gemini_enabled or self.claude_enabled

    def _call_gemini_vision(self, messages_content):
        """
        调用 Gemini 原生 API 进行视觉分析。
        """
        try:
            parts = messages_content_to_parts(messages_content)
            content = generate_content_from_parts(parts, timeout=120)
            if not content:
                print("   ⚠️ Gemini 返回空内容，将尝试回退到 Claude。")
                return None
            return content if isinstance(content, str) else str(content)
        except Exception as e:
            print(f"   ⚠️ Gemini 视觉调用失败: {e}")
            return None

    def _call_claude_vision(self, messages_content):
        """
        调用 Claude 进行视觉分析（Anthropic Messages API）。
        """
        if not self.claude_enabled:
            return None

        def _to_claude_blocks(items):
            blocks = []
            for item in items:
                if item.get("type") == "text":
                    blocks.append({"type": "text", "text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    if not image_url.startswith("data:"):
                        continue
                    header, b64_data = image_url.split(",", 1)
                    media_type = header.split(";")[0].replace("data:", "")
                    blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_data,
                        },
                    })
            return blocks

        blocks = _to_claude_blocks(messages_content)
        if not blocks:
            return None

        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": CLAUDE_MODEL_NAME,
            "max_tokens": 4096,  # Critic 需要足够空间输出详细的视觉分析反馈
            "system": CRITIC_PROMPT,
            # Claude 的 system 已包含 CRITIC_PROMPT，
            # 用户消息中过滤掉重复的 CRITIC_PROMPT 文本
            "messages": [{"role": "user", "content": [
                b for b in blocks if not (b.get("type") == "text" and b.get("text") == CRITIC_PROMPT)
            ] or blocks}],
        }
        try:
            response = requests.post(
                f"{CLAUDE_BASE_URL}/messages",
                headers=headers,
                json=payload,
                timeout=120,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Claude API error {response.status_code}: {response.text[:200]}")
            data = response.json()
            content_blocks = data.get("content", [])
            text = "".join(
                block.get("text", "") for block in content_blocks if block.get("type") == "text"
            )
            return text.strip() if text else None
        except Exception as e:
            print(f"   ⚠️ Claude 视觉调用失败: {e}")
            return None

    def _parse_feedback(self, content):
        if not content:
            return None
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            return json.loads(content)
        except Exception as e:
            print(f"   ⚠️ 视觉反馈解析失败: {e}")
            return None

    def critique(self, video_path, storyboard_section):
        """
        Analyze the video (or frames from it) and return feedback.
        使用 Gemini 3 Pro 进行视觉分析。
        """
        if not self.enabled:
            if USE_VISUAL_FEEDBACK and not GEMINI_API_KEY and not CLAUDE_API_KEY:
                print("   ⚠️ GEMINI_API_KEY / CLAUDE_API_KEY 未设置，跳过视觉分析。")
            return None

        print(f"🧐 Critiquing video: {video_path}")
        
        # 1. 使用 PyAV 提取帧（无需系统安装 ffmpeg CLI）
        import av
        import glob
        import os
        from PIL import Image
        
        frames_dir = os.path.join(os.path.dirname(video_path), "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # 清理旧帧
        for f in glob.glob(os.path.join(frames_dir, "frame_*.png")):
            os.remove(f)
            
        try:
            # 用 PyAV 打开视频，每秒提取 1 帧，缩放到 320px 宽度以减少 token 消耗
            container = av.open(video_path)
            stream = container.streams.video[0]
            fps = float(stream.average_rate)  # 视频帧率
            frame_interval = max(1, int(fps))  # 每秒取 1 帧
            
            frame_idx = 0
            saved_count = 0
            for frame in container.decode(video=0):
                if frame_idx % frame_interval == 0:
                    img = frame.to_image()  # PIL Image
                    # 缩放到 320px 宽度，保持宽高比
                    w, h = img.size
                    new_w = 320
                    new_h = int(h * new_w / w)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    save_path = os.path.join(frames_dir, f"frame_{saved_count:03d}.png")
                    img.save(save_path)
                    saved_count += 1
                frame_idx += 1
            container.close()
            
            # 2. 选取最多 4 帧代表帧（首、中、中、尾），节省 token 和时间
            frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
            
            if len(frame_files) > 4:
                indices = [0, len(frame_files)//3, 2*len(frame_files)//3, len(frame_files)-1]
                selected_frames = [frame_files[i] for i in indices]
            else:
                selected_frames = frame_files

            if not selected_frames:
                print("   ⚠️ 未能提取到任何帧，跳过视觉分析。")
                return None

            # 3. 构建视觉分析的消息格式
            # 注意: CRITIC_PROMPT 在 Gemini 中作为文本消息传入，
            # 在 Claude 中作为 system 消息传入（Claude _call_claude_vision 中处理）
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

            # 4. 调用 Gemini Vision API（失败则回退 Claude）
            content = None
            source = None
            if self.gemini_enabled:
                content = self._call_gemini_vision(messages_content)
                source = "gemini" if content else None
            if not content and self.claude_enabled:
                print("   🔁 Gemini 无法使用，切换到 Claude 视觉模型。")
                content = self._call_claude_vision(messages_content)
                source = "claude" if content else None

            feedback = self._parse_feedback(content)
            if feedback is None and source != "claude" and self.claude_enabled:
                print("   🔁 解析失败，尝试 Claude 视觉模型。")
                content = self._call_claude_vision(messages_content)
                feedback = self._parse_feedback(content)
            if feedback is None:
                return None
            
            if feedback.get("has_issues"):
                print(f"   ⚠️ Issues found: {feedback['issues']}")
                return feedback['suggestion']
            else:
                print("   ✅ Visual check passed.")
                return None
                
        except Exception as e:
            print(f"   Visual critique failed (soft fail): {e}")
            return None
