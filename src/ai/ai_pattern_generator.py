#!/usr/bin/env python3
"""
AI Pattern Generator for ViralShorts Factory v17.8
===================================================

THIS IS THE CORE OF AI-FIRST ARCHITECTURE!

Instead of hardcoding patterns, this module:
1. Asks AI to analyze viral content and generate patterns
2. Saves patterns to JSON files for caching
3. Refreshes patterns periodically (daily/weekly)

NO HARDCODED PATTERNS - Everything comes from AI!
"""

import os
import json

# Try both import styles for compatibility
try:
    from model_helper import get_dynamic_gemini_model
except ImportError:
    try:
        from src.ai.model_helper import get_dynamic_gemini_model
    except ImportError:
        # Fallback if model_helper not available
        def get_dynamic_gemini_model():
            return "gemini-2.5-flash"
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# Data directory
DATA_DIR = Path("./data/persistent")
DATA_DIR.mkdir(parents=True, exist_ok=True)

PATTERNS_FILE = DATA_DIR / "viral_patterns.json"
PATTERNS_CACHE_TTL = 24 * 3600  # 24 hours


class AIPatternGenerator:
    """
    Generates viral content patterns using AI.
    
    This is the REPLACEMENT for hardcoded patterns!
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load existing patterns from file."""
        try:
            if PATTERNS_FILE.exists():
                with open(PATTERNS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return self._get_minimal_fallback()
    
    def _get_minimal_fallback(self) -> Dict:
        """
        MINIMAL fallback - only used if AI completely unavailable.
        This is NOT the source of truth - AI is!
        """
        return {
            "patterns_source": "FALLBACK_ONLY",
            "ai_generated": False,
            "last_ai_update": None,
            "title_patterns": [],
            "hook_patterns": [],
            "engagement_baits": [],
            "psychological_triggers": [],
            "note": "This is emergency fallback. Run AI generation ASAP!"
        }
    
    def _save_patterns(self, patterns: Dict):
        """Save patterns to file."""
        patterns["last_saved"] = datetime.now().isoformat()
        with open(PATTERNS_FILE, 'w') as f:
            json.dump(patterns, f, indent=2)
        self.patterns = patterns
    
    def needs_refresh(self) -> bool:
        """Check if patterns need to be refreshed by AI."""
        if not self.patterns.get("ai_generated"):
            return True
        
        last_update = self.patterns.get("last_ai_update")
        if not last_update:
            return True
        
        try:
            last_dt = datetime.fromisoformat(last_update)
            age = (datetime.now() - last_dt).total_seconds()
            return age > PATTERNS_CACHE_TTL
        except:
            return True
    
    def generate_patterns_with_ai(self) -> Dict:
        """
        THE CORE FUNCTION: Ask AI to generate viral patterns.
        
        This replaces ALL hardcoded patterns!
        """
        safe_print("[AI PATTERNS] Generating patterns with AI...")
        
        prompt = """You are a viral content strategist who has analyzed millions of successful YouTube Shorts.

Generate the CURRENT and most effective viral patterns based on your latest knowledge of what works right now.

Analyze and provide:

1. TITLE PATTERNS (10 patterns that get clicks):
   - Use {placeholders} for dynamic content
   - Examples: "{number} {topic} You Didn't Know", "Why {topic} Changes Everything"

2. HOOK PATTERNS (10 scroll-stopping first lines):
   - Must stop the scroll in first 1.5 seconds
   - Include pattern interrupts, questions, shocking statements

3. ENGAGEMENT BAITS (8 comment-driving CTAs):
   - Questions that FORCE comments
   - Save/share triggers

4. PSYCHOLOGICAL TRIGGERS (8 triggers that work):
   - One word each: curiosity, fomo, etc.

5. SCROLL_STOP_OPENERS (8 openers):
   - Full template sentences that stop scrolling

6. PROVEN_CATEGORIES (8 categories that consistently perform):
   - Single words: psychology, money, etc.

7. RETENTION_TRICKS (6 tricks to keep viewers):
   - Brief descriptions

8. CTA_FORMULAS (6 call-to-action templates):
   - Use {placeholders}

OUTPUT AS JSON:
{
    "title_patterns": ["pattern1", "pattern2", ...],
    "hook_patterns": ["hook1", "hook2", ...],
    "engagement_baits": ["bait1", "bait2", ...],
    "psychological_triggers": ["trigger1", "trigger2", ...],
    "scroll_stop_openers": ["opener1", "opener2", ...],
    "proven_categories": ["cat1", "cat2", ...],
    "retention_tricks": ["trick1", "trick2", ...],
    "cta_formulas": ["cta1", "cta2", ...]
}

JSON ONLY - no other text!"""

        result = self._call_ai(prompt)
        
        if result:
            parsed = self._parse_json(result)
            if parsed and parsed.get("title_patterns"):
                parsed["ai_generated"] = True
                parsed["patterns_source"] = "AI_GENERATED"
                parsed["last_ai_update"] = datetime.now().isoformat()
                parsed["generation_model"] = "gemini/groq"
                self._save_patterns(parsed)
                safe_print(f"[AI PATTERNS] Generated {len(parsed.get('title_patterns', []))} title patterns")
                return parsed
        
        safe_print("[AI PATTERNS] AI generation failed, using cached/fallback")
        return self.patterns
    
    def _call_ai(self, prompt: str, max_tokens: int = 1500) -> Optional[str]:
        """Call AI (Gemini first, then Groq)."""
        # Try Gemini first (more quota)
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                safe_print(f"[!] Gemini error: {e}")
        
        # Try Groq
        if self.groq_key:
            try:
                from groq import Groq
                # v17.8: Dynamic model selection
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
                    max_tokens=max_tokens,
                    temperature=0.8
                )
                return response.choices[0].message.content
            except Exception as e:
                safe_print(f"[!] Groq error: {e}")
        
        return None
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        try:
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            # Find JSON object
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            safe_print(f"[!] JSON parse error: {e}")
        return None
    
    def get_patterns(self) -> Dict:
        """
        Get patterns - refresh if needed.
        
        This is the main entry point.
        """
        if self.needs_refresh():
            return self.generate_patterns_with_ai()
        return self.patterns
    
    def get_title_patterns(self) -> List[str]:
        """Get title patterns."""
        return self.get_patterns().get("title_patterns", [])
    
    def get_hook_patterns(self) -> List[str]:
        """Get hook patterns."""
        return self.get_patterns().get("hook_patterns", [])
    
    def get_engagement_baits(self) -> List[str]:
        """Get engagement baits."""
        return self.get_patterns().get("engagement_baits", [])


# Singleton
_pattern_generator = None

def get_pattern_generator() -> AIPatternGenerator:
    """Get the singleton pattern generator."""
    global _pattern_generator
    if _pattern_generator is None:
        _pattern_generator = AIPatternGenerator()
    return _pattern_generator


def refresh_patterns_if_needed() -> Dict:
    """Convenience function to refresh patterns."""
    return get_pattern_generator().get_patterns()


if __name__ == "__main__":
    # Test the pattern generator
    safe_print("Testing AI Pattern Generator...")
    generator = get_pattern_generator()
    
    if generator.needs_refresh():
        safe_print("Patterns need refresh - generating with AI...")
        patterns = generator.generate_patterns_with_ai()
    else:
        safe_print("Patterns are fresh - using cached...")
        patterns = generator.patterns
    
    safe_print(f"\nPatterns source: {patterns.get('patterns_source', 'unknown')}")
    safe_print(f"AI generated: {patterns.get('ai_generated', False)}")
    safe_print(f"Title patterns: {len(patterns.get('title_patterns', []))}")
    safe_print(f"Hook patterns: {len(patterns.get('hook_patterns', []))}")


