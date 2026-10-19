#!/usr/bin/env python3
"""
ViralShorts Factory - AI Voice Script Optimizer v17.8
=======================================================

Optimizes scripts for text-to-speech (TTS) output.
Ensures natural pacing, emphasis, and timing.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FILE = STATE_DIR / "voice_optimization.json"


class AIVoiceScriptOptimizer:
    """Optimizes scripts for TTS."""
    
    # Words that should have emphasis
    EMPHASIS_WORDS = [
        "stop", "wait", "never", "always", "secret", "truth", "hidden",
        "now", "today", "free", "important", "critical", "shocking",
        "first", "last", "only", "best", "worst"
    ]
    
    # Words to replace for TTS clarity
    TTS_REPLACEMENTS = {
        "&": "and",
        "%": "percent",
        "$": "dollars",
        "AI": "A I",
        "CEO": "C E O",
        "DIY": "D I Y",
        "vs": "versus",
        "w/": "with",
        "b/c": "because",
        "yr": "year",
        "yrs": "years",
    }
    
    # Punctuation for pacing
    PAUSE_MARKERS = {
        "short": ",",
        "medium": "...",
        "long": "."
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if VOICE_FILE.exists():
                with open(VOICE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "optimizations": [],
            "learned_patterns": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(VOICE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def optimize_script(self, content: Dict) -> Dict:
        """
        Optimize script for TTS output.
        
        Args:
            content: Dict with hook, phrases, cta
        
        Returns:
            Optimized content with timing info
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        
        # Optimize each part
        opt_hook = self._optimize_text(hook)
        opt_phrases = [self._optimize_text(p) for p in phrases]
        opt_cta = self._optimize_text(cta)
        
        # Calculate timing
        timing = self._calculate_timing(opt_hook, opt_phrases, opt_cta)
        
        # Get voice settings
        voice_settings = self._get_voice_settings(content.get("category", "general"))
        
        return {
            "original": content,
            "optimized": {
                "hook": opt_hook,
                "phrases": opt_phrases,
                "cta": opt_cta
            },
            "timing": timing,
            "voice_settings": voice_settings,
            "script_for_tts": self._combine_for_tts(opt_hook, opt_phrases, opt_cta)
        }
    
    def _optimize_text(self, text: str) -> str:
        """Optimize single text for TTS."""
        if not text:
            return text
        
        # Apply TTS replacements
        for old, new in self.TTS_REPLACEMENTS.items():
            text = text.replace(old, new)
        
        # Add pauses before emphasis words
        for word in self.EMPHASIS_WORDS:
            # Add slight pause before emphasis word
            pattern = r'\b' + word + r'\b'
            text = re.sub(pattern, f"... {word}", text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up multiple periods
        text = re.sub(r'\.{4,}', '...', text)
        
        return text.strip()
    
    def _calculate_timing(self, hook: str, phrases: List[str], 
                         cta: str) -> Dict:
        """Calculate timing for each segment."""
        # Approximate: 150 words per minute = 2.5 words per second
        wps = 2.5
        
        def time_for_text(text: str) -> float:
            words = len(text.split())
            # Add extra time for pauses
            pauses = text.count('...') * 0.3 + text.count('.') * 0.2
            return (words / wps) + pauses
        
        hook_time = time_for_text(hook)
        phrase_times = [time_for_text(p) for p in phrases]
        cta_time = time_for_text(cta)
        
        total = hook_time + sum(phrase_times) + cta_time
        
        return {
            "hook_duration": round(hook_time, 1),
            "phrase_durations": [round(t, 1) for t in phrase_times],
            "cta_duration": round(cta_time, 1),
            "total_duration": round(total, 1),
            "fits_shorts": total <= 60,
            "recommended_speed": self._get_recommended_speed(total)
        }
    
    def _get_recommended_speed(self, duration: float) -> str:
        """Get recommended voice speed."""
        if duration < 20:
            return "0.9x (slow for clarity)"
        elif duration <= 35:
            return "1.0x (normal)"
        elif duration <= 50:
            return "1.1x (slightly fast)"
        else:
            return "1.2x (fast - consider shortening)"
    
    def _get_voice_settings(self, category: str) -> Dict:
        """Get voice settings based on category."""
        settings = {
            "psychology": {"pitch": "medium", "rate": "1.0x", "style": "intriguing"},
            "money": {"pitch": "low", "rate": "1.0x", "style": "authoritative"},
            "productivity": {"pitch": "medium-high", "rate": "1.1x", "style": "energetic"},
            "motivation": {"pitch": "medium", "rate": "1.0x", "style": "inspiring"},
            "health": {"pitch": "medium", "rate": "1.0x", "style": "calm"},
        }
        
        return settings.get(category, {
            "pitch": "medium",
            "rate": "1.0x",
            "style": "conversational"
        })
    
    def _combine_for_tts(self, hook: str, phrases: List[str], 
                        cta: str) -> str:
        """Combine all parts into TTS-ready script."""
        parts = []
        
        if hook:
            parts.append(hook)
        
        for phrase in phrases:
            if phrase:
                parts.append(phrase)
        
        if cta:
            parts.append(cta)
        
        # Join with proper pauses
        return " ... ".join(parts)
    
    def add_emphasis_markers(self, text: str) -> str:
        """
        Add SSML-like emphasis markers for TTS.
        
        Returns text with markers like <emphasis>word</emphasis>
        """
        for word in self.EMPHASIS_WORDS:
            pattern = r'\b(' + word + r')\b'
            text = re.sub(pattern, r'<emphasis>\1</emphasis>', 
                         text, flags=re.IGNORECASE)
        
        return text
    
    def estimate_word_count(self, duration_seconds: float, 
                           speed: float = 1.0) -> int:
        """Estimate word count for target duration."""
        wps = 2.5 * speed  # Base words per second * speed multiplier
        return int(duration_seconds * wps)


# Singleton
_voice_optimizer = None


def get_voice_optimizer() -> AIVoiceScriptOptimizer:
    """Get singleton optimizer."""
    global _voice_optimizer
    if _voice_optimizer is None:
        _voice_optimizer = AIVoiceScriptOptimizer()
    return _voice_optimizer


def optimize_voice_script(content: Dict) -> Dict:
    """Convenience function."""
    return get_voice_optimizer().optimize_script(content)


if __name__ == "__main__":
    safe_print("Testing AI Voice Script Optimizer...")
    
    optimizer = get_voice_optimizer()
    
    # Test content
    content = {
        "hook": "STOP - here's something AI won't tell you",
        "phrases": [
            "First, always remember this simple truth.",
            "The secret to success is hidden in plain sight.",
            "Most people never realize this important fact.",
            "Now you know what 99% don't."
        ],
        "cta": "Comment if this changed your perspective!",
        "category": "productivity"
    }
    
    result = optimizer.optimize_script(content)
    
    safe_print(f"\nVoice Script Optimization:")
    safe_print("=" * 50)
    safe_print(f"\nOriginal Hook: {content['hook']}")
    safe_print(f"Optimized Hook: {result['optimized']['hook']}")
    
    safe_print(f"\nTiming:")
    safe_print(f"  Hook: {result['timing']['hook_duration']}s")
    safe_print(f"  Phrases: {result['timing']['phrase_durations']}")
    safe_print(f"  CTA: {result['timing']['cta_duration']}s")
    safe_print(f"  Total: {result['timing']['total_duration']}s")
    safe_print(f"  Fits Shorts: {result['timing']['fits_shorts']}")
    safe_print(f"  Speed: {result['timing']['recommended_speed']}")
    
    safe_print(f"\nVoice Settings:")
    for k, v in result['voice_settings'].items():
        safe_print(f"  {k}: {v}")
    
    safe_print(f"\nFull TTS Script:")
    safe_print(result['script_for_tts'][:100] + "...")
    
    # Test word count estimation
    safe_print(f"\nWord Count for 30s at 1.0x: {optimizer.estimate_word_count(30, 1.0)}")
    
    safe_print("\nTest complete!")

