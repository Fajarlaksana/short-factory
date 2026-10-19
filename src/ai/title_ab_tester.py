#!/usr/bin/env python3
"""
ViralShorts Factory - Title A/B Testing System v17.9.50
========================================================

Generates multiple title variants and tracks which perform best.
Uses AI to create psychologically-optimized title alternatives.

Features:
- Generates 3 title variants per video
- Tracks view/engagement by title style
- Learns optimal patterns over time
- Integrates with analytics feedback
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Smart AI caller
try:
    from src.ai.smart_ai_caller import smart_call_ai
except ImportError:
    smart_call_ai = None


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
AB_TEST_FILE = STATE_DIR / "title_ab_tests.json"


class TitleABTester:
    """
    Generates and tracks title variants for A/B testing.
    """
    
    # Title style templates - each has different psychological approach
    TITLE_STYLES = {
        "curiosity_gap": {
            "pattern": "What {topic} reveals about {outcome}",
            "triggers": ["curiosity", "mystery"],
            "example": "What your morning routine reveals about success"
        },
        "number_power": {
            "pattern": "{number} {topic} secrets that {outcome}",
            "triggers": ["specificity", "value"],
            "example": "7 money secrets that millionaires use"
        },
        "bold_claim": {
            "pattern": "This {topic} hack will {transform}",
            "triggers": ["transformation", "promise"],
            "example": "This productivity hack will double your output"
        },
        "controversy": {
            "pattern": "Why {common_belief} is wrong about {topic}",
            "triggers": ["challenge", "debate"],
            "example": "Why experts are wrong about sleep"
        },
        "urgency": {
            "pattern": "Stop {bad_action} before {consequence}",
            "triggers": ["fear", "prevention"],
            "example": "Stop this habit before it ruins your health"
        },
        "identity": {
            "pattern": "Only {percent}% of people know this {topic} secret",
            "triggers": ["exclusivity", "intelligence"],
            "example": "Only 3% of people know this wealth secret"
        },
        "story": {
            "pattern": "I tried {topic} for {time} - here's what happened",
            "triggers": ["authenticity", "journey"],
            "example": "I tried cold showers for 30 days - here's what happened"
        },
        "versus": {
            "pattern": "{option_a} vs {option_b}: The truth about {topic}",
            "triggers": ["comparison", "decision"],
            "example": "Morning vs Night workouts: The truth about gains"
        }
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load A/B test data."""
        try:
            if AB_TEST_FILE.exists():
                with open(AB_TEST_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[AB] Load error: {e}")
        
        return {
            "tests": [],
            "style_performance": {style: {"uses": 0, "avg_views": 0, "total_views": 0}
                                  for style in self.TITLE_STYLES.keys()},
            "best_patterns": [],
            "last_updated": None
        }
    
    def _save(self):
        """Save A/B test data."""
        self.data["last_updated"] = datetime.now().isoformat()
        try:
            with open(AB_TEST_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            safe_print(f"[AB] Save error: {e}")
    
    def generate_title_variants(self, topic: str, category: str, 
                                 base_title: str = None) -> List[Dict]:
        """
        Generate 3 title variants using different psychological approaches.
        
        Args:
            topic: Video topic
            category: Content category
            base_title: Original title (optional)
        
        Returns:
            List of {title, style, triggers} dicts
        """
        variants = []
        
        # Get top 3 performing styles + 1 experimental
        top_styles = self._get_top_styles(3)
        
        # Use AI to generate variants
        if smart_call_ai:
            for style_name in top_styles:
                style = self.TITLE_STYLES.get(style_name, self.TITLE_STYLES["curiosity_gap"])
                variant = self._generate_ai_variant(topic, category, style_name, style)
                if variant:
                    variants.append({
                        "title": variant,
                        "style": style_name,
                        "triggers": style["triggers"]
                    })
        
        # Fallback: use template-based generation
        if len(variants) < 3:
            template_variants = self._generate_template_variants(topic, category)
            variants.extend(template_variants[:3 - len(variants)])
        
        # Record this test
        test_record = {
            "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "category": category,
            "variants": variants,
            "selected": None,
            "views": None,
            "created": datetime.now().isoformat()
        }
        self.data["tests"].append(test_record)
        self._save()
        
        safe_print(f"[AB] Generated {len(variants)} title variants")
        return variants
    
    def _generate_ai_variant(self, topic: str, category: str,
                             style_name: str, style: Dict) -> Optional[str]:
        """Generate a title variant using AI."""
        prompt = f"""Generate a viral YouTube Shorts title using the {style_name.upper()} style.

Topic: {topic}
Category: {category}

Style Pattern: {style['pattern']}
Psychological Triggers: {', '.join(style['triggers'])}
Example: {style['example']}

Requirements:
1. Maximum 60 characters
2. Use the style pattern as inspiration (don't copy exactly)
3. Create curiosity/urgency
4. Be specific and compelling
5. No emojis
6. No quotes in response

Return ONLY the title, nothing else."""
        
        try:
            result = smart_call_ai(prompt, hint="creative", max_tokens=50)
            if result:
                # Clean the result
                title = result.strip().strip('"\'')
                if len(title) <= 80:
                    return title
        except Exception as e:
            safe_print(f"[AB] AI variant error: {e}")
        
        return None
    
    def _generate_template_variants(self, topic: str, category: str) -> List[Dict]:
        """Generate variants using templates (fallback)."""
        import random
        
        variants = []
        templates = [
            (f"The {topic} secret nobody talks about", "curiosity_gap"),
            (f"5 {topic} facts that change everything", "number_power"),
            (f"Why {topic} will transform your life", "bold_claim"),
        ]
        
        for title, style in templates:
            style_info = self.TITLE_STYLES.get(style, {})
            variants.append({
                "title": title[:60],  # Ensure max length
                "style": style,
                "triggers": style_info.get("triggers", ["curiosity"])
            })
        
        return variants
    
    def _get_top_styles(self, n: int = 3) -> List[str]:
        """Get top performing title styles."""
        style_perf = self.data.get("style_performance", {})
        
        # Calculate score: uses * avg_views (balanced metric)
        scored = []
        for style, stats in style_perf.items():
            uses = stats.get("uses", 0)
            avg_views = stats.get("avg_views", 100)  # Default baseline
            score = (uses + 1) * avg_views  # +1 to avoid zero
            scored.append((style, score))
        
        # Sort by score, return top n
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Always include at least one experimental style
        top = [s[0] for s in scored[:n-1]]
        
        # Add one less-used style for exploration
        all_styles = list(self.TITLE_STYLES.keys())
        for style in all_styles:
            if style not in top:
                top.append(style)
                break
        
        return top[:n]
    
    def record_performance(self, test_id: str, selected_title: str, views: int):
        """
        Record which title was selected and its performance.
        
        Call this after video gets views to learn from results.
        """
        for test in self.data["tests"]:
            if test["id"] == test_id:
                test["selected"] = selected_title
                test["views"] = views
                
                # Update style performance
                for variant in test["variants"]:
                    if variant["title"] == selected_title:
                        style = variant["style"]
                        perf = self.data["style_performance"].get(style, 
                                {"uses": 0, "avg_views": 0, "total_views": 0})
                        
                        perf["uses"] += 1
                        perf["total_views"] += views
                        perf["avg_views"] = perf["total_views"] / perf["uses"]
                        
                        self.data["style_performance"][style] = perf
                        break
                
                self._save()
                safe_print(f"[AB] Recorded performance: {views} views for '{selected_title[:30]}...'")
                return
        
        safe_print(f"[AB] Test {test_id} not found")
    
    def get_best_style(self) -> str:
        """Get the current best-performing title style."""
        style_perf = self.data.get("style_performance", {})
        
        best_style = "curiosity_gap"  # Default
        best_score = 0
        
        for style, stats in style_perf.items():
            if stats.get("uses", 0) >= 3:  # Only consider if enough data
                if stats.get("avg_views", 0) > best_score:
                    best_score = stats["avg_views"]
                    best_style = style
        
        return best_style
    
    def get_stats(self) -> Dict:
        """Get A/B testing statistics."""
        return {
            "total_tests": len(self.data.get("tests", [])),
            "style_performance": self.data.get("style_performance", {}),
            "best_style": self.get_best_style(),
            "last_updated": self.data.get("last_updated")
        }


# Global instance
_tester = None


def get_ab_tester() -> TitleABTester:
    """Get global A/B tester instance."""
    global _tester
    if _tester is None:
        _tester = TitleABTester()
    return _tester


def generate_ab_titles(topic: str, category: str) -> List[Dict]:
    """Convenience function to generate A/B title variants."""
    return get_ab_tester().generate_title_variants(topic, category)


# Test
if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("TITLE A/B TESTER - TEST")
    safe_print("=" * 60)
    
    tester = TitleABTester()
    
    # Test variant generation
    variants = tester.generate_title_variants(
        topic="morning routines of successful people",
        category="productivity"
    )
    
    safe_print("\nGenerated variants:")
    for i, v in enumerate(variants, 1):
        safe_print(f"  {i}. [{v['style']}] {v['title']}")
    
    # Show stats
    stats = tester.get_stats()
    safe_print(f"\nStats: {json.dumps(stats, indent=2)}")
