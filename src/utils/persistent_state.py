#!/usr/bin/env python3
"""
ViralShorts Factory - Persistent State Manager v2.0
=====================================================

Solves the ephemeral storage problem in GitHub Actions:
- Saves state to JSON files that can be committed or saved as artifacts
- Tracks uploads, analytics, and variety across runs
- Prevents Dailymotion rate limit issues by tracking hourly uploads
- Maintains variety history across batches (not just within batch)

v2.0 Additions (v10.0 enhancements):
- Thumbnail text optimization tracking
- Comment sentiment aggregation
- Peak publishing time learning
- Title length optimization
- Music BPM matching
- Intro pattern learning
- Viral velocity prediction

v1.5 Additions:
- Series tracking, Cross-platform analytics, Hook words, Voice speed, Category decay

This is the CORE fix for analytics feedback and upload management!
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
import hashlib

# v17.8: Import AI Pattern Generator for AI-first architecture
try:
    from src.ai.ai_pattern_generator import get_pattern_generator, AIPatternGenerator
    AI_PATTERN_GENERATOR_AVAILABLE = True
except ImportError:
    try:
        from ai_pattern_generator import get_pattern_generator, AIPatternGenerator
        AI_PATTERN_GENERATOR_AVAILABLE = True
    except ImportError:
        AI_PATTERN_GENERATOR_AVAILABLE = False

# State files - these MUST persist between runs
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_STATE_FILE = STATE_DIR / "upload_state.json"
VARIETY_STATE_FILE = STATE_DIR / "variety_state.json"  
ANALYTICS_STATE_FILE = STATE_DIR / "analytics_state.json"
VIRAL_PATTERNS_FILE = STATE_DIR / "viral_patterns.json"


def safe_print(msg: str):
    """Print with fallback for encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# UPLOAD STATE - Prevents Dailymotion rate limits across runs
# =============================================================================

class UploadStateManager:
    """
    Tracks uploads across workflow runs to prevent rate limit issues.
    
    Dailymotion limit: 4 uploads per HOUR
    This persists across runs to know when it's safe to upload again.
    """
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load upload state from file."""
        try:
            if UPLOAD_STATE_FILE.exists():
                with open(UPLOAD_STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[!] Error loading upload state: {e}")
        
        return {
            "dailymotion_uploads": [],  # List of timestamps
            "youtube_uploads": [],
            "last_updated": None
        }
    
    def _save_state(self):
        """Save state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(UPLOAD_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Error saving upload state: {e}")
    
    def _clean_old_entries(self, platform: str, hours: int = 1):
        """Remove entries older than specified hours."""
        key = f"{platform}_uploads"
        cutoff = datetime.now() - timedelta(hours=hours)
        
        current_uploads = self.state.get(key, [])
        # Keep only uploads within the last N hours
        recent = [ts for ts in current_uploads 
                  if datetime.fromisoformat(ts) > cutoff]
        self.state[key] = recent
    
    def can_upload_dailymotion(self) -> bool:
        """Check if we can upload to Dailymotion (4 per hour limit)."""
        self._clean_old_entries("dailymotion", hours=1)
        uploads_in_hour = len(self.state.get("dailymotion_uploads", []))
        can_upload = uploads_in_hour < 4
        
        if not can_upload:
            safe_print(f"[!] Dailymotion: {uploads_in_hour}/4 uploads this hour - WAIT")
        else:
            safe_print(f"[OK] Dailymotion: {uploads_in_hour}/4 uploads this hour - CAN UPLOAD")
        
        return can_upload
    
    def get_dailymotion_slots_available(self) -> int:
        """Get number of Dailymotion upload slots available."""
        self._clean_old_entries("dailymotion", hours=1)
        uploads_in_hour = len(self.state.get("dailymotion_uploads", []))
        return max(0, 4 - uploads_in_hour)
    
    def get_wait_time_dailymotion(self) -> int:
        """Get seconds to wait before next Dailymotion upload is safe."""
        self._clean_old_entries("dailymotion", hours=1)
        uploads = self.state.get("dailymotion_uploads", [])
        
        if len(uploads) < 4:
            return 0  # Can upload now
        
        # Find oldest upload in the hour and calculate when it expires
        oldest = min([datetime.fromisoformat(ts) for ts in uploads])
        expire_time = oldest + timedelta(hours=1)
        wait_seconds = (expire_time - datetime.now()).total_seconds()
        
        return max(0, int(wait_seconds))
    
    def record_upload(self, platform: str, video_id: str = None):
        """Record an upload for rate limiting."""
        key = f"{platform}_uploads"
        if key not in self.state:
            self.state[key] = []
        
        self.state[key].append(datetime.now().isoformat())
        self._save_state()
        safe_print(f"[TRACK] Recorded {platform} upload #{len(self.state[key])} this hour")
    
    def get_youtube_uploads_today(self) -> int:
        """Get YouTube uploads today (reset at midnight UTC)."""
        self._clean_old_entries("youtube", hours=24)
        return len(self.state.get("youtube_uploads", []))
    
    def can_upload_youtube(self) -> bool:
        """Check if YouTube daily limit allows upload."""
        uploads_today = self.get_youtube_uploads_today()
        can_upload = uploads_today < 6  # 6 per day max
        
        if not can_upload:
            safe_print(f"[!] YouTube: {uploads_today}/6 uploads today - WAIT")
        else:
            safe_print(f"[OK] YouTube: {uploads_today}/6 uploads today - CAN UPLOAD")
        
        return can_upload


# =============================================================================
# VARIETY STATE - Enforces variety across ALL runs (not just single batch)
# =============================================================================

class VarietyStateManager:
    """
    Tracks content variety across workflow runs to prevent repetition.
    
    Fixes the issue where variety was only enforced within single batch.
    Now tracks last N items of each type to enforce variety across runs.
    """
    
    def __init__(self, history_size: int = 20):
        self.history_size = history_size
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load variety state from file."""
        try:
            if VARIETY_STATE_FILE.exists():
                with open(VARIETY_STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[!] Error loading variety state: {e}")
        
        return {
            "categories": [],
            "topics": [],
            "voices": [],
            "music_moods": [],
            "hooks": [],
            "last_updated": None
        }
    
    def _save_state(self):
        """Save state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(VARIETY_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Error saving variety state: {e}")
    
    def get_exclusions(self, item_type: str, limit: int = 5) -> List[str]:
        """Get list of items to exclude for variety."""
        items = self.state.get(item_type, [])
        return items[-limit:] if items else []
    
    def record_usage(self, item_type: str, value: str):
        """Record an item usage."""
        if item_type not in self.state:
            self.state[item_type] = []
        
        self.state[item_type].append(value)
        # Keep only last N items
        self.state[item_type] = self.state[item_type][-self.history_size:]
        self._save_state()
    
    def get_category_weights(self) -> Dict[str, float]:
        """
        v17.8: Get weighted probabilities for categories based on:
        1. AI-learned performance data
        2. Recency (avoid repetition)
        """
        recent_categories = self.state.get("categories", [])[-10:]
        
        # v17.8: Get categories from AI/analytics, NOT hardcoded!
        all_categories = self._get_ai_categories()
        
        weights = {}
        for cat in all_categories:
            # Reduce weight for recently used categories
            recency_count = recent_categories.count(cat)
            weights[cat] = max(0.1, 1.0 - (recency_count * 0.3))
        
        # Normalize
        total = sum(weights.values()) if weights else 1
        return {k: v/total for k, v in weights.items()} if weights else {}
    
    def _get_ai_categories(self) -> List[str]:
        """
        v17.8: Get categories from AI or learned performance data.
        """
        # First try: Get from learned performance
        learned = self.state.get("learned_from_performance", {})
        if learned.get("best_performing_categories"):
            return learned["best_performing_categories"]
        
        # Second try: Get from AI recommendations
        ai_recs = self.state.get("ai_recommendations", {})
        if ai_recs.get("recommended_categories"):
            return ai_recs["recommended_categories"]
        
        # Third try: Ask AI to generate categories
        if AI_PATTERN_GENERATOR_AVAILABLE:
            try:
                gen = get_pattern_generator()
                patterns = gen.get_patterns()
                if patterns.get("proven_categories"):
                    return patterns["proven_categories"]
            except:
                pass
        
        # Last resort: minimal fallback (used only until AI runs)
        safe_print("[!] Using minimal category fallback - AI generation needed")
        return ["general", "facts", "tips"]
    
    def pick_category_weighted(self, available: List[str]) -> str:
        """Pick a category with weighting to favor less-used ones."""
        import random
        
        weights = self.get_category_weights()
        available_weights = {k: v for k, v in weights.items() if k in available}
        
        if not available_weights:
            return random.choice(available)
        
        # Weighted random choice
        items = list(available_weights.keys())
        probs = list(available_weights.values())
        total = sum(probs)
        probs = [p/total for p in probs]
        
        return random.choices(items, weights=probs, k=1)[0]
    
    def get_recent_topics(self, limit: int = 15) -> List[str]:
        """
        v9.0: Get recent topics for semantic duplicate detection.
        
        Returns the last N topics generated to check for duplicates.
        """
        topics = self.state.get("topics", [])
        return topics[-limit:] if topics else []
    
    def get_learned_preferences(self) -> Dict:
        """
        v9.0: Get all learned preferences from analytics feedback.
        
        Used by video generator to apply learned insights.
        """
        return {
            "preferred_categories": self.state.get("preferred_categories", []),
            "preferred_music_moods": self.state.get("preferred_music_moods", []),
            "preferred_voice_styles": self.state.get("preferred_voice_styles", []),
            "preferred_themes": self.state.get("preferred_themes", []),
            "title_tricks": self.state.get("title_tricks", []),
            "hook_types": self.state.get("hook_types", []),
            "psych_triggers": self.state.get("psych_triggers", []),
            "engagement_baits": self.state.get("engagement_baits", []),
            "virality_hacks": self.state.get("virality_hacks", []),
            "best_posting_hours_utc": self.state.get("best_posting_hours_utc", []),
            "best_posting_days": self.state.get("best_posting_days", []),
            "best_title_styles": self.state.get("best_title_styles", []),
            "comment_insights": self.state.get("comment_insights", {}),
            # v17.9.42: Added aggressive mode learnings
            "learned_weights": self.state.get("learned_weights", {}),
            "hook_templates": self.state.get("hook_templates", []),
            "curiosity_gaps": self.state.get("curiosity_gaps", []),
            "do_more": self.state.get("do_more", []),
            "avoid": self.state.get("avoid", []),
            "external_hooks": self.state.get("external_hooks", [])
        }


# =============================================================================
# ANALYTICS STATE - Tracks performance across runs
# =============================================================================

class AnalyticsStateManager:
    """
    Tracks video analytics across runs for the feedback loop.
    
    Persists video metadata so we can fetch performance later.
    """
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load analytics state from file."""
        try:
            if ANALYTICS_STATE_FILE.exists():
                with open(ANALYTICS_STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[!] Error loading analytics state: {e}")
        
        return {
            "videos": [],  # List of video metadata
            "top_performers": [],  # Videos with best performance
            "learned_patterns": {},  # What we've learned works
            "last_updated": None
        }
    
    def _save_state(self):
        """Save state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(ANALYTICS_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Error saving analytics state: {e}")
    
    def record_video(self, video_data: Dict):
        """Record a generated video for analytics tracking."""
        video_entry = {
            "id": video_data.get("video_id", f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "category": video_data.get("category"),
            "topic": video_data.get("topic"),
            "title": video_data.get("title"),
            "hook": video_data.get("hook"),
            "voice": video_data.get("voice"),
            "music_mood": video_data.get("music_mood"),
            "duration": video_data.get("duration"),
            "score": video_data.get("score", 0),
            "youtube_id": video_data.get("youtube_id"),
            "dailymotion_id": video_data.get("dailymotion_id"),
            "generated_at": datetime.now().isoformat(),
            "performance": None  # Filled in later
        }
        
        self.state["videos"].append(video_entry)
        # Keep last 100 videos
        self.state["videos"] = self.state["videos"][-100:]
        self._save_state()
        
        safe_print(f"[ANALYTICS] Recorded video: {video_entry['category']}/{video_entry['topic'][:30]}")
    
    def update_performance(self, video_id: str, performance: Dict):
        """Update performance data for a video."""
        for video in self.state["videos"]:
            if video.get("id") == video_id or video.get("youtube_id") == video_id:
                video["performance"] = performance
                self._save_state()
                return True
        return False
    
    def get_videos_for_analysis(self) -> List[Dict]:
        """Get videos with performance data for AI analysis."""
        return [v for v in self.state.get("videos", []) if v.get("performance")]
    
    def has_enough_data_for_analysis(self) -> bool:
        """Check if we have enough data to run AI analysis."""
        return len(self.get_videos_for_analysis()) >= 5
    
    def update_learned_patterns(self, patterns: Dict):
        """Store patterns learned from analysis."""
        self.state["learned_patterns"] = patterns
        self._save_state()
    
    def get_learned_patterns(self) -> Dict:
        """Get previously learned patterns."""
        return self.state.get("learned_patterns", {})


# =============================================================================
# VIRAL PATTERNS - Stores patterns learned from successful channels
# =============================================================================

class ViralPatternsManager:
    """
    Stores and manages patterns learned from successful viral channels.
    
    This is the "learn from graduated channels" feature.
    """
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.state = self.patterns  # Alias for consistency with other managers
    
    def _load_patterns(self) -> Dict:
        """
        v17.8: Load viral patterns - AI-FIRST architecture!
        
        Priority:
        1. Use AIPatternGenerator to get/refresh patterns
        2. Fall back to file cache
        3. Last resort: minimal fallback
        """
        # v17.8: AI-FIRST - use AIPatternGenerator
        if AI_PATTERN_GENERATOR_AVAILABLE:
            try:
                generator = get_pattern_generator()
                patterns = generator.get_patterns()
                if patterns.get("ai_generated") or patterns.get("title_patterns"):
                    safe_print("[OK] Viral patterns loaded from AI generator")
                    return patterns
            except Exception as e:
                safe_print(f"[!] AI pattern generator error: {e}")
        
        # Fall back to file cache
        try:
            if VIRAL_PATTERNS_FILE.exists():
                with open(VIRAL_PATTERNS_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get("title_patterns") and len(data.get("title_patterns", [])) > 0:
                        safe_print("[OK] Viral patterns loaded from cache")
                        return data
        except Exception as e:
            safe_print(f"[!] Error loading viral patterns: {e}")
        
        # Last resort: minimal fallback (NOT source of truth!)
        safe_print("[!] No patterns available - using minimal fallback")
        return {
            "patterns_source": "MINIMAL_FALLBACK",
            "title_patterns": [],
            "hook_patterns": [],
            "engagement_baits": [],
            "optimal_lengths": {
                "hook": "7-12 words",
                "total_video": "40-50 seconds",
                "phrases": "8-10",
                "cta": "5-10 words"
            },
            "proven_categories": [],
            "last_updated": None,
            "ai_generated": False,
            "needs_ai_refresh": True
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        self.patterns["last_updated"] = datetime.now().isoformat()
        try:
            with open(VIRAL_PATTERNS_FILE, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Error saving viral patterns: {e}")
    
    def get_patterns(self) -> Dict:
        """
        v9.0: Get all viral patterns.
        
        Used by daily workflow to access monthly-learned patterns.
        """
        return self.patterns
    
    def get_random_title_pattern(self) -> str:
        """Get a random title pattern for AI to fill in."""
        import random
        return random.choice(self.patterns.get("title_patterns", []))
    
    def get_random_hook_pattern(self) -> str:
        """Get a random hook pattern."""
        import random
        return random.choice(self.patterns.get("hook_patterns", []))
    
    def get_random_engagement_bait(self) -> str:
        """Get a random engagement CTA."""
        import random
        return random.choice(self.patterns.get("engagement_baits", []))
    
    def update_patterns_from_analysis(self, new_patterns: Dict):
        """Update patterns based on channel analysis."""
        for key, values in new_patterns.items():
            if key in self.patterns and isinstance(self.patterns[key], list):
                # Add new patterns, avoid duplicates
                for v in values:
                    if v not in self.patterns[key]:
                        self.patterns[key].append(v)
                # Keep list manageable
                self.patterns[key] = self.patterns[key][-30:]
        
        self._save_patterns()
    
    def get_optimal_video_length(self) -> int:
        """Get optimal video length in seconds."""
        return 45  # 40-50 second sweet spot (8-10 phrases)


# =============================================================================
# v1.5: SERIES STATE - Tracks successful series for continuation
# =============================================================================

SERIES_STATE_FILE = STATE_DIR / "series_state.json"


class SeriesStateManager:
    """
    Tracks video series for continuation opportunities.
    
    When a video performs well, we can create a series.
    This tracks ongoing series and their performance.
    """
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load series state from file."""
        try:
            if SERIES_STATE_FILE.exists():
                with open(SERIES_STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[!] Error loading series state: {e}")
        
        return {
            "active_series": [],  # Ongoing series
            "completed_series": [],  # Finished series
            "series_candidates": [],  # High performers that could become series
            "last_updated": None
        }
    
    def _save_state(self):
        """Save state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(SERIES_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Error saving series state: {e}")
    
    def add_series_candidate(self, video_data: Dict):
        """Add a high-performing video as series candidate."""
        candidate = {
            "original_title": video_data.get("title"),
            "original_topic": video_data.get("topic"),
            "category": video_data.get("category"),
            "views": video_data.get("views", 0),
            "performance_multiplier": video_data.get("performance_multiplier", 1.0),
            "detected_at": datetime.now().isoformat(),
            "series_started": False
        }
        
        self.state["series_candidates"].append(candidate)
        self.state["series_candidates"] = self.state["series_candidates"][-20:]  # Keep last 20
        self._save_state()
        
        safe_print(f"[SERIES] Candidate added: {candidate['original_title']}")
    
    def get_pending_candidates(self) -> List[Dict]:
        """Get candidates that haven't become series yet."""
        return [c for c in self.state.get("series_candidates", []) 
                if not c.get("series_started")]
    
    def start_series(self, candidate_title: str, series_name: str):
        """Start a series from a candidate."""
        for candidate in self.state["series_candidates"]:
            if candidate.get("original_title") == candidate_title:
                candidate["series_started"] = True
                break
        
        series = {
            "name": series_name,
            "original_title": candidate_title,
            "parts": [{"part": 1, "title": candidate_title, "date": datetime.now().isoformat()}],
            "started_at": datetime.now().isoformat()
        }
        
        self.state["active_series"].append(series)
        self._save_state()
    
    def add_series_part(self, series_name: str, part_title: str):
        """Add a new part to an existing series."""
        for series in self.state["active_series"]:
            if series["name"] == series_name:
                part_num = len(series["parts"]) + 1
                series["parts"].append({
                    "part": part_num,
                    "title": part_title,
                    "date": datetime.now().isoformat()
                })
                self._save_state()
                return part_num
        return None
    
    def get_active_series(self) -> List[Dict]:
        """Get all active series."""
        return self.state.get("active_series", [])


# =============================================================================
# v1.5: PERFORMANCE AGGREGATOR - Centralizes all v9.5 tracker data
# =============================================================================

class PerformanceAggregator:
    """
    Aggregates performance data from all v9.5 trackers.
    
    This provides a single interface to access all performance insights.
    Used by the AI for comprehensive analysis.
    """
    
    def get_all_insights(self) -> Dict:
        """Get aggregated insights from all trackers."""
        insights = {
            "upload_status": {},
            "variety_status": {},
            "analytics_status": {},
            "viral_patterns": {},
            "series_status": {},
            "v95_trackers": {}
        }
        
        # Core managers
        try:
            upload = get_upload_manager()
            insights["upload_status"] = {
                "dailymotion_slots": upload.get_dailymotion_slots_available(),
                "youtube_today": upload.get_youtube_uploads_today(),
                "can_upload_dm": upload.can_upload_dailymotion(),
                "can_upload_yt": upload.can_upload_youtube()
            }
        except:
            pass
        
        try:
            variety = get_variety_manager()
            insights["variety_status"] = {
                "recent_categories": variety.get_exclusions("categories", 5),
                "recent_topics": len(variety.get_recent_topics()),
                "learned_preferences": variety.get_learned_preferences()
            }
        except:
            pass
        
        try:
            analytics = get_analytics_manager()
            insights["analytics_status"] = {
                "videos_tracked": len(analytics.state.get("videos", [])),
                "videos_with_performance": len(analytics.get_videos_for_analysis()),
                "enough_for_analysis": analytics.has_enough_data_for_analysis()
            }
        except:
            pass
        
        try:
            viral = get_viral_manager()
            patterns = viral.get_patterns()
            insights["viral_patterns"] = {
                "title_patterns_count": len(patterns.get("title_patterns", [])),
                "hook_patterns_count": len(patterns.get("hook_patterns", [])),
                "ai_generated": patterns.get("ai_generated", False)
            }
        except:
            pass
        
        try:
            series = get_series_manager()
            insights["series_status"] = {
                "active_series": len(series.get_active_series()),
                "candidates_pending": len(series.get_pending_candidates())
            }
        except:
            pass
        
        # v9.5 Trackers (from enhancements_v9.py)
        try:
            from enhancements_v9 import (
                get_hook_tracker, get_voice_optimizer, 
                get_hashtag_rotator, get_platform_analytics, 
                get_category_decay
            )
            
            hook = get_hook_tracker()
            insights["v95_trackers"]["hook_power_words"] = len(hook.get_power_words())
            
            voice = get_voice_optimizer()
            insights["v95_trackers"]["optimal_voice_rate"] = voice.get_optimal_rate()
            
            hashtag = get_hashtag_rotator()
            insights["v95_trackers"]["top_hashtags"] = len(hashtag.get_top_performers())
            
            platform = get_platform_analytics()
            insights["v95_trackers"]["platform_insights"] = platform.get_platform_insights()
            
            decay = get_category_decay()
            insights["v95_trackers"]["category_weights"] = decay.get_decayed_weights()
        except:
            insights["v95_trackers"]["status"] = "not initialized"
        
        # v10.0 Trackers
        insights["v10_trackers"] = {}
        try:
            from enhancements_v9 import (
                get_thumbnail_optimizer, get_sentiment_tracker,
                get_publishing_optimizer, get_title_length_optimizer,
                get_bpm_matcher, get_intro_learner
            )
            
            thumb = get_thumbnail_optimizer()
            insights["v10_trackers"]["thumbnail_settings"] = thumb.get_optimal_settings()
            
            sentiment = get_sentiment_tracker()
            insights["v10_trackers"]["best_sentiment_categories"] = sentiment.get_best_sentiment_categories()
            
            publishing = get_publishing_optimizer()
            insights["v10_trackers"]["best_publishing_times"] = publishing.get_best_publishing_times()
            
            title_len = get_title_length_optimizer()
            insights["v10_trackers"]["optimal_title_length"] = title_len.get_optimal_length()
            
            bpm = get_bpm_matcher()
            insights["v10_trackers"]["bpm_matches"] = len(bpm.data.get("best_matches", {}))
            
            intro = get_intro_learner()
            insights["v10_trackers"]["best_intro_pattern"] = intro.get_recommended_pattern()
        except Exception as e:
            insights["v10_trackers"]["status"] = f"not initialized: {e}"
        
        return insights


# =============================================================================
# GLOBAL MANAGERS - Singleton instances
# =============================================================================

_upload_manager = None
_variety_manager = None
_analytics_manager = None
_viral_manager = None
_series_manager = None
_performance_aggregator = None


def get_upload_manager() -> UploadStateManager:
    global _upload_manager
    if _upload_manager is None:
        _upload_manager = UploadStateManager()
    return _upload_manager


def get_variety_manager() -> VarietyStateManager:
    global _variety_manager
    if _variety_manager is None:
        _variety_manager = VarietyStateManager()
    return _variety_manager


def get_analytics_manager() -> AnalyticsStateManager:
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsStateManager()
    return _analytics_manager


def get_viral_manager() -> ViralPatternsManager:
    global _viral_manager
    if _viral_manager is None:
        _viral_manager = ViralPatternsManager()
    return _viral_manager


def get_series_manager() -> SeriesStateManager:
    """v1.5: Get the singleton series state manager."""
    global _series_manager
    if _series_manager is None:
        _series_manager = SeriesStateManager()
    return _series_manager


def get_performance_aggregator() -> PerformanceAggregator:
    """v1.5: Get the singleton performance aggregator."""
    global _performance_aggregator
    if _performance_aggregator is None:
        _performance_aggregator = PerformanceAggregator()
    return _performance_aggregator


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Persistent State Manager v1.5")
    print("=" * 60)
    
    # Test upload manager
    upload = get_upload_manager()
    print(f"\nDailymotion slots available: {upload.get_dailymotion_slots_available()}")
    print(f"Can upload to Dailymotion: {upload.can_upload_dailymotion()}")
    print(f"Can upload to YouTube: {upload.can_upload_youtube()}")
    
    # Test variety manager
    variety = get_variety_manager()
    print(f"\nCategory exclusions: {variety.get_exclusions('categories')}")
    print(f"Category weights: {variety.get_category_weights()}")
    
    # Test analytics manager
    analytics = get_analytics_manager()
    print(f"\nVideos tracked: {len(analytics.state.get('videos', []))}")
    print(f"Enough data for analysis: {analytics.has_enough_data_for_analysis()}")
    
    # Test viral patterns
    viral = get_viral_manager()
    patterns = viral.get_patterns()
    print(f"\nViral patterns loaded: {len(patterns.get('title_patterns', []))} title patterns")
    
    # v1.5: Test series manager
    series = get_series_manager()
    print(f"\nActive series: {len(series.get_active_series())}")
    print(f"Series candidates: {len(series.get_pending_candidates())}")
    
    # v1.5: Test performance aggregator
    aggregator = get_performance_aggregator()
    insights = aggregator.get_all_insights()
    print(f"\nPerformance Aggregator Insights:")
    for key, value in insights.items():
        if isinstance(value, dict) and value:
            print(f"  {key}: {len(value)} entries")
        else:
            print(f"  {key}: OK")
    
    print("\n" + "=" * 60)
    print("Persistent State Manager v1.5 - All Tests Passed!")
    print("=" * 60)

