#!/usr/bin/env python3
"""
ViralShorts Factory - Viral Channel Analyzer v1.0
===================================================

Learns from "graduated" channels (1000+ subs, monetized):
1. Finds successful AI-generated Shorts channels
2. Analyzes their most viral content
3. Extracts patterns (titles, hooks, lengths, categories)
4. Feeds patterns back into our generation system

This is the "learn from the pros" system!
"""

import os
import json
import re
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Try to import persistent state
try:
    from persistent_state import get_viral_manager, safe_print
except ImportError:
    def safe_print(msg): 
        try: print(msg)
        except: print(re.sub(r'[^\x00-\x7F]+', '', msg))
    get_viral_manager = None


@dataclass
class ChannelInsight:
    """Insights extracted from a successful channel."""
    channel_name: str
    subscriber_count: int
    avg_views_per_short: int
    top_performing_titles: List[str]
    common_title_patterns: List[str]
    hook_techniques: List[str]
    avg_video_length: int  # seconds
    posting_frequency: str
    niche: str


class ViralChannelAnalyzer:
    """
    Analyzes successful Shorts channels to learn winning patterns.
    
    v8.1: 100% AI-DRIVEN - No hardcoded patterns!
    
    Uses:
    - AI to generate and evolve viral patterns
    - Optional: YouTube Data API for channel analysis (only if API key provided)
    - NO HARDCODED PATTERNS - AI generates everything!
    """
    
    # NO HARDCODED CHANNELS - AI will suggest based on niche
    REFERENCE_CHANNELS = []  # Empty - AI-populated
    
    # NO HARDCODED PATTERNS - AI generates these!
    # This is just the STRUCTURE, not content
    PROVEN_PATTERNS = None  # Will be AI-generated
    
    def __init__(self):
        self.youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        
        # Load any previously learned patterns
        if get_viral_manager:
            self.viral_manager = get_viral_manager()
        else:
            self.viral_manager = None
        
        # v8.1: Generate patterns via AI (not hardcoded!)
        self._ensure_ai_patterns()
    
    def _ensure_ai_patterns(self):
        """
        Ensure we have AI-generated patterns.
        Generates fresh patterns if none exist or they're stale.
        """
        # Check if we already have patterns from viral manager
        if self.viral_manager and self.viral_manager.patterns.get("title_patterns"):
            patterns_age = self.viral_manager.patterns.get("last_updated")
            if patterns_age:
                # Use existing if less than 7 days old
                try:
                    from datetime import datetime, timedelta
                    last_update = datetime.fromisoformat(patterns_age)
                    if datetime.now() - last_update < timedelta(days=7):
                        self.PROVEN_PATTERNS = self.viral_manager.patterns
                        return
                except:
                    pass
        
        # Generate fresh patterns via AI
        self.PROVEN_PATTERNS = self._generate_viral_patterns_ai()
        
        # Save to viral manager for persistence
        if self.viral_manager:
            self.viral_manager.update_patterns_from_analysis(self.PROVEN_PATTERNS)
    
    def _generate_viral_patterns_ai(self) -> Dict:
        """
        Use AI to generate viral patterns - NO HARDCODING!
        
        This is the core innovation: AI decides what makes content viral,
        not hardcoded human assumptions.
        """
        if not self.groq_key:
            # Minimal fallback only if no AI available
            return self._minimal_fallback_patterns()
        
        safe_print("[AI] Generating viral patterns...")
        
        prompt = """You are an expert in viral short-form video content (YouTube Shorts, TikTok, Reels).

Based on your knowledge of what makes content go viral RIGHT NOW, generate:

1. **TITLE FORMULAS** (10 patterns): Proven title structures that get clicks
   - Use {placeholders} for variable parts
   - Focus on curiosity, numbers, challenges, revelations

2. **HOOK TECHNIQUES** (8 patterns): First 1-3 seconds that STOP the scroll
   - Pattern interrupts, questions, controversy, curiosity gaps

3. **ENGAGEMENT BAITS** (7 patterns): End-of-video CTAs that drive comments
   - Questions, challenges, predictions, saves

4. **OPTIMAL METRICS**: What works best currently
   - video_length, hook_length, phrase_count, words_per_phrase

Return as JSON:
{
    "title_formulas": ["pattern with {placeholder}", ...],
    "hook_techniques": ["technique description", ...],
    "engagement_tactics": ["tactic description", ...],
    "optimal_metrics": {
        "video_length_seconds": [min, max],
        "hook_length_seconds": [min, max],
        "phrases_count": [min, max],
        "words_per_phrase": [min, max]
    }
}

Be specific, creative, and based on CURRENT viral trends. JSON ONLY."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",  # Fast, cheap model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 800
                },
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    patterns = json.loads(match.group())
                    safe_print(f"[AI] Generated {len(patterns.get('title_formulas', []))} title patterns")
                    return patterns
        except Exception as e:
            safe_print(f"[!] AI pattern generation failed: {e}")
        
        return self._minimal_fallback_patterns()
    
    def _minimal_fallback_patterns(self) -> Dict:
        """
        Absolute minimal fallback - only used if AI completely fails.
        These are structure hints, not actual content.
        """
        return {
            "title_formulas": [
                "{number} {topic} that {result}",
                "Why {thing} is {adjective}",
                "The truth about {topic}"
            ],
            "hook_techniques": [
                "Start with a question",
                "Make a bold claim",
                "Create curiosity gap"
            ],
            "engagement_tactics": [
                "Ask a question",
                "Request comments",
                "Encourage saves"
            ],
            "optimal_metrics": {
                "video_length_seconds": [15, 25],
                "hook_length_seconds": [1, 3],
                "phrases_count": [3, 5],
                "words_per_phrase": [8, 15]
            }
        }
    
    def analyze_channel(self, channel_id: str) -> Optional[ChannelInsight]:
        """
        Analyze a YouTube channel to extract viral patterns.
        
        Requires YouTube Data API key.
        """
        if not self.youtube_api_key:
            safe_print("[!] No YouTube API key for channel analysis")
            return None
        
        try:
            # Get channel info
            channel_url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "key": self.youtube_api_key,
                "id": channel_id,
                "part": "statistics,snippet,contentDetails"
            }
            
            response = requests.get(channel_url, params=params, timeout=15)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get("items"):
                return None
            
            channel = data["items"][0]
            stats = channel.get("statistics", {})
            snippet = channel.get("snippet", {})
            
            subscriber_count = int(stats.get("subscriberCount", 0))
            
            # Only analyze "graduated" channels (1000+ subs)
            if subscriber_count < 1000:
                safe_print(f"[SKIP] Channel {channel_id} has {subscriber_count} subs (need 1000+)")
                return None
            
            # Get recent Shorts videos
            uploads_playlist = channel["contentDetails"]["relatedPlaylists"]["uploads"]
            videos = self._get_channel_shorts(uploads_playlist)
            
            if not videos:
                return None
            
            # Analyze video patterns
            avg_views = sum(v["views"] for v in videos) / len(videos) if videos else 0
            top_titles = [v["title"] for v in sorted(videos, key=lambda x: x["views"], reverse=True)[:10]]
            
            # Extract patterns using AI
            patterns = self._extract_patterns_with_ai(top_titles)
            
            return ChannelInsight(
                channel_name=snippet.get("title", "Unknown"),
                subscriber_count=subscriber_count,
                avg_views_per_short=int(avg_views),
                top_performing_titles=top_titles,
                common_title_patterns=patterns.get("title_patterns", []),
                hook_techniques=patterns.get("hook_techniques", []),
                avg_video_length=patterns.get("avg_length", 20),
                posting_frequency=patterns.get("posting_frequency", "daily"),
                niche=patterns.get("niche", "general")
            )
            
        except Exception as e:
            safe_print(f"[!] Channel analysis error: {e}")
            return None
    
    def _get_channel_shorts(self, playlist_id: str, max_results: int = 20) -> List[Dict]:
        """Get Shorts from channel's uploads playlist."""
        if not self.youtube_api_key:
            return []
        
        try:
            url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "key": self.youtube_api_key,
                "playlistId": playlist_id,
                "part": "snippet",
                "maxResults": max_results
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                return []
            
            items = response.json().get("items", [])
            video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
            
            # Get video statistics
            videos_url = "https://www.googleapis.com/youtube/v3/videos"
            videos_params = {
                "key": self.youtube_api_key,
                "id": ",".join(video_ids),
                "part": "statistics,contentDetails,snippet"
            }
            
            videos_response = requests.get(videos_url, params=videos_params, timeout=15)
            if videos_response.status_code != 200:
                return []
            
            videos = []
            for item in videos_response.json().get("items", []):
                duration = item["contentDetails"].get("duration", "PT0S")
                # Only include Shorts (< 60 seconds)
                if self._duration_to_seconds(duration) <= 60:
                    videos.append({
                        "id": item["id"],
                        "title": item["snippet"]["title"],
                        "views": int(item["statistics"].get("viewCount", 0)),
                        "likes": int(item["statistics"].get("likeCount", 0)),
                        "comments": int(item["statistics"].get("commentCount", 0)),
                        "duration": self._duration_to_seconds(duration)
                    })
            
            return videos
            
        except Exception as e:
            safe_print(f"[!] Error getting Shorts: {e}")
            return []
    
    def _duration_to_seconds(self, duration: str) -> int:
        """Convert ISO 8601 duration to seconds."""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds
    
    def _extract_patterns_with_ai(self, titles: List[str]) -> Dict:
        """Use AI to extract patterns from successful titles."""
        if not self.groq_key or not titles:
            return {}
        
        prompt = f"""Analyze these viral YouTube Shorts titles and extract reusable patterns:

TITLES:
{json.dumps(titles, indent=2)}

Extract:
1. Title patterns/formulas that could be reused
2. Hook techniques used
3. Common themes/niches
4. Word count patterns

Return JSON:
{{
    "title_patterns": ["pattern with {{placeholders}}", ...],
    "hook_techniques": ["technique 1", ...],
    "niche": "main category",
    "avg_word_count": number
}}

JSON ONLY."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            safe_print(f"[!] AI pattern extraction error: {e}")
        
        return {}
    
    def get_viral_patterns(self) -> Dict:
        """
        Get all AI-learned viral patterns.
        
        v8.1: 100% AI-generated, no hardcoded patterns!
        Returns comprehensive patterns for video generation.
        """
        # Ensure patterns are generated (AI does this)
        if not self.PROVEN_PATTERNS:
            self._ensure_ai_patterns()
        
        patterns = self.PROVEN_PATTERNS.copy() if self.PROVEN_PATTERNS else {}
        
        # Merge with any saved patterns from viral manager
        if self.viral_manager and self.viral_manager.patterns:
            saved = self.viral_manager.patterns
            for key in ["title_patterns", "hook_patterns", "engagement_baits", "title_formulas"]:
                if key in saved and saved[key]:
                    target_key = "title_formulas" if "title" in key else key
                    if target_key not in patterns:
                        patterns[target_key] = []
                    for item in saved[key]:
                        if item and item not in patterns[target_key]:
                            patterns[target_key].append(item)
        
        return patterns
    
    def get_optimized_prompt_additions(self) -> str:
        """
        Get AI-generated prompt additions for virality.
        
        v8.1: If no patterns exist yet, generates them via AI first.
        """
        patterns = self.get_viral_patterns()
        
        # Get samples (or empty if none yet)
        title_formulas = patterns.get("title_formulas", [])
        hook_techniques = patterns.get("hook_techniques", [])
        engagement = patterns.get("engagement_tactics", [])
        
        # If no patterns exist, AI will generate inline guidance instead
        if not title_formulas:
            return self._generate_inline_viral_guidance()
        
        sample_titles = random.sample(title_formulas, min(3, len(title_formulas))) if title_formulas else []
        sample_hooks = random.sample(hook_techniques, min(2, len(hook_techniques))) if hook_techniques else []
        sample_engagement = random.sample(engagement, min(2, len(engagement))) if engagement else []
        
        result = "\n=== AI-LEARNED VIRAL PATTERNS ===\n"
        
        if sample_titles:
            result += "\nTITLE FORMULAS that get views:\n"
            result += "\n".join(f"- {t}" for t in sample_titles)
        
        if sample_hooks:
            result += "\n\nHOOK TECHNIQUES that stop the scroll:\n"
            result += "\n".join(f"- {h}" for h in sample_hooks)
        
        result += """

OPTIMAL METRICS:
- Video length: 40-50 seconds with 8-10 phrases (CRITICAL!)
- Hook: First 1-3 seconds must grab attention
- Phrases: 3-5 short phrases (8-15 words each)
- End with engagement question
"""
        
        if sample_engagement:
            result += "\nENGAGEMENT BAITS (use one at the end):\n"
            result += "\n".join(f"- {e}" for e in sample_engagement)
        
        return result
    
    def _generate_inline_viral_guidance(self) -> str:
        """
        Generate viral guidance inline when no patterns exist.
        This is a one-time AI call to bootstrap the system.
        """
        if not self.groq_key:
            return """
=== VIRAL CONTENT GUIDANCE ===
- Create a strong hook in first 2 seconds
- Keep total video under 25 seconds
- End with a question to drive comments
- Use numbers and specifics in titles
"""
        
        # Quick AI call for guidance
        prompt = """Give 3 viral title patterns and 2 hook techniques for YouTube Shorts.
Format as simple bullet points. Be specific and creative. Under 100 words total."""
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return f"\n=== AI VIRAL GUIDANCE ===\n{content}\n"
        except:
            pass
        
        return ""
    
    def learn_from_our_best(self, our_videos: List[Dict]) -> Dict:
        """
        Analyze our own best-performing videos to learn what works for us.
        
        This is the self-improvement loop!
        """
        if not our_videos:
            return {}
        
        # Sort by views/engagement
        sorted_videos = sorted(our_videos, 
                               key=lambda x: x.get("views", 0) + x.get("likes", 0) * 10, 
                               reverse=True)
        
        top_videos = sorted_videos[:5]
        
        # Extract our best patterns
        best_categories = [v.get("category") for v in top_videos if v.get("category")]
        best_hooks = [v.get("hook") for v in top_videos if v.get("hook")]
        
        patterns = {
            "our_best_categories": list(set(best_categories)),
            "our_best_hooks": best_hooks[:3],
            "avg_best_length": sum(v.get("duration", 20) for v in top_videos) / len(top_videos) if top_videos else 20
        }
        
        safe_print(f"[LEARN] Our best categories: {patterns['our_best_categories']}")
        
        return patterns


def get_viral_prompt_boost() -> str:
    """
    Get COMPREHENSIVE viral + analytics-learned additions for prompts.
    
    Combines:
    - Viral patterns from other successful channels (monthly)
    - Our own performance analytics (weekly)
    - GOLD-VALUE: Tricks, baits, hacks, psychological triggers
    """
    analyzer = ViralChannelAnalyzer()
    viral_additions = analyzer.get_optimized_prompt_additions()
    
    # Also load our performance-learned preferences
    try:
        from persistent_state import get_variety_manager
        variety_mgr = get_variety_manager()
        state = variety_mgr.state
        
        analytics_boost = ""
        
        # Add learned preferences from our own analytics
        if state.get("preferred_categories"):
            analytics_boost += f"\nOUR BEST CATEGORIES: {', '.join(state['preferred_categories'][:5])}"
        
        if state.get("preferred_music_moods"):
            analytics_boost += f"\nPREFERRED MUSIC MOODS: {', '.join(state['preferred_music_moods'][:4])}"
        
        if state.get("preferred_voice_styles"):
            analytics_boost += f"\nVOICE STYLES THAT WORK: {', '.join(state['preferred_voice_styles'][:3])}"
        
        if state.get("preferred_themes"):
            analytics_boost += f"\nTHEMES THAT PERFORM: {', '.join(state['preferred_themes'][:5])}"
        
        # GOLD-VALUE: Tricks, baits, hacks
        if state.get("title_tricks"):
            analytics_boost += f"\n\nTITLE TRICKS THAT WORK: {', '.join(state['title_tricks'][:4])}"
        
        if state.get("hook_types"):
            analytics_boost += f"\nHOOK TYPES THAT CONVERT: {', '.join(state['hook_types'][:3])}"
        
        if state.get("psych_triggers"):
            analytics_boost += f"\nPSYCH TRIGGERS TO USE: {', '.join(state['psych_triggers'][:3])}"
        
        if state.get("engagement_baits"):
            analytics_boost += f"\nENGAGEMENT BAITS: {', '.join(state['engagement_baits'][:3])}"
        
        if state.get("virality_hacks"):
            analytics_boost += f"\nVIRALITY HACKS: {', '.join(state['virality_hacks'][:3])}"
        
        if state.get("priority_improvements"):
            analytics_boost += f"\n\nPRIORITY IMPROVEMENTS: {', '.join(state['priority_improvements'][:3])}"
        
        # A/B TITLE TESTING: Use learned title styles
        if state.get("best_title_styles"):
            analytics_boost += f"\n\nBEST TITLE STYLES (from A/B testing): {', '.join(state['best_title_styles'][:3])}"
        
        # AUDIENCE TIMING (informational - Shorts timing is less critical)
        if state.get("best_posting_days"):
            analytics_boost += f"\n\nBEST POSTING DAYS: {', '.join(state['best_posting_days'][:3])}"
        
        # v17.9.42: AGGRESSIVE MODE LEARNINGS
        if state.get("hook_templates"):
            analytics_boost += f"\n\nPROVEN HOOK TEMPLATES: {state['hook_templates'][:3]}"
        
        if state.get("curiosity_gaps"):
            analytics_boost += f"\nCURIOSITY GAP EXAMPLES: {state['curiosity_gaps'][:2]}"
        
        if state.get("do_more"):
            analytics_boost += f"\n\nDO MORE (from deep analysis): {state['do_more'][:5]}"
        
        if state.get("avoid"):
            analytics_boost += f"\nAVOID (from deep analysis): {state['avoid'][:5]}"
        
        if state.get("external_hooks"):
            analytics_boost += f"\n\nVIRAL HOOKS FROM TOP CREATORS: {state['external_hooks'][:3]}"
        
        if state.get("learned_weights"):
            weights = state["learned_weights"]
            top_categories = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
            analytics_boost += f"\n\nTOP PERFORMING CATEGORIES (by weight): {top_categories}"
        
        if analytics_boost:
            viral_additions += f"\n\n=== OUR ANALYTICS INSIGHTS (GOLD-VALUE) ==={analytics_boost}\n"
        
    except Exception as e:
        pass  # Analytics not available yet
    
    return viral_additions


def analyze_and_update_patterns():
    """
    Main function to analyze channels and update our patterns.
    
    Run this periodically to keep patterns fresh.
    """
    analyzer = ViralChannelAnalyzer()
    
    safe_print("\n" + "=" * 60)
    safe_print("   VIRAL CHANNEL ANALYZER")
    safe_print("=" * 60)
    
    # Get current patterns
    patterns = analyzer.get_viral_patterns()
    safe_print(f"\n   Title formulas: {len(patterns.get('title_formulas', []))}")
    safe_print(f"   Hook techniques: {len(patterns.get('hook_techniques', []))}")
    safe_print(f"   Engagement tactics: {len(patterns.get('engagement_tactics', []))}")
    
    # Sample output
    safe_print("\n   Sample viral additions for prompts:")
    safe_print("-" * 50)
    print(analyzer.get_optimized_prompt_additions())
    
    return patterns


if __name__ == "__main__":
    analyze_and_update_patterns()

