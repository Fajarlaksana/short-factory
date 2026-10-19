#!/usr/bin/env python3
"""
ViralShorts Factory - AI Hashtag Generator v17.8
=================================================

Generates optimized hashtags for YouTube Shorts.

Hashtag strategy:
- 3-5 hashtags MAX (YouTube Shorts limit)
- Mix of broad (reach) and niche (targeting)
- #shorts is almost always required
- Trending hashtags boost visibility
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

HASHTAG_FILE = STATE_DIR / "hashtag_performance.json"


class AIHashtagGenerator:
    """
    Generates optimized hashtags using AI and performance data.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if HASHTAG_FILE.exists():
                with open(HASHTAG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "best_hashtags": {},
            "trending": [],
            "performance": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(HASHTAG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_hashtags(self, topic: str, category: str, 
                         title: str = None, count: int = 5) -> List[str]:
        """
        Generate optimized hashtags.
        
        Args:
            topic: Video topic
            category: Content category
            title: Video title (optional)
            count: Number of hashtags (default 5)
        
        Returns:
            List of hashtags with #
        """
        # Always include #shorts
        hashtags = ["#shorts"]
        
        # Get AI suggestions
        ai_hashtags = self._generate_with_ai(topic, category, title, count - 1)
        
        if ai_hashtags:
            safe_print("   [HASHTAG] AI-generated hashtags")
            hashtags.extend(ai_hashtags)
        else:
            hashtags.extend(self._get_category_hashtags(category, count - 1))
        
        # Ensure #shorts is first and limit to count
        hashtags = list(dict.fromkeys(hashtags))[:count]
        
        return hashtags
    
    def _generate_with_ai(self, topic: str, category: str,
                         title: str, count: int) -> Optional[List[str]]:
        """Generate hashtags with AI."""
        prompt = f"""You are a YouTube Shorts hashtag expert.

TASK: Generate {count} trending hashtags for this video.

Video Details:
- Topic: {topic}
- Category: {category}
{f'- Title: {title}' if title else ''}

HASHTAG RULES:
1. Return EXACTLY {count} hashtags (we already have #shorts)
2. Mix trending (broad reach) with niche (targeted)
3. NO spaces in hashtags
4. Lowercase preferred
5. Keep short (under 20 chars each)
6. Relevant to the content

Return ONLY the hashtags, one per line, with # symbol.
Example:
#productivity
#successmindset
#lifehacks"""

        result = self._call_ai(prompt)
        
        if result:
            return self._parse_hashtags(result, count)
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        # Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                safe_print(f"   [!] Gemini error: {e}")
        
        # Try Groq
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
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _parse_hashtags(self, text: str, count: int) -> List[str]:
        """Parse hashtags from AI response."""
        hashtags = []
        
        # Find all hashtags in text
        found = re.findall(r'#\w+', text)
        
        for h in found:
            h_clean = h.lower()
            if h_clean not in hashtags and h_clean != "#shorts":
                hashtags.append(h_clean)
        
        return hashtags[:count]
    
    def _get_category_hashtags(self, category: str, count: int) -> List[str]:
        """Get fallback hashtags for a category."""
        category_tags = {
            "psychology": ["#psychologyfacts", "#mindset", "#brain", "#mentalhealth"],
            "money": ["#moneytips", "#financialfreedom", "#investing", "#wealthbuilding"],
            "productivity": ["#productivityhacks", "#success", "#motivation", "#grindset"],
            "health": ["#healthtips", "#wellness", "#fitness", "#healthylifestyle"],
            "motivation": ["#motivation", "#success", "#mindset", "#inspiration"],
            "relationships": ["#relationships", "#love", "#dating", "#psychology"],
            "tech": ["#tech", "#technology", "#gadgets", "#innovation"],
        }
        
        tags = category_tags.get(category, ["#viral", "#trending", "#foryou"])
        return tags[:count]
    
    def record_performance(self, hashtags: List[str], views: int, 
                          category: str):
        """Record hashtag performance for learning."""
        for tag in hashtags:
            tag_lower = tag.lower()
            
            if tag_lower not in self.data["performance"]:
                self.data["performance"][tag_lower] = {
                    "uses": 0,
                    "total_views": 0,
                    "categories": []
                }
            
            self.data["performance"][tag_lower]["uses"] += 1
            self.data["performance"][tag_lower]["total_views"] += views
            
            if category not in self.data["performance"][tag_lower]["categories"]:
                self.data["performance"][tag_lower]["categories"].append(category)
        
        self._save()
    
    def get_best_hashtags(self, category: str = None, count: int = 5) -> List[str]:
        """Get best performing hashtags."""
        if not self.data["performance"]:
            return self._get_category_hashtags(category or "general", count)
        
        # Sort by average views
        sorted_tags = sorted(
            self.data["performance"].items(),
            key=lambda x: x[1]["total_views"] / max(1, x[1]["uses"]),
            reverse=True
        )
        
        # Filter by category if provided
        if category:
            sorted_tags = [
                (tag, data) for tag, data in sorted_tags
                if category in data.get("categories", [])
            ]
        
        return [tag for tag, _ in sorted_tags[:count]]


# Singleton
_hashtag_generator = None


def get_hashtag_generator() -> AIHashtagGenerator:
    """Get singleton hashtag generator."""
    global _hashtag_generator
    if _hashtag_generator is None:
        _hashtag_generator = AIHashtagGenerator()
    return _hashtag_generator


def generate_hashtags(topic: str, category: str, **kwargs) -> List[str]:
    """Convenience function to generate hashtags."""
    return get_hashtag_generator().generate_hashtags(topic, category, **kwargs)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Hashtag Generator...")
    
    gen = get_hashtag_generator()
    
    # Test generation
    hashtags = gen.generate_hashtags(
        topic="morning routines for success",
        category="productivity",
        title="5 Morning Habits of Billionaires"
    )
    
    safe_print(f"\nGenerated Hashtags:")
    safe_print("-" * 40)
    for h in hashtags:
        safe_print(f"  {h}")
    safe_print("-" * 40)
    
    # Test best hashtags
    best = gen.get_best_hashtags("productivity", 3)
    safe_print(f"\nBest performing tags:")
    for h in best:
        safe_print(f"  {h}")
    
    safe_print("\nTest complete!")


