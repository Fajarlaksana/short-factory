#!/usr/bin/env python3
"""
Trending Content Generator v2.0
================================

Generates viral content based on:
1. Google Trends RSS Feed (PRIMARY - no PyTrends!)
2. Reddit trending topics
3. AI-generated trends
4. Seasonal/timely content

NOTE: PyTrends has been COMPLETELY REMOVED due to compatibility issues.
We now use the more reliable RSS feed + AI approach.
"""

import os
import sys
import json
import random
import re
from datetime import datetime
from typing import List, Dict, Optional

# Windows-safe print function
def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        clean = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TrendingContentGenerator:
    """
    Generates viral, engaging content based on current trends.
    Uses RSS feed + AI - NO PyTrends (was causing issues).
    """
    
    # Seasonal/timely content boosters
    SEASONAL_TOPICS = {
        1: ["New Year's resolutions", "winter", "gym", "fresh start"],
        2: ["Valentine's Day", "love", "relationships", "dating"],
        3: ["Spring", "March Madness", "St Patrick's"],
        4: ["Easter", "spring break", "taxes"],
        5: ["Mother's Day", "summer planning", "graduation"],
        6: ["Father's Day", "summer", "vacation"],
        7: ["Summer vacation", "beach", "4th of July"],
        8: ["Back to school", "summer ending"],
        9: ["Fall", "football season", "Labor Day"],
        10: ["Halloween", "fall vibes", "pumpkin spice"],
        11: ["Thanksgiving", "Black Friday", "gratitude"],
        12: ["Christmas", "holidays", "New Year's", "gifts", "family"],
    }
    
    def __init__(self):
        self.current_month = datetime.now().month
    
    def get_google_trends(self) -> List[str]:
        """Fetch current Google Trends using RSS feed (NOT PyTrends)."""
        
        # Method 1: RSS Feed (PRIMARY - most reliable)
        try:
            if REQUESTS_AVAILABLE:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/rss+xml,application/xml',
                }
                response = requests.get(
                    'https://trends.google.com/trending/rss?geo=US',
                    headers=headers,
                    timeout=15
                )
                if response.status_code == 200:
                    # Parse RSS for titles
                    titles = re.findall(r'<title>([^<]+)</title>', response.text)
                    # Skip first title (feed title) and get actual trends
                    topics = [t.strip() for t in titles[1:11] if t.strip() and 'Daily Search Trends' not in t]
                    if topics:
                        safe_print(f"[OK] Got {len(topics)} trends from Google RSS feed")
                        return topics
        except Exception as e:
            safe_print(f"[!] RSS feed failed: {str(e)[:50]}")
        
        # Method 2: AI-generated trends
        return self._get_ai_trends()
    
    def _get_ai_trends(self) -> List[str]:
        """Use AI to generate current trending topics."""
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                return self._get_fallback_trends()
            
            client = Groq(api_key=api_key)
            today = datetime.now().strftime("%B %d, %Y")
            
            # v16.8: DYNAMIC MODEL - No hardcoded model names
            try:
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                groq_models = optimizer.get_groq_models(api_key)
                model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
            except:
                model_to_use = "llama-3.3-70b-versatile"
            
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": f"""Today is {today}. 
What are 10 topics that are likely trending RIGHT NOW on social media and Google?

Consider:
- Current events, news, celebrity drama
- Seasonal events (holidays, sports, weather)
- Viral challenges and memes
- Tech/AI news
- Entertainment (movies, music, TV shows)

Return ONLY a JSON array of 10 short topic strings, nothing else.
Example: ["Topic 1", "Topic 2", ...]"""}],
                max_tokens=200,
                temperature=0.7
            )
            
            topics = json.loads(response.choices[0].message.content.strip())
            if topics and len(topics) > 0:
                safe_print(f"[OK] Got {len(topics)} AI-generated trending topics")
                return topics[:10]
        except Exception as e:
            safe_print(f"[!] AI trends failed: {str(e)[:50]}")
        
        return self._get_fallback_trends()
    
    def _get_fallback_trends(self) -> List[str]:
        """Final fallback: evergreen viral topics."""
        today = datetime.now()
        month = today.month
        
        # Dynamic based on current month
        seasonal = self.SEASONAL_TOPICS.get(month, [])
        
        evergreen = [
            "money tips", "relationship advice", "life hacks",
            "psychology facts", "AI technology", "fitness goals"
        ]
        
        return seasonal + evergreen
    
    def get_reddit_trends(self) -> List[str]:
        """Fetch trending topics from Reddit."""
        if not REQUESTS_AVAILABLE:
            return []
        
        subreddits = ['r/AskReddit', 'r/polls', 'r/unpopularopinion']
        topics = []
        
        for subreddit in subreddits:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 ViralShorts/2.0'}
                response = requests.get(
                    f'https://www.reddit.com/{subreddit}/hot.json?limit=10',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for post in data.get('data', {}).get('children', []):
                        title = post.get('data', {}).get('title', '')
                        if len(title) > 10 and len(title) < 200:
                            topics.append(title[:80])
                    
                    if topics:
                        safe_print(f"[OK] Got {len(topics)} topics from Reddit")
                        break
            except Exception as e:
                continue
        
        return topics[:10]
    
    def get_all_trends(self) -> List[str]:
        """Get trends from all sources combined."""
        all_trends = []
        
        # Google RSS trends
        google = self.get_google_trends()
        all_trends.extend(google)
        
        # Reddit trends
        reddit = self.get_reddit_trends()
        all_trends.extend(reddit)
        
        # Seasonal topics
        seasonal = self.SEASONAL_TOPICS.get(self.current_month, [])
        all_trends.extend(seasonal)
        
        # Deduplicate
        seen = set()
        unique = []
        for t in all_trends:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        
        return unique


def main():
    """Test trend fetching."""
    generator = TrendingContentGenerator()
    
    safe_print("\n=== Google Trends (RSS) ===")
    google = generator.get_google_trends()
    for i, t in enumerate(google[:5], 1):
        safe_print(f"  {i}. {t}")
    
    safe_print("\n=== Reddit Trends ===")
    reddit = generator.get_reddit_trends()
    for i, t in enumerate(reddit[:5], 1):
        safe_print(f"  {i}. {t}")
    
    safe_print("\n=== All Combined Trends ===")
    all_trends = generator.get_all_trends()
    safe_print(f"Total: {len(all_trends)} unique trends")


if __name__ == "__main__":
    main()
