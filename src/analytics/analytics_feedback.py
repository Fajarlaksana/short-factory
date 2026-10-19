#!/usr/bin/env python3
"""
ViralShorts Factory - Analytics Feedback Loop System
======================================================

This system:
1. Tracks metadata for every video we generate
2. Fetches performance metrics (views, likes, comments)
3. Uses AI to analyze what works and what doesn't
4. Feeds insights back into content generation

THE GOAL: Learn and improve automatically!

Data Flow:
[Generate Video] → [Save Metadata] → [Upload] → [Wait] → 
[Fetch Analytics] → [AI Analysis] → [Update Preferences] → [Better Videos!]
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import requests


# =============================================================================
# VIDEO METADATA TRACKING
# =============================================================================

@dataclass
class VideoMetadata:
    """Complete metadata for a generated video - v3.0 Enhanced."""
    # Identification
    video_id: str
    local_path: str
    filename: str
    
    # Content
    topic: str
    video_type: str
    hook: str
    content_summary: str
    
    # Generation details
    broll_keywords: List[str]
    music_mood: str
    voiceover_style: str
    theme_name: str
    
    # AI scores (pre-upload)
    value_check_score: int
    virality_score: int
    timeliness_score: int
    
    # Platform details
    platforms_uploaded: List[str]
    youtube_video_id: Optional[str]
    dailymotion_video_id: Optional[str]
    
    # Timestamps
    generated_at: str
    uploaded_at: Optional[str]
    
    # Performance (updated later)
    performance: Optional[Dict] = None
    
    # ===== v3.0 ENHANCEMENT TRACKING =====
    # Trend source (for analyzing which sources work best)
    trend_source: Optional[str] = None  # "google_rss", "reddit", "ai", "combined"
    
    # Visual enhancements (for A/B testing)
    has_captions: bool = False
    caption_style: Optional[str] = None  # "tiktok", "netflix", "minimal"
    has_progress_bar: bool = False
    progress_bar_style: Optional[str] = None  # "gradient", "minimal", "youtube"
    has_ken_burns_zoom: bool = False
    zoom_intensity: float = 0.0
    has_vignette: bool = False
    has_particles: bool = False
    
    # Thumbnail (for A/B testing)
    thumbnail_generated: bool = False
    thumbnail_style: Optional[str] = None  # "fire", "electric", "gold", "viral", "money"
    thumbnail_headline: Optional[str] = None
    
    # A/B test variant tracking
    ab_test_variants: Optional[Dict] = None  # {"title_style": "question", "thumbnail": "fire"}
    
    # ===== v16.11 ENHANCEMENT TRACKING =====
    # Track which enhancements were active and their effectiveness
    v12_enhancements_active: bool = False  # Were v12 enhancements enabled?
    v9_enhancements_active: bool = False   # Were v9 enhancements enabled?
    quality_score: Optional[int] = None    # Post-render quality score (1-10)
    enhancement_boosts_applied: Optional[List[str]] = None  # List of boosts applied
    regeneration_count: int = 0            # How many times video was regenerated
    
    # Phrase count (for analyzing optimal content length)
    phrase_count: int = 0
    total_word_count: int = 0
    
    # Optimization applied
    viral_optimizer_used: bool = False
    ai_title_generated: bool = False
    ai_hashtags_generated: bool = False
    
    # ===== v7.x AI-DRIVEN TRACKING =====
    # Voice selection (for analyzing which voices perform best)
    voice_name: Optional[str] = None  # e.g., "en-US-AriaNeural"
    voice_style: Optional[str] = None  # e.g., "energetic", "calm"
    
    # Music selection (AI-driven in v7.2+)
    music_file: Optional[str] = None  # Actual file used
    music_source: Optional[str] = None  # "bensound", "pixabay", "ai_selected"
    
    # AI evaluation (Stage 3)
    ai_evaluation_score: int = 0  # 1-10 score from AI
    ai_improvements: Optional[List[str]] = None  # What AI improved
    
    # Batch tracking (v7.1+)
    batch_id: Optional[str] = None  # Which batch this video belongs to
    batch_position: int = 0  # Position in batch (1-8)
    was_youtube_selected: bool = False  # Was this the "best" video for YouTube?


class VideoMetadataStore:
    """
    Store and retrieve video metadata.
    
    Saves to JSON file for persistence across runs.
    """
    
    def __init__(self, store_path: str = "data/video_metadata.json"):
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, VideoMetadata] = {}
        self._load()
    
    def _load(self):
        """Load metadata from file."""
        if self.store_path.exists():
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    for vid_id, meta in data.items():
                        self.metadata[vid_id] = VideoMetadata(**meta)
            except Exception as e:
                print(f"⚠️ Error loading metadata: {e}")
    
    def _save(self):
        """Save metadata to file."""
        try:
            data = {vid_id: asdict(meta) for vid_id, meta in self.metadata.items()}
            with open(self.store_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Error saving metadata: {e}")
    
    def add(self, metadata: VideoMetadata):
        """Add new video metadata."""
        self.metadata[metadata.video_id] = metadata
        self._save()
        print(f"📝 Saved metadata for: {metadata.video_id}")
    
    def update_performance(self, video_id: str, performance: Dict):
        """Update performance metrics for a video."""
        if video_id in self.metadata:
            self.metadata[video_id].performance = performance
            self._save()
            print(f"📊 Updated performance for: {video_id}")
    
    def get_all(self) -> List[VideoMetadata]:
        """Get all video metadata."""
        return list(self.metadata.values())
    
    def get_recent(self, days: int = 7) -> List[VideoMetadata]:
        """Get videos from the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        for meta in self.metadata.values():
            try:
                gen_time = datetime.fromisoformat(meta.generated_at)
                if gen_time > cutoff:
                    recent.append(meta)
            except:
                pass
        return recent
    
    def get_top_performers(self, limit: int = 10) -> List[VideoMetadata]:
        """Get top performing videos by views."""
        with_performance = [m for m in self.metadata.values() if m.performance]
        sorted_videos = sorted(
            with_performance,
            key=lambda x: x.performance.get("views", 0),
            reverse=True
        )
        return sorted_videos[:limit]


# =============================================================================
# YOUTUBE ANALYTICS FETCHER
# =============================================================================

class YouTubeAnalyticsFetcher:
    """
    Fetch video analytics from YouTube.
    
    Uses the YouTube Data API to get:
    - View count
    - Like count
    - Comment count
    - Watch time (if available)
    """
    
    def __init__(self):
        self.client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        self.client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
        self.access_token = None
    
    def _get_access_token(self) -> Optional[str]:
        """Get fresh access token."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            return None
        
        try:
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                }
            )
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                return self.access_token
        except Exception as e:
            print(f"⚠️ Error getting access token: {e}")
        return None
    
    def get_video_stats(self, video_id: str) -> Optional[Dict]:
        """
        Get statistics for a specific video.
        
        Returns: {views, likes, comments, published_at}
        """
        if not self.access_token:
            if not self._get_access_token():
                return None
        
        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics,snippet",
                    "id": video_id,
                },
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    item = data["items"][0]
                    stats = item.get("statistics", {})
                    snippet = item.get("snippet", {})
                    
                    return {
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                        "title": snippet.get("title", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "fetched_at": datetime.now().isoformat(),
                    }
        except Exception as e:
            print(f"⚠️ Error fetching video stats: {e}")
        
        return None
    
    def get_channel_videos(self, max_results: int = 50) -> List[Dict]:
        """Get recent videos from our channel."""
        if not self.access_token:
            if not self._get_access_token():
                return []
        
        try:
            # First get channel uploads playlist
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "contentDetails",
                    "mine": "true",
                },
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code != 200:
                return []
            
            channel_data = response.json()
            if not channel_data.get("items"):
                return []
            
            uploads_playlist = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get videos from uploads playlist
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_playlist,
                    "maxResults": max_results,
                },
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                videos = []
                for item in response.json().get("items", []):
                    videos.append({
                        "video_id": item["snippet"]["resourceId"]["videoId"],
                        "title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                    })
                return videos
        except Exception as e:
            print(f"⚠️ Error fetching channel videos: {e}")
        
        return []


# =============================================================================
# AI-POWERED ANALYTICS ANALYZER
# =============================================================================

class AnalyticsAnalyzer:
    """
    Use AI to analyze performance data and extract insights.
    
    This is the BRAIN that learns from our video performance!
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.client = None
        
        if self.groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_key)
            except ImportError:
                pass
    
    def analyze_performance(self, videos: List[VideoMetadata]) -> Dict:
        """
        Analyze video performance and extract actionable insights.
        
        Returns insights about:
        - Which topics perform best
        - Which video types get most engagement
        - What hooks work
        - What music moods are effective
        - What to do MORE of and LESS of
        """
        if not self.client:
            return self._basic_analysis(videos)
        
        # Prepare data for AI analysis (v3.0 enhanced)
        video_data = []
        for v in videos:
            if v.performance:
                video_data.append({
                    "topic": v.topic,
                    "video_type": v.video_type,
                    "hook": v.hook[:50],
                    "music_mood": v.music_mood,
                    "views": v.performance.get("views", 0),
                    "likes": v.performance.get("likes", 0),
                    "comments": v.performance.get("comments", 0),
                    "virality_score": v.virality_score,
                    # v3.0 enhancement data for correlation analysis
                    "trend_source": v.trend_source or "unknown",
                    "has_captions": v.has_captions,
                    "caption_style": v.caption_style,
                    "has_progress_bar": v.has_progress_bar,
                    "has_ken_burns_zoom": v.has_ken_burns_zoom,
                    "has_vignette": v.has_vignette,
                    "thumbnail_style": v.thumbnail_style,
                    "phrase_count": v.phrase_count,
                    "word_count": v.total_word_count,
                    "ai_title_used": v.ai_title_generated,
                })
        
        if not video_data:
            return {"error": "No performance data available"}
        
        prompt = f"""You are a YouTube Shorts analytics expert. Analyze this video performance data and provide actionable insights.

VIDEO DATA:
{json.dumps(video_data, indent=2)}

Analyze the data and provide:

1. TOP PERFORMERS: Which videos performed best and why?

2. TOPIC ANALYSIS: Which topics get the most views/engagement?

3. VIDEO TYPE ANALYSIS: Which video types (psychology_fact, life_hack, etc.) perform best?

4. HOOK ANALYSIS: What hook patterns lead to better performance?

5. MUSIC MOOD ANALYSIS: Does music mood affect performance?

6. TREND SOURCE ANALYSIS: Do videos from certain sources (google_rss, reddit, ai) perform better?

7. ENHANCEMENT CORRELATION: Do videos WITH these features perform better?
   - TikTok-style captions (has_captions)
   - Progress bar (has_progress_bar)
   - Ken Burns zoom (has_ken_burns_zoom)
   - Vignette effect (has_vignette)
   - AI-generated titles (ai_title_used)

8. CONTENT LENGTH: Is there an optimal phrase_count or word_count?

9. RECOMMENDATIONS:
   - What should we do MORE of?
   - What should we AVOID?
   - Which enhancements to enable/disable?
   - Specific topic suggestions for next videos

Return as JSON:
{{
    "top_performers": ["topic1", "topic2"],
    "best_video_types": ["type1", "type2"],
    "best_hooks_patterns": ["pattern1", "pattern2"],
    "best_music_moods": ["mood1", "mood2"],
    "best_trend_source": "google_rss|reddit|ai|combined",
    "enhancement_analysis": {{
        "captions_impact": "positive|negative|neutral",
        "progress_bar_impact": "positive|negative|neutral",
        "zoom_impact": "positive|negative|neutral",
        "vignette_impact": "positive|negative|neutral",
        "ai_title_impact": "positive|negative|neutral"
    }},
    "optimal_content_length": {{
        "ideal_phrase_count": 4,
        "ideal_word_count": 60
    }},
    "do_more": ["recommendation1", "recommendation2"],
    "do_less": ["thing_to_avoid1", "thing_to_avoid2"],
    "enhancements_to_enable": ["captions", "progress_bar"],
    "enhancements_to_disable": [],
    "next_video_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "key_insight": "One sentence summary of most important finding"
}}"""

        try:
            # v16.10: DYNAMIC MODEL - No hardcoding
            try:
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                groq_models = optimizer.get_groq_models()
                model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
            except:
                model_to_use = "llama-3.3-70b-versatile"
            
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result.strip())
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
            return self._basic_analysis(videos)
    
    def _basic_analysis(self, videos: List[VideoMetadata]) -> Dict:
        """Basic analysis without AI."""
        with_performance = [v for v in videos if v.performance]
        
        if not with_performance:
            return {"error": "No performance data"}
        
        # Simple analysis
        total_views = sum(v.performance.get("views", 0) for v in with_performance)
        avg_views = total_views / len(with_performance)
        
        # Find best video type
        type_views = {}
        for v in with_performance:
            vtype = v.video_type
            if vtype not in type_views:
                type_views[vtype] = []
            type_views[vtype].append(v.performance.get("views", 0))
        
        best_type = max(type_views.keys(), key=lambda t: sum(type_views[t]) / len(type_views[t]))
        
        return {
            "total_videos": len(with_performance),
            "total_views": total_views,
            "average_views": avg_views,
            "best_video_type": best_type,
            "key_insight": f"Average of {avg_views:.0f} views. {best_type} performs best.",
        }
    
    def get_content_recommendations(self, insights: Dict) -> Dict:
        """
        Convert insights into actionable content recommendations.
        
        This feeds back into the content generation system!
        """
        recommendations = {
            "preferred_video_types": insights.get("best_video_types", []),
            "preferred_topics": insights.get("top_performers", []),
            "preferred_music_moods": insights.get("best_music_moods", []),
            "avoid_topics": insights.get("do_less", []),
            "next_videos": insights.get("next_video_suggestions", []),
        }
        
        return recommendations


# =============================================================================
# FEEDBACK LOOP CONTROLLER
# =============================================================================

class FeedbackLoopController:
    """
    Main controller that orchestrates the feedback loop.
    
    1. Saves metadata when videos are generated
    2. Periodically fetches performance data
    3. Analyzes performance with AI
    4. Updates content preferences
    """
    
    def __init__(self):
        self.metadata_store = VideoMetadataStore()
        self.youtube_fetcher = YouTubeAnalyticsFetcher()
        self.analyzer = AnalyticsAnalyzer()
        
        # Content preferences (updated by analytics)
        self.preferences_path = Path("data/content_preferences.json")
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict:
        """Load content preferences."""
        if self.preferences_path.exists():
            try:
                with open(self.preferences_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default preferences
        return {
            "preferred_video_types": [],
            "preferred_topics": [],
            "preferred_music_moods": [],
            "avoid_topics": [],
            "last_updated": None,
        }
    
    def _save_preferences(self):
        """Save content preferences."""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences["last_updated"] = datetime.now().isoformat()
        with open(self.preferences_path, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def record_video_generation(self, 
                                  video_id: str,
                                  local_path: str,
                                  topic_data: Dict,
                                  generation_data: Optional[Dict] = None) -> VideoMetadata:
        """
        Record metadata when a video is generated.
        
        Call this right after video generation!
        
        Args:
            video_id: Unique identifier for the video
            local_path: Path to the generated video file
            topic_data: The topic/content data used for generation
            generation_data: v3.0 enhancement tracking data
        """
        gen = generation_data or {}
        
        metadata = VideoMetadata(
            video_id=video_id,
            local_path=local_path,
            filename=Path(local_path).name,
            topic=topic_data.get("topic", "Unknown"),
            video_type=topic_data.get("video_type", "unknown"),
            hook=topic_data.get("hook", ""),
            content_summary=topic_data.get("content", "")[:200],
            broll_keywords=topic_data.get("broll_keywords", []),
            music_mood=topic_data.get("music_mood", "dramatic"),
            voiceover_style=gen.get("voiceover_style", "energetic"),
            theme_name=gen.get("theme_name", "dynamic"),
            value_check_score=topic_data.get("value_check", {}).get("score", 0),
            virality_score=topic_data.get("virality_score", 0),
            timeliness_score=topic_data.get("timeliness_score", 0),
            platforms_uploaded=[],
            youtube_video_id=None,
            dailymotion_video_id=None,
            generated_at=datetime.now().isoformat(),
            uploaded_at=None,
            performance=None,
            
            # v3.0 Enhancement Tracking
            trend_source=gen.get("trend_source"),  # Where topic came from
            has_captions=gen.get("has_captions", False),
            caption_style=gen.get("caption_style"),
            has_progress_bar=gen.get("has_progress_bar", False),
            progress_bar_style=gen.get("progress_bar_style"),
            has_ken_burns_zoom=gen.get("has_ken_burns_zoom", False),
            zoom_intensity=gen.get("zoom_intensity", 0.0),
            has_vignette=gen.get("has_vignette", False),
            has_particles=gen.get("has_particles", False),
            thumbnail_generated=gen.get("thumbnail_generated", False),
            thumbnail_style=gen.get("thumbnail_style"),
            thumbnail_headline=gen.get("thumbnail_headline"),
            ab_test_variants=gen.get("ab_test_variants"),
            phrase_count=gen.get("phrase_count", 0),
            total_word_count=gen.get("total_word_count", 0),
            viral_optimizer_used=gen.get("viral_optimizer_used", False),
            ai_title_generated=gen.get("ai_title_generated", False),
            ai_hashtags_generated=gen.get("ai_hashtags_generated", False),
            
            # v7.x AI-Driven Fields
            voice_name=gen.get("voice_name"),
            voice_style=gen.get("voiceover_style"),
            music_file=gen.get("music_file"),
            music_source=gen.get("music_source", "bensound"),
            ai_evaluation_score=topic_data.get("value_check", {}).get("score", 0),
            ai_improvements=gen.get("ai_improvements"),
            batch_id=gen.get("batch_id"),
            batch_position=gen.get("batch_position", 0),
            was_youtube_selected=gen.get("was_youtube_selected", False),
        )
        
        self.metadata_store.add(metadata)
        return metadata
    
    def record_upload(self, video_id: str, platform: str, platform_video_id: str):
        """Record when a video is uploaded to a platform."""
        if video_id in self.metadata_store.metadata:
            meta = self.metadata_store.metadata[video_id]
            meta.platforms_uploaded.append(platform)
            meta.uploaded_at = datetime.now().isoformat()
            
            if platform == "youtube":
                meta.youtube_video_id = platform_video_id
            elif platform == "dailymotion":
                meta.dailymotion_video_id = platform_video_id
            
            self.metadata_store._save()
    
    def update_all_performance(self) -> int:
        """
        Fetch and update performance for all videos with YouTube IDs.
        
        Returns number of videos updated.
        """
        updated = 0
        
        for video_id, meta in self.metadata_store.metadata.items():
            if meta.youtube_video_id:
                stats = self.youtube_fetcher.get_video_stats(meta.youtube_video_id)
                if stats:
                    self.metadata_store.update_performance(video_id, stats)
                    updated += 1
        
        print(f"📊 Updated performance for {updated} videos")
        return updated
    
    def run_analysis(self) -> Dict:
        """
        Run full analytics analysis and update preferences.
        v17.8: Now refreshes AI patterns based on insights!
        """
        # Get videos with performance data
        all_videos = self.metadata_store.get_all()
        
        # Analyze
        insights = self.analyzer.analyze_performance(all_videos)
        
        # Update preferences
        recommendations = self.analyzer.get_content_recommendations(insights)
        
        self.preferences.update(recommendations)
        self._save_preferences()
        
        # v17.8: Refresh AI patterns with new insights
        self._update_ai_patterns_from_insights(insights)
        
        print("\n[ANALYTICS] Analytics Analysis Complete!")
        print(f"   Key Insight: {insights.get('key_insight', 'N/A')}")
        
        return insights
    
    def _update_ai_patterns_from_insights(self, insights: Dict):
        """
        v17.8: Update AI patterns based on analytics insights.
        This ensures our viral patterns stay fresh and data-driven.
        """
        try:
            from ai_pattern_generator import get_pattern_generator
            gen = get_pattern_generator()
            
            # Check if patterns need refresh (e.g., more than 24 hours old)
            if gen.needs_refresh():
                print("   [AI PATTERNS] Refreshing patterns based on analytics...")
                gen.generate_patterns_with_ai()
                print("   [AI PATTERNS] Patterns refreshed!")
            else:
                print("   [AI PATTERNS] Patterns are fresh (less than 24h old)")
        except ImportError:
            pass  # AI pattern generator not available
        except Exception as e:
            print(f"   [!] AI pattern refresh failed: {e}")
        
        # v17.9.15: Feed performance data to ALL generators for learning
        self._update_all_generators_from_insights(insights)
    
    def _update_all_generators_from_insights(self, insights: Dict):
        """
        v17.9.15: Update ALL content generators with performance data.
        This ensures the feedback loop is COMPLETE - learned patterns 
        are used in future content generation!
        """
        all_videos = self.metadata_store.get_all()
        
        # Update Hook Generator with hook performance
        try:
            from ai_hook_generator import get_hook_generator
            hook_gen = get_hook_generator()
            
            for video in all_videos:
                if video.performance and video.hook:
                    views = video.performance.get('views', 0)
                    likes = video.performance.get('likes', 0)
                    
                    # Only record hooks with sufficient data
                    if views > 0:
                        hook_gen.record_performance(video.hook, views, likes)
            
            # Update best/worst patterns based on performance
            if hook_gen.data.get("performance"):
                sorted_hooks = sorted(
                    hook_gen.data["performance"].items(),
                    key=lambda x: x[1].get("ctr", 0),
                    reverse=True
                )
                
                # Top patterns become "best_patterns"
                hook_gen.data["best_patterns"] = [
                    h[1].get("hook", "")[:20] for h in sorted_hooks[:5]
                ]
                # Bottom patterns become "worst_patterns"
                hook_gen.data["worst_patterns"] = [
                    h[1].get("hook", "")[:20] for h in sorted_hooks[-3:]
                ]
                hook_gen._save()
                
            print("   [FEEDBACK] Hook generator updated with performance data")
        except Exception as e:
            print(f"   [!] Hook feedback failed: {e}")
        
        # Update CTA Generator with engagement performance
        try:
            from ai_cta_generator import get_cta_generator
            cta_gen = get_cta_generator()
            
            for video in all_videos:
                if video.performance:
                    comments = video.performance.get('comments', 0)
                    likes = video.performance.get('likes', 0)
                    shares = video.performance.get('shares', 0)
                    
                    # Extract CTA from content summary if available
                    cta = video.content_summary.split('.')[-1] if video.content_summary else ""
                    if cta and comments + likes > 0:
                        cta_gen.record_performance(
                            cta, 
                            video.video_type,
                            comments, 
                            likes,
                            shares
                        )
            
            print("   [FEEDBACK] CTA generator updated with engagement data")
        except Exception as e:
            print(f"   [!] CTA feedback failed: {e}")
        
        # Update Title Optimizer with CTR data
        try:
            from ai_title_optimizer import get_title_optimizer
            title_opt = get_title_optimizer()
            
            for video in all_videos:
                if video.performance:
                    views = video.performance.get('views', 0)
                    impressions = video.performance.get('impressions', views * 10)  # Estimate
                    ctr = views / max(impressions, 1)
                    
                    title = video.topic or video.filename
                    if views > 0:
                        title_opt.record_performance(title, views, ctr)
            
            print("   [FEEDBACK] Title optimizer updated with CTR data")
        except Exception as e:
            print(f"   [!] Title feedback failed: {e}")
        
        # Update Music Mood learner
        try:
            from ai_music_mood import get_mood_selector
            mood_sel = get_mood_selector()
            
            for video in all_videos:
                if video.performance and video.music_mood:
                    views = video.performance.get('views', 0)
                    avg_view_duration = video.performance.get('avg_view_duration', 0)
                    video_duration = video.performance.get('duration', 30)
                    retention = (avg_view_duration / max(video_duration, 1)) * 100
                    
                    mood_sel.record_performance(
                        video.music_mood,
                        video.video_type,
                        retention,
                        views
                    )
            
            print("   [FEEDBACK] Music mood selector updated with retention data")
        except Exception as e:
            print(f"   [!] Music feedback failed: {e}")
        
        print("   [FEEDBACK] All generators updated from analytics!")
    
    def get_content_guidance(self) -> Dict:
        """
        Get guidance for next content generation based on analytics.
        
        Use this when generating new videos!
        """
        return {
            "preferred_types": self.preferences.get("preferred_video_types", []),
            "suggested_topics": self.preferences.get("next_videos", []),
            "avoid": self.preferences.get("avoid_topics", []),
            "preferred_moods": self.preferences.get("preferred_music_moods", []),
        }
    
    def update_type_weights(self) -> Dict[str, float]:
        """
        Calculate and update video type weights based on performance.
        
        This is the core of our analytics-driven content strategy:
        - Higher views/engagement = higher weight
        - More videos of that type will be generated
        
        Returns updated weights dict.
        """
        from pro_video_generator import VIDEO_TYPES
        
        all_videos = self.metadata_store.get_all()
        
        if not all_videos:
            # No data yet - equal weights
            types = list(VIDEO_TYPES.keys())
            return {t: 1.0 / len(types) for t in types}
        
        # Calculate performance score per type
        type_scores = {}
        type_counts = {}
        
        for video in all_videos:
            video_type = video.video_type
            if not video_type:
                continue
            
            if video_type not in type_scores:
                type_scores[video_type] = 0
                type_counts[video_type] = 0
            
            type_counts[video_type] += 1
            
            # Calculate score from performance
            if video.performance:
                views = video.performance.get('views', 0)
                likes = video.performance.get('likes', 0)
                comments = video.performance.get('comments', 0)
                engagement = likes + (comments * 5)  # Comments are more valuable
                score = views + (engagement * 10)
                type_scores[video_type] += score
        
        # Calculate average scores
        avg_scores = {}
        for video_type in type_scores:
            if type_counts[video_type] > 0:
                avg_scores[video_type] = type_scores[video_type] / type_counts[video_type]
            else:
                avg_scores[video_type] = 1
        
        # Include types with no videos yet (give them minimum weight)
        for video_type in VIDEO_TYPES:
            if video_type not in avg_scores:
                avg_scores[video_type] = 1  # Minimum score
        
        # Normalize to weights (sum = 1)
        total = sum(avg_scores.values())
        weights = {}
        for video_type, score in avg_scores.items():
            # Ensure minimum 5% weight for exploration
            weights[video_type] = max(0.05, score / total) if total > 0 else 1.0 / len(VIDEO_TYPES)
        
        # Re-normalize after applying minimums
        total_weights = sum(weights.values())
        weights = {t: w / total_weights for t, w in weights.items()}
        
        # Save weights file for pro_video_generator to use
        weights_file = Path("type_weights.json")
        with open(weights_file, 'w') as f:
            json.dump(weights, f, indent=2)
        
        print(f"📊 Updated type weights: {weights}")
        
        return weights
    
    def update_hook_word_performance(self) -> Dict:
        """
        v17.7.7: Analyze hook words that correlate with high performance.
        
        Integrates with HookWordTracker from enhancements_v9 to learn
        which words in hooks drive engagement.
        
        Returns: Dict of power words and words to avoid
        """
        try:
            from enhancements_v9 import get_hook_tracker
            hook_tracker = get_hook_tracker()
            
            all_videos = self.metadata_store.get_all()
            
            for video in all_videos:
                if video.performance and video.hook:
                    views = video.performance.get('views', 0)
                    avg_views = self.preferences.get('avg_views', 100)
                    
                    hook_tracker.record_hook_performance(
                        hook=video.hook,
                        views=views,
                        avg_views=avg_views
                    )
            
            power_words = hook_tracker.get_power_words()
            avoid_words = hook_tracker.get_words_to_avoid()
            
            print(f"📊 Hook word analysis: {len(power_words)} power words, {len(avoid_words)} to avoid")
            
            return {
                "power_words": power_words,
                "avoid_words": avoid_words
            }
            
        except ImportError:
            print("   [!] HookWordTracker not available")
            return {}
        except Exception as e:
            print(f"   [!] Hook word analysis failed: {e}")
            return {}
    
    def calculate_engagement_rate(self, video: VideoMetadata) -> float:
        """
        v17.7.7: Calculate engagement rate for a video.
        
        Engagement Rate = (Likes + Comments*3 + Shares*5) / Views * 100
        """
        if not video.performance:
            return 0.0
        
        views = video.performance.get('views', 1)
        likes = video.performance.get('likes', 0)
        comments = video.performance.get('comments', 0)
        shares = video.performance.get('shares', 0)
        
        if views < 1:
            return 0.0
        
        engagement = likes + (comments * 3) + (shares * 5)
        return (engagement / views) * 100
    
    def get_best_posting_times(self) -> Dict:
        """
        v17.7.7: Analyze which posting times perform best.
        
        Returns: Dict with best hours and days for posting
        """
        all_videos = self.metadata_store.get_all()
        
        hour_performance = {}
        day_performance = {}
        
        for video in all_videos:
            if video.uploaded_at and video.performance:
                try:
                    upload_dt = datetime.fromisoformat(video.uploaded_at)
                    hour = upload_dt.hour
                    day = upload_dt.strftime("%A")
                    
                    engagement = self.calculate_engagement_rate(video)
                    
                    if hour not in hour_performance:
                        hour_performance[hour] = []
                    hour_performance[hour].append(engagement)
                    
                    if day not in day_performance:
                        day_performance[day] = []
                    day_performance[day].append(engagement)
                except:
                    pass
        
        # Calculate averages
        best_hours = sorted(
            [(h, sum(e)/len(e)) for h, e in hour_performance.items() if len(e) >= 2],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        best_days = sorted(
            [(d, sum(e)/len(e)) for d, e in day_performance.items() if len(e) >= 2],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        result = {
            "best_hours": [h for h, _ in best_hours],
            "best_days": [d for d, _ in best_days],
            "sample_size": len(all_videos)
        }
        
        print(f"📊 Best posting times: Hours {result['best_hours']}, Days {result['best_days']}")
        
        return result


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'VideoMetadata',
    'VideoMetadataStore',
    'YouTubeAnalyticsFetcher',
    'AnalyticsAnalyzer',
    'FeedbackLoopController',
]


if __name__ == "__main__":
    print("=" * 60)
    print("📊 Analytics Feedback Loop System")
    print("=" * 60)
    
    controller = FeedbackLoopController()
    
    print("\n📋 Current Preferences:")
    for key, value in controller.preferences.items():
        print(f"   {key}: {value}")
    
    print("\n📈 Fetching YouTube Analytics...")
    fetcher = YouTubeAnalyticsFetcher()
    
    # Try to get channel videos
    videos = fetcher.get_channel_videos(10)
    print(f"   Found {len(videos)} videos")
    
    for video in videos[:3]:
        print(f"   - {video['title'][:50]}...")
        stats = fetcher.get_video_stats(video['video_id'])
        if stats:
            print(f"     Views: {stats['views']}, Likes: {stats['likes']}")
    
    print("\n🎯 Content Guidance for Next Video:")
    guidance = controller.get_content_guidance()
    for key, value in guidance.items():
        print(f"   {key}: {value}")





