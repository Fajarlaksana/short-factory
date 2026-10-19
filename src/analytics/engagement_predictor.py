#!/usr/bin/env python3
"""
ViralShorts Factory - Engagement Rate Predictor v17.8
======================================================

Predicts engagement rates (likes, comments, shares) based on content.

Engagement factors:
- Hook questions (drive comments)
- Controversy (drive shares)
- CTA clarity (drive likes)
- Value delivery (drive saves)
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

ENGAGEMENT_FILE = STATE_DIR / "engagement_patterns.json"


class EngagementPredictor:
    """
    v17.9.16: Predicts engagement rates for video content.
    
    Now uses HYBRID approach:
    - Baseline triggers (algorithm patterns)
    - Learned triggers from analytics
    - AI-discovered triggers (periodically refreshed)
    """
    
    # v17.9.16: Minimal baseline patterns (algorithm will look for these)
    # Extended dynamically by learned patterns from self_learning_engine
    _BASELINE_COMMENT = ["comment", "tell me", "what do you think", "?"]
    _BASELINE_SHARE = ["share this", "tag someone", "send this to"]
    _BASELINE_LIKE = ["like if", "if you agree"]
    _BASELINE_SAVE = ["save this", "bookmark", "how to"]
    
    def __init__(self):
        self.data = self._load()
        
        # v17.9.16: Initialize triggers with baseline + learned
        self._init_dynamic_triggers()
    
    def _init_dynamic_triggers(self):
        """Initialize triggers from baseline + learned patterns."""
        # Start with baseline
        self.COMMENT_TRIGGERS = list(self._BASELINE_COMMENT)
        self.SHARE_TRIGGERS = list(self._BASELINE_SHARE)
        self.LIKE_TRIGGERS = list(self._BASELINE_LIKE)
        self.SAVE_TRIGGERS = list(self._BASELINE_SAVE)
        
        # Try to extend with learned patterns
        try:
            from self_learning_engine import get_learning_engine
            engine = get_learning_engine()
            triggers = engine.get_viral_triggers()
            
            if triggers.get("source") != "none_available":
                # Extend with learned engagement triggers
                engagement = triggers.get("engagement_triggers", [])
                for t in engagement:
                    t_lower = t.lower()
                    if "comment" in t_lower and t_lower not in self.COMMENT_TRIGGERS:
                        self.COMMENT_TRIGGERS.append(t_lower)
                    elif "share" in t_lower or "tag" in t_lower:
                        if t_lower not in self.SHARE_TRIGGERS:
                            self.SHARE_TRIGGERS.append(t_lower)
                    elif "like" in t_lower:
                        if t_lower not in self.LIKE_TRIGGERS:
                            self.LIKE_TRIGGERS.append(t_lower)
                    elif "save" in t_lower:
                        if t_lower not in self.SAVE_TRIGGERS:
                            self.SAVE_TRIGGERS.append(t_lower)
        except:
            pass  # Use baseline only
    
    def _load(self) -> Dict:
        try:
            if ENGAGEMENT_FILE.exists():
                with open(ENGAGEMENT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "patterns": {},
            "historical": [],
            "best_ctas": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(ENGAGEMENT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def predict_engagement(self, content: Dict) -> Dict:
        """
        Predict engagement rates for content.
        
        Args:
            content: Dict with hook, phrases, cta, category
        
        Returns:
            Dict with predicted rates and recommendations
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        category = content.get("category", "general")
        
        # Combine all text
        all_text = f"{hook} {' '.join(phrases)} {cta}".lower()
        
        # Score each engagement type
        comment_score = self._score_comment_potential(all_text, cta)
        like_score = self._score_like_potential(all_text, cta)
        share_score = self._score_share_potential(all_text, cta)
        save_score = self._score_save_potential(all_text, phrases)
        
        # Overall engagement
        overall = (comment_score + like_score + share_score + save_score) / 4
        
        return {
            "overall_engagement": round(overall, 1),
            "comment_rate": round(comment_score / 10, 2),  # As percentage
            "like_rate": round(like_score / 10, 2),
            "share_rate": round(share_score / 10, 2),
            "save_rate": round(save_score / 10, 2),
            "predicted_engagement_rate": round(overall / 10, 2),
            "strongest": self._get_strongest(comment_score, like_score, share_score, save_score),
            "weakest": self._get_weakest(comment_score, like_score, share_score, save_score),
            "recommendations": self._get_recommendations(
                comment_score, like_score, share_score, save_score
            )
        }
    
    def _score_comment_potential(self, text: str, cta: str) -> float:
        """Score comment potential (0-100)."""
        score = 30  # Base
        
        # Question marks
        score += text.count("?") * 15
        
        # Comment triggers
        for trigger in self.COMMENT_TRIGGERS:
            if trigger in text:
                score += 10
        
        # Controversy indicators
        if any(w in text for w in ["wrong", "truth", "lie", "unpopular"]):
            score += 15
        
        return min(100, score)
    
    def _score_like_potential(self, text: str, cta: str) -> float:
        """Score like potential (0-100)."""
        score = 40  # Base (easier to get likes)
        
        # Like triggers
        for trigger in self.LIKE_TRIGGERS:
            if trigger in text:
                score += 15
        
        # Value indicators
        if any(w in text for w in ["tip", "hack", "secret", "trick", "easy"]):
            score += 10
        
        return min(100, score)
    
    def _score_share_potential(self, text: str, cta: str) -> float:
        """Score share potential (0-100)."""
        score = 20  # Base (hardest to get)
        
        # Share triggers
        for trigger in self.SHARE_TRIGGERS:
            if trigger in text:
                score += 15
        
        # Viral indicators
        if any(w in text for w in ["everyone", "mind-blowing", "shocking", "unbelievable"]):
            score += 15
        
        # Social proof
        if any(w in text for w in ["millions", "viral", "trending", "famous"]):
            score += 10
        
        return min(100, score)
    
    def _score_save_potential(self, text: str, phrases: List[str]) -> float:
        """Score save potential (0-100)."""
        score = 25  # Base
        
        # Save triggers
        for trigger in self.SAVE_TRIGGERS:
            if trigger in text:
                score += 15
        
        # List/step format
        if len(phrases) >= 3:
            score += 15
        
        # Actionable content
        if any(w in text for w in ["step", "how to", "guide", "tips", "ways"]):
            score += 15
        
        return min(100, score)
    
    def _get_strongest(self, comment: float, like: float, 
                      share: float, save: float) -> str:
        """Get strongest engagement type."""
        scores = {"comments": comment, "likes": like, "shares": share, "saves": save}
        return max(scores, key=scores.get)
    
    def _get_weakest(self, comment: float, like: float,
                    share: float, save: float) -> str:
        """Get weakest engagement type."""
        scores = {"comments": comment, "likes": like, "shares": share, "saves": save}
        return min(scores, key=scores.get)
    
    def _get_recommendations(self, comment: float, like: float,
                            share: float, save: float) -> List[str]:
        """Get engagement improvement recommendations."""
        recs = []
        
        if comment < 50:
            recs.append("Add a question to boost comments (What do you think?)")
        
        if like < 50:
            recs.append("Add value statement to boost likes (Like if this helped!)")
        
        if share < 40:
            recs.append("Add share trigger (Share with someone who needs this)")
        
        if save < 40:
            recs.append("Format as steps/tips to boost saves")
        
        if not recs:
            recs.append("Engagement triggers look good!")
        
        return recs
    
    def record_actual_engagement(self, content_id: str, 
                                predicted: Dict, actual: Dict):
        """Record actual engagement for learning."""
        self.data["historical"].append({
            "id": content_id,
            "predicted": predicted,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 100
        self.data["historical"] = self.data["historical"][-100:]
        self._save()
    
    def get_best_ctas_for_engagement(self, target: str = "comments") -> List[str]:
        """Get CTAs that drive specific engagement."""
        ctas = {
            "comments": [
                "What do you think? Comment below!",
                "Is this true for you? Tell me!",
                "Share your experience in the comments!",
                "Agree or disagree? Let me know!"
            ],
            "likes": [
                "Like if this helped you!",
                "Double tap if you agree!",
                "Smash that like button!"
            ],
            "shares": [
                "Share this with someone who needs it!",
                "Tag a friend who should see this!",
                "Send this to someone!"
            ],
            "saves": [
                "Save this for later!",
                "Bookmark these steps!",
                "Come back to this when you need it!"
            ]
        }
        
        return ctas.get(target, ctas["comments"])


# Singleton
_engagement_predictor = None


def get_engagement_predictor() -> EngagementPredictor:
    """Get singleton predictor."""
    global _engagement_predictor
    if _engagement_predictor is None:
        _engagement_predictor = EngagementPredictor()
    return _engagement_predictor


def predict_engagement(content: Dict) -> Dict:
    """Convenience function."""
    return get_engagement_predictor().predict_engagement(content)


if __name__ == "__main__":
    # Test
    safe_print("Testing Engagement Predictor...")
    
    predictor = get_engagement_predictor()
    
    # Test content
    content = {
        "hook": "Why do successful people wake up at 5 AM?",
        "phrases": [
            "Here are 3 reasons that will change your perspective.",
            "First, they get focused work time before distractions.",
            "Second, morning routines build discipline.",
            "Third, early wins create momentum for the day.",
        ],
        "cta": "What time do YOU wake up? Comment below!",
        "category": "productivity"
    }
    
    result = predictor.predict_engagement(content)
    
    safe_print(f"\nEngagement Prediction:")
    safe_print("-" * 40)
    safe_print(f"Overall Score: {result['overall_engagement']}/100")
    safe_print(f"Predicted Engagement Rate: {result['predicted_engagement_rate']}%")
    safe_print(f"\nBy Type (score out of 10):")
    safe_print(f"  Comments: {result['comment_rate']}")
    safe_print(f"  Likes: {result['like_rate']}")
    safe_print(f"  Shares: {result['share_rate']}")
    safe_print(f"  Saves: {result['save_rate']}")
    safe_print(f"\nStrongest: {result['strongest']}")
    safe_print(f"Weakest: {result['weakest']}")
    safe_print(f"\nRecommendations:")
    for rec in result['recommendations']:
        safe_print(f"  - {rec}")
    safe_print("-" * 40)
    
    # Get best CTAs
    best_ctas = predictor.get_best_ctas_for_engagement("comments")
    safe_print(f"\nBest CTAs for Comments:")
    for cta in best_ctas[:2]:
        safe_print(f"  - {cta}")
    
    safe_print("\nTest complete!")

