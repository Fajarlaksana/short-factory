#!/usr/bin/env python3
"""
Competitor Analyzer for ViralShorts Factory v17.7.8
====================================================

Analyzes competitor content to find opportunities:
1. Track popular topics from successful channels
2. Identify content gaps we can fill
3. Generate unique angles on trending topics
4. Learn from competitor engagement patterns

FREE: Uses YouTube API (limited) + AI analysis
"""

import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# State file
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
COMPETITOR_FILE = STATE_DIR / "competitor_analysis.json"


class CompetitorAnalyzer:
    """Analyzes competitors to find content opportunities."""
    
    # Sample competitor channels (shorts/educational niche)
    # Note: YouTube API has quota limits, so we cache results
    NICHE_KEYWORDS = [
        "psychology facts shorts",
        "money tips shorts", 
        "productivity hacks shorts",
        "life hacks shorts",
        "mind blowing facts shorts"
    ]
    
    def __init__(self):
        self.data = self._load()
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
    
    def _load(self) -> Dict:
        """Load competitor data."""
        try:
            if COMPETITOR_FILE.exists():
                with open(COMPETITOR_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "trending_topics": [],
            "content_gaps": [],
            "unique_angles": [],
            "competitor_patterns": [],
            "last_analysis": None,
            "our_differentiators": []
        }
    
    def _save(self):
        """Save competitor data."""
        self.data["last_analysis"] = datetime.now().isoformat()
        with open(COMPETITOR_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def identify_content_gaps(self, our_topics: List[str], popular_topics: List[str]) -> List[Dict]:
        """
        Find topics that are popular but we haven't covered.
        
        Args:
            our_topics: Topics we've already covered
            popular_topics: Topics that are trending/popular
        
        Returns: List of gap opportunities
        """
        our_set = set(t.lower() for t in our_topics)
        
        gaps = []
        for topic in popular_topics:
            topic_lower = topic.lower()
            # Check if we've covered something similar
            is_covered = any(
                our in topic_lower or topic_lower in our 
                for our in our_set
            )
            
            if not is_covered:
                gaps.append({
                    "topic": topic,
                    "reason": "Trending but not covered",
                    "priority": "high"
                })
        
        self.data["content_gaps"] = gaps[:10]  # Top 10 gaps
        self._save()
        
        return gaps
    
    def generate_unique_angle(self, competitor_topic: str) -> Dict:
        """
        AI generates our unique angle on a competitor's topic.
        
        Instead of copying, we differentiate!
        """
        if not self.groq_key and not self.gemini_key:
            return self._fallback_angle(competitor_topic)
        
        prompt = f"""A competitor posted a viral video about: "{competitor_topic}"

We want to cover the same topic but with a UNIQUE ANGLE that:
1. Adds MORE value than the competitor
2. Has a STRONGER hook
3. Takes a DIFFERENT perspective
4. Makes our version BETTER and worth watching even if they saw the competitor's

Generate our differentiated approach:

OUTPUT JSON:
{{
    "our_topic_angle": "How we'll approach this differently",
    "our_hook": "Our stronger/different hook",
    "unique_value": "What we add that competitor didn't",
    "perspective_shift": "Our unique take/perspective",
    "why_watch_us": "Why watch us instead of competitor"
}}

JSON ONLY."""

        try:
            if self.gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                result = response.text
            elif self.groq_key:
                from groq import Groq
                # v17.8: Dynamic model selection
                try:
                    from quota_optimizer import get_best_groq_model
                    model = get_best_groq_model(self.groq_key)
                except ImportError:
                    model = "llama-3.3-70b-versatile"
                
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
                result = response.choices[0].message.content
            else:
                return self._fallback_angle(competitor_topic)
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result.strip())
            
        except Exception as e:
            print(f"[!] Angle generation failed: {e}")
            return self._fallback_angle(competitor_topic)
    
    def _fallback_angle(self, topic: str) -> Dict:
        """Generate angle without AI."""
        angles = [
            "the contrarian view",
            "the deeper psychology",
            "the practical application",
            "what experts miss",
            "the 2026 update"
        ]
        
        return {
            "our_topic_angle": f"{topic} - {random.choice(angles)}",
            "our_hook": f"What nobody tells you about {topic}...",
            "unique_value": "Deeper insight with specific examples",
            "perspective_shift": "Challenge the conventional wisdom",
            "why_watch_us": "We provide the real, actionable truth"
        }
    
    def analyze_competitor_patterns(self, competitor_videos: List[Dict]) -> Dict:
        """
        Analyze patterns in competitor success.
        
        Args:
            competitor_videos: List of video dicts with title, views, etc.
        
        Returns: Pattern analysis
        """
        patterns = {
            "hook_patterns": [],
            "title_structures": [],
            "common_topics": [],
            "avg_length": 0,
            "engagement_tricks": []
        }
        
        # Analyze hooks (first few words of titles)
        for video in competitor_videos:
            title = video.get('title', '')
            words = title.split()[:3]
            hook = ' '.join(words)
            
            if hook and len(hook) > 5:
                patterns["hook_patterns"].append(hook)
        
        # Find common topics
        topic_words = []
        for video in competitor_videos:
            title = video.get('title', '').lower()
            for word in title.split():
                if len(word) > 4:  # Skip short words
                    topic_words.append(word)
        
        # Count frequency
        from collections import Counter
        word_counts = Counter(topic_words)
        patterns["common_topics"] = [w for w, c in word_counts.most_common(10)]
        
        self.data["competitor_patterns"] = patterns
        self._save()
        
        return patterns
    
    def get_content_suggestions(self, count: int = 5) -> List[Dict]:
        """
        Get content suggestions based on competitor analysis.
        
        Returns: List of content ideas with unique angles
        """
        suggestions = []
        
        # Use content gaps
        for gap in self.data.get("content_gaps", [])[:count]:
            suggestions.append({
                "type": "gap",
                "topic": gap["topic"],
                "reason": "Trending but we haven't covered"
            })
        
        # Use unique angles
        for angle in self.data.get("unique_angles", [])[:count]:
            suggestions.append({
                "type": "angle",
                "topic": angle.get("our_topic_angle", ""),
                "reason": "Differentiated take on popular topic"
            })
        
        return suggestions[:count]
    
    def set_our_differentiators(self, differentiators: List[str]):
        """
        Set what makes our channel unique.
        
        These will be incorporated into all content.
        """
        self.data["our_differentiators"] = differentiators
        self._save()


# Singleton
_analyzer = None

def get_competitor_analyzer() -> CompetitorAnalyzer:
    """Get the singleton competitor analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = CompetitorAnalyzer()
    return _analyzer


if __name__ == "__main__":
    # Test
    analyzer = get_competitor_analyzer()
    
    # Test unique angle generation
    angle = analyzer.generate_unique_angle("Why successful people wake up at 5 AM")
    print("Unique Angle:", json.dumps(angle, indent=2))
    
    # Test content gaps
    our_topics = ["morning routines", "productivity tips"]
    trending = ["5 AM club secrets", "money mindset", "dopamine detox", "social media break"]
    gaps = analyzer.identify_content_gaps(our_topics, trending)
    print("\nContent Gaps:", gaps)
    
    # Test suggestions
    suggestions = analyzer.get_content_suggestions(3)
    print("\nSuggestions:", suggestions)

