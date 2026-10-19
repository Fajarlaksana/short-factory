#!/usr/bin/env python3
"""
ViralShorts Factory - First 3 Seconds Optimizer v17.9.51
=========================================================

The first 3 seconds determine if a viewer stays or swipes.
YouTube's algorithm heavily weighs early retention.

This module optimizes the critical opening moments:
- Pattern interrupts
- Visual hooks
- Audio spikes
- Text overlays
- Curiosity gaps

Research shows:
- 65% of viewers decide within 3 seconds
- Strong hooks increase watch time by 40%
- Pattern interrupts reduce swipe-away by 35%
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
HOOKS_FILE = STATE_DIR / "first_seconds_hooks.json"


class FirstSecondsOptimizer:
    """
    Optimizes the critical first 3 seconds of every video.
    """
    
    # Proven pattern interrupt techniques
    PATTERN_INTERRUPTS = {
        "shocking_stat": {
            "template": "{shocking_number}% of people don't know this...",
            "visual": "big_number_zoom",
            "audio": "impact_sound",
            "effectiveness": 9.2
        },
        "direct_challenge": {
            "template": "You're doing {topic} completely wrong.",
            "visual": "face_close_up",
            "audio": "record_scratch",
            "effectiveness": 8.8
        },
        "impossible_claim": {
            "template": "This {topic} trick is literally impossible... but it works.",
            "visual": "split_screen",
            "audio": "suspense_build",
            "effectiveness": 8.5
        },
        "time_pressure": {
            "template": "In the next {seconds} seconds, you'll learn...",
            "visual": "countdown_timer",
            "audio": "ticking_clock",
            "effectiveness": 8.3
        },
        "insider_secret": {
            "template": "I shouldn't be telling you this, but...",
            "visual": "whisper_close",
            "audio": "quiet_then_normal",
            "effectiveness": 8.7
        },
        "identity_hook": {
            "template": "If you're a {identity}, watch this NOW.",
            "visual": "pointing_gesture",
            "audio": "attention_grab",
            "effectiveness": 8.4
        },
        "controversy_spark": {
            "template": "Everyone says {common_belief}. They're all wrong.",
            "visual": "crossed_out_text",
            "audio": "wrong_buzzer",
            "effectiveness": 9.0
        },
        "story_hook": {
            "template": "I lost ${money} before I learned this...",
            "visual": "emotion_face",
            "audio": "emotional_music",
            "effectiveness": 8.6
        }
    }
    
    # Visual techniques for first 3 seconds
    VISUAL_HOOKS = {
        "zoom_in": "Start zoomed out, quickly zoom to subject",
        "flash_text": "Large text appears with flash effect",
        "split_reveal": "Screen splits to reveal content",
        "countdown": "3-2-1 countdown with anticipation",
        "before_after": "Quick flash of transformation",
        "reaction_face": "Shocked/surprised expression",
        "movement": "Subject moves toward camera",
        "color_pop": "Desaturated then color bursts in"
    }
    
    # Audio techniques
    AUDIO_HOOKS = {
        "bass_drop": "Low frequency hit for impact",
        "record_scratch": "Attention-grabbing scratch sound",
        "woosh": "Quick transition sound",
        "impact": "Deep thud for emphasis",
        "rising_tone": "Building anticipation",
        "silence_break": "Brief silence then loud",
        "voice_effect": "Distorted then clear voice"
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if HOOKS_FILE.exists():
                with open(HOOKS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "hooks_used": [],
            "hook_performance": {},
            "best_hooks": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(HOOKS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_opening(self, topic: str, category: str, 
                         target_emotion: str = "curiosity") -> Dict:
        """
        Generate an optimized opening for the first 3 seconds.
        
        Returns:
            Dict with text, visual, audio, and timing recommendations
        """
        # Get best performing hook type for this category
        hook_type = self._get_best_hook_for_category(category)
        hook_template = self.PATTERN_INTERRUPTS.get(
            hook_type, 
            self.PATTERN_INTERRUPTS["shocking_stat"]
        )
        
        # Generate hook text with AI
        hook_text = self._generate_hook_text(topic, category, hook_type)
        
        # Select complementary visual and audio
        visual = self._select_visual(hook_type, target_emotion)
        audio = self._select_audio(hook_type, target_emotion)
        
        opening = {
            "hook_type": hook_type,
            "text": hook_text,
            "visual_technique": visual,
            "audio_technique": audio,
            "timing": {
                "text_appear": 0.3,  # seconds
                "text_duration": 2.5,
                "visual_effect_start": 0.0,
                "audio_hit": 0.2
            },
            "effectiveness_score": hook_template["effectiveness"],
            "tips": self._get_execution_tips(hook_type)
        }
        
        # Record usage
        self._record_usage(hook_type, category)
        
        safe_print(f"[HOOK] Generated {hook_type} opening: '{hook_text[:50]}...'")
        return opening
    
    def _generate_hook_text(self, topic: str, category: str, 
                            hook_type: str) -> str:
        """Generate hook text using AI."""
        template = self.PATTERN_INTERRUPTS[hook_type]["template"]
        
        if smart_call_ai:
            prompt = f"""Create a powerful opening hook for a YouTube Short.

Topic: {topic}
Category: {category}
Hook Style: {hook_type}
Template Pattern: {template}

Requirements:
1. Maximum 15 words
2. Create INSTANT curiosity
3. Make viewer NEED to keep watching
4. Use the template pattern as inspiration
5. Be specific, not generic
6. No emojis

Return ONLY the hook text, nothing else."""

            try:
                result = smart_call_ai(prompt, hint="creative", max_tokens=50)
                if result:
                    return result.strip().strip('"\'')[:100]
            except:
                pass
        
        # Fallback: use template with topic
        return template.replace("{topic}", topic).replace(
            "{shocking_number}", "97"
        ).replace("{seconds}", "30")
    
    def _get_best_hook_for_category(self, category: str) -> str:
        """Get the best performing hook type for a category."""
        perf = self.data.get("hook_performance", {})
        cat_perf = perf.get(category, {})
        
        if cat_perf:
            # Return hook with highest views
            best = max(cat_perf.items(), key=lambda x: x[1].get("avg_views", 0))
            if best[1].get("uses", 0) >= 3:  # Enough data
                return best[0]
        
        # Default recommendations by category
        category_defaults = {
            "psychology": "insider_secret",
            "money": "shocking_stat",
            "productivity": "time_pressure",
            "health": "direct_challenge",
            "technology": "impossible_claim",
            "motivation": "story_hook",
            "relationships": "identity_hook",
            "education": "controversy_spark"
        }
        
        return category_defaults.get(category.lower(), "shocking_stat")
    
    def _select_visual(self, hook_type: str, emotion: str) -> Dict:
        """Select visual technique for hook."""
        hook_info = self.PATTERN_INTERRUPTS.get(hook_type, {})
        visual_key = hook_info.get("visual", "flash_text")
        
        return {
            "technique": visual_key,
            "description": self.VISUAL_HOOKS.get(visual_key, "Standard text overlay"),
            "recommended_duration": 2.0
        }
    
    def _select_audio(self, hook_type: str, emotion: str) -> Dict:
        """Select audio technique for hook."""
        hook_info = self.PATTERN_INTERRUPTS.get(hook_type, {})
        audio_key = hook_info.get("audio", "impact")
        
        return {
            "technique": audio_key,
            "description": self.AUDIO_HOOKS.get(audio_key, "Impact sound"),
            "timing": "0.2s before text appears"
        }
    
    def _get_execution_tips(self, hook_type: str) -> List[str]:
        """Get execution tips for hook type."""
        tips = {
            "shocking_stat": [
                "Show the number BIG on screen",
                "Use a bold, contrasting color",
                "Add a subtle shake effect"
            ],
            "direct_challenge": [
                "Speak with confident authority",
                "Look directly at camera",
                "Slight pause after statement"
            ],
            "impossible_claim": [
                "Build slight confusion",
                "Quick visual proof tease",
                "Promise payoff is coming"
            ],
            "time_pressure": [
                "Show actual countdown",
                "Increase pace slightly",
                "Create urgency in voice"
            ],
            "insider_secret": [
                "Lower voice slightly",
                "Create intimacy",
                "Lean toward camera"
            ],
            "identity_hook": [
                "Be specific about identity",
                "Create belonging feeling",
                "Use 'you' frequently"
            ],
            "controversy_spark": [
                "State common belief clearly",
                "Pause for effect",
                "Strong contradiction"
            ],
            "story_hook": [
                "Show genuine emotion",
                "Specific numbers/details",
                "Promise transformation"
            ]
        }
        return tips.get(hook_type, ["Speak clearly", "Create curiosity"])
    
    def _record_usage(self, hook_type: str, category: str):
        """Record hook usage for learning."""
        usage = {
            "hook_type": hook_type,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        self.data["hooks_used"].append(usage)
        
        # Initialize category performance if needed
        if "hook_performance" not in self.data:
            self.data["hook_performance"] = {}
        if category not in self.data["hook_performance"]:
            self.data["hook_performance"][category] = {}
        if hook_type not in self.data["hook_performance"][category]:
            self.data["hook_performance"][category][hook_type] = {
                "uses": 0, "total_views": 0, "avg_views": 0
            }
        
        self.data["hook_performance"][category][hook_type]["uses"] += 1
        self._save()
    
    def record_performance(self, hook_type: str, category: str, views: int):
        """Record how a hook performed for learning."""
        if category in self.data.get("hook_performance", {}):
            if hook_type in self.data["hook_performance"][category]:
                perf = self.data["hook_performance"][category][hook_type]
                perf["total_views"] += views
                perf["avg_views"] = perf["total_views"] / perf["uses"]
                self._save()
                safe_print(f"[HOOK] Recorded {views} views for {hook_type} in {category}")
    
    def get_recommendations(self, category: str) -> Dict:
        """Get hook recommendations for a category."""
        perf = self.data.get("hook_performance", {}).get(category, {})
        
        recommendations = []
        for hook_type, info in self.PATTERN_INTERRUPTS.items():
            hook_perf = perf.get(hook_type, {})
            recommendations.append({
                "hook_type": hook_type,
                "base_effectiveness": info["effectiveness"],
                "uses": hook_perf.get("uses", 0),
                "avg_views": hook_perf.get("avg_views", 0),
                "template": info["template"]
            })
        
        # Sort by effectiveness and performance
        recommendations.sort(
            key=lambda x: (x["avg_views"] if x["uses"] >= 3 else x["base_effectiveness"] * 100),
            reverse=True
        )
        
        return {
            "category": category,
            "top_recommendations": recommendations[:3],
            "all_hooks": recommendations
        }


# Global instance
_optimizer = None

def get_first_seconds_optimizer() -> FirstSecondsOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = FirstSecondsOptimizer()
    return _optimizer

def generate_hook(topic: str, category: str) -> Dict:
    """Convenience function to generate an optimized hook."""
    return get_first_seconds_optimizer().generate_opening(topic, category)


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("FIRST 3 SECONDS OPTIMIZER - TEST")
    safe_print("=" * 60)
    
    optimizer = FirstSecondsOptimizer()
    
    # Test hook generation
    hook = optimizer.generate_opening(
        topic="morning routines that boost productivity",
        category="productivity"
    )
    
    safe_print(f"\nHook Type: {hook['hook_type']}")
    safe_print(f"Text: {hook['text']}")
    safe_print(f"Visual: {hook['visual_technique']}")
    safe_print(f"Audio: {hook['audio_technique']}")
    safe_print(f"Effectiveness: {hook['effectiveness_score']}/10")
    safe_print(f"\nTips: {hook['tips']}")
