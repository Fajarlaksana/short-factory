#!/usr/bin/env python3
"""
ViralShorts Factory - Engagement Predictor v17.9.51
====================================================

Predicts video performance BEFORE upload using:
- Title analysis
- Hook strength scoring
- Category performance history
- Thumbnail quality assessment
- Trend alignment scoring

This allows:
- Pre-upload optimization
- A/B testing decisions
- Quality gates before publishing
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from src.ai.smart_ai_caller import smart_call_ai
except ImportError:
    smart_call_ai = None


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_FILE = STATE_DIR / "engagement_predictions.json"
VARIETY_FILE = STATE_DIR / "variety_state.json"


class EngagementPredictor:
    """
    Predicts engagement metrics before upload.
    """
    
    # Power words that increase engagement
    POWER_WORDS = {
        "high_impact": ["secret", "truth", "never", "always", "why", "how", 
                       "shocking", "proven", "instant", "free", "new"],
        "curiosity": ["revealed", "hidden", "unknown", "surprising", "strange",
                     "weird", "mysterious", "discover", "uncover"],
        "urgency": ["now", "today", "immediately", "urgent", "warning", "stop",
                   "before", "quickly", "hurry", "limited"],
        "emotion": ["love", "hate", "fear", "amazing", "incredible", "insane",
                   "mind-blowing", "heartbreaking", "inspiring"]
    }
    
    # Category baseline engagement (views per 1000 impressions)
    CATEGORY_BASELINES = {
        "psychology": 45,
        "money": 50,
        "productivity": 40,
        "technology": 38,
        "health": 42,
        "motivation": 35,
        "entertainment": 55,
        "relationships": 48,
        "education": 32,
        "science": 30
    }
    
    def __init__(self):
        self.data = self._load()
        self.variety_state = self._load_variety_state()
    
    def _load(self) -> Dict:
        try:
            if PREDICTIONS_FILE.exists():
                with open(PREDICTIONS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "predictions": [],
            "accuracy_tracking": {},
            "last_updated": None
        }
    
    def _load_variety_state(self) -> Dict:
        try:
            if VARIETY_FILE.exists():
                with open(VARIETY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(PREDICTIONS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def predict_engagement(self, title: str, hook: str, category: str,
                           description: str = "", thumbnail_score: float = None) -> Dict:
        """
        Predict engagement for a video before upload.
        
        Returns:
            Dict with predicted metrics and recommendations
        """
        # Analyze each component
        title_score = self._analyze_title(title)
        hook_score = self._analyze_hook(hook)
        category_score = self._analyze_category(category)
        
        # Thumbnail score (if provided)
        if thumbnail_score is None:
            thumbnail_score = 7.0  # Default
        
        # Calculate overall prediction
        weights = {
            "title": 0.25,
            "hook": 0.35,
            "category": 0.20,
            "thumbnail": 0.20
        }
        
        overall_score = (
            title_score["score"] * weights["title"] +
            hook_score["score"] * weights["hook"] +
            category_score["score"] * weights["category"] +
            thumbnail_score * weights["thumbnail"]
        )
        
        # Convert to predicted metrics
        predicted_views = self._score_to_views(overall_score, category)
        predicted_engagement = self._score_to_engagement(overall_score)
        
        prediction = {
            "overall_score": round(overall_score, 1),
            "grade": self._score_to_grade(overall_score),
            "predicted_views_24h": predicted_views,
            "predicted_engagement_rate": round(predicted_engagement, 1),
            "components": {
                "title": title_score,
                "hook": hook_score,
                "category": category_score,
                "thumbnail": {"score": thumbnail_score}
            },
            "recommendations": self._generate_recommendations(
                title_score, hook_score, overall_score
            ),
            "should_upload": overall_score >= 6.5,
            "confidence": self._calculate_confidence()
        }
        
        # Record prediction for tracking
        self._record_prediction(title, category, prediction)
        
        return prediction
    
    def _analyze_title(self, title: str) -> Dict:
        """Analyze title for engagement potential."""
        score = 5.0  # Base score
        factors = []
        
        title_lower = title.lower()
        
        # Check power words
        for category, words in self.POWER_WORDS.items():
            matches = [w for w in words if w in title_lower]
            if matches:
                score += len(matches) * 0.5
                factors.append(f"+{len(matches)} {category} words")
        
        # Check length (optimal: 40-60 chars)
        length = len(title)
        if 40 <= length <= 60:
            score += 1.0
            factors.append("Optimal length")
        elif length < 30:
            score -= 0.5
            factors.append("Too short")
        elif length > 80:
            score -= 1.0
            factors.append("Too long")
        
        # Check for numbers (increases CTR)
        if any(char.isdigit() for char in title):
            score += 0.8
            factors.append("Contains numbers")
        
        # Check for question (increases engagement)
        if "?" in title:
            score += 0.5
            factors.append("Question format")
        
        # Cap at 10
        score = min(10, max(1, score))
        
        return {
            "score": round(score, 1),
            "factors": factors,
            "text": title[:50] + "..." if len(title) > 50 else title
        }
    
    def _analyze_hook(self, hook: str) -> Dict:
        """Analyze hook for engagement potential."""
        score = 5.0
        factors = []
        
        hook_lower = hook.lower()
        
        # Check for pattern interrupts
        pattern_interrupts = [
            "you won't believe", "wait", "stop", "this is",
            "what if", "the truth", "i found", "secret"
        ]
        for phrase in pattern_interrupts:
            if phrase in hook_lower:
                score += 1.5
                factors.append("Pattern interrupt detected")
                break
        
        # Check for direct address ("you")
        if "you" in hook_lower or "your" in hook_lower:
            score += 0.8
            factors.append("Direct address (you)")
        
        # Check for specificity (numbers, percentages)
        if any(char.isdigit() for char in hook):
            score += 0.7
            factors.append("Specific numbers")
        
        # Check length (optimal: 10-25 words for hooks)
        word_count = len(hook.split())
        if 10 <= word_count <= 25:
            score += 0.5
            factors.append("Good hook length")
        elif word_count < 5:
            score -= 0.5
            factors.append("Hook too short")
        
        # Power words in hook
        power_count = sum(
            1 for words in self.POWER_WORDS.values()
            for w in words if w in hook_lower
        )
        if power_count >= 2:
            score += 1.0
            factors.append(f"{power_count} power words")
        
        score = min(10, max(1, score))
        
        return {
            "score": round(score, 1),
            "factors": factors,
            "text": hook[:50] + "..." if len(hook) > 50 else hook
        }
    
    def _analyze_category(self, category: str) -> Dict:
        """Analyze category performance potential."""
        category_lower = category.lower()
        
        # Get baseline
        baseline = self.CATEGORY_BASELINES.get(category_lower, 35)
        
        # Check learned performance from variety_state
        learned_perf = self.variety_state.get("analytics_insights", {}).get(
            "avg_views_by_category", {}
        )
        
        if category_lower in learned_perf:
            actual_avg = learned_perf[category_lower]
            # Score based on actual performance
            score = min(10, (actual_avg / 100) * 2)
            source = "learned"
        else:
            # Score based on industry baseline
            score = min(10, (baseline / 50) * 5)
            source = "baseline"
        
        # Check if it's a preferred category
        preferred = self.variety_state.get("preferred_categories", [])
        if category_lower in [c.lower() for c in preferred]:
            score += 0.5
        
        return {
            "score": round(score, 1),
            "baseline": baseline,
            "source": source,
            "factors": [f"Category baseline: {baseline}/1000 impressions"]
        }
    
    def _score_to_views(self, score: float, category: str) -> int:
        """Convert prediction score to estimated 24h views."""
        # Base views depending on channel size (conservative estimate)
        base_views = 100  # Small channel baseline
        
        # Get category multiplier
        category_mult = self.CATEGORY_BASELINES.get(category.lower(), 35) / 40
        
        # Score multiplier (exponential impact)
        score_mult = (score / 5) ** 1.5
        
        predicted = int(base_views * category_mult * score_mult)
        
        return max(50, predicted)  # Minimum 50 views
    
    def _score_to_engagement(self, score: float) -> float:
        """Convert score to predicted engagement rate (%)."""
        # Engagement rate typically 2-8% for Shorts
        base_rate = 3.0
        rate = base_rate * (score / 5)
        return min(10, max(1, rate))
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 9.0:
            return "A+"
        elif score >= 8.0:
            return "A"
        elif score >= 7.0:
            return "B+"
        elif score >= 6.0:
            return "B"
        elif score >= 5.0:
            return "C"
        elif score >= 4.0:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, title_score: Dict, 
                                   hook_score: Dict, overall: float) -> List[str]:
        """Generate improvement recommendations."""
        recs = []
        
        if title_score["score"] < 7:
            recs.append("Add power words to title (secret, truth, why, how)")
        
        if hook_score["score"] < 7:
            recs.append("Strengthen hook with pattern interrupt technique")
        
        if overall < 6.5:
            recs.append("Consider regenerating content before upload")
        
        if not any("numbers" in str(f).lower() for f in title_score.get("factors", [])):
            recs.append("Add a number to title for higher CTR")
        
        if not recs:
            recs.append("Content looks good! Ready for upload.")
        
        return recs
    
    def _calculate_confidence(self) -> float:
        """Calculate prediction confidence based on historical accuracy."""
        accuracy = self.data.get("accuracy_tracking", {})
        total_predictions = accuracy.get("total", 0)
        
        if total_predictions < 10:
            return 0.6  # Low confidence with little data
        elif total_predictions < 50:
            return 0.7
        else:
            # Calculate from actual accuracy
            correct = accuracy.get("within_50_percent", 0)
            return min(0.95, correct / max(1, total_predictions))
    
    def _record_prediction(self, title: str, category: str, prediction: Dict):
        """Record prediction for later accuracy tracking."""
        record = {
            "title": title[:50],
            "category": category,
            "predicted_score": prediction["overall_score"],
            "predicted_views": prediction["predicted_views_24h"],
            "timestamp": datetime.now().isoformat(),
            "actual_views": None  # Filled in later
        }
        self.data["predictions"].append(record)
        
        # Keep only last 100 predictions
        self.data["predictions"] = self.data["predictions"][-100:]
        self._save()
    
    def record_actual_performance(self, title: str, actual_views: int):
        """Record actual performance to improve accuracy."""
        for pred in reversed(self.data["predictions"]):
            if pred["title"] == title[:50] and pred["actual_views"] is None:
                pred["actual_views"] = actual_views
                
                # Update accuracy tracking
                predicted = pred["predicted_views"]
                accuracy = self.data.get("accuracy_tracking", 
                                         {"total": 0, "within_50_percent": 0})
                accuracy["total"] += 1
                
                # Check if within 50% of actual
                if predicted * 0.5 <= actual_views <= predicted * 1.5:
                    accuracy["within_50_percent"] += 1
                
                self.data["accuracy_tracking"] = accuracy
                self._save()
                
                safe_print(f"[PREDICT] Recorded: predicted {predicted}, actual {actual_views}")
                return
    
    def quick_score(self, title: str, hook: str) -> float:
        """Quick scoring without full analysis."""
        title_score = self._analyze_title(title)["score"]
        hook_score = self._analyze_hook(hook)["score"]
        return round((title_score * 0.4 + hook_score * 0.6), 1)


# Global instance
_predictor = None

def get_predictor() -> EngagementPredictor:
    global _predictor
    if _predictor is None:
        _predictor = EngagementPredictor()
    return _predictor

def predict_video_performance(title: str, hook: str, category: str) -> Dict:
    """Predict video performance before upload."""
    return get_predictor().predict_engagement(title, hook, category)


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("ENGAGEMENT PREDICTOR - TEST")
    safe_print("=" * 60)
    
    predictor = EngagementPredictor()
    
    # Test prediction
    prediction = predictor.predict_engagement(
        title="7 Psychology Secrets That Will Change Your Life",
        hook="You won't believe what 97% of people don't know about their own brain",
        category="psychology"
    )
    
    safe_print(f"\nOverall Score: {prediction['overall_score']}/10 ({prediction['grade']})")
    safe_print(f"Predicted 24h Views: {prediction['predicted_views_24h']}")
    safe_print(f"Engagement Rate: {prediction['predicted_engagement_rate']}%")
    safe_print(f"Should Upload: {prediction['should_upload']}")
    safe_print(f"Confidence: {prediction['confidence']*100:.0f}%")
    
    safe_print("\nRecommendations:")
    for rec in prediction["recommendations"]:
        safe_print(f"  - {rec}")
