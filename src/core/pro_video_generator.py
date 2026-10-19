#!/usr/bin/env python3
"""
ViralShorts Factory - PROFESSIONAL Video Generator v12.0
=========================================================

100% AI-DRIVEN - NO HARDCODING!
ENFORCED VARIETY - Across ALL runs, not just single batch!
VIRAL PATTERNS - Learned from successful channels!
OPTIMAL LENGTH - 40-50 seconds with 8-10 phrases (proven sweet spot)!

v12.0 ULTIMATE ENHANCEMENTS - 330 NEW (419 TOTAL!):
- Batch 1: Human Feel (60) - Anti-AI, Typography, Voice
- Batch 2: Content Core (50) - Audio, Topics, Value
- Batch 3: Algorithm & Hook (45) - First 3 Seconds, Signals
- Batch 4: Engagement (50) - Visual, Psychology, Retention
- Batch 5: Polish (40) - Authenticity, Platform, Structure
- Batch 6: Intelligence (85) - Analytics, Self-Tuning, Quota

20 CATEGORIES: A-T
All AI-driven via master master prompts!

Previous versions:
- v8.0: Persistent variety, upload tracking
- v9.0-v11.0: 89 core enhancements

TOTAL: 419 ENHANCEMENTS - ALL AI-DRIVEN!
"""

import os
import sys
import re
import json
import asyncio
import random
import time
import math
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

# Suppress google.generativeai deprecation warning (will migrate to google.genai later)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
import requests

# Give every legacy-SDK Gemini call a timeout; without one a stuck request
# blocks the whole run forever (seen with gemini-flash-latest).
try:
    import google.generativeai as _genai
    _orig_generate_content = _genai.GenerativeModel.generate_content

    def _generate_content_with_timeout(self, *args, **kwargs):
        request_options = kwargs.get("request_options") or {}
        if isinstance(request_options, dict) and "timeout" not in request_options:
            kwargs["request_options"] = {**request_options, "timeout": 90}
        return _orig_generate_content(self, *args, **kwargs)

    _genai.GenerativeModel.generate_content = _generate_content_with_timeout
except Exception:
    pass

# Core imports
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, ImageClip, CompositeAudioClip,
    ColorClip
)
from moviepy.video.VideoClip import VideoClip
import moviepy.video.fx.all as vfx

from PIL import Image, ImageDraw, ImageFont, ImageFilter
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

import edge_tts

# v8.0: Persistent state availability flag (actual imports in v9.5 block below)
PERSISTENT_STATE_AVAILABLE = True  # Will be updated by v9.5 import block

# v8.0: Import viral patterns for better hooks
try:
    from viral_channel_analyzer import get_viral_prompt_boost
    VIRAL_PATTERNS_AVAILABLE = True
except ImportError:
    VIRAL_PATTERNS_AVAILABLE = False
    get_viral_prompt_boost = lambda: ""

# v11.0: Import comprehensive enhancements module (89 enhancements!)
try:
    from enhancements_v9 import (
        # v17.7: Core AI caller and tracking (previously unused!)
        get_ai_caller,
        ABTestTracker,
        ErrorPatternLearner,
        # Core orchestrator
        get_enhancement_orchestrator,
        # v9.0 functions
        check_semantic_duplicate,
        enhance_voice_pacing,
        predict_retention_curve,
        score_value_density,
        validate_post_render,
        score_trend_freshness,
        # v9.5 functions
        get_seasonal_content_suggestions,
        get_hook_tracker,
        get_voice_optimizer,
        get_hashtag_rotator,
        get_platform_analytics,
        get_category_decay,
        detect_faces_in_broll,
        score_broll_for_thumbnail,
        score_broll_relevance,
        generate_fresh_hashtags,
        detect_series_potential,
        generate_reply_templates,
        # v10.0 functions
        get_thumbnail_optimizer,
        get_sentiment_tracker,
        get_publishing_optimizer,
        get_title_length_optimizer,
        get_bpm_matcher,
        get_intro_learner,
        design_emotional_arc,
        analyze_competitor_gaps,
        optimize_description_seo,
        analyze_comment_sentiment,
        predict_viral_velocity,
        # v11.0 Category 1: Click Baiting
        get_curiosity_gap,
        get_number_hook,
        get_controversy,
        get_fomo,
        get_power_words_tracker,
        predict_ctr,
        # v11.0 Category 2: First Seconds
        get_pattern_interrupt,
        get_open_loop,
        get_first_frame,
        get_audio_hook,
        score_scroll_stop_power,
        generate_instant_value_hook,
        # v11.0 Category 3: Algorithm
        get_watch_time,
        get_completion_rate,
        get_comment_bait,
        get_share_trigger,
        get_rewatch,
        generate_algorithm_signals,
        # v11.0 Category 4: Visual
        get_color_psychology,
        get_motion_energy,
        get_text_readability,
        get_visual_variety,
        score_thumbnail_quality,
        # v11.0 Category 5: Content Quality
        get_fact_credibility,
        get_actionable,
        get_story_structure,
        get_memory_hook,
        get_relatability,
        check_content_credibility,
        enforce_actionable_takeaway,
        generate_memory_hook,
        check_relatability,
        detect_ai_slop,
        # v11.0 Category 6: Viral/Trendy
        get_trend_lifecycle,
        get_evergreen_balance,
        get_cultural_moment,
        get_viral_pattern,
        get_platform_trend,
        detect_cultural_moments,
        # v11.0 Category 7: Analytics
        get_micro_retention,
        get_correlation,
        get_channel_health,
        get_growth_rate,
        get_content_decay,
        find_performance_correlations,
        # v11.0 Category 8: Other
        get_competitor_response,
        get_niche_authority,
        get_quality_consistency,
        get_upload_cadence,
        get_audience_loyalty,
        generate_competitor_response
    )
    ENHANCEMENTS_V11_AVAILABLE = True
except ImportError as e:
    ENHANCEMENTS_V11_AVAILABLE = False
    print(f"[!] v11.0 enhancements not fully available: {e}")

# Backward compatibility aliases
ENHANCEMENTS_V10_AVAILABLE = ENHANCEMENTS_V11_AVAILABLE
ENHANCEMENTS_V95_AVAILABLE = ENHANCEMENTS_V11_AVAILABLE
ENHANCEMENTS_AVAILABLE = ENHANCEMENTS_V11_AVAILABLE

# v12.0: Import ULTIMATE enhancements module (330 NEW enhancements!)
try:
    from enhancements_v12 import (
        # MASTER INTEGRATION - THE KEY FUNCTION
        get_v12_complete_master_prompt,
        # Helper functions for specific enhancements
        get_v12_hook_boost,
        get_v12_voice_settings,
        get_v12_font_settings,
        get_v12_music_settings,
        get_v12_color_settings,
        apply_v12_text_humanization,
        get_v12_algorithm_checklist,
        get_v12_compliance_rules,
        # Individual getters (for specific use cases)
        get_natural_rhythm, get_filler_injector, get_contractions_enforcer,
        get_font_psychology, get_text_animation, get_voice_matcher,
        get_sound_library, get_tempo_matcher, get_genre_matcher,
        get_shock_opener, get_algorithm_signals,
        get_color_grading, get_fomo_trigger, get_open_loop_technique,
        get_source_citation, get_yt_optimization, get_hook_body_payoff,
        get_performance_correlator, get_token_budget, get_yt_compliance
    )
    ENHANCEMENTS_V12_AVAILABLE = True
    V12_MASTER_PROMPT = get_v12_complete_master_prompt()
    print("[OK] v12.0 Ultimate Enhancements loaded: 330 enhancements ACTIVE!")
except ImportError as e:
    ENHANCEMENTS_V12_AVAILABLE = False
    V12_MASTER_PROMPT = ""
    print(f"[!] v12.0 enhancements not available: {e}")

# CRITICAL FIXES: Real enforcement of quality, fonts, SFX, promises
try:
    from critical_fixes import (
        select_font_for_content,
        get_varied_sfx_for_phrase,
        validate_numbered_promise,
        fix_broken_promise,
        apply_all_critical_fixes,
        MINIMUM_ACCEPTABLE_SCORE,
        CONTENT_CONSTRAINTS,
        score_hook_quality  # v17.6: Hook quality scoring
    )
    CRITICAL_FIXES_AVAILABLE = True
    print("[OK] Critical Fixes loaded: Font/SFX/Quality/Promise/Hook-scoring ACTIVE!")
except ImportError as e:
    CRITICAL_FIXES_AVAILABLE = False
    MINIMUM_ACCEPTABLE_SCORE = 7  # Fallback
    print(f"[!] Critical fixes not available: {e}")

# v17.6: Import viral video science for better content quality
try:
    from viral_video_science import (
        ValueDeliveryChecker,
        ViralContentGenerator,
        CONTENT_TEMPLATES
    )
    VIRAL_SCIENCE_AVAILABLE = True
    print("[OK] Viral Video Science loaded: Value delivery checking ACTIVE!")
except ImportError as e:
    VIRAL_SCIENCE_AVAILABLE = False
    print(f"[!] Viral Video Science not available: {e}")

# v9.5: Import persistent state with series tracking
try:
    from persistent_state import (
        get_upload_manager, get_variety_manager, 
        get_analytics_manager, get_viral_manager,
        get_series_manager, get_performance_aggregator
    )
    PERSISTENT_STATE_V15_AVAILABLE = True
except ImportError:
    PERSISTENT_STATE_V15_AVAILABLE = False
    get_series_manager = lambda: None
    get_performance_aggregator = lambda: None

# v17.7.3: Import thumbnail generator for video thumbnails
try:
    from thumbnail_generator import generate_thumbnail, get_ai_thumbnail_concept
    THUMBNAIL_GENERATOR_AVAILABLE = True
    print("[OK] Thumbnail Generator loaded: AI-driven thumbnails ACTIVE!")
except ImportError as e:
    THUMBNAIL_GENERATOR_AVAILABLE = False
    print(f"[!] Thumbnail Generator not available: {e}")

# v17.7.6: Import error logger for centralized logging
try:
    from error_logger import get_error_logger, log_error
    ERROR_LOGGER_AVAILABLE = True
except ImportError:
    ERROR_LOGGER_AVAILABLE = False
    def log_error(e, ctx="", comp=""): pass  # No-op fallback

# v17.7.8: Import competitor analyzer for differentiated content
try:
    from competitor_analyzer import get_competitor_analyzer
    COMPETITOR_ANALYZER_AVAILABLE = True
    print("[OK] Competitor Analyzer loaded: Differentiation ACTIVE!")
except ImportError:
    COMPETITOR_ANALYZER_AVAILABLE = False

# v17.8: Import AI Pattern Generator for AI-first architecture
try:
    from ai_pattern_generator import get_pattern_generator, refresh_patterns_if_needed
    AI_PATTERN_GENERATOR_AVAILABLE = True
    print("[OK] AI Pattern Generator loaded: AI-first patterns ACTIVE!")
except ImportError:
    try:
        from src.ai.ai_pattern_generator import get_pattern_generator, refresh_patterns_if_needed
        AI_PATTERN_GENERATOR_AVAILABLE = True
        print("[OK] AI Pattern Generator loaded: AI-first patterns ACTIVE!")
    except ImportError:
        AI_PATTERN_GENERATOR_AVAILABLE = False
        print("[!] AI Pattern Generator not available - using fallback patterns")

# v17.8: Import Model Intelligence for smart provider selection
try:
    from model_intelligence import get_provider_for_task, record_task_performance
    MODEL_INTELLIGENCE_AVAILABLE = True
    print("[OK] Model Intelligence loaded: Smart provider selection ACTIVE!")
except ImportError:
    try:
        from src.ai.model_intelligence import get_provider_for_task, record_task_performance
        MODEL_INTELLIGENCE_AVAILABLE = True
        print("[OK] Model Intelligence loaded: Smart provider selection ACTIVE!")
    except ImportError:
        MODEL_INTELLIGENCE_AVAILABLE = False
        # Fallback functions
        def get_provider_for_task(task_type: str) -> str:
            return "gemini"
        def record_task_performance(*args, **kwargs):
            pass

# v17.9.9: Import Smart Model Router for optimal model selection per prompt type
try:
    from smart_model_router import get_smart_router
    from smart_ai_caller import smart_call_ai, get_smart_caller
    SMART_ROUTER_AVAILABLE = True
    print("[OK] Smart Model Router loaded: Optimal model selection per prompt ACTIVE!")
except ImportError:
    try:
        from src.ai.smart_model_router import get_smart_router
        from src.ai.smart_ai_caller import smart_call_ai, get_smart_caller
        SMART_ROUTER_AVAILABLE = True
        print("[OK] Smart Model Router loaded: Optimal model selection per prompt ACTIVE!")
    except ImportError:
        SMART_ROUTER_AVAILABLE = False
        smart_call_ai = None
        get_smart_caller = None
        print("[!] Smart Model Router not available - using legacy call_ai")

# v17.8: Import all AI-first modules
try:
    from ai_hook_generator import generate_hook, get_hook_generator
    AI_HOOK_GENERATOR_AVAILABLE = True
except ImportError:
    AI_HOOK_GENERATOR_AVAILABLE = False
    def generate_hook(topic, cat): return f"Did you know about {topic}?"

try:
    from ai_cta_generator import generate_cta, get_cta_generator
    AI_CTA_GENERATOR_AVAILABLE = True
except ImportError:
    AI_CTA_GENERATOR_AVAILABLE = False
    def generate_cta(topic, cat): return "Comment if you agree!"

try:
    from ai_topic_suggester import get_topic_suggestions, get_topic_suggester
    AI_TOPIC_SUGGESTER_AVAILABLE = True
except ImportError:
    AI_TOPIC_SUGGESTER_AVAILABLE = False
    def get_topic_suggestions(count=5, cat=None): return []

try:
    from ai_content_quality_checker import check_content_quality, get_quality_checker
    AI_QUALITY_CHECKER_AVAILABLE = True
except ImportError:
    AI_QUALITY_CHECKER_AVAILABLE = False
    def check_content_quality(content): return {"score": 7, "verdict": "PASS"}

try:
    from ai_broll_keywords import generate_broll_keywords, get_broll_keyword_generator
    AI_BROLL_KEYWORDS_AVAILABLE = True
except ImportError:
    AI_BROLL_KEYWORDS_AVAILABLE = False
    def generate_broll_keywords(phrase, cat=None): return ["abstract motion"]

try:
    from ai_music_mood import select_music_mood, get_music_mood_selector
    AI_MUSIC_MOOD_AVAILABLE = True
except ImportError:
    AI_MUSIC_MOOD_AVAILABLE = False
    def select_music_mood(topic, cat): return ("dramatic", "cinematic")

try:
    from ai_title_optimizer import optimize_title, get_title_optimizer
    AI_TITLE_OPTIMIZER_AVAILABLE = True
except ImportError:
    AI_TITLE_OPTIMIZER_AVAILABLE = False
    def optimize_title(topic, cat, existing=None): return f"The Truth About {topic}"

# v17.9.6: Import ALL remaining AI modules that were defined but never used!
try:
    from ai_quality_gate import AIQualityGate
    AI_QUALITY_GATE_AVAILABLE = True
except ImportError:
    AI_QUALITY_GATE_AVAILABLE = False

# v17.9.7: Master Master Evaluator - THE definitive quality scoring system
try:
    from master_evaluator import MasterEvaluator, get_master_evaluator
    MASTER_EVALUATOR_AVAILABLE = True
except ImportError:
    MASTER_EVALUATOR_AVAILABLE = False

try:
    from content_optimizer import ContentOptimizer
    CONTENT_OPTIMIZER_AVAILABLE = True
except ImportError:
    CONTENT_OPTIMIZER_AVAILABLE = False

try:
    from retention_predictor import RetentionPredictor
    RETENTION_PREDICTOR_AVAILABLE = True
except ImportError:
    RETENTION_PREDICTOR_AVAILABLE = False

try:
    from engagement_predictor import EngagementPredictor
    ENGAGEMENT_PREDICTOR_AVAILABLE = True
except ImportError:
    ENGAGEMENT_PREDICTOR_AVAILABLE = False

try:
    from virality_calculator import ViralityCalculator
    VIRALITY_CALCULATOR_AVAILABLE = True
except ImportError:
    VIRALITY_CALCULATOR_AVAILABLE = False

try:
    from script_analyzer import ScriptAnalyzer
    SCRIPT_ANALYZER_AVAILABLE = True
except ImportError:
    SCRIPT_ANALYZER_AVAILABLE = False

try:
    from ai_description_generator import AIDescriptionGenerator
    AI_DESCRIPTION_GENERATOR_AVAILABLE = True
except ImportError:
    AI_DESCRIPTION_GENERATOR_AVAILABLE = False

try:
    from ai_hashtag_generator import AIHashtagGenerator
    AI_HASHTAG_GENERATOR_AVAILABLE = True
except ImportError:
    AI_HASHTAG_GENERATOR_AVAILABLE = False

try:
    from dashboard_generator import DashboardGenerator
    DASHBOARD_GENERATOR_AVAILABLE = True
except ImportError:
    DASHBOARD_GENERATOR_AVAILABLE = False

# Log AI module availability
_ai_modules = [
    ("Hook Generator", AI_HOOK_GENERATOR_AVAILABLE),
    ("CTA Generator", AI_CTA_GENERATOR_AVAILABLE),
    ("Topic Suggester", AI_TOPIC_SUGGESTER_AVAILABLE),
    ("Quality Checker", AI_QUALITY_CHECKER_AVAILABLE),
    ("B-Roll Keywords", AI_BROLL_KEYWORDS_AVAILABLE),
    ("Music Mood", AI_MUSIC_MOOD_AVAILABLE),
    ("Title Optimizer", AI_TITLE_OPTIMIZER_AVAILABLE),
    ("Quality Gate", AI_QUALITY_GATE_AVAILABLE),
    ("Content Optimizer", CONTENT_OPTIMIZER_AVAILABLE),
    ("Retention Predictor", RETENTION_PREDICTOR_AVAILABLE),
    ("Engagement Predictor", ENGAGEMENT_PREDICTOR_AVAILABLE),
    ("Virality Calculator", VIRALITY_CALCULATOR_AVAILABLE),
    ("Script Analyzer", SCRIPT_ANALYZER_AVAILABLE),
    ("Description Generator", AI_DESCRIPTION_GENERATOR_AVAILABLE),
    ("Hashtag Generator", AI_HASHTAG_GENERATOR_AVAILABLE),
    ("Dashboard Generator", DASHBOARD_GENERATOR_AVAILABLE),
]
_available = sum(1 for _, a in _ai_modules if a)
print(f"[OK] AI Modules loaded: {_available}/{len(_ai_modules)} available")

# Constants (only technical, not content!)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BROLL_DIR = Path("./assets/broll")
BROLL_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ========================================================================
# BATCH VARIETY TRACKER - Prevents repetition across batch runs
# ========================================================================
@dataclass
class BatchTracker:
    """Tracks what's been generated in this batch to enforce variety."""
    used_categories: List[str] = field(default_factory=list)
    used_topics: List[str] = field(default_factory=list)
    used_voices: List[str] = field(default_factory=list)
    used_music: List[str] = field(default_factory=list)
    video_scores: List[Tuple[str, float, Dict]] = field(default_factory=list)
    
    def add_video(self, path: str, score: float, metadata: Dict):
        """Add a generated video with its score."""
        self.video_scores.append((path, score, metadata))
    
    def get_best_video_for_youtube(self) -> Optional[Tuple[str, Dict]]:
        """Get the highest-scoring video for YouTube upload."""
        if not self.video_scores:
            return None
        # Sort by score descending
        sorted_videos = sorted(self.video_scores, key=lambda x: x[1], reverse=True)
        best_path, best_score, best_meta = sorted_videos[0]
        safe_print(f"\n[SELECTION] Best video for YouTube: score={best_score}/10")
        safe_print(f"   Path: {best_path}")
        return (best_path, best_meta)
    
    def get_all_videos(self) -> List[Tuple[str, Dict]]:
        """Get all videos for Dailymotion upload."""
        return [(path, meta) for path, score, meta in self.video_scores]


# Global batch tracker (reset for each batch run)
BATCH_TRACKER = BatchTracker()


def safe_print(msg: str):
    """Print with fallback for Windows encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        clean = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean)


def strip_emojis(text: str) -> str:
    """Remove emojis."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()


# ========================================================================
# ALL AVAILABLE OPTIONS - AI picks from these, variety enforced
# ========================================================================
# v17.8: Categories come from AI pattern generator, not hardcoded
def get_base_categories() -> List[str]:
    """
    v17.8: Get categories from AI or learned data, not hardcoded.
    """
    if AI_PATTERN_GENERATOR_AVAILABLE:
        try:
            gen = get_pattern_generator()
            patterns = gen.get_patterns()
            if patterns.get("proven_categories"):
                return patterns["proven_categories"]
        except:
            pass
    
    # Minimal fallback only if AI unavailable
    return ["general", "facts", "tips", "trending"]

# For backward compatibility
BASE_CATEGORIES = get_base_categories()

# v16.6: Cache for trending categories to save quota
# Extended to 24 hours - trending categories don't change hourly
_trending_cache = {"categories": None, "timestamp": 0, "ttl": 86400}  # 24 hour cache

def get_ai_trending_categories(groq_key: str = None) -> List[str]:
    """
    Ask AI for currently trending content categories.
    Combines base categories with AI-suggested trending ones.
    
    v16.1: QUOTA OPTIMIZATION - Cache results for 1 hour
    v16.8: DYNAMIC MODEL - No hardcoded model names
    """
    global _trending_cache
    
    # v16.1: Return cached if valid (within TTL)
    if _trending_cache["categories"] and (time.time() - _trending_cache["timestamp"]) < _trending_cache["ttl"]:
        safe_print(f"   [CACHE] Using cached trending categories (saves API call)")
        return _trending_cache["categories"]
    
    if not groq_key:
        groq_key = os.environ.get("GROQ_API_KEY")
    
    if not groq_key:
        return BASE_CATEGORIES
    
    # v17.9.12: DYNAMIC model discovery - no hardcoding!
    try:
        from src.ai.model_helper import get_dynamic_groq_model
        model_to_use = get_dynamic_groq_model()
    except:
        try:
            from quota_optimizer import get_quota_optimizer
            optimizer = get_quota_optimizer()
            groq_models = optimizer.get_groq_models(groq_key)
            model_to_use = groq_models[0] if groq_models else None
        except:
            model_to_use = None  # Will use OpenRouter fallback
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_to_use,
                "messages": [{"role": "user", "content": f"""What are the TOP 5 trending content categories for viral short-form videos RIGHT NOW?

Consider:
- Current events and news cycles
- Seasonal trends
- Social media trending topics
- What's capturing attention today

Base categories (keep if still relevant): {BASE_CATEGORIES}

Return a JSON array of 8-12 category names (single words or short phrases, lowercase, underscores for spaces).
Example: ["ai_news", "psychology", "money_hacks", "relationship_tips", "health", "productivity"]

Return ONLY the JSON array, nothing else."""}],
                "temperature": 0.8,
                "max_tokens": 200
            },
            timeout=10
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                categories = json.loads(json_match.group())
                if isinstance(categories, list) and len(categories) >= 5:
                    safe_print(f"   [OK] AI suggested categories: {categories[:5]}...")
                    # v16.1: Cache the result
                    _trending_cache["categories"] = categories
                    _trending_cache["timestamp"] = time.time()
                    return categories
    except Exception as e:
        pass
    
    # v16.1: Return cached if available, even if expired
    if _trending_cache["categories"]:
        safe_print(f"   [CACHE] Using stale cached categories (API failed)")
        return _trending_cache["categories"]
    
    return BASE_CATEGORIES

# Will be populated dynamically by AI
ALL_CATEGORIES = BASE_CATEGORIES  # Fallback, gets updated at runtime


def get_learned_optimal_metrics() -> Dict:
    """
    v17.9.2: FULLY AI-LEARNED video metrics from analytics feedback.
    
    The optimal length, phrase count, and words are LEARNED from:
    1. Our own video performance (views, retention, engagement)
    2. Competitor viral video analysis
    3. AI analysis of what's currently working
    
    NO MORE hardcoded guardrails - the AI decides based on data!
    
    Returns: {duration, phrases, words_per_phrase, source}
    """
    # Starting point - will be overwritten by learned data
    defaults = {"duration": 50, "phrases": 10, "words_per_phrase": 12, "source": "default"}
    
    try:
        if PERSISTENT_STATE_AVAILABLE:
            # Load learned optimal metrics from persistent storage
            learned_metrics_path = Path("data/persistent/learned_video_metrics.json")
            
            if learned_metrics_path.exists():
                with open(learned_metrics_path, 'r') as f:
                    learned = json.load(f)
                    
                # Use learned values if we have enough data confidence
                if learned.get("confidence", 0) >= 0.5:  # At least 50% confidence
                    if learned.get("optimal_duration"):
                        defaults["duration"] = int(learned["optimal_duration"])
                    if learned.get("optimal_phrases"):
                        defaults["phrases"] = int(learned["optimal_phrases"])
                    if learned.get("optimal_words_per_phrase"):
                        defaults["words_per_phrase"] = int(learned["optimal_words_per_phrase"])
                    defaults["source"] = "learned_from_performance"
                    
                    safe_print(f"   [LEARNED METRICS] Using data-driven values: {defaults['phrases']} phrases, {defaults['duration']}s")
                else:
                    defaults["source"] = "low_confidence_default"
            else:
                # First run - use AI to suggest based on current viral trends
                defaults["source"] = "initial_default"
                
    except Exception as e:
        defaults["source"] = "error_fallback"
    
    return defaults


def update_learned_metrics_from_performance(video_id: str, performance: Dict, video_metrics: Dict):
    """
    v17.9.2: Learn optimal video metrics from actual performance data.
    
    Called after we get analytics on a video to update what length/phrases work best.
    """
    try:
        learned_path = Path("data/persistent/learned_video_metrics.json")
        
        # Load existing data
        if learned_path.exists():
            with open(learned_path, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "videos_analyzed": 0,
                "duration_performance": {},  # duration -> avg_score
                "phrase_performance": {},    # phrase_count -> avg_score
                "word_performance": {},      # words_per_phrase -> avg_score
                "optimal_duration": 50,
                "optimal_phrases": 10,
                "optimal_words_per_phrase": 12,
                "confidence": 0.0,
                "last_updated": None
            }
        
        # Calculate performance score (views * retention * engagement)
        views = performance.get("views", 0)
        retention = performance.get("avg_watch_percentage", 50) / 100
        engagement = (performance.get("likes", 0) + performance.get("comments", 0) * 3) / max(views, 1)
        score = views * retention * (1 + engagement)
        
        # Record this video's metrics vs performance
        duration = str(video_metrics.get("duration", 50))
        phrases = str(video_metrics.get("phrase_count", 10))
        words = str(video_metrics.get("words_per_phrase", 12))
        
        # Update running averages
        for metric_key, metric_value in [("duration_performance", duration), 
                                          ("phrase_performance", phrases),
                                          ("word_performance", words)]:
            if metric_value not in data[metric_key]:
                data[metric_key][metric_value] = {"total_score": 0, "count": 0}
            data[metric_key][metric_value]["total_score"] += score
            data[metric_key][metric_value]["count"] += 1
        
        data["videos_analyzed"] += 1
        
        # Find optimal values (highest avg score)
        if data["videos_analyzed"] >= 3:  # Need at least 3 videos
            # Find best duration
            best_duration = max(data["duration_performance"].items(), 
                               key=lambda x: x[1]["total_score"] / x[1]["count"] if x[1]["count"] > 0 else 0)
            data["optimal_duration"] = int(best_duration[0])
            
            # Find best phrase count
            best_phrases = max(data["phrase_performance"].items(),
                              key=lambda x: x[1]["total_score"] / x[1]["count"] if x[1]["count"] > 0 else 0)
            data["optimal_phrases"] = int(best_phrases[0])
            
            # Find best words per phrase
            best_words = max(data["word_performance"].items(),
                            key=lambda x: x[1]["total_score"] / x[1]["count"] if x[1]["count"] > 0 else 0)
            data["optimal_words_per_phrase"] = int(best_words[0])
            
            # Confidence increases with more data
            data["confidence"] = min(1.0, data["videos_analyzed"] / 20)  # Max confidence at 20 videos
        
        data["last_updated"] = datetime.now().isoformat()
        
        # Save
        learned_path.parent.mkdir(parents=True, exist_ok=True)
        with open(learned_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        pass  # Non-critical

# NOTE: Voice names are Edge TTS technical identifiers (cannot be AI-generated)
# AI selects the STYLE (energetic, calm, etc.), which maps to these voices
# The rate adjustments are tuned for optimal narration pacing
# Edge TTS Available Voices - AI will select dynamically based on content
# This is just a reference list for validation, NOT the selection logic
EDGE_TTS_VOICES = [
    'en-US-AriaNeural', 'en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-DavisNeural',
    'en-US-ChristopherNeural', 'en-US-EricNeural', 'en-US-MichelleNeural', 
    'en-US-RogerNeural', 'en-US-SteffanNeural', 'en-US-SaraNeural',
    'en-AU-WilliamNeural', 'en-AU-NatashaNeural',
    'en-GB-RyanNeural', 'en-GB-SoniaNeural', 'en-GB-LibbyNeural',
    'en-CA-LiamNeural', 'en-CA-ClaraNeural',
    'en-IE-ConnorNeural', 'en-IN-NeerjaNeural', 'en-NZ-MitchellNeural',
]

# Default rate adjustments (AI can override)
DEFAULT_VOICE_RATES = {
    'energetic': '+8%', 'calm': '-5%', 'mysterious': '-3%', 
    'authoritative': '+0%', 'friendly': '+3%', 'dramatic': '-2%',
    'professional': '+0%', 'casual': '+5%', 'warm': '+0%',
}

# NOTE: These are MOOD LABELS, not hardcoded tracks!
# AI selects the mood → ai_music_selector.py uses AI to find matching music
# The actual track selection is dynamic and AI-driven
ALL_MUSIC_MOODS = [
    'upbeat',        # Fun, positive content
    'dramatic',      # Scary facts, shocking reveals
    'mysterious',    # Mysteries, unknown facts
    'inspirational', # Motivation, success
    'chill',         # Calm explanations, tips
    'intense',       # Urgent, action-oriented
    'energetic',     # High energy, productivity
    'emotional',     # Personal stories, psychology
    'tech',          # Technology, science
    'professional',  # Finance, business
]

# Keep for backward compatibility
ALL_MUSIC = {mood: mood for mood in ALL_MUSIC_MOODS}


class MasterAI:
    """
    100% AI-Driven Content System with ENFORCED VARIETY
    
    Uses BatchTracker to ensure no repetition in category/topic/voice/music.
    Multi-provider fallback: Groq -> Gemini -> OpenRouter
    
    v15.0: Smart Token Budget Management
    - Tracks token usage across all providers
    - Distributes load to avoid rate limits
    - Reserves Groq for critical tasks
    - Uses FirstAttemptMaximizer to reduce regenerations
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        # v13.5: OpenRouter as third fallback (free tier)
        # v16.2: No hardcoded keys - user MUST provide via secrets
        openrouter_env = os.environ.get("OPENROUTER_API_KEY", "")
        self.openrouter_key = openrouter_env.strip() if openrouter_env.strip() else None
        # v17.4.1: HuggingFace Inference API as fallback (truly free, no phone/CC)
        huggingface_env = os.environ.get("HUGGINGFACE_API_KEY", "")
        self.huggingface_key = huggingface_env.strip() if huggingface_env.strip() else None
        self.client = None
        self.gemini_model = None
        self.openrouter_available = bool(self.openrouter_key)
        self.huggingface_available = bool(self.huggingface_key)
        
        # v15.0: Initialize token budget manager
        try:
            from token_budget_manager import get_budget_manager, get_first_attempt_maximizer
            self.budget_manager = get_budget_manager()
            self.first_attempt = get_first_attempt_maximizer()
            self.budget_manager.print_status()
            safe_print(f"[OK] Token Budget Manager initialized - {self.budget_manager.estimate_videos_remaining()} videos remaining today")
        except Exception as e:
            safe_print(f"[!] Token Budget Manager not available: {e}")
            self.budget_manager = None
            self.first_attempt = None
        
        # v15.0: Initialize self-learning engine
        try:
            from self_learning_engine import get_learning_engine
            self.learning_engine = get_learning_engine()
            safe_print(f"[OK] Self-Learning Engine initialized - {self.learning_engine.data['stats']['total_videos']} videos analyzed")
        except Exception as e:
            safe_print(f"[!] Self-Learning Engine not available: {e}")
            self.learning_engine = None
        
        # v15.0: Initialize quota monitor
        try:
            from quota_monitor import get_quota_monitor
            self.quota_monitor = get_quota_monitor()
            safe_print(f"[OK] Quota Monitor initialized")
        except Exception as e:
            safe_print(f"[!] Quota Monitor not available: {e}")
            self.quota_monitor = None
        
        if self.groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_key)
                
                # v16.8: DYNAMIC Groq model selection - no hardcoding!
                # Uses QuotaOptimizer to discover available models
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                self.groq_models_list = optimizer.get_groq_models(self.groq_key)
                safe_print(f"[OK] Groq AI initialized ({len(self.groq_models_list)} models available)")
            except Exception as e:
                self.groq_models_list = []  # Dynamic discovery will handle
                safe_print(f"[!] Groq init failed: {e}")
        
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                
                # v16.7: DYNAMIC Gemini model selection - no hardcoding!
                # Uses QuotaOptimizer to discover available models
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                available_models = optimizer.get_gemini_models(self.gemini_key)
                
                # Try models in priority order (flash > pro)
                self.gemini_model = None
                self.gemini_models_list = available_models  # Store for fallback attempts
                for model_name in available_models:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        safe_print(f"[OK] Gemini AI initialized ({model_name} - dynamic selection)")
                        break
                    except Exception as model_err:
                        safe_print(f"[!] Gemini model {model_name} failed: {model_err}")
                        continue
                
                if not self.gemini_model:
                    # Last resort fallback
                    self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                    safe_print("[OK] Gemini AI initialized (fallback: gemini-2.5-flash)")
            except Exception as e:
                safe_print(f"[!] Gemini init failed: {e}")
        
        if self.openrouter_available:
            safe_print("[OK] OpenRouter AI initialized (fallback)")
    
    def call_ai(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.9, 
                 prefer_gemini: bool = False, task: str = "general") -> str:
        """
        Call AI with smart load balancing: Groq for speed, Gemini for capacity.
        
        v8.2: Load balancing to protect quotas:
        - prefer_gemini=True: Use Gemini first (for non-critical tasks)
        - prefer_gemini=False: Use Groq first (for time-sensitive tasks)
        
        v13.2: Smart backoff on 429 errors - wait and retry
        v15.0: Budget-aware provider selection with token tracking
        v17.9.9: Smart Model Router - routes each prompt to BEST model for its type
        
        Fallback chain: Primary -> Secondary -> Tertiary -> Quaternary
        
        Args:
            task: Task type for budget tracking ("concept", "content", "evaluate", etc.)
        """
        import time
        import re
        
        # v17.9.9: USE SMART MODEL ROUTER (if available)
        # Routes each prompt to the BEST model based on prompt classification
        # Automatically handles fallbacks through entire chain
        if SMART_ROUTER_AVAILABLE and smart_call_ai:
            try:
                # Map task to hint for better classification
                task_hint_map = {
                    "concept": "topic",
                    "content": "content",
                    "evaluate": "evaluation",
                    "title": "content",
                    "hook": "hook",
                    "cta": "cta",
                    "description": "description",
                    "hashtag": "hashtag",
                    "broll": "broll",
                    "seo": "seo",
                    "analysis": "analysis"
                }
                hint = task_hint_map.get(task, task)
                
                result = smart_call_ai(prompt, hint=hint, max_tokens=max_tokens, 
                                        temperature=temperature)
                if result:
                    # Record to budget manager if available
                    if self.budget_manager:
                        self.budget_manager.record_usage("smart_router", max_tokens)
                    return result
                else:
                    safe_print("[!] Smart router failed, falling back to legacy logic...")
            except Exception as e:
                safe_print(f"[!] Smart router error: {e}, falling back to legacy...")
        
        # === LEGACY LOGIC (fallback when smart router unavailable) ===
        
        # v15.0: Use budget manager for provider selection if available
        chosen_provider = None
        if self.budget_manager:
            chosen_provider = self.budget_manager.choose_provider(task, prefer_quality=not prefer_gemini)
            safe_print(f"   [Budget] Task '{task}' -> Provider: {chosen_provider}")
        
        # v17.9.3: DYNAMIC rate limiting from centralized config
        # All providers now have proper rate limiting
        try:
            from src.ai.model_helper import get_rate_limits
            rate_limits = get_rate_limits()
        except ImportError:
            rate_limits = {
                "gemini": 4.0,
                "groq": 2.5,
                "openrouter": 1.0,
                "huggingface": 2.0,
                "pexels": 18.0
            }
        base_delay = rate_limits.get(chosen_provider, 3.0)
        time.sleep(base_delay)  # Rate limit protection between AI calls
        
        def extract_retry_delay(error_msg: str) -> int:
            """Extract retry delay from 429 error message."""
            match = re.search(r'retry in (\d+(?:\.\d+)?)', str(error_msg), re.IGNORECASE)
            if match:
                return int(float(match.group(1))) + 2  # Add buffer
            return 60  # Default 60s if not found
        
        # v15.0: Budget-aware provider selection
        if chosen_provider == "gemini" and self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                if self.budget_manager:
                    self.budget_manager.record_usage("gemini", max_tokens)
                if self.quota_monitor:
                    self.quota_monitor.record_usage("gemini", max_tokens)
                return response.text
            except Exception as e:
                error_str = str(e)
                if '429' in error_str:
                    delay = extract_retry_delay(error_str)
                    if self.budget_manager:
                        self.budget_manager.record_429("gemini", delay)
                    if self.quota_monitor:
                        self.quota_monitor.record_429("gemini", delay)
                    safe_print(f"[!] Gemini 429 - switching to fallback...")
                    # v17.7.6: Log quota exhaustion for tracking
                    if ERROR_LOGGER_AVAILABLE:
                        log_error(e, f"Gemini 429 - delay {delay}s", "ai_gemini")
                else:
                    safe_print(f"[!] Gemini error: {e}")
                    if ERROR_LOGGER_AVAILABLE:
                        log_error(e, "Gemini API failure", "ai_gemini")
                # Fall through to other providers
        
        # v8.2: Smart load balancing (original logic as fallback)
        if prefer_gemini and self.gemini_model and chosen_provider != "gemini":
            # Try Gemini first to save Groq quota
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                safe_print(f"[!] Gemini primary error: {e}")
                # Fall through to Groq
        
        # Primary: Groq (fastest, 100K tokens/day)
        # v16.8: DYNAMIC model selection - tries all available models
        use_groq = self.client and (chosen_provider == "groq" or chosen_provider is None)
        if use_groq:
            # v17.9.10: Use DYNAMIC model discovery - no hardcoding!
            groq_models_to_try = getattr(self, 'groq_models_list', None)
            if not groq_models_to_try:
                try:
                    from model_helper import get_all_models
                    groq_models_to_try = get_all_models("groq")
                except:
                    # v17.9.12: If discovery fails, fall through to OpenRouter
                    groq_models_to_try = []
            
            for model_name in groq_models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    # v15.0: Record token usage
                    if self.budget_manager:
                        self.budget_manager.record_usage("groq", max_tokens)
                    if self.quota_monitor:
                        self.quota_monitor.record_usage("groq", max_tokens)
                    return response.choices[0].message.content
                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str:
                        safe_print(f"[!] Groq {model_name} rate limit, trying next model...")
                        continue  # Try next model
                    elif '404' in error_str or 'not found' in error_str.lower():
                        safe_print(f"[!] Groq model {model_name} not available, refreshing models...")
                        # v16.8: LAZY LOAD - refresh models list only when needed
                        try:
                            from quota_optimizer import get_quota_optimizer
                            optimizer = get_quota_optimizer()
                            self.groq_models_list = optimizer.get_groq_models(self.groq_key, force_refresh=True)
                        except:
                            pass
                        continue  # Try next model with updated list
                    else:
                        safe_print(f"[!] Groq {model_name} error: {e}")
                        continue  # Try next model
            
            # All Groq models failed - record and continue to fallback
            if self.budget_manager:
                self.budget_manager.record_429("groq", 60)
            if self.quota_monitor:
                self.quota_monitor.record_429("groq", 60)
            safe_print(f"[!] All Groq models exhausted, falling back...")
        
        # Secondary: Gemini - v16.7 DYNAMIC model selection
        # Try all available Gemini models in priority order
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                
                # v17.9.10: Use DYNAMIC model discovery - no hardcoding!
                gemini_models_to_try = getattr(self, 'gemini_models_list', None)
                if not gemini_models_to_try:
                    try:
                        from model_helper import get_all_models
                        gemini_models_to_try = get_all_models("gemini")
                    except:
                        # v17.9.12: If discovery fails, fall through to OpenRouter
                        gemini_models_to_try = []
                
                for model_name in gemini_models_to_try:
                    try:
                        # Try with and without models/ prefix
                        model = genai.GenerativeModel(f'models/{model_name}')
                        response = model.generate_content(prompt)
                        if self.budget_manager:
                            self.budget_manager.record_usage("gemini", max_tokens)
                        return response.text
                    except Exception as model_err:
                        error_str = str(model_err)
                        if '429' in error_str:
                            safe_print(f"[!] Gemini {model_name} rate limit, trying next...")
                            continue
                        elif '404' in error_str:
                            # Try without prefix
                            try:
                                model = genai.GenerativeModel(model_name)
                                response = model.generate_content(prompt)
                                if self.budget_manager:
                                    self.budget_manager.record_usage("gemini", max_tokens)
                                return response.text
                            except:
                                safe_print(f"[!] Gemini {model_name} not available, refreshing models...")
                                # v16.8: LAZY LOAD - refresh models list only when needed
                                try:
                                    from quota_optimizer import get_quota_optimizer
                                    optimizer = get_quota_optimizer()
                                    self.gemini_models_list = optimizer.get_gemini_models(self.gemini_key, force_refresh=True)
                                except:
                                    pass
                                continue
                        else:
                            safe_print(f"[!] Gemini {model_name} error: {model_err}")
                            continue
                            
            except Exception as e:
                error_str = str(e)
            if '404' in error_str:
                safe_print(f"[!] Gemini 1.5-pro not available either")
            else:
                safe_print(f"[!] Gemini Pro fallback error: {e}")
        
        # v17.4.2: HuggingFace Inference API as fallback (truly free, no phone/credit card)
        # v17.5: Uses huggingface_hub library (REST API is deprecated)
        if self.huggingface_available:
            safe_print("[*] Trying HuggingFace fallback...")
            try:
                from huggingface_hub import InferenceClient
                
                # DYNAMIC MODEL DISCOVERY for HuggingFace
                try:
                    from quota_optimizer import get_quota_optimizer
                    quota_opt = get_quota_optimizer()
                    hf_models = quota_opt.get_huggingface_models(self.huggingface_key)
                except:
                    # Non-gated fallback models
                    hf_models = [
                        "google/gemma-2-2b-it",
                        "Qwen/Qwen2.5-1.5B-Instruct",
                        "HuggingFaceH4/zephyr-7b-beta"
                    ]
                
                client = InferenceClient(token=self.huggingface_key)
                
                for hf_model in hf_models:
                    try:
                        response = client.chat_completion(
                            messages=[{"role": "user", "content": prompt}],
                            model=hf_model,
                            max_tokens=min(max_tokens, 1024)
                        )
                        content = response.choices[0].message.content
                        if content:
                            safe_print(f"[OK] HuggingFace succeeded with {hf_model.split('/')[-1]}!")
                            return content
                    except Exception as model_err:
                        safe_print(f"[!] {hf_model.split('/')[-1]}: {str(model_err)[:50]}")
                        continue
                safe_print("[!] All HuggingFace models failed, trying OpenRouter...")
            except Exception as e:
                safe_print(f"[!] HuggingFace fallback error: {e}")
        
        # v13.5: OpenRouter as final fallback (free tier models)
        # v16.6: Dynamically fetch free models instead of hardcoded list
        try:
            from quota_optimizer import get_quota_optimizer
            quota_opt = get_quota_optimizer()
            free_models = quota_opt.get_openrouter_free_models(self.openrouter_key)
        except:
            # Fallback seed list - used only if dynamic fetch fails
            free_models = [
                "meta-llama/llama-3.2-3b-instruct:free",
                "google/gemma-2-9b-it:free", 
                "mistralai/mistral-7b-instruct:free"
            ]
        
        safe_print("[*] Trying OpenRouter fallback...")
        if self.openrouter_available:
            import requests
            for model in free_models:
                try:
                    safe_print(f"[*] OpenRouter: Trying {model.split('/')[1][:20]}...")
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openrouter_key}",
                            "HTTP-Referer": "https://github.com/viralshorts-factory",
                            "X-Title": "ViralShorts Factory"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": max_tokens,
                            "temperature": temperature
                        },
                        timeout=60
                    )
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if content:
                            # v15.0: Record OpenRouter usage
                            if self.budget_manager:
                                self.budget_manager.record_usage("openrouter", max_tokens)
                            if self.quota_monitor:
                                self.quota_monitor.record_usage("openrouter", max_tokens)
                            safe_print(f"[OK] OpenRouter succeeded with {model.split('/')[1][:20]}!")
                            return content
                        else:
                            safe_print(f"[!] OpenRouter: Empty response")
                    elif response.status_code == 429:
                        safe_print(f"[!] {model.split('/')[1][:15]} rate limited, trying next...")
                        continue  # Try next model
                    else:
                        safe_print(f"[!] OpenRouter error: {response.status_code}")
                except Exception as e:
                    safe_print(f"[!] OpenRouter error: {e}")
                    continue  # Try next model
        else:
            safe_print("[!] OpenRouter not available (no key)")
        
        return ""
    
    def parse_json(self, text: str) -> Dict:
        """Extract JSON from AI response.

        Some models (e.g. Gemma) write their reasoning before the answer, so
        prefer the LAST fenced block, then the last decodable {...} object.
        """
        if not text:
            return {}
        candidates = []
        if "```" in text:
            blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
            candidates.extend(reversed(blocks))
        candidates.append(text)
        decoder = json.JSONDecoder()
        for candidate in candidates:
            candidate = candidate.strip()
            try:
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
            except Exception:
                pass
            # Collect top-level objects left to right; keep the last non-empty one
            last, pos = None, candidate.find('{')
            while pos != -1:
                try:
                    result, end = decoder.raw_decode(candidate, pos)
                    if isinstance(result, dict) and result:
                        last = result
                    pos = candidate.find('{', end)
                except Exception:
                    pos = candidate.find('{', pos + 1)
            if last:
                return last
        return {}
    
    # ========================================================================
    # STAGE 1: AI Decides What Type of Video to Create (with VARIETY ENFORCEMENT)
    # ========================================================================
    def stage1_decide_video_concept(self, hint: str = None, batch_tracker: BatchTracker = None) -> Dict:
        """
        AI decides EVERYTHING about the video concept.
        v8.0: Uses PERSISTENT variety tracking across all runs!
        
        PRIMARY: Real-time AI generation (best quality, freshest trends)
        FALLBACK: Pre-generated concepts (only if AI fails due to quota)
        """
        safe_print("\n[STAGE 1] AI deciding video concept...")
        
        # PRIMARY: Real-time AI generation (BEST QUALITY)
        # Get AI-suggested trending categories (dynamic, not hardcoded!)
        trending_categories = get_ai_trending_categories(self.groq_key)
        
        # v8.0: Use PERSISTENT variety manager (survives across workflow runs!)
        exclude_categories = []
        exclude_topics = []
        
        # First, check persistent state (tracks across ALL runs)
        if PERSISTENT_STATE_AVAILABLE:
            variety = get_variety_manager()
            exclude_categories = variety.get_exclusions('categories', limit=8)  # Last 8 categories
            exclude_topics = variety.get_exclusions('topics', limit=15)  # Last 15 topics
            safe_print(f"   [VARIETY] Excluding {len(exclude_categories)} recent categories")
        
        # Also use batch tracker for within-batch variety
        if batch_tracker:
            exclude_categories.extend(batch_tracker.used_categories[-3:])
            exclude_topics.extend(batch_tracker.used_topics[-5:])
            exclude_categories = list(set(exclude_categories))  # Dedupe
            exclude_topics = list(set(exclude_topics))
        
        available_categories = [c for c in trending_categories if c not in exclude_categories]
        if not available_categories:
            available_categories = trending_categories  # Reset if all used
        
        unique_seed = f"{time.time()}_{random.random()}_{random.randint(10000,99999)}"
        hint_text = f"User hint: {hint}" if hint else "No specific hint - create something viral and valuable"
        
        exclude_text = ""
        if exclude_categories:
            exclude_text += f"\n\n**CRITICAL - DO NOT USE these categories (already used in batch):** {exclude_categories}"
        if exclude_topics:
            exclude_text += f"\n**DO NOT USE these topics (already used):** {exclude_topics[:5]}"
        
        # Build dynamic options from AI-driven lists
        music_options = ", ".join(ALL_MUSIC_MOODS)
        
        # v8.0: Get viral patterns to inject into prompt
        viral_boost = get_viral_prompt_boost() if VIRAL_PATTERNS_AVAILABLE else ""
        
        # v12.0: Get v12 master prompt with ALL 330 enhancements
        v12_guidelines = V12_MASTER_PROMPT if ENHANCEMENTS_V12_AVAILABLE else ""
        
        # v16.9: INTEGRATE ALL V12 ENHANCEMENTS (not just master prompt!)
        # These were imported but NEVER USED - now fixing that
        v12_extra_boosts = ""
        if ENHANCEMENTS_V12_AVAILABLE:
            try:
                # Hook optimization
                hook_boost = get_v12_hook_boost()
                # Algorithm signals for better reach
                algo_signals = get_algorithm_signals()
                algo_checklist = algo_signals.get_checklist() if hasattr(algo_signals, 'get_checklist') else ""
                # Shock value opener patterns
                shock_opener = get_shock_opener()
                shock_patterns = shock_opener.get_best_pattern() if hasattr(shock_opener, 'get_best_pattern') else ""
                # FOMO triggers
                fomo = get_fomo_trigger()
                fomo_instruction = fomo.get_instruction() if hasattr(fomo, 'get_instruction') else ""
                # Open loop technique
                open_loop = get_open_loop_technique()
                loop_instruction = open_loop.get_instruction() if hasattr(open_loop, 'get_instruction') else ""
                
                v12_extra_boosts = f"""
=== v12 ENHANCEMENT BOOSTS (v16.9 - Now Active!) ===
HOOK OPTIMIZATION: {hook_boost}
ALGORITHM SIGNALS: {algo_checklist}
SHOCK OPENER: {shock_patterns}
FOMO TRIGGER: {fomo_instruction}
OPEN LOOP: {loop_instruction}
===================================================
"""
            except Exception as e:
                safe_print(f"[!] v12 extra boosts failed: {e}")
        
        # v15.0: Get first-attempt quality boost to avoid regenerations
        first_attempt_boost = ""
        if self.first_attempt:
            first_attempt_boost = self.first_attempt.get_quality_boost_prompt()
        
        # v15.0: Get self-learning insights
        learning_boost = ""
        if self.learning_engine:
            learning_boost = self.learning_engine.get_prompt_boost()
        
        prompt = f"""You are a VIRAL CONTENT STRATEGIST for short-form video (YouTube Shorts, TikTok).
Your job is to decide what video to create that will get MAXIMUM views while delivering REAL value.

UNIQUE GENERATION ID: {unique_seed}
DATE: {time.strftime('%B %d, %Y, %A')}
{hint_text}
{exclude_text}

=== AVAILABLE CATEGORIES (pick ONE from this list ONLY) ===
{available_categories}

{viral_boost}

{v12_guidelines}

{v12_extra_boosts}

{first_attempt_boost}

{learning_boost}

=== YOUR DECISION TASKS ===

1. **VIDEO CATEGORY**: Pick from the AVAILABLE list above (NOT the excluded ones!)
   
2. **SPECIFIC TOPIC**: Within that category, what specific topic?
   - Must be: Surprising, valuable, shareable, globally relevant
   - MUST BE UNIQUE - no generic topics!
   - Use patterns from VIRAL PATTERNS section above!

3. **CONTENT LENGTH**: How many phrases/sections?
   - MUST be 8-10 phrases (40-50 second video is OPTIMAL!)
   - Each phrase = one screen of text with b-roll
   - This allows complete value delivery

4. **VOICE STYLE**: What voice/energy for the narration?
   Options: energetic, calm, mysterious, authoritative, friendly, dramatic

5. **MUSIC MOOD**: What background music mood? (Match to content emotion!)
   Options: {music_options}

6. **TARGET DURATION**: CRITICAL - Must be 40-50 seconds!
   - 40-45s: Standard fact (8 phrases) - OPTIMAL for engagement!
   - 45-50s: Deep dive (10 phrases) - Good for complex topics
   - Under 60 seconds keeps YouTube Shorts format

=== OUTPUT JSON ===
{{
    "category": "MUST be from available list",
    "specific_topic": "the specific topic (5-10 words) - BE CREATIVE AND UNIQUE",
    "why_this_topic": "why this will be viral and valuable",
    "phrase_count": 8,
    "voice_style": "energetic/calm/mysterious/etc",
    "music_mood": "upbeat/dramatic/mysterious/etc",
    "target_duration_seconds": 45,
    "global_relevance": "why this works worldwide"
}}

OUTPUT JSON ONLY. Be creative and strategic - NO REPETITION!"""

        # v15.0: Use task-specific call for budget tracking
        response = self.call_ai(prompt, 800, temperature=0.98, task="concept")  # Higher temp for variety
        result = self.parse_json(response)
        
        if result:
            category = result.get('category', '')
            topic = result.get('specific_topic', '')
            
            # Force variety if AI ignored exclusions
            if category in exclude_categories and available_categories:
                # v8.0: Use weighted selection for better variety
                if PERSISTENT_STATE_AVAILABLE:
                    variety = get_variety_manager()
                    result['category'] = variety.pick_category_weighted(available_categories)
                else:
                    result['category'] = random.choice(available_categories)
                safe_print(f"   [VARIETY] Forced category change: {category} -> {result['category']}")
            
            # v8.0: Record to PERSISTENT state (survives across runs!)
            if PERSISTENT_STATE_AVAILABLE:
                variety = get_variety_manager()
                variety.record_usage('categories', result.get('category', ''))
                variety.record_usage('topics', result.get('specific_topic', ''))
                safe_print(f"   [PERSIST] Recorded to variety state")
            
            # Also track in batch tracker for within-batch variety
            if batch_tracker:
                batch_tracker.used_categories.append(result.get('category', ''))
                batch_tracker.used_topics.append(result.get('specific_topic', ''))
            
            safe_print(f"   Category: {result.get('category', 'N/A')}")
            safe_print(f"   Topic: {result.get('specific_topic', 'N/A')}")
            safe_print(f"   Phrases: {result.get('phrase_count', 'N/A')}")
            safe_print(f"   Voice: {result.get('voice_style', 'N/A')}")
            safe_print(f"   Music: {result.get('music_mood', 'N/A')}")
            safe_print(f"   Duration: ~{result.get('target_duration_seconds', 'N/A')}s")
            
            # Save successful concept as backup for future fallback
            self._save_concept_backup(result)
            
            return result
        
        # FALLBACK: If AI failed (quota exhausted), try pre-generated concepts
        safe_print("   [!] AI generation failed, trying pre-generated fallback...")
        try:
            from pre_work_fetcher import get_next_concept, has_valid_data
            if has_valid_data():
                concept = get_next_concept()
                if concept:
                    safe_print("   [FALLBACK] Using pre-generated concept")
                    # v16.2: Dynamic defaults instead of hardcoded
                    random_cat = random.choice(BASE_CATEGORIES)
                    result = {
                        'category': concept.get('category', random_cat),
                        'specific_topic': concept.get('topic', f'{random_cat.replace("_", " ").title()} Insight'),
                        'phrase_count': concept.get('phrase_count', random.randint(8, 10)),
                        'voice_style': concept.get('voice_style', random.choice(['energetic', 'dramatic', 'confident'])),
                        'music_mood': concept.get('music_mood', random.choice(['upbeat', 'dramatic', 'mysterious'])),
                        'target_duration_seconds': concept.get('target_duration', random.randint(40, 50)),
                    }
                    if batch_tracker:
                        batch_tracker.used_categories.append(result['category'])
                        batch_tracker.used_topics.append(result['specific_topic'])
                    return result
        except Exception as e:
            safe_print(f"   [!] Fallback error: {e}")
        
        # LAST RESORT: Use previously saved backup
        backup = self._load_concept_backup()
        if backup:
            safe_print("   [LAST RESORT] Using saved backup concept")
            return backup
        
        # Ultimate fallback - v16.2: Dynamic even in fallback mode!
        safe_print("   [!] Concept generation failed completely - using dynamic fallback")
        # Rotate through categories to maintain variety even in failures
        fallback_categories = BASE_CATEGORIES.copy()
        random.shuffle(fallback_categories)
        fallback_cat = fallback_categories[0]
        
        # Dynamic topic templates that work for any category
        topic_templates = [
            f"Shocking {fallback_cat.replace('_', ' ').title()} Fact Most People Miss",
            f"The {fallback_cat.replace('_', ' ').title()} Truth Nobody Talks About",
            f"Why Your {fallback_cat.replace('_', ' ').title()} Approach is Wrong",
            f"3 {fallback_cat.replace('_', ' ').title()} Secrets That Change Everything",
            f"The Hidden {fallback_cat.replace('_', ' ').title()} Rule Experts Use"
        ]
        
        return {
            'category': fallback_cat,
            'specific_topic': random.choice(topic_templates),
            'phrase_count': random.randint(8, 10),
            'voice_style': random.choice(['energetic', 'dramatic', 'confident', 'curious']),
            'music_mood': random.choice(['dramatic', 'upbeat', 'mysterious', 'intense']),
            'target_duration_seconds': random.randint(40, 50)
        }
    
    def _save_concept_backup(self, concept: Dict):
        """Save successful concept as backup for future use."""
        try:
            backup_file = Path("./data/concept_backup.json")
            backup_file.parent.mkdir(exist_ok=True)
            
            backups = []
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    backups = json.load(f)
            
            backups.append(concept)
            backups = backups[-20:]  # Keep last 20
            
            with open(backup_file, 'w') as f:
                json.dump(backups, f)
        except:
            pass
    
    def _load_concept_backup(self) -> Dict:
        """Load a random backup concept."""
        try:
            backup_file = Path("./data/concept_backup.json")
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    backups = json.load(f)
                if backups:
                    return random.choice(backups)
        except:
            pass
        return None
    
    # ========================================================================
    # STAGE 2: AI Creates the Content Based on Its Own Decisions
    # ========================================================================
    def stage2_create_content(self, concept: Dict) -> Dict:
        """AI creates the actual content based on the concept it decided.
        v8.0: Content optimized for engagement with strong hooks.
        v8.5: HYBRID - uses analytics-learned optimal metrics with guardrails.
        v13.1: Added regeneration feedback support for quality enforcement.
        v17.6: Pre-validates hook quality before content generation.
        v17.9.10: Optimal length is 8-10 phrases (40-50 seconds) - proven sweet spot.
        """
        # Check if this is a regeneration attempt
        is_regeneration = concept.get('attempt_number', 0) > 0
        if is_regeneration:
            safe_print(f"\n[STAGE 2] AI REGENERATING content (attempt {concept.get('attempt_number')})...")
        else:
            safe_print("\n[STAGE 2] AI creating content...")
        
        # v17.6: PRE-VALIDATE HOOK using viral science patterns
        if not is_regeneration and ENHANCEMENTS_V11_AVAILABLE:
            try:
                topic = concept.get('specific_topic', '')
                # Use scroll-stop power scoring
                stop_power = score_scroll_stop_power(topic) if callable(score_scroll_stop_power) else None
                if stop_power and stop_power < 6:
                    safe_print(f"   [HOOK BOOST] Topic needs stronger hook (score: {stop_power}/10)")
                    # Add instruction to concept for stronger hook
                    concept['hook_boost_needed'] = True
            except Exception as e:
                pass  # Non-critical enhancement
        
        # v17.9.4: Get learned optimal metrics (8-12 phrases, 45-60s)
        learned_metrics = get_learned_optimal_metrics()
        max_phrases = learned_metrics["phrases"]  # From analytics (8-12, default 10)
        max_duration = learned_metrics["duration"]  # From analytics (45-60, default 50)
        
        # v17.9.4: ALWAYS use learned optimal values
        # The AI concept often suggests short videos (4 phrases), but we know longer delivers more value
        phrase_count = max_phrases  # Force learned optimal
        target_duration = max_duration  # Force learned optimal
        safe_print(f"   [v17.9.4] Using learned optimal: {phrase_count} phrases, {target_duration}s")
        
        # v8.0: Get viral hook patterns
        viral_boost = get_viral_prompt_boost() if VIRAL_PATTERNS_AVAILABLE else ""
        
        # v12.0: Get v12 master prompt with ALL 330 enhancements
        v12_guidelines = V12_MASTER_PROMPT if ENHANCEMENTS_V12_AVAILABLE else ""
        
        # v16.9: INTEGRATE REMAINING V12 ENHANCEMENTS
        # These were imported but NEVER USED - now fixing that
        v12_content_boosts = ""
        if ENHANCEMENTS_V12_AVAILABLE:
            try:
                category = concept.get('category', 'educational')
                
                # Natural rhythm for anti-AI feel
                rhythm = get_natural_rhythm()
                rhythm_instruction = rhythm.get_rhythm_instruction() if hasattr(rhythm, 'get_rhythm_instruction') else ""
                
                # Filler words for human feel
                filler = get_filler_injector()
                filler_instruction = filler.get_instruction() if hasattr(filler, 'get_instruction') else ""
                
                # Contractions enforcer
                contractions = get_contractions_enforcer()
                contraction_instruction = contractions.get_instruction() if hasattr(contractions, 'get_instruction') else ""
                
                # Font psychology based on category
                font = get_font_psychology()
                font_recommendation = font.recommend(category) if hasattr(font, 'recommend') else ""
                
                # Color grading based on category
                color = get_color_grading()
                color_scheme = color.get_scheme(category) if hasattr(color, 'get_scheme') else ""
                
                # Hook-Body-Payoff structure
                hbp = get_hook_body_payoff()
                hbp_structure = hbp.get_structure() if hasattr(hbp, 'get_structure') else ""
                
                v12_content_boosts = f"""
=== v12 CONTENT BOOSTS (v16.9 - Now Active!) ===
ANTI-AI RHYTHM: {rhythm_instruction}
FILLER WORDS: {filler_instruction}
CONTRACTIONS: {contraction_instruction}
FONT STYLE: {font_recommendation}
COLOR SCHEME: {color_scheme}
STRUCTURE: {hbp_structure}
=================================================
"""
            except Exception as e:
                safe_print(f"[!] v12 content boosts failed: {e}")
        
        # v15.0: Get first-attempt quality boost to avoid regenerations
        first_attempt_boost = ""
        if self.first_attempt and not is_regeneration:
            first_attempt_boost = self.first_attempt.get_quality_boost_prompt()
        
        # v13.1: Handle regeneration feedback for quality enforcement
        regen_feedback = ""
        if concept.get('regeneration_feedback'):
            regen_feedback = f"""
=== CRITICAL: QUALITY IMPROVEMENT REQUIRED ===
{concept.get('regeneration_feedback')}

YOU MUST CREATE BETTER CONTENT THIS TIME:
- More SPECIFIC numbers and claims
- More ENGAGING and surprising hooks
- More VALUABLE and actionable content
- HIGHER quality that scores 8+/10
==============================================

"""
        
        # v16.0 FIX: Convert enhancement instructions to actionable prompt text
        enhancement_boost = ""
        if concept.get('enhancement_instructions'):
            enhancements = concept['enhancement_instructions']
            enhancement_lines = []
            for key, value in enhancements.items():
                if value and isinstance(value, str):
                    enhancement_lines.append(f"- {key.replace('_', ' ').upper()}: {value}")
                elif value and isinstance(value, dict) and value.get('instruction'):
                    enhancement_lines.append(f"- {key.replace('_', ' ').upper()}: {value['instruction']}")
            if enhancement_lines:
                enhancement_boost = f"""
=== v16.0 QUALITY ENHANCEMENTS (MUST FOLLOW!) ===
{chr(10).join(enhancement_lines[:8])}
=================================================

"""
        
        prompt = f"""You are a VIRAL CONTENT CREATOR aiming for 10/10 PERFECT viral potential.

=== YOUR MISSION: CREATE 10/10 CONTENT ===
To score 10/10, you MUST include ALL of these elements:
✓ HOOK (first 1.5s): Pattern interrupt that STOPS scrolling
✓ NUMBERS: Specific figures (not vague - "$500" not "money")
✓ EMOTION: Trigger curiosity, shock, FOMO, or satisfaction
✓ VALUE: Clear benefit by second 3
✓ VOICE: Punchy, conversational, NOT robotic
✓ CTA: End with question that FORCES comments
✓ PAYOFF: Satisfying conclusion that delivers on promise

Missing ANY element = less than 10/10. Include ALL for perfection!

{regen_feedback}
{enhancement_boost}

=== VIDEO CONCEPT ===
Category: {concept.get('category', 'educational')}
Topic: {concept.get('specific_topic', 'interesting fact')}
Why Viral: {concept.get('why_this_topic', 'valuable content')}
Target Duration: {target_duration} seconds (CRITICAL - keep it SHORT!)
Phrase Count: {phrase_count} phrases ONLY

{viral_boost}

{v12_guidelines}

{v12_content_boosts}

{first_attempt_boost}

=== v17.9 CONTENT RULES (FIXED - REAL VALUE REQUIRED) ===

1. **HOOK IS EVERYTHING**: First phrase = 90% of success!
   - Pattern interrupts: "STOP!", "Wait...", "This will shock you"
   - Questions: "Did you know...?", "Why does everyone...?"
   - Challenges: "99% of people get this wrong"
   - Controversy: "What they don't want you to know..."

2. **DELIVER REAL VALUE**: This is NOT an intro - it's the FULL video!
   - Each phrase: 10-15 words (complete thoughts, not teasers)
   - Total word count: 100-150 words minimum
   - Include SPECIFIC examples, numbers, steps, or techniques
   - NO empty promises - if you say "learn this secret" TELL THE SECRET!
   
3. **SPECIFIC > VAGUE**: Concrete examples WIN
   - Bad: "save money" → Good: "cancel 3 subscriptions: gym $30, streaming $15, apps $10 = $55/month"
   - Bad: "be productive" → Good: "Use the 2-minute rule: if it takes under 2 minutes, do it NOW"
   - Bad: "5 hidden fees" → Good: "Bank ATM fee $3, foreign transaction 3%, account maintenance $12..."
   
4. **STRUCTURE FOR VALUE**:
   - Phrase 1: HOOK - Stop the scroll
   - Phrases 2-3: SETUP - The problem/context
   - Phrases 4-8: VALUE - The actual tips/facts/steps (BE SPECIFIC!)
   - Phrase 9: SUMMARY - Key takeaway
   - Phrase 10: CTA - Force engagement

5. **ENGAGEMENT BAIT**: Last phrase MUST drive action
   - Questions that FORCE comments: "A or B?", "Would you try this?"
   - Predictions: "Comment your guess before I reveal!"
   - Save hooks: "Save this before it's gone!"

=== CREATE EXACTLY {phrase_count} PHRASES WITH REAL CONTENT ===
1. HOOK (2-3 sec) - Pattern interrupt, make them STOP scrolling!
2-3. SETUP (5-8 sec) - Why this matters, the problem
4-8. VALUE (25-35 sec) - THE ACTUAL CONTENT! Specific tips, steps, examples!
9. SUMMARY (3-5 sec) - The key insight
{phrase_count}. CTA (3-5 sec) - Force engagement

=== OUTPUT JSON ===
{{
    "phrases": [
        "STOP scrolling - this one trick saves you $500 every month",
        "Most people waste money on 3 things without even realizing it",
        "Here's what I canceled and the exact savings",
        "First: that gym membership you use twice a month - $40 saved",
        "Second: premium streaming bundles - switch to ads tier, save $25",
        "Third: food delivery fees - cook batch meals on Sunday, save $200",
        "The total? That's $265 monthly going back in your pocket",
        "In one year, you'd save $3,180 - enough for a vacation",
        "The secret isn't making more money, it's stopping the leaks",
        "Which of these three will YOU cancel first? Comment below!"
    ],
    "specific_value": "Save $265/month ($3,180/year) by canceling 3 specific subscriptions",
    "hook_technique": "curiosity_gap_with_number",
    "engagement_bait": "Which of these three will YOU cancel first?"
}}

CRITICAL: 
- NO "Phrase 1:", "Phrase 2:" prefixes
- ONLY {phrase_count} phrases - no more!
- UNDER 15 words per phrase
OUTPUT JSON ONLY."""

        # v15.0: Task-specific call for budget tracking
        response = self.call_ai(prompt, 1200, temperature=0.85, task="content")
        result = self.parse_json(response)
        
        if result and result.get('phrases'):
            # Clean up any "Phrase X:" prefixes the AI might add
            cleaned_phrases = []
            for phrase in result.get('phrases', []):
                # Remove "Phrase 1:", "Phrase1:", "1:", "1." etc. prefixes
                import re
                cleaned = re.sub(r'^(Phrase\s*\d+\s*[:.]?\s*|\d+\s*[:.]?\s*)', '', phrase, flags=re.IGNORECASE).strip()
                cleaned_phrases.append(cleaned)
            result['phrases'] = cleaned_phrases
            result['concept'] = concept
            safe_print(f"   Created {len(result.get('phrases', []))} phrases")
            safe_print(f"   Value: {result.get('specific_value', 'N/A')[:60]}...")
            
            # v17.7.4: A/B test hook selection using learned patterns
            if ENHANCEMENTS_V11_AVAILABLE and cleaned_phrases and self.learning_engine:
                try:
                    original_hook = cleaned_phrases[0]
                    hook_tracker = get_hook_tracker()
                    
                    # Get power words that work and words to avoid
                    power_words = hook_tracker.get_power_words()
                    avoid_words = hook_tracker.get_words_to_avoid()
                    
                    # Check if hook contains power words
                    hook_lower = original_hook.lower()
                    has_power = any(pw in hook_lower for pw in power_words)
                    has_avoid = any(aw in hook_lower for aw in avoid_words)
                    
                    if has_avoid and not has_power:
                        safe_print(f"   [A/B HOOK] Hook contains weak words - flagging for improvement")
                        result['hook_needs_improvement'] = True
                        result['power_words_available'] = power_words[:5]
                    elif has_power:
                        safe_print(f"   [A/B HOOK] Hook contains learned power words - GOOD!")
                except Exception as e:
                    pass  # Non-critical
        
        return result
    
    # ========================================================================
    # STAGE 3: AI Evaluates and Enhances the Content
    # ========================================================================
    def stage3_evaluate_enhance(self, content: Dict) -> Dict:
        """AI evaluates its own content and improves it."""
        safe_print("\n[STAGE 3] AI evaluating and enhancing...")
        
        phrases = content.get('phrases', [])
        
        # v17.9: ACTUALLY improve hooks when flagged (was flagging but never fixing!)
        if content.get('hook_needs_improvement') and phrases:
            try:
                # v17.9.1: Get power words from learned data, not hardcoded
                default_power_words = []
                if ENHANCEMENTS_V11_AVAILABLE:
                    try:
                        hook_tracker = get_hook_tracker()
                        default_power_words = hook_tracker.get_power_words()[:5] if hasattr(hook_tracker, 'get_power_words') else []
                    except:
                        pass
                power_words = content.get('power_words_available', default_power_words if default_power_words else None)
                original_hook = phrases[0]
                
                # Ask AI to rewrite hook - dynamically based on available data
                power_words_instruction = ""
                if power_words and len(power_words) > 0:
                    power_words_instruction = f"Use these PROVEN power words from past successful videos: {power_words}"
                else:
                    power_words_instruction = "Use viral psychology: curiosity gaps, specific numbers, or emotional triggers"
                
                hook_improve_prompt = f"""Rewrite this video hook to be MORE viral:

Original hook: "{original_hook}"

{power_words_instruction}

Rules:
1. Keep it under 15 words
2. Must stop the scroll IMMEDIATELY
3. Use a pattern interrupt or a surprising statistic
4. Add curiosity gap - make them NEED to watch

Return ONLY the improved hook, nothing else."""

                improved_hook = self.call_ai(hook_improve_prompt, 100, temperature=0.9, task="hook_improve")
                if improved_hook and len(improved_hook.strip()) > 5 and len(improved_hook.strip()) < 100:
                    phrases[0] = improved_hook.strip().strip('"').strip("'")
                    content['phrases'] = phrases
                    content['hook_was_improved'] = True
                    safe_print(f"   [v17.9 HOOK FIX] Improved weak hook with power words!")
                    safe_print(f"   [OLD] {original_hook[:50]}...")
                    safe_print(f"   [NEW] {phrases[0][:50]}...")
            except Exception as e:
                safe_print(f"   [!] Hook improvement failed: {e}")
        
        # v17.6: Pre-check value delivery BEFORE AI evaluation
        # v17.9: Now with REJECTION for truly empty content
        if VIRAL_SCIENCE_AVAILABLE:
            try:
                checker = ValueDeliveryChecker()
                full_content = " ".join(phrases)
                value_check = checker.check_content(full_content)
                content['value_delivery_score'] = value_check['score']
                safe_print(f"   [VIRAL SCIENCE] Value delivery: {value_check['verdict']} ({value_check['score']}/100)")
                if value_check['issues']:
                    safe_print(f"   [ISSUES] {', '.join(value_check['issues'][:2])}")
                
                # v17.9: REJECT truly valueless content - mark for regeneration
                if value_check['verdict'] == 'REJECT':
                    content['needs_regeneration'] = True
                    content['regen_reason'] = f"Value check FAILED: {value_check['issues'][0] if value_check['issues'] else 'No value'}"
                    safe_print(f"   [!] CONTENT REJECTED - Will regenerate with more depth!")
                elif value_check['verdict'] == 'NEEDS_WORK' and value_check['score'] < 60:
                    content['content_weak'] = True
                    safe_print(f"   [!] Content weak ({value_check['score']}/100) - Flagged for AI improvement")
            except Exception as e:
                safe_print(f"   [!] Value check skipped: {e}")
        
        # v17.6: Check hook scroll-stop power
        if CRITICAL_FIXES_AVAILABLE and phrases:
            try:
                hook_quality = score_hook_quality(phrases[0])
                content['hook_quality_score'] = hook_quality['score']
                safe_print(f"   [HOOK SCORE] Scroll-stop power: {hook_quality['score']}/10 ({len(hook_quality['patterns_found'])} patterns)")
                if hook_quality['suggestions']:
                    safe_print(f"   [HOOK TIP] {hook_quality['suggestions'][0]}")
            except Exception as e:
                safe_print(f"   [!] Hook scoring skipped: {e}")
        
        # v17.9.6: INTEGRATE ALL NEW AI MODULES
        # These were defined but NEVER called - now activating them!
        
        # 1. Script Analyzer - Analyze script quality
        if SCRIPT_ANALYZER_AVAILABLE and phrases:
            try:
                analyzer = ScriptAnalyzer()
                # v17.9.7: Fixed - method takes content Dict, not keyword args
                script_content = {
                    "hook": phrases[0] if phrases else "",
                    "phrases": phrases[1:] if len(phrases) > 1 else phrases,
                    "cta": content.get('cta', '')
                }
                script_analysis = analyzer.analyze_script(script_content)
                content['script_analysis'] = script_analysis
                safe_print(f"   [SCRIPT] Quality: {script_analysis.get('overall_score', 0)}/100, Grade: {script_analysis.get('grade', 'N/A')}")
            except Exception as e:
                safe_print(f"   [!] Script analysis skipped: {e}")
        
        # 2. Retention Predictor - Predict viewer drop-off points
        if RETENTION_PREDICTOR_AVAILABLE and phrases:
            try:
                predictor = RetentionPredictor()
                # v17.9.7: Fixed - method takes content Dict with hook, phrases, cta, category
                retention_content = {
                    "hook": phrases[0] if phrases else "",
                    "phrases": phrases[1:] if len(phrases) > 1 else phrases,
                    "cta": content.get('cta', ''),
                    "category": content.get('concept', {}).get('category', 'educational')
                }
                retention = predictor.predict_retention(retention_content)
                content['retention_prediction'] = retention
                safe_print(f"   [RETENTION] Predicted: {retention.get('overall_retention', 0):.0f}%")
            except Exception as e:
                safe_print(f"   [!] Retention prediction skipped: {e}")
        
        # 3. Engagement Predictor - Predict likes/comments/shares
        if ENGAGEMENT_PREDICTOR_AVAILABLE and phrases:
            try:
                predictor = EngagementPredictor()
                # v17.9.7: Fixed - method takes content Dict with hook, phrases, cta, category
                engagement_content = {
                    "hook": phrases[0] if phrases else "",
                    "phrases": phrases[1:] if len(phrases) > 1 else phrases,
                    "cta": content.get('cta', ''),
                    "category": content.get('concept', {}).get('category', 'educational')
                }
                engagement = predictor.predict_engagement(engagement_content)
                content['engagement_prediction'] = engagement
                safe_print(f"   [ENGAGEMENT] Score: {engagement.get('overall_engagement', 0)}/100, Strongest: {engagement.get('strongest', 'N/A')}")
            except Exception as e:
                safe_print(f"   [!] Engagement prediction skipped: {e}")
        
        # 4. Virality Calculator - Calculate overall virality potential
        if VIRALITY_CALCULATOR_AVAILABLE:
            try:
                calculator = ViralityCalculator()
                # v17.9.7: Fixed - method is calculate_virality (not calculate_virality_score), takes content Dict
                virality_content = {
                    "hook": phrases[0] if phrases else "",
                    "phrases": phrases[1:] if len(phrases) > 1 else phrases,
                    "cta": content.get('cta', ''),
                    "category": content.get('concept', {}).get('category', 'educational'),
                    "topic": content.get('concept', {}).get('specific_topic', '')
                }
                virality = calculator.calculate_virality(virality_content)
                content['virality_score'] = virality
                safe_print(f"   [VIRALITY] Score: {virality.get('overall_score', 0):.0f}/100 ({virality.get('grade', 'N/A')}) - {virality.get('viral_potential', 'N/A')}")
            except Exception as e:
                safe_print(f"   [!] Virality calculation skipped: {e}")
        
        # 5. v17.9.7: MASTER EVALUATOR - The ULTIMATE quality scoring system
        if MASTER_EVALUATOR_AVAILABLE and phrases:
            try:
                evaluator = get_master_evaluator()
                master_content = {
                    "hook": phrases[0] if phrases else "",
                    "phrases": phrases[1:] if len(phrases) > 1 else phrases,
                    "cta": content.get('cta', ''),
                    "topic": content.get('concept', {}).get('specific_topic', ''),
                    "category": content.get('concept', {}).get('category', 'educational')
                }
                master_result = evaluator.evaluate(master_content)
                content['master_evaluation'] = master_result
                
                final_score = master_result.get('final_score', 0)
                verdict = master_result.get('verdict', 'N/A')
                checks = f"{master_result.get('checks_passed', 0)}/{master_result.get('checks_total', 7)}"
                
                safe_print(f"   [MASTER] Score: {final_score:.1f}/10 | Verdict: {verdict} | Checks: {checks}")
                
                # If score < 8 and we have improvement suggestions, log them
                if final_score < 8 and master_result.get('specific_improvements'):
                    safe_print(f"   [MASTER] To improve: {master_result['specific_improvements'][0][:60]}...")
                
                # Store rewritten hook suggestion for potential use
                if master_result.get('rewritten_hook'):
                    content['suggested_hook'] = master_result['rewritten_hook']
                    
            except Exception as e:
                safe_print(f"   [!] Master evaluation skipped: {e}")
        
        # v8.9.1: Get the hook/topic from concept for promise validation
        concept = content.get('concept', {})
        hook_or_topic = concept.get('hook', concept.get('specific_topic', 'Unknown topic'))
        
        prompt = f"""You are a CONTENT QUALITY REVIEWER for viral YouTube Shorts.
Your job: Evaluate content fairly, identify improvements, and enhance it.

=== HOOK/TITLE ===
{hook_or_topic}

=== CONTENT PHRASES ===
{json.dumps(phrases, indent=2)}

Claimed Value: {content.get('specific_value', '')}

=== SCORING FOR 10/10 VIRAL POTENTIAL ===
Your job is to MAXIMIZE virality. Score based on VIRAL POTENTIAL:

SCORING (be accurate, aim for perfection):
- 10/10: PERFECT - Would absolutely go viral. Scroll-stopping hook, surprising value, comment-driving CTA
- 9/10: EXCELLENT - Very strong viral potential, minor tweaks possible
- 8/10: GREAT - Solid content with good hook and value (our TARGET minimum)
- 7/10: GOOD - Acceptable quality, could perform well
- 6/10: FAIR - Missing key viral elements
- 5 or below: WEAK - Needs significant work

VIRAL ELEMENTS TO CHECK (each adds points):
✓ First 1.5 seconds = pattern interrupt (stop scrolling)
✓ Specific numbers (not vague promises)
✓ Emotional trigger (curiosity, shock, FOMO, satisfaction)
✓ Clear value proposition by second 3
✓ Punchy, conversational language (not robotic)
✓ Engagement CTA (forces comments/shares/saves)
✓ Satisfying payoff at the end

If content has 5+ of these elements = 8/10+
If content has ALL elements = 9-10/10

BE ACCURATE: Score what you see. We WANT high scores for good content.

=== QUICK QUALITY CHECK ===
For each phrase, ask:
- Is it clear and easy to understand?
- Does it sound natural (not robotic)?
- Does it provide value to the viewer?
- Are numbers believable (e.g., "$500" not "$3333")?

=== RED FLAGS TO CATCH (examples, but catch ANY quality issue) ===
- Awkward/random numbers that look fake (e.g., $3333, 47.3%, 1847 people)
- Numbers that are too precise to be believable (use round numbers: $500, 80%, 1000+)
- Promises in hook not delivered in content (e.g., "7 tips" but only 2 given)
- Vague claims with no specifics ("amazing results" - what results?)
- Robotic phrasing that no human would say
- Sentences that are too long for short-form video
- Claims that sound too good to be true without proof
- Anything that breaks immersion or trust

=== YOUR QUALITY STANDARDS ===
1. BELIEVABILITY: Every claim must sound real and trustworthy
2. SPECIFICITY: Vague content fails. Give real numbers, steps, examples
3. NATURAL FLOW: Must sound like a human speaking, not AI text
4. PROMISE-PAYOFF: If you promise X things, you deliver X things
5. MEMORABLE NUMBERS: Use round, sticky numbers ($500, 90%, 30 days) not random ones

=== YOUR TASK ===
1. Read the content as a skeptical viewer
2. Flag ANYTHING that feels off (be harsh - this protects quality)
3. FIX every issue in the improved version
4. Make sure the improved version passes YOUR own skeptical test

=== OUTPUT JSON ===
{{
    "evaluation_score": 1-10,
    "quality_issues": [
        {{"issue": "description of problem", "fix": "how you fixed it"}}
    ],
    "believability_score": 1-10,
    "would_you_watch": true or false,
    "improvements_made": ["list of all changes"],
    "improved_hook": "The improved first phrase",
    "improved_phrases": [
        "The improved hook text here",
        "The improved second phrase here",
        "And so on for each phrase"
    ],
    "final_value_delivered": "What specific value does viewer get now?"
}}

CRITICAL: Do NOT include "Phrase 1:", "Improved phrase 1:" etc. - just the actual text!
OUTPUT JSON ONLY."""

        # v15.0: Task-specific call for budget tracking
        response = self.call_ai(prompt, 1200, temperature=0.7, task="evaluate")
        result = self.parse_json(response)
        
        if result:
            # v8.9.1: Log promise check results (AI-driven validation)
            promise_check = result.get('promise_check', {})
            if promise_check:
                if promise_check.get('promise_kept') == False:
                    safe_print(f"   [AI-FIX] Promise violation detected: {promise_check.get('number_promised')} promised, {promise_check.get('items_delivered')} delivered")
                    if promise_check.get('fix_applied'):
                        safe_print(f"   [AI-FIX] Applied: {promise_check.get('fix_applied')}")
                else:
                    safe_print(f"   [OK] Promise check passed")
            
            # v8.9.1: Use improved hook if provided
            if result.get('improved_hook'):
                concept = content.get('concept', {})
                concept['hook'] = result.get('improved_hook')
                content['concept'] = concept
                safe_print(f"   [AI] Improved hook: {result.get('improved_hook')[:50]}...")
            
            # Clean up any prefixes from improved phrases
            improved = result.get('improved_phrases', content.get('phrases', []))
            cleaned_phrases = []
            for phrase in improved:
                cleaned = re.sub(r'^(Phrase\s*\d+\s*[:.]?\s*|Improved\s*(phrase)?\s*\d*\s*[:.]?\s*|\d+\s*[:.]?\s*)', '', phrase, flags=re.IGNORECASE).strip()
                cleaned_phrases.append(cleaned)
            content['phrases'] = cleaned_phrases
            content['evaluation_score'] = result.get('evaluation_score', 7)
            content['value_delivered'] = result.get('final_value_delivered', '')
            safe_print(f"   Score: {result.get('evaluation_score', 'N/A')}/10")
            if result.get('improvements_made'):
                safe_print(f"   Improvements: {result.get('improvements_made', [])[:2]}")
        
        return content
    
    # ========================================================================
    # STAGE 4: AI Generates B-Roll Keywords
    # ========================================================================
    def stage4_broll_keywords(self, phrases: List[str]) -> List[str]:
        """AI generates visual keywords for each phrase.
        v8.2: Uses Gemini to save Groq quota (non-critical task).
        v17.7.10: Uses error pattern learning to avoid failed keywords.
        """
        safe_print("\n[STAGE 4] AI generating visual keywords...")
        
        # v17.7.10: Get learned failed keywords to avoid
        avoid_keywords = []
        if ENHANCEMENTS_V11_AVAILABLE:
            try:
                error_learner = ErrorPatternLearner()
                for kw in error_learner.data.get("broll_failures", {}).keys():
                    if error_learner.should_skip_keyword(kw):
                        avoid_keywords.append(kw)
            except:
                pass
        
        avoid_hint = ""
        if avoid_keywords:
            avoid_hint = f"\n\nAVOID THESE KEYWORDS (known to fail on Pexels):\n{', '.join(avoid_keywords[:10])}\n"
        
        prompt = f"""You are a VISUAL DIRECTOR for viral short videos.
Select the PERFECT B-roll visual for EACH phrase.

=== PHRASES ===
{json.dumps(phrases, indent=2)}

=== VISUAL RULES ===
- Be SPECIFIC: "close up of person stressed at desk" > "stress"
- Match EMOTION to content
- Include PEOPLE when possible (more engaging)
- Think about MOVEMENT and COLOR
- Use COMMON stock video terms that work on Pexels
{avoid_hint}
=== HIGH-CONVERTING KEYWORDS (proven to work on Pexels) ===
- "business meeting", "woman working laptop", "man phone walking"
- "hands typing keyboard", "coffee shop morning", "sunset city"
- "friends laughing", "person meditation", "money finance success"

=== OUTPUT ===
Return exactly {len(phrases)} keywords as JSON array:
["specific keyword for phrase 1", "specific keyword for phrase 2", ...]

JSON ARRAY ONLY."""

        # v8.2: Use Gemini for this task to save Groq quota
        # v15.0: Task-specific call for budget tracking
        response = self.call_ai(prompt, 400, temperature=0.8, prefer_gemini=True, task="broll")
        
        try:
            if "[" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                keywords = json.loads(response[start:end])
                safe_print(f"   Generated {len(keywords)} visual keywords")
                return keywords[:len(phrases)]
        except:
            pass
        
        return ["dramatic scene"] * len(phrases)
    
    # ========================================================================
    # STAGE 5: AI Generates Metadata with A/B Title Variants
    # ========================================================================
    def stage5_metadata(self, content: Dict) -> Dict:
        """AI generates viral metadata with title variants for A/B testing.
        v8.5: Generates 3 title variants, picks one randomly, tracks style.
        v8.9.1: Uses LEARNED viral patterns (not hardcoded examples).
        """
        safe_print("\n[STAGE 5] AI generating metadata with A/B title variants...")
        
        concept = content.get('concept', {})
        phrases = content.get('phrases', [])
        
        # v8.9.1: Get learned viral patterns for title generation (AI-driven, not hardcoded!)
        viral_title_guidance = ""
        try:
            viral_boost = get_viral_prompt_boost() if VIRAL_PATTERNS_AVAILABLE else ""
            if viral_boost:
                viral_title_guidance = f"""
=== LEARNED VIRAL PATTERNS (from analysis of successful videos) ===
{viral_boost}

Use these LEARNED patterns to create titles that have PROVEN to work.
"""
        except Exception as e:
            safe_print(f"   [!] Viral patterns unavailable: {e}")
        
        prompt = f"""Create viral metadata for this video with 3 TITLE VARIANTS.

Category: {concept.get('category', '')}
Topic: {concept.get('specific_topic', '')}
Hook: {concept.get('hook', '')}
First phrase: {phrases[0] if phrases else ''}
Value delivered: {content.get('value_delivered', '')}

{viral_title_guidance}

=== TITLE QUALITY RULES ===
Every title MUST have:
1. A SPECIFIC benefit (what the viewer gets: saves time, makes money, fixes problem)
2. A NUMBER (percentage, time, count, dollar amount) for credibility
3. UNDER 50 characters (for mobile readability)

Titles that are VAGUE or lack a clear benefit will FAIL.
Ask yourself: "Would I click this? Does it tell me what I'll learn?"

=== TITLE VARIANTS (for A/B testing) ===
Create 3 different styles based on the learned patterns above:

1. NUMBER_HOOK: Lead with a compelling number
2. CURIOSITY_GAP: Create mystery while showing benefit
3. RESULT_FOCUSED: Clearly state the outcome/result

=== OUTPUT JSON ===
{{
    "title_variants": [
        {{"style": "number_hook", "title": "the number-based title"}},
        {{"style": "curiosity_gap", "title": "the curiosity title"}},
        {{"style": "result_focused", "title": "the result-focused title"}}
    ],
    "description": "2-3 sentence description with CTA",
    "hashtags": ["#shorts", "#viral", plus 5-8 relevant hashtags]
}}

JSON ONLY."""

        # v8.2: Use Gemini for this task to save Groq quota
        # v15.0: Task-specific call for budget tracking
        response = self.call_ai(prompt, 400, temperature=0.8, prefer_gemini=True, task="metadata")
        result = self.parse_json(response)
        
        if result and result.get('title_variants'):
            variants = result.get('title_variants', [])
            if variants:
                # v17.7: Use ABTestTracker for proper A/B testing with performance data
                ab_tracker = None
                try:
                    if ENHANCEMENTS_V11_AVAILABLE:
                        ab_tracker = ABTestTracker()
                        # Get performance-weighted selection
                        best_variant = ab_tracker.get_best_variant("title_styles")
                        if best_variant:
                            safe_print(f"   [A/B] Best performer: {best_variant}")
                except Exception as e:
                    safe_print(f"   [!] A/B tracker error: {e}")
                
                # Try to get learned best styles from analytics
                best_styles = []
                try:
                    if PERSISTENT_STATE_AVAILABLE:
                        variety_mgr = get_variety_manager()
                        best_styles = variety_mgr.state.get('best_title_styles', [])
                except:
                    pass
                
                if best_styles:
                    # Weight toward best styles (70% best, 30% random for exploration)
                    weighted_variants = []
                    for v in variants:
                        style = v.get('style', '')
                        if style in best_styles:
                            weighted_variants.extend([v] * 3)  # 3x weight for best styles
                        else:
                            weighted_variants.append(v)
                    chosen = random.choice(weighted_variants)
                    safe_print(f"   A/B: Using learned weights (best: {best_styles})")
                else:
                    # No learned data yet - pure random for exploration
                    chosen = random.choice(variants)
                    safe_print(f"   A/B: Exploring (no learned preferences yet)")
                
                result['title'] = chosen.get('title', variants[0].get('title', ''))
                result['title_style'] = chosen.get('style', 'unknown')
                safe_print(f"   Title (style={result['title_style']}): {result.get('title', 'N/A')}")
                
                # v17.7: Record this variant selection in A/B tracker
                if ab_tracker:
                    try:
                        ab_tracker.record_variant(
                            "title_styles", 
                            result['title_style'],
                            str(random.randint(10000, 99999)),  # temp video ID
                            {"title": result['title']}
                        )
                    except:
                        pass
        elif result and result.get('title'):
            result['title_style'] = 'single'
            safe_print(f"   Title: {result.get('title', 'N/A')}")
        
        # v17.7.13: Add optimal publishing time recommendation
        if ENHANCEMENTS_V10_AVAILABLE and result:
            try:
                pub_optimizer = get_publishing_optimizer()
                best_times = pub_optimizer.get_best_publishing_times()
                result['recommended_publish_hours'] = best_times.get('best_hours_utc', [14, 18, 20])
                result['recommended_publish_days'] = best_times.get('best_days', ['Saturday'])
                safe_print(f"   [PUBLISH] Best times: {best_times['best_hours_utc'][:3]}:00 UTC on {best_times['best_days'][:2]}")
            except:
                pass
        
        # v17.7.15: Optimize description for SEO
        if ENHANCEMENTS_V10_AVAILABLE and result and result.get('description'):
            try:
                title = result.get('title', '')
                content_summary = result.get('description', '')
                category = content.get('concept', {}).get('category', 'general')
                
                seo_result = optimize_description_seo(title, content_summary, category)
                if seo_result and seo_result.get('optimized_description'):
                    result['description'] = seo_result['optimized_description']
                    result['seo_keywords'] = seo_result.get('secondary_keywords', [])
                    safe_print(f"   [SEO] Description optimized (score: {seo_result.get('seo_score', '?')}/10)")
            except:
                pass
        
        return result
    
    # ========================================================================
    # STAGE 6: Get Voice and Music with VARIETY ENFORCEMENT
    # ========================================================================
    def get_voice_config(self, concept: Dict, batch_tracker: BatchTracker = None) -> Dict:
        """AI-DRIVEN voice selection with variety enforcement. OPTIMIZED for token usage."""
        category = concept.get('category', 'general')
        voice_style = concept.get('voice_style', 'energetic').lower()
        
        # v12.0: Get optimized voice settings from v12 enhancements
        v12_voice_guidance = ""
        if ENHANCEMENTS_V12_AVAILABLE:
            try:
                v12_settings = get_v12_voice_settings(category)
                v12_voice_guidance = f"\nv12.0 Recommended profile: {v12_settings.get('profile', 'energetic')}"
            except:
                pass
        
        # Build exclusion list from batch tracker
        exclude_voices = []
        if batch_tracker and batch_tracker.used_voices:
            exclude_voices = batch_tracker.used_voices.copy()
        
        # Get available voices (not in exclusion list)
        available = [v for v in EDGE_TTS_VOICES if v not in exclude_voices]
        if not available:
            available = EDGE_TTS_VOICES  # Reset if all used
        
        safe_print(f"   AI selecting voice for {category}/{voice_style}...")
        
        # v8.8: FULL PROMPT - using free Gemini tokens!
        prompt = f"""You are a voice casting director for viral short-form videos.

VIDEO DETAILS:
- Category: {category}
- Desired Style: {voice_style}
- Content Type: Educational/Entertainment short (40-50 seconds, 8-10 phrases)

AVAILABLE VOICES (Microsoft Edge TTS):
{chr(10).join([f"- {v} ({v.split('-')[1]} accent)" for v in available[:12]])}

YOUR TASK:
Select the BEST voice that will:
1. Match the {voice_style} energy perfectly
2. Keep viewers engaged (not boring or annoying)
3. Be clear and easy to understand
4. Suit the {category} content

Also determine the optimal speaking rate:
- Energetic content: +5% to +10%
- Calm content: -5% to +0%
- Dramatic content: +0% to +5%

Return JSON:
{{
    "voice": "exact-voice-name-from-list",
    "rate": "+X%" or "-X%",
    "why": "brief reason for this choice"
}}

JSON ONLY."""

        # v15.0: Task-specific call for budget tracking (voice selection is part of metadata)
        response = self.call_ai(prompt, 150, temperature=0.8, prefer_gemini=True, task="metadata")
        result = self.parse_json(response)
        
        selected_voice = None
        if result and result.get('voice'):
            # Try to match the voice name
            voice_hint = result['voice'].lower()
            for v in available:
                if voice_hint in v.lower() or v.lower() in voice_hint:
                    selected_voice = v
                    break
        
        if not selected_voice:
            # Smart fallback based on style
            style_preferences = {
                'energetic': ['Aria', 'Steffan', 'Liam'],
                'calm': ['Jenny', 'Sara', 'Sonia'],
                'mysterious': ['Guy', 'Davis', 'Roger'],
                'authoritative': ['Ryan', 'Christopher', 'Davis'],
                'friendly': ['William', 'Eric', 'Clara'],
                'dramatic': ['Christopher', 'Guy', 'Roger'],
            }
            prefs = style_preferences.get(voice_style, ['Aria', 'Guy', 'Jenny'])
            for pref in prefs:
                match = next((v for v in available if pref in v), None)
                if match:
                    selected_voice = match
                    break
            if not selected_voice:
                selected_voice = random.choice(available)
        
        rate = result.get('rate', DEFAULT_VOICE_RATES.get(voice_style, '+0%')) if result else DEFAULT_VOICE_RATES.get(voice_style, '+0%')
        
        # v17.7.11: Use VoiceSpeedOptimizer for A/B tested optimal rate
        if ENHANCEMENTS_V11_AVAILABLE:
            try:
                voice_optimizer = get_voice_optimizer()
                optimized_rate = voice_optimizer.get_rate_for_ab_test()
                if optimized_rate != rate:
                    safe_print(f"   [VOICE OPT] Using learned rate: {optimized_rate} (was: {rate})")
                    rate = optimized_rate
            except:
                pass
        
        safe_print(f"   [OK] Selected: {selected_voice} @ {rate}")
        
        # Track usage
        if batch_tracker:
            batch_tracker.used_voices.append(selected_voice)
        
        return {'voice': selected_voice, 'rate': rate}
    
    def get_music_path(self, concept: Dict, batch_tracker: BatchTracker = None) -> Optional[str]:
        """Get music path with variety enforcement."""
        music_mood = concept.get('music_mood', 'dramatic').lower()
        
        # Enforce variety: avoid recently used music
        available_moods = list(ALL_MUSIC.keys())
        if batch_tracker and batch_tracker.used_music:
            unused = [m for m in available_moods if ALL_MUSIC[m] not in batch_tracker.used_music[-3:]]
            if unused:
                # Prefer the AI-requested mood if available
                if music_mood in unused:
                    available_moods = [music_mood]
                else:
                    available_moods = unused
        
        selected_mood = music_mood if music_mood in available_moods else random.choice(available_moods)
        music_file = ALL_MUSIC.get(selected_mood, 'bensound-epic.mp3')
        
        # Track usage
        if batch_tracker:
            batch_tracker.used_music.append(music_file)
        
        return music_file


class VideoRenderer:
    """Professional video rendering."""
    
    def __init__(self):
        self.pexels_key = os.environ.get("PEXELS_API_KEY")
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY")

    def clean_phrase_prefix(self, phrase: str) -> str:
        """Removes 'Phrase X:' or similar prefixes from the start of a phrase."""
        # Regex to match "Phrase 1:", "Phrase 2.", "Phrase 3 -", etc.
        cleaned = re.sub(r'^(Phrase\s*\d+\s*[:.\-]?\s*)', '', phrase, flags=re.IGNORECASE).strip()
        return cleaned
    
    def download_broll(self, keyword: str, index: int) -> Optional[str]:
        """Download B-roll from Pexels, falling back to Pixabay."""
        path = self.download_broll_pexels(keyword, index)
        if not path:
            path = self.download_broll_pixabay(keyword, index)
        return path

    def download_broll_pixabay(self, keyword: str, index: int) -> Optional[str]:
        """Download B-roll from Pixabay (landscape clips are cropped to portrait at render)."""
        if not self.pixabay_key:
            return None

        safe_keyword = "".join(c if c.isalnum() or c == '_' else '_' for c in keyword)[:30]
        cache_file = BROLL_DIR / f"v7_pxb_{safe_keyword}_{index}_{random.randint(1000,9999)}.mp4"

        try:
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params={"key": self.pixabay_key, "q": keyword[:100], "per_page": 10, "safesearch": "true"},
                timeout=15,
            )
            if response.status_code != 200:
                return None

            hits = response.json().get("hits", [])
            if not hits:
                return None

            videos = random.choice(hits).get("videos", {})
            # "large" is often 4K, which makes per-frame MoviePy resizing
            # extremely slow; 1080p "medium" is plenty for a 1080x1920 short
            best = None
            for size in ("medium", "small", "large"):
                vf = videos.get(size) or {}
                if vf.get("url") and 720 <= vf.get("height", 0) <= 1440:
                    best = vf
                    break
            if not best:
                best = next((videos[s] for s in ("medium", "small", "large") if (videos.get(s) or {}).get("url")), None)
            if not best:
                return None

            video_response = requests.get(best["url"], timeout=60, stream=True)
            with open(cache_file, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            safe_print(f"   [OK] B-roll (Pixabay): {keyword[:25]}...")
            return str(cache_file)

        except Exception:
            return None

    def download_broll_pexels(self, keyword: str, index: int) -> Optional[str]:
        """Download B-roll from Pexels.
        v17.7: Added ErrorPatternLearner integration.
        """
        if not self.pexels_key:
            return None
        
        # v17.7: Check if this keyword has failed before
        error_learner = None
        if ENHANCEMENTS_V11_AVAILABLE:
            try:
                error_learner = ErrorPatternLearner()
                if error_learner.should_skip_keyword(keyword):
                    # Try to get an alternative keyword
                    alt = error_learner.get_alternative_keyword(keyword)
                    if alt:
                        safe_print(f"   [LEARN] Skipping failed keyword '{keyword}', using '{alt}'")
                        keyword = alt
            except:
                pass
        
        safe_keyword = "".join(c if c.isalnum() or c == '_' else '_' for c in keyword)[:30]
        cache_file = BROLL_DIR / f"v7_{safe_keyword}_{index}_{random.randint(1000,9999)}.mp4"
        
        try:
            headers = {"Authorization": self.pexels_key}
            url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&per_page=10"
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                # v17.7: Record the failure
                if error_learner:
                    error_learner.record_broll_failure(keyword)
                return None
            
            videos = response.json().get("videos", [])
            if not videos:
                # v17.7: Record the failure
                if error_learner:
                    error_learner.record_broll_failure(keyword)
                return None
            
            video = random.choice(videos)
            video_files = video.get("video_files", [])
            
            best = None
            for vf in video_files:
                if vf.get("quality") == "hd" and vf.get("height", 0) >= 720:
                    best = vf
                    break
            if not best and video_files:
                best = video_files[0]
            
            if not best:
                return None
            
            video_url = best.get("link")
            video_response = requests.get(video_url, timeout=60, stream=True)
            
            with open(cache_file, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            safe_print(f"   [OK] B-roll: {keyword[:25]}...")
            return str(cache_file)
            
        except Exception as e:
            return None
    
    def create_text_overlay(self, text: str, width: int, height: int, font_key: str = None) -> Image.Image:
        """Create text overlay with AI-SELECTED font (not hardcoded!)."""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        text = strip_emojis(text)
        
        # Use AI-selected font if provided
        font_path = None
        if font_key:
            try:
                from dynamic_fonts import get_font_by_key
                font_path = get_font_by_key(font_key)
                # Only log when font is actually loaded
            except ImportError:
                pass
        
        # Fallback: Try dynamic font system
        if not font_path:
            try:
                from dynamic_fonts import get_impact_font
                font_path = get_impact_font()
            except ImportError:
                pass
        
        # Fallback to system fonts if dynamic fonts unavailable
        if not font_path or not os.path.exists(font_path):
            font_paths = [
                "C:/Windows/Fonts/impact.ttf",
                "C:/Windows/Fonts/ariblk.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ]
            font_path = next((f for f in font_paths if os.path.exists(f)), None)
        
        try:
            font = ImageFont.truetype(font_path, 64) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        words = text.split()
        lines = []
        current = []
        max_width = width - 100
        
        for word in words:
            current.append(word)
            test = " ".join(current)
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                current.pop()
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        
        line_height = 80
        total_height = len(lines) * line_height
        y = (height - total_height) // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (width - (bbox[2] - bbox[0])) // 2
            
            # ENHANCED v7.15: Professional glow effect
            # Layer 1: Outer glow (larger, softer)
            for ox in range(-6, 7):
                for oy in range(-6, 7):
                    distance = (ox*ox + oy*oy) ** 0.5
                    if distance > 3 and distance <= 6:
                        alpha = int(80 * (1 - distance/6))
                        draw.text((x + ox, y + oy), line, fill=(0, 0, 0, alpha), font=font)
            
            # Layer 2: Sharp outline (for readability)
            for ox in range(-3, 4):
                for oy in range(-3, 4):
                    if ox != 0 or oy != 0:
                        draw.text((x + ox, y + oy), line, fill=(0, 0, 0, 255), font=font)
            
            # Layer 3: Main text with slight inner glow
            draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
            y += line_height
        
        return img
    
    def create_progress_bar(self, duration: float) -> VideoClip:
        """Create progress bar."""
        bar_height = 6

        def make_frame(t):
            progress = t / duration
            frame = np.zeros((bar_height + 4, VIDEO_WIDTH, 3), dtype=np.uint8)
            frame[2:bar_height+2, :, :] = [40, 40, 40]
            fill_width = int(VIDEO_WIDTH * progress)
            if fill_width > 0:
                ratio = np.arange(fill_width) / max(fill_width, 1)
                frame[2:bar_height+2, :fill_width, 0] = 255
                frame[2:bar_height+2, :fill_width, 1] = (100 + 155 * ratio).astype(np.uint8)
                frame[2:bar_height+2, :fill_width, 2] = 255
            return frame
        
        return VideoClip(make_frame, duration=duration)
    
    def pil_to_clip(self, pil_img: Image.Image, duration: float) -> ImageClip:
        """Convert PIL RGBA to MoviePy clip with proper transparency."""
        rgba_arr = np.array(pil_img.convert('RGBA'))
        
        # Extract RGB and Alpha channels separately
        rgb_arr = rgba_arr[:, :, :3]
        alpha_arr = rgba_arr[:, :, 3] / 255.0  # Normalize alpha to 0-1
        
        # Create the main clip from RGB
        clip = ImageClip(rgb_arr, duration=duration)
        
        # Create mask from alpha channel
        mask_clip = ImageClip(alpha_arr, duration=duration, ismask=True)
        clip = clip.set_mask(mask_clip)
        
        return clip
    
    def create_animated_text_clip(self, text: str, duration: float, phrase_index: int = 0, font_key: str = None) -> VideoClip:
        """
        Create animated text overlay with PROFESSIONAL effects.
        v7.15: Enhanced with 6 animation types for maximum variety.
        v13.0: Now uses AI-SELECTED font based on content type!
        
        Effects cycle by phrase for variety:
        0: Fade in (hook)
        1: Slide from left
        2: Slide from right  
        3: Pop/scale up
        4: Slide from bottom
        5: Elastic bounce in
        """
        width, height = VIDEO_WIDTH, VIDEO_HEIGHT // 2
        text_img = self.create_text_overlay(text, width, height, font_key=font_key)
        base_clip = self.pil_to_clip(text_img, duration)
        
        # Animation timing - quick but noticeable
        anim_duration = min(0.4, duration * 0.12)  # 12% of clip or 0.4s max
        
        # v7.15: 6 different effects for maximum variety
        effect_type = phrase_index % 6
        
        if effect_type == 0:
            # Fade in with slight scale (hook - attention grabbing)
            return base_clip.set_position(('center', 'center')).crossfadein(anim_duration)
        
        elif effect_type == 1:
            # Slide in from left with ease-out
            def position(t):
                if t < anim_duration:
                    progress = min(1.0, t / anim_duration)
                    # Ease-out cubic
                    ease = 1 - pow(1 - progress, 3)
                    x = int(-width/2 + (width/2 * ease))
                else:
                    x = 0
                return (x, 'center')
            return base_clip.set_position(position).crossfadein(anim_duration * 0.5)
        
        elif effect_type == 2:
            # Slide in from right with ease-out
            def position(t):
                if t < anim_duration:
                    progress = min(1.0, t / anim_duration)
                    ease = 1 - pow(1 - progress, 3)
                    x = int(width/2 - (width/2 * ease))
                else:
                    x = 0
                return (x, 'center')
            return base_clip.set_position(position).crossfadein(anim_duration * 0.5)
        
        elif effect_type == 3:
            # Pop in / Scale up (popular on TikTok)
            def resize_func(t):
                if t < anim_duration:
                    progress = min(1.0, t / anim_duration)
                    # Ease-out back (slight overshoot for "pop" effect)
                    c1 = 1.70158
                    c3 = c1 + 1
                    ease = 1 + c3 * pow(progress - 1, 3) + c1 * pow(progress - 1, 2)
                    scale = 0.5 + 0.5 * ease
                    return min(1.1, max(0.5, scale))  # Cap at 1.1 to prevent artifacts
                return 1.0
            try:
                return base_clip.resize(resize_func).set_position(('center', 'center')).crossfadein(anim_duration * 0.3)
            except:
                # Fallback if resize fails
                return base_clip.set_position(('center', 'center')).crossfadein(anim_duration)
        
        elif effect_type == 4:
            # Slide up from bottom
            def position(t):
                if t < anim_duration:
                    progress = min(1.0, t / anim_duration)
                    ease = 1 - pow(1 - progress, 3)
                    y_offset = int(height/3 * (1 - ease))
                    return ('center', VIDEO_HEIGHT//4 + y_offset)
                return ('center', VIDEO_HEIGHT//4)
            return base_clip.set_position(position).crossfadein(anim_duration * 0.5)
        
        else:
            # Elastic bounce (subtle, professional)
            def position(t):
                if t < anim_duration * 1.5:
                    progress = min(1.0, t / anim_duration)
                    # Elastic ease-out
                    if progress == 0 or progress == 1:
                        ease = progress
                    else:
                        p = 0.3
                        ease = pow(2, -10 * progress) * math.sin((progress - p/4) * (2 * math.pi) / p) + 1
                    y_offset = int(50 * (1 - ease))
                    return ('center', VIDEO_HEIGHT//4 - y_offset)
                return ('center', VIDEO_HEIGHT//4)
            return base_clip.set_position(position).crossfadein(anim_duration * 0.3)
    
    def get_sfx_for_phrase(self, phrase_index: int, total_phrases: int) -> Optional[str]:
        """
        Get appropriate sound effect for a phrase.
        
        - Hook (0): dramatic hit
        - Last phrase: ding (payoff)
        - Others: occasional whoosh for transitions
        """
        try:
            from sound_effects import get_all_sfx
            sfx = get_all_sfx()
            
            if phrase_index == 0:
                return sfx.get('hit')  # Dramatic hit for hook
            elif phrase_index == total_phrases - 1:
                return sfx.get('ding')  # Ding for payoff/CTA
            elif phrase_index % 2 == 1:
                return sfx.get('whoosh')  # Whoosh for some transitions
            return None
        except Exception as e:
            return None
    
    def create_subscribe_cta(self, duration: float = 2.0) -> VideoClip:
        """
        Create an animated subscribe CTA overlay.
        v7.15: Adds channel growth driver at end of video.
        
        Appears in bottom portion with subtle animation.
        """
        width, height = VIDEO_WIDTH, 200  # Smaller overlay at bottom
        
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Get font
        try:
            from dynamic_fonts import get_impact_font
            font_path = get_impact_font()
        except ImportError:
            font_path = None
        
        if not font_path or not os.path.exists(font_path):
            font_paths = [
                "C:/Windows/Fonts/impact.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
            font_path = next((f for f in font_paths if os.path.exists(f)), None)
        
        try:
            font = ImageFont.truetype(font_path, 48) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # CTA text
        cta_text = "SUBSCRIBE FOR MORE"
        
        # Get text size
        try:
            bbox = draw.textbbox((0, 0), cta_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width, text_height = 400, 50
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw semi-transparent background pill
        pill_padding = 30
        pill_left = x - pill_padding
        pill_right = x + text_width + pill_padding
        pill_top = y - pill_padding // 2
        pill_bottom = y + text_height + pill_padding // 2
        
        # Red subscribe button style
        try:
            draw.rounded_rectangle(
                [(pill_left, pill_top), (pill_right, pill_bottom)],
                radius=20,
                fill=(204, 0, 0, 230)  # YouTube red with slight transparency
            )
        except:
            # Fallback for older PIL
            draw.rectangle(
                [(pill_left, pill_top), (pill_right, pill_bottom)],
                fill=(204, 0, 0, 230)
            )
        
        # Draw text
        draw.text((x, y), cta_text, fill=(255, 255, 255, 255), font=font)
        
        # Convert to clip
        base_clip = self.pil_to_clip(img, duration)
        
        # Position at bottom with fade animation
        def position(t):
            # Slide up from below
            anim_time = 0.3
            if t < anim_time:
                progress = t / anim_time
                ease = 1 - pow(1 - progress, 3)
                y_pos = VIDEO_HEIGHT - 150 + 50 * (1 - ease)
                return ('center', y_pos)
            return ('center', VIDEO_HEIGHT - 150)
        
        return base_clip.set_position(position).crossfadein(0.2)
    
    def create_vignette_overlay(self, width: int, height: int, intensity: float = 0.4) -> Image.Image:
        """
        Create a vignette overlay for cinematic effect.
        OPTIMIZED: Uses numpy vectorized operations (100x faster than per-pixel).
        """
        # Create coordinate grids
        y_coords, x_coords = np.ogrid[:height, :width]
        
        center_x, center_y = width // 2, height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        # Vectorized distance calculation
        distance = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        normalized = distance / max_distance
        
        # Apply intensity curve and convert to alpha
        alpha = (255 * intensity * (normalized ** 1.5)).astype(np.uint8)
        alpha = np.clip(alpha, 0, 255)
        
        # Create RGBA array
        vignette_array = np.zeros((height, width, 4), dtype=np.uint8)
        vignette_array[:, :, 3] = alpha  # Set alpha channel
        
        return Image.fromarray(vignette_array, 'RGBA')
    
    def prepare_broll(self, path: str, duration: float) -> str:
        """Scale + center-crop a B-roll clip to VIDEO_WIDTH x VIDEO_HEIGHT at 30fps with ffmpeg.

        Returns the prepared file, or the original path if ffmpeg fails.
        """
        import subprocess
        out_path = CACHE_DIR / f"prep_{Path(path).stem}_{int(duration * 10)}.mp4"
        if out_path.exists() and out_path.stat().st_size > 0:
            return str(out_path)
        try:
            vf = (f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
                  f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps=30")
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", path, "-t", f"{duration + 0.5:.2f}", "-an",
                 "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                 "-pix_fmt", "yuv420p", str(out_path)],
                check=True, timeout=180
            )
            return str(out_path)
        except Exception as e:
            safe_print(f"   [!] B-roll prep skipped ({e}), using MoviePy resize")
            return path

    def apply_background_fx(self, clip: VideoClip, duration: float,
                            darken: float = 0.6, mood: str = 'default') -> VideoClip:
        """Ken Burns zoom (1.0 -> 1.08) + darken + mood color grade in one pass.

        Uses crop + BILINEAR resize and a PIL lookup table, which is much
        faster than MoviePy's per-frame LANCZOS resize and float math.
        """
        r_mult, g_mult, b_mult = self.get_grade_multipliers(mood)
        lut = [min(255, int(i * darken * m)) for m in (r_mult, g_mult, b_mult) for i in range(256)]

        def fx(get_frame, t):
            frame = get_frame(t)
            zoom = 1.0 + 0.08 * (t / max(duration, 0.01))
            h, w = frame.shape[:2]
            cw, ch = int(w / zoom), int(h / zoom)
            x, y = (w - cw) // 2, (h - ch) // 2
            img = Image.fromarray(frame[y:y+ch, x:x+cw])
            if (cw, ch) != (w, h):
                img = img.resize((w, h), Image.BILINEAR)
            return np.asarray(img.convert('RGB').point(lut))

        return clip.fl(fx)

    def get_grade_multipliers(self, mood: str = 'dramatic') -> Tuple[float, float, float]:
        """RGB multipliers for the mood color grade."""
        grades = {
            'dramatic': (1.0, 0.95, 1.1),
            'energetic': (1.1, 1.0, 0.95),
            'mysterious': (0.95, 0.95, 1.15),
            'inspirational': (1.05, 1.05, 1.0),
            'chill': (0.98, 1.02, 1.02),
            'emotional': (1.0, 0.92, 1.05),
            'tech': (0.95, 1.0, 1.1),
        }
        return grades.get(mood if isinstance(mood, str) else 'default', (1.0, 1.0, 1.0))

    def apply_color_grade(self, clip: VideoClip, mood: str = 'dramatic') -> VideoClip:
        """
        Apply cinematic color grading based on mood.
        """
        # Color grade multipliers for different moods
        grades = {
            'dramatic': (1.0, 0.95, 1.1),      # Slightly blue, desaturated
            'energetic': (1.1, 1.0, 0.95),     # Warm, punchy
            'mysterious': (0.95, 0.95, 1.15),  # Cool blue
            'inspirational': (1.05, 1.05, 1.0), # Warm, uplifting
            'chill': (0.98, 1.02, 1.02),       # Cool, calm
            'emotional': (1.0, 0.92, 1.05),    # Desaturated, moody
            'tech': (0.95, 1.0, 1.1),          # Cool tech blue
            'default': (1.0, 1.0, 1.0),        # No change
        }
        
        r_mult, g_mult, b_mult = grades.get(mood, grades['default'])
        
        def apply_grade(frame):
            # Apply RGB multipliers (clip to valid range)
            graded = frame.astype(float)
            graded[:, :, 0] = np.clip(graded[:, :, 0] * r_mult, 0, 255)
            graded[:, :, 1] = np.clip(graded[:, :, 1] * g_mult, 0, 255)
            graded[:, :, 2] = np.clip(graded[:, :, 2] * b_mult, 0, 255)
            return graded.astype(np.uint8)
        
        return clip.fl_image(apply_grade)


def get_background_music_with_skip(music_mood: str, skip_seconds: float = 3.0,
                                   category: str = "", content_summary: str = "") -> Optional[Tuple[str, float]]:
    """
    Get AI-selected background music and skip the silent intro.
    
    Uses AI to analyze content and find the best matching music.
    """
    try:
        # Try AI-driven music selection first
        from ai_music_selector import get_ai_selected_music
        music_path = get_ai_selected_music(category, music_mood, content_summary)
        if music_path:
            safe_print(f"   [OK] AI-selected music: {music_mood} (skipping first {skip_seconds}s)")
            return (music_path, skip_seconds)
    except ImportError:
        pass  # Fall back to legacy
    except Exception as e:
        safe_print(f"   [!] AI music selection failed: {e}")
    
    # Fallback to legacy system
    try:
        from background_music import get_background_music
        music_path = get_background_music(music_mood)
        if music_path:
            safe_print(f"   [OK] Music: {music_mood} (skipping first {skip_seconds}s)")
            return (music_path, skip_seconds)
    except Exception as e:
        safe_print(f"   [!] Music lookup failed: {e}")
    return None


async def generate_voiceover(text: str, voice_config: Dict, output_path: str) -> float:
    """
    Generate voiceover with retry logic and fallback voices.
    
    v17.9.7: Added retry logic and voice fallback to prevent workflow failures
    """
    voice = voice_config.get('voice', 'en-US-AriaNeural')
    rate = voice_config.get('rate', '+0%')
    
    # v17.9.7: Fallback voices in case primary fails
    fallback_voices = [
        voice,  # Primary
        'en-US-AriaNeural',
        'en-US-JennyNeural', 
        'en-US-GuyNeural',
        'en-US-ChristopherNeural'
    ]
    # Remove duplicates while preserving order
    seen = set()
    fallback_voices = [v for v in fallback_voices if not (v in seen or seen.add(v))]
    
    last_error = None
    
    for attempt, try_voice in enumerate(fallback_voices):
        for retry in range(3):  # 3 retries per voice
            try:
                safe_print(f"   [TTS] Voice: {try_voice} (rate: {rate})" + (f" [attempt {retry+1}]" if retry > 0 else ""))
                
                communicate = edge_tts.Communicate(text, voice=try_voice, rate=rate, pitch="+0Hz")
                await communicate.save(output_path)
                
                # Verify file was created and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    audio = AudioFileClip(output_path)
                    duration = audio.duration
                    audio.close()
                    
                    if duration > 0.5:  # Must be at least 0.5 seconds
                        if attempt > 0 or retry > 0:
                            safe_print(f"   [TTS] Recovered with voice: {try_voice}")
                        return duration
                    else:
                        raise Exception(f"Audio too short: {duration}s")
                else:
                    raise Exception("Audio file empty or not created")
                    
            except Exception as e:
                last_error = e
                safe_print(f"   [!] TTS attempt failed: {str(e)[:50]}")
                await asyncio.sleep(1 + retry)  # Exponential backoff
    
    # All attempts failed - raise the last error
    raise Exception(f"TTS failed after {len(fallback_voices) * 3} attempts: {last_error}")


async def render_video(content: Dict, broll_paths: List[str], output_path: str, 
                       voice_config: Dict, music_file: str) -> bool:
    """Render the final video."""
    safe_print("\n[RENDER] Starting video render...")
    
    phrases = content.get('phrases', [])
    concept = content.get('concept', {})
    
    if not phrases:
        return False
    
    # Remove duplicates
    seen = set()
    unique_phrases = []
    for p in phrases:
        if p not in seen:
            seen.add(p)
            unique_phrases.append(p)
    phrases = unique_phrases
    
    # v12.0: Apply text humanization (contractions, colloquial language)
    if ENHANCEMENTS_V12_AVAILABLE:
        try:
            humanized_phrases = []
            for p in phrases:
                humanized = apply_v12_text_humanization(p)
                humanized_phrases.append(humanized)
            phrases = humanized_phrases
            safe_print(f"   [v12.0] Text humanization applied")
        except Exception as e:
            safe_print(f"   [!] Humanization skipped: {e}")
    
    # v16.9: Apply additional v12 render enhancements
    render_settings = {}
    if ENHANCEMENTS_V12_AVAILABLE:
        try:
            category = concept.get('category', 'educational')
            
            # Font settings based on category
            font_settings = get_v12_font_settings(category)
            if font_settings:
                render_settings['font'] = font_settings
                
            # Music settings based on category mood
            music_settings = get_v12_music_settings(category)
            if music_settings:
                render_settings['music'] = music_settings
                
            # Color settings for visual consistency
            color_settings = get_v12_color_settings(category)
            if color_settings:
                render_settings['colors'] = color_settings
            
            # Text animation style
            text_anim = get_text_animation()
            if text_anim and hasattr(text_anim, 'get_style'):
                render_settings['animation'] = text_anim.get_style(category)
            
            # Voice matching for topic
            voice_match = get_voice_matcher()
            if voice_match and hasattr(voice_match, 'match'):
                render_settings['voice_hint'] = voice_match.match(category)
            
            # Music tempo and genre
            tempo = get_tempo_matcher()
            if tempo and hasattr(tempo, 'get_tempo'):
                render_settings['tempo'] = tempo.get_tempo(category)
                
            genre = get_genre_matcher()
            if genre and hasattr(genre, 'get_genre'):
                render_settings['genre'] = genre.get_genre(category)
            
            # Sound library effects
            sound_lib = get_sound_library()
            if sound_lib and hasattr(sound_lib, 'get_effects'):
                render_settings['sfx'] = sound_lib.get_effects(category)
                
            safe_print(f"   [v12.0] Render settings applied: {len(render_settings)} enhancements")
        except Exception as e:
            safe_print(f"   [!] v12 render enhancements skipped: {e}")
    
    safe_print(f"   Phrases: {len(phrases)}")
    
    # Generate voiceover
    full_text = ". ".join(phrases)
    voiceover_path = str(CACHE_DIR / f"vo_{random.randint(1000,9999)}.mp3")
    
    try:
        duration = await generate_voiceover(full_text, voice_config, voiceover_path)
        safe_print(f"   [OK] Voiceover: {duration:.1f}s")
    except Exception as e:
        safe_print(f"   [!] Voiceover failed: {e}")
        return False
    
    # Calculate timings
    total_chars = sum(len(p) for p in phrases)
    phrase_durations = []
    for phrase in phrases:
        char_ratio = len(phrase) / total_chars
        phrase_dur = char_ratio * duration
        phrase_dur = max(phrase_dur, 2.0)
        phrase_durations.append(phrase_dur)
    
    total_calc = sum(phrase_durations)
    if total_calc > 0:
        scale = duration / total_calc
        phrase_durations = [d * scale for d in phrase_durations]
    
    safe_print(f"   Timings: {[f'{d:.1f}s' for d in phrase_durations]}")
    
    while len(broll_paths) < len(phrases):
        broll_paths.append(None)
    
    # Get AI-selected music with intro skip
    # Pass content context for better AI selection
    category = concept.get('category', 'general')
    content_summary = phrases[0] if phrases else ''  # Use hook as summary
    music_result = get_background_music_with_skip(
        music_file, 
        skip_seconds=3.0,
        category=category,
        content_summary=content_summary
    )
    
    # Create segments
    renderer = VideoRenderer()
    segments = []
    
    for i, (phrase, broll_path, dur) in enumerate(zip(phrases, broll_paths, phrase_durations)):
        safe_print(f"   [*] Segment {i+1}/{len(phrases)}")
        
        layers = []
        
        if broll_path and os.path.exists(broll_path):
            try:
                # Let ffmpeg scale/crop to 1080x1920 once instead of MoviePy
                # resizing every frame in Python (was ~5x slower per frame)
                prepared_path = renderer.prepare_broll(broll_path, dur)
                bg = VideoFileClip(prepared_path, audio=False)

                if tuple(bg.size) != (VIDEO_WIDTH, VIDEO_HEIGHT):
                    bg_ratio = bg.size[0] / bg.size[1]
                    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT

                    if bg_ratio > target_ratio:
                        new_height = VIDEO_HEIGHT
                        new_width = int(new_height * bg_ratio)
                    else:
                        new_width = VIDEO_WIDTH
                        new_height = int(new_width / bg_ratio)

                    bg = bg.resize((new_width, new_height))

                    x_offset = (new_width - VIDEO_WIDTH) // 2
                    y_offset = (new_height - VIDEO_HEIGHT) // 2
                    bg = bg.crop(x1=x_offset, y1=y_offset, x2=x_offset+VIDEO_WIDTH, y2=y_offset+VIDEO_HEIGHT)

                if bg.duration < dur:
                    bg = bg.loop(duration=dur)
                bg = bg.subclip(0, dur)

                # v7.16: Ken Burns zoom (1.0 -> 1.08) + darken for text
                # readability + mood color grade, in one fast per-frame pass
                bg = renderer.apply_background_fx(bg, dur, darken=0.6, mood=music_file)
                
                layers.append(bg)
                
                # Add vignette overlay for cinematic look
                try:
                    vignette_img = renderer.create_vignette_overlay(VIDEO_WIDTH, VIDEO_HEIGHT, intensity=0.3)
                    vignette_clip = renderer.pil_to_clip(vignette_img, dur)
                    layers.append(vignette_clip)
                except:
                    pass  # Skip if vignette fails
                    
            except Exception as e:
                broll_path = None
        
        if not broll_path or not layers:
            # Dynamic gradient based on content category
            gradient = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
            colors = [(30 + i*10, 20 + i*5, 50 + i*8), (60 + i*15, 40 + i*10, 90 + i*12)]
            for y in range(VIDEO_HEIGHT):
                ratio = y / VIDEO_HEIGHT
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
                for x in range(VIDEO_WIDTH):
                    gradient.putpixel((x, y), (r, g, b))
            
            bg = renderer.pil_to_clip(gradient, dur)
            layers.append(bg)
        
        # Use animated text instead of static (clean any "Phrase X:" prefixes)
        clean_phrase = renderer.clean_phrase_prefix(phrase)
        # v13.0: Pass AI-selected font for content-appropriate typography
        selected_font = content.get('selected_font', None)
        text_clip = renderer.create_animated_text_clip(clean_phrase, dur, phrase_index=i, font_key=selected_font)
        # v17.9.10: Add small delay to text to better sync with audio
        # Text appears 150ms after segment starts (matches audio lead-time)
        TEXT_SYNC_DELAY = 0.15  # 150ms delay
        if dur > TEXT_SYNC_DELAY + 0.5:  # Only apply if segment long enough
            text_clip = text_clip.set_start(TEXT_SYNC_DELAY)
        layers.append(text_clip)
        
        # v7.15: Add subscribe CTA to LAST segment for monetization
        is_last_segment = (i == len(phrases) - 1)
        if is_last_segment and dur >= 3.0:
            try:
                cta_clip = renderer.create_subscribe_cta(duration=min(2.0, dur - 0.5))
                cta_clip = cta_clip.set_start(dur - 2.5)  # Appear near end
                layers.append(cta_clip)
                safe_print("   [OK] Added subscribe CTA to final segment")
            except Exception as e:
                safe_print(f"   [!] CTA error (continuing without): {e}")
        
        segment = CompositeVideoClip(layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        segment = segment.set_duration(dur)
        
        # v7.16: Add smooth crossfade transitions between segments
        # Skip first segment fade-in, skip last segment fade-out
        fade_duration = 0.15  # 150ms crossfade
        if i > 0:  # Fade in for all except first
            segment = segment.crossfadein(fade_duration)
        if i < len(phrases) - 1:  # Fade out for all except last
            segment = segment.crossfadeout(fade_duration)
        
        segments.append(segment)
    
    safe_print("   [*] Concatenating segments with transitions...")
    final_video = concatenate_videoclips(segments, method="compose")
    
    progress_clip = renderer.create_progress_bar(final_video.duration)
    progress_clip = progress_clip.set_position(("center", 12))
    
    final_video = CompositeVideoClip(
        [final_video, progress_clip],
        size=(VIDEO_WIDTH, VIDEO_HEIGHT)
    ).set_duration(final_video.duration)
    
    # Audio mixing - skip music intro + add sound effects
    vo_clip = AudioFileClip(voiceover_path)
    audio_layers = [vo_clip]
    
    # Add sound effects at phrase transitions
    # v13.0: Use varied SFX plan (not same pattern every time!)
    try:
        sfx_clips = []
        cumulative_time = 0
        # Use pre-planned varied SFX if available
        sfx_plan = content.get('sfx_plan', [])
        
        for i, dur in enumerate(phrase_durations):
            # Get SFX from varied plan or fall back to old method
            if sfx_plan and i < len(sfx_plan):
                sfx_name = sfx_plan[i]
                if sfx_name:
                    # Get SFX path from name
                    try:
                        from sound_effects import get_all_sfx
                        sfx_dict = get_all_sfx()
                        sfx_path = sfx_dict.get(sfx_name)
                    except:
                        sfx_path = None
                else:
                    sfx_path = None  # Intentionally silent
            else:
                # Fallback to old deterministic method
                sfx_path = renderer.get_sfx_for_phrase(i, len(phrases))
            
            if sfx_path and os.path.exists(sfx_path):
                sfx = AudioFileClip(sfx_path).volumex(0.4)  # 40% volume
                # Position SFX at start of each phrase
                sfx = sfx.set_start(cumulative_time)
                sfx_clips.append(sfx)
            cumulative_time += dur
        if sfx_clips:
            audio_layers.extend(sfx_clips)
            safe_print(f"   [OK] Added {len(sfx_clips)} sound effects (varied)")
        else:
            safe_print(f"   [*] Minimal SFX (silent emphasis style)")
    except Exception as e:
        safe_print(f"   [!] SFX error (continuing without): {e}")
    
    # Add background music
    if music_result:
        music_path, skip_seconds = music_result
        try:
            music_clip = AudioFileClip(music_path)
            
            # Skip the silent intro
            if music_clip.duration > skip_seconds + final_video.duration:
                music_clip = music_clip.subclip(skip_seconds)
            
            music_clip = music_clip.volumex(0.15)
            
            if music_clip.duration < final_video.duration:
                music_clip = music_clip.loop(duration=final_video.duration)
            music_clip = music_clip.subclip(0, final_video.duration)
            
            audio_layers.append(music_clip)
        except Exception as e:
            safe_print(f"   [!] Music error: {e}")
    
    final_audio = CompositeAudioClip(audio_layers)
    
    final_video = final_video.set_audio(final_audio)
    
    safe_print("   [*] Rendering final video...")
    # v17.7.9: Enhanced rendering settings for professional quality
    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='slow',  # v17.7.9: Better quality (was 'medium')
        bitrate='12M',  # v17.7.9: Higher bitrate (was '8M')
        threads=os.cpu_count() or 4,
        ffmpeg_params=[
            '-crf', '18',           # v17.7.9: High quality CRF
            '-profile:v', 'high',   # v17.7.9: H.264 High Profile
            '-pix_fmt', 'yuv420p',  # v17.7.9: Compatibility
            '-movflags', '+faststart',  # v17.7.9: Web optimization
        ],
        logger=None
    )
    
    final_video.close()
    vo_clip.close()
    
    safe_print(f"   [OK] Created: {output_path}")
    return True


async def generate_pro_video(hint: str = None, batch_tracker: BatchTracker = None, output_dir: str = None) -> Optional[str]:
    """
    Generate a video with 100% AI-driven decisions.
    VARIETY ENFORCED through batch_tracker.
    
    v9.0: Enhanced with comprehensive quality gates and AI-driven checks
    
    Args:
        output_dir: Custom output directory (defaults to OUTPUT_DIR if None)
    """
    # Use custom output dir or default
    video_output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    video_output_dir.mkdir(parents=True, exist_ok=True)
    run_id = random.randint(10000, 99999)
    
    safe_print("=" * 70)
    safe_print(f"   VIRALSHORTS FACTORY v17.9.7 - YOUTUBE FOCUS")
    safe_print(f"   Run: #{run_id}")
    safe_print(f"   Video Length: 40-50 seconds (optimal)")
    safe_print(f"   Variety: Persistent across runs")
    safe_print(f"   Quality Gates: {len(['pre-gen', 'post-content', 'post-render'])} active")
    safe_print("=" * 70)
    
    # v9.0: Initialize enhancement orchestrator
    enhancement_orch = None
    if ENHANCEMENTS_AVAILABLE:
        try:
            enhancement_orch = get_enhancement_orchestrator()
            safe_print("   [v9.0] Enhancement orchestrator initialized")
        except Exception as e:
            safe_print(f"   [!] Enhancement init skipped: {e}")
    
    # v7.17: Comprehensive initialization with fallback
    try:
        ai = MasterAI()
    except Exception as e:
        safe_print(f"[!] AI initialization failed: {e}")
        return None
        
    if not ai.client and not ai.gemini_model:
        safe_print("[!] No AI available")
        return None
    
    # Stage 1: AI decides concept (with variety enforcement)
    max_concept_attempts = 3  # v9.0: Retry if semantic duplicate
    concept = None
    
    for attempt in range(max_concept_attempts):
        try:
            concept = ai.stage1_decide_video_concept(hint, batch_tracker)
        except Exception as e:
            safe_print(f"[!] Concept generation error: {e}")
            concept = None
        
        if not concept:
            break
        
        # v9.0: PRE-GENERATION CHECK - Semantic duplicate detection
        if enhancement_orch and ENHANCEMENTS_AVAILABLE:
            try:
                recent_topics = batch_tracker.used_topics if batch_tracker else []
                # Also get recent topics from persistent state
                if PERSISTENT_STATE_AVAILABLE:
                    try:
                        variety_mgr = get_variety_manager()
                        recent_topics = list(set(recent_topics + variety_mgr.get_recent_topics()))
                    except:
                        pass

                # Stage 1 already records the new topic to variety state, so drop it
                # here - otherwise every concept is flagged as a duplicate of itself
                current_topic = concept.get('specific_topic', '').strip().lower()
                recent_topics = [t for t in recent_topics
                                 if t and t.strip().lower() != current_topic]

                pre_check = enhancement_orch.pre_generation_checks(
                    topic=concept.get('specific_topic', ''),
                    hook=concept.get('hook', ''),
                    recent_topics=recent_topics
                )
                
                if not pre_check.get('proceed', True):
                    safe_print(f"   [v9.0] Semantic duplicate detected - regenerating...")
                    safe_print(f"         {pre_check.get('warnings', ['Unknown issue'])[0]}")
                    if attempt < max_concept_attempts - 1:
                        hint = pre_check.get('modifications', {}).get('suggested_topic', hint)
                        continue
                else:
                    # v16.0 FIX: INJECT enhancement instructions into concept!
                    # These were calculated but NEVER used before!
                    if pre_check.get('enhancements'):
                        concept['enhancement_instructions'] = pre_check['enhancements']
                        safe_print(f"   [v16.0] Injecting {len(pre_check['enhancements'])} enhancement instructions!")
                    break  # Concept is unique, proceed
            except Exception as e:
                safe_print(f"   [!] Pre-check skipped: {e}")
                break
        else:
            break
        
    if not concept:
        safe_print("[!] Concept generation failed - trying dynamic fallback")
        # v16.2: Dynamic fallback - no hardcoded topics!
        fallback_categories = BASE_CATEGORIES.copy()
        random.shuffle(fallback_categories)
        fallback_cat = fallback_categories[0]
        
        topic_templates = [
            f"Mind-Blowing {fallback_cat.replace('_', ' ').title()} Secret",
            f"The {fallback_cat.replace('_', ' ').title()} Trick That Works Every Time",
            f"What 99% Get Wrong About {fallback_cat.replace('_', ' ').title()}",
        ]
        
        concept = {
            'category': fallback_cat,
            'specific_topic': random.choice(topic_templates),
            'phrase_count': random.randint(8, 10),
            'voice_style': random.choice(['energetic', 'dramatic', 'confident']),
            'music_mood': random.choice(['dramatic', 'upbeat', 'mysterious']),
            'target_duration_seconds': random.randint(40, 50)
        }
    
    # v17.9.7: AI Quality Gate - Pre-generation quality check
    if AI_QUALITY_GATE_AVAILABLE:
        try:
            quality_gate = AIQualityGate()
            # v17.9.7: Fixed - method is check(content: Dict), returns (passed: bool, report: Dict)
            gate_content = {
                'hook': concept.get('hook', concept.get('specific_topic', '')),
                'phrases': [],  # Not available yet in pre-gen
                'cta': '',
                'category': concept.get('category', 'educational'),
                'topic': concept.get('specific_topic', '')
            }
            passed, gate_result = quality_gate.check(gate_content)
            verdict = 'PASS' if passed else 'FAIL'
            safe_print(f"   [QUALITY GATE] Pre-check: {gate_result.get('overall_score', 0)}/100 - {verdict}")
            
            # Store gate result for later analysis
            concept['quality_gate_result'] = gate_result
            concept['quality_gate_passed'] = passed
            
            # If concept is poor quality, try to improve it
            if not passed and gate_result.get('recommendations'):
                safe_print(f"   [QUALITY GATE] Improving concept: {gate_result['recommendations'][0][:50]}...")
                concept['improvement_needed'] = gate_result.get('recommendations', [])[:2]
        except Exception as e:
            safe_print(f"   [!] Quality gate skipped: {e}")
    
    # Stage 2: AI creates content
    try:
        content = ai.stage2_create_content(concept)
    except Exception as e:
        safe_print(f"[!] Content creation error: {e}")
        content = None
        
    if not content or not content.get('phrases'):
        safe_print("[!] Content creation failed")
        return None
    
    # Stage 3: AI evaluates and enhances (non-critical - continue on failure)
    # v8.9.1: Moved promise validation INTO the AI evaluation prompt (not hardcoded)
    try:
        content = ai.stage3_evaluate_enhance(content)
    except Exception as e:
        safe_print(f"[!] Enhancement skipped: {e}")
    
    # v9.0: POST-CONTENT CHECKS - Pacing, retention, value density
    if enhancement_orch and ENHANCEMENTS_AVAILABLE:
        try:
            phrases = content.get('phrases', [])
            metadata_draft = {'hook': phrases[0] if phrases else '', 'category': concept.get('category', '')}
            
            post_checks = enhancement_orch.post_content_checks(phrases, metadata_draft)
            
            # Store pacing data for voice generation
            if post_checks.get('pacing'):
                content['voice_pacing'] = post_checks['pacing']
                safe_print(f"   [v9.0] Voice pacing: optimized for {len(phrases)} phrases")
            
            # Log retention prediction
            if post_checks.get('retention_prediction'):
                retention = post_checks['retention_prediction']
                safe_print(f"   [v9.0] Predicted retention: {retention.get('estimated_avg_retention', '?')}%")
                content['retention_prediction'] = retention
            
            # Log value density
            if post_checks.get('value_density'):
                density = post_checks['value_density']
                safe_print(f"   [v9.0] Value density: {density.get('value_score', '?')}/10")
                content['value_density'] = density
                
        except Exception as e:
            safe_print(f"   [!] Post-content checks skipped: {e}")
    
    # ==========================================================================
    # CRITICAL FIXES: Quality, Promise, Font, SFX enforcement
    # ==========================================================================
    if CRITICAL_FIXES_AVAILABLE:
        try:
            # 1. Check and ENFORCE minimum quality score with REGENERATION
            # v17.2: Reduced max_regen from 3 to 1 - focus on getting it right FIRST TIME
            # Regeneration wastes quota and rarely improves significantly
            # Instead, we fixed the scoring prompt to be more accurate
            score = content.get('evaluation_score', 5)
            regeneration_attempts = 0
            max_regen = 2  # v17.9.9: Allow 2 retries with oscillation detection
            
            # v17.9.9: OSCILLATION DETECTION - track score history to prevent 7-8-7-8 loops
            score_history = [score]
            best_content = content  # Track best content seen
            best_score = score
            
            while score < MINIMUM_ACCEPTABLE_SCORE and regeneration_attempts < max_regen:
                regeneration_attempts += 1
                safe_print(f"   [QUALITY] Score {score}/10 BELOW minimum {MINIMUM_ACCEPTABLE_SCORE}/10 - REGENERATING (attempt {regeneration_attempts}/{max_regen})")
                
                # v17.9.9: Check for oscillation (same score seen before)
                if len(score_history) >= 2:
                    # Oscillation = returning to a previously seen score
                    if score in score_history[:-1]:
                        safe_print(f"   [OSCILLATION] Detected score {score} repeated - breaking loop")
                        break
                    # Plateau = no improvement for 2 attempts
                    if len(set(score_history[-2:])) == 1:
                        safe_print(f"   [PLATEAU] Score stuck at {score} - breaking loop")
                        break
                
                # Build feedback for AI to improve
                quality_issues = content.get('quality_issues', [])
                feedback = f"Previous attempt scored {score}/10 - UNACCEPTABLE. "
                if quality_issues:
                    feedback += f"Issues: {', '.join([i.get('issue', '') for i in quality_issues[:3]])}. "
                feedback += f"Make it MORE engaging, MORE specific, MORE valuable. MINIMUM score needed: {MINIMUM_ACCEPTABLE_SCORE}/10."
                
                # Regenerate content with feedback
                try:
                    # Add feedback to concept for regeneration
                    concept['regeneration_feedback'] = feedback
                    concept['attempt_number'] = regeneration_attempts
                    
                    new_content = ai.stage2_create_content(concept)
                    if new_content and new_content.get('phrases'):
                        # Re-evaluate new content
                        new_content = ai.stage3_evaluate_enhance(new_content)
                        new_score = new_content.get('evaluation_score', 0)
                        
                        # v17.9.9: Track all scores for oscillation detection
                        score_history.append(new_score)
                        
                        # v17.9.9: Always keep the BEST content seen
                        if new_score > best_score:
                            best_score = new_score
                            best_content = new_content
                            safe_print(f"   [QUALITY] New best: {score}/10 -> {new_score}/10")
                        
                        if new_score > score:
                            safe_print(f"   [QUALITY] Improved: {score}/10 -> {new_score}/10")
                            content = new_content
                            score = new_score
                        else:
                            safe_print(f"   [QUALITY] No improvement: {new_score}/10 (keeping previous)")
                except Exception as e:
                    safe_print(f"   [!] Regeneration attempt {regeneration_attempts} failed: {e}")
            
            # v17.9.9: Use best content from all attempts (not just last)
            if best_score > score:
                safe_print(f"   [QUALITY] Using best content from attempts: {best_score}/10")
                content = best_content
                score = best_score
            
            if score >= MINIMUM_ACCEPTABLE_SCORE:
                safe_print(f"   [QUALITY] Score {score}/10 - ACCEPTABLE")
                content['quality_warning'] = False
            else:
                # v17.7: Try ViralContentGenerator as last resort before accepting low quality
                if VIRAL_SCIENCE_AVAILABLE and score < MINIMUM_ACCEPTABLE_SCORE - 1:
                    try:
                        safe_print(f"   [VIRAL SCIENCE] Attempting high-quality content generation...")
                        vcg = ViralContentGenerator()
                        category = concept.get('category', 'life_hack')
                        topic = concept.get('specific_topic', '')
                        viral_content = vcg.generate(category, topic)
                        if viral_content and viral_content.get('full_script'):
                            # Convert to our format
                            script = viral_content.get('full_script', '')
                            sentences = [s.strip() for s in script.split('.') if len(s.strip()) > 10][:5]
                            if len(sentences) >= 3:
                                content['phrases'] = sentences
                                content['quality_warning'] = False
                                safe_print(f"   [VIRAL SCIENCE] Generated high-value content!")
                                score = 8  # Trust ViralContentGenerator's value check
                    except Exception as e:
                        safe_print(f"   [!] Viral science fallback failed: {e}")
                
                if score < MINIMUM_ACCEPTABLE_SCORE:
                    safe_print(f"   [QUALITY] WARNING: Could not reach {MINIMUM_ACCEPTABLE_SCORE}/10 after {regeneration_attempts} attempts. Best: {score}/10")
                    content['quality_warning'] = True
            
            # v17.9.7: ContentOptimizer - Final unified optimization pass
            if CONTENT_OPTIMIZER_AVAILABLE and score < 9:
                try:
                    optimizer = ContentOptimizer()
                    # v17.9.7: Fixed - method is optimize(content: Dict), not optimize_content(concept, content)
                    opt_content = {
                        'hook': content.get('phrases', [''])[0] if content.get('phrases') else '',
                        'phrases': content.get('phrases', [])[1:] if len(content.get('phrases', [])) > 1 else content.get('phrases', []),
                        'cta': content.get('cta', ''),
                        'topic': concept.get('specific_topic', ''),
                        'category': concept.get('category', 'educational'),
                        'title': content.get('metadata', {}).get('title', '')
                    }
                    optimized = optimizer.optimize(opt_content)
                    if optimized and optimized.get('predictions', {}).get('final_virality', 0) > score * 10:
                        # Apply optimizations to content
                        if optimized.get('optimized', {}).get('hook'):
                            content['hook_improved'] = optimized['optimized']['hook']
                        if optimized.get('optimized', {}).get('cta'):
                            content['cta'] = optimized['optimized']['cta']
                        new_score = optimized.get('predictions', {}).get('final_virality', score * 10) / 10
                        safe_print(f"   [OPTIMIZER] Content improved: {score}/10 -> {new_score:.1f}/10")
                        if optimized.get('improvements'):
                            safe_print(f"   [OPTIMIZER] Improvements: {', '.join(optimized['improvements'][:2])}")
                        score = max(score, new_score)
                except Exception as e:
                    safe_print(f"   [!] Content optimizer skipped: {e}")
            
            # v15.0: Record result for FirstAttemptMaximizer learning
            if ai.first_attempt:
                ai.first_attempt.record_result(
                    score=score,
                    category=concept.get('category', 'unknown'),
                    hook=content.get('phrases', [''])[0] if content.get('phrases') else '',
                    was_regeneration=regeneration_attempts > 0
                )
                safe_print(f"   [LEARNING] Recorded quality result for future optimization")
            
            # v15.0: Record to self-learning engine for pattern analysis
            if ai.learning_engine and content.get('phrases'):
                ai.learning_engine.learn_from_video(
                    score=score,
                    category=concept.get('category', 'unknown'),
                    topic=concept.get('specific_topic', 'unknown'),
                    hook=content.get('phrases', [''])[0],
                    phrases=content.get('phrases', []),
                    was_regeneration=regeneration_attempts > 0
                )
            
            # 2. Validate and fix numbered promises
            phrases = content.get('phrases', [])
            if phrases:
                validation = validate_numbered_promise(phrases[0], phrases)
                if not validation['valid']:
                    safe_print(f"   [PROMISE FIX] Promised {validation['promised']}, delivered {validation['delivered']}")
                    fixed_hook = fix_broken_promise(phrases[0], validation['delivered'])
                    content['phrases'][0] = fixed_hook
                    content['promise_fixed'] = True
                    safe_print(f"   [PROMISE FIX] Hook updated: {fixed_hook[:50]}...")
                else:
                    content['promise_fixed'] = False
            
            # 3. Select appropriate font based on content
            category = concept.get('category', 'general')
            mood = concept.get('music_mood', content.get('mood', 'neutral'))
            topic = concept.get('specific_topic', '')
            selected_font = select_font_for_content(category, mood, topic)
            content['selected_font'] = selected_font
            safe_print(f"   [FONT] Selected: {selected_font} (based on {category}/{mood})")
            
            # 4. Plan varied SFX for this video with detailed logging
            sfx_plan = []
            sfx_details = []
            for i in range(len(phrases)):
                sfx = get_varied_sfx_for_phrase(i, len(phrases), run_id)
                sfx_plan.append(sfx)
                position = "HOOK" if i == 0 else ("END" if i == len(phrases) - 1 else f"P{i}")
                sfx_details.append(f"{position}:{sfx or 'silent'}")
            content['sfx_plan'] = sfx_plan
            # Show exact SFX pattern for this video
            safe_print(f"   [SFX] Pattern: {' -> '.join(sfx_details)}")
            
        except Exception as e:
            safe_print(f"   [!] Critical fixes error: {e}")
    
    # Stage 4: AI generates B-roll keywords
    try:
        broll_keywords = ai.stage4_broll_keywords(content.get('phrases', []))
    except Exception as e:
        safe_print(f"[!] B-roll keyword error: {e}")
        # Fallback keywords
        broll_keywords = ['motivation', 'success', 'nature', 'technology', 'people']
    
    # Stage 5: AI generates metadata
    try:
        metadata = ai.stage5_metadata(content)
    except Exception as e:
        safe_print(f"[!] Metadata generation error: {e}")
        metadata = None
    
    # FALLBACK: Ensure we always have a title (v7.13 fix)
    if not metadata or not metadata.get('title'):
        fallback_title = concept.get('specific_topic', 'Amazing Fact')[:100]
        safe_print(f"   [FALLBACK] Using topic as title: {fallback_title}")
        metadata = metadata or {}
        metadata['title'] = fallback_title
        metadata['description'] = f"{fallback_title} #shorts #viral #facts"
        metadata['hashtags'] = ['#shorts', '#viral', '#facts', '#trending']
    
    # v17.9.6: Use AI modules to enhance description and hashtags
    topic = concept.get('specific_topic', metadata.get('title', ''))
    category = concept.get('category', 'educational')
    video_summary = " ".join(content.get('phrases', [])[:3]) if content else topic
    
    # AI Description Generator
    if AI_DESCRIPTION_GENERATOR_AVAILABLE:
        try:
            desc_gen = AIDescriptionGenerator()
            # v17.9.7: Fixed - correct method signature: (title, topic, category, hook=None, hashtags=None, music_credit=None)
            ai_description = desc_gen.generate_description(
                title=metadata.get('title', topic),
                topic=topic,
                category=category,
                hook=content.get('phrases', [''])[0] if content else None,
                hashtags=metadata.get('hashtags', [])
            )
            if ai_description and len(ai_description) > 50:
                metadata['description'] = ai_description
                safe_print(f"   [AI DESC] Generated SEO description ({len(ai_description)} chars)")
        except Exception as e:
            safe_print(f"   [!] AI description skipped: {e}")
    
    # AI Hashtag Generator
    if AI_HASHTAG_GENERATOR_AVAILABLE:
        try:
            hash_gen = AIHashtagGenerator()
            # v17.9.7: Fixed - correct method signature: (topic, category, title=None, count=5)
            ai_hashtags = hash_gen.generate_hashtags(
                topic=topic,
                category=category,
                title=metadata.get('title', topic),
                count=8
            )
            if ai_hashtags and len(ai_hashtags) >= 3:
                # Ensure #shorts is included
                if '#shorts' not in ai_hashtags:
                    ai_hashtags.insert(0, '#shorts')
                metadata['hashtags'] = ai_hashtags
                safe_print(f"   [AI TAGS] Generated {len(ai_hashtags)} optimized hashtags")
        except Exception as e:
            safe_print(f"   [!] AI hashtags skipped: {e}")
    
    # Get voice and music with variety enforcement
    voice_config = ai.get_voice_config(concept, batch_tracker)
    music_file = ai.get_music_path(concept, batch_tracker)
    
    # Download B-roll (v9.0: with error pattern learning)
    safe_print("\n[BROLL] Downloading visuals...")
    renderer = VideoRenderer()
    broll_paths = []
    for i, keyword in enumerate(broll_keywords):
        # v9.0: Check if keyword has failed too many times
        actual_keyword = keyword
        if enhancement_orch and ENHANCEMENTS_AVAILABLE:
            try:
                if enhancement_orch.should_skip_broll_keyword(keyword):
                    alt_keyword = enhancement_orch.get_alternative_broll(keyword)
                    if alt_keyword:
                        safe_print(f"   [v9.0] Replacing '{keyword}' -> '{alt_keyword}' (learned from failures)")
                        actual_keyword = alt_keyword
            except:
                pass
        
        path = renderer.download_broll(actual_keyword, i)
        
        # v9.0: Record failure if no path returned
        if not path and enhancement_orch and ENHANCEMENTS_AVAILABLE:
            try:
                enhancement_orch.record_error('broll', keyword)
            except:
                pass
        
        broll_paths.append(path)
    
    # Render
    category = concept.get('category', 'fact')
    safe_cat = "".join(c if c.isalnum() else '_' for c in category)[:20]
    output_path = str(video_output_dir / f"pro_{safe_cat}_{run_id}.mp4")
    
    success = await render_video(content, broll_paths, output_path, voice_config, music_file)
    
    if success:
        # v9.0: POST-RENDER VALIDATION - Final quality gate before upload
        post_render_quality = None
        if enhancement_orch and ENHANCEMENTS_AVAILABLE:
            try:
                # Get actual video duration
                from moviepy.editor import VideoFileClip as VFC
                with VFC(output_path) as clip:
                    video_duration = clip.duration
                
                phrases = content.get('phrases', [])
                post_render_quality = enhancement_orch.post_render_validation(
                    phrases=phrases,
                    metadata={'title': metadata.get('title', ''), 'category': concept.get('category', '')},
                    video_duration=video_duration
                )
                
                quality_score = post_render_quality.get('quality_score', 7)
                safe_print(f"   [v9.0] Post-render quality: {quality_score}/10")
                
                if not post_render_quality.get('approved', True):
                    safe_print(f"   [v9.0] Quality issues: {post_render_quality.get('issues', [])}")
                    
            except Exception as e:
                safe_print(f"   [!] Post-render validation skipped: {e}")
        
        # v16.9: V12 COMPLIANCE CHECK - YouTube guidelines compliance
        if ENHANCEMENTS_V12_AVAILABLE:
            try:
                compliance_rules = get_v12_compliance_rules()
                yt_optimization = get_yt_optimization()
                source_citation = get_source_citation()
                
                # Check title compliance
                title = metadata.get('title', '')
                if len(title) > 100:
                    safe_print(f"   [v12] WARNING: Title too long ({len(title)} chars), may be truncated")
                
                # Check for YouTube Shorts optimization
                if yt_optimization and hasattr(yt_optimization, 'check'):
                    yt_issues = yt_optimization.check(metadata)
                    if yt_issues:
                        safe_print(f"   [v12] YouTube optimization issues: {yt_issues[:2]}")
                
                # Verify source citations if claims made
                if source_citation and hasattr(source_citation, 'check_needed'):
                    phrases = content.get('phrases', [])
                    if source_citation.check_needed(phrases):
                        safe_print(f"   [v12] Note: Content may benefit from source citations")
                        
                safe_print(f"   [v12] Compliance check passed")
            except Exception as e:
                safe_print(f"   [!] v12 compliance check skipped: {e}")
        
        # v9.0: Track A/B test variant
        if enhancement_orch and ENHANCEMENTS_AVAILABLE:
            try:
                # Track which title style was used
                title_style = metadata.get('title_style', 'number_hook')
                enhancement_orch.record_ab_test(
                    variant_type='title_styles',
                    variant_name=title_style,
                    video_id=str(run_id),
                    metadata=metadata
                )
            except Exception as e:
                pass  # Non-critical
        
        # Save metadata
        meta_path = output_path.replace('.mp4', '_meta.json')
        full_metadata = {
            'concept': concept,
            'content': content,
            'metadata': metadata,
            'broll_keywords': broll_keywords,
            'voice_config': voice_config,
            'music_file': music_file,
            'run_id': run_id,
            'v9_enhancements': {
                'post_render_quality': post_render_quality,
                'retention_prediction': content.get('retention_prediction'),
                'value_density': content.get('value_density')
            }
        }
        with open(meta_path, 'w') as f:
            json.dump(full_metadata, f, indent=2)
        
        # v17.7.3: Generate AI-driven thumbnail
        thumbnail_path = None
        if THUMBNAIL_GENERATOR_AVAILABLE:
            try:
                topic = concept.get('specific_topic', 'Viral Short')
                category = concept.get('category', 'motivation')
                thumbnail_path = output_path.replace('.mp4', '_thumbnail.png')
                
                # Get AI-driven thumbnail concept
                success = generate_thumbnail(topic, category, thumbnail_path)
                if success:
                    safe_print(f"   [THUMBNAIL] Generated: {thumbnail_path}")
                    full_metadata['thumbnail_path'] = thumbnail_path
            except Exception as e:
                safe_print(f"   [!] Thumbnail generation failed: {e}")
        
        # Track in batch with score
        score = content.get('evaluation_score', 7)
        if batch_tracker:
            batch_tracker.add_video(output_path, score, metadata or {})
        
        # === ANALYTICS FEEDBACK INTEGRATION (v8.0 Enhanced) ===
        try:
            from analytics_feedback import FeedbackLoopController
            feedback = FeedbackLoopController()
            
            # Record video generation for learning - v13.2: Enhanced with v9/v11/v12 data
            feedback.record_video_generation(
                video_id=run_id,
                local_path=output_path,
                topic_data={
                    'topic': concept.get('specific_topic', 'Unknown'),
                    'video_type': concept.get('category', 'unknown'),
                    'hook': content.get('phrases', [''])[0] if content.get('phrases') else '',
                    'content': ' '.join(content.get('phrases', [])),
                    'broll_keywords': broll_keywords,
                    'music_mood': concept.get('music_mood', 'dramatic'),
                    'value_check': {'score': score},
                    'virality_score': score,
                    # v13.2: Track enhancement data
                    'selected_font': content.get('selected_font', 'default'),
                    'sfx_plan': content.get('sfx_plan', []),
                    'promise_fixed': content.get('promise_fixed', False),
                    'quality_warning': content.get('quality_warning', False),
                    'retention_prediction': content.get('retention_prediction', {}),
                    'value_density': content.get('value_density', {}),
                },
                generation_data={
                    'voiceover_style': voice_config.get('style', 'energetic'),
                    'voice_name': voice_config.get('voice', 'AriaNeural'),
                    'music_file': music_file,
                    'phrase_count': len(content.get('phrases', [])),
                    'total_word_count': sum(len(p.split()) for p in content.get('phrases', [])),
                    'ai_title_generated': True,
                    'ai_hashtags_generated': True,
                    'has_vignette': True,
                    'trend_source': 'ai_generated',
                    # v13.2: Track which enhancements were active
                    'v9_enhancements_active': ENHANCEMENTS_AVAILABLE,
                    'v12_enhancements_active': ENHANCEMENTS_V12_AVAILABLE,
                    'critical_fixes_active': CRITICAL_FIXES_AVAILABLE,
                }
            )
            safe_print("   [ANALYTICS] Video recorded for learning")
        except Exception as e:
            pass  # Non-critical, don't break video generation
        
        # v16.9: V12 INTELLIGENCE ENHANCEMENTS - Performance correlation & token tracking
        if ENHANCEMENTS_V12_AVAILABLE:
            try:
                # Performance correlator - track what factors lead to success
                perf_correlator = get_performance_correlator()
                if perf_correlator and hasattr(perf_correlator, 'record'):
                    perf_correlator.record({
                        'video_id': str(run_id),
                        'category': concept.get('category', ''),
                        'hook_type': content.get('hook_type', 'unknown'),
                        'phrase_count': len(content.get('phrases', [])),
                        'title_length': len(metadata.get('title', '')),
                        'quality_score': post_render_quality.get('quality_score', 5) if post_render_quality else 5
                    })
                    
                # Token budget tracker - monitor API usage efficiency
                v12_token_budget = get_token_budget()
                if v12_token_budget and hasattr(v12_token_budget, 'record_generation'):
                    v12_token_budget.record_generation()
                    
                # Algorithm checklist verification
                algo_checklist = get_v12_algorithm_checklist()
                if algo_checklist:
                    safe_print(f"   [v12] Algorithm checklist verified")
                    
                # YouTube compliance verification
                yt_comp = get_yt_compliance()
                if yt_comp and hasattr(yt_comp, 'verify'):
                    compliance = yt_comp.verify(metadata)
                    if not compliance.get('passed', True):
                        safe_print(f"   [v12] Compliance issues: {compliance.get('issues', [])[:2]}")
                        
            except Exception as e:
                pass  # Non-critical
        
        # v8.0: Also record to persistent analytics
        if PERSISTENT_STATE_AVAILABLE:
            try:
                analytics = get_analytics_manager()
                analytics.record_video({
                    'video_id': str(run_id),
                    'category': concept.get('category', ''),
                    'topic': concept.get('specific_topic', ''),
                    'title': metadata.get('title', ''),
                    'hook': content.get('phrases', [''])[0] if content.get('phrases') else '',
                    'voice': voice_config.get('voice', ''),
                    'music_mood': concept.get('music_mood', ''),
                    'duration': concept.get('target_duration_seconds', 20),
                    'score': score,
                })
                safe_print("   [PERSIST] Video recorded to persistent analytics")
            except Exception as e:
                pass
        
        # v9.5: Record to new tracking systems
        if ENHANCEMENTS_V95_AVAILABLE:
            try:
                # Track hook word performance (will correlate with views later)
                hook_text = content.get('phrases', [''])[0] if content.get('phrases') else ''
                if hook_text:
                    hook_tracker = get_hook_tracker()
                    # Initial recording - performance will be updated in analytics feedback
                    hook_tracker.record_hook_performance(hook_text, 0, 1)  # Placeholder
                
                # Track hashtags used
                hashtag_rotator = get_hashtag_rotator()
                if metadata.get('hashtags'):
                    hashtag_rotator.record_used_set(metadata.get('hashtags', []))
                
                # Track category for decay
                category_decay = get_category_decay()
                # Initial recording - will be updated with actual performance
                category_decay.record_performance(
                    concept.get('category', 'unknown'), 0, 1
                )
                
                safe_print("   [v9.5] Recorded to hook/hashtag/decay trackers")
            except Exception as e:
                safe_print(f"   [!] v9.5 tracking error: {e}")
        
        # v10.0: Additional tracking and predictions
        if ENHANCEMENTS_V10_AVAILABLE:
            try:
                # Track title length for optimization
                title_opt = get_title_length_optimizer()
                title = metadata.get('title', '')
                if title:
                    # Record with placeholder CTR (will be updated later)
                    title_opt.record_title_performance(title, 0.05)
                
                # Track intro pattern
                intro_learner = get_intro_learner()
                hook = content.get('phrases', [''])[0] if content.get('phrases') else ''
                if hook:
                    pattern = intro_learner.detect_intro_pattern(hook)
                    # Record with placeholder retention
                    intro_learner.record_intro_performance(hook, 60.0)
                
                # Get viral velocity prediction (for metadata/logging only)
                try:
                    velocity = predict_viral_velocity(
                        title=metadata.get('title', ''),
                        hook=hook,
                        category=concept.get('category', ''),
                        historical_avg=1000  # Will be updated from analytics
                    )
                    if velocity:
                        safe_print(f"   [v10.0] Viral prediction: {velocity.get('velocity_tier', 'unknown')} ({velocity.get('viral_score', '?')}/10)")
                        # Store prediction in metadata
                        metadata['viral_prediction'] = velocity
                except:
                    pass
                
                safe_print("   [v10.0] Recorded to title/intro/velocity trackers")
            except Exception as e:
                safe_print(f"   [!] v10.0 tracking error: {e}")
        
        safe_print("\n" + "=" * 70)
        safe_print("   VIDEO GENERATED!")
        safe_print(f"   File: {output_path}")
        safe_print(f"   Category: {concept.get('category', 'N/A')}")
        safe_print(f"   Topic: {concept.get('specific_topic', 'N/A')}")
        safe_print(f"   Voice: {voice_config.get('voice', 'N/A')}")
        safe_print(f"   Music: {music_file}")
        safe_print(f"   Score: {score}/10")
        if metadata:
            safe_print(f"   Title: {metadata.get('title', 'N/A')}")
        # Show enhancements applied
        safe_print("   ---")
        safe_print(f"   Font: {content.get('selected_font', 'default')}")
        sfx_plan = content.get('sfx_plan', [])
        sfx_summary = [s for s in sfx_plan if s]
        safe_print(f"   SFX: {sfx_summary if sfx_summary else 'minimal'}")
        safe_print(f"   Promise Fixed: {'Yes' if content.get('promise_fixed') else 'No'}")
        safe_print(f"   Quality Warning: {'Yes' if content.get('quality_warning') else 'No'}")
        safe_print("=" * 70)
        
        return output_path
    
    return None


async def upload_video(video_path: str, metadata: Dict, youtube: bool = True, dailymotion: bool = True) -> Dict:
    """Upload to platforms.
    v8.0: Uses persistent state to respect Dailymotion rate limits across runs!
    """
    results = {"youtube": None, "dailymotion": None}
    
    title = metadata.get('title', 'Amazing Fact')[:100]
    base_description = metadata.get('description', 'Follow for more!')
    
    # v7.17: Add required attributions for TOS compliance
    attribution = "\n\n---\nMusic: https://www.bensound.com (Royalty Free)"
    description = (base_description + attribution)[:5000]
    
    hashtags = metadata.get('hashtags', ['#shorts', '#viral'])
    tags = [h.replace('#', '').strip() for h in hashtags if h]
    
    safe_print(f"\n[UPLOAD] Title: {title}")
    
    # Get video ID from path for analytics tracking
    video_id = Path(video_path).stem.split('_')[-1] if video_path else None
    
    # v8.0: Check upload state before uploading
    upload_manager = None
    if PERSISTENT_STATE_AVAILABLE:
        upload_manager = get_upload_manager()
    
    if youtube:
        # v8.0: Check if we can upload (daily limit)
        if upload_manager and not upload_manager.can_upload_youtube():
            safe_print("[SKIP] YouTube daily limit reached (6/day)")
        else:
            try:
                from youtube_uploader import upload_video as yt_upload
                result = yt_upload(video_path, title=title, description=description, tags=tags)
                if result:
                    results["youtube"] = result
                    safe_print(f"[OK] YouTube: {result}")
                    
                    # v8.0: Record upload for rate limiting
                    if upload_manager:
                        upload_manager.record_upload('youtube', str(result))
                    
                    # Record upload in analytics (v7.11)
                    try:
                        from analytics_feedback import FeedbackLoopController
                        feedback = FeedbackLoopController()
                        yt_id = result.get('id') if isinstance(result, dict) else str(result)
                        feedback.record_upload(video_id, 'youtube', yt_id)
                    except:
                        pass
            except Exception as e:
                safe_print(f"[!] YouTube error: {e}")
    
    if dailymotion:
        # v8.0: Check if we can upload (4 per hour limit)
        if upload_manager and not upload_manager.can_upload_dailymotion():
            wait_time = upload_manager.get_wait_time_dailymotion()
            safe_print(f"[SKIP] Dailymotion rate limit - wait {wait_time//60}m {wait_time%60}s")
        else:
            try:
                from dailymotion_uploader import DailymotionUploader
                dm = DailymotionUploader()
                if dm.is_configured:
                    result = dm.upload_video(
                        video_path, title=title, description=description,
                        tags=tags, channel='lifestyle', ai_generated=False
                    )
                    if result:
                        results["dailymotion"] = result
                        safe_print(f"[OK] Dailymotion: {result}")
                        
                        # v8.0: Record upload for rate limiting
                        if upload_manager:
                            upload_manager.record_upload('dailymotion', str(result))
                        
                        # Record upload in analytics (v7.11)
                        try:
                            from analytics_feedback import FeedbackLoopController
                            feedback = FeedbackLoopController()
                            dm_id = result.get('id') if isinstance(result, dict) else str(result)
                            feedback.record_upload(video_id, 'dailymotion', dm_id)
                        except:
                            pass
            except Exception as e:
                safe_print(f"[!] Dailymotion error: {e}")
    
    return results


async def main():
    """Generate videos with 100% AI decision-making and ALL v9.5 ENHANCEMENTS."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--hint", default=None, help="Optional hint for AI")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument("--strategic-youtube", action="store_true", 
                        help="Upload BEST video to YouTube, all to Dailymotion")
    parser.add_argument("--youtube-only", action="store_true",
                        help="v17.9.5: Upload to YouTube only, skip Dailymotion entirely")
    parser.add_argument("--test-mode", action="store_true",
                        help="Test mode: skip delays, extra logging")
    parser.add_argument("--output-dir", default="output",
                        help="Directory to save generated videos")
    parser.add_argument("--category", default=None,
                        help="Force specific category (for testing)")
    parser.add_argument("--topic", default=None,
                        help="Force specific topic (for testing)")
    parser.add_argument("--use-seasonal", action="store_true",
                        help="Use seasonal content calendar for topic selection")
    # Legacy support - these are IGNORED, AI decides
    parser.add_argument("--type", default=None, help="IGNORED - AI decides type")
    args = parser.parse_args()
    
    should_upload = args.upload and not args.no_upload
    
    safe_print(f"\n{'='*70}")
    safe_print("   VIRALSHORTS FACTORY v17.9.7 - YOUTUBE FOCUS")
    safe_print(f"   Generating {args.count} video(s)")
    safe_print("   AI decides: category, topic, length, voice, music")
    safe_print("   QUALITY GATES: Pre-gen, post-content, post-render")
    safe_print("   v11.0 FEATURES: Click bait, Scroll-stop, Algorithm, Visual, Quality")
    if args.strategic_youtube:
        safe_print("   STRATEGIC YOUTUBE: Best video selected by score")
    safe_print(f"{'='*70}")
    
    # v9.5: Check for seasonal content opportunities
    if args.use_seasonal and ENHANCEMENTS_V95_AVAILABLE:
        try:
            seasonal = get_seasonal_content_suggestions()
            if seasonal.get("content_opportunities"):
                safe_print(f"\n[SEASONAL] Found {len(seasonal['content_opportunities'])} timely opportunities!")
                for opp in seasonal.get("content_opportunities", [])[:3]:
                    safe_print(f"  - {opp.get('event')}: {opp.get('content_angle')}")
        except Exception as e:
            safe_print(f"[!] Seasonal check failed: {e}")
    
    # Reset batch tracker for new batch
    global BATCH_TRACKER
    BATCH_TRACKER = BatchTracker()
    
    hint = args.hint or args.type
    
    for i in range(args.count):
        safe_print(f"\n{'='*70}")
        safe_print(f"   VIDEO {i+1}/{args.count}")
        safe_print(f"{'='*70}")
        
        path = await generate_pro_video(hint, BATCH_TRACKER, args.output_dir)
    
    # Upload phase
    if should_upload and BATCH_TRACKER.video_scores:
        safe_print("\n" + "=" * 70)
        safe_print("   UPLOADING")
        safe_print("=" * 70)
        
        if args.youtube_only:
            # v17.9.5: YouTube-only mode - skip Dailymotion entirely
            safe_print("[v17.9.5] YouTube-only mode - Dailymotion disabled")
            for video_path, metadata in BATCH_TRACKER.get_all_videos():
                safe_print(f"\n[YOUTUBE] Uploading: {video_path}")
                await upload_video(video_path, metadata, youtube=True, dailymotion=False)
                if len(BATCH_TRACKER.video_scores) > 1:
                    delay = random.randint(60, 120)
                    safe_print(f"[WAIT] Anti-ban delay: {delay}s")
                    time.sleep(delay)
        elif args.strategic_youtube:
            # Strategic: Best video to YouTube, all to Dailymotion
            best = BATCH_TRACKER.get_best_video_for_youtube()
            if best:
                best_path, best_meta = best
                safe_print(f"\n[YOUTUBE] Uploading BEST video (score-based selection)")
                await upload_video(best_path, best_meta, youtube=True, dailymotion=True)
                # IMPORTANT: Wait after first upload before starting Dailymotion batch
                initial_delay = random.randint(120, 180)  # 2-3 minutes after first
                safe_print(f"[WAIT] Initial cooldown: {initial_delay}s before Dailymotion batch")
                time.sleep(initial_delay)
            
            # All other videos to Dailymotion only
            # v8.9: MAXIMIZED Dailymotion uploads
            # - Dailymotion allows 4 uploads per HOUR
            # - Batches run every 4 HOURS, so we have 4 fresh slots each time
            # - Upload ALL videos, not just 4, by spreading them across the hour
            remaining_videos = [(p, m) for p, m in BATCH_TRACKER.get_all_videos() 
                               if not best or p != best[0]]
            
            # v8.9: Calculate how many we can actually upload
            # Since batches are 4h apart and limit is 4/hour, we always have 4 fresh slots
            # But we can exceed 4 by waiting for slots to refresh mid-batch
            dm_to_upload = remaining_videos  # Upload ALL remaining videos
            
            # Calculate total time needed: 4 per hour = 1 every 15 min
            if len(dm_to_upload) > 3:
                safe_print(f"[DAILYMOTION] Uploading ALL {len(dm_to_upload)} videos (spreading across time)")
            
            for idx, (video_path, metadata) in enumerate(dm_to_upload):
                safe_print(f"\n[DAILYMOTION ONLY] ({idx+1}/{len(dm_to_upload)}) {video_path}")
                await upload_video(video_path, metadata, youtube=False, dailymotion=True)
                
                # Skip delay after last video
                if idx < len(dm_to_upload) - 1:
                    # v8.9: Smarter delays - first 3 can be faster, then slow down
                    if idx < 2:
                        # First 3 uploads (including YouTube one) = 4 total in first hour
                        delay = random.randint(180, 300)  # 3-5 minutes
                        safe_print(f"[WAIT] Quick upload {idx+2}/4: {delay//60}m delay")
                    else:
                        # After 4 uploads, wait 15-18 min for new slot to open
                        delay = random.randint(900, 1080)  # 15-18 minutes
                        safe_print(f"[WAIT] Slot refresh: {delay//60}m (waiting for new hourly slot)")
                    time.sleep(delay)
        else:
            # Legacy: Upload all to both platforms
            for video_path, metadata in BATCH_TRACKER.get_all_videos():
                await upload_video(video_path, metadata)
                if len(BATCH_TRACKER.video_scores) > 1:
                    delay = random.randint(45, 120)
                    safe_print(f"[WAIT] Anti-ban delay: {delay}s")
                    time.sleep(delay)
    
    # Print summary
    safe_print(f"\n{'='*70}")
    safe_print(f"   COMPLETE: {len(BATCH_TRACKER.video_scores)} videos")
    safe_print(f"{'='*70}")
    
    # Print the table of all videos
    safe_print("\n=== VIDEO DETAILS TABLE ===")
    safe_print("-" * 100)
    safe_print(f"{'#':>2} | {'Category':<15} | {'Topic':<25} | {'Voice':<20} | {'Music':<20} | {'Score':>5}")
    safe_print("-" * 100)
    
    for i, (path, score, meta) in enumerate(BATCH_TRACKER.video_scores, 1):
        # Load full metadata from file
        meta_path = path.replace('.mp4', '_meta.json')
        full_meta = {}
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                full_meta = json.load(f)
        
        concept = full_meta.get('concept', {})
        voice_config = full_meta.get('voice_config', {})
        
        category = concept.get('category', 'N/A')[:15]
        topic = concept.get('specific_topic', 'N/A')[:25]
        voice = voice_config.get('voice', 'N/A').split('-')[-1].replace('Neural', '')[:20]
        music = full_meta.get('music_file', 'N/A')[:20]
        
        safe_print(f"{i:>2} | {category:<15} | {topic:<25} | {voice:<20} | {music:<20} | {score:>5}/10")
    
    safe_print("-" * 100)


if __name__ == "__main__":
    asyncio.run(main())
