#!/usr/bin/env python3
"""
ViralShorts Factory - AI B-Roll Keyword Generator v17.8
========================================================

Generates relevant B-roll search keywords using AI.

Good B-roll is essential for engaging videos:
- Must match content emotionally
- Must be visually interesting
- Must not distract from message

This replaces hardcoded keyword mappings with AI intelligence.
"""

import os
from src.ai.model_helper import get_dynamic_gemini_model
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

BROLL_KEYWORDS_FILE = STATE_DIR / "broll_keywords_learned.json"


class AIBRollKeywordGenerator:
    """
    Generates B-roll keywords using AI.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if BROLL_KEYWORDS_FILE.exists():
                with open(BROLL_KEYWORDS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "learned_mappings": {},  # phrase -> [keywords]
            "category_keywords": {}, # category -> [best keywords]
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(BROLL_KEYWORDS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_keywords(self, phrase: str, category: str = None,
                         count: int = 5) -> List[str]:
        """
        Generate B-roll search keywords for a phrase.
        
        Args:
            phrase: The content phrase to find B-roll for
            category: Optional content category
            count: Number of keywords to return
        
        Returns:
            List of search keywords for Pexels/Pixabay
        """
        # First try: Check learned mappings
        learned = self._get_learned_keywords(phrase, category)
        if learned:
            safe_print(f"   [BROLL] Using learned keywords")
            return learned[:count]
        
        # Second try: Generate with AI
        ai_keywords = self._generate_with_ai(phrase, category, count)
        if ai_keywords:
            safe_print(f"   [BROLL] AI-generated keywords")
            # Cache for future use
            self._cache_keywords(phrase, category, ai_keywords)
            return ai_keywords
        
        # Fallback: Extract keywords from phrase
        return self._fallback_keywords(phrase, category, count)
    
    def _get_learned_keywords(self, phrase: str, category: str) -> Optional[List[str]]:
        """Get learned keywords."""
        # Check phrase-specific cache
        phrase_key = phrase[:50].lower()
        if phrase_key in self.data.get("learned_mappings", {}):
            return self.data["learned_mappings"][phrase_key]
        
        # Check category cache
        if category and category in self.data.get("category_keywords", {}):
            return self.data["category_keywords"][category]
        
        return None
    
    def _generate_with_ai(self, phrase: str, category: str, 
                         count: int) -> Optional[List[str]]:
        """Generate keywords with AI."""
        prompt = f"""You are a video producer choosing B-roll footage.

TASK: Generate {count} search keywords to find PERFECT B-roll for this phrase.

Content Phrase: "{phrase}"
Category: {category if category else "general"}

REQUIREMENTS:
1. Keywords should find VISUALLY INTERESTING footage
2. Keywords should EMOTIONALLY match the content
3. Keywords should be abstract enough to find results on Pexels/Pixabay
4. NO text overlays needed - just background visuals

GOOD B-ROLL TYPES:
- Abstract/motion graphics (particles, light, flow)
- Nature metaphors (sunrise for new beginnings, storm for challenges)
- Human activities (working, thinking, succeeding)
- Technology/modern (for tech/productivity topics)
- Lifestyle (office, home, outdoors)

Return ONLY a JSON array of keywords:
["keyword1", "keyword2", "keyword3"]

JSON ONLY."""

        result = self._call_ai(prompt)
        
        if result:
            return self._parse_keywords(result)
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        # Try Groq first (faster for simple tasks)
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
                    temperature=0.7
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
    
    def _parse_keywords(self, result: str) -> Optional[List[str]]:
        """Parse AI response to keyword list."""
        try:
            # Extract JSON array
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                keywords = json.loads(result[start:end])
                return [str(k).strip() for k in keywords if k]
        except Exception as e:
            safe_print(f"   [!] Parse error: {e}")
        
        return None
    
    def _cache_keywords(self, phrase: str, category: str, keywords: List[str]):
        """Cache keywords for future use."""
        phrase_key = phrase[:50].lower()
        self.data["learned_mappings"][phrase_key] = keywords
        
        # Also update category cache
        if category:
            if category not in self.data["category_keywords"]:
                self.data["category_keywords"][category] = []
            
            # Add unique keywords
            for kw in keywords:
                if kw not in self.data["category_keywords"][category]:
                    self.data["category_keywords"][category].append(kw)
            
            # Keep only top 20 per category
            self.data["category_keywords"][category] = self.data["category_keywords"][category][:20]
        
        self._save()
    
    def _fallback_keywords(self, phrase: str, category: str, 
                          count: int) -> List[str]:
        """Generate fallback keywords from phrase."""
        # Extract key words from phrase
        words = re.findall(r'\b\w{4,}\b', phrase.lower())
        
        # Remove common words
        stop_words = {"this", "that", "your", "what", "when", "where", "which", 
                     "about", "with", "have", "from", "they", "will", "more"}
        keywords = [w for w in words if w not in stop_words][:3]
        
        # Add category-based generic keywords
        category_generics = {
            "psychology": ["brain", "thinking person", "meditation"],
            "money": ["money growth", "finance success", "coins"],
            "productivity": ["work focus", "time management", "office"],
            "health": ["fitness", "wellness", "healthy lifestyle"],
            "relationships": ["people talking", "couple", "friends"],
        }
        
        generics = category_generics.get(category, ["abstract motion", "colorful background"])
        
        # Combine
        result = keywords + generics
        return result[:count]
    
    def get_keywords_for_phrases(self, phrases: List[str], 
                                 category: str = None) -> Dict[str, List[str]]:
        """
        Generate keywords for multiple phrases.
        
        Returns dict: {phrase: [keywords]}
        """
        result = {}
        for phrase in phrases:
            result[phrase] = self.generate_keywords(phrase, category, count=3)
        return result


# Singleton
_broll_generator = None


def get_broll_keyword_generator() -> AIBRollKeywordGenerator:
    """Get singleton B-roll keyword generator."""
    global _broll_generator
    if _broll_generator is None:
        _broll_generator = AIBRollKeywordGenerator()
    return _broll_generator


def generate_broll_keywords(phrase: str, category: str = None) -> List[str]:
    """Convenience function to generate B-roll keywords."""
    return get_broll_keyword_generator().generate_keywords(phrase, category)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI B-Roll Keyword Generator...")
    
    gen = get_broll_keyword_generator()
    
    # Test phrases
    phrases = [
        ("Wake up 30 minutes earlier every day", "productivity"),
        ("Your brain is lying to you", "psychology"),
        ("Save $500 per month with this simple trick", "money"),
    ]
    
    for phrase, cat in phrases:
        keywords = gen.generate_keywords(phrase, cat)
        safe_print(f"\nPhrase: {phrase}")
        safe_print(f"Keywords: {keywords}")
    
    safe_print("\nTest complete!")


