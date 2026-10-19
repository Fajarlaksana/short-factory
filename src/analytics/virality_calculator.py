#!/usr/bin/env python3
"""
ViralShorts Factory - Virality Score Calculator v17.8
=======================================================

Calculates a comprehensive virality score for video content.

Virality factors:
- Hook strength (scroll-stop power)
- Shareability (emotional triggers)
- Retention prediction
- Engagement potential
- Trending alignment
- Platform optimization
"""

import os
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

VIRALITY_FILE = STATE_DIR / "virality_scores.json"


class ViralityCalculator:
    """
    v17.9.16: Comprehensive virality score calculator.
    
    Now uses HYBRID approach for pattern detection:
    - Baseline patterns (algorithm fundamentals)
    - Learned patterns from analytics
    """
    
    # Viral elements and their weights
    WEIGHTS = {
        "hook_strength": 0.25,       # First impression
        "shareability": 0.20,        # Will people share?
        "engagement": 0.20,          # Will people interact?
        "retention": 0.15,           # Will people watch till end?
        "trending": 0.10,            # Is topic trending?
        "platform_fit": 0.10         # Optimized for Shorts?
    }
    
    # v17.9.16: Minimal baseline patterns (always checked)
    _BASELINE_INTERRUPT = ["stop", "wait", "hold on"]
    _BASELINE_CURIOSITY = ["secret", "truth", "why", "how", "hidden"]
    
    def __init__(self):
        self.data = self._load()
        
        # v17.9.16: Initialize with baseline + learned
        self._init_dynamic_patterns()
    
    def _load(self) -> Dict:
        try:
            if VIRALITY_FILE.exists():
                with open(VIRALITY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "scores": [],
            "average": 0,
            "best": 0,
            "last_updated": None
        }
    
    def _init_dynamic_patterns(self):
        """v17.9.16: Initialize patterns with baseline + learned."""
        # Start with baseline
        self.pattern_interrupt_words = list(self._BASELINE_INTERRUPT)
        self.curiosity_words = list(self._BASELINE_CURIOSITY)
        
        # Try to extend with learned patterns
        try:
            from self_learning_engine import get_learning_engine
            engine = get_learning_engine()
            triggers = engine.get_viral_triggers()
            
            if triggers.get("source") != "none_available":
                # Extend with learned hook triggers
                for t in triggers.get("hook_triggers", []):
                    t_lower = t.lower()
                    if t_lower not in self.pattern_interrupt_words:
                        self.pattern_interrupt_words.append(t_lower)
                
                # Extend with learned power words
                for w in triggers.get("power_words", []):
                    w_lower = w.lower()
                    if w_lower not in self.curiosity_words:
                        self.curiosity_words.append(w_lower)
        except:
            pass  # Use baseline only
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(VIRALITY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def calculate_virality(self, content: Dict) -> Dict:
        """
        Calculate comprehensive virality score.
        
        Args:
            content: Dict with hook, phrases, cta, category, topic
        
        Returns:
            Dict with overall score, component scores, and grade
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        category = content.get("category", "general")
        topic = content.get("topic", "")
        
        # Calculate component scores
        hook_score = self._score_hook(hook)
        share_score = self._score_shareability(hook, phrases, cta)
        engage_score = self._score_engagement(hook, phrases, cta)
        retain_score = self._score_retention(hook, phrases)
        trend_score = self._score_trending(topic, category)
        platform_score = self._score_platform_fit(hook, phrases, cta)
        
        # Weighted average
        overall = (
            hook_score * self.WEIGHTS["hook_strength"] +
            share_score * self.WEIGHTS["shareability"] +
            engage_score * self.WEIGHTS["engagement"] +
            retain_score * self.WEIGHTS["retention"] +
            trend_score * self.WEIGHTS["trending"] +
            platform_score * self.WEIGHTS["platform_fit"]
        )
        
        # Grade
        grade = self._get_grade(overall)
        
        # Recommendations
        recommendations = self._get_recommendations(
            hook_score, share_score, engage_score, 
            retain_score, trend_score, platform_score
        )
        
        result = {
            "overall_score": round(overall, 1),
            "grade": grade,
            "components": {
                "hook_strength": round(hook_score, 1),
                "shareability": round(share_score, 1),
                "engagement": round(engage_score, 1),
                "retention": round(retain_score, 1),
                "trending": round(trend_score, 1),
                "platform_fit": round(platform_score, 1)
            },
            "recommendations": recommendations,
            "viral_potential": self._get_potential(overall)
        }
        
        # Record for history
        self._record_score(overall)
        
        return result
    
    def _score_hook(self, hook: str) -> float:
        """
        v17.9.16: Score hook strength (0-100).
        Uses DYNAMIC patterns from learning engine.
        """
        if not hook:
            return 20
        
        score = 30
        hook_lower = hook.lower()
        
        # Pattern interrupt - uses dynamic patterns
        if any(w in hook_lower for w in self.pattern_interrupt_words):
            score += 20
        
        # Question
        if "?" in hook:
            score += 15
        
        # Numbers
        if re.search(r'\d', hook):
            score += 15
        
        # Curiosity/power words - uses dynamic patterns
        if any(w in hook_lower for w in self.curiosity_words):
            score += 15
        
        # Short and punchy
        if len(hook.split()) <= 10:
            score += 10
        
        return min(100, score)
    
    def _score_shareability(self, hook: str, phrases: List[str], cta: str) -> float:
        """Score shareability (0-100)."""
        score = 25
        text = f"{hook} {' '.join(phrases)} {cta}".lower()
        
        # Emotional triggers
        if any(w in text for w in ["amazing", "incredible", "unbelievable", "shocking"]):
            score += 20
        
        # Social proof
        if any(w in text for w in ["everyone", "millions", "viral", "most people"]):
            score += 15
        
        # Controversy
        if any(w in text for w in ["truth", "lie", "wrong", "actually"]):
            score += 15
        
        # Share prompts
        if any(w in text for w in ["share", "send this", "tag someone"]):
            score += 15
        
        # Relatability
        if any(w in text for w in ["you", "your", "we all", "everyone knows"]):
            score += 15
        
        return min(100, score)
    
    def _score_engagement(self, hook: str, phrases: List[str], cta: str) -> float:
        """Score engagement potential (0-100)."""
        score = 30
        text = f"{hook} {' '.join(phrases)} {cta}".lower()
        
        # Questions
        score += text.count("?") * 10
        
        # CTA presence
        if any(w in text for w in ["comment", "like", "follow", "save"]):
            score += 20
        
        # Opinion prompts
        if any(w in text for w in ["what do you think", "agree", "disagree", "opinion"]):
            score += 15
        
        # Call to action
        if cta and len(cta) > 5:
            score += 15
        
        return min(100, score)
    
    def _score_retention(self, hook: str, phrases: List[str]) -> float:
        """Score retention potential (0-100)."""
        if not phrases:
            return 30
        
        score = 40
        
        # Good hook
        if len(hook) > 10:
            score += 15
        
        # Optimal phrase count
        if 3 <= len(phrases) <= 5:
            score += 15
        
        # Value delivery
        text = " ".join(phrases).lower()
        if any(w in text for w in ["first", "second", "third", "next", "finally"]):
            score += 15
        
        # Curiosity maintenance
        if any(w in text for w in ["but", "however", "actually", "here's the thing"]):
            score += 10
        
        return min(100, score)
    
    def _score_trending(self, topic: str, category: str) -> float:
        """Score trending alignment (0-100)."""
        score = 40  # Base - most topics are somewhat relevant
        
        # Hot categories
        hot_categories = ["psychology", "money", "productivity", "motivation", "tech"]
        if category.lower() in hot_categories:
            score += 25
        
        # Evergreen topics
        evergreen = ["success", "habits", "mindset", "health", "relationships"]
        if any(e in topic.lower() for e in evergreen):
            score += 20
        
        # Trending signals - use current year dynamically
        from datetime import datetime
        current_year = str(datetime.now().year)
        trending_words = [current_year, "new", "latest", "breaking", "trending", "ai"]
        if any(t in topic.lower() for t in trending_words):
            score += 20
        
        return min(100, score)
    
    def _score_platform_fit(self, hook: str, phrases: List[str], cta: str) -> float:
        """Score YouTube Shorts optimization (0-100)."""
        score = 50
        
        # Short hook (under 10 words)
        if len(hook.split()) <= 10:
            score += 15
        
        # Right phrase count (3-5)
        if 3 <= len(phrases) <= 5:
            score += 15
        
        # Has CTA
        if cta:
            score += 10
        
        # Total content length (ideal: 100-200 words)
        total_words = len(hook.split()) + sum(len(p.split()) for p in phrases)
        if 60 <= total_words <= 150:
            score += 15
        
        return min(100, score)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def _get_potential(self, score: float) -> str:
        """Get viral potential description."""
        if score >= 85:
            return "HIGHLY VIRAL - Strong potential for millions of views"
        elif score >= 70:
            return "VIRAL LIKELY - Good chance of significant reach"
        elif score >= 55:
            return "MODERATE - May get traction with good timing"
        elif score >= 40:
            return "LOW - Needs improvements to go viral"
        else:
            return "POOR - Major improvements needed"
    
    def _get_recommendations(self, hook: float, share: float, engage: float,
                            retain: float, trend: float, platform: float) -> List[str]:
        """Get improvement recommendations."""
        recs = []
        
        # Find weakest areas
        scores = {
            "hook": (hook, "Add pattern interrupt (STOP, WAIT) or question to hook"),
            "shareability": (share, "Add emotional triggers or relatable content"),
            "engagement": (engage, "Add question or clear CTA to boost engagement"),
            "retention": (retain, "Use numbered points and curiosity gaps"),
            "trending": (trend, "Align with trending topics or hot categories"),
            "platform": (platform, "Optimize length: 8-10 phrases, 80-150 words total")
        }
        
        # Get top 3 weakest areas
        sorted_scores = sorted(scores.items(), key=lambda x: x[1][0])
        
        for name, (score, rec) in sorted_scores[:3]:
            if score < 70:
                recs.append(rec)
        
        if not recs:
            recs.append("Content looks great! Minor tweaks could push it higher.")
        
        return recs
    
    def _record_score(self, score: float):
        """Record score for history."""
        self.data["scores"].append({
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 100
        self.data["scores"] = self.data["scores"][-100:]
        
        # Update stats
        if self.data["scores"]:
            all_scores = [s["score"] for s in self.data["scores"]]
            self.data["average"] = sum(all_scores) / len(all_scores)
            self.data["best"] = max(all_scores)
        
        self._save()
    
    def get_stats(self) -> Dict:
        """Get virality stats."""
        return {
            "total_scored": len(self.data["scores"]),
            "average_score": round(self.data.get("average", 0), 1),
            "best_score": round(self.data.get("best", 0), 1)
        }


# Singleton
_virality_calculator = None


def get_virality_calculator() -> ViralityCalculator:
    """Get singleton calculator."""
    global _virality_calculator
    if _virality_calculator is None:
        _virality_calculator = ViralityCalculator()
    return _virality_calculator


def calculate_virality(content: Dict) -> Dict:
    """Convenience function."""
    return get_virality_calculator().calculate_virality(content)


if __name__ == "__main__":
    # Test
    safe_print("Testing Virality Calculator...")
    
    calc = get_virality_calculator()
    
    # Test content
    content = {
        "hook": "STOP - Why do 90% of people fail at this?",
        "phrases": [
            "Here's the truth nobody tells you about success.",
            "First, you need to change your morning routine.",
            "Second, eliminate these three habits immediately.",
            "Third, focus on this one thing every day.",
            "The results will shock you."
        ],
        "cta": "Comment which habit you'll change first!",
        "category": "productivity",
        "topic": "success habits and morning routines"
    }
    
    result = calc.calculate_virality(content)
    
    safe_print(f"\nVirality Analysis:")
    safe_print("=" * 50)
    safe_print(f"OVERALL SCORE: {result['overall_score']}/100 ({result['grade']})")
    safe_print(f"Potential: {result['viral_potential']}")
    safe_print("\nComponent Scores:")
    for name, score in result['components'].items():
        bar = "=" * int(score / 5)
        safe_print(f"  {name:15}: {score:5.1f} |{bar}")
    safe_print("\nRecommendations:")
    for rec in result['recommendations']:
        safe_print(f"  - {rec}")
    safe_print("=" * 50)
    
    # Stats
    stats = calc.get_stats()
    safe_print(f"\nHistory Stats:")
    safe_print(f"  Total scored: {stats['total_scored']}")
    safe_print(f"  Average: {stats['average_score']}")
    safe_print(f"  Best: {stats['best_score']}")
    
    safe_print("\nTest complete!")

