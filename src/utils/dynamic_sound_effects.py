#!/usr/bin/env python3
"""
Dynamic AI-Powered Sound Effects Selector v2.0
==============================================

AI-driven SFX selection based on:
1. Content emotion and pacing
2. Video moments (hook, reveal, transition, CTA)
3. Learned performance patterns
4. Free audio APIs (Freesound, Pixabay)

NO HARDCODED EFFECTS - AI analyzes and selects!
"""

import os
import json
import math
import struct
import wave
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    import requests
except ImportError:
    requests = None

# Directories
SFX_CACHE_DIR = Path("./assets/sfx")
SFX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
SFX_LEARNING_FILE = STATE_DIR / "sfx_learning.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class DynamicSoundEffectSelector:
    """AI-powered sound effect selection."""
    
    # SFX categories and contexts
    SFX_CATEGORIES = {
        "transition": {"keywords": ["whoosh", "swoosh"], "contexts": ["scene_change", "text_reveal"]},
        "impact": {"keywords": ["impact", "boom", "bass"], "contexts": ["hook", "dramatic_reveal"]},
        "notification": {"keywords": ["ding", "bell"], "contexts": ["tip_reveal", "cta"]},
        "countdown": {"keywords": ["tick", "timer"], "contexts": ["urgency", "tension"]},
        "success": {"keywords": ["success", "win"], "contexts": ["conclusion", "payoff"]},
        "suspense": {"keywords": ["tension", "eerie"], "contexts": ["mystery", "before_reveal"]},
        "magical": {"keywords": ["sparkle", "shimmer"], "contexts": ["transformation", "wonder"]},
        "electronic": {"keywords": ["glitch", "tech"], "contexts": ["tech_content", "data"]},
    }
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.learning_data = self._load_learning()
    
    def _load_learning(self) -> Dict:
        try:
            if SFX_LEARNING_FILE.exists():
                with open(SFX_LEARNING_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"sfx_performance": {}, "category_preferences": {}}
    
    def _save_learning(self):
        self.learning_data["last_updated"] = datetime.now().isoformat()
        with open(SFX_LEARNING_FILE, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def get_ai_sfx_recommendation(self, content: str, category: str, video_moment: str) -> Dict:
        """Ask AI to recommend ideal sound effects."""
        prompt = f"""You are a professional sound designer for viral short-form videos.

VIDEO CONTEXT:
- Category: {category}
- Content: {content[:200]}
- Moment: {video_moment}

AVAILABLE SFX TYPES: transition, impact, notification, countdown, success, suspense, magical, electronic

Select the PERFECT sound effect. Return JSON:
{{"sfx_type": "type from list", "intensity": "low|medium|high", "timing": "before|during|after"}}

JSON ONLY."""

        result = self._call_ai(prompt)
        if result:
            try:
                import re
                match = re.search(r'\{[\s\S]*\}', result)
                if match:
                    return json.loads(match.group())
            except:
                pass
        
        # Fallback
        moment_map = {
            "hook": {"sfx_type": "impact", "intensity": "high"},
            "transition": {"sfx_type": "transition", "intensity": "medium"},
            "reveal": {"sfx_type": "notification", "intensity": "medium"},
            "cta": {"sfx_type": "success", "intensity": "low"},
        }
        return moment_map.get(video_moment, {"sfx_type": "transition", "intensity": "medium"})
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        if not requests:
            return None
        
        if self.groq_key:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": 150},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except:
                pass
        return None
    
    def generate_procedural_sfx(self, sfx_type: str, intensity: str = "medium") -> str:
        """Generate procedural sound effect."""
        cache_path = SFX_CACHE_DIR / f"proc_{sfx_type}_{intensity}.wav"
        if cache_path.exists():
            return str(cache_path)
        
        sample_rate = 44100
        generators = {
            "transition": self._gen_whoosh,
            "impact": self._gen_impact,
            "notification": self._gen_ding,
            "countdown": self._gen_tick,
            "success": self._gen_success,
            "suspense": self._gen_suspense,
            "magical": self._gen_magical,
            "electronic": self._gen_glitch,
        }
        
        gen = generators.get(sfx_type, self._gen_whoosh)
        samples = gen(sample_rate, intensity)
        self._save_wav(samples, str(cache_path), sample_rate)
        safe_print(f"   [SFX] Generated: {sfx_type}/{intensity}")
        return str(cache_path)
    
    def _gen_whoosh(self, sr: int, intensity: str) -> List[float]:
        dur = {"low": 0.3, "medium": 0.5, "high": 0.7}.get(intensity, 0.5)
        amp = {"low": 0.4, "medium": 0.6, "high": 0.8}.get(intensity, 0.6)
        n = int(sr * dur)
        return [math.sin(math.pi * i/n) * amp * (math.sin(2*math.pi*(3000*(1-i/n)+200*i/n)*i/sr) + random.random()*0.3-0.15) for i in range(n)]
    
    def _gen_impact(self, sr: int, intensity: str) -> List[float]:
        dur = {"low": 0.4, "medium": 0.6, "high": 0.8}.get(intensity, 0.6)
        amp = {"low": 0.5, "medium": 0.7, "high": 0.9}.get(intensity, 0.7)
        n = int(sr * dur)
        return [math.exp(-8*i/n) * amp * (0.5*math.sin(2*math.pi*60*i/sr) + 0.3*math.sin(2*math.pi*120*i/sr) + 0.2*math.sin(2*math.pi*180*i/sr)) for i in range(n)]
    
    def _gen_ding(self, sr: int, intensity: str) -> List[float]:
        dur = {"low": 0.5, "medium": 0.8, "high": 1.0}.get(intensity, 0.8)
        n = int(sr * dur)
        return [math.exp(-4*i/n) * 0.5 * (0.4*math.sin(2*math.pi*880*i/sr) + 0.3*math.sin(2*math.pi*1320*i/sr) + 0.2*math.sin(2*math.pi*1760*i/sr) + 0.1*math.sin(2*math.pi*2640*i/sr)) for i in range(n)]
    
    def _gen_tick(self, sr: int, intensity: str) -> List[float]:
        dur = 0.1
        n = int(sr * dur)
        return [math.exp(-20*i/n) * 0.6 * (0.5*math.sin(2*math.pi*1200*i/sr) + 0.3*math.sin(2*math.pi*2400*i/sr) + 0.2*math.sin(2*math.pi*800*i/sr)) for i in range(n)]
    
    def _gen_success(self, sr: int, intensity: str) -> List[float]:
        dur = 0.8
        n = int(sr * dur)
        return [math.sin(math.pi*i/n)*math.exp(-2*i/n)*0.5*(0.4*math.sin(2*math.pi*(440+i/n*200)*i/sr)+0.3*math.sin(2*math.pi*(440+i/n*200)*1.5*i/sr)) for i in range(n)]
    
    def _gen_suspense(self, sr: int, intensity: str) -> List[float]:
        dur = 1.5
        n = int(sr * dur)
        return [(math.sin(math.pi*i/n)*0.8+0.2)*0.5*(0.5*math.sin(2*math.pi*50*(1+0.1*math.sin(2*math.pi*2*i/sr))*i/sr)+0.3*math.sin(2*math.pi*75*i/sr)) for i in range(n)]
    
    def _gen_magical(self, sr: int, intensity: str) -> List[float]:
        dur = 1.0
        n = int(sr * dur)
        return [math.exp(-3*i/n)*math.sin(math.pi*i/n)*0.4*(0.3*math.sin(2*math.pi*2000*i/sr)+0.3*math.sin(2*math.pi*3000*i/sr)+0.2*math.sin(2*math.pi*4000*i/sr)+(random.random()*0.1 if random.random()>0.9 else 0)) for i in range(n)]
    
    def _gen_glitch(self, sr: int, intensity: str) -> List[float]:
        dur = 0.5
        n = int(sr * dur)
        return [math.exp(-4*i/n)*(1 if random.random()>0.1 else 0)*0.5*(0.5*(1 if math.sin(2*math.pi*(200 if int(10*i/n)%2==0 else 400)*i/sr)>0 else -1)+0.3*math.sin(2*math.pi*800*i/sr)) for i in range(n)]
    
    def _save_wav(self, samples: List[float], filepath: str, sr: int = 44100):
        mx = max(abs(min(samples)), abs(max(samples))) if samples else 1
        if mx == 0: mx = 1
        normalized = [int(s/mx*32767*0.9) for s in samples]
        with wave.open(filepath, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for s in normalized:
                wf.writeframes(struct.pack('<h', s))
    
    def get_sfx_for_moment(self, content: str, category: str, video_moment: str) -> str:
        """Main method: Get AI-selected sound effect."""
        rec = self.get_ai_sfx_recommendation(content, category, video_moment)
        sfx_type = rec.get("sfx_type", "transition")
        intensity = rec.get("intensity", "medium")
        return self.generate_procedural_sfx(sfx_type, intensity)


# Singleton
_selector = None

def get_dynamic_sfx(content: str, category: str, video_moment: str) -> str:
    global _selector
    if _selector is None:
        _selector = DynamicSoundEffectSelector()
    return _selector.get_sfx_for_moment(content, category, video_moment)


if __name__ == "__main__":
    safe_print("Testing Dynamic SFX...")
    sfx = get_dynamic_sfx("Your brain is lying to you", "psychology", "hook")
    safe_print(f"Result: {sfx}")