#!/usr/bin/env python3
"""
ViralShorts Factory - Google Trends Integration v17.9.50
=========================================================

Fetches real-time trending topics from Google Trends.
Uses the free RSS feed (no API key required!).

Features:
- Fetches daily trending searches
- Categorizes trends by topic
- Suggests content angles
- Integrates with topic generation
"""

import os
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
TRENDS_CACHE_FILE = STATE_DIR / "google_trends_cache.json"


class GoogleTrendsFetcher:
    """
    Fetches trending topics from Google Trends RSS feed.
    No API key required - uses public RSS feeds.
    """
    
    # Google Trends RSS feeds by country
    TRENDS_FEEDS = {
        "US": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
        "UK": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=GB",
        "CA": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=CA",
        "AU": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=AU",
    }
    
    # Category keywords for classification
    CATEGORY_KEYWORDS = {
        "psychology": ["mind", "brain", "mental", "therapy", "anxiety", "depression", 
                      "personality", "behavior", "emotion", "psychology", "mindset"],
        "money": ["stock", "crypto", "bitcoin", "investment", "economy", "inflation",
                 "money", "wealth", "finance", "market", "trading", "bank"],
        "technology": ["ai", "tech", "apple", "google", "microsoft", "software",
                      "robot", "computer", "digital", "app", "device", "gadget"],
        "health": ["health", "fitness", "diet", "workout", "medical", "doctor",
                  "disease", "treatment", "exercise", "nutrition", "wellness"],
        "entertainment": ["movie", "music", "celebrity", "concert", "netflix",
                         "game", "streaming", "album", "tour", "release"],
        "sports": ["football", "basketball", "soccer", "nfl", "nba", "baseball",
                  "tennis", "golf", "olympics", "championship", "match"],
        "politics": ["election", "president", "congress", "vote", "policy",
                    "government", "democrat", "republican", "law", "court"],
    }
    
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached trends."""
        try:
            if TRENDS_CACHE_FILE.exists():
                with open(TRENDS_CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[TRENDS] Cache load error: {e}")
        return {"trends": [], "last_fetched": None}
    
    def _save_cache(self):
        """Save trends to cache."""
        self.cache["last_fetched"] = datetime.now().isoformat()
        try:
            with open(TRENDS_CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            safe_print(f"[TRENDS] Cache save error: {e}")
    
    def fetch_trends(self, countries: List[str] = None, 
                     max_per_country: int = 10) -> List[Dict]:
        """
        Fetch trending topics from Google Trends RSS feeds.
        
        Args:
            countries: List of country codes (default: ["US", "UK"])
            max_per_country: Max trends per country
        
        Returns:
            List of trending topics with metadata
        """
        if countries is None:
            countries = ["US", "UK"]
        
        all_trends = []
        
        for country in countries:
            feed_url = self.TRENDS_FEEDS.get(country)
            if not feed_url:
                continue
            
            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    trends = self._parse_rss(response.text, country, max_per_country)
                    all_trends.extend(trends)
                    safe_print(f"[TRENDS] Fetched {len(trends)} trends from {country}")
                else:
                    safe_print(f"[TRENDS] {country} feed returned {response.status_code}")
            except Exception as e:
                safe_print(f"[TRENDS] {country} fetch error: {e}")
        
        # Deduplicate by title
        seen = set()
        unique_trends = []
        for trend in all_trends:
            if trend["title"].lower() not in seen:
                seen.add(trend["title"].lower())
                unique_trends.append(trend)
        
        self.cache["trends"] = unique_trends
        self._save_cache()
        
        return unique_trends
    
    def _parse_rss(self, rss_content: str, country: str, 
                   max_items: int) -> List[Dict]:
        """Parse Google Trends RSS feed."""
        trends = []
        
        try:
            root = ElementTree.fromstring(rss_content)
            
            for item in root.findall(".//item")[:max_items]:
                title = item.find("title")
                traffic = item.find("{https://trends.google.com/trends/trendingsearches/daily}approx_traffic")
                news_item = item.find("{https://trends.google.com/trends/trendingsearches/daily}news_item")
                
                if title is not None:
                    trend_data = {
                        "title": title.text,
                        "country": country,
                        "traffic": traffic.text if traffic is not None else "Unknown",
                        "category": self._classify_trend(title.text),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Get related news headline if available
                    if news_item is not None:
                        headline = news_item.find(
                            "{https://trends.google.com/trends/trendingsearches/daily}news_item_title"
                        )
                        if headline is not None:
                            trend_data["news_headline"] = headline.text
                    
                    trends.append(trend_data)
        
        except Exception as e:
            safe_print(f"[TRENDS] RSS parse error: {e}")
        
        return trends
    
    def _classify_trend(self, title: str) -> str:
        """Classify trend into content category."""
        title_lower = title.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                return category
        
        return "general"
    
    def get_trending_for_category(self, category: str, 
                                   limit: int = 5) -> List[Dict]:
        """Get trending topics for a specific category."""
        # Use cache if fresh (within 6 hours)
        if self.cache.get("last_fetched"):
            try:
                last = datetime.fromisoformat(self.cache["last_fetched"])
                if (datetime.now() - last).total_seconds() < 6 * 3600:
                    cached = [t for t in self.cache["trends"] 
                             if t["category"] == category][:limit]
                    if cached:
                        return cached
            except:
                pass
        
        # Fetch fresh trends
        trends = self.fetch_trends()
        return [t for t in trends if t["category"] == category][:limit]
    
    def suggest_video_topics(self, limit: int = 10) -> List[Dict]:
        """
        Suggest video topics based on current trends.
        
        Returns topics with suggested angles for viral potential.
        """
        trends = self.fetch_trends()
        suggestions = []
        
        for trend in trends[:limit]:
            title = trend["title"]
            category = trend["category"]
            
            # Generate content angles based on category
            angles = self._get_content_angles(title, category)
            
            suggestions.append({
                "trend": title,
                "category": category,
                "traffic": trend.get("traffic", "Unknown"),
                "content_angles": angles,
                "urgency": "high" if "+" in str(trend.get("traffic", "")) else "normal"
            })
        
        return suggestions
    
    def _get_content_angles(self, trend: str, category: str) -> List[str]:
        """Generate content angles for a trending topic."""
        angles = []
        
        # Universal angles
        angles.append(f"The truth about {trend} nobody talks about")
        angles.append(f"What {trend} reveals about human psychology")
        
        # Category-specific angles
        if category == "psychology":
            angles.append(f"The psychological reason behind {trend}")
        elif category == "money":
            angles.append(f"How {trend} affects your wallet")
        elif category == "technology":
            angles.append(f"Why {trend} changes everything in tech")
        elif category == "health":
            angles.append(f"What {trend} means for your health")
        elif category == "politics":
            angles.append(f"The hidden psychology behind {trend}")
        else:
            angles.append(f"5 things you need to know about {trend}")
        
        return angles


# Global instance
_fetcher = None


def get_trends_fetcher() -> GoogleTrendsFetcher:
    """Get global trends fetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = GoogleTrendsFetcher()
    return _fetcher


def fetch_trending_topics(category: str = None, limit: int = 10) -> List[Dict]:
    """
    Convenience function to fetch trending topics.
    
    Args:
        category: Optional category filter
        limit: Maximum topics to return
    
    Returns:
        List of trending topics
    """
    fetcher = get_trends_fetcher()
    
    if category:
        return fetcher.get_trending_for_category(category, limit)
    else:
        return fetcher.fetch_trends()[:limit]


# Test
if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("GOOGLE TRENDS FETCHER - TEST")
    safe_print("=" * 60)
    
    fetcher = GoogleTrendsFetcher()
    
    # Fetch trends
    safe_print("\n[FETCHING] Getting trending topics...")
    trends = fetcher.fetch_trends()
    
    safe_print(f"\nFound {len(trends)} trending topics:\n")
    for i, trend in enumerate(trends[:10], 1):
        safe_print(f"  {i}. [{trend['category']}] {trend['title']} ({trend['traffic']})")
    
    # Get suggestions
    safe_print("\n[SUGGESTIONS] Video topic ideas:\n")
    suggestions = fetcher.suggest_video_topics(5)
    for s in suggestions:
        safe_print(f"  Trend: {s['trend']}")
        safe_print(f"    Angles: {s['content_angles'][:2]}")
        safe_print("")
