import json
import base64
from openai import OpenAI
from src.agents.prompts import CRITIC_PROMPT
from src.config import USE_VISUAL_FEEDBACK, HF_API_KEY, HF_BASE_URL, HF_VISION_MODEL_NAME

class VisualCritic:
    def __init__(self):
        pass

    def _get_vision_client(self):
        """
        Creates a raw OpenAI client for Hugging Face Vision API.
        """
        return OpenAI(
            base_url=HF_BASE_URL,
            api_key=HF_API_KEY
        )

    def critique(self, video_path, storyboard_section):
        """
        Analyze the video (or frames from it) and return feedback.
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
            # Extract frames: 1 frame every 2 seconds to avoid too many images, but ensure we cover the timeline
            # -vf fps=0.5 means 1 frame every 2 seconds. 
            # For short videos (e.g. 5s), this gives ~3 frames. For 10s -> 5 frames.
            image_pattern = os.path.join(frames_dir, "frame_%03d.png")
            subprocess.run([
                "ffmpeg", "-i", video_path, 
                "-vf", "fps=1.0", 
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

            image_contents = []
            for img_path in selected_frames:
                with open(img_path, "rb") as image_file:
                    b64_data = base64.b64encode(image_file.read()).decode('utf-8')
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_data}"
                        }
                    })

            # 3. Call Vision LLM using Raw Client
            client = self._get_vision_client()
            
            messages_payload = [
                {"type": "text", "text": CRITIC_PROMPT},
                *image_contents
            ]

            response = client.chat.completions.create(
                model=HF_VISION_MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": messages_payload
                    }
                ],
                max_tokens=1024,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
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
