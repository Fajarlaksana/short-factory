#!/usr/bin/env python3
"""
ViralShorts Factory - Competitor Learner v17.9.51
==================================================

Learns successful patterns from competitor channels.
Uses YouTube Data API to analyze top-performing shorts.

Features:
- Tracks successful channels in your niche
- Extracts title patterns that work
- Learns optimal video lengths
- Identifies trending topics
- Copies winning strategies (legally!)

Note: Requires YouTube API access for full functionality
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
COMPETITOR_FILE = STATE_DIR / "competitor_analysis.json"


class CompetitorLearner:
    """
    Learns from successful competitor channels.
    """
    
    # Top YouTube Shorts channels by niche (for reference)
    REFERENCE_CHANNELS = {
        "psychology": [
            "Psych2Go",
            "Psychology Element",
            "Practical Psychology"
        ],
        "money": [
            "Graham Stephan",
            "Mark Tilbury",
            "Minority Mindset"
        ],
        "productivity": [
            "Thomas Frank",
            "Ali Abdaal",
            "Matt D'Avella"
        ],
        "motivation": [
            "Motivation2Study",
            "Be Inspired",
            "Absolute Motivation"
        ],
        "technology": [
            "MKBHD",
            "Linus Tech Tips",
            "Austin Evans"
        ]
    }
    
    # Common patterns in viral titles
    TITLE_PATTERNS = {
        "number_first": r"^\d+\s",
        "question": r"\?$",
        "how_to": r"^(how to|how i)",
        "why": r"^why\s",
        "secret": r"secret",
        "truth": r"truth",
        "never": r"never",
        "always": r"always",
        "stop": r"^stop\s",
        "dont": r"don'?t",
        "mistake": r"mistake",
        "hack": r"hack",
        "trick": r"trick"
    }
    
    def __init__(self):
        self.data = self._load()
        self.youtube_key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if COMPETITOR_FILE.exists():
                with open(COMPETITOR_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "tracked_channels": {},
            "learned_patterns": {},
            "top_titles": [],
            "analyzed_videos": 0,
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(COMPETITOR_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_successful_titles(self, titles: List[str]) -> Dict:
        """
        Analyze a list of successful video titles to extract patterns.
        
        Args:
            titles: List of successful video titles
        
        Returns:
            Dict with pattern analysis
        """
        pattern_counts = {p: 0 for p in self.TITLE_PATTERNS}
        total = len(titles)
        
        word_freq = {}
        lengths = []
        
        for title in titles:
            title_lower = title.lower()
            lengths.append(len(title.split()))
            
            # Check patterns
            for pattern_name, regex in self.TITLE_PATTERNS.items():
                if re.search(regex, title_lower, re.IGNORECASE):
                    pattern_counts[pattern_name] += 1
            
            # Word frequency
            words = re.findall(r'\b[a-z]{3,}\b', title_lower)
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate pattern percentages
        pattern_percentages = {
            k: round((v / total) * 100, 1) 
            for k, v in pattern_counts.items()
        }
        
        # Top patterns
        top_patterns = sorted(
            pattern_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Top words
        top_words = sorted(
            word_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Optimal length
        avg_length = sum(lengths) / len(lengths) if lengths else 8
        
        analysis = {
            "total_analyzed": total,
            "pattern_percentages": pattern_percentages,
            "top_patterns": [{"pattern": p, "usage": f"{u}%"} for p, u in top_patterns],
            "top_words": [{"word": w, "count": c} for w, c in top_words],
            "avg_title_length": round(avg_length, 1),
            "recommendations": self._generate_pattern_recommendations(top_patterns)
        }
        
        # Save learned patterns
        self.data["learned_patterns"] = analysis
        self.data["analyzed_videos"] += total
        self._save()
        
        return analysis
    
    def _generate_pattern_recommendations(self, top_patterns: List) -> List[str]:
        """Generate recommendations based on patterns."""
        recs = []
        
        pattern_tips = {
            "number_first": "Start titles with numbers (e.g., '5 Ways to...')",
            "question": "Ask questions to spark curiosity",
            "how_to": "Use 'How to' for practical content",
            "why": "Use 'Why' to explain phenomena",
            "secret": "Include 'secret' for exclusivity feel",
            "truth": "Reveal 'truth' for authority positioning",
            "never": "Use 'never' for strong warnings",
            "stop": "Start with 'Stop' for pattern interrupts",
            "hack": "Use 'hack' for quick tips content",
            "mistake": "Highlight 'mistakes' people make"
        }
        
        for pattern, _ in top_patterns[:3]:
            if pattern in pattern_tips:
                recs.append(pattern_tips[pattern])
        
        return recs
    
    def learn_from_search(self, query: str, max_results: int = 20) -> Dict:
        """
        Learn from top YouTube search results.
        
        Args:
            query: Search query (e.g., "psychology facts shorts")
            max_results: Number of results to analyze
        
        Returns:
            Analysis of top results
        """
        if not self.youtube_key:
            safe_print("[COMPETITOR] No YouTube API key, using cached patterns")
            return self.data.get("learned_patterns", {})
        
        try:
            # Search YouTube
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query + " #shorts",
                "type": "video",
                "videoDuration": "short",
                "order": "viewCount",
                "maxResults": min(max_results, 50),
                "key": self.youtube_key
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                
                titles = []
                for item in results.get("items", []):
                    title = item["snippet"]["title"]
                    titles.append(title)
                    self.data["top_titles"].append({
                        "title": title,
                        "query": query,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Keep only recent titles
                self.data["top_titles"] = self.data["top_titles"][-200:]
                
                # Analyze patterns
                analysis = self.analyze_successful_titles(titles)
                analysis["query"] = query
                analysis["source"] = "youtube_api"
                
                return analysis
            else:
                safe_print(f"[COMPETITOR] API error: {response.status_code}")
        
        except Exception as e:
            safe_print(f"[COMPETITOR] Error: {e}")
        
        return self.data.get("learned_patterns", {})
    
    def get_title_suggestions(self, topic: str, category: str) -> List[str]:
        """
        Generate title suggestions based on learned patterns.
        
        Args:
            topic: Video topic
            category: Content category
        
        Returns:
            List of suggested titles
        """
        learned = self.data.get("learned_patterns", {})
        top_patterns = learned.get("top_patterns", [])
        
        suggestions = []
        
        # Generate titles using top patterns
        pattern_templates = {
            "number_first": [
                f"5 {topic.title()} Facts That Will Blow Your Mind",
                f"7 {topic.title()} Tips You Need to Know",
                f"3 {topic.title()} Mistakes Everyone Makes"
            ],
            "question": [
                f"Why Does {topic.title()} Work This Way?",
                f"What If {topic.title()} Is Wrong?",
                f"Is This {topic.title()} Hack Real?"
            ],
            "how_to": [
                f"How To Master {topic.title()} in 30 Seconds",
                f"How I Learned {topic.title()} The Hard Way",
                f"How To Use {topic.title()} Like a Pro"
            ],
            "secret": [
                f"The {topic.title()} Secret Nobody Tells You",
                f"Secret {topic.title()} Hack That Actually Works",
                f"This {topic.title()} Secret Changed Everything"
            ],
            "truth": [
                f"The Truth About {topic.title()} Nobody Talks About",
                f"The Real Truth Behind {topic.title()}",
                f"Why The {topic.title()} Truth Hurts"
            ]
        }
        
        # Add suggestions from top patterns
        for pattern_info in top_patterns[:3]:
            pattern = pattern_info["pattern"]
            if pattern in pattern_templates:
                suggestions.extend(pattern_templates[pattern][:2])
        
        # Fallback suggestions
        if not suggestions:
            suggestions = [
                f"The {topic.title()} Hack You Need",
                f"Why {topic.title()} Changes Everything",
                f"This {topic.title()} Tip Is Game-Changing"
            ]
        
        return suggestions[:5]
    
    def get_competitor_insights(self, category: str = None) -> Dict:
        """Get insights from competitor analysis."""
        learned = self.data.get("learned_patterns", {})
        
        insights = {
            "total_videos_analyzed": self.data.get("analyzed_videos", 0),
            "top_patterns": learned.get("top_patterns", [])[:5],
            "top_power_words": learned.get("top_words", [])[:5],
            "avg_title_length": learned.get("avg_title_length", 8),
            "recommendations": learned.get("recommendations", []),
            "reference_channels": self.REFERENCE_CHANNELS.get(
                category.lower() if category else "productivity",
                self.REFERENCE_CHANNELS["productivity"]
            )
        }
        
        return insights
    
    def track_channel(self, channel_name: str, channel_id: str = None,
                      category: str = None):
        """Add a channel to track for learning."""
        self.data["tracked_channels"][channel_name] = {
            "channel_id": channel_id,
            "category": category,
            "added": datetime.now().isoformat(),
            "last_analyzed": None
        }
        self._save()
        safe_print(f"[COMPETITOR] Now tracking: {channel_name}")


# Global instance
_learner = None

def get_competitor_learner() -> CompetitorLearner:
    global _learner
    if _learner is None:
        _learner = CompetitorLearner()
    return _learner

def learn_from_competitors(query: str) -> Dict:
    """Learn from competitor search results."""
    return get_competitor_learner().learn_from_search(query)


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("COMPETITOR LEARNER - TEST")
    safe_print("=" * 60)
    
    learner = CompetitorLearner()
    
    # Test with sample titles
    sample_titles = [
        "5 Psychology Facts That Will Blow Your Mind",
        "Why Your Brain Lies to You",
        "The Secret to Being More Confident",
        "How I Overcame Social Anxiety",
        "7 Money Habits of Millionaires",
        "Stop Making These 3 Mistakes",
        "The Truth About Success Nobody Tells You",
        "Why 99% of People Fail at This"
    ]
    
    analysis = learner.analyze_successful_titles(sample_titles)
    
    safe_print(f"\nAnalyzed: {analysis['total_analyzed']} titles")
    safe_print(f"\nTop Patterns:")
    for p in analysis['top_patterns'][:5]:
        safe_print(f"  - {p['pattern']}: {p['usage']}")
    
    safe_print(f"\nTop Words:")
    for w in analysis['top_words'][:5]:
        safe_print(f"  - {w['word']}: {w['count']} times")
    
    safe_print(f"\nRecommendations:")
    for r in analysis['recommendations']:
        safe_print(f"  - {r}")
    
    # Test title suggestions
    safe_print("\nTitle Suggestions for 'morning routine':")
    for title in learner.get_title_suggestions("morning routine", "productivity"):
        safe_print(f"  - {title}")
