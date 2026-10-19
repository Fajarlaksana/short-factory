#!/usr/bin/env python3
"""
ViralShorts Factory - Retention Curve Predictor v17.8
======================================================

Predicts viewer retention curves based on content analysis.

Key retention factors:
- Hook strength (first 3 seconds)
- Pacing and information density
- Visual variety
- Open loops and curiosity gaps
- Payoff timing
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

RETENTION_FILE = STATE_DIR / "retention_patterns.json"


class RetentionPredictor:
    """
    Predicts viewer retention curves for video content.
    """
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if RETENTION_FILE.exists():
                with open(RETENTION_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "patterns": {},
            "retention_factors": {},
            "historical": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(RETENTION_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def predict_retention(self, content: Dict) -> Dict:
        """
        Predict retention curve for content.
        
        Args:
            content: Dict with hook, phrases, cta, category
        
        Returns:
            Dict with predicted retention curve and recommendations
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        category = content.get("category", "general")
        
        # Analyze content factors
        hook_score = self._score_hook(hook)
        pacing_score = self._score_pacing(phrases)
        structure_score = self._score_structure(hook, phrases, cta)
        
        # Overall retention prediction
        overall = (hook_score + pacing_score + structure_score) / 3
        
        # Predict drop-off points
        drop_points = self._predict_drop_points(hook, phrases)
        
        # Generate retention curve (simplified)
        curve = self._generate_curve(hook_score, pacing_score, structure_score, len(phrases))
        
        return {
            "overall_retention": round(overall, 1),
            "hook_score": hook_score,
            "pacing_score": pacing_score,
            "structure_score": structure_score,
            "predicted_curve": curve,
            "drop_off_risks": drop_points,
            "recommendations": self._get_recommendations(
                hook_score, pacing_score, structure_score
            )
        }
    
    def _score_hook(self, hook: str) -> float:
        """Score hook strength (0-100)."""
        score = 50  # Base
        
        hook_lower = hook.lower()
        
        # Pattern interrupt words (+15)
        if any(w in hook_lower for w in ["stop", "wait", "hold on"]):
            score += 15
        
        # Questions (+10)
        if "?" in hook:
            score += 10
        
        # Numbers (+10)
        if re.search(r'\d', hook):
            score += 10
        
        # Short and punchy (+10)
        if len(hook.split()) <= 8:
            score += 10
        
        # Curiosity triggers (+10)
        if any(w in hook_lower for w in ["secret", "truth", "why", "how"]):
            score += 10
        
        # Shock/controversy (+5)
        if any(w in hook_lower for w in ["shocking", "unbelievable", "wrong"]):
            score += 5
        
        return min(100, score)
    
    def _score_pacing(self, phrases: List[str]) -> float:
        """Score pacing and information density (0-100)."""
        if not phrases:
            return 50
        
        score = 60  # Base
        
        # Ideal phrase count: 3-5
        if 3 <= len(phrases) <= 5:
            score += 15
        elif len(phrases) > 7:
            score -= 15
        
        # Average word count per phrase (ideal: 8-15 words)
        avg_words = sum(len(p.split()) for p in phrases) / len(phrases)
        if 8 <= avg_words <= 15:
            score += 15
        elif avg_words > 20:
            score -= 10
        
        # Variety in phrase length
        lengths = [len(p.split()) for p in phrases]
        variance = max(lengths) - min(lengths) if lengths else 0
        if variance >= 3:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_structure(self, hook: str, phrases: List[str], cta: str) -> float:
        """Score content structure (0-100)."""
        score = 50  # Base
        
        # Has clear hook
        if len(hook) > 10:
            score += 15
        
        # Has CTA
        if len(cta) > 5:
            score += 15
        
        # Has multiple value points
        if len(phrases) >= 3:
            score += 10
        
        # Open loop detection
        all_text = hook + " " + " ".join(phrases)
        if any(w in all_text.lower() for w in ["later", "coming up", "wait for it"]):
            score += 10
        
        # Payoff detection
        if any(w in " ".join(phrases[-2:]).lower() for w in ["result", "answer", "secret", "here's"]):
            score += 10
        
        return min(100, score)
    
    def _predict_drop_points(self, hook: str, phrases: List[str]) -> List[Dict]:
        """Predict where viewers might drop off."""
        risks = []
        
        # Hook risk
        if len(hook) < 5:
            risks.append({
                "position": "start",
                "risk": "high",
                "reason": "Weak or missing hook"
            })
        
        # Mid-content risk
        if len(phrases) > 5:
            risks.append({
                "position": "middle",
                "risk": "medium",
                "reason": "Too many phrases may lose attention"
            })
        
        # Check for low-value phrases
        for i, phrase in enumerate(phrases):
            if len(phrase.split()) > 25:
                risks.append({
                    "position": f"phrase_{i+1}",
                    "risk": "medium",
                    "reason": f"Phrase {i+1} is too long"
                })
        
        return risks
    
    def _generate_curve(self, hook_score: float, pacing_score: float,
                       structure_score: float, phrase_count: int) -> List[Dict]:
        """Generate simplified retention curve."""
        curve = []
        
        # Start at 100%
        current = 100
        
        # First 3 seconds (hook impact)
        hook_impact = hook_score / 100 * 0.3  # 0-30% retention
        current -= (30 - hook_impact * 100)
        curve.append({"time": 3, "retention": round(max(50, current), 1)})
        
        # Middle (pacing impact)
        mid_impact = pacing_score / 100 * 0.2
        current -= (20 - mid_impact * 100)
        curve.append({"time": 15, "retention": round(max(40, current), 1)})
        
        # End (structure impact)
        end_impact = structure_score / 100 * 0.1
        current -= (10 - end_impact * 100)
        curve.append({"time": 30, "retention": round(max(30, current), 1)})
        
        return curve
    
    def _get_recommendations(self, hook_score: float, pacing_score: float,
                            structure_score: float) -> List[str]:
        """Get improvement recommendations."""
        recs = []
        
        if hook_score < 70:
            recs.append("Strengthen hook with pattern interrupt (STOP, WAIT) or question")
        
        if pacing_score < 70:
            recs.append("Adjust pacing: aim for 8-10 phrases, 8-15 words each")
        
        if structure_score < 70:
            recs.append("Add clear CTA and ensure payoff delivers value")
        
        if not recs:
            recs.append("Content structure looks good!")
        
        return recs
    
    def record_actual_retention(self, content_id: str, content: Dict, 
                               actual_retention: float):
        """Record actual retention for learning."""
        self.data["historical"].append({
            "id": content_id,
            "predicted": self.predict_retention(content)["overall_retention"],
            "actual": actual_retention,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 100 records
        self.data["historical"] = self.data["historical"][-100:]
        self._save()
    
    def get_prediction_accuracy(self) -> Dict:
        """Get prediction accuracy stats."""
        if len(self.data["historical"]) < 5:
            return {"error": "Not enough data (need 5+ records)"}
        
        errors = []
        for record in self.data["historical"]:
            pred = record.get("predicted", 50)
            actual = record.get("actual", 50)
            errors.append(abs(pred - actual))
        
        avg_error = sum(errors) / len(errors)
        
        return {
            "sample_size": len(errors),
            "average_error": round(avg_error, 2),
            "accuracy": round(100 - avg_error, 1)
        }


# Singleton
_retention_predictor = None


def get_retention_predictor() -> RetentionPredictor:
    """Get singleton predictor."""
    global _retention_predictor
    if _retention_predictor is None:
        _retention_predictor = RetentionPredictor()
    return _retention_predictor


def predict_retention(content: Dict) -> Dict:
    """Convenience function."""
    return get_retention_predictor().predict_retention(content)


if __name__ == "__main__":
    # Test
    safe_print("Testing Retention Predictor...")
    
    predictor = get_retention_predictor()
    
    # Test content
    content = {
        "hook": "STOP - This will change how you see money forever",
        "phrases": [
            "Most people work for money their whole life.",
            "But wealthy people do something different.",
            "They make money work for THEM.",
            "Here's how you can start today.",
            "Invest just $100 per month consistently."
        ],
        "cta": "Comment your investment goal!",
        "category": "money"
    }
    
    result = predictor.predict_retention(content)
    
    safe_print(f"\nRetention Prediction:")
    safe_print("-" * 40)
    safe_print(f"Overall Retention: {result['overall_retention']}%")
    safe_print(f"Hook Score: {result['hook_score']}")
    safe_print(f"Pacing Score: {result['pacing_score']}")
    safe_print(f"Structure Score: {result['structure_score']}")
    safe_print(f"\nPredicted Curve:")
    for point in result['predicted_curve']:
        safe_print(f"  {point['time']}s: {point['retention']}%")
    safe_print(f"\nDrop-off Risks:")
    for risk in result['drop_off_risks']:
        safe_print(f"  {risk['position']}: {risk['risk']} - {risk['reason']}")
    safe_print(f"\nRecommendations:")
    for rec in result['recommendations']:
        safe_print(f"  - {rec}")
    safe_print("-" * 40)
    
    safe_print("\nTest complete!")

