#!/usr/bin/env python3
"""
ViralShorts Factory - Video Script Analyzer v17.8
==================================================

Analyzes video scripts for quality, structure, and improvement opportunities.

Analysis categories:
- Structure (hook, body, CTA)
- Pacing (word count, timing)
- Clarity (readability, complexity)
- Value (information density)
- Entertainment (hooks, surprises)
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

ANALYSIS_FILE = STATE_DIR / "script_analysis.json"


class ScriptAnalyzer:
    """
    Analyzes video scripts for quality and improvement opportunities.
    """
    
    # Ideal metrics for YouTube Shorts
    IDEAL_METRICS = {
        "hook_words": (5, 12),         # Word count
        "phrase_count": (3, 5),         # Number of phrases
        "words_per_phrase": (10, 20),   # Words per phrase
        "total_words": (60, 120),       # Total word count
        "duration_seconds": (15, 45),   # Estimated duration
        "readability_score": (60, 80)   # Flesch reading ease
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if ANALYSIS_FILE.exists():
                with open(ANALYSIS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "analyses": [],
            "patterns": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(ANALYSIS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_script(self, content: Dict) -> Dict:
        """
        Analyze a video script comprehensively.
        
        Args:
            content: Dict with hook, phrases, cta
        
        Returns:
            Dict with analysis results, issues, and suggestions
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        
        # Basic metrics
        metrics = self._calculate_metrics(hook, phrases, cta)
        
        # Structure analysis
        structure = self._analyze_structure(hook, phrases, cta)
        
        # Readability analysis
        readability = self._analyze_readability(hook, phrases, cta)
        
        # Value analysis
        value = self._analyze_value(hook, phrases)
        
        # Issues and suggestions
        issues = self._find_issues(metrics, structure, readability, value)
        suggestions = self._get_suggestions(issues)
        
        # Overall score
        overall = self._calculate_overall(structure, readability, value, len(issues))
        
        return {
            "overall_score": overall,
            "grade": self._get_grade(overall),
            "metrics": metrics,
            "structure": structure,
            "readability": readability,
            "value": value,
            "issues": issues,
            "suggestions": suggestions,
            "estimated_duration": metrics["estimated_duration"],
            "voice_speed_needed": self._calculate_voice_speed(metrics["total_words"])
        }
    
    def _calculate_metrics(self, hook: str, phrases: List[str], cta: str) -> Dict:
        """Calculate basic metrics."""
        hook_words = len(hook.split()) if hook else 0
        phrase_count = len(phrases)
        phrase_word_counts = [len(p.split()) for p in phrases]
        avg_words_per_phrase = sum(phrase_word_counts) / max(1, phrase_count)
        cta_words = len(cta.split()) if cta else 0
        total_words = hook_words + sum(phrase_word_counts) + cta_words
        
        # Estimate duration (assuming ~150 words per minute)
        estimated_duration = total_words / 2.5  # words per second
        
        return {
            "hook_words": hook_words,
            "phrase_count": phrase_count,
            "phrase_word_counts": phrase_word_counts,
            "avg_words_per_phrase": round(avg_words_per_phrase, 1),
            "cta_words": cta_words,
            "total_words": total_words,
            "estimated_duration": round(estimated_duration, 1)
        }
    
    def _analyze_structure(self, hook: str, phrases: List[str], cta: str) -> Dict:
        """Analyze script structure."""
        scores = {
            "hook_present": 1 if hook and len(hook) > 5 else 0,
            "hook_strong": self._is_strong_hook(hook),
            "body_organized": self._is_body_organized(phrases),
            "cta_present": 1 if cta and len(cta) > 3 else 0,
            "cta_clear": self._is_clear_cta(cta)
        }
        
        total = sum(scores.values()) / len(scores) * 100
        
        return {
            "score": round(total, 1),
            "details": scores
        }
    
    def _is_strong_hook(self, hook: str) -> int:
        """Check if hook is strong."""
        if not hook:
            return 0
        
        hook_lower = hook.lower()
        triggers = ["stop", "wait", "?", "secret", "truth", "why", "how"]
        
        return 1 if any(t in hook_lower for t in triggers) else 0
    
    def _is_body_organized(self, phrases: List[str]) -> int:
        """Check if body is organized."""
        if len(phrases) < 2:
            return 0
        
        # Check for numbering or transitions
        text = " ".join(phrases).lower()
        markers = ["first", "second", "third", "next", "then", "finally", "1.", "2.", "3."]
        
        return 1 if any(m in text for m in markers) else 0
    
    def _is_clear_cta(self, cta: str) -> int:
        """Check if CTA is clear."""
        if not cta:
            return 0
        
        cta_lower = cta.lower()
        actions = ["comment", "like", "share", "follow", "subscribe", "save", "try", "start"]
        
        return 1 if any(a in cta_lower for a in actions) else 0
    
    def _analyze_readability(self, hook: str, phrases: List[str], cta: str) -> Dict:
        """Analyze text readability."""
        all_text = f"{hook} {' '.join(phrases)} {cta}"
        
        # Simple readability metrics
        sentences = len(re.findall(r'[.!?]+', all_text)) + 1
        words = len(all_text.split())
        syllables = self._count_syllables(all_text)
        
        # Flesch Reading Ease (simplified)
        if words > 0 and sentences > 0:
            flesch = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
            flesch = max(0, min(100, flesch))
        else:
            flesch = 50
        
        # Average word length
        avg_word_length = len(all_text.replace(" ", "")) / max(1, words)
        
        return {
            "score": round(flesch, 1),
            "level": self._get_reading_level(flesch),
            "avg_word_length": round(avg_word_length, 1),
            "sentence_count": sentences
        }
    
    def _count_syllables(self, text: str) -> int:
        """Rough syllable count."""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        
        for word in text.split():
            word_count = 0
            prev_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_vowel:
                    word_count += 1
                prev_vowel = is_vowel
            count += max(1, word_count)
        
        return count
    
    def _get_reading_level(self, score: float) -> str:
        """Convert Flesch score to reading level."""
        if score >= 90:
            return "Very Easy"
        elif score >= 70:
            return "Easy"
        elif score >= 50:
            return "Moderate"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _analyze_value(self, hook: str, phrases: List[str]) -> Dict:
        """Analyze value delivery."""
        all_text = f"{hook} {' '.join(phrases)}".lower()
        
        # Value indicators
        value_words = ["tip", "trick", "hack", "secret", "learn", "discover",
                       "way", "step", "method", "strategy", "how to", "guide"]
        value_count = sum(1 for w in value_words if w in all_text)
        
        # Actionable content
        action_words = ["do", "try", "start", "stop", "avoid", "use", "make"]
        action_count = sum(1 for w in action_words if w in all_text)
        
        # Numbers (specificity)
        numbers = len(re.findall(r'\d+', all_text))
        
        score = min(100, 30 + value_count * 10 + action_count * 10 + numbers * 10)
        
        return {
            "score": score,
            "value_indicators": value_count,
            "actionable_items": action_count,
            "specificity": numbers
        }
    
    def _find_issues(self, metrics: Dict, structure: Dict, 
                    readability: Dict, value: Dict) -> List[Dict]:
        """Find issues in the script."""
        issues = []
        
        # Metric issues
        if metrics["hook_words"] < self.IDEAL_METRICS["hook_words"][0]:
            issues.append({"type": "structure", "severity": "warning", 
                          "message": "Hook is too short"})
        elif metrics["hook_words"] > self.IDEAL_METRICS["hook_words"][1]:
            issues.append({"type": "structure", "severity": "warning",
                          "message": "Hook is too long"})
        
        if metrics["phrase_count"] < self.IDEAL_METRICS["phrase_count"][0]:
            issues.append({"type": "content", "severity": "warning",
                          "message": "Too few content phrases"})
        elif metrics["phrase_count"] > self.IDEAL_METRICS["phrase_count"][1]:
            issues.append({"type": "pacing", "severity": "info",
                          "message": "Many phrases - ensure fast pacing"})
        
        if metrics["total_words"] > self.IDEAL_METRICS["total_words"][1]:
            issues.append({"type": "length", "severity": "error",
                          "message": "Script may be too long for Shorts"})
        
        # Structure issues
        if structure["details"]["hook_strong"] == 0:
            issues.append({"type": "structure", "severity": "warning",
                          "message": "Hook lacks attention-grabbing elements"})
        
        if structure["details"]["cta_clear"] == 0:
            issues.append({"type": "engagement", "severity": "warning",
                          "message": "CTA is unclear or missing"})
        
        # Readability issues
        if readability["score"] < 50:
            issues.append({"type": "readability", "severity": "warning",
                          "message": "Text may be too complex for quick consumption"})
        
        # Value issues
        if value["score"] < 40:
            issues.append({"type": "value", "severity": "error",
                          "message": "Low value indicators - add actionable content"})
        
        return issues
    
    def _get_suggestions(self, issues: List[Dict]) -> List[str]:
        """Get suggestions based on issues."""
        suggestions = []
        
        suggestion_map = {
            "Hook is too short": "Add pattern interrupt or question to hook",
            "Hook is too long": "Shorten hook to 5-12 words",
            "Too few content phrases": "Add 1-2 more value-packed phrases",
            "Script may be too long": "Cut unnecessary words, aim for 60-120 total",
            "Hook lacks attention-grabbing": "Start with STOP, WAIT, or a question",
            "CTA is unclear": "Add clear action: Comment, Like, Share",
            "Text may be too complex": "Use shorter sentences and simpler words",
            "Low value indicators": "Add specific tips, numbers, or actionable steps"
        }
        
        for issue in issues:
            for key, suggestion in suggestion_map.items():
                if key in issue["message"]:
                    suggestions.append(suggestion)
                    break
        
        if not suggestions:
            suggestions.append("Script looks good! Minor tweaks could help.")
        
        return list(dict.fromkeys(suggestions))  # Remove duplicates
    
    def _calculate_overall(self, structure: Dict, readability: Dict,
                          value: Dict, issue_count: int) -> float:
        """Calculate overall script score."""
        base = (structure["score"] + readability["score"] + value["score"]) / 3
        penalty = issue_count * 5
        
        return max(0, min(100, base - penalty))
    
    def _get_grade(self, score: float) -> str:
        """Convert score to grade."""
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 55:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def _calculate_voice_speed(self, word_count: int, target_duration: int = 30) -> str:
        """Calculate needed voice speed."""
        wpm_needed = (word_count / target_duration) * 60
        
        if wpm_needed < 120:
            return "slow (0.9x)"
        elif wpm_needed < 150:
            return "normal (1.0x)"
        elif wpm_needed < 180:
            return "fast (1.1x)"
        else:
            return "very fast (1.2x) - consider shortening"


# Singleton
_script_analyzer = None


def get_script_analyzer() -> ScriptAnalyzer:
    """Get singleton analyzer."""
    global _script_analyzer
    if _script_analyzer is None:
        _script_analyzer = ScriptAnalyzer()
    return _script_analyzer


def analyze_script(content: Dict) -> Dict:
    """Convenience function."""
    return get_script_analyzer().analyze_script(content)


if __name__ == "__main__":
    # Test
    safe_print("Testing Script Analyzer...")
    
    analyzer = get_script_analyzer()
    
    # Test content
    content = {
        "hook": "STOP - Here's why 90% of people fail",
        "phrases": [
            "Most people start their day wrong.",
            "They check their phone before anything else.",
            "This kills productivity for the entire day.",
            "Instead, try this simple 5-minute routine.",
            "You'll see results within one week."
        ],
        "cta": "Comment if you'll try this tomorrow!"
    }
    
    result = analyzer.analyze_script(content)
    
    safe_print(f"\nScript Analysis:")
    safe_print("=" * 50)
    safe_print(f"OVERALL: {result['overall_score']:.1f}/100 ({result['grade']})")
    safe_print(f"\nMetrics:")
    safe_print(f"  Hook words: {result['metrics']['hook_words']}")
    safe_print(f"  Phrase count: {result['metrics']['phrase_count']}")
    safe_print(f"  Total words: {result['metrics']['total_words']}")
    safe_print(f"  Est. duration: {result['estimated_duration']}s")
    safe_print(f"  Voice speed: {result['voice_speed_needed']}")
    safe_print(f"\nStructure: {result['structure']['score']:.1f}/100")
    safe_print(f"Readability: {result['readability']['score']:.1f}/100 ({result['readability']['level']})")
    safe_print(f"Value: {result['value']['score']}/100")
    
    if result['issues']:
        safe_print(f"\nIssues Found:")
        for issue in result['issues']:
            safe_print(f"  [{issue['severity'].upper()}] {issue['message']}")
    
    safe_print(f"\nSuggestions:")
    for s in result['suggestions']:
        safe_print(f"  - {s}")
    safe_print("=" * 50)
    
    safe_print("\nTest complete!")

