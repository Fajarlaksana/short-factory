#!/usr/bin/env python3
"""
ViralShorts Factory - Master Quality Evaluator v17.9.7
=========================================================

A COMPREHENSIVE AI-powered quality evaluation system that:
1. Uses a master prompt to evaluate ALL aspects of a video
2. Combines AI evaluation with hardcoded viral science rules
3. Provides actionable feedback to achieve 10/10 scores

This is THE definitive quality gate for viral video content.
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

# State directory
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# MASTER MASTER EVALUATION PROMPT
# =============================================================================

MASTER_EVALUATION_PROMPT = """You are the ULTIMATE VIRAL VIDEO QUALITY EXPERT.

Your job: Evaluate this video content with BRUTAL HONESTY and provide a score from 1-10.
You have seen millions of viral videos. You know EXACTLY what makes content go viral.

=== SCORING CRITERIA (Each out of 10) ===

1. HOOK POWER (20% weight)
   - Does the first 1-3 seconds FORCE viewers to stop scrolling?
   - Pattern interrupt? Question? Shock? Curiosity gap?
   - 10 = "I physically CANNOT scroll past this"
   - 5 = "It's okay, might watch"
   - 1 = "I'd scroll instantly"

2. VALUE DELIVERY (25% weight)
   - Does the viewer GAIN something concrete?
   - Specific tips, numbers, insights, entertainment?
   - 10 = "I learned something I'll remember and use"
   - 5 = "Nice info but nothing groundbreaking"
   - 1 = "Empty promises, no actual value"

3. EMOTIONAL TRIGGER (15% weight)
   - Does it trigger: Curiosity, FOMO, Shock, Awe, Relatability, Controversy?
   - 10 = "I FELT something watching this"
   - 5 = "Mildly interesting"
   - 1 = "Emotionally flat"

4. SHAREABILITY (15% weight)
   - Would someone share this with a friend?
   - 10 = "I need to send this to 5 people RIGHT NOW"
   - 5 = "Maybe I'd share if asked"
   - 1 = "No one would care about this"

5. BELIEVABILITY (10% weight)
   - Are claims realistic and trustworthy?
   - Numbers round and memorable? Sources implied?
   - 10 = "I believe this completely"
   - 5 = "Seems plausible"
   - 1 = "Sounds like BS"

6. PACING & FLOW (10% weight)
   - Does it feel natural? Good rhythm?
   - Not too fast, not too slow?
   - 10 = "Perfectly paced, couldn't look away"
   - 5 = "Fine pacing"
   - 1 = "Boring or rushed"

7. CTA EFFECTIVENESS (5% weight)
   - Does the call-to-action drive engagement?
   - 10 = "I MUST comment/like/share"
   - 5 = "Standard CTA"
   - 1 = "No CTA or ineffective"

=== BONUS POINTS FOR AGGRESSIVE (BUT TRUTHFUL) CONTENT (v17.9.9) ===

Add +0.5 for each of these VIRAL BOOSTERS:
+ Names an ENEMY: "Banks", "Your boss", "Doctors", "Traditional advice"
+ Takes a BOLD STANCE: "Everyone says X, but they're wrong"
+ Creates DEBATE: Viewers will argue about this
+ Uses URGENCY: "Before your next paycheck", "Starting tonight"
+ Creates SUPERIORITY: "The 10% who succeed know this"
+ CHALLENGES BELIEFS: Makes viewer question something they assumed true

These are what separate 8/10 from 10/10. Safe content = 7-8. Bold content = 9-10.

=== HARDCODED REQUIREMENTS FOR 10/10 ===

A PERFECT 10/10 video MUST have ALL of these:
✓ Hook uses pattern interrupt (STOP, WAIT, DON'T) or intriguing question
✓ Hook ATTACKS or CHALLENGES something (not just informs)
✓ At least 3 specific, actionable tips/insights with real numbers
✓ Delivers EXACTLY what the hook promises - OVER-delivers
✓ Uses round, memorable numbers ($500, 90%, 30 days)
✓ Sounds like a real human, not AI-generated text
✓ Creates STRONG urgency or FOMO
✓ Has a POLARIZING CTA that forces debate (not generic "comment below")
✓ Takes a STANCE that some people will disagree with (but is truthful)
✓ Total content feels complete, not like an intro that was cut off

Missing ANY = Maximum 9/10
Missing 2+ = Maximum 8/10
Missing 3+ = Maximum 7/10

=== CONTENT TO EVALUATE ===

HOOK: {hook}

PHRASES:
{phrases}

CTA: {cta}

TOPIC: {topic}
CATEGORY: {category}

=== YOUR EVALUATION ===

Evaluate each criterion, then provide your final assessment.

OUTPUT JSON ONLY:
{{
    "scores": {{
        "hook_power": 1-10,
        "value_delivery": 1-10,
        "emotional_trigger": 1-10,
        "shareability": 1-10,
        "believability": 1-10,
        "pacing_flow": 1-10,
        "cta_effectiveness": 1-10
    }},
    "weighted_score": calculated_score_out_of_10,
    "missing_requirements": ["list", "of", "missing", "10/10", "requirements"],
    "score_cap": "what is max possible score given missing requirements",
    "final_score": 1-10,
    "would_go_viral": true/false,
    "strongest_element": "what's best about this",
    "weakest_element": "what needs most improvement",
    "specific_improvements": [
        "Exact change 1 to improve score",
        "Exact change 2 to improve score",
        "Exact change 3 to improve score"
    ],
    "rewritten_hook": "Your improved version of the hook",
    "verdict": "VIRAL_GUARANTEED" / "VIRAL_LIKELY" / "NEEDS_WORK" / "WILL_FLOP"
}}

BE HARSH. We want 10/10 videos, not participation trophies.
OUTPUT JSON ONLY."""


class MasterEvaluator:
    """
    The ultimate quality evaluator for viral video content.
    Combines AI evaluation with hardcoded viral science rules.
    """
    
    # Weights for each criterion (must sum to 1.0)
    WEIGHTS = {
        "hook_power": 0.20,
        "value_delivery": 0.25,
        "emotional_trigger": 0.15,
        "shareability": 0.15,
        "believability": 0.10,
        "pacing_flow": 0.10,
        "cta_effectiveness": 0.05
    }
    
    # Hardcoded requirements for 10/10
    PERFECT_REQUIREMENTS = [
        ("pattern_interrupt", ["stop", "wait", "don't", "?"], "Hook needs pattern interrupt"),
        ("specific_numbers", None, "Needs specific, actionable numbers"),  # Check with regex
        ("promise_delivered", None, "Must deliver what hook promises"),  # AI checks this
        ("memorable_numbers", None, "Use round numbers ($500, 90%, 30 days)"),
        ("human_voice", None, "Must sound human, not AI"),  # AI checks
        ("urgency_fomo", ["now", "today", "before", "hurry", "limited", "last"], "Create urgency/FOMO"),
        ("engaging_cta", ["comment", "tell me", "what do you think", "share", "?"], "CTA must drive comments"),
        ("complete_content", None, "Content must feel complete, not cut off")
    ]
    
    def __init__(self):
        self.history = self._load_history()
        self.ai_available = self._check_ai()
    
    def _load_history(self) -> Dict:
        """Load evaluation history."""
        history_file = STATE_DIR / "master_history.json"
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"evaluations": [], "avg_score": 0, "best_score": 0}
    
    def _save_history(self, evaluation: Dict):
        """Save evaluation to history."""
        self.history["evaluations"].append({
            "score": evaluation.get("final_score", 0),
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 100
        self.history["evaluations"] = self.history["evaluations"][-100:]
        
        # Update stats
        scores = [e["score"] for e in self.history["evaluations"]]
        self.history["avg_score"] = sum(scores) / len(scores) if scores else 0
        self.history["best_score"] = max(scores) if scores else 0
        
        history_file = STATE_DIR / "master_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _check_ai(self) -> bool:
        """Check if AI is available."""
        return any([
            os.environ.get("GROQ_API_KEY"),
            os.environ.get("GEMINI_API_KEY"),
            os.environ.get("OPENROUTER_API_KEY")
        ])
    
    def evaluate(self, content: Dict) -> Dict:
        """
        Perform master evaluation of content.
        
        Args:
            content: Dict with hook, phrases, cta, topic, category
        
        Returns:
            Comprehensive evaluation with scores and improvements
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        topic = content.get("topic", "")
        category = content.get("category", "")
        
        # Phase 1: Hardcoded checks (instant, no AI needed)
        hardcoded_result = self._hardcoded_checks(hook, phrases, cta)
        
        # Phase 2: AI evaluation (if available)
        if self.ai_available:
            ai_result = self._ai_evaluation(hook, phrases, cta, topic, category)
            if ai_result:
                # Combine results
                result = self._combine_results(hardcoded_result, ai_result)
            else:
                # AI failed, use hardcoded only
                result = hardcoded_result
        else:
            result = hardcoded_result
        
        # Save to history
        self._save_history(result)
        
        return result
    
    def _hardcoded_checks(self, hook: str, phrases: List[str], cta: str) -> Dict:
        """Run hardcoded viral science checks."""
        missing = []
        score_cap = 10
        
        all_text = f"{hook} {' '.join(phrases)} {cta}".lower()
        
        # 1. Pattern interrupt in hook
        if not any(word in hook.lower() for word in ["stop", "wait", "don't", "?"]):
            missing.append("Hook lacks pattern interrupt (STOP, WAIT, ?) ")
            score_cap = min(score_cap, 9)
        
        # 2. Specific numbers
        numbers = re.findall(r'\$?\d+[\d,]*%?', all_text)
        if len(numbers) < 2:
            missing.append("Needs more specific numbers (at least 2)")
            score_cap = min(score_cap, 9)
        
        # 3. Memorable/round numbers check
        has_weird_number = any(re.search(r'\d{4,}(?!\s*%)', n) for n in numbers if n)
        if has_weird_number:
            missing.append("Avoid random numbers like 1847 - use round numbers")
            score_cap = min(score_cap, 9)
        
        # 4. Urgency/FOMO
        urgency_words = ["now", "today", "immediately", "before", "hurry", "limited", "last chance"]
        if not any(word in all_text for word in urgency_words):
            missing.append("Add urgency (today, now, before it's too late)")
            score_cap = min(score_cap, 9)
        
        # 5. Engaging CTA
        cta_words = ["comment", "tell me", "what do you think", "share", "?"]
        if not any(word in cta.lower() for word in cta_words):
            missing.append("CTA needs question to drive comments")
            score_cap = min(score_cap, 9)
        
        # 6. Content completeness (word count)
        total_words = len(all_text.split())
        if total_words < 80:
            missing.append(f"Content too short ({total_words} words) - feels incomplete")
            score_cap = min(score_cap, 8)
        
        # 7. Phrase count
        if len(phrases) < 5:
            missing.append(f"Only {len(phrases)} phrases - needs more value points")
            score_cap = min(score_cap, 8)
        
        # Calculate hardcoded score
        base_score = 10 - len(missing)
        base_score = max(4, min(10, base_score))  # Clamp to 4-10
        
        return {
            "hardcoded_score": base_score,
            "missing_requirements": missing,
            "score_cap": score_cap,
            "checks_passed": 7 - len(missing),
            "checks_total": 7
        }
    
    def _ai_evaluation(self, hook: str, phrases: List[str], cta: str, 
                       topic: str, category: str) -> Optional[Dict]:
        """Get AI evaluation using the master prompt."""
        try:
            # Build the prompt
            prompt = MASTER_EVALUATION_PROMPT.format(
                hook=hook,
                phrases="\n".join([f"- {p}" for p in phrases]),
                cta=cta,
                topic=topic,
                category=category
            )
            
            # Try Groq first (primary)
            result = self._call_groq(prompt)
            if result:
                return result
            
            # Try Gemini as fallback
            result = self._call_gemini(prompt)
            if result:
                return result
            
            return None
        except Exception as e:
            safe_print(f"[!] AI evaluation failed: {e}")
            return None
    
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
                    "temperature": 0.7,
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
        
        v17.9.36: Now uses centralized smart_call_ai to respect rate limits.
        """
        # v17.9.36: Use centralized rate-limited caller if available
        if SMART_CALLER_AVAILABLE and smart_call_ai:
            try:
                result = smart_call_ai(prompt, hint="evaluation", max_tokens=1500)
                if result:
                    return self._parse_json(result)
                return None
            except Exception as e:
                safe_print(f"[!] Smart AI call failed: {e}")
                return None
        
        # Fallback to direct call with manual delay
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
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json(text)
            elif response.status_code == 429:
                safe_print("[!] Gemini 429 - rate limited")
            return None
        except Exception as e:
            safe_print(f"[!] Gemini call failed: {e}")
            return None
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        try:
            # Find JSON in response
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            return None
        except:
            return None
    
    def _combine_results(self, hardcoded: Dict, ai: Dict) -> Dict:
        """Combine hardcoded and AI results."""
        # Calculate weighted AI score
        scores = ai.get("scores", {})
        weighted = sum(
            scores.get(k, 5) * v 
            for k, v in self.WEIGHTS.items()
        )
        
        # Apply hardcoded cap
        final_score = min(
            weighted,
            hardcoded.get("score_cap", 10),
            ai.get("final_score", 10)
        )
        
        # Combine missing requirements
        all_missing = list(set(
            hardcoded.get("missing_requirements", []) + 
            ai.get("missing_requirements", [])
        ))
        
        return {
            "final_score": round(final_score, 1),
            "ai_weighted_score": round(weighted, 1),
            "hardcoded_cap": hardcoded.get("score_cap", 10),
            "scores": scores,
            "missing_requirements": all_missing,
            "would_go_viral": ai.get("would_go_viral", False),
            "strongest_element": ai.get("strongest_element", "Unknown"),
            "weakest_element": ai.get("weakest_element", "Unknown"),
            "specific_improvements": ai.get("specific_improvements", []),
            "rewritten_hook": ai.get("rewritten_hook", ""),
            "verdict": ai.get("verdict", self._get_verdict(final_score)),
            "checks_passed": hardcoded.get("checks_passed", 0),
            "checks_total": hardcoded.get("checks_total", 7)
        }
    
    def _get_verdict(self, score: float) -> str:
        """Get verdict based on score."""
        if score >= 9:
            return "VIRAL_GUARANTEED"
        elif score >= 8:
            return "VIRAL_LIKELY"
        elif score >= 6:
            return "NEEDS_WORK"
        else:
            return "WILL_FLOP"
    
    def get_tips_for_10(self) -> List[str]:
        """Get tips for achieving a perfect 10/10 score."""
        return [
            "START WITH A BANG: Use 'STOP', 'WAIT', or a shocking question",
            "BE SPECIFIC: Replace 'make money' with 'earn $500/week'",
            "USE ROUND NUMBERS: $500, 90%, 30 days - not $487, 93.2%",
            "CREATE URGENCY: 'before it's too late', 'starting today'",
            "DELIVER VALUE: At least 3 concrete, actionable tips",
            "END WITH A QUESTION: 'What's YOUR biggest challenge?'",
            "COMPLETE THE STORY: Don't leave viewers hanging",
            "SOUND HUMAN: Use contractions (don't, can't, won't)",
            "TRIGGER EMOTION: Curiosity, FOMO, Shock, or Awe",
            "KEEP IT PUNCHY: 8-15 words per phrase, 80-150 total"
        ]


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

_master_evaluator = None


def get_master_evaluator() -> MasterEvaluator:
    """Get singleton evaluator."""
    global _master_evaluator
    if _master_evaluator is None:
        _master_evaluator = MasterEvaluator()
    return _master_evaluator


def evaluate_content(content: Dict) -> Dict:
    """Convenience function for evaluation."""
    return get_master_evaluator().evaluate(content)


def get_tips_for_10() -> List[str]:
    """Get tips for achieving 10/10."""
    return get_master_evaluator().get_tips_for_10()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("MASTER EVALUATOR TEST")
    safe_print("=" * 60)
    
    evaluator = get_master_evaluator()
    
    # Test content
    test_content = {
        "hook": "STOP - This $500/week side hustle changed my life",
        "phrases": [
            "Most people think making extra money is hard.",
            "But I found a method that takes just 2 hours a day.",
            "First, you need to identify your valuable skill.",
            "Second, create a simple offer on freelance platforms.",
            "Third, start small and scale when you get reviews.",
            "I went from $0 to $2,000/month in 90 days.",
            "And you can start today with zero investment."
        ],
        "cta": "What skill would YOU monetize? Comment below!",
        "topic": "side hustle strategies",
        "category": "money"
    }
    
    result = evaluator.evaluate(test_content)
    
    safe_print(f"\nFINAL SCORE: {result.get('final_score', 'N/A')}/10")
    safe_print(f"Verdict: {result.get('verdict', 'N/A')}")
    safe_print(f"Would go viral: {result.get('would_go_viral', 'N/A')}")
    
    if result.get("scores"):
        safe_print("\nComponent Scores:")
        for name, score in result.get("scores", {}).items():
            safe_print(f"  {name}: {score}/10")
    
    safe_print(f"\nHardcoded checks: {result.get('checks_passed', 0)}/{result.get('checks_total', 7)}")
    
    if result.get("missing_requirements"):
        safe_print("\nMissing for 10/10:")
        for req in result.get("missing_requirements", []):
            safe_print(f"  - {req}")
    
    if result.get("specific_improvements"):
        safe_print("\nSpecific improvements:")
        for imp in result.get("specific_improvements", [])[:3]:
            safe_print(f"  - {imp}")
    
    if result.get("rewritten_hook"):
        safe_print(f"\nSuggested hook: {result.get('rewritten_hook')}")
    
    safe_print("\n" + "=" * 60)
    safe_print("TIPS FOR 10/10:")
    for tip in evaluator.get_tips_for_10()[:5]:
        safe_print(f"  - {tip}")
    safe_print("=" * 60)

