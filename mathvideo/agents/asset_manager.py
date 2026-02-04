import json
import os
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from mathvideo.llm_client import get_llm
from mathvideo.agents.prompts import ASSET_PROMPT
from mathvideo.config import ICONFINDER_API_KEY, USE_ASSETS

class AssetManager:
    def __init__(self, assets_dir):
        self.assets_dir = assets_dir
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            
    def process(self, storyboard_data):
        """
        Main entry point: Analyze storyboard -> Download Assets -> Update Storyboard
        In a real scenario, this would inject asset paths into the storyboard JSON.
        For now, we just download them and print availability.
        """
        if not USE_ASSETS:
            return storyboard_data
            
        print("🤖 Analyzing assets needed...")
        keywords = self._analyze_needs(storyboard_data)
        
        assets_map = {}
        for kw in keywords:
            path = self._download_asset(kw)
            if path:
                assets_map[kw] = path
                
        # Inject into storyboard (simple injection)
        # We add a new field 'available_assets' to the topic info
        storyboard_data['available_assets'] = assets_map
        return storyboard_data

    def _analyze_needs(self, storyboard):
        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_template(ASSET_PROMPT)
        chain = prompt | llm | JsonOutputParser()
        
        try:
            # We convert storyboard to string to pass to LLM
            sb_str = json.dumps(storyboard, ensure_ascii=False)
            keywords = chain.invoke({"storyboard": sb_str})
            print(f"   Identified assets: {keywords}")
            return keywords
        except Exception as e:
            print(f"   Asset analysis failed: {e}")
            return []

    def _download_asset(self, keyword):
        """
        Download icon from IconFinder (or Mock/Placeholder).
        """
        local_filename = f"{keyword}.svg" # Use SVG for placeholders or downloads
        local_path = os.path.join(self.assets_dir, local_filename)

        if not ICONFINDER_API_KEY:
            print(f"   ⚠️ No API Key. Creating placeholder for '{keyword}'")
            return self._create_placeholder_asset(keyword, local_path)
            
        # Simplified IconFinder logic
        headers = {
            "Authorization": f"Bearer {ICONFINDER_API_KEY}",
            "Accept": "application/json"
        }
        url = "https://api.iconfinder.com/v4/icons/search"
        params = {
            "query": keyword,
            "count": 1,
            "premium": "false",
            "style": "flat" # Prefer flat style
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if data['icons']:
                icon = data['icons'][0]
                # Try to get largest PNG
                raster = icon['raster_sizes'][-1]
                img_url = raster['formats'][0]['preview_url']
                
                # Download
                local_path = os.path.join(self.assets_dir, f"{keyword}.png")
                img_data = requests.get(img_url).content
                with open(local_path, "wb") as f:
                    f.write(img_data)
                print(f"   Downloaded: {local_path}")
                return local_path
        except Exception as e:
            print(f"   Download failed for {keyword}: {e}")
            
        return None

    def _create_placeholder_asset(self, keyword, path):
        """
        Creates a simple SVG placeholder with the keyword text.
        """
        # Simple SVG template
        svg_content = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#E0E0E0" stroke="black" stroke-width="2"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
        font-family="Arial" fill="#333" font-size="24">{keyword}</text>
</svg>'''
        
        try:
            with open(path, "w") as f:
                f.write(svg_content)
            print(f"   Created placeholder: {path}")
            return path
        except Exception as e:
            print(f"   Failed to create placeholder: {e}")
            return None
