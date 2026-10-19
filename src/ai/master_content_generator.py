#!/usr/bin/env python3
"""
ViralShorts Factory - Master Content Generator v17.9.7
=========================================================

This module GENERATES 10/10 content by:
1. Using a master prompt with ALL viral requirements baked in
2. Auto-checking against hardcoded rules before returning
3. Iteratively improving until 10/10 is achieved

This is the GENERATION counterpart to master_evaluator.py
"""

import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# v17.9.36: Import centralized rate-limited AI caller
try:
    from src.ai.smart_ai_caller import smart_call_ai
    SMART_CALLER_AVAILABLE = True
except ImportError:
    try:
        from smart_ai_caller import smart_call_ai
        SMART_CALLER_AVAILABLE = True
    except ImportError:
        SMART_CALLER_AVAILABLE = False
        smart_call_ai = None

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# MASTER CONTENT GENERATION PROMPT
# =============================================================================

MASTER_GENERATION_PROMPT = """You are the WORLD'S MOST AGGRESSIVE (but truthful) VIRAL CONTENT CREATOR.

Your ONLY goal: Create content that is IMPOSSIBLE TO SCROLL PAST and scores 10/10.

=== MINDSET: MAXIMUM VIRALITY (v17.9.9) ===
You are NOT creating "helpful content" - you are creating UNMISSABLE content.
The difference: helpful content = skipped. Unmissable content = watched, shared, debated.

Your content must make viewers feel:
- "Wait, am I doing this wrong?" (Identity threat)
- "I NEED to know the rest" (Open loop)
- "This person knows something I don't" (Authority gap)
- "I have to share this / argue about this" (Social currency)

=== ABSOLUTE REQUIREMENTS (ALL MUST BE MET) ===

1. HOOK (First Phrase) - MUST BE AGGRESSIVE:
   ✓ Start with ATTACK: "STOP what you're doing" / "You're doing this WRONG"
   ✓ OR irresistible question: "Why do 90% of people FAIL at...?"
   ✓ Include a NUMBER that creates tension ($500 you're losing, 90% fail rate)
   ✓ Be under 12 words - every word must PUNCH
   ✓ Create instant "I MUST know more" reaction
   ✓ NAME AN ENEMY: "Banks don't want you to know" / "Your boss hopes you never learn"

2. VALUE DELIVERY - MUST BE SPECIFIC AND BOLD:
   ✓ Provide AT LEAST 3 specific, actionable tips with EXACT steps
   ✓ Include REAL numbers ($500, 90%, 30 days) - NO random numbers
   ✓ Each tip must be USABLE in the next 5 MINUTES
   ✓ Total content: 80-150 words (dense with value)
   ✓ Deliver EXACTLY what the hook promises - OVER-deliver
   ✓ TAKE A STANCE: "Most advice says X, but here's why that's wrong"

3. EMOTIONAL TRIGGERS - MUST include at least TWO:
   ✓ FOMO: "before it's too late", "starting TONIGHT", "most people will ignore this"
   ✓ Curiosity: "the REAL reason", "what they don't tell you", "the truth nobody shares"
   ✓ Outrage: "this is costing you", "they're hiding this", "you're being played"
   ✓ Superiority: "while everyone else", "the 10% who succeed know", "smart people"
   ✓ Urgency: "before your next paycheck", "this week", "before Monday"

4. NATURAL VOICE - MUST SOUND HUMAN:
   ✓ Use contractions: don't, can't, won't, it's, you're
   ✓ Short sentences: 8-15 words max per phrase - PUNCHY
   ✓ Conversational: Like a smart friend telling you a secret
   ✓ NO corporate speak, NO academic tone, NO AI-sounding phrases
   ✓ Use "you" and "your" constantly - make it PERSONAL

5. CTA (Last Phrase) - MUST FORCE ENGAGEMENT:
   ✓ End with a POLARIZING question that splits the audience
   ✓ Examples: "Are you in the 90% or the 10%?", "Agree or disagree?"
   ✓ Make them WANT to defend their position
   ✓ NOT generic like "Comment below" - create DEBATE

=== CONTENT TO CREATE ===

Topic: {topic}
Category: {category}
Target Duration: {duration} seconds
Target Phrases: {phrase_count}

=== PREVIOUS FEEDBACK (if any) ===
{feedback}

=== YOUR OUTPUT FORMAT ===

Create EXACTLY {phrase_count} phrases. Output JSON:

{{
    "hook": "Your scroll-stopping hook (first phrase)",
    "phrases": [
        "Hook goes here as first phrase",
        "Second phrase with first tip/insight",
        "Third phrase with second tip/insight",
        "Fourth phrase with third tip/insight",
        "Fifth phrase building to payoff",
        "CTA phrase with engaging question"
    ],
    "cta": "The CTA question at the end",
    "numbers_used": ["$500", "90%", "30 days"],
    "emotional_trigger": "FOMO/Curiosity/Shock/Relatability",
    "self_score": 1-10,
    "why_viral": "One sentence on why this will go viral"
}}

REMEMBER: If this content doesn't make YOU want to stop scrolling and watch, START OVER.
OUTPUT JSON ONLY."""


class MasterContentGenerator:
    """
    Generates 10/10 viral content using the master prompt.
    """
    
    # Hardcoded checks that MUST pass
    REQUIREMENTS = {
        "pattern_interrupt": (
            ["stop", "wait", "don't", "?"],
            "Hook must have pattern interrupt or question"
        ),
        "has_numbers": (
            r'\$?\d+',
            "Must include specific numbers"
        ),
        "round_numbers": (
            r'(\$\d{3,4}|[0-9]+0%|[0-9]+ day|[0-9]+ week)',
            "Numbers should be round/memorable"
        ),
        "urgency_words": (
            ["today", "now", "before", "starting", "immediately", "don't miss"],
            "Must create urgency"
        ),
        "contractions": (
            ["don't", "can't", "won't", "it's", "you're", "that's", "here's"],
            "Must use contractions for natural voice"
        ),
        "question_cta": (
            ["?"],
            "CTA must include a question"
        ),
    }
    
    def __init__(self):
        self.history = []
        
    def generate(self, topic: str, category: str, 
                duration: int = 50, phrase_count: int = 8,
                max_attempts: int = 3) -> Dict:
        """
        Generate 10/10 viral content.
        
        Iterates until content passes all hardcoded checks.
        """
        feedback = ""
        best_result = None
        best_score = 0
        
        for attempt in range(max_attempts):
            safe_print(f"   [MASTER GEN] Attempt {attempt + 1}/{max_attempts}")
            
            # Generate content
            result = self._generate_content(topic, category, duration, phrase_count, feedback)
            
            if not result:
                continue
            
            # Check against hardcoded requirements
            check_result = self._check_requirements(result)
            
            # Calculate score
            score = 10 - len(check_result["failed"])
            
            if score > best_score:
                best_score = score
                best_result = result
                best_result["master_score"] = score
                best_result["checks_passed"] = check_result["passed"]
                best_result["checks_failed"] = check_result["failed"]
            
            # If perfect, we're done
            if score == 10:
                safe_print(f"   [MASTER GEN] PERFECT 10/10!")
                return best_result
            
            # Build feedback for next attempt
            feedback = f"Previous attempt scored {score}/10. Issues:\n"
            for fail in check_result["failed"]:
                feedback += f"- {fail}\n"
            feedback += "Fix ALL issues in next attempt."
        
        if best_result:
            safe_print(f"   [MASTER GEN] Best score: {best_score}/10")
        
        return best_result
    
    def _generate_content(self, topic: str, category: str,
                         duration: int, phrase_count: int, 
                         feedback: str) -> Optional[Dict]:
        """Call AI to generate content."""
        prompt = MASTER_GENERATION_PROMPT.format(
            topic=topic,
            category=category,
            duration=duration,
            phrase_count=phrase_count,
            feedback=feedback or "No previous feedback - this is your first attempt."
        )
        
        # Try Groq first
        result = self._call_groq(prompt)
        if result:
            return result
        
        # Try Gemini as fallback
        result = self._call_gemini(prompt)
        if result:
            return result
        
        return None
    
    def _check_requirements(self, content: Dict) -> Dict:
        """Check content against hardcoded requirements."""
        passed = []
        failed = []
        
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        all_text = f"{hook} {' '.join(phrases)} {cta}".lower()
        
        # 1. Pattern interrupt in hook
        req = self.REQUIREMENTS["pattern_interrupt"]
        if any(word in hook.lower() for word in req[0]):
            passed.append("Pattern interrupt: OK")
        else:
            failed.append(req[1])
        
        # 2. Has numbers
        req = self.REQUIREMENTS["has_numbers"]
        if re.search(req[0], all_text):
            passed.append("Has numbers: OK")
        else:
            failed.append(req[1])
        
        # 3. Round numbers (not weird ones)
        weird_numbers = re.findall(r'\d{4,}', all_text)
        has_weird = any(int(n) > 2030 and int(n) % 100 != 0 for n in weird_numbers if n.isdigit())
        if not has_weird:
            passed.append("Round numbers: OK")
        else:
            failed.append("Avoid random numbers like 1847 - use round numbers")
        
        # 4. Urgency words
        req = self.REQUIREMENTS["urgency_words"]
        if any(word in all_text for word in req[0]):
            passed.append("Urgency: OK")
        else:
            failed.append(req[1])
        
        # 5. Contractions
        req = self.REQUIREMENTS["contractions"]
        if any(word in all_text for word in req[0]):
            passed.append("Natural voice: OK")
        else:
            failed.append(req[1])
        
        # 6. Question in CTA
        if "?" in cta:
            passed.append("Question CTA: OK")
        else:
            failed.append("CTA must end with a question")
        
        # 7. Content length
        word_count = len(all_text.split())
        if word_count >= 80:
            passed.append(f"Word count ({word_count}): OK")
        else:
            failed.append(f"Content too short ({word_count} words) - need 80+")
        
        # 8. Phrase count
        if len(phrases) >= 5:
            passed.append(f"Phrase count ({len(phrases)}): OK")
        else:
            failed.append(f"Only {len(phrases)} phrases - need 5+")
        
        return {"passed": passed, "failed": failed}
    
    def _call_groq(self, prompt: str) -> Optional[Dict]:
        """Call Groq API."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None
        
        try:
            import requests
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 1500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"]
                return self._parse_json(text)
            return None
        except Exception as e:
            safe_print(f"[!] Groq call failed: {e}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[Dict]:
        """
        Call Gemini API with RATE LIMITING.
        
        v17.9.36: Now uses centralized smart_call_ai to respect rate limits
        and avoid 429 errors.
        """
        # v17.9.36: Use centralized rate-limited caller if available
        if SMART_CALLER_AVAILABLE and smart_call_ai:
            try:
                result = smart_call_ai(prompt, hint="creative", max_tokens=1500)
                if result:
                    return self._parse_json(result)
                return None
            except Exception as e:
                safe_print(f"[!] Smart AI call failed: {e}")
                return None
        
        # Fallback to direct call (with manual delay)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        
        try:
            import requests
            
            # v17.9.37: DYNAMIC rate limit delay
            try:
                from src.ai.model_helper import get_smart_delay
                delay = get_smart_delay("gemini-2.5-flash", "gemini")
            except ImportError:
                delay = 4.4  # Fallback
            time.sleep(delay)
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.8, "maxOutputTokens": 1500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json(text)
            elif response.status_code == 429:
                safe_print("[!] Gemini 429 - rate limited (fallback mode)")
            return None
        except Exception as e:
            safe_print(f"[!] Gemini call failed: {e}")
            return None
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            return None
        except:
            return None


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

_master_generator = None


def get_master_generator() -> MasterContentGenerator:
    """Get singleton generator."""
    global _master_generator
    if _master_generator is None:
        _master_generator = MasterContentGenerator()
    return _master_generator


def generate_master_content(topic: str, category: str, 
                              duration: int = 50, 
                              phrase_count: int = 8) -> Dict:
    """Convenience function."""
    return get_master_generator().generate(topic, category, duration, phrase_count)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("MASTER CONTENT GENERATOR TEST")
    safe_print("=" * 60)
    
    generator = get_master_generator()
    
    # Test with a sample topic
    result = generator.generate(
        topic="side hustle strategies for beginners",
        category="money",
        duration=50,
        phrase_count=7
    )
    
    if result:
        safe_print(f"\nGenerated Content:")
        safe_print(f"Hook: {result.get('hook', 'N/A')}")
        safe_print(f"\nPhrases:")
        for i, phrase in enumerate(result.get('phrases', []), 1):
            safe_print(f"  {i}. {phrase}")
        safe_print(f"\nCTA: {result.get('cta', 'N/A')}")
        safe_print(f"\nMaster Score: {result.get('master_score', 'N/A')}/10")
        safe_print(f"Checks Passed: {len(result.get('checks_passed', []))}")
        safe_print(f"Checks Failed: {len(result.get('checks_failed', []))}")
        
        if result.get('checks_failed'):
            safe_print(f"\nIssues to fix:")
            for issue in result.get('checks_failed', []):
                safe_print(f"  - {issue}")
    else:
        safe_print("\nFailed to generate content (no API keys available)")
    
    safe_print("=" * 60)

