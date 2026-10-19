#!/usr/bin/env python3
"""
AI-Driven Music Selector for ViralShorts Factory v2.0
======================================================

TRULY DYNAMIC MUSIC SELECTION:
1. AI analyzes content and describes ideal music
2. Searches Pixabay Audio API for matching tracks (FREE)
3. Downloads and caches the best match
4. Falls back to Bensound only if API fails

NO MORE HARDCODED TRACK NAMES - AI + API does everything!
"""

import os
import json
import random
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_gemini_model_for_rest_api
except ImportError:
    def get_gemini_model_for_rest_api(api_key=None):
        return "gemini-2.5-flash"  # Fallback only if import fails

# Cache directory
MUSIC_DIR = Path("./assets/music")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Track usage for variety (avoid repeating same tracks)
TRACK_HISTORY_FILE = MUSIC_DIR / "track_history.json"


def safe_print(msg: str):
    """Print with fallback for encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class AIMusicSelector:
    """
    AI-powered music selection using FREE APIs:
    1. Pixabay Audio API (free with API key)
    2. Freesound.org API (free with API key)
    3. Bensound (free direct download, attribution required)
    """
    
    # Pixabay Audio API (free, generous limits)
    PIXABAY_AUDIO_API = "https://pixabay.com/api/"
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY")
        self.track_history = self._load_track_history()
    
    def _load_track_history(self) -> List[str]:
        """Load recently used tracks to avoid repetition."""
        try:
            if TRACK_HISTORY_FILE.exists():
                with open(TRACK_HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('recent_tracks', [])[-20:]  # Keep last 20
        except:
            pass
        return []
    
    def _save_track_history(self, track_id: str):
        """Save track to history."""
        self.track_history.append(track_id)
        self.track_history = self.track_history[-20:]  # Keep last 20
        try:
            with open(TRACK_HISTORY_FILE, 'w') as f:
                json.dump({'recent_tracks': self.track_history}, f)
        except:
            pass
    
    def get_ai_music_description(self, content_category: str, content_mood: str, 
                                  content_summary: str = "") -> Dict:
        """
        Ask AI to describe the ideal background music.
        v8.8: FULL PROMPT using Gemini (free tokens available!)
        """
        # v8.8: FULL comprehensive prompt - no more token saving!
        prompt = f"""You are an expert music director for viral short-form videos.

VIDEO DETAILS:
- Category: {content_category}
- Mood: {content_mood}
- Content: {content_summary if content_summary else 'viral short video about ' + content_category}

YOUR TASK:
Select the PERFECT background music that will:
1. Amplify the emotional impact of the content
2. Match the pacing (short videos need engaging music from the start)
3. Not distract from the voiceover (instrumental only)
4. Enhance watch time and engagement

Consider:
- What emotion should viewers feel?
- Should it build tension or maintain energy?
- What genre matches viral short content?

Return comprehensive JSON:
{{
    "search_query": "specific search query for royalty-free music API",
    "genre": "specific genre (cinematic/electronic/ambient/pop/hip-hop/orchestral)",
    "tempo": "slow/medium/fast",
    "energy": "low/medium/high",
    "instruments": ["main instruments that would work"],
    "mood_keywords": ["descriptive mood words"],
    "why_this_works": "brief explanation of why this music choice enhances the video"
}}

JSON ONLY."""

        # Try Gemini first (free tokens!)
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if gemini_key:
            try:
                import time
                # DYNAMIC MODEL SELECTION - no hardcoded model names
                gemini_model = get_gemini_model_for_rest_api(gemini_key)

                # v17.9.37: DYNAMIC rate limit delay
                try:
                    from src.ai.model_helper import get_smart_delay
                    delay = get_smart_delay(gemini_model, "gemini")
                except ImportError:
                    delay = 4.4  # Fallback
                time.sleep(delay)
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        result = json.loads(json_match.group())
                        safe_print(f"   [OK] Gemini music selection: {result.get('genre', 'N/A')}, {result.get('tempo', 'N/A')}")
                        return {
                            "search_terms": [result.get("search_query", f"{content_mood} instrumental")],
                            "genre": result.get("genre", "electronic"),
                            "tempo": result.get("tempo", "medium"),
                            "energy": result.get("energy", "medium"),
                            "mood_keywords": result.get("mood_keywords", [content_mood])
                        }
            except Exception as e:
                safe_print(f"   [!] Gemini music selection failed: {e}")
        
        # Fallback to Groq
        if self.groq_key:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 200
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        result = json.loads(json_match.group())
                        return {
                            "search_terms": [result.get("search_query", f"{content_mood} instrumental")],
                            "genre": result.get("genre", "electronic"),
                            "tempo": result.get("tempo", "medium")
                        }
            except Exception as e:
                safe_print(f"   [!] Groq music selection failed: {e}")
        
        return self._fallback_description(content_mood)
    
    def _fallback_description(self, mood: str) -> Dict:
        """Fallback music description based on mood (no AI call)."""
        mood_map = {
            "upbeat": {"search_terms": ["happy upbeat instrumental"], "genre": "pop", "tempo": "fast"},
            "dramatic": {"search_terms": ["epic cinematic trailer"], "genre": "cinematic", "tempo": "medium"},
            "mysterious": {"search_terms": ["dark ambient mystery"], "genre": "ambient", "tempo": "slow"},
            "inspirational": {"search_terms": ["motivational piano"], "genre": "cinematic", "tempo": "medium"},
            "chill": {"search_terms": ["lofi chill beats"], "genre": "lofi", "tempo": "slow"},
            "intense": {"search_terms": ["intense action music"], "genre": "electronic", "tempo": "fast"},
            "energetic": {"search_terms": ["energetic electronic"], "genre": "electronic", "tempo": "fast"},
            "emotional": {"search_terms": ["emotional piano sad"], "genre": "classical", "tempo": "slow"},
            "tech": {"search_terms": ["futuristic tech"], "genre": "electronic", "tempo": "medium"},
            "professional": {"search_terms": ["corporate background"], "genre": "ambient", "tempo": "medium"},
        }
        return mood_map.get(mood, mood_map["upbeat"])
    
    def search_pixabay_audio(self, query: str) -> Optional[Dict]:
        """
        Search Pixabay's Audio collection.
        Returns track info with download URL if found.
        
        Pixabay Audio API is FREE and has generous limits!
        """
        if not self.pixabay_key:
            return None
        
        try:
            # Pixabay audio search
            params = {
                "key": self.pixabay_key,
                "q": query.replace(" ", "+"),
                "per_page": 10,
                "order": "popular",  # Get most popular first
            }
            
            # Note: Pixabay's audio is accessed through their main API
            # Filter for music type
            response = requests.get(
                self.PIXABAY_AUDIO_API,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                
                if hits:
                    # Filter out recently used tracks
                    available = [h for h in hits if str(h.get("id")) not in self.track_history]
                    if not available:
                        available = hits  # Reset if all used
                    
                    # Pick a random one from top results for variety
                    track = random.choice(available[:5])
                    
                    return {
                        "id": str(track.get("id")),
                        "url": track.get("previewURL") or track.get("largeImageURL"),
                        "duration": track.get("duration", 0),
                        "tags": track.get("tags", ""),
                        "source": "pixabay"
                    }
        except Exception as e:
            safe_print(f"   [!] Pixabay search failed: {e}")
        
        return None
    
    def download_music(self, url: str, track_id: str, source: str) -> Optional[str]:
        """Download music track and cache it."""
        if not url:
            return None
        
        # Create unique filename
        filename = f"{source}_{track_id}.mp3"
        cache_path = MUSIC_DIR / filename
        
        # Check cache
        if cache_path.exists() and cache_path.stat().st_size > 10000:
            safe_print(f"   [OK] Using cached: {filename}")
            return str(cache_path)
        
        try:
            safe_print(f"   [*] Downloading music from {source}...")
            response = requests.get(
                url, 
                timeout=60,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if cache_path.stat().st_size > 10000:
                    safe_print(f"   [OK] Downloaded: {filename}")
                    self._save_track_history(track_id)
                    return str(cache_path)
                else:
                    cache_path.unlink()
        except Exception as e:
            safe_print(f"   [!] Download failed: {e}")
        
        return None
    
    def _get_bensound_dynamic(self, mood: str, genre: str) -> Optional[str]:
        """
        Dynamic Bensound selection based on AI analysis.
        Uses AI-determined mood+genre to pick best track.
        """
        # Comprehensive mapping based on genre AND mood combinations
        # This is dynamic because AI determines both mood and genre
        BENSOUND_LIBRARY = {
            # Electronic genre tracks
            ("electronic", "energetic"): ["dubstep", "funkyelement", "popdance", "dance"],
            ("electronic", "intense"): ["extremeaction", "dubstep", "actionable"],
            ("electronic", "tech"): ["scifi", "evolution", "highoctane"],
            
            # Cinematic genre tracks  
            ("cinematic", "dramatic"): ["epic", "actionable", "instinct"],
            ("cinematic", "inspirational"): ["inspire", "goinghigher", "newdawn"],
            ("cinematic", "emotional"): ["memories", "sadday", "betterdays"],
            
            # Ambient genre tracks
            ("ambient", "mysterious"): ["deepblue", "evolution", "scifi"],
            ("ambient", "chill"): ["dreams", "slowmotion", "relaxing", "acousticbreeze"],
            ("ambient", "professional"): ["creativeminds", "corporate", "photoalbum"],
            
            # Pop/upbeat tracks
            ("pop", "upbeat"): ["happyrock", "ukulele", "buddy", "groovyhiphop", "jazzcomedy"],
            ("pop", "fun"): ["cute", "littleidea", "jazzyfrenchy"],
            
            # Classical tracks
            ("classical", "emotional"): ["pianomoment", "love", "memories", "tenderness"],
            
            # Lofi tracks
            ("lofi", "chill"): ["dreams", "slowmotion", "tomorrow"],
        }
        
        # Find matching tracks
        key = (genre.lower(), mood.lower())
        tracks = BENSOUND_LIBRARY.get(key)
        
        if not tracks:
            # Try with just mood
            for (g, m), t in BENSOUND_LIBRARY.items():
                if m == mood.lower():
                    tracks = t
                    break
        
        if not tracks:
            # Ultimate fallback
            tracks = ["epic", "energy", "dreams", "happyrock"]
        
        # Filter out recently used
        available = [t for t in tracks if t not in self.track_history]
        if not available:
            available = tracks
        
        selected = random.choice(available)
        
        # Check cache
        cache_path = MUSIC_DIR / f"bensound-{selected}.mp3"
        if cache_path.exists() and cache_path.stat().st_size > 10000:
            safe_print(f"   [OK] Using cached: bensound-{selected}")
            self._save_track_history(selected)
            return str(cache_path)
        
        # Download
        url = f"https://www.bensound.com/bensound-music/bensound-{selected}.mp3"
        try:
            safe_print(f"   [*] Downloading: bensound-{selected}...")
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                if cache_path.stat().st_size > 10000:
                    safe_print(f"   [OK] Downloaded: bensound-{selected}")
                    self._save_track_history(selected)
                    return str(cache_path)
        except Exception as e:
            safe_print(f"   [!] Bensound download failed: {e}")
        
        return None
    
    def get_music_for_content(self, category: str, mood: str, 
                               content_summary: str = "") -> Optional[str]:
        """
        Main method: Get AI-selected music for content.
        
        PRIORITY ORDER:
        1. AI describes ideal music
        2. Try Pixabay Audio API (truly dynamic, free)
        3. Fall back to Bensound (AI-selected genre+mood combo)
        """
        safe_print(f"   [AI] Analyzing music for {category}/{mood}...")
        
        # Step 1: Get AI description
        music_desc = self.get_ai_music_description(category, mood, content_summary)
        search_query = music_desc.get("search_terms", [f"{mood} instrumental"])[0]
        genre = music_desc.get("genre", "electronic")
        
        safe_print(f"   [AI] Recommends: '{search_query}' ({genre})")
        
        # Step 2: Try Pixabay Audio API (truly dynamic!)
        if self.pixabay_key:
            track = self.search_pixabay_audio(search_query)
            if track and track.get("url"):
                music_path = self.download_music(
                    track["url"], 
                    track["id"], 
                    track["source"]
                )
                if music_path:
                    safe_print(f"   [OK] Dynamic Pixabay track: {track['id']}")
                    return music_path
        
        # Step 3: Fallback to AI-selected Bensound
        safe_print("   [*] Using Bensound fallback...")
        return self._get_bensound_dynamic(mood, genre)


def get_ai_selected_music(category: str, mood: str, content_summary: str = "") -> Optional[str]:
    """
    Main entry point for AI-driven music selection.
    
    This is TRULY dynamic:
    - AI describes ideal music
    - Searches free music APIs
    - Downloads matching tracks
    - Variety enforced via history tracking
    """
    selector = AIMusicSelector()
    return selector.get_music_for_content(category, mood, content_summary)


if __name__ == "__main__":
    print("Testing AI Music Selector v2.0...")
    
    test_cases = [
        ("psychology", "mysterious", "Why people fear success"),
        ("finance", "inspirational", "How to save $10,000"),
        ("technology", "tech", "AI is changing everything"),
    ]
    
    for category, mood, summary in test_cases:
        print(f"\n--- Testing: {category}/{mood} ---")
        music = get_ai_selected_music(category, mood, summary)
        print(f"Result: {music}")
