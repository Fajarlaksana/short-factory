#!/usr/bin/env python3
"""
ViralShorts Factory - AI Audience Persona Generator v17.8
==========================================================

Generates detailed audience personas for content targeting.
"""

import os
from src.ai.model_helper import get_dynamic_gemini_model
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

PERSONA_FILE = STATE_DIR / "audience_personas.json"


class AIAudiencePersonaGenerator:
    """Generates audience personas using AI."""
    
    # Base persona templates
    PERSONA_TEMPLATES = {
        "productivity": {
            "name": "Ambitious Alex",
            "age_range": "25-34",
            "interests": ["productivity", "self-improvement", "career growth"],
            "pain_points": ["lack of time", "overwhelm", "procrastination"],
            "content_preferences": ["quick tips", "actionable advice", "life hacks"]
        },
        "money": {
            "name": "Wealth-Builder Wendy",
            "age_range": "28-40",
            "interests": ["investing", "financial freedom", "side hustles"],
            "pain_points": ["debt", "low savings", "missing opportunities"],
            "content_preferences": ["money tips", "investment guides", "success stories"]
        },
        "psychology": {
            "name": "Curious Chris",
            "age_range": "18-35",
            "interests": ["human behavior", "self-understanding", "relationships"],
            "pain_points": ["understanding others", "self-doubt", "social anxiety"],
            "content_preferences": ["mind tricks", "psychology facts", "behavior analysis"]
        },
        "motivation": {
            "name": "Driven Dana",
            "age_range": "20-35",
            "interests": ["success", "mindset", "personal growth"],
            "pain_points": ["lack of motivation", "fear of failure", "comparison"],
            "content_preferences": ["quotes", "success stories", "mindset shifts"]
        }
    }
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if PERSONA_FILE.exists():
                with open(PERSONA_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "personas": {},
            "generated": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(PERSONA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_persona(self, category: str, topic: str = None) -> Dict:
        """
        Generate a detailed audience persona.
        
        Returns persona dict with demographics, interests, pain points, etc.
        """
        # Check cache
        if category in self.data["personas"]:
            cached = self.data["personas"][category]
            safe_print(f"   [PERSONA] Using cached persona for {category}")
            return cached
        
        # Try AI generation
        ai_result = self._generate_with_ai(category, topic)
        
        if ai_result:
            safe_print(f"   [PERSONA] AI-generated for {category}")
            self.data["personas"][category] = ai_result
            self._save()
            return ai_result
        
        # Use template
        return self._get_template_persona(category)
    
    def _generate_with_ai(self, category: str, topic: str) -> Optional[Dict]:
        """Generate with AI."""
        prompt = f"""Create a detailed audience persona for YouTube Shorts viewers.

CONTENT CATEGORY: {category}
{f'SPECIFIC TOPIC: {topic}' if topic else ''}

Create a persona for someone who would watch and engage with this content.

Return JSON:
{{
  "name": "A memorable persona name",
  "age_range": "XX-XX",
  "gender_split": "60% male, 40% female",
  "interests": ["interest1", "interest2", "interest3"],
  "pain_points": ["pain1", "pain2", "pain3"],
  "goals": ["goal1", "goal2"],
  "content_preferences": ["preference1", "preference2"],
  "viewing_habits": "When and how they watch",
  "engagement_style": "How they interact with content",
  "hook_triggers": ["what makes them stop scrolling"],
  "value_expectations": "What value they expect"
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
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse JSON response."""
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None
    
    def _get_template_persona(self, category: str) -> Dict:
        """Get template persona."""
        template = self.PERSONA_TEMPLATES.get(category)
        
        if template:
            return {
                **template,
                "gender_split": "55% male, 45% female",
                "viewing_habits": "During commute, before bed, during breaks",
                "engagement_style": "Likes, occasionally comments",
                "hook_triggers": ["curiosity", "controversy", "quick value"],
                "value_expectations": "Quick, actionable insights"
            }
        
        # Generic persona
        return {
            "name": "Curious Viewer",
            "age_range": "18-34",
            "gender_split": "50% male, 50% female",
            "interests": [category, "learning", "entertainment"],
            "pain_points": ["boredom", "seeking knowledge", "self-improvement"],
            "goals": ["learn something new", "be entertained"],
            "content_preferences": ["short videos", "quick facts", "surprises"],
            "viewing_habits": "Throughout the day",
            "engagement_style": "Passive viewer, occasional liker",
            "hook_triggers": ["curiosity", "shock", "relatability"],
            "value_expectations": "Entertainment or quick learning"
        }
    
    def get_hook_for_persona(self, category: str) -> List[str]:
        """Get hooks that resonate with the persona."""
        persona = self.generate_persona(category)
        triggers = persona.get("hook_triggers", ["curiosity"])
        
        hooks = {
            "curiosity": "Did you know that...",
            "controversy": "Everyone is wrong about...",
            "shock": "This will SHOCK you...",
            "relatability": "If you've ever felt...",
            "quick value": "In 30 seconds, you'll learn...",
            "fomo": "Before it's too late..."
        }
        
        return [hooks.get(t, hooks["curiosity"]) for t in triggers[:3]]
    
    def get_content_recommendations(self, category: str) -> Dict:
        """Get content recommendations based on persona."""
        persona = self.generate_persona(category)
        
        return {
            "persona_name": persona.get("name"),
            "target_age": persona.get("age_range"),
            "address_pain_points": persona.get("pain_points", [])[:2],
            "offer_value": persona.get("value_expectations"),
            "use_hooks": persona.get("hook_triggers", ["curiosity"])[:2],
            "content_style": persona.get("content_preferences", ["quick tips"])[:2]
        }


# Singleton
_persona_generator = None


def get_persona_generator() -> AIAudiencePersonaGenerator:
    """Get singleton generator."""
    global _persona_generator
    if _persona_generator is None:
        _persona_generator = AIAudiencePersonaGenerator()
    return _persona_generator


def generate_persona(category: str, topic: str = None) -> Dict:
    """Convenience function."""
    return get_persona_generator().generate_persona(category, topic)


if __name__ == "__main__":
    safe_print("Testing AI Audience Persona Generator...")
    
    generator = get_persona_generator()
    
    # Test persona generation
    persona = generator.generate_persona("productivity", "morning routines")
    
    safe_print(f"\nAudience Persona:")
    safe_print("-" * 40)
    safe_print(f"Name: {persona.get('name')}")
    safe_print(f"Age: {persona.get('age_range')}")
    safe_print(f"Gender: {persona.get('gender_split')}")
    safe_print(f"Interests: {', '.join(persona.get('interests', []))}")
    safe_print(f"Pain Points: {', '.join(persona.get('pain_points', []))}")
    safe_print(f"Hook Triggers: {', '.join(persona.get('hook_triggers', []))}")
    
    # Test recommendations
    safe_print(f"\nContent Recommendations:")
    recs = generator.get_content_recommendations("productivity")
    safe_print(f"  Target: {recs.get('persona_name')}, age {recs.get('target_age')}")
    safe_print(f"  Address: {', '.join(recs.get('address_pain_points', []))}")
    safe_print(f"  Use hooks: {', '.join(recs.get('use_hooks', []))}")
    
    # Test hooks
    safe_print(f"\nRecommended Hooks:")
    hooks = generator.get_hook_for_persona("productivity")
    for h in hooks:
        safe_print(f"  - {h}")
    
    safe_print("\nTest complete!")


