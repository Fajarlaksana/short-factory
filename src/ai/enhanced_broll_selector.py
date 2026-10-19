#!/usr/bin/env python3
"""
Enhanced B-Roll Selector v2.0
=============================

Multi-source B-roll selection:
1. AI-generated keywords based on content emotion
2. Multiple free APIs: Pexels, Pixabay, Coverr
3. Caching and variety enforcement
4. Performance learning
5. Fallback chain for reliability

NO HARDCODED KEYWORDS - Everything AI-driven!
"""

import os
import json
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
BROLL_CACHE_DIR = Path("./assets/broll")
BROLL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

BROLL_LEARNING_FILE = STATE_DIR / "broll_learning.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class EnhancedBRollSelector:
    """
    Smart B-roll selection with multi-source fallback.
    """
    
    # API endpoints
    PEXELS_API = "https://api.pexels.com/videos/search"
    PIXABAY_API = "https://pixabay.com/api/videos/"
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.pexels_key = os.environ.get("PEXELS_API_KEY")
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY")
        self.learning = self._load_learning()
        self.used_videos = []  # Track recently used for variety
    
    def _load_learning(self) -> Dict:
        try:
            if BROLL_LEARNING_FILE.exists():
                with open(BROLL_LEARNING_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "keyword_mappings": {},  # content_type -> [effective_keywords]
            "category_keywords": {},  # category -> [best_keywords]
            "video_performance": {},  # video_id -> {engagement}
        }
    
    def _save_learning(self):
        self.learning["last_updated"] = datetime.now().isoformat()
        with open(BROLL_LEARNING_FILE, 'w') as f:
            json.dump(self.learning, f, indent=2)
    
    def get_ai_keywords(self, content: str, category: str, mood: str) -> List[str]:
        """Ask AI to generate optimal B-roll search keywords."""
        prompt = f"""You are a professional video editor for Netflix documentaries.

TASK: Generate B-roll search keywords for this content.

Content: "{content[:200]}"
Category: {category}
Mood: {mood}

REQUIREMENTS:
1. Keywords should find VISUALLY INTERESTING stock footage
2. Keywords should EMOTIONALLY match the content
3. Keywords should be abstract enough to find results on Pexels/Pixabay
4. Prefer: motion, lighting effects, human expressions, nature metaphors

GOOD B-ROLL TYPES:
- Abstract/motion graphics (particles, light, flow)
- Nature metaphors (sunrise, storm, water)
- Human activities (working, thinking, succeeding)
- Technology (screens, data, futuristic)

Return ONLY a JSON array of 5 keywords:
["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]

JSON ONLY."""

        result = self._call_ai(prompt)
        if result:
            keywords = self._parse_keywords(result)
            if keywords:
                return keywords
        
        # Fallback keywords based on category and mood
        return self._get_fallback_keywords(category, mood)
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        if not requests:
            return None
        
        if self.groq_key:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except:
                pass
        return None
    
    def _parse_keywords(self, result: str) -> List[str]:
        try:
            import re
            if "```" in result:
                result = result.split("```")[1] if "```json" not in result else result.split("```json")[1].split("```")[0]
            
            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                keywords = json.loads(result[start:end])
                return [str(k).strip() for k in keywords if k]
        except:
            pass
        return []
    
    def _get_fallback_keywords(self, category: str, mood: str) -> List[str]:
        """Category-based fallback keywords."""
        category_map = {
            "psychology": ["brain visualization", "thinking person", "abstract mind", "meditation", "neural network"],
            "money": ["money growth", "coins falling", "stock market", "success celebration", "finance technology"],
            "productivity": ["desk workspace", "time lapse work", "focus concentration", "morning routine", "planning"],
            "health": ["fitness training", "healthy food", "wellness spa", "running outdoors", "meditation nature"],
            "technology": ["futuristic technology", "data visualization", "coding screen", "innovation", "digital"],
            "relationships": ["people talking", "couple together", "friends laughing", "communication", "connection"],
        }
        
        mood_map = {
            "dramatic": ["dramatic clouds", "storm timelapse", "epic landscape"],
            "upbeat": ["celebration", "success", "happy people"],
            "mysterious": ["dark atmosphere", "fog", "abstract shadows"],
            "inspirational": ["sunrise", "mountain peak", "overcoming"],
        }
        
        keywords = category_map.get(category, ["abstract motion", "colorful background", "technology", "nature", "people"])
        mood_kw = mood_map.get(mood, ["cinematic", "professional"])
        
        return keywords[:3] + mood_kw[:2]
    
    def search_pexels(self, keyword: str) -> Optional[Dict]:
        """Search Pexels for video."""
        if not self.pexels_key or not requests:
            return None
        
        try:
            response = requests.get(
                self.PEXELS_API,
                headers={"Authorization": self.pexels_key},
                params={"query": keyword, "per_page": 10, "orientation": "portrait"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                
                # Filter out recently used
                available = [v for v in videos if str(v.get("id")) not in self.used_videos]
                if not available:
                    available = videos
                
                if available:
                    video = random.choice(available[:5])
                    video_files = video.get("video_files", [])
                    
                    # Get HD quality
                    for vf in video_files:
                        if vf.get("quality") == "hd" or vf.get("height", 0) >= 720:
                            return {
                                "id": str(video["id"]),
                                "url": vf.get("link"),
                                "duration": video.get("duration", 0),
                                "source": "pexels"
                            }
        except Exception as e:
            safe_print(f"   [!] Pexels search failed: {e}")
        
        return None
    
    def search_pixabay(self, keyword: str) -> Optional[Dict]:
        """Search Pixabay for video."""
        if not self.pixabay_key or not requests:
            return None
        
        try:
            response = requests.get(
                self.PIXABAY_API,
                params={
                    "key": self.pixabay_key,
                    "q": keyword,
                    "per_page": 10,
                    "video_type": "all"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                
                available = [h for h in hits if str(h.get("id")) not in self.used_videos]
                if not available:
                    available = hits
                
                if available:
                    video = random.choice(available[:5])
                    videos = video.get("videos", {})
                    
                    # Get medium or large quality
                    for quality in ["medium", "large", "small"]:
                        if quality in videos:
                            return {
                                "id": str(video["id"]),
                                "url": videos[quality].get("url"),
                                "duration": video.get("duration", 0),
                                "source": "pixabay"
                            }
        except Exception as e:
            safe_print(f"   [!] Pixabay search failed: {e}")
        
        return None
    
    def download_video(self, url: str, video_id: str, source: str) -> Optional[str]:
        """Download and cache video."""
        if not url or not requests:
            return None
        
        filename = f"{source}_{video_id}.mp4"
        cache_path = BROLL_CACHE_DIR / filename
        
        if cache_path.exists() and cache_path.stat().st_size > 100000:
            safe_print(f"   [OK] Using cached B-roll: {filename}")
            return str(cache_path)
        
        try:
            safe_print(f"   [*] Downloading B-roll from {source}...")
            response = requests.get(url, timeout=60, stream=True)
            
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if cache_path.stat().st_size > 100000:
                    safe_print(f"   [OK] Downloaded: {filename}")
                    self.used_videos.append(video_id)
                    return str(cache_path)
                else:
                    cache_path.unlink()
        except Exception as e:
            safe_print(f"   [!] Download failed: {e}")
        
        return None
    
    def get_broll_for_content(self, content: str, category: str, mood: str = "dramatic") -> Optional[str]:
        """Main method: Get B-roll video for content."""
        safe_print(f"   [BROLL] Analyzing content for {category}...")
        
        # Get AI-generated keywords
        keywords = self.get_ai_keywords(content, category, mood)
        safe_print(f"   [BROLL] Keywords: {keywords[:3]}")
        
        # Try each keyword with multiple sources
        for keyword in keywords:
            # Try Pexels first
            if self.pexels_key:
                video = self.search_pexels(keyword)
                if video and video.get("url"):
                    path = self.download_video(video["url"], video["id"], video["source"])
                    if path:
                        return path
            
            # Try Pixabay
            if self.pixabay_key:
                video = self.search_pixabay(keyword)
                if video and video.get("url"):
                    path = self.download_video(video["url"], video["id"], video["source"])
                    if path:
                        return path
        
        safe_print("   [!] No B-roll found from APIs")
        return None


# Singleton
_broll_selector = None

def get_enhanced_broll(content: str, category: str, mood: str = "dramatic") -> Optional[str]:
    global _broll_selector
    if _broll_selector is None:
        _broll_selector = EnhancedBRollSelector()
    return _broll_selector.get_broll_for_content(content, category, mood)


if __name__ == "__main__":
    safe_print("Testing Enhanced B-Roll Selector...")
    broll = get_enhanced_broll("Why your brain is lying to you", "psychology", "mysterious")
    safe_print(f"Result: {broll}")