#!/usr/bin/env python3
"""
ViralShorts Factory - AI Description Generator v17.8
=====================================================

Generates SEO-optimized video descriptions using AI.

Descriptions are important for:
- YouTube search ranking (SEO)
- Viewer expectations
- Call-to-action links
- Attribution (music, content)
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

DESCRIPTION_FILE = STATE_DIR / "description_templates.json"


class AIDescriptionGenerator:
    """
    Generates SEO-optimized descriptions using AI.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if DESCRIPTION_FILE.exists():
                with open(DESCRIPTION_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "templates": [],
            "best_keywords": [],
            "performance": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(DESCRIPTION_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_description(self, title: str, topic: str, category: str,
                            hook: str = None, hashtags: List[str] = None,
                            music_credit: str = None) -> str:
        """
        Generate SEO-optimized video description.
        
        Args:
            title: Video title
            topic: Video topic
            category: Content category
            hook: Video hook (optional)
            hashtags: List of hashtags (optional)
            music_credit: Music attribution (optional)
        
        Returns:
            Full video description text
        """
        # Try AI generation
        ai_desc = self._generate_with_ai(title, topic, category, hook)
        
        if ai_desc:
            safe_print("   [DESC] AI-generated description")
        else:
            ai_desc = self._fallback_description(title, topic, category)
        
        # Add hashtags
        if hashtags:
            ai_desc += "\n\n" + " ".join(hashtags)
        else:
            ai_desc += "\n\n#shorts #viral #" + category.replace("_", "")
        
        # Add music credit
        if music_credit:
            ai_desc += f"\n\nMusic: {music_credit}"
        
        return ai_desc
    
    def _generate_with_ai(self, title: str, topic: str, 
                         category: str, hook: str) -> Optional[str]:
        """Generate description with AI."""
        prompt = f"""You are a YouTube SEO expert writing video descriptions.

TASK: Write a short, SEO-optimized description for this YouTube Short.

Video Details:
- Title: {title}
- Topic: {topic}
- Category: {category}
{f'- Hook: {hook}' if hook else ''}

DESCRIPTION REQUIREMENTS:
1. 2-3 sentences MAX (Shorts descriptions are short!)
2. Include 2-3 relevant keywords naturally
3. Create curiosity to watch
4. Add value proposition
5. End with engagement prompt
6. NO hashtags (we add those separately)
7. NO emojis unless essential

STRUCTURE:
Line 1: Hook/value proposition
Line 2: What viewer will learn/gain
Line 3: Engagement prompt (optional)

Return ONLY the description text, no quotes, no formatting."""

        result = self._call_ai(prompt)
        
        if result:
            return self._clean_description(result)
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        # Try Gemini (better for writing)
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
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _clean_description(self, desc: str) -> str:
        """Clean description text."""
        desc = desc.strip('"\'')
        
        # Remove any hashtags (we add our own)
        desc = re.sub(r'#\w+', '', desc)
        
        # Limit length
        if len(desc) > 500:
            desc = desc[:500]
        
        return desc.strip()
    
    def _fallback_description(self, title: str, topic: str, 
                             category: str) -> str:
        """Generate fallback description."""
        templates = [
            f"Discover the truth about {topic}. This quick video reveals what most people miss.",
            f"Watch this before scrolling! {topic} explained in under 60 seconds.",
            f"The {topic} secrets they don't teach you. Save this for later!",
        ]
        
        import random
        return random.choice(templates) + "\n\nComment what you think!"
    
    def get_seo_keywords(self, category: str) -> List[str]:
        """Get SEO keywords for a category."""
        keywords = {
            "psychology": ["mind tricks", "psychology facts", "brain science"],
            "money": ["finance tips", "money hacks", "wealth building"],
            "productivity": ["productivity tips", "time management", "success habits"],
            "health": ["health tips", "wellness", "fitness"],
            "motivation": ["motivation", "success mindset", "inspiration"],
        }
        
        return keywords.get(category, ["viral", "trending", category])


# Singleton
_description_generator = None


def get_description_generator() -> AIDescriptionGenerator:
    """Get singleton description generator."""
    global _description_generator
    if _description_generator is None:
        _description_generator = AIDescriptionGenerator()
    return _description_generator


def generate_description(title: str, topic: str, category: str, **kwargs) -> str:
    """Convenience function to generate description."""
    return get_description_generator().generate_description(title, topic, category, **kwargs)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Description Generator...")
    
    gen = get_description_generator()
    
    # Test generation
    desc = gen.generate_description(
        title="5 Morning Habits of Billionaires",
        topic="morning routines for success",
        category="productivity",
        hook="STOP - This will change your mornings forever"
    )
    
    safe_print(f"\nGenerated Description:")
    safe_print("-" * 40)
    safe_print(desc)
    safe_print("-" * 40)
    
    safe_print("\nTest complete!")


