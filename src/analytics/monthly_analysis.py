#!/usr/bin/env python3
"""
Monthly Viral Analysis Script v9.5
Analyzes top-performing AI-generated YouTube Shorts and extracts patterns
for the ViralShorts Factory to use.

v9.5 Enhancements:
- Seasonal content calendar integration (#27)
- Cross-platform analytics (#32)
- Series detection for high performers (#33)
- Enhanced hook word analysis (#28)

v9.0 Enhancements:
- Competitor tracking (#24) - Track specific competitor channels over time
- Better pattern extraction with expanded analysis
- Content recycling identification (#23) - Find our underperforming content to recycle
"""

import os
import json
import requests
import re
from datetime import datetime
from pathlib import Path

# API Keys - Use OAuth credentials (same as upload)
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ANALYSIS_FILE = Path("data/persistent/monthly_analysis.json")
VIRAL_PATTERNS_FILE = Path("data/persistent/viral_patterns.json")
COMPETITOR_TRACKING_FILE = Path("data/persistent/competitor_tracking.json")
RECYCLE_CANDIDATES_FILE = Path("data/persistent/recycle_candidates.json")

# YouTube access token (refreshed at runtime)
_youtube_access_token = None


def safe_print(msg):
    """Print message safely, handling Unicode."""
    try:
        print(msg)
    except:
        print(msg.encode('ascii', 'ignore').decode())


def get_youtube_access_token():
    """Get YouTube access token using OAuth refresh token."""
    global _youtube_access_token
    if _youtube_access_token:
        return _youtube_access_token
    
    if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
        safe_print("[!] Missing YouTube OAuth credentials")
        return None
    
    try:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": YOUTUBE_CLIENT_ID,
                "client_secret": YOUTUBE_CLIENT_SECRET,
                "refresh_token": YOUTUBE_REFRESH_TOKEN,
                "grant_type": "refresh_token"
            },
            timeout=10
        )
        if response.status_code == 200:
            _youtube_access_token = response.json().get("access_token")
            safe_print("[OK] YouTube OAuth token refreshed")
            return _youtube_access_token
        else:
            safe_print(f"[!] Token refresh failed: {response.status_code}")
    except Exception as e:
        safe_print(f"[!] Token refresh error: {e}")
    return None


def youtube_search(query, max_results=10):
    """Search YouTube for videos using OAuth."""
    token = get_youtube_access_token()
    if not token:
        safe_print("[!] No YouTube access token")
        return []
    
    url = "https://www.googleapis.com/youtube/v3/search"
    # v17.9.17: Use dynamic date (past 6 months) instead of hardcoded year
    from datetime import datetime, timedelta
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00Z")
    
    params = {
        "q": query,
        "part": "snippet",
        "type": "video",
        "videoDuration": "short",  # Shorts only
        "order": "viewCount",
        "maxResults": max_results,
        "publishedAfter": six_months_ago  # Dynamic, not hardcoded
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            safe_print(f"[!] Search failed: {response.status_code}")
    except Exception as e:
        safe_print(f"[!] Search error: {e}")
    return []


def get_video_details(video_ids):
    """Get detailed stats for videos using OAuth."""
    token = get_youtube_access_token()
    if not token or not video_ids:
        return []
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": ",".join(video_ids),
        "part": "statistics,snippet,contentDetails"
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            safe_print(f"[!] Details failed: {response.status_code}")
    except Exception as e:
        safe_print(f"[!] Details error: {e}")
    return []


def analyze_with_ai(videos_data):
    """Use AI for MICRO-LEVEL analysis of successful videos.
    Extracts GOLD-VALUE: tricks, baits, hacks, psychological triggers.
    """
    if not GROQ_API_KEY or not videos_data:
        return {}
    
    prompt = f"""You are a viral video reverse-engineer. Extract EVERY secret from these successful YouTube Shorts:

VIDEO DATA (from viral competitors):
{json.dumps(videos_data, indent=2)}

Extract GOLD-VALUE patterns - the TRICKS, BAITS, and HACKS that made these go viral:

1. **TITLE TRICKS**: Numbers? Power words? Curiosity gaps? Click-bait techniques?
2. **HOOK HACKS**: What grabs attention in first 1-2 seconds? Shocking statements? Questions?
3. **PSYCHOLOGICAL TRIGGERS**: FOMO? Curiosity? Controversy? Social proof? Fear? Greed?
4. **ENGAGEMENT BAITS**: How do they farm comments? "Comment 1 if...", "Tag someone who..."
5. **CONTENT SECRETS**: What makes the content irresistible? Secrets? Hacks? Hidden truths?
6. **RETENTION TRICKS**: How do they keep viewers watching? Open loops? Countdowns?
7. **VIRALITY HACKS**: Shareability factors? Controversy? Relatability?
8. **MUSIC/MOOD**: Dramatic? Mysterious? Upbeat? What amplifies emotion?
9. **TOPIC ANGLES**: What specific angles within categories work best?
10. **CTA TRICKS**: How do they convert viewers to subscribers/commenters?

Return comprehensive GOLD-VALUE JSON:
{{
    "title_tricks": ["use X number", "curiosity gap with...", ...],
    "title_patterns": ["pattern with {{placeholder}}", ...],
    "hook_hacks": ["start with question", "shocking first word", ...],
    "psychological_triggers": ["fomo", "curiosity", "controversy", ...],
    "engagement_baits": ["comment 1 if you...", "tag someone who...", ...],
    "retention_tricks": ["open loop", "countdown", ...],
    "virality_hacks": ["make it shareable by...", ...],
    "top_categories": ["category1", "category2", ...],
    "hook_patterns": ["specific hook technique", ...],
    "music_moods_that_work": ["dramatic", "mysterious", ...],
    "visual_keywords": ["keyword for b-roll", ...],
    "voice_styles": ["energetic", "calm", ...],
    "optimal_phrase_count": number,
    "optimal_duration_seconds": number,
    "content_themes": ["secrets about X", "hacks for Y", ...],
    "insights": ["key gold-value insight 1", "insight 2", ...]
}}

Be SPECIFIC. Extract the SECRETS that make these videos viral. JSON ONLY."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",  # Best model for analysis
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                return json.loads(match.group())
    except Exception as e:
        safe_print(f"[!] AI analysis error: {e}")
    return {}


def generate_search_queries_ai():
    """AI generates search queries - NO HARDCODING!"""
    if not GROQ_API_KEY:
        return ["viral shorts trending", "facts shorts viral"]  # No year-specific
    
    prompt = """You are a YouTube search expert. Generate 5-7 search queries to find the most viral AI-generated YouTube Shorts from the past year.

We want to find:
- Fact-based Shorts with millions of views
- AI voiceover content that went viral
- Psychology, money, life hack content
- Any AI-generated short-form content that succeeded

Return a JSON array of search queries:
["query 1", "query 2", ...]

Be specific and use terms that will find HIGH-VIEW viral content.
JSON ARRAY ONLY."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 200
            },
            timeout=10
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                queries = json.loads(match.group())
                if queries and len(queries) >= 3:
                    safe_print(f"[AI] Generated {len(queries)} search queries")
                    return queries
    except Exception as e:
        safe_print(f"[!] AI query generation failed: {e}")
    
    # Minimal fallback only if AI completely fails
    return ["viral shorts million views", "trending facts shorts"]


def identify_recycle_candidates(analytics_file=Path("data/persistent/analytics_state.json")):
    """v9.0: Find our underperforming videos that could be recycled with a new angle.
    Enhancement #23: Failed content recycling.
    """
    if not analytics_file.exists():
        return []
    
    try:
        with open(analytics_file, 'r') as f:
            analytics = json.load(f)
        
        videos = analytics.get("videos", [])
        avg_views = analytics.get("avg_views", 100)
        
        # Find videos with less than 25% of average views
        threshold = avg_views * 0.25
        underperformers = [
            v for v in videos 
            if v.get("views", 0) < threshold and v.get("title")
        ]
        
        safe_print(f"[RECYCLE] Found {len(underperformers)} underperforming videos")
        return underperformers[:5]  # Return top 5 candidates
        
    except Exception as e:
        safe_print(f"[!] Recycle identification error: {e}")
        return []


def generate_recycle_suggestions(underperformers, groq_key):
    """v9.0: AI suggests how to recycle underperforming content."""
    if not groq_key or not underperformers:
        return {}
    
    prompt = f"""You are a content recycling expert. These videos underperformed - diagnose WHY and suggest a FRESH ANGLE:

UNDERPERFORMING VIDEOS:
{json.dumps(underperformers, indent=2)}

For each video, provide:
1. DIAGNOSIS: Why did it likely fail? (weak hook? boring topic? bad timing?)
2. SALVAGEABLE?: Is the core idea worth recycling?
3. FRESH ANGLE: A completely new approach to the same topic
4. NEW HOOK: A more compelling first sentence
5. NEW TITLE: A more clickable title

Return JSON:
{{
    "recycle_suggestions": [
        {{
            "original_title": "...",
            "diagnosis": "why it failed",
            "salvageable": true/false,
            "fresh_angle": "new approach",
            "new_hook": "better hook",
            "new_title": "better title"
        }}
    ]
}}

JSON ONLY."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=20
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                return json.loads(match.group())
    except Exception as e:
        safe_print(f"[!] Recycle suggestion error: {e}")
    return {}


def track_competitors():
    """v9.0: Track competitor channels over time to spot trends.
    Enhancement #24: Competitor monitoring.
    """
    competitor_data = {}
    
    if COMPETITOR_TRACKING_FILE.exists():
        try:
            with open(COMPETITOR_TRACKING_FILE, 'r') as f:
                competitor_data = json.load(f)
        except:
            pass
    
    # AI identifies potential competitors from our search results
    # (channels that appear frequently in viral searches)
    safe_print("[COMPETITORS] Tracking competitor trends...")
    
    return competitor_data


def main():
    """Main analysis flow (v9.5 enhanced)."""
    safe_print("=" * 60)
    safe_print("MONTHLY VIRAL ANALYSIS v9.5")
    safe_print(f"Date: {datetime.now().isoformat()}")
    safe_print("v9.5: Seasonal, Cross-platform, Series, Hook words")
    safe_print("v9.0: Competitor tracking, Content recycling")
    safe_print("=" * 60)

    # Ensure directories exist
    Path("data/persistent").mkdir(parents=True, exist_ok=True)
    Path("data/analysis").mkdir(parents=True, exist_ok=True)

    # AI-generated search queries - NOT HARDCODED!
    safe_print("\n[AI] Generating search queries...")
    search_queries = generate_search_queries_ai()
    safe_print(f"[OK] Will search: {search_queries}")

    all_videos = []
    seen_ids = set()

    for query in search_queries:
        safe_print(f"\n[SEARCH] {query}")
        results = youtube_search(query, max_results=5)
        
        for item in results:
            vid_id = item.get("id", {}).get("videoId")
            if vid_id and vid_id not in seen_ids:
                seen_ids.add(vid_id)
                all_videos.append({
                    "id": vid_id,
                    "title": item.get("snippet", {}).get("title", ""),
                    "channel": item.get("snippet", {}).get("channelTitle", ""),
                    "published": item.get("snippet", {}).get("publishedAt", "")
                })

    safe_print(f"\n[FOUND] {len(all_videos)} unique videos")

    # Get detailed stats
    if all_videos:
        video_ids = [v["id"] for v in all_videos[:20]]  # Limit API calls
        details = get_video_details(video_ids)
        
        # Merge stats
        stats_map = {d["id"]: d for d in details}
        for video in all_videos:
            if video["id"] in stats_map:
                stats = stats_map[video["id"]]
                video["views"] = int(stats.get("statistics", {}).get("viewCount", 0))
                video["likes"] = int(stats.get("statistics", {}).get("likeCount", 0))
                video["comments"] = int(stats.get("statistics", {}).get("commentCount", 0))

    # Sort by views
    all_videos.sort(key=lambda x: x.get("views", 0), reverse=True)
    top_videos = all_videos[:10]

    safe_print("\n[TOP VIDEOS]")
    for i, v in enumerate(top_videos, 1):
        safe_print(f"  {i}. {v.get('views', 0):,} views - {v.get('title', 'N/A')[:50]}")

    # AI Analysis
    safe_print("\n[AI ANALYSIS]")
    analysis = analyze_with_ai(top_videos)

    if analysis:
        safe_print(f"  Title patterns: {len(analysis.get('title_patterns', []))}")
        safe_print(f"  Top categories: {analysis.get('top_categories', [])}")
        safe_print(f"  Key insights: {len(analysis.get('insights', []))}")
        
        # Save analysis results
        analysis_result = {
            "date": datetime.now().isoformat(),
            "videos_analyzed": len(top_videos),
            "top_video_views": top_videos[0].get("views", 0) if top_videos else 0,
            "patterns": analysis,
            "raw_videos": top_videos
        }
        
        with open(ANALYSIS_FILE, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        # Update viral patterns file for use by video generator
        existing_patterns = {}
        if VIRAL_PATTERNS_FILE.exists():
            try:
                with open(VIRAL_PATTERNS_FILE, 'r') as f:
                    existing_patterns = json.load(f)
            except:
                pass
        
        # Merge ALL micro-level patterns including GOLD-VALUE fields
        array_keys = [
            "title_patterns", "hook_patterns", "engagement_baits",
            "music_moods_that_work", "visual_keywords", "voice_styles",
            "content_themes",
            # GOLD-VALUE fields
            "title_tricks", "hook_hacks", "psychological_triggers",
            "retention_tricks", "virality_hacks"
        ]
        for key in array_keys:
            if key in analysis:
                existing = existing_patterns.get(key, [])
                for item in analysis[key]:
                    if item not in existing:
                        existing.append(item)
                existing_patterns[key] = existing[-20:]  # Keep last 20
        
        # Direct value updates
        if analysis.get("top_categories"):
            existing_patterns["proven_categories"] = analysis["top_categories"]
        
        if analysis.get("insights"):
            existing_patterns["latest_insights"] = analysis["insights"]
        
        if analysis.get("optimal_duration_seconds"):
            existing_patterns["optimal_duration"] = analysis["optimal_duration_seconds"]
        
        if analysis.get("optimal_phrase_count"):
            existing_patterns["optimal_phrase_count"] = analysis["optimal_phrase_count"]
        
        existing_patterns["last_updated"] = datetime.now().isoformat()
        existing_patterns["ai_generated"] = True
        existing_patterns["source"] = "youtube_analysis"
        
        with open(VIRAL_PATTERNS_FILE, 'w') as f:
            json.dump(existing_patterns, f, indent=2)
        
        safe_print("\n[SAVED] Patterns updated for video generation")
    else:
        safe_print("[!] AI analysis returned no results")

    # v9.0: Content recycling analysis
    safe_print("\n[RECYCLE ANALYSIS]")
    underperformers = identify_recycle_candidates()
    if underperformers:
        recycle_data = generate_recycle_suggestions(underperformers, GROQ_API_KEY)
        if recycle_data.get("recycle_suggestions"):
            with open(RECYCLE_CANDIDATES_FILE, 'w') as f:
                json.dump({
                    "date": datetime.now().isoformat(),
                    "candidates": recycle_data["recycle_suggestions"]
                }, f, indent=2)
            safe_print(f"  Found {len(recycle_data['recycle_suggestions'])} recycle candidates")
    
    # v9.0: Competitor tracking
    competitor_data = track_competitors()
    
    # Update with new competitor sightings from this analysis
    for video in top_videos:
        channel = video.get("channel", "Unknown")
        if channel not in competitor_data:
            competitor_data[channel] = {
                "first_seen": datetime.now().isoformat(),
                "videos_seen": 0,
                "total_views": 0
            }
        competitor_data[channel]["videos_seen"] += 1
        competitor_data[channel]["total_views"] += video.get("views", 0)
        competitor_data[channel]["last_seen"] = datetime.now().isoformat()
    
    with open(COMPETITOR_TRACKING_FILE, 'w') as f:
        json.dump(competitor_data, f, indent=2)
    safe_print(f"\n[COMPETITORS] Tracking {len(competitor_data)} channels")

    # v9.5: Extract hook words from top-performing titles
    safe_print("\n[v9.5] Hook Word Analysis")
    hook_word_file = Path("data/persistent/hook_word_performance.json")
    hook_data = {"words": {}, "last_updated": datetime.now().isoformat()}
    if hook_word_file.exists():
        try:
            with open(hook_word_file, 'r') as f:
                hook_data = json.load(f)
        except:
            pass
    
    # Learn from competitor hook words
    avg_views = sum(v.get("views", 0) for v in top_videos) / len(top_videos) if top_videos else 1
    for video in top_videos:
        title = video.get("title", "")
        views = video.get("views", 0)
        if title and avg_views > 0:
            performance = views / avg_views
            words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
            for word in words:
                if word not in hook_data["words"]:
                    hook_data["words"][word] = {"total_performance": 0, "count": 0, "source": "competitor"}
                hook_data["words"][word]["total_performance"] += performance
                hook_data["words"][word]["count"] += 1
    
    hook_data["last_updated"] = datetime.now().isoformat()
    with open(hook_word_file, 'w') as f:
        json.dump(hook_data, f, indent=2)
    safe_print(f"  Updated hook words from {len(top_videos)} competitor videos")
    
    # v9.5: Seasonal content suggestions for next month
    safe_print("\n[v9.5] Seasonal Content Calendar")
    try:
        from master_prompts import SEASONAL_CALENDAR_PROMPT
        # Generate seasonal suggestions using AI
        prompt = SEASONAL_CALENDAR_PROMPT.format(
            current_date=datetime.now().strftime("%A, %B %d, %Y")
        )
        
        if GROQ_API_KEY:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    seasonal_data = json.loads(match.group())
                    seasonal_file = Path("data/persistent/seasonal_calendar.json")
                    seasonal_data["generated_at"] = datetime.now().isoformat()
                    with open(seasonal_file, 'w') as f:
                        json.dump(seasonal_data, f, indent=2)
                    safe_print(f"  Generated seasonal content for {len(seasonal_data.get('content_opportunities', []))} opportunities")
    except Exception as e:
        safe_print(f"  [!] Seasonal calendar error: {e}")

    safe_print("\n" + "=" * 60)
    safe_print("ANALYSIS COMPLETE (v9.5)")
    safe_print("Files updated:")
    safe_print("  - viral_patterns.json")
    safe_print("  - competitor_tracking.json")
    safe_print("  - hook_word_performance.json")
    safe_print("  - seasonal_calendar.json")
    safe_print("=" * 60)


if __name__ == "__main__":
    main()

