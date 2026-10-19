#!/usr/bin/env python3
"""
ViralShorts Factory - AI Thumbnail Text Optimizer v17.8
========================================================

Generates optimal text overlays for YouTube Short thumbnails.

Key factors for high-CTR thumbnails:
- Power words that trigger emotions
- Maximum 3-4 words visible
- High contrast/readability
- Curiosity gap
"""

import os
try:
    from model_helper import get_dynamic_gemini_model
except ImportError:
    try:
        from src.ai.model_helper import get_dynamic_gemini_model
    except ImportError:
        def get_dynamic_gemini_model(): return "gemini-2.5-flash"
import json
import re
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

THUMBNAIL_FILE = STATE_DIR / "thumbnail_performance.json"


class AIThumbnailTextOptimizer:
    """
    Generates optimal text for video thumbnails.
    """
    
    # Power words that increase CTR
    POWER_WORDS = [
        "SECRET", "TRUTH", "HIDDEN", "SHOCKING", "NEVER", "ALWAYS",
        "FREE", "NOW", "STOP", "WAIT", "WHY", "HOW", "EXPOSED",
        "LIES", "HACK", "TRICK", "EASY", "FAST", "NEW"
    ]
    
    # Emotion triggers
    EMOTION_WORDS = {
        "curiosity": ["secret", "hidden", "truth", "why", "how"],
        "urgency": ["now", "stop", "wait", "today", "before"],
        "fear": ["never", "danger", "warning", "avoid", "risk"],
        "excitement": ["amazing", "incredible", "wow", "mind-blowing"],
        "trust": ["proven", "real", "works", "guaranteed", "tested"]
    }
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if THUMBNAIL_FILE.exists():
                with open(THUMBNAIL_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "best_words": [],
            "performance": {},
            "learned_patterns": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(THUMBNAIL_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_thumbnail_text(self, title: str, topic: str, 
                               category: str) -> Dict:
        """
        Generate optimal thumbnail text.
        
        Args:
            title: Video title
            topic: Video topic
            category: Content category
        
        Returns:
            Dict with main_text, emphasis_word, color_suggestion
        """
        # Try AI generation
        ai_result = self._generate_with_ai(title, topic, category)
        
        if ai_result:
            safe_print("   [THUMB] AI-generated thumbnail text")
            return ai_result
        
        # Fallback to rule-based
        return self._fallback_generation(title, topic)
    
    def _generate_with_ai(self, title: str, topic: str, 
                         category: str) -> Optional[Dict]:
        """Generate with AI."""
        prompt = f"""You are a YouTube thumbnail text expert.

TASK: Create high-CTR thumbnail text for this video.

Video Details:
- Title: {title}
- Topic: {topic}
- Category: {category}

THUMBNAIL TEXT RULES:
1. Main text: MAX 3-4 words
2. Include ONE power word (SECRET, TRUTH, HIDDEN, etc.)
3. Create curiosity gap (make viewer NEED to click)
4. All CAPS for impact
5. Must be readable on small mobile screen

Return JSON:
{{
  "main_text": "THE HIDDEN TRUTH",
  "emphasis_word": "HIDDEN",
  "color_mood": "dramatic",
  "emotion_trigger": "curiosity"
}}

JSON ONLY."""

        result = self._call_ai(prompt)
        
        if result:
            return self._parse_response(result)
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                safe_print(f"   [!] Gemini error: {e}")
        
        if self.groq_key:
            try:
                from groq import Groq
                try:
                    from quota_optimizer import get_best_groq_model
                    model = get_best_groq_model(self.groq_key)
                except ImportError:
                    try:
                        from src.ai.model_helper import get_dynamic_groq_model
                        model = get_dynamic_groq_model()
                    except:
                        model = "llama-3.3-70b-versatile"  # Emergency only
                
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse JSON response."""
        try:
            # Extract JSON
            match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None
    
    def _fallback_generation(self, title: str, topic: str) -> Dict:
        """Generate with rules."""
        # Extract key words from title
        words = title.upper().split()
        
        # Pick a power word
        power_word = random.choice(self.POWER_WORDS)
        
        # Get key concept (2-3 words)
        key_words = [w for w in words if len(w) > 3][:2]
        
        if key_words:
            main_text = f"{power_word} {' '.join(key_words)}"
        else:
            main_text = f"THE {power_word}"
        
        # Determine emotion
        topic_lower = topic.lower()
        emotion = "curiosity"
        for emo, triggers in self.EMOTION_WORDS.items():
            if any(t in topic_lower for t in triggers):
                emotion = emo
                break
        
        return {
            "main_text": main_text[:25],  # Limit length
            "emphasis_word": power_word,
            "color_mood": "dramatic",
            "emotion_trigger": emotion
        }
    
    def get_best_power_words(self, category: str = None, count: int = 5) -> List[str]:
        """Get best performing power words."""
        if not self.data["performance"]:
            return self.POWER_WORDS[:count]
        
        sorted_words = sorted(
            self.data["performance"].items(),
            key=lambda x: x[1].get("avg_ctr", 0),
            reverse=True
        )
        
        return [word for word, _ in sorted_words[:count]]
    
    def record_performance(self, text: str, emphasis_word: str, 
                          ctr: float, views: int):
        """Record thumbnail performance for learning."""
        word = emphasis_word.upper()
        
        if word not in self.data["performance"]:
            self.data["performance"][word] = {
                "uses": 0,
                "total_ctr": 0,
                "total_views": 0,
                "avg_ctr": 0
            }
        
        self.data["performance"][word]["uses"] += 1
        self.data["performance"][word]["total_ctr"] += ctr
        self.data["performance"][word]["total_views"] += views
        
        uses = self.data["performance"][word]["uses"]
        total = self.data["performance"][word]["total_ctr"]
        self.data["performance"][word]["avg_ctr"] = total / uses
        
        # Track as best if high CTR
        if ctr > 0.05 and word not in self.data["best_words"]:
            self.data["best_words"].append(word)
        
        self._save()
    
    def get_color_for_mood(self, mood: str) -> Tuple[str, str]:
        """Get text and background colors for a mood."""
        colors = {
            "dramatic": ("#FFFFFF", "#FF0000"),  # White on red
            "mystery": ("#FFFFFF", "#000000"),   # White on black
            "energy": ("#000000", "#FFFF00"),    # Black on yellow
            "trust": ("#FFFFFF", "#0066FF"),     # White on blue
            "nature": ("#FFFFFF", "#00AA00"),    # White on green
            "luxury": ("#FFD700", "#000000"),    # Gold on black
        }
        
        return colors.get(mood, colors["dramatic"])


# Singleton
_thumbnail_optimizer = None


def get_thumbnail_optimizer() -> AIThumbnailTextOptimizer:
    """Get singleton optimizer."""
    global _thumbnail_optimizer
    if _thumbnail_optimizer is None:
        _thumbnail_optimizer = AIThumbnailTextOptimizer()
    return _thumbnail_optimizer


def generate_thumbnail_text(title: str, topic: str, category: str) -> Dict:
    """Convenience function."""
    return get_thumbnail_optimizer().generate_thumbnail_text(title, topic, category)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Thumbnail Text Optimizer...")
    
    opt = get_thumbnail_optimizer()
    
    # Test generation
    result = opt.generate_thumbnail_text(
        title="5 Morning Habits That Changed My Life",
        topic="morning routines for success",
        category="productivity"
    )
    
    safe_print(f"\nGenerated Thumbnail Text:")
    safe_print("-" * 40)
    safe_print(f"Main Text: {result['main_text']}")
    safe_print(f"Emphasis: {result['emphasis_word']}")
    safe_print(f"Color Mood: {result['color_mood']}")
    safe_print(f"Emotion: {result['emotion_trigger']}")
    
    text_color, bg_color = opt.get_color_for_mood(result['color_mood'])
    safe_print(f"Colors: Text={text_color}, BG={bg_color}")
    safe_print("-" * 40)
    
    # Test best words
    best = opt.get_best_power_words(count=5)
    safe_print(f"\nTop Power Words: {', '.join(best)}")
    
    safe_print("\nTest complete!")


