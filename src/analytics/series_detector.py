#!/usr/bin/env python3
"""
ViralShorts Factory - Series Detection System v17.9.51
========================================================

Identifies high-performing content that should become series.
Series content gets 2-3x more views on average.

Features:
- Detects content patterns worth repeating
- Suggests part 2, 3, N for successful videos
- Tracks series performance over time
- Recommends optimal series frequency

Why series matter:
- Builds viewer anticipation
- Higher subscriber conversion
- Algorithm favors consistent themes
- Easier content planning
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
SERIES_FILE = STATE_DIR / "series_tracking.json"
VARIETY_FILE = STATE_DIR / "variety_state.json"


class SeriesDetector:
    """
    Detects content that should become recurring series.
    """
    
    # Series name patterns
    SERIES_PATTERNS = [
        "{topic} Part {n}",
        "{topic} #{n}",
        "More {topic} Facts",
        "{topic} Tips You Need #{n}",
        "Daily {topic} #{n}",
        "{topic} Secrets Vol. {n}",
        "{n} More {topic} Hacks"
    ]
    
    # Thresholds for series candidacy
    THRESHOLDS = {
        "views_percentile": 75,      # Top 25% of videos
        "engagement_min": 3.0,       # Minimum engagement rate %
        "comments_min": 5,           # Minimum comments
        "shares_min": 2,             # Minimum shares
        "repeat_within_days": 30     # Suggest repeat within this many days
    }
    
    def __init__(self):
        self.data = self._load()
        self.variety_state = self._load_variety_state()
    
    def _load(self) -> Dict:
        try:
            if SERIES_FILE.exists():
                with open(SERIES_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "series": {},
            "candidates": [],
            "video_performance": [],
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
        with open(SERIES_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_video(self, video_id: str, title: str, category: str,
                      views: int, engagement_rate: float, comments: int = 0,
                      topic_keywords: List[str] = None) -> Dict:
        """
        Analyze a video to determine if it should become a series.
        
        Returns:
            Dict with series recommendation
        """
        # Record performance
        video_data = {
            "id": video_id,
            "title": title,
            "category": category,
            "views": views,
            "engagement_rate": engagement_rate,
            "comments": comments,
            "keywords": topic_keywords or self._extract_keywords(title),
            "timestamp": datetime.now().isoformat()
        }
        self.data["video_performance"].append(video_data)
        
        # Calculate performance percentile
        percentile = self._calculate_percentile(views)
        
        # Check series candidacy
        is_candidate = self._check_candidacy(views, engagement_rate, comments, percentile)
        
        result = {
            "is_series_candidate": is_candidate,
            "performance_percentile": percentile,
            "recommendation": None,
            "suggested_titles": [],
            "optimal_timing": None
        }
        
        if is_candidate:
            # Check if already part of a series
            existing_series = self._find_matching_series(category, topic_keywords)
            
            if existing_series:
                # Add to existing series
                result["recommendation"] = f"Add to series: {existing_series['name']}"
                result["series_id"] = existing_series["id"]
                result["part_number"] = len(existing_series["videos"]) + 1
                result["suggested_titles"] = self._generate_sequel_titles(
                    existing_series["name"], 
                    len(existing_series["videos"]) + 1
                )
                
                # Update series
                self._add_to_series(existing_series["id"], video_data)
            else:
                # Create new series candidate
                result["recommendation"] = "Start a new series!"
                result["suggested_series_name"] = self._suggest_series_name(title, category)
                result["suggested_titles"] = self._generate_sequel_titles(
                    result["suggested_series_name"], 2
                )
                
                # Add to candidates
                self._add_candidate(video_data)
            
            # Calculate optimal timing for next episode
            result["optimal_timing"] = self._calculate_optimal_timing(category)
        
        self._save()
        return result
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract topic keywords from title."""
        # Remove common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "must", "shall",
                     "can", "need", "dare", "ought", "used", "to", "of", "in",
                     "for", "on", "with", "at", "by", "from", "as", "into",
                     "through", "during", "before", "after", "above", "below",
                     "between", "under", "again", "further", "then", "once",
                     "here", "there", "when", "where", "why", "how", "all",
                     "each", "few", "more", "most", "other", "some", "such",
                     "no", "nor", "not", "only", "own", "same", "so", "than",
                     "too", "very", "just", "and", "but", "if", "or", "because",
                     "that", "this", "these", "those", "your", "you", "i", "my"}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return keywords[:5]  # Top 5 keywords
    
    def _calculate_percentile(self, views: int) -> int:
        """Calculate view percentile compared to other videos."""
        all_views = [v["views"] for v in self.data["video_performance"]]
        
        if not all_views:
            return 50  # Default to median
        
        # Sort and find position
        sorted_views = sorted(all_views)
        position = sum(1 for v in sorted_views if v <= views)
        percentile = int((position / len(sorted_views)) * 100)
        
        return percentile
    
    def _check_candidacy(self, views: int, engagement: float, 
                          comments: int, percentile: int) -> bool:
        """Check if video qualifies for series."""
        thresholds = self.THRESHOLDS
        
        # Must be in top percentile by views
        if percentile < thresholds["views_percentile"]:
            return False
        
        # Check engagement
        if engagement < thresholds["engagement_min"]:
            return False
        
        # Comments show strong interest
        if comments >= thresholds["comments_min"]:
            return True
        
        # High views alone can qualify
        if percentile >= 90:
            return True
        
        return False
    
    def _find_matching_series(self, category: str, 
                               keywords: List[str]) -> Optional[Dict]:
        """Find an existing series that matches."""
        for series_id, series in self.data.get("series", {}).items():
            if series["category"] != category:
                continue
            
            # Check keyword overlap
            series_keywords = series.get("keywords", [])
            overlap = len(set(keywords) & set(series_keywords))
            
            if overlap >= 2:  # At least 2 matching keywords
                return {"id": series_id, **series}
        
        return None
    
    def _suggest_series_name(self, title: str, category: str) -> str:
        """Suggest a series name based on video title."""
        keywords = self._extract_keywords(title)
        
        if keywords:
            # Use most specific keyword
            main_topic = keywords[0].title()
            return f"{main_topic} Series"
        
        return f"{category.title()} Tips"
    
    def _generate_sequel_titles(self, series_name: str, part_number: int) -> List[str]:
        """Generate title suggestions for sequel."""
        import random
        
        titles = []
        base_topic = series_name.replace(" Series", "").replace(" Tips", "")
        
        patterns = [
            f"{base_topic} Part {part_number}",
            f"More {base_topic} Secrets (Part {part_number})",
            f"{base_topic} Tips #{part_number}",
            f"You Asked For It: {base_topic} Part {part_number}",
            f"{part_number} More {base_topic} Facts You Need"
        ]
        
        # Shuffle and return top 3
        random.shuffle(patterns)
        return patterns[:3]
    
    def _add_candidate(self, video_data: Dict):
        """Add video to series candidates."""
        candidate = {
            **video_data,
            "added_as_candidate": datetime.now().isoformat(),
            "status": "candidate"
        }
        self.data["candidates"].append(candidate)
        
        # Keep only recent candidates
        self.data["candidates"] = self.data["candidates"][-50:]
    
    def _add_to_series(self, series_id: str, video_data: Dict):
        """Add video to existing series."""
        if series_id in self.data["series"]:
            self.data["series"][series_id]["videos"].append({
                "id": video_data["id"],
                "title": video_data["title"],
                "views": video_data["views"],
                "added": datetime.now().isoformat()
            })
            self.data["series"][series_id]["last_updated"] = datetime.now().isoformat()
    
    def create_series(self, name: str, category: str, 
                      keywords: List[str], first_video: Dict) -> str:
        """Create a new series."""
        series_id = f"series_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.data["series"][series_id] = {
            "name": name,
            "category": category,
            "keywords": keywords,
            "videos": [{
                "id": first_video.get("id"),
                "title": first_video.get("title"),
                "views": first_video.get("views", 0),
                "added": datetime.now().isoformat()
            }],
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active"
        }
        
        self._save()
        safe_print(f"[SERIES] Created: {name}")
        return series_id
    
    def _calculate_optimal_timing(self, category: str) -> Dict:
        """Calculate optimal timing for next series episode."""
        # Analyze past series performance
        base_days = 3  # Default: 3 days between episodes
        
        # Category adjustments
        category_frequency = {
            "psychology": 3,
            "money": 4,
            "productivity": 3,
            "technology": 5,
            "entertainment": 2,
            "motivation": 2
        }
        
        days = category_frequency.get(category.lower(), base_days)
        next_date = datetime.now() + timedelta(days=days)
        
        return {
            "days_until_next": days,
            "recommended_date": next_date.strftime("%Y-%m-%d"),
            "reasoning": f"Optimal for {category} series is {days} days between episodes"
        }
    
    def get_active_series(self) -> List[Dict]:
        """Get all active series."""
        active = []
        for series_id, series in self.data.get("series", {}).items():
            if series.get("status") == "active":
                active.append({
                    "id": series_id,
                    "name": series["name"],
                    "category": series["category"],
                    "episode_count": len(series["videos"]),
                    "total_views": sum(v.get("views", 0) for v in series["videos"]),
                    "last_updated": series.get("last_updated")
                })
        
        return sorted(active, key=lambda x: x["total_views"], reverse=True)
    
    def get_pending_sequels(self) -> List[Dict]:
        """Get series that need new episodes."""
        pending = []
        now = datetime.now()
        
        for series_id, series in self.data.get("series", {}).items():
            if series.get("status") != "active":
                continue
            
            last_updated = datetime.fromisoformat(series.get("last_updated", now.isoformat()))
            days_since = (now - last_updated).days
            
            optimal = self._calculate_optimal_timing(series["category"])
            
            if days_since >= optimal["days_until_next"]:
                pending.append({
                    "series_id": series_id,
                    "series_name": series["name"],
                    "days_overdue": days_since - optimal["days_until_next"],
                    "next_part": len(series["videos"]) + 1,
                    "suggested_titles": self._generate_sequel_titles(
                        series["name"], len(series["videos"]) + 1
                    )
                })
        
        return sorted(pending, key=lambda x: x["days_overdue"], reverse=True)
    
    def get_recommendations(self) -> Dict:
        """Get series recommendations."""
        active = self.get_active_series()
        pending = self.get_pending_sequels()
        candidates = self.data.get("candidates", [])[-10:]
        
        return {
            "active_series": active[:5],
            "pending_sequels": pending[:5],
            "series_candidates": len(candidates),
            "recommendation": self._generate_top_recommendation(pending, candidates)
        }
    
    def _generate_top_recommendation(self, pending: List, candidates: List) -> str:
        """Generate top recommendation."""
        if pending:
            top = pending[0]
            return f"Create Part {top['next_part']} of {top['series_name']} (overdue by {top['days_overdue']} days)"
        elif candidates:
            return f"Consider starting series from {len(candidates)} high-performing videos"
        return "No series recommendations yet. Need more performance data."


# Global instance
_detector = None

def get_series_detector() -> SeriesDetector:
    global _detector
    if _detector is None:
        _detector = SeriesDetector()
    return _detector

def check_series_potential(title: str, views: int, category: str) -> Dict:
    """Check if a video should become a series."""
    return get_series_detector().analyze_video(
        video_id=f"vid_{datetime.now().timestamp()}",
        title=title,
        category=category,
        views=views,
        engagement_rate=4.5
    )


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("SERIES DETECTOR - TEST")
    safe_print("=" * 60)
    
    detector = SeriesDetector()
    
    # Simulate some video performance
    videos = [
        ("5 Psychology Facts That Blow Your Mind", "psychology", 1500, 5.2),
        ("Money Habits of Millionaires", "money", 800, 3.5),
        ("7 More Psychology Facts You Need", "psychology", 2200, 6.1),
    ]
    
    for title, cat, views, engagement in videos:
        result = detector.analyze_video(
            video_id=f"test_{hash(title)}",
            title=title,
            category=cat,
            views=views,
            engagement_rate=engagement,
            comments=10
        )
        
        safe_print(f"\nVideo: {title}")
        safe_print(f"  Percentile: {result['performance_percentile']}%")
        safe_print(f"  Series Candidate: {result['is_series_candidate']}")
        if result["recommendation"]:
            safe_print(f"  Recommendation: {result['recommendation']}")
    
    # Get recommendations
    safe_print("\n" + "=" * 60)
    recs = detector.get_recommendations()
    safe_print(f"Top Recommendation: {recs['recommendation']}")
