#!/usr/bin/env python3
"""
ViralShorts Factory - AI Music Mood Selector v17.8
====================================================

Selects music mood based on content using AI.

Music mood is crucial for:
- Setting emotional tone
- Maintaining engagement
- Creating professional feel

This replaces hardcoded mood mappings with AI intelligence.
"""

import os
from src.ai.model_helper import get_dynamic_gemini_model
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

MUSIC_MOOD_FILE = STATE_DIR / "music_mood_performance.json"


class AIMusicMoodSelector:
    """
    Selects music mood using AI based on content.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if MUSIC_MOOD_FILE.exists():
                with open(MUSIC_MOOD_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "mood_performance": {},  # mood -> {uses, avg_retention}
            "category_moods": {},     # category -> [best moods]
            "content_patterns": {},   # content_type -> mood
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(MUSIC_MOOD_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def select_mood(self, topic: str, category: str, 
                   content_type: str = "educational") -> Tuple[str, str]:
        """
        Select music mood and genre for content.
        
        Args:
            topic: Video topic
            category: Content category
            content_type: Type of content (educational, story, shocking, etc.)
        
        Returns:
            Tuple of (mood, genre)
        """
        # First try: Get learned best mood for category
        learned = self._get_learned_mood(category)
        if learned:
            safe_print(f"   [MUSIC] Using learned mood: {learned}")
            return learned
        
        # Second try: Select with AI
        ai_result = self._select_with_ai(topic, category, content_type)
        if ai_result:
            safe_print(f"   [MUSIC] AI-selected mood: {ai_result[0]}")
            return ai_result
        
        # Fallback
        return self._fallback_mood(category)
    
    def _get_learned_mood(self, category: str) -> Optional[Tuple[str, str]]:
        """Get best mood from performance data."""
        cat_moods = self.data.get("category_moods", {}).get(category)
        
        if cat_moods and len(cat_moods) > 0:
            best = cat_moods[0]
            if isinstance(best, dict):
                return (best.get("mood", "dramatic"), best.get("genre", "cinematic"))
            return (best, "cinematic")
        
        return None
    
    def _select_with_ai(self, topic: str, category: str,
                       content_type: str) -> Optional[Tuple[str, str]]:
        """Select mood with AI."""
        prompt = f"""You are a video music director choosing background music.

TASK: Select the PERFECT music mood and genre for this video.

Content:
- Topic: {topic}
- Category: {category}
- Type: {content_type}

MOOD OPTIONS:
- dramatic: Big, impactful, reveals
- mysterious: Builds curiosity, suspense
- uplifting: Positive, motivational, hopeful
- intense: Fast-paced, urgent, exciting
- calm: Peaceful, educational, trustworthy
- energetic: Upbeat, fun, engaging
- emotional: Touching, deep, moving
- dark: Warning, danger, serious

GENRE OPTIONS:
- cinematic: Epic orchestral, trailer-style
- electronic: Modern synths, tech feel
- acoustic: Organic, friendly, warm
- ambient: Subtle, background, atmospheric
- pop: Catchy, youthful, fun

Consider:
1. What EMOTION should viewers feel?
2. What matches the content PACING?
3. What will keep viewers ENGAGED?

Return ONLY JSON:
{{"mood": "mood_name", "genre": "genre_name", "reason": "brief reason"}}

JSON ONLY."""

        result = self._call_ai(prompt)
        
        if result:
            parsed = self._parse_result(result)
            if parsed:
                return (parsed.get("mood", "dramatic"), parsed.get("genre", "cinematic"))
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        # Try Groq (faster for simple tasks)
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
                    max_tokens=100,
                    temperature=0.5
                )
                return response.choices[0].message.content
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        # Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                safe_print(f"   [!] Gemini error: {e}")
        
        return None
    
    def _parse_result(self, result: str) -> Optional[Dict]:
        """Parse AI response."""
        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception as e:
            safe_print(f"   [!] Parse error: {e}")
        
        return None
    
    def _fallback_mood(self, category: str) -> Tuple[str, str]:
        """Fallback mood selection."""
        fallbacks = {
            "psychology": ("mysterious", "ambient"),
            "money": ("uplifting", "electronic"),
            "productivity": ("energetic", "electronic"),
            "health": ("calm", "acoustic"),
            "motivation": ("dramatic", "cinematic"),
            "relationships": ("emotional", "acoustic"),
            "shocking_facts": ("intense", "cinematic"),
        }
        
        return fallbacks.get(category, ("dramatic", "cinematic"))
    
    def record_performance(self, mood: str, category: str, 
                          retention_pct: float, views: int):
        """Record mood performance for learning."""
        # Update mood performance
        if mood not in self.data["mood_performance"]:
            self.data["mood_performance"][mood] = {"uses": 0, "total_retention": 0}
        
        self.data["mood_performance"][mood]["uses"] += 1
        self.data["mood_performance"][mood]["total_retention"] += retention_pct
        
        # Update category moods if good performance
        if retention_pct > 60:  # Above 60% retention is good
            if category not in self.data["category_moods"]:
                self.data["category_moods"][category] = []
            
            # Add or update mood for this category
            found = False
            for i, m in enumerate(self.data["category_moods"][category]):
                if isinstance(m, dict) and m.get("mood") == mood:
                    m["score"] = m.get("score", 0) + 1
                    found = True
                    break
            
            if not found:
                self.data["category_moods"][category].append({
                    "mood": mood,
                    "score": 1
                })
            
            # Sort by score
            self.data["category_moods"][category].sort(
                key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
                reverse=True
            )
        
        self._save()
    
    def get_best_moods(self) -> Dict:
        """Get best performing moods."""
        return {
            mood: {
                "uses": stats["uses"],
                "avg_retention": stats["total_retention"] / stats["uses"] if stats["uses"] > 0 else 0
            }
            for mood, stats in self.data.get("mood_performance", {}).items()
        }


# Singleton
_music_selector = None


def get_music_mood_selector() -> AIMusicMoodSelector:
    """Get singleton music mood selector."""
    global _music_selector
    if _music_selector is None:
        _music_selector = AIMusicMoodSelector()
    return _music_selector


def select_music_mood(topic: str, category: str) -> Tuple[str, str]:
    """Convenience function to select music mood."""
    return get_music_mood_selector().select_mood(topic, category)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Music Mood Selector...")
    
    selector = get_music_mood_selector()
    
    # Test selections
    tests = [
        ("Why successful people wake up at 5 AM", "productivity"),
        ("The psychology of first impressions", "psychology"),
        ("5 money mistakes that keep you poor", "money"),
    ]
    
    for topic, cat in tests:
        mood, genre = selector.select_mood(topic, cat)
        safe_print(f"\nTopic: {topic}")
        safe_print(f"Mood: {mood}, Genre: {genre}")
    
    safe_print("\nTest complete!")


