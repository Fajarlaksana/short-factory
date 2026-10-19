#!/usr/bin/env python3
"""
ViralShorts Factory - Multi-Source Trend Fetcher
=================================================

Fetches trending topics from MULTIPLE sources for maximum relevance:
1. Google Trends (RSS fallback when API blocked)
2. Reddit trending (r/all, r/todayilearned, etc.)
3. Twitter/X trending (via nitter/scraping)
4. YouTube trending
5. AI-generated trends based on current events

NO HARDCODED TOPICS - Everything is dynamically fetched!
"""

import os
import json
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import re


def safe_print(msg: str):
    """Print with Unicode fallback for Windows."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


@dataclass
class TrendingTopic:
    """A trending topic with metadata."""
    topic: str
    source: str  # google, reddit, twitter, youtube, ai
    score: int  # Relevance score 1-100
    category: str  # news, entertainment, science, tech, etc.
    description: str
    keywords: List[str]


class GoogleTrendsFetcher:
    """
    Fetch Google Trends using RSS feed (more reliable than pytrends).
    
    RSS feeds are NOT blocked like the API!
    """
    
    RSS_URLS = {
        "us": "https://trends.google.com/trending/rss?geo=US",
        "uk": "https://trends.google.com/trending/rss?geo=GB",
        "global": "https://trends.google.com/trending/rss?geo=",
    }
    
    def fetch(self, region: str = "us", count: int = 10) -> List[TrendingTopic]:
        """Fetch trending topics from Google Trends RSS."""
        topics = []
        
        url = self.RSS_URLS.get(region, self.RSS_URLS["us"])
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse RSS XML
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item')[:count]:
                    title = item.find('title')
                    description = item.find('description')
                    
                    if title is not None:
                        topic_text = title.text or ""
                        desc_text = description.text if description is not None else ""
                        
                        # Extract keywords
                        keywords = [w.lower() for w in topic_text.split() if len(w) > 3]
                        
                        # v17.7.17: Fix None description bug
                        safe_desc = (desc_text or topic_text)[:200]
                        
                        topics.append(TrendingTopic(
                            topic=topic_text,
                            source="google",
                            score=90 - len(topics) * 5,  # Higher score for top trends
                            category=self._categorize(topic_text),
                            description=safe_desc,
                            keywords=keywords[:5]
                        ))
                
                safe_print(f"[OK] Fetched {len(topics)} trends from Google RSS")
            else:
                safe_print(f"[!] Google RSS returned {response.status_code}")
                
        except Exception as e:
            safe_print(f"[!] Google Trends RSS error: {e}")
        
        return topics
    
    def _categorize(self, text: str) -> str:
        """Categorize a topic based on keywords."""
        text_lower = text.lower()
        
        categories = {
            "tech": ["ai", "tech", "apple", "google", "microsoft", "phone", "app"],
            "entertainment": ["movie", "film", "celebrity", "actor", "singer", "album"],
            "sports": ["game", "match", "player", "team", "nba", "nfl", "soccer"],
            "politics": ["president", "election", "congress", "vote", "government"],
            "science": ["study", "research", "space", "nasa", "discovery"],
            "health": ["health", "covid", "vaccine", "doctor", "medical"],
        }
        
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return "general"


class RedditTrendsFetcher:
    """
    Fetch trending topics from Reddit.
    
    Uses Reddit's JSON API (no auth needed for public data).
    """
    
    SUBREDDITS = [
        "todayilearned",
        "Showerthoughts", 
        "LifeProTips",
        "interestingasfuck",
        "Damnthatsinteresting",
    ]
    
    def fetch(self, count: int = 10) -> List[TrendingTopic]:
        """Fetch trending posts from relevant subreddits."""
        topics = []
        
        for subreddit in self.SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
                headers = {
                    "User-Agent": "ViralShortsBot/1.0"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    for post in posts[:2]:  # Top 2 from each subreddit
                        post_data = post.get("data", {})
                        title = post_data.get("title", "")
                        score = post_data.get("score", 0)
                        
                        if title and score > 1000:  # Only popular posts
                            # Clean title
                            title = re.sub(r'\[.*?\]', '', title).strip()
                            title = re.sub(r'^TIL\s+', '', title).strip()
                            title = re.sub(r'^LPT:\s*', '', title).strip()
                            
                            keywords = [w.lower() for w in title.split() if len(w) > 3][:5]
                            
                            topics.append(TrendingTopic(
                                topic=title[:100],
                                source="reddit",
                                score=min(90, score // 1000),
                                category=self._subreddit_category(subreddit),
                                description=f"From r/{subreddit} with {score} upvotes",
                                keywords=keywords
                            ))
                
            except Exception as e:
                print(f"⚠️ Reddit r/{subreddit} error: {e}")
        
        print(f"✅ Fetched {len(topics)} trends from Reddit")
        return topics[:count]
    
    def _subreddit_category(self, subreddit: str) -> str:
        """Map subreddit to category."""
        mapping = {
            "todayilearned": "facts",
            "Showerthoughts": "psychology",
            "LifeProTips": "life_hack",
            "interestingasfuck": "facts",
            "Damnthatsinteresting": "facts",
        }
        return mapping.get(subreddit, "general")


class AITrendGenerator:
    """
    Generate trend predictions using AI.
    
    Uses current date/time context to predict what's relevant.
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def generate(self, count: int = 5) -> List[TrendingTopic]:
        """Generate AI-predicted trending topics."""
        if not self.groq_key:
            return []
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            now = datetime.now()
            
            prompt = f"""You are a viral content strategist analyzing what's trending RIGHT NOW.

Current context:
- Date: {now.strftime("%B %d, %Y")}
- Day: {now.strftime("%A")}
- Time of day: {"morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"}

Based on your knowledge of:
1. Current events and news
2. Seasonal trends
3. Social media patterns
4. Evergreen viral topics

Generate {count} topics that would go VIRAL on short-form video platforms TODAY.

For each topic, provide:
- A specific, actionable topic (not vague)
- The psychological reason it would go viral
- Keywords for B-roll footage

Return JSON array:
[{{"topic": "specific topic", "category": "psychology|money|health|facts|life_hack", "description": "why viral", "keywords": ["visual1", "visual2"]}}]

Only return valid JSON, no markdown."""

            # v17.8: Use dynamic model selection instead of hardcoded
            try:
                from quota_optimizer import get_best_groq_model
                model = get_best_groq_model(self.groq_key)
            except ImportError:
                try:
                    from src.ai.model_helper import get_dynamic_groq_model
                    model = get_dynamic_groq_model()
                except:
                    model = "llama-3.3-70b-versatile"  # Emergency only
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            data = json.loads(result.strip())
            
            topics = []
            for item in data:
                topics.append(TrendingTopic(
                    topic=item.get("topic", ""),
                    source="ai",
                    score=85,
                    category=item.get("category", "facts"),
                    description=item.get("description", ""),
                    keywords=item.get("keywords", [])
                ))
            
            print(f"✅ Generated {len(topics)} AI trends")
            return topics
            
        except Exception as e:
            print(f"⚠️ AI trend generation error: {e}")
            return []


class MultiTrendFetcher:
    """
    Main class that combines all trend sources.
    
    Fetches from multiple sources and ranks by relevance.
    Sources: Google RSS, Reddit, Twitter, AI
    """
    
    def __init__(self):
        self.google = GoogleTrendsFetcher()
        self.reddit = RedditTrendsFetcher()
        self.ai = AITrendGenerator()
        
        # Import Twitter fetcher
        try:
            from trending_twitter import TwitterTrendsFetcher
            self.twitter = TwitterTrendsFetcher()
            self.has_twitter = True
        except ImportError:
            self.twitter = None
            self.has_twitter = False
    
    def fetch_all(self, count: int = 10) -> List[TrendingTopic]:
        """
        Fetch trends from all sources and merge.
        
        Returns the top trends sorted by score.
        Sources: Google RSS, Reddit, Twitter, AI
        """
        all_topics = []
        
        # 1. Google Trends RSS (most reliable for current events)
        try:
            all_topics.extend(self.google.fetch(count=5))
        except Exception as e:
            print(f"[!] Google fetch failed: {e}")
        
        # 2. Reddit (great for interesting facts/tips)
        try:
            all_topics.extend(self.reddit.fetch(count=5))
        except Exception as e:
            print(f"[!] Reddit fetch failed: {e}")
        
        # 3. Twitter/X (viral topics and hashtags)
        if self.has_twitter and self.twitter:
            try:
                twitter_trends = self.twitter.fetch(count=5)
                for t in twitter_trends:
                    all_topics.append(TrendingTopic(
                        topic=t.topic,
                        source="twitter",
                        score=85,
                        category=t.category,
                        description=f"Trending on Twitter (~{t.tweet_volume:,} tweets)",
                        keywords=[t.topic.replace("#", "").lower()]
                    ))
            except Exception as e:
                print(f"[!] Twitter fetch failed: {e}")
        
        # 4. AI-generated (fills gaps and adds creativity)
        try:
            all_topics.extend(self.ai.generate(count=5))
        except Exception as e:
            print(f"[!] AI generation failed: {e}")
        
        # Sort by score
        all_topics.sort(key=lambda x: x.score, reverse=True)
        
        # Remove duplicates (similar topics)
        unique_topics = []
        seen_keywords = set()
        
        for topic in all_topics:
            topic_lower = topic.topic.lower()
            key_words = set(topic_lower.split()[:3])
            
            if not key_words.intersection(seen_keywords):
                unique_topics.append(topic)
                seen_keywords.update(key_words)
        
        print(f"\n📊 Total unique trends: {len(unique_topics)}")
        return unique_topics[:count]
    
    def get_best_for_video_type(self, video_type: str) -> Optional[TrendingTopic]:
        """Get the best trending topic for a specific video type."""
        topics = self.fetch_all(count=20)
        
        # Filter by category match
        matching = [t for t in topics if t.category == video_type]
        
        if matching:
            return matching[0]
        
        # Fallback to any topic
        return topics[0] if topics else None


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Source Trend Fetcher Test")
    print("=" * 60)
    
    fetcher = MultiTrendFetcher()
    
    # Test individual sources
    print("\n📡 Testing Google Trends RSS...")
    google_trends = fetcher.google.fetch(count=3)
    for t in google_trends:
        print(f"   [{t.score}] {t.topic}")
    
    print("\n📡 Testing Reddit...")
    reddit_trends = fetcher.reddit.fetch(count=3)
    for t in reddit_trends:
        print(f"   [{t.score}] {t.topic[:50]}...")
    
    print("\n📡 Testing AI generation...")
    ai_trends = fetcher.ai.generate(count=3)
    for t in ai_trends:
        print(f"   [{t.score}] {t.topic}")
    
    print("\n" + "=" * 60)
    print("📊 Combined Top Trends:")
    print("=" * 60)
    
    all_trends = fetcher.fetch_all(count=5)
    for i, t in enumerate(all_trends, 1):
        print(f"\n{i}. [{t.source.upper()}] {t.topic}")
        print(f"   Category: {t.category} | Score: {t.score}")
        print(f"   Keywords: {', '.join(t.keywords[:3])}")

