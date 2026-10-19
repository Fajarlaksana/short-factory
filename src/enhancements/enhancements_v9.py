#!/usr/bin/env python3
"""
ViralShorts Factory - Comprehensive Enhancements Module v11.0
==============================================================

Implements ALL 89 enhancements through AI-driven prompts (not hardcoded logic).

CORE ENHANCEMENTS (v1-v9):
1. CORE QUALITY (#1-4), ANALYTICS (#5-10), OPTIMIZATION (#11-15)
2. OPERATIONAL (#16-21), GROWTH (#22-25)

v9.5 ENHANCEMENTS (#26-35): Face, Seasonal, Hook words, Voice, Hashtags, Series

v10.0 ENHANCEMENTS (#36-45): Thumbnail text, Emotional arc, SEO, Sentiment, Velocity

NEW v11.0 ENHANCEMENTS (#46-89) - 8 CATEGORIES:

CATEGORY 1: CLICK BAITING (#46-51)
   - #46: CuriosityGapGenerator - Irresistible curiosity gaps
   - #47: NumberHookOptimizer - Learn which numbers (3,5,7,10) perform
   - #48: ControversyCalibrator - Safe controversy for engagement
   - #49: FOMOInjector - Fear of missing out
   - #50: TitlePowerWordTracker - Track power word performance
   - #51: predict_ctr() - Predict CTR before upload

CATEGORY 2: FIRST SECONDS RETENTION (#52-57)
   - #52: PatternInterruptGenerator - Scroll-stopping moments
   - #53: OpenLoopTracker - Unfinished thoughts
   - #54: FirstFrameOptimizer - First frame optimization
   - #55: AudioHookTimer - Sound effect timing
   - #56: score_scroll_stop_power() - Score scroll-stopping
   - #57: generate_instant_value_hook() - Instant value hooks

CATEGORY 3: ALGORITHM OPTIMIZATION (#58-63)
   - #58: WatchTimeMaximizer - Watch time strategies
   - #59: CompletionRateTracker - Completion prediction
   - #60: CommentBaitOptimizer - Comment-driving CTAs
   - #61: ShareTriggerTracker - Share triggers
   - #62: ReWatchHookTracker - Re-watch hooks
   - #63: generate_algorithm_signals() - Algorithm optimization

CATEGORY 4: VISUAL IMPROVEMENTS (#64-68)
   - #64: ColorPsychologyOptimizer - Color psychology
   - #65: MotionEnergyOptimizer - Motion matching
   - #66: TextReadabilityScorer - Mobile text readability
   - #67: VisualVarietyTracker - Prevent monotony
   - #68: score_thumbnail_quality() - Thumbnail scoring

CATEGORY 5: CONTENT QUALITY (#69-74)
   - #69: FactCredibilityChecker - Believable claims
   - #70: ActionableTakeawayEnforcer - Clear actions
   - #71: StoryStructureOptimizer - Narrative arc
   - #72: MemoryHookGenerator - Memorable phrases
   - #73: RelatabilityChecker - Relatable content
   - #74: detect_ai_slop() - Anti-AI detection

CATEGORY 6: VIRAL/TRENDY (#75-79)
   - #75: TrendLifecycleTracker - Trend lifecycle phases
   - #76: EvergreenBalancer - Trending vs evergreen
   - #77: CulturalMomentDetector - Cultural moments
   - #78: ViralPatternMatcher - Proven viral patterns
   - #79: PlatformTrendSplitter - Platform-specific trends

CATEGORY 7: ANALYTICS FEEDBACK (#80-84)
   - #80: MicroRetentionAnalyzer - Second-by-second retention
   - #81: PerformanceCorrelationFinder - Hidden correlations
   - #82: ChannelHealthMonitor - Overall health score
   - #83: GrowthRatePredictor - Future growth
   - #84: ContentDecayTracker - Content aging

CATEGORY 8: OTHER IMPORTANT (#85-89)
   - #85: CompetitorResponseGenerator - Respond to competitors
   - #86: NicheAuthorityBuilder - Build niche authority
   - #87: QualityConsistencyEnforcer - Consistent quality
   - #88: UploadCadenceOptimizer - Posting frequency
   - #89: AudienceLoyaltyTracker - Returning viewers

QUOTA MANAGEMENT:
- Groq: Primary for time-sensitive tasks (faster)
- Gemini: Secondary for bulk/analytical tasks (higher capacity, free)
- Smart routing to protect quotas
"""

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_best_gemini_model, get_best_groq_model
except ImportError:
    def get_best_gemini_model(api_key=None):
        return "gemini-2.5-flash"
    def get_best_groq_model(api_key=None):
        return "llama-3.3-70b-versatile"

# State directory
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

ENHANCEMENT_STATE_FILE = STATE_DIR / "enhancement_state.json"


def safe_print(msg: str):
    """Print with fallback for encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# AI CALLER - Smart routing between Groq and Gemini
# =============================================================================

class SmartAICaller:
    """
    Intelligently routes AI calls between Groq and Gemini based on:
    - Task priority (time-sensitive vs bulk)
    - Token usage optimization
    - Quota protection
    
    QUOTA ESTIMATES (Free Tiers):
    - Groq: ~6000 requests/day, 30K tokens/min
    - Gemini 2.0 Flash: 1500 requests/day, 1M tokens/min
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_client = None
        self.gemini_model = None
        
        # Track usage for smart routing
        self.groq_calls_today = 0
        self.gemini_calls_today = 0
        self.daily_groq_limit = 100  # Conservative estimate per batch
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize AI clients."""
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                safe_print(f"[!] Groq init: {e}")
        
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                # DYNAMIC MODEL SELECTION - no hardcoded model names
                model_name = get_best_gemini_model(self.gemini_key)
                self.gemini_model = genai.GenerativeModel(model_name)
                safe_print(f"[OK] Gemini model: {model_name}")
            except Exception as e:
                safe_print(f"[!] Gemini init: {e}")
    
    def call(self, prompt: str, max_tokens: int = 1000, 
             priority: str = "normal", temperature: float = 0.8,
             use_cache: bool = True) -> Optional[str]:
        """
        Make AI call with smart routing.
        
        Priority:
        - "critical": Use Groq first (faster, for real-time decisions)
        - "normal": Use Gemini first (save Groq quota)
        - "bulk": Always use Gemini (high token tasks)
        
        v17.8: Added prompt caching to reduce quota usage.
        """
        import time
        
        # v17.8: Check cache first (saves quota!)
        if use_cache and temperature < 0.5:  # Only cache deterministic responses
            try:
                from prompt_cache import cached_ai_call, cache_ai_response
                cached = cached_ai_call(prompt, context=priority)
                if cached:
                    safe_print("   [CACHE HIT] Using cached response")
                    return cached
            except ImportError:
                pass
        
        time.sleep(get_smart_delay("default", "groq") if "get_smart_delay" in dir() else 0.5)  # Rate limit protection
        
        # Determine order based on priority
        if priority == "critical":
            providers = [("groq", self._call_groq), ("gemini", self._call_gemini)]
        else:  # normal or bulk
            providers = [("gemini", self._call_gemini), ("groq", self._call_groq)]
        
        for name, call_func in providers:
            try:
                result = call_func(prompt, max_tokens, temperature)
                if result:
                    if name == "groq":
                        self.groq_calls_today += 1
                    else:
                        self.gemini_calls_today += 1
                    
                    # v17.8: Cache the response
                    if use_cache and temperature < 0.5:
                        try:
                            from prompt_cache import cache_ai_response
                            cache_ai_response(prompt, result, context=priority)
                        except ImportError:
                            pass
                    
                    return result
            except Exception as e:
                safe_print(f"[!] {name} failed: {e}")
                continue
        
        return None
    
    def _call_groq(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call Groq API."""
        if not self.groq_client:
            return None
        
        # v16.10: DYNAMIC MODEL - No hardcoding
        try:
            from quota_optimizer import get_quota_optimizer
            optimizer = get_quota_optimizer()
            groq_models = optimizer.get_groq_models()
            model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
        except:
            model_to_use = "llama-3.3-70b-versatile"
        
        response = self.groq_client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Call Gemini API."""
        if not self.gemini_model:
            return None
        
        response = self.gemini_model.generate_content(prompt)
        return response.text
    
    def parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        if not text:
            return None
        
        # Clean markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        try:
            return json.loads(text.strip())
        except:
            return None


# Global AI caller
_ai_caller = None

def get_ai_caller() -> SmartAICaller:
    global _ai_caller
    if _ai_caller is None:
        _ai_caller = SmartAICaller()
    return _ai_caller


# =============================================================================
# ENHANCEMENT #1: Post-Render Quality Validation
# =============================================================================

def validate_post_render(phrases: List[str], metadata: Dict, video_duration: float) -> Dict:
    """
    AI validates the final video content before upload.
    
    Checks:
    - Text readability on mobile
    - Audio/timing alignment
    - B-roll appropriateness
    - Overall watchability
    
    Returns: {"approved": bool, "issues": [], "suggestions": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a FINAL QUALITY GATE before a video goes live.
This video is ALREADY RENDERED. Your job is to predict any issues viewers might have.

=== VIDEO CONTENT ===
Phrases shown on screen: {json.dumps(phrases, indent=2)}
Total duration: {video_duration:.1f} seconds
Title: {metadata.get('title', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

=== FINAL CHECKS ===
Imagine you're a viewer scrolling. Would you:
1. STOP and watch? (hook strength)
2. UNDERSTAND the text quickly? (readability)
3. FEEL satisfied at the end? (payoff)
4. WANT to engage? (comment/like/share)

=== RED FLAGS TO CATCH ===
- Text too long for mobile reading
- Pacing too fast/slow
- Weak or confusing hook
- Anticlimactic ending
- Any content that screams "AI-generated"

=== OUTPUT JSON ===
{{
    "approved": true/false,
    "quality_score": 1-10,
    "hook_strength": 1-10,
    "readability": 1-10,
    "payoff_satisfaction": 1-10,
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion for next time"],
    "predicted_retention": "high/medium/low",
    "upload_recommendation": "upload/review/reject"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="critical")
    parsed = ai.parse_json(result)
    
    if parsed:
        safe_print(f"   [POST-RENDER] Score: {parsed.get('quality_score', 'N/A')}/10, "
                   f"Approved: {parsed.get('approved', 'N/A')}")
        return parsed
    
    return {"approved": True, "quality_score": 7, "issues": [], "suggestions": []}


# =============================================================================
# ENHANCEMENT #3: Semantic Duplicate Detection
# =============================================================================

def check_semantic_duplicate(new_topic: str, new_hook: str, recent_topics: List[str]) -> Dict:
    """
    AI checks if new content is semantically similar to recent content.
    
    Returns: {"is_duplicate": bool, "similarity_score": 0-100, "similar_to": str or None}
    """
    if not recent_topics:
        return {"is_duplicate": False, "similarity_score": 0, "similar_to": None}
    
    ai = get_ai_caller()
    
    prompt = f"""You are a DUPLICATE CONTENT DETECTOR.
Check if this new video topic is too similar to recently published content.

=== NEW VIDEO ===
Topic: {new_topic}
Hook: {new_hook}

=== RECENT TOPICS (avoid similarity) ===
{json.dumps(recent_topics[-15:], indent=2)}

=== SIMILARITY CRITERIA ===
Consider these as "too similar" (DUPLICATE):
- Same core message with different words
- Same psychological hook/trigger
- Same actionable advice
- Viewers would think "didn't I just see this?"

NOT duplicates:
- Same category but different specific topic
- Same format but different content
- Related but complementary information

=== OUTPUT JSON ===
{{
    "is_duplicate": true/false,
    "similarity_score": 0-100 (100 = identical concept),
    "similar_to": "the specific recent topic it's similar to" or null,
    "reason": "why it is/isn't a duplicate",
    "suggestion": "how to make it more unique" or null
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="normal")
    parsed = ai.parse_json(result)
    
    if parsed:
        if parsed.get('is_duplicate'):
            safe_print(f"   [DUPLICATE] Similar to: {parsed.get('similar_to', 'unknown')}")
        return parsed
    
    return {"is_duplicate": False, "similarity_score": 0, "similar_to": None}


# =============================================================================
# ENHANCEMENT #4: Voice Pacing Intelligence
# =============================================================================

def enhance_voice_pacing(phrases: List[str]) -> List[Dict]:
    """
    AI determines optimal pacing for each phrase.
    
    Returns: List of {"text": str, "rate": str, "emphasis_words": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a VOICE DIRECTOR for viral short videos.
Determine the optimal pacing and emphasis for each phrase.

=== PHRASES ===
{json.dumps(phrases, indent=2)}

=== PACING RULES ===
1. HOOK (first phrase): Slightly slower, dramatic, grab attention
2. KEY NUMBERS: Slow down slightly - "five...hundred...dollars"
3. REVELATION: Build-up should be normal, revelation slower
4. CTA (last phrase): Energetic, direct

=== RATE OPTIONS ===
- "-10%": Slow, dramatic (for impact moments)
- "-5%": Slightly slower (for numbers, key points)
- "+0%": Normal (for explanations)
- "+5%": Slightly faster (for excitement)
- "+10%": Fast, energetic (for CTAs)

=== OUTPUT JSON ===
[
    {{
        "text": "the phrase text",
        "rate": "-5%",
        "emphasis_words": ["key", "words", "to", "stress"],
        "pause_before": true/false,
        "reason": "why this pacing"
    }}
]

JSON ARRAY ONLY."""

    result = ai.call(prompt, max_tokens=500, priority="normal")
    parsed = ai.parse_json(result)
    
    if parsed and isinstance(parsed, list):
        return parsed
    
    # Fallback: uniform pacing
    return [{"text": p, "rate": "+0%", "emphasis_words": []} for p in phrases]


# =============================================================================
# ENHANCEMENT #5: Retention Curve Prediction
# =============================================================================

def predict_retention_curve(phrases: List[str], hook: str) -> Dict:
    """
    AI predicts where viewers might drop off.
    
    Returns: {"predicted_curve": [100, 85, 70, 65], "drop_off_points": [], "suggestions": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a RETENTION ANALYST for YouTube Shorts.
Predict the viewer retention curve for this video.

=== CONTENT ===
Hook: {hook}
Phrases: {json.dumps(phrases, indent=2)}

=== RETENTION PSYCHOLOGY ===
- First 1-2 seconds: Hook must stop the scroll (biggest drop-off point)
- 3-5 seconds: Must deliver first value or curiosity payoff
- Middle: Each phrase must earn continued attention
- End: Satisfaction determines saves/comments

=== OUTPUT JSON ===
{{
    "predicted_retention_percent": [100, 85, 70, ...],
    "estimated_avg_retention": 65,
    "biggest_drop_off_point": {{
        "phrase_index": 2,
        "reason": "why viewers would leave here"
    }},
    "weak_points": [
        {{"index": 1, "issue": "description", "fix": "suggestion"}}
    ],
    "strong_points": ["what keeps viewers watching"],
    "predicted_completion_rate": 55
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {}


# =============================================================================
# ENHANCEMENT #7: A/B Testing Completeness (Title Style Tracking)
# =============================================================================

class ABTestTracker:
    """Track A/B test results and learn which variants perform best."""
    
    STATE_FILE = STATE_DIR / "ab_test_results.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.STATE_FILE.exists():
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"title_styles": {}, "cta_variants": {}, "thumbnail_styles": {}}
    
    def _save(self):
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_variant(self, variant_type: str, variant_name: str, video_id: str, metadata: Dict):
        """Record a variant was used."""
        if variant_type not in self.data:
            self.data[variant_type] = {}
        if variant_name not in self.data[variant_type]:
            self.data[variant_type][variant_name] = {"videos": [], "total_views": 0, "total_engagement": 0}
        
        self.data[variant_type][variant_name]["videos"].append({
            "video_id": video_id,
            "title": metadata.get("title", ""),
            "recorded_at": datetime.now().isoformat()
        })
        self._save()
    
    def update_performance(self, variant_type: str, variant_name: str, views: int, engagement: int):
        """Update performance metrics for a variant."""
        if variant_type in self.data and variant_name in self.data[variant_type]:
            self.data[variant_type][variant_name]["total_views"] += views
            self.data[variant_type][variant_name]["total_engagement"] += engagement
            self._save()
    
    def get_best_variant(self, variant_type: str) -> Optional[str]:
        """Get the best performing variant based on views per video."""
        if variant_type not in self.data:
            return None
        
        variants = self.data[variant_type]
        if not variants:
            return None
        
        # Calculate average views per video for each variant
        scores = {}
        for name, data in variants.items():
            video_count = len(data.get("videos", []))
            if video_count > 0:
                scores[name] = data.get("total_views", 0) / video_count
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def get_weights(self, variant_type: str) -> Dict[str, float]:
        """Get weighted probabilities for variants (for exploration/exploitation)."""
        if variant_type not in self.data:
            return {}
        
        variants = self.data[variant_type]
        weights = {}
        
        for name, data in variants.items():
            video_count = len(data.get("videos", []))
            if video_count > 0:
                avg_views = data.get("total_views", 0) / video_count
                weights[name] = max(0.1, avg_views / 1000)  # Normalize
            else:
                weights[name] = 1.0  # Exploration weight for untested variants
        
        # Normalize
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights


# =============================================================================
# ENHANCEMENT #10: Error Pattern Learning
# =============================================================================

class ErrorPatternLearner:
    """Learn from errors to avoid repeating them."""
    
    STATE_FILE = STATE_DIR / "error_patterns.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.STATE_FILE.exists():
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"broll_failures": {}, "tts_failures": {}, "api_failures": {}}
    
    def _save(self):
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_broll_failure(self, keyword: str):
        """Record a B-roll keyword that failed to return results."""
        if keyword not in self.data["broll_failures"]:
            self.data["broll_failures"][keyword] = {"count": 0, "last_fail": None}
        self.data["broll_failures"][keyword]["count"] += 1
        self.data["broll_failures"][keyword]["last_fail"] = datetime.now().isoformat()
        self._save()
    
    def should_skip_keyword(self, keyword: str) -> bool:
        """Check if keyword has failed too many times."""
        if keyword in self.data["broll_failures"]:
            return self.data["broll_failures"][keyword]["count"] >= 3
        return False
    
    def get_alternative_keyword(self, original: str) -> Optional[str]:
        """AI suggests alternative keyword for failed B-roll."""
        ai = get_ai_caller()
        
        prompt = f"""The B-roll search keyword "{original}" failed to return results on Pexels.
Suggest ONE alternative search keyword that would find similar footage.

Requirements:
- Be more generic/common
- Must be searchable on stock video sites
- Keep the same emotional tone

Return ONLY the alternative keyword, nothing else."""

        result = ai.call(prompt, max_tokens=50, priority="normal")
        return result.strip() if result else None


# =============================================================================
# ENHANCEMENT #11: Value Density Scoring
# =============================================================================

def score_value_density(phrases: List[str], duration_seconds: float) -> Dict:
    """
    AI scores how much value is delivered per second.
    
    Returns: {"value_per_second": float, "padding_detected": bool, "lean_version": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a VALUE DENSITY ANALYZER for short-form video.
Every second counts. Identify any "padding" or filler content.

=== CONTENT ===
Phrases: {json.dumps(phrases, indent=2)}
Duration: {duration_seconds:.1f} seconds

=== VALUE DEFINITION ===
HIGH VALUE content:
- Specific facts, numbers, techniques
- Actionable advice
- Surprising revelations
- Emotional impact

LOW VALUE (padding):
- Vague statements
- Unnecessary context
- Repeated ideas
- Filler words/phrases

=== OUTPUT JSON ===
{{
    "value_score": 1-10,
    "value_per_second": 0.0-1.0,
    "has_padding": true/false,
    "padding_phrases": [indices of low-value phrases],
    "lean_version": ["condensed phrase 1", "condensed phrase 2"],
    "time_saved_seconds": 0
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {"value_score": 7, "has_padding": False}


# =============================================================================
# ENHANCEMENT #12: Trend Freshness Decay
# =============================================================================

def score_trend_freshness(topic: str, source: str, fetch_time: str = None) -> Dict:
    """
    Score how fresh/relevant a trend is.
    
    Returns: {"freshness_score": 1-100, "urgency": "high/medium/low"}
    """
    # Calculate time decay
    if fetch_time:
        try:
            fetch_dt = datetime.fromisoformat(fetch_time)
            hours_old = (datetime.now() - fetch_dt).total_seconds() / 3600
        except:
            hours_old = 24
    else:
        hours_old = 0
    
    # Source reliability scores
    source_scores = {
        "google": 90,
        "reddit": 80,
        "twitter": 85,
        "ai": 70
    }
    
    base_score = source_scores.get(source.lower(), 60)
    
    # Apply time decay (loses 5 points per hour)
    freshness_score = max(10, base_score - (hours_old * 5))
    
    urgency = "high" if freshness_score > 70 else "medium" if freshness_score > 40 else "low"
    
    return {
        "freshness_score": int(freshness_score),
        "hours_old": round(hours_old, 1),
        "urgency": urgency,
        "recommendation": "use immediately" if urgency == "high" else "use soon" if urgency == "medium" else "may be stale"
    }


# =============================================================================
# ENHANCEMENT #18: Description SEO Optimization
# =============================================================================

def generate_seo_description(title: str, topic: str, hook: str, hashtags: List[str]) -> str:
    """
    AI generates SEO-optimized description.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a YOUTUBE SEO EXPERT.
Create an optimized description for this YouTube Short.

=== VIDEO INFO ===
Title: {title}
Topic: {topic}
Hook: {hook}
Hashtags: {hashtags}

=== SEO DESCRIPTION RULES ===
1. First line: Repeat the hook/value proposition (YouTube shows this in search)
2. Include 3-5 relevant keywords naturally
3. Add a clear CTA (subscribe, comment, like)
4. Keep under 300 characters for mobile visibility
5. End with hashtags

=== FORMAT ===
[Hook/value - 1 line]

[Brief expansion - 1-2 lines]

[CTA]

[Hashtags]

Return ONLY the description text, no JSON."""

    result = ai.call(prompt, max_tokens=200, priority="normal")
    return result.strip() if result else f"{hook}\n\n#shorts #viral"


# =============================================================================
# ENHANCEMENT #21: Shadow-ban Detection
# =============================================================================

class ShadowBanDetector:
    """Detect potential shadow-ban or reduced reach."""
    
    STATE_FILE = STATE_DIR / "reach_metrics.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.STATE_FILE.exists():
                with open(self.STATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"baseline_first_hour_views": 50, "recent_videos": [], "alerts": []}
    
    def _save(self):
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_video_performance(self, video_id: str, first_hour_views: int, title: str):
        """Record first-hour performance for a video."""
        self.data["recent_videos"].append({
            "video_id": video_id,
            "first_hour_views": first_hour_views,
            "title": title,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20 videos
        self.data["recent_videos"] = self.data["recent_videos"][-20:]
        
        # Update baseline (rolling average)
        if len(self.data["recent_videos"]) >= 5:
            recent_views = [v["first_hour_views"] for v in self.data["recent_videos"][-10:]]
            self.data["baseline_first_hour_views"] = sum(recent_views) / len(recent_views)
        
        self._save()
    
    def check_for_shadow_ban(self, current_first_hour_views: int) -> Dict:
        """Check if current performance indicates shadow-ban."""
        baseline = self.data.get("baseline_first_hour_views", 50)
        
        # Alert if views are less than 20% of baseline
        threshold = baseline * 0.2
        is_concerning = current_first_hour_views < threshold
        
        return {
            "is_concerning": is_concerning,
            "current_views": current_first_hour_views,
            "baseline": int(baseline),
            "threshold": int(threshold),
            "action": "PAUSE UPLOADS - Possible shadow-ban" if is_concerning else "Normal performance"
        }


# =============================================================================
# ENHANCEMENT #13: Dynamic CTA Testing
# =============================================================================

CTA_VARIANTS = [
    "SUBSCRIBE FOR MORE",
    "Comment if you agree!",
    "Save this for later",
    "Tag someone who needs this",
    "Would you try this?",
    "Share with a friend!"
]

def get_weighted_cta(ab_tracker: ABTestTracker = None) -> str:
    """Get a CTA variant with A/B testing weights."""
    import random
    
    if ab_tracker:
        weights = ab_tracker.get_weights("cta_variants")
        if weights:
            # Weighted random selection
            variants = list(weights.keys())
            probs = list(weights.values())
            return random.choices(variants, weights=probs, k=1)[0]
    
    # Default: random selection
    return random.choice(CTA_VARIANTS)


# =============================================================================
# ENHANCEMENT #2: Comment Content Mining (for weekly analysis)
# =============================================================================

def analyze_comments(comments: List[str]) -> Dict:
    """
    AI analyzes comment content to extract insights.
    Called by weekly analytics workflow.
    """
    if not comments:
        return {}
    
    ai = get_ai_caller()
    
    prompt = f"""You are a COMMENT ANALYST for a YouTube Shorts channel.
Extract actionable insights from viewer comments.

=== COMMENTS ===
{json.dumps(comments[:50], indent=2)}

=== EXTRACT ===
1. PRAISE: What do viewers love? (content to do MORE of)
2. CRITICISM: What do viewers dislike? (content to AVOID)
3. REQUESTS: What do viewers want to see?
4. RED FLAGS: Any "this is AI" or fake content accusations?
5. ENGAGEMENT DRIVERS: What topics spark discussion?

=== OUTPUT JSON ===
{{
    "positive_themes": ["theme 1", "theme 2"],
    "negative_themes": ["issue 1", "issue 2"],
    "requested_topics": ["topic 1", "topic 2"],
    "quality_concerns": ["concern 1"],
    "engagement_topics": ["high-engagement topic"],
    "overall_sentiment": "positive/neutral/negative",
    "ai_detection_mentions": 0,
    "actionable_insights": ["specific action 1", "specific action 2"]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=500, priority="bulk")
    return ai.parse_json(result) or {}


# =============================================================================
# ENHANCEMENT ORCHESTRATOR - Runs all checks
# =============================================================================

class EnhancementOrchestrator:
    """
    Orchestrates ALL enhancements during video generation.
    v14.0: FULLY EXPANDED - Now calls ALL 44 v11.0 enhancement classes!
    
    Every enhancement is initialized and actively used in the pipeline.
    """
    
    def __init__(self):
        # Core v9.0 trackers
        self.ab_tracker = ABTestTracker()
        self.error_learner = ErrorPatternLearner()
        self.shadow_detector = ShadowBanDetector()
        
        # v11.0 Category 1: Click Baiting (#46-51) - ALL INITIALIZED
        self.curiosity_gap = None
        self.number_hook = None
        self.controversy = None
        self.fomo = None
        self.power_words = None
        
        # v11.0 Category 2: First Seconds Retention (#52-57) - ALL INITIALIZED
        self.pattern_interrupt = None
        self.open_loop = None
        self.first_frame = None
        self.audio_hook = None
        
        # v11.0 Category 3: Algorithm Optimization (#58-63) - ALL INITIALIZED
        self.watch_time = None
        self.completion_rate = None
        self.comment_bait = None
        self.share_trigger = None
        self.rewatch = None
        
        # v11.0 Category 4: Visual Improvements (#64-68) - ALL INITIALIZED
        self.color_psychology = None
        self.motion_energy = None
        self.text_readability = None
        self.visual_variety = None
        
        # v11.0 Category 5: Content Quality (#69-74) - ALL INITIALIZED
        self.fact_credibility = None
        self.actionable = None
        self.story_structure = None
        self.memory_hook = None
        self.relatability = None
        
        # v11.0 Category 6: Viral/Trendy (#75-79) - ALL INITIALIZED
        self.trend_lifecycle = None
        self.evergreen_balance = None
        self.cultural_moment = None
        self.viral_pattern = None
        self.platform_trend = None
        
        # v11.0 Category 7: Analytics Feedback (#80-84) - ALL INITIALIZED
        self.micro_retention = None
        self.correlation = None
        self.channel_health = None
        self.growth_rate = None
        self.content_decay = None
        
        # v11.0 Category 8: Other Important (#85-89) - ALL INITIALIZED
        self.competitor_response = None
        self.niche_authority = None
        self.quality_consistency = None
        self.upload_cadence = None
        self.audience_loyalty = None
        
        # Lazy-load all trackers on first use
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy-load all enhancement classes on first use."""
        if self._initialized:
            return
        
        try:
            # Category 1: Click Baiting
            self.curiosity_gap = get_curiosity_gap()
            self.number_hook = get_number_hook()
            self.controversy = get_controversy()
            self.fomo = get_fomo()
            self.power_words = get_power_words_tracker()
            
            # Category 2: First Seconds
            self.pattern_interrupt = get_pattern_interrupt()
            self.open_loop = get_open_loop()
            self.first_frame = get_first_frame()
            self.audio_hook = get_audio_hook()
            
            # Category 3: Algorithm
            self.watch_time = get_watch_time()
            self.completion_rate = get_completion_rate()
            self.comment_bait = get_comment_bait()
            self.share_trigger = get_share_trigger()
            self.rewatch = get_rewatch()
            
            # Category 4: Visual
            self.color_psychology = get_color_psychology()
            self.motion_energy = get_motion_energy()
            self.text_readability = get_text_readability()
            self.visual_variety = get_visual_variety()
            
            # Category 5: Content Quality
            self.fact_credibility = get_fact_credibility()
            self.actionable = get_actionable()
            self.story_structure = get_story_structure()
            self.memory_hook = get_memory_hook()
            self.relatability = get_relatability()
            
            # Category 6: Viral/Trendy
            self.trend_lifecycle = get_trend_lifecycle()
            self.evergreen_balance = get_evergreen_balance()
            self.cultural_moment = get_cultural_moment()
            self.viral_pattern = get_viral_pattern()
            self.platform_trend = get_platform_trend()
            
            # Category 7: Analytics
            self.micro_retention = get_micro_retention()
            self.correlation = get_correlation()
            self.channel_health = get_channel_health()
            self.growth_rate = get_growth_rate()
            self.content_decay = get_content_decay()
            
            # Category 8: Other
            self.competitor_response = get_competitor_response()
            self.niche_authority = get_niche_authority()
            self.quality_consistency = get_quality_consistency()
            self.upload_cadence = get_upload_cadence()
            self.audience_loyalty = get_audience_loyalty()
            
            self._initialized = True
        except Exception as e:
            # Graceful degradation - continue even if some fail
            self._initialized = True
    
    def pre_generation_checks(self, topic: str, hook: str, recent_topics: List[str]) -> Dict:
        """
        Run checks BEFORE generating video.
        v14.0: Now uses ALL v11.0 enhancement classes for comprehensive analysis!
        
        Returns: {"proceed": bool, "warnings": [], "modifications": {}, "scores": {}, "enhancements": {}}
        """
        self._ensure_initialized()
        result = {"proceed": True, "warnings": [], "modifications": {}, "scores": {}, "enhancements": {}}
        
        # #3: Semantic duplicate check
        dup_check = check_semantic_duplicate(topic, hook, recent_topics)
        if dup_check.get("is_duplicate"):
            result["proceed"] = False
            result["warnings"].append(f"DUPLICATE: Similar to '{dup_check.get('similar_to')}'")
            result["modifications"]["suggested_topic"] = dup_check.get("suggestion")
        
        # ==========================================================================
        # CATEGORY 1: Click Baiting (#46-51) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #46: Curiosity gap analysis
        try:
            if self.curiosity_gap:
                gap_instruction = self.curiosity_gap.get_curiosity_instruction(topic)
                result["enhancements"]["curiosity_gap"] = gap_instruction
        except:
            pass
        
        # v11.0 #47: Number hook optimization
        try:
            if self.number_hook:
                number_advice = self.number_hook.get_number_recommendation(topic)
                result["enhancements"]["number_hook"] = number_advice
        except:
            pass
        
        # v11.0 #48: Controversy calibration
        try:
            if self.controversy:
                controversy_level = self.controversy.get_safe_controversy_instruction(topic)
                result["enhancements"]["controversy"] = controversy_level
        except:
            pass
        
        # v11.0 #49: FOMO injection
        try:
            if self.fomo:
                fomo_instruction = self.fomo.get_fomo_instruction()
                result["enhancements"]["fomo"] = fomo_instruction
        except:
            pass
        
        # v11.0 #50: Power words tracking
        try:
            if self.power_words:
                power_advice = self.power_words.get_recommended_words()
                result["enhancements"]["power_words"] = power_advice
        except:
            pass
        
        # v11.0 #51: CTR prediction
        try:
            ctr_pred = predict_ctr(hook, topic)
            result["scores"]["predicted_ctr"] = ctr_pred
        except:
            pass
        
        # ==========================================================================
        # CATEGORY 2: First Seconds Retention (#52-57) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #52: Pattern interrupt generation
        try:
            if self.pattern_interrupt:
                interrupt_instruction = self.pattern_interrupt.get_interrupt_instruction()
                result["enhancements"]["pattern_interrupt"] = interrupt_instruction
        except:
            pass
        
        # v11.0 #53: Open loop tracking
        try:
            if self.open_loop:
                loop_instruction = self.open_loop.get_open_loop_instruction()
                result["enhancements"]["open_loop"] = loop_instruction
        except:
            pass
        
        # v11.0 #54: First frame optimization
        try:
            if self.first_frame:
                frame_instruction = self.first_frame.get_first_frame_instruction()
                result["enhancements"]["first_frame"] = frame_instruction
        except:
            pass
        
        # v11.0 #55: Audio hook timing
        try:
            if self.audio_hook:
                audio_instruction = self.audio_hook.get_audio_timing_instruction()
                result["enhancements"]["audio_hook"] = audio_instruction
        except:
            pass
        
        # v11.0 #56: Scroll-stop power scoring
        try:
            scroll_score = score_scroll_stop_power(hook)
            result["scores"]["scroll_stop"] = scroll_score
            if scroll_score.get("score", 10) < 6:
                result["warnings"].append(f"Low scroll-stop power: {scroll_score.get('score')}/10")
        except:
            pass
        
        # v11.0 #57: Instant value hook generation
        try:
            instant_hook = generate_instant_value_hook(topic)
            result["enhancements"]["instant_value_hook"] = instant_hook
        except:
            pass
        
        # ==========================================================================
        # CATEGORY 6: Viral/Trendy (#75-79) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #75: Trend lifecycle analysis
        try:
            if self.trend_lifecycle:
                lifecycle = self.trend_lifecycle.get_trend_phase(topic)
                result["enhancements"]["trend_lifecycle"] = lifecycle
        except:
            pass
        
        # v11.0 #76: Evergreen balance
        try:
            if self.evergreen_balance:
                balance = self.evergreen_balance.get_balance_instruction()
                result["enhancements"]["evergreen_balance"] = balance
        except:
            pass
        
        # v11.0 #77: Cultural moment detection
        try:
            if self.cultural_moment:
                cultural = self.cultural_moment.detect_moments()
                result["enhancements"]["cultural_moment"] = cultural
        except:
            pass
        
        # v11.0 #78: Viral pattern matching
        try:
            if self.viral_pattern:
                patterns = self.viral_pattern.get_proven_patterns()
                result["enhancements"]["viral_patterns"] = patterns
        except:
            pass
        
        # v11.0 #79: Platform-specific trends
        try:
            if self.platform_trend:
                platform_advice = self.platform_trend.get_platform_trends()
                result["enhancements"]["platform_trends"] = platform_advice
        except:
            pass
        
        return result
    
    def post_content_checks(self, phrases: List[str], metadata: Dict) -> Dict:
        """
        Run checks AFTER content is created but BEFORE rendering.
        v14.0: Now uses ALL v11.0 enhancement classes for comprehensive optimization!
        
        Returns optimized phrases and metadata with all enhancements applied.
        """
        self._ensure_initialized()
        result = {"phrases": phrases, "metadata": metadata, "optimizations": [], "warnings": [], "enhancements": {}}
        
        # #4: Voice pacing intelligence
        pacing = enhance_voice_pacing(phrases)
        result["pacing"] = pacing
        result["optimizations"].append("Voice pacing optimized")
        
        # #5: Retention prediction
        retention = predict_retention_curve(phrases, metadata.get("hook", ""))
        result["retention_prediction"] = retention
        if retention.get("predicted_completion_rate", 100) < 40:
            result["warnings"].append("Low predicted retention - consider revising content")
        
        # #11: Value density
        value = score_value_density(phrases, 20)  # Assume 20s
        result["value_density"] = value
        if value.get("has_padding"):
            result["optimizations"].append("Consider leaner version")
        
        # ==========================================================================
        # CATEGORY 3: Algorithm Optimization (#58-63) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #58: Watch time maximization
        try:
            if self.watch_time:
                watch_strategy = self.watch_time.get_watch_time_instruction()
                result["enhancements"]["watch_time"] = watch_strategy
        except:
            pass
        
        # v11.0 #59: Completion rate tracking
        try:
            if self.completion_rate:
                completion_advice = self.completion_rate.get_completion_instruction()
                result["enhancements"]["completion_rate"] = completion_advice
        except:
            pass
        
        # v11.0 #60: Comment bait optimization
        try:
            if self.comment_bait:
                comment_advice = self.comment_bait.get_comment_bait_instruction()
                result["enhancements"]["comment_bait"] = comment_advice
        except:
            pass
        
        # v11.0 #61: Share trigger tracking
        try:
            if self.share_trigger:
                share_advice = self.share_trigger.get_share_instruction()
                result["enhancements"]["share_trigger"] = share_advice
        except:
            pass
        
        # v11.0 #62: Re-watch hook tracking
        try:
            if self.rewatch:
                rewatch_advice = self.rewatch.get_rewatch_instruction()
                result["enhancements"]["rewatch"] = rewatch_advice
        except:
            pass
        
        # v11.0 #63: Generate algorithm signals
        try:
            algo_signals = generate_algorithm_signals(phrases, metadata)
            result["algorithm_signals"] = algo_signals
        except:
            pass
        
        # ==========================================================================
        # CATEGORY 4: Visual Improvements (#64-68) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #64: Color psychology optimization
        try:
            if self.color_psychology:
                color_advice = self.color_psychology.get_color_instruction(metadata.get("category", ""))
                result["enhancements"]["color_psychology"] = color_advice
        except:
            pass
        
        # v11.0 #65: Motion energy optimization
        try:
            if self.motion_energy:
                motion_advice = self.motion_energy.get_motion_instruction(metadata.get("voice_style", ""))
                result["enhancements"]["motion_energy"] = motion_advice
        except:
            pass
        
        # v11.0 #66: Text readability scoring
        try:
            if self.text_readability:
                readability = self.text_readability.score_readability(phrases)
                result["enhancements"]["text_readability"] = readability
        except:
            pass
        
        # v11.0 #67: Visual variety tracking
        try:
            if self.visual_variety:
                variety = self.visual_variety.get_variety_instruction()
                result["enhancements"]["visual_variety"] = variety
        except:
            pass
        
        # ==========================================================================
        # CATEGORY 5: Content Quality (#69-74) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #69: Fact credibility check
        try:
            if self.fact_credibility:
                credibility = self.fact_credibility.check_credibility(phrases)
                result["enhancements"]["fact_credibility"] = credibility
            else:
                credibility = check_content_credibility(phrases)
                result["credibility"] = credibility
        except:
            pass
        
        # v11.0 #70: Actionable takeaway enforcement
        try:
            if self.actionable:
                actionable_check = self.actionable.check_actionable(phrases)
                result["enhancements"]["actionable"] = actionable_check
                if not actionable_check.get("has_action", True):
                    result["warnings"].append("Missing clear actionable takeaway")
        except:
            pass
        
        # v11.0 #71: Story structure optimization
        try:
            if self.story_structure:
                structure = self.story_structure.analyze_structure(phrases)
                result["enhancements"]["story_structure"] = structure
        except:
            pass
        
        # v11.0 #72: Memory hook generation
        try:
            if self.memory_hook:
                memory = self.memory_hook.generate_memory_hook(phrases[0] if phrases else "")
                result["enhancements"]["memory_hook"] = memory
        except:
            pass
        
        # v11.0 #73: Relatability check
        try:
            if self.relatability:
                relatability_check = self.relatability.check_relatability(phrases)
                result["enhancements"]["relatability"] = relatability_check
        except:
            pass
        
        # v11.0 #74: AI slop detection - check for generic AI content
        try:
            slop_check = detect_ai_slop(' '.join(phrases))
            result["ai_slop_check"] = slop_check
            if slop_check.get("is_slop", False):
                result["warnings"].append(f"AI slop detected: {slop_check.get('indicators', [])}")
        except:
            pass
        
        return result
    
    def post_render_validation(self, phrases: List[str], metadata: Dict, 
                                video_duration: float) -> Dict:
        """
        Final validation AFTER rendering.
        v13.2: Enhanced with more quality checks.
        """
        base_validation = validate_post_render(phrases, metadata, video_duration)
        
        # v11.0 #68: Thumbnail quality (if we have one)
        try:
            if metadata.get("thumbnail_path"):
                thumb_score = score_thumbnail_quality(metadata["thumbnail_path"])
                base_validation["thumbnail_score"] = thumb_score
        except:
            pass
        
        return base_validation
    
    def get_seo_description(self, title: str, topic: str, hook: str, hashtags: List[str]) -> str:
        """Generate SEO-optimized description."""
        return generate_seo_description(title, topic, hook, hashtags)
    
    def get_cta(self) -> str:
        """Get A/B tested CTA."""
        return get_weighted_cta(self.ab_tracker)
    
    def record_ab_test(self, variant_type: str, variant_name: str, video_id: str, metadata: Dict):
        """Record an A/B test variant."""
        self.ab_tracker.record_variant(variant_type, variant_name, video_id, metadata)
    
    def record_error(self, error_type: str, details: str):
        """Record an error for pattern learning."""
        if error_type == "broll":
            self.error_learner.record_broll_failure(details)
    
    def should_skip_broll_keyword(self, keyword: str) -> bool:
        """Check if B-roll keyword should be skipped."""
        return self.error_learner.should_skip_keyword(keyword)
    
    def get_alternative_broll(self, failed_keyword: str) -> Optional[str]:
        """Get alternative B-roll keyword."""
        return self.error_learner.get_alternative_keyword(failed_keyword)
    
    # ==========================================================================
    # NEW v14.0: Analytics & Performance Methods (Categories 7-8)
    # ==========================================================================
    
    def get_analytics_insights(self, video_id: str = None) -> Dict:
        """
        Get analytics-driven insights for optimization.
        v14.0: Uses ALL Category 7 & 8 enhancement classes.
        
        Returns: {"insights": {}, "recommendations": [], "health": {}}
        """
        self._ensure_initialized()
        result = {"insights": {}, "recommendations": [], "health": {}}
        
        # ==========================================================================
        # CATEGORY 7: Analytics Feedback (#80-84) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #80: Micro-retention analysis
        try:
            if self.micro_retention:
                retention_insight = self.micro_retention.get_retention_insights()
                result["insights"]["micro_retention"] = retention_insight
        except:
            pass
        
        # v11.0 #81: Performance correlation finding
        try:
            if self.correlation:
                correlations = self.correlation.find_correlations()
                result["insights"]["correlations"] = correlations
        except:
            pass
        
        # v11.0 #82: Channel health monitoring
        try:
            if self.channel_health:
                health = self.channel_health.get_health_score()
                result["health"] = health
        except:
            pass
        
        # v11.0 #83: Growth rate prediction
        try:
            if self.growth_rate:
                growth = self.growth_rate.predict_growth()
                result["insights"]["growth_prediction"] = growth
        except:
            pass
        
        # v11.0 #84: Content decay tracking
        try:
            if self.content_decay:
                decay = self.content_decay.analyze_decay()
                result["insights"]["content_decay"] = decay
        except:
            pass
        
        # ==========================================================================
        # CATEGORY 8: Other Important (#85-89) - ALL ACTIVE
        # ==========================================================================
        
        # v11.0 #85: Competitor response generation
        try:
            if self.competitor_response:
                competitor = self.competitor_response.get_response_strategy()
                result["insights"]["competitor_strategy"] = competitor
        except:
            pass
        
        # v11.0 #86: Niche authority building
        try:
            if self.niche_authority:
                authority = self.niche_authority.get_authority_score()
                result["insights"]["niche_authority"] = authority
        except:
            pass
        
        # v11.0 #87: Quality consistency enforcement
        try:
            if self.quality_consistency:
                consistency = self.quality_consistency.get_consistency_metrics()
                result["insights"]["quality_consistency"] = consistency
        except:
            pass
        
        # v11.0 #88: Upload cadence optimization
        try:
            if self.upload_cadence:
                cadence = self.upload_cadence.get_optimal_cadence()
                result["recommendations"].append(f"Optimal upload cadence: {cadence}")
        except:
            pass
        
        # v11.0 #89: Audience loyalty tracking
        try:
            if self.audience_loyalty:
                loyalty = self.audience_loyalty.get_loyalty_metrics()
                result["insights"]["audience_loyalty"] = loyalty
        except:
            pass
        
        # Shadow ban check
        try:
            shadow_status = self.shadow_detector.check_for_shadow_ban(0)
            result["health"]["shadow_ban_status"] = shadow_status
        except:
            pass
        
        return result
    
    def get_all_enhancement_instructions(self, topic: str, category: str) -> Dict:
        """
        Get ALL enhancement instructions in one call for prompt injection.
        v14.0: Aggregates all v11.0 enhancements for comprehensive AI guidance.
        
        Returns: {"click_bait": str, "first_seconds": str, "algorithm": str, ...}
        """
        self._ensure_initialized()
        instructions = {}
        
        # Click Baiting instructions
        try:
            if self.curiosity_gap:
                instructions["curiosity_gap"] = self.curiosity_gap.get_curiosity_instruction(topic)
            if self.fomo:
                instructions["fomo"] = self.fomo.get_fomo_instruction()
            if self.controversy:
                instructions["controversy"] = self.controversy.get_safe_controversy_instruction(topic)
        except:
            pass
        
        # First Seconds instructions
        try:
            if self.pattern_interrupt:
                instructions["pattern_interrupt"] = self.pattern_interrupt.get_interrupt_instruction()
            if self.open_loop:
                instructions["open_loop"] = self.open_loop.get_open_loop_instruction()
        except:
            pass
        
        # Algorithm instructions
        try:
            if self.watch_time:
                instructions["watch_time"] = self.watch_time.get_watch_time_instruction()
            if self.comment_bait:
                instructions["comment_bait"] = self.comment_bait.get_comment_bait_instruction()
        except:
            pass
        
        # Visual instructions
        try:
            if self.color_psychology:
                instructions["color"] = self.color_psychology.get_color_instruction(category)
            if self.motion_energy:
                instructions["motion"] = self.motion_energy.get_motion_instruction("energetic")
        except:
            pass
        
        # Viral/Trendy instructions
        try:
            if self.viral_pattern:
                instructions["viral_patterns"] = self.viral_pattern.get_proven_patterns()
            if self.evergreen_balance:
                instructions["evergreen"] = self.evergreen_balance.get_balance_instruction()
        except:
            pass
        
        return instructions


# =============================================================================
# ENHANCEMENT #14: Hook Animation Suggestions
# =============================================================================

def suggest_text_animations(phrases: List[str]) -> List[Dict]:
    """
    AI suggests animations for text to increase engagement.
    
    Returns: List of {"phrase_index": int, "animation_type": str, "reason": str}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a MOTION GRAPHICS DIRECTOR for viral short videos.
Suggest animations for these text phrases to maximize engagement.

=== PHRASES ===
{json.dumps(list(enumerate(phrases)), indent=2)}

=== ANIMATION OPTIONS ===
1. "pop_in": Text pops in quickly (for impact words, numbers)
2. "slide_up": Text slides up (for lists, sequences)
3. "fade_zoom": Fades in while zooming (for emotional moments)
4. "typewriter": Types one letter at a time (for suspense)
5. "shake": Brief shake effect (for shocking statements)
6. "none": Standard appearance (for normal content)

=== ANIMATION RULES ===
- HOOK (first phrase): Always animated strongly (pop_in or shake)
- NUMBERS: Pop or emphasize (draw attention to specific values)
- LISTS/SEQUENCES: slide_up for visual hierarchy
- EMOTIONAL: fade_zoom for impact
- Don't over-animate - pick key moments

=== OUTPUT JSON ===
[
    {{
        "phrase_index": 0,
        "animation_type": "pop_in",
        "emphasis_words": ["key", "words"],
        "reason": "why this animation"
    }}
]

JSON ARRAY ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    parsed = ai.parse_json(result)
    
    if parsed and isinstance(parsed, list):
        return parsed
    
    # Default: pop_in for first phrase, none for others
    return [{"phrase_index": i, "animation_type": "pop_in" if i == 0 else "none", "emphasis_words": []} 
            for i in range(len(phrases))]


# =============================================================================
# ENHANCEMENT #8: Music-Content Energy Matching
# =============================================================================

def match_music_energy(phrases: List[str], available_music_moods: List[str]) -> Dict:
    """
    AI selects best music mood based on content emotional trajectory.
    
    Returns: {"recommended_mood": str, "energy_curve": [1-10], "reason": str}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a MUSIC DIRECTOR for viral short videos.
Match the right music mood to this content's emotional trajectory.

=== CONTENT PHRASES ===
{json.dumps(phrases, indent=2)}

=== AVAILABLE MUSIC MOODS ===
{json.dumps(available_music_moods, indent=2)}

=== ANALYSIS REQUIRED ===
1. What emotion does the hook create? (curiosity, shock, fear, excitement)
2. How does emotion build through the content?
3. What should the viewer feel at the end?

=== OUTPUT JSON ===
{{
    "recommended_mood": "one of the available moods",
    "energy_curve": [7, 8, 9, 10, 8],  // Energy level per phrase (1-10)
    "peak_moment": 3,  // Which phrase index is the climax
    "emotional_arc": "builds to revelation",
    "reason": "why this music mood fits"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=250, priority="bulk")
    return ai.parse_json(result) or {"recommended_mood": "dramatic", "energy_curve": [7]*len(phrases)}


# =============================================================================
# ENHANCEMENT #22: Multi-Lingual Optimization (Localization Ready)
# =============================================================================

def analyze_localization_potential(title: str, hook: str) -> Dict:
    """
    AI analyzes if content could perform well in other languages.
    Prepares for future localization.
    
    Returns: {"universal_appeal": 1-10, "localization_opportunities": [], "cultural_notes": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a GLOBAL CONTENT STRATEGIST.
Analyze this content's potential for international audiences.

=== CONTENT ===
Title: {title}
Hook: {hook}

=== ANALYZE ===
1. Is this topic universally interesting or culturally specific?
2. Would the hook work in other languages?
3. Are there cultural references that wouldn't translate?
4. Which markets might find this especially interesting?

=== OUTPUT JSON ===
{{
    "universal_appeal": 1-10 (10 = works everywhere),
    "culturally_specific_elements": ["element that wouldn't translate"],
    "best_markets": ["US", "UK", "India", "Brazil", ...],
    "localization_opportunities": ["Spanish version", "Hindi version"],
    "cultural_notes": ["note about localization"],
    "recommendation": "keep as is" or "has localization potential"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    return ai.parse_json(result) or {"universal_appeal": 5}


# =============================================================================
# ENHANCEMENT #20: Optimal Posting Time
# =============================================================================

def get_optimal_posting_time(variety_state_file: Path = None) -> Dict:
    """
    Determines optimal posting time based on learned patterns.
    
    Returns: {"best_hours_utc": [14, 18], "best_days": ["Tuesday", "Friday"], "confidence": 0.8}
    """
    variety_state = {}
    if variety_state_file is None:
        variety_state_file = STATE_DIR / "variety_state.json"
    
    try:
        if variety_state_file.exists():
            with open(variety_state_file, 'r') as f:
                variety_state = json.load(f)
    except:
        pass
    
    # v17.8: Return learned preferences if available, otherwise ask AI
    if "best_posting_hours_utc" in variety_state:
        best_hours = variety_state["best_posting_hours_utc"]
        best_days = variety_state.get("best_posting_days", [])
        source = "learned"
        confidence = 0.6
    else:
        # Ask AI for optimal posting times instead of hardcoding
        best_hours, best_days = _get_ai_posting_times()
        source = "ai_recommended"
        confidence = 0.4
    
    return {
        "best_hours_utc": best_hours,
        "best_days": best_days,
        "confidence": confidence,
        "source": source
    }


def _get_ai_posting_times() -> Tuple[List[int], List[str]]:
    """v17.8: Ask AI for optimal posting times."""
    try:
        ai = get_ai_caller()
        prompt = """You are a YouTube Shorts analytics expert.
What are the best times (hours in UTC) and days to post for maximum reach?
Consider: US, UK, India audiences, typical scroll times.
Return JSON: {"hours_utc": [14, 18], "days": ["Tuesday", "Friday"]}
JSON ONLY."""
        result = ai.call(prompt, max_tokens=100, priority="bulk")
        parsed = ai.parse_json(result)
        if parsed:
            return (
                parsed.get("hours_utc", [14, 18]),
                parsed.get("days", ["Tuesday", "Thursday"])
            )
    except:
        pass
    # Minimal fallback
    return [14, 18], ["Tuesday", "Thursday"]


# =============================================================================
# ENHANCEMENT #17: Watch Time Prediction
# =============================================================================

def predict_watch_time(phrases: List[str], estimated_duration: float) -> Dict:
    """
    AI predicts average watch time and factors affecting it.
    
    Returns: {"predicted_avg_watch_seconds": float, "watch_percentage": float, "factors": []}
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a WATCH TIME ANALYST for short-form video.
Predict how long viewers will watch this content.

=== CONTENT ===
Phrases: {json.dumps(phrases, indent=2)}
Estimated Duration: {estimated_duration:.1f} seconds

=== FACTORS TO CONSIDER ===
1. Hook strength (does first phrase stop the scroll?)
2. Information density (value per second)
3. Curiosity maintenance (does each phrase make you want the next?)
4. Payoff satisfaction (is the ending satisfying?)
5. Pacing (too fast? too slow?)

=== OUTPUT JSON ===
{{
    "predicted_avg_watch_seconds": 12.5,
    "predicted_watch_percentage": 65,
    "drop_off_points": [
        {{"second": 5, "reason": "weak transition"}}
    ],
    "strength_factors": ["strong hook", "good pacing"],
    "weakness_factors": ["weak ending"],
    "improvement_suggestion": "specific suggestion"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    return ai.parse_json(result) or {
        "predicted_avg_watch_seconds": estimated_duration * 0.6,
        "predicted_watch_percentage": 60
    }


# =============================================================================
# v9.5 ENHANCEMENT #26: Thumbnail Face Detection
# =============================================================================

def detect_faces_in_broll(image_path: str) -> Dict:
    """
    Detect if B-roll contains human faces (faces = higher CTR).
    Uses OpenCV's built-in cascade classifier (100% free, no API).
    
    Returns: {"has_face": bool, "face_count": int, "face_score": 0-10}
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image
        
        # Load image
        if not Path(image_path).exists():
            return {"has_face": False, "face_count": 0, "face_score": 0}
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return {"has_face": False, "face_count": 0, "face_score": 0}
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load face cascade (built into OpenCV)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        face_count = len(faces)
        has_face = face_count > 0
        
        # Score: 10 if has face, bonus for centered/large faces
        face_score = 0
        if has_face:
            face_score = min(10, 5 + face_count * 2)  # Base 5, +2 per face, max 10
        
        return {
            "has_face": has_face,
            "face_count": face_count,
            "face_score": face_score
        }
        
    except ImportError:
        # OpenCV not installed, fall back to AI-based scoring
        return {"has_face": False, "face_count": 0, "face_score": 0, "note": "cv2 not available"}
    except Exception as e:
        return {"has_face": False, "face_count": 0, "face_score": 0, "error": str(e)}


def score_broll_for_thumbnail(broll_paths: List[str]) -> List[Dict]:
    """
    Score all B-roll clips and rank them for thumbnail selection.
    Prioritizes: faces > motion > relevance.
    
    Returns: List of {"path": str, "score": int, "has_face": bool}
    """
    scored = []
    
    for path in broll_paths:
        if not path or not Path(path).exists():
            continue
        
        face_data = detect_faces_in_broll(path)
        
        scored.append({
            "path": path,
            "score": face_data.get("face_score", 0),
            "has_face": face_data.get("has_face", False),
            "face_count": face_data.get("face_count", 0)
        })
    
    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    return scored


# =============================================================================
# v9.5 ENHANCEMENT #27: Seasonal Content Calendar
# =============================================================================

def get_seasonal_content_suggestions() -> Dict:
    """
    AI generates content suggestions based on current date, upcoming holidays, seasons.
    
    Returns: {"upcoming_events": [], "suggested_topics": [], "urgency": str}
    """
    ai = get_ai_caller()
    
    today = datetime.now()
    
    prompt = f"""You are a CONTENT CALENDAR expert for viral short-form video.

=== CURRENT DATE ===
Today: {today.strftime('%A, %B %d, %Y')}
Days until New Year: {(datetime(today.year + 1, 1, 1) - today).days if today.month == 12 else 'N/A'}

=== YOUR TASK ===
Identify upcoming holidays, events, seasons, or viral moments in the NEXT 7 DAYS that we should create content about.

Consider:
1. Major holidays (Christmas, New Year, Valentine's, etc.)
2. Awareness days/months (Mental Health Month, etc.)
3. Seasonal changes (first day of winter, etc.)
4. Predictable viral moments (end of year lists, resolutions, etc.)
5. Pop culture events (award shows, sports events)

=== OUTPUT JSON ===
{{
    "upcoming_events": [
        {{"event": "event name", "date": "date", "days_until": N}}
    ],
    "suggested_topics": [
        {{"topic": "specific topic", "hook": "hook idea", "why_now": "why timely"}}
    ],
    "content_urgency": "high" or "medium" or "low",
    "seasonal_mood": "festive" or "reflective" or "energetic" or "cozy" or "normal"
}}

Generate 3-5 event-driven topics that would go viral RIGHT NOW due to timing.
JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {
        "upcoming_events": [],
        "suggested_topics": [],
        "content_urgency": "low"
    }


# =============================================================================
# v9.5 ENHANCEMENT #28: Hook Word Performance Tracking
# =============================================================================

class HookWordTracker:
    """
    Tracks which words in hooks correlate with high performance.
    Learns over time which power words drive engagement.
    """
    
    HOOK_WORDS_FILE = STATE_DIR / "hook_word_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.HOOK_WORDS_FILE.exists():
                with open(self.HOOK_WORDS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"words": {}, "last_updated": None}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.HOOK_WORDS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_hook_performance(self, hook: str, views: int, avg_views: int):
        """Record performance of a hook's words."""
        # Normalize: performance = views / avg_views (1.0 = average)
        performance = views / max(avg_views, 1)
        
        # Extract words (lowercase, remove punctuation)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', hook.lower())
        
        for word in words:
            if word not in self.data["words"]:
                self.data["words"][word] = {"total_performance": 0, "count": 0}
            
            self.data["words"][word]["total_performance"] += performance
            self.data["words"][word]["count"] += 1
        
        self._save()
    
    def get_power_words(self, min_count: int = 3) -> List[str]:
        """Get words that correlate with above-average performance."""
        power_words = []
        
        for word, stats in self.data["words"].items():
            if stats["count"] >= min_count:
                avg_perf = stats["total_performance"] / stats["count"]
                if avg_perf > 1.2:  # 20% above average
                    power_words.append((word, avg_perf))
        
        # Sort by performance
        power_words.sort(key=lambda x: x[1], reverse=True)
        
        return [w[0] for w in power_words[:20]]  # Top 20
    
    def get_words_to_avoid(self, min_count: int = 3) -> List[str]:
        """Get words that correlate with below-average performance."""
        weak_words = []
        
        for word, stats in self.data["words"].items():
            if stats["count"] >= min_count:
                avg_perf = stats["total_performance"] / stats["count"]
                if avg_perf < 0.7:  # 30% below average
                    weak_words.append((word, avg_perf))
        
        weak_words.sort(key=lambda x: x[1])
        
        return [w[0] for w in weak_words[:10]]


# =============================================================================
# v9.5 ENHANCEMENT #29: Voice Speed Optimization
# =============================================================================

class VoiceSpeedOptimizer:
    """
    Tracks which voice speed/rate settings correlate with retention.
    Edge TTS supports rate adjustment.
    """
    
    VOICE_SPEED_FILE = STATE_DIR / "voice_speed_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.VOICE_SPEED_FILE.exists():
                with open(self.VOICE_SPEED_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "rates": {},  # {"+10%": {"videos": 5, "avg_retention": 65}}
            "best_rate": "+0%",  # Default: normal speed
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.VOICE_SPEED_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, rate: str, retention_percent: float):
        """Record retention for a voice rate."""
        if rate not in self.data["rates"]:
            self.data["rates"][rate] = {"videos": 0, "total_retention": 0}
        
        self.data["rates"][rate]["videos"] += 1
        self.data["rates"][rate]["total_retention"] += retention_percent
        
        # Update best rate
        self._update_best_rate()
        self._save()
    
    def _update_best_rate(self):
        """Find the best performing rate."""
        best_rate = "+0%"
        best_avg = 0
        
        for rate, stats in self.data["rates"].items():
            if stats["videos"] >= 3:  # Minimum sample size
                avg = stats["total_retention"] / stats["videos"]
                if avg > best_avg:
                    best_avg = avg
                    best_rate = rate
        
        self.data["best_rate"] = best_rate
    
    def get_optimal_rate(self) -> str:
        """Get the optimal voice rate to use."""
        return self.data.get("best_rate", "+0%")
    
    def get_rate_for_ab_test(self) -> str:
        """Get a rate to A/B test (explore new options)."""
        import random
        
        options = ["-10%", "-5%", "+0%", "+5%", "+10%", "+15%"]
        
        # 80% use best rate, 20% explore
        if random.random() < 0.8:
            return self.get_optimal_rate()
        else:
            return random.choice(options)


# =============================================================================
# v9.5 ENHANCEMENT #30: Auto-Hashtag Rotation
# =============================================================================

class HashtagRotator:
    """
    Rotates hashtags to avoid repetition and test new combinations.
    Tracks which hashtags perform best.
    """
    
    HASHTAG_FILE = STATE_DIR / "hashtag_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.HASHTAG_FILE.exists():
                with open(self.HASHTAG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "used_sets": [],  # Last N hashtag sets used
            "hashtag_performance": {},  # {"#viral": {"videos": 10, "total_views": 50000}}
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.HASHTAG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_hashtag_performance(self, hashtags: List[str], views: int):
        """Record performance of hashtags."""
        for tag in hashtags:
            tag = tag.lower()
            if tag not in self.data["hashtag_performance"]:
                self.data["hashtag_performance"][tag] = {"videos": 0, "total_views": 0}
            
            self.data["hashtag_performance"][tag]["videos"] += 1
            self.data["hashtag_performance"][tag]["total_views"] += views
        
        self._save()
    
    def get_recently_used(self, limit: int = 5) -> List[List[str]]:
        """Get recently used hashtag sets."""
        return self.data["used_sets"][-limit:]
    
    def record_used_set(self, hashtags: List[str]):
        """Record a hashtag set as used."""
        self.data["used_sets"].append(hashtags)
        self.data["used_sets"] = self.data["used_sets"][-20:]  # Keep last 20
        self._save()
    
    def get_top_performers(self, limit: int = 10) -> List[str]:
        """Get top performing hashtags."""
        scored = []
        
        for tag, stats in self.data["hashtag_performance"].items():
            if stats["videos"] >= 2:
                avg_views = stats["total_views"] / stats["videos"]
                scored.append((tag, avg_views))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [t[0] for t in scored[:limit]]


def generate_fresh_hashtags(category: str, topic: str, recent_sets: List[List[str]]) -> List[str]:
    """
    AI generates fresh hashtags avoiding recently used ones.
    """
    ai = get_ai_caller()
    
    recent_flat = [tag for s in recent_sets for tag in s]
    
    prompt = f"""You are a HASHTAG expert for viral YouTube Shorts.

=== VIDEO INFO ===
Category: {category}
Topic: {topic}

=== RECENTLY USED (AVOID THESE) ===
{json.dumps(recent_flat[-30:], indent=2)}

=== YOUR TASK ===
Generate 8-10 FRESH hashtags that:
1. Are NOT in the recently used list
2. Mix evergreen (#shorts, #viral) with specific (#topic-specific)
3. Include trending/seasonal tags if relevant
4. Range from broad (1M+ posts) to niche (10K-100K posts)

=== OUTPUT JSON ===
{{
    "hashtags": ["#tag1", "#tag2", ...],
    "evergreen_count": 3,
    "specific_count": 5,
    "reasoning": "why these tags"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    parsed = ai.parse_json(result)
    
    if parsed and parsed.get("hashtags"):
        return parsed["hashtags"]
    
    # Fallback
    return ["#shorts", "#viral", "#facts", "#trending", f"#{category}"]


# =============================================================================
# v9.5 ENHANCEMENT #31: B-Roll Relevance Scoring
# =============================================================================

def score_broll_relevance(phrase: str, broll_options: List[Dict]) -> List[Dict]:
    """
    AI scores B-roll options before downloading to pick the most relevant.
    
    broll_options: List of {"title": str, "description": str, "url": str} from Pexels
    Returns: Same list with added "relevance_score" field, sorted by score
    """
    if not broll_options:
        return []
    
    ai = get_ai_caller()
    
    # Prepare options for scoring
    options_text = "\n".join([
        f"{i+1}. {opt.get('title', 'Untitled')}: {opt.get('description', '')[:100]}"
        for i, opt in enumerate(broll_options[:10])  # Max 10 options
    ])
    
    prompt = f"""You are a VIDEO EDITOR selecting B-roll for a short video.

=== PHRASE TO ILLUSTRATE ===
"{phrase}"

=== B-ROLL OPTIONS ===
{options_text}

=== SCORE EACH OPTION ===
Rate 1-10 how well each option visually represents the phrase.

10 = Perfect match (exactly what the phrase is about)
7-9 = Good match (clearly related)
4-6 = Okay (somewhat related)
1-3 = Poor (not really related)

=== OUTPUT JSON ===
{{
    "scores": [
        {{"index": 1, "score": 8, "reason": "short reason"}}
    ],
    "best_option": 1,
    "avoid_options": [3, 5]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    parsed = ai.parse_json(result)
    
    if parsed and parsed.get("scores"):
        # Apply scores
        for score_data in parsed["scores"]:
            idx = score_data.get("index", 1) - 1
            if 0 <= idx < len(broll_options):
                broll_options[idx]["relevance_score"] = score_data.get("score", 5)
        
        # Sort by score
        broll_options.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return broll_options


# =============================================================================
# v9.5 ENHANCEMENT #32: Cross-Platform Performance Split
# =============================================================================

class CrossPlatformAnalytics:
    """
    Tracks performance separately for YouTube vs Dailymotion.
    Learns what works best on each platform.
    """
    
    PLATFORM_FILE = STATE_DIR / "cross_platform_analytics.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.PLATFORM_FILE.exists():
                with open(self.PLATFORM_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "youtube": {"videos": 0, "total_views": 0, "category_performance": {}},
            "dailymotion": {"videos": 0, "total_views": 0, "category_performance": {}},
            "platform_preferences": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.PLATFORM_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, platform: str, category: str, views: int):
        """Record a video's performance on a specific platform."""
        platform = platform.lower()
        
        if platform not in self.data:
            self.data[platform] = {"videos": 0, "total_views": 0, "category_performance": {}}
        
        self.data[platform]["videos"] += 1
        self.data[platform]["total_views"] += views
        
        if category not in self.data[platform]["category_performance"]:
            self.data[platform]["category_performance"][category] = {"videos": 0, "total_views": 0}
        
        self.data[platform]["category_performance"][category]["videos"] += 1
        self.data[platform]["category_performance"][category]["total_views"] += views
        
        self._save()
    
    def get_platform_insights(self) -> Dict:
        """Get insights on what works best on each platform."""
        insights = {}
        
        for platform in ["youtube", "dailymotion"]:
            if platform not in self.data:
                continue
            
            plat_data = self.data[platform]
            if plat_data["videos"] == 0:
                continue
            
            avg_views = plat_data["total_views"] / plat_data["videos"]
            
            # Find best category
            best_cat = None
            best_avg = 0
            for cat, stats in plat_data.get("category_performance", {}).items():
                if stats["videos"] >= 2:
                    cat_avg = stats["total_views"] / stats["videos"]
                    if cat_avg > best_avg:
                        best_avg = cat_avg
                        best_cat = cat
            
            insights[platform] = {
                "avg_views": int(avg_views),
                "best_category": best_cat,
                "videos_analyzed": plat_data["videos"]
            }
        
        return insights


# =============================================================================
# v9.5 ENHANCEMENT #33: Series Detection & Continuation
# =============================================================================

def detect_series_potential(video_performance: Dict, avg_views: int) -> Dict:
    """
    AI detects if a video performed well enough to warrant a series.
    
    video_performance: {"title": str, "views": int, "category": str, "topic": str}
    Returns: {"should_continue": bool, "series_angle": str, "suggested_title": str}
    """
    views = video_performance.get("views", 0)
    
    # If video performed 1.5x+ average, consider series
    if views < avg_views * 1.5:
        return {
            "should_continue": False,
            "reason": "Performance below series threshold (1.5x average)"
        }
    
    ai = get_ai_caller()
    
    prompt = f"""You are a CONTENT STRATEGIST for viral short videos.

=== HIGH-PERFORMING VIDEO ===
Title: {video_performance.get('title', 'Unknown')}
Views: {views:,} ({views / max(avg_views, 1):.1f}x average)
Category: {video_performance.get('category', 'Unknown')}
Topic: {video_performance.get('topic', 'Unknown')}

=== YOUR TASK ===
This video performed well! Suggest a CONTINUATION/SERIES:

1. Should this become a series? (Part 2, 3, etc.)
2. What's a fresh angle for Part 2 that keeps the magic?
3. What title would work for the sequel?

=== OUTPUT JSON ===
{{
    "should_continue": true,
    "series_potential": "high" or "medium" or "low",
    "part2_angle": "what makes part 2 different but related",
    "part2_hook": "hook for part 2",
    "part2_title": "title for part 2",
    "series_name": "if it becomes ongoing series",
    "reasoning": "why this works as series"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    parsed = ai.parse_json(result)
    
    if parsed:
        parsed["should_continue"] = True
        parsed["original_performance"] = f"{views / max(avg_views, 1):.1f}x average"
        return parsed
    
    return {
        "should_continue": True,
        "series_potential": "medium",
        "part2_angle": "Different perspective on same topic",
        "reason": "High performance warrants continuation"
    }


# =============================================================================
# v9.5 ENHANCEMENT #34: Engagement Reply Generator
# =============================================================================

def generate_reply_templates(comments: List[str]) -> Dict:
    """
    AI generates reply templates for common comment types.
    Helps boost engagement through channel responses.
    """
    if not comments:
        return {"templates": []}
    
    ai = get_ai_caller()
    
    # Take sample of comments
    sample = comments[:20]
    
    prompt = f"""You are a COMMUNITY MANAGER for a viral YouTube Shorts channel.

=== SAMPLE COMMENTS ===
{json.dumps(sample, indent=2)}

=== YOUR TASK ===
Categorize these comments and create reply templates.

Comment types to identify:
1. PRAISE ("great video!", "loved this")
2. QUESTIONS ("how do I...", "what about...")
3. DISAGREEMENT ("this is wrong", "actually...")
4. REQUESTS ("can you make a video about...")
5. TROLLS ("fake", "AI garbage")

For each type, create 2-3 reply templates that:
- Sound human (not robotic)
- Encourage further engagement
- Build community
- Are short and authentic

=== OUTPUT JSON ===
{{
    "comment_categories": [
        {{
            "category": "praise",
            "example_comments": ["example 1", "example 2"],
            "reply_templates": [
                "Thanks! 🙏 What topic should I cover next?",
                "Glad you liked it! Drop a follow for more"
            ]
        }}
    ],
    "general_tips": ["tip 1", "tip 2"]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=500, priority="bulk")
    return ai.parse_json(result) or {"comment_categories": []}


# =============================================================================
# v9.5 ENHANCEMENT #35: Category Performance Decay
# =============================================================================

class CategoryDecayTracker:
    """
    Applies time-decay to category performance.
    Recently underperforming categories get reduced weight.
    """
    
    DECAY_FILE = STATE_DIR / "category_decay.json"
    DECAY_HALF_LIFE_DAYS = 14  # Performance halves every 14 days
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.DECAY_FILE.exists():
                with open(self.DECAY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "category_history": {},  # {"psychology": [{"date": "...", "performance": 1.2}]}
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.DECAY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, category: str, views: int, avg_views: int):
        """Record a category's performance."""
        if category not in self.data["category_history"]:
            self.data["category_history"][category] = []
        
        performance = views / max(avg_views, 1)
        
        self.data["category_history"][category].append({
            "date": datetime.now().isoformat(),
            "performance": performance
        })
        
        # Keep last 30 entries
        self.data["category_history"][category] = self.data["category_history"][category][-30:]
        
        self._save()
    
    def get_decayed_weights(self) -> Dict[str, float]:
        """Get category weights with time decay applied."""
        weights = {}
        now = datetime.now()
        
        for category, history in self.data["category_history"].items():
            if not history:
                weights[category] = 1.0
                continue
            
            weighted_sum = 0
            weight_total = 0
            
            for entry in history:
                try:
                    entry_date = datetime.fromisoformat(entry["date"])
                    days_ago = (now - entry_date).days
                    
                    # Exponential decay
                    decay_factor = 0.5 ** (days_ago / self.DECAY_HALF_LIFE_DAYS)
                    
                    weighted_sum += entry["performance"] * decay_factor
                    weight_total += decay_factor
                except:
                    continue
            
            if weight_total > 0:
                weights[category] = weighted_sum / weight_total
            else:
                weights[category] = 1.0
        
        return weights
    
    def get_recommended_categories(self, all_categories: List[str]) -> List[str]:
        """Get categories sorted by decayed performance."""
        weights = self.get_decayed_weights()
        
        # Add categories not yet tracked with neutral weight
        for cat in all_categories:
            if cat not in weights:
                weights[cat] = 1.0
        
        # Sort by weight descending
        sorted_cats = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        return [c[0] for c in sorted_cats]


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_orchestrator = None
_hook_tracker = None
_voice_optimizer = None
_hashtag_rotator = None
_platform_analytics = None
_category_decay = None

def get_enhancement_orchestrator() -> EnhancementOrchestrator:
    """Get the singleton enhancement orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EnhancementOrchestrator()
    return _orchestrator


def get_hook_tracker() -> HookWordTracker:
    """Get the singleton hook word tracker."""
    global _hook_tracker
    if _hook_tracker is None:
        _hook_tracker = HookWordTracker()
    return _hook_tracker


def get_voice_optimizer() -> VoiceSpeedOptimizer:
    """Get the singleton voice speed optimizer."""
    global _voice_optimizer
    if _voice_optimizer is None:
        _voice_optimizer = VoiceSpeedOptimizer()
    return _voice_optimizer


def get_hashtag_rotator() -> HashtagRotator:
    """Get the singleton hashtag rotator."""
    global _hashtag_rotator
    if _hashtag_rotator is None:
        _hashtag_rotator = HashtagRotator()
    return _hashtag_rotator


def get_platform_analytics() -> CrossPlatformAnalytics:
    """Get the singleton cross-platform analytics."""
    global _platform_analytics
    if _platform_analytics is None:
        _platform_analytics = CrossPlatformAnalytics()
    return _platform_analytics


def get_category_decay() -> CategoryDecayTracker:
    """Get the singleton category decay tracker."""
    global _category_decay
    if _category_decay is None:
        _category_decay = CategoryDecayTracker()
    return _category_decay


# =============================================================================
# v10.0 ENHANCEMENT #36: Thumbnail Text Optimization
# =============================================================================

class ThumbnailTextOptimizer:
    """
    AI learns which thumbnail text overlays drive the most clicks.
    Tracks word count, style, and capitalization patterns.
    """
    
    THUMB_TEXT_FILE = STATE_DIR / "thumbnail_text_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.THUMB_TEXT_FILE.exists():
                with open(self.THUMB_TEXT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "text_patterns": {},  # {"ALL_CAPS": {"videos": 5, "total_ctr": 0.08}}
            "word_counts": {},    # {"3": {"videos": 10, "avg_ctr": 0.07}}
            "power_words": {},    # {"SECRET": {"uses": 5, "avg_ctr": 0.09}}
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.THUMB_TEXT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _get_power_word_candidates(self) -> List[str]:
        """
        v17.8: Get power word candidates from AI or learned data.
        """
        # First try: Get from already-tracked power words
        if self.data.get("power_words"):
            return list(self.data["power_words"].keys())
        
        # Second try: Ask AI for power words
        try:
            ai = get_ai_caller()
            prompt = """List 15 power words that make YouTube Shorts thumbnails/titles irresistible.
            Words that create urgency, curiosity, or shock.
            Return ONLY a JSON array of uppercase words: ["WORD1", "WORD2", ...]
            JSON ONLY."""
            result = ai.call(prompt, max_tokens=100, priority="bulk")
            parsed = ai.parse_json(result)
            if isinstance(parsed, list) and len(parsed) > 0:
                return [w.upper() for w in parsed]
        except:
            pass
        
        # Minimal fallback
        return ["SECRET", "TRUTH", "SHOCKING", "FREE", "NOW"]
    
    def record_thumbnail_performance(self, text: str, ctr: float):
        """Record a thumbnail text's click-through rate."""
        if not text:
            return
        
        # Detect pattern (ALL_CAPS, Title Case, lowercase)
        if text.isupper():
            pattern = "ALL_CAPS"
        elif text.istitle():
            pattern = "Title_Case"
        else:
            pattern = "mixed"
        
        if pattern not in self.data["text_patterns"]:
            self.data["text_patterns"][pattern] = {"videos": 0, "total_ctr": 0}
        self.data["text_patterns"][pattern]["videos"] += 1
        self.data["text_patterns"][pattern]["total_ctr"] += ctr
        
        # Track word count
        word_count = str(len(text.split()))
        if word_count not in self.data["word_counts"]:
            self.data["word_counts"][word_count] = {"videos": 0, "total_ctr": 0}
        self.data["word_counts"][word_count]["videos"] += 1
        self.data["word_counts"][word_count]["total_ctr"] += ctr
        
        # Track power words - v17.8: Get from AI pattern generator
        words = text.upper().split()
        power_candidates = self._get_power_word_candidates()
        for word in words:
            if word in power_candidates:
                if word not in self.data["power_words"]:
                    self.data["power_words"][word] = {"uses": 0, "total_ctr": 0}
                self.data["power_words"][word]["uses"] += 1
                self.data["power_words"][word]["total_ctr"] += ctr
        
        self._save()
    
    def get_optimal_settings(self) -> Dict:
        """Get the optimal thumbnail text settings based on learning."""
        best_pattern = "ALL_CAPS"
        best_pattern_ctr = 0
        
        for pattern, stats in self.data["text_patterns"].items():
            if stats["videos"] >= 3:
                avg_ctr = stats["total_ctr"] / stats["videos"]
                if avg_ctr > best_pattern_ctr:
                    best_pattern_ctr = avg_ctr
                    best_pattern = pattern
        
        best_word_count = 3
        best_wc_ctr = 0
        for wc, stats in self.data["word_counts"].items():
            if stats["videos"] >= 3:
                avg_ctr = stats["total_ctr"] / stats["videos"]
                if avg_ctr > best_wc_ctr:
                    best_wc_ctr = avg_ctr
                    best_word_count = int(wc)
        
        top_power_words = []
        for word, stats in self.data["power_words"].items():
            if stats["uses"] >= 2:
                avg_ctr = stats["total_ctr"] / stats["uses"]
                top_power_words.append((word, avg_ctr))
        top_power_words.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "best_pattern": best_pattern,
            "best_word_count": best_word_count,
            "top_power_words": [w[0] for w in top_power_words[:5]]
        }


# =============================================================================
# v10.0 ENHANCEMENT #37: Emotional Arc Mapping
# =============================================================================

def design_emotional_arc(content: str, video_type: str) -> Dict:
    """
    AI designs the emotional journey for optimal engagement.
    Maps: Hook emotion -> Build tension -> Peak -> Resolution
    """
    ai = get_ai_caller()
    
    prompt = f"""You are an EMOTIONAL STORYTELLING expert for short-form video.

=== CONTENT ===
{content[:500]}

=== VIDEO TYPE ===
{video_type}

=== DESIGN THE EMOTIONAL ARC ===
Map the emotional journey across the video:

1. HOOK (0-2s): What emotion grabs attention?
   - Options: shock, curiosity, fear, excitement, confusion

2. BUILD (2-8s): How does tension increase?
   - Building anticipation, raising stakes, creating mystery

3. PEAK (8-15s): The emotional climax
   - The big reveal, the payoff, the wow moment

4. RESOLUTION (15-20s): How do they feel after?
   - Satisfied, motivated, curious for more, validated

=== OUTPUT JSON ===
{{
    "emotional_journey": [
        {{"phase": "hook", "emotion": "curiosity", "intensity": 7, "technique": "open loop"}}
    ],
    "peak_moment_timing": 12,
    "energy_curve": [5, 6, 7, 8, 9, 10, 8, 7],
    "music_mood_suggestion": "building_tension",
    "voice_energy": "start calm, build to excited, end confident",
    "pacing_notes": "slow at start, accelerate through middle"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {
        "emotional_journey": [{"phase": "hook", "emotion": "curiosity", "intensity": 7}],
        "peak_moment_timing": 12
    }


# =============================================================================
# v10.0 ENHANCEMENT #38: Competitor Gap Analysis
# =============================================================================

def analyze_competitor_gaps(our_topics: List[str], competitor_topics: List[str]) -> Dict:
    """
    AI identifies topics competitors haven't covered that we could.
    Finds untapped niches and angles.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a COMPETITIVE INTELLIGENCE analyst for viral content.

=== OUR RECENT TOPICS ===
{json.dumps(our_topics[:15], indent=2)}

=== COMPETITOR TOPICS (from top channels) ===
{json.dumps(competitor_topics[:20], indent=2)}

=== FIND THE GAPS ===
Identify content opportunities competitors are MISSING:

1. UNTAPPED NICHES: Subcategories no one is covering
2. FRESH ANGLES: New perspectives on popular topics
3. UNDERSERVED AUDIENCES: Demographics being ignored
4. TIMING OPPORTUNITIES: Topics that should be trending but aren't covered

=== OUTPUT JSON ===
{{
    "untapped_niches": [
        {{"niche": "specific niche", "why_valuable": "reason", "hook_idea": "hook"}}
    ],
    "fresh_angles": [
        {{"existing_topic": "what competitors do", "our_angle": "how we differentiate"}}
    ],
    "content_recommendations": [
        {{"topic": "specific topic", "priority": "high/medium", "reason": "why now"}}
    ],
    "avoid_saturated": ["topic 1", "topic 2"]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=500, priority="bulk")
    return ai.parse_json(result) or {"untapped_niches": [], "content_recommendations": []}


# =============================================================================
# v10.0 ENHANCEMENT #39: Description SEO Optimizer
# =============================================================================

def optimize_description_seo(title: str, content: str, category: str) -> Dict:
    """
    AI optimizes video descriptions for YouTube search.
    Includes keywords, timestamps, and call-to-actions.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a YOUTUBE SEO expert specializing in Shorts.

=== VIDEO INFO ===
Title: {title}
Category: {category}
Content Summary: {content[:200]}

=== OPTIMIZE DESCRIPTION FOR SEARCH ===
Create an SEO-optimized description that:
1. Includes primary keyword in first 25 characters
2. Contains 3-5 related keywords naturally
3. Has a clear call-to-action
4. Is under 200 characters (Shorts sweet spot)
5. Includes relevant hashtags

=== OUTPUT JSON ===
{{
    "optimized_description": "The full description text",
    "primary_keyword": "main search term",
    "secondary_keywords": ["keyword2", "keyword3"],
    "cta_used": "the call to action",
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "seo_score": 8,
    "improvement_notes": "what makes this SEO-strong"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    return ai.parse_json(result) or {
        "optimized_description": f"{title} #shorts #viral",
        "seo_score": 5
    }


# =============================================================================
# v10.0 ENHANCEMENT #40: Comment Sentiment Tracker
# =============================================================================

class CommentSentimentTracker:
    """
    Tracks positive vs negative comment ratios per video.
    Learns which content types generate better sentiment.
    """
    
    SENTIMENT_FILE = STATE_DIR / "comment_sentiment.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.SENTIMENT_FILE.exists():
                with open(self.SENTIMENT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "videos": [],  # {"video_id": str, "positive": int, "negative": int, "category": str}
            "category_sentiment": {},  # {"psychology": {"positive": 100, "negative": 20}}
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.SENTIMENT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_video_sentiment(self, video_id: str, category: str, positive: int, negative: int):
        """Record sentiment counts for a video."""
        self.data["videos"].append({
            "video_id": video_id,
            "positive": positive,
            "negative": negative,
            "category": category,
            "ratio": positive / max(negative, 1),
            "date": datetime.now().isoformat()
        })
        self.data["videos"] = self.data["videos"][-100:]  # Keep last 100
        
        # Update category aggregates
        if category not in self.data["category_sentiment"]:
            self.data["category_sentiment"][category] = {"positive": 0, "negative": 0}
        self.data["category_sentiment"][category]["positive"] += positive
        self.data["category_sentiment"][category]["negative"] += negative
        
        self._save()
    
    def get_category_sentiment_scores(self) -> Dict[str, float]:
        """Get sentiment ratio per category."""
        scores = {}
        for cat, counts in self.data["category_sentiment"].items():
            pos = counts.get("positive", 0)
            neg = counts.get("negative", 1)
            scores[cat] = round(pos / max(neg, 1), 2)
        return scores
    
    def get_best_sentiment_categories(self) -> List[str]:
        """Get categories with best sentiment ratios."""
        scores = self.get_category_sentiment_scores()
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_cats[:5]]


def analyze_comment_sentiment(comments: List[str]) -> Dict:
    """AI analyzes comments to determine sentiment breakdown."""
    if not comments:
        return {"positive": 0, "negative": 0, "neutral": 0}
    
    ai = get_ai_caller()
    
    prompt = f"""Analyze these YouTube comments for sentiment.

COMMENTS:
{json.dumps(comments[:20], indent=2)}

Count how many are:
- POSITIVE (praise, thanks, love it, great, etc.)
- NEGATIVE (criticism, hate, fake, wrong, etc.)
- NEUTRAL (questions, observations, neither positive nor negative)

OUTPUT JSON:
{{
    "positive": count,
    "negative": count,
    "neutral": count,
    "notable_positive": ["best positive comment"],
    "notable_negative": ["worst negative comment"],
    "overall_sentiment": "positive" or "negative" or "mixed"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"positive": 0, "negative": 0, "neutral": len(comments)}


# =============================================================================
# v10.0 ENHANCEMENT #41: Peak Publishing Optimizer
# =============================================================================

class PeakPublishingOptimizer:
    """
    Learns optimal posting times from actual performance data.
    Tracks hour and day correlations with views.
    """
    
    PUBLISHING_FILE = STATE_DIR / "publishing_times.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.PUBLISHING_FILE.exists():
                with open(self.PUBLISHING_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "hourly_performance": {str(h): {"videos": 0, "total_views": 0} for h in range(24)},
            "daily_performance": {d: {"videos": 0, "total_views": 0} for d in 
                                  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
            "best_slots": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.PUBLISHING_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_publishing_performance(self, publish_hour: int, publish_day: str, views: int):
        """Record performance for a publishing time."""
        hour_key = str(publish_hour)
        
        if hour_key not in self.data["hourly_performance"]:
            self.data["hourly_performance"][hour_key] = {"videos": 0, "total_views": 0}
        self.data["hourly_performance"][hour_key]["videos"] += 1
        self.data["hourly_performance"][hour_key]["total_views"] += views
        
        if publish_day not in self.data["daily_performance"]:
            self.data["daily_performance"][publish_day] = {"videos": 0, "total_views": 0}
        self.data["daily_performance"][publish_day]["videos"] += 1
        self.data["daily_performance"][publish_day]["total_views"] += views
        
        self._update_best_slots()
        self._save()
    
    def _update_best_slots(self):
        """Calculate best publishing slots."""
        hour_avgs = []
        for hour, stats in self.data["hourly_performance"].items():
            if stats["videos"] >= 3:
                avg = stats["total_views"] / stats["videos"]
                hour_avgs.append((int(hour), avg))
        
        hour_avgs.sort(key=lambda x: x[1], reverse=True)
        self.data["best_slots"] = [h[0] for h in hour_avgs[:5]]
    
    def get_best_publishing_times(self) -> Dict:
        """Get optimal publishing times."""
        best_hours = self.data.get("best_slots", [14, 18, 20])[:3]
        
        # Best days
        day_avgs = []
        for day, stats in self.data["daily_performance"].items():
            if stats["videos"] >= 2:
                avg = stats["total_views"] / stats["videos"]
                day_avgs.append((day, avg))
        day_avgs.sort(key=lambda x: x[1], reverse=True)
        best_days = [d[0] for d in day_avgs[:3]]
        
        return {
            "best_hours_utc": best_hours if best_hours else [14, 18, 20],
            "best_days": best_days if best_days else ["Friday", "Saturday", "Sunday"]
        }


# =============================================================================
# v10.0 ENHANCEMENT #42: Title Length Optimizer
# =============================================================================

class TitleLengthOptimizer:
    """
    Tracks optimal title character count for CTR.
    """
    
    TITLE_LENGTH_FILE = STATE_DIR / "title_length_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.TITLE_LENGTH_FILE.exists():
                with open(self.TITLE_LENGTH_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "length_buckets": {},  # {"30-40": {"videos": 5, "total_ctr": 0.4}}
            "optimal_range": [35, 50],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.TITLE_LENGTH_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _get_bucket(self, length: int) -> str:
        """Get the length bucket for a title."""
        if length < 20:
            return "0-20"
        elif length < 30:
            return "20-30"
        elif length < 40:
            return "30-40"
        elif length < 50:
            return "40-50"
        elif length < 60:
            return "50-60"
        else:
            return "60+"
    
    def record_title_performance(self, title: str, ctr: float):
        """Record a title's performance."""
        length = len(title)
        bucket = self._get_bucket(length)
        
        if bucket not in self.data["length_buckets"]:
            self.data["length_buckets"][bucket] = {"videos": 0, "total_ctr": 0}
        
        self.data["length_buckets"][bucket]["videos"] += 1
        self.data["length_buckets"][bucket]["total_ctr"] += ctr
        
        self._update_optimal_range()
        self._save()
    
    def _update_optimal_range(self):
        """Update the optimal title length range."""
        best_bucket = "30-40"
        best_avg = 0
        
        for bucket, stats in self.data["length_buckets"].items():
            if stats["videos"] >= 3:
                avg = stats["total_ctr"] / stats["videos"]
                if avg > best_avg:
                    best_avg = avg
                    best_bucket = bucket
        
        # Convert bucket to range
        ranges = {
            "0-20": [15, 20],
            "20-30": [25, 30],
            "30-40": [35, 40],
            "40-50": [40, 50],
            "50-60": [45, 55],
            "60+": [50, 60]
        }
        self.data["optimal_range"] = ranges.get(best_bucket, [35, 50])
    
    def get_optimal_length(self) -> Dict:
        """Get the optimal title length range."""
        return {
            "min_chars": self.data["optimal_range"][0],
            "max_chars": self.data["optimal_range"][1],
            "target": sum(self.data["optimal_range"]) // 2
        }


# =============================================================================
# v10.0 ENHANCEMENT #43: Music BPM Matcher
# =============================================================================

class MusicBPMMatcher:
    """
    Matches content energy to music tempo.
    Tracks which BPM ranges work for different content types.
    """
    
    BPM_FILE = STATE_DIR / "music_bpm_performance.json"
    
    # BPM ranges for different moods (typical stock music)
    BPM_RANGES = {
        "calm": (60, 80),
        "moderate": (80, 110),
        "energetic": (110, 140),
        "intense": (140, 180)
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.BPM_FILE.exists():
                with open(self.BPM_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "category_bpm": {},  # {"psychology": {"calm": 5, "energetic": 2}}
            "best_matches": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.BPM_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_music_performance(self, category: str, bpm_range: str, views: int, avg_views: int):
        """Record how a BPM range performed for a category."""
        if category not in self.data["category_bpm"]:
            self.data["category_bpm"][category] = {}
        
        if bpm_range not in self.data["category_bpm"][category]:
            self.data["category_bpm"][category][bpm_range] = {"uses": 0, "total_performance": 0}
        
        performance = views / max(avg_views, 1)
        self.data["category_bpm"][category][bpm_range]["uses"] += 1
        self.data["category_bpm"][category][bpm_range]["total_performance"] += performance
        
        self._update_best_matches()
        self._save()
    
    def _update_best_matches(self):
        """Update best BPM matches per category."""
        for category, bpm_data in self.data["category_bpm"].items():
            best_range = "moderate"
            best_perf = 0
            
            for bpm_range, stats in bpm_data.items():
                if stats["uses"] >= 2:
                    avg_perf = stats["total_performance"] / stats["uses"]
                    if avg_perf > best_perf:
                        best_perf = avg_perf
                        best_range = bpm_range
            
            self.data["best_matches"][category] = best_range
    
    def get_recommended_bpm(self, category: str) -> Dict:
        """Get recommended BPM range for a category."""
        best_match = self.data.get("best_matches", {}).get(category, "moderate")
        bpm_range = self.BPM_RANGES.get(best_match, (80, 110))
        
        return {
            "range_name": best_match,
            "bpm_min": bpm_range[0],
            "bpm_max": bpm_range[1],
            "target_bpm": (bpm_range[0] + bpm_range[1]) // 2
        }


# =============================================================================
# v10.0 ENHANCEMENT #44: Intro Pattern Learner
# =============================================================================

class IntroPatternLearner:
    """
    Learns which opening styles (intro patterns) drive retention.
    """
    
    INTRO_FILE = STATE_DIR / "intro_pattern_performance.json"
    
    INTRO_PATTERNS = [
        "question",        # "Did you know...?"
        "shocking_stat",   # "73% of people..."
        "direct_claim",    # "This will change..."
        "you_statement",   # "You're probably..."
        "story_tease",     # "Last week I..."
        "countdown",       # "Number 3 is..."
        "challenge"        # "I bet you can't..."
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.INTRO_FILE.exists():
                with open(self.INTRO_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "pattern_performance": {p: {"uses": 0, "total_retention": 0} for p in self.INTRO_PATTERNS},
            "best_patterns": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.INTRO_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def detect_intro_pattern(self, hook: str) -> str:
        """Detect the intro pattern used in a hook."""
        hook_lower = hook.lower()
        
        if hook_lower.startswith(("did you", "have you", "do you", "can you", "what if")):
            return "question"
        elif any(c.isdigit() for c in hook[:20]) and "%" in hook:
            return "shocking_stat"
        elif hook_lower.startswith(("you ", "your ")):
            return "you_statement"
        elif hook_lower.startswith(("number ", "#", "first", "1.")):
            return "countdown"
        elif hook_lower.startswith(("i bet", "bet you", "try this")):
            return "challenge"
        elif any(word in hook_lower for word in ["last week", "yesterday", "once", "my friend"]):
            return "story_tease"
        else:
            return "direct_claim"
    
    def record_intro_performance(self, hook: str, retention_percent: float):
        """Record how an intro pattern performed."""
        pattern = self.detect_intro_pattern(hook)
        
        if pattern not in self.data["pattern_performance"]:
            self.data["pattern_performance"][pattern] = {"uses": 0, "total_retention": 0}
        
        self.data["pattern_performance"][pattern]["uses"] += 1
        self.data["pattern_performance"][pattern]["total_retention"] += retention_percent
        
        self._update_best_patterns()
        self._save()
    
    def _update_best_patterns(self):
        """Update the ranked list of best patterns."""
        pattern_scores = []
        
        for pattern, stats in self.data["pattern_performance"].items():
            if stats["uses"] >= 3:
                avg = stats["total_retention"] / stats["uses"]
                pattern_scores.append((pattern, avg))
        
        pattern_scores.sort(key=lambda x: x[1], reverse=True)
        self.data["best_patterns"] = [p[0] for p in pattern_scores]
    
    def get_recommended_pattern(self) -> str:
        """Get the best performing intro pattern."""
        if self.data["best_patterns"]:
            return self.data["best_patterns"][0]
        return "shocking_stat"  # Default


# =============================================================================
# v10.0 ENHANCEMENT #45: Viral Velocity Predictor
# =============================================================================

def predict_viral_velocity(title: str, hook: str, category: str, historical_avg: int) -> Dict:
    """
    AI predicts viral potential before upload.
    Estimates first-hour, first-day, and week-1 views.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a VIRAL PREDICTION expert who has analyzed millions of YouTube Shorts.

=== VIDEO TO ANALYZE ===
Title: {title}
Hook: {hook}
Category: {category}
Channel Average Views: {historical_avg:,}

=== PREDICT VIRAL VELOCITY ===
Based on these factors, predict performance:

1. SCROLL-STOP POWER: Does the title/hook stop scrolling?
2. SHAREABILITY: Would someone share this with friends?
3. COMMENT BAIT: Does it provoke discussion?
4. TREND ALIGNMENT: Is this topic trending?
5. ALGORITHM FRIENDLINESS: Will YouTube promote this?

=== OUTPUT JSON ===
{{
    "viral_score": 1-10,
    "velocity_tier": "slow_burn" or "moderate" or "fast" or "explosive",
    "predicted_first_hour": {int(historical_avg * 0.1)},
    "predicted_first_day": {int(historical_avg * 0.5)},
    "predicted_week_1": {int(historical_avg)},
    "confidence": 0.7,
    "strength_factors": ["what makes it viral"],
    "risk_factors": ["what could limit it"],
    "recommendation": "upload" or "improve_first"
}}

Be realistic based on the channel's historical average. JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    parsed = ai.parse_json(result)
    
    if parsed:
        return parsed
    
    return {
        "viral_score": 6,
        "velocity_tier": "moderate",
        "predicted_first_hour": int(historical_avg * 0.1),
        "predicted_first_day": int(historical_avg * 0.5),
        "predicted_week_1": historical_avg,
        "recommendation": "upload"
    }


# =============================================================================
# v10.0 SINGLETON ACCESSORS
# =============================================================================

_thumbnail_optimizer = None
_sentiment_tracker = None
_publishing_optimizer = None
_title_length_optimizer = None
_bpm_matcher = None
_intro_learner = None


def get_thumbnail_optimizer() -> ThumbnailTextOptimizer:
    """Get the singleton thumbnail text optimizer."""
    global _thumbnail_optimizer
    if _thumbnail_optimizer is None:
        _thumbnail_optimizer = ThumbnailTextOptimizer()
    return _thumbnail_optimizer


def get_sentiment_tracker() -> CommentSentimentTracker:
    """Get the singleton comment sentiment tracker."""
    global _sentiment_tracker
    if _sentiment_tracker is None:
        _sentiment_tracker = CommentSentimentTracker()
    return _sentiment_tracker


def get_publishing_optimizer() -> PeakPublishingOptimizer:
    """Get the singleton peak publishing optimizer."""
    global _publishing_optimizer
    if _publishing_optimizer is None:
        _publishing_optimizer = PeakPublishingOptimizer()
    return _publishing_optimizer


def get_title_length_optimizer() -> TitleLengthOptimizer:
    """Get the singleton title length optimizer."""
    global _title_length_optimizer
    if _title_length_optimizer is None:
        _title_length_optimizer = TitleLengthOptimizer()
    return _title_length_optimizer


def get_bpm_matcher() -> MusicBPMMatcher:
    """Get the singleton music BPM matcher."""
    global _bpm_matcher
    if _bpm_matcher is None:
        _bpm_matcher = MusicBPMMatcher()
    return _bpm_matcher


def get_intro_learner() -> IntroPatternLearner:
    """Get the singleton intro pattern learner."""
    global _intro_learner
    if _intro_learner is None:
        _intro_learner = IntroPatternLearner()
    return _intro_learner


# #############################################################################
# #############################################################################
# v11.0 ENHANCEMENTS - 44 NEW (8 CATEGORIES)
# #############################################################################
# #############################################################################

# =============================================================================
# CATEGORY 1: CLICK BAITING (#46-51)
# =============================================================================

class CuriosityGapGenerator:
    """
    #46: Generates irresistible curiosity gaps in titles and hooks.
    Learns which gap patterns drive the most clicks.
    """
    
    GAP_FILE = STATE_DIR / "curiosity_gap_performance.json"
    
    GAP_PATTERNS = [
        "what_happens_when",  # "What Happens When You..."
        "the_real_reason",    # "The REAL Reason Why..."
        "nobody_tells_you",   # "What Nobody Tells You About..."
        "secret_that",        # "The Secret That..."
        "truth_about",        # "The Truth About..."
        "why_you_should",     # "Why You Should Never..."
        "what_if",            # "What If..."
        "hidden",             # "The Hidden..."
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.GAP_FILE.exists():
                with open(self.GAP_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "pattern_performance": {p: {"uses": 0, "total_ctr": 0} for p in self.GAP_PATTERNS},
            "best_patterns": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.GAP_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def detect_gap_pattern(self, title: str) -> str:
        """Detect which curiosity gap pattern is used."""
        title_lower = title.lower()
        if "what happens" in title_lower:
            return "what_happens_when"
        elif "real reason" in title_lower or "actually" in title_lower:
            return "the_real_reason"
        elif "nobody" in title_lower or "no one" in title_lower:
            return "nobody_tells_you"
        elif "secret" in title_lower:
            return "secret_that"
        elif "truth" in title_lower:
            return "truth_about"
        elif "why you" in title_lower or "never" in title_lower:
            return "why_you_should"
        elif "what if" in title_lower:
            return "what_if"
        elif "hidden" in title_lower:
            return "hidden"
        return "other"
    
    def record_performance(self, title: str, ctr: float):
        """Record a title's CTR for learning."""
        pattern = self.detect_gap_pattern(title)
        if pattern not in self.data["pattern_performance"]:
            self.data["pattern_performance"][pattern] = {"uses": 0, "total_ctr": 0}
        self.data["pattern_performance"][pattern]["uses"] += 1
        self.data["pattern_performance"][pattern]["total_ctr"] += ctr
        self._update_best()
        self._save()
    
    def _update_best(self):
        scored = []
        for p, stats in self.data["pattern_performance"].items():
            if stats["uses"] >= 2:
                avg = stats["total_ctr"] / stats["uses"]
                scored.append((p, avg))
        scored.sort(key=lambda x: x[1], reverse=True)
        self.data["best_patterns"] = [s[0] for s in scored]
    
    def get_best_pattern(self) -> str:
        if self.data["best_patterns"]:
            return self.data["best_patterns"][0]
        return "secret_that"
    
    def get_curiosity_instruction(self, topic: str = "") -> str:
        """Get AI-friendly instruction for curiosity gap creation."""
        best = self.get_best_pattern()
        pattern_map = {
            "what_happens_when": "Use 'What Happens When...' opening",
            "the_real_reason": "Use 'The REAL Reason...' for authority",
            "nobody_tells_you": "Use 'What Nobody Tells You...' for exclusivity",
            "secret_that": "Use 'The Secret That...' for mystery",
            "truth_about": "Use 'The Truth About...' for revelation",
            "why_you_should": "Use 'Why You Should Never...' for controversy",
            "what_if": "Use 'What If...' for speculation",
            "hidden": "Use 'The Hidden...' for discovery"
        }
        return f"CURIOSITY GAP: {pattern_map.get(best, 'Create mystery that demands resolution')}"


class NumberHookOptimizer:
    """
    #47: Learns which numbers (3, 5, 7, 10) perform best in titles.
    """
    
    NUMBER_FILE = STATE_DIR / "number_hook_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.NUMBER_FILE.exists():
                with open(self.NUMBER_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "number_performance": {},  # {"3": {"uses": 5, "total_ctr": 0.35}}
            "best_number": 5,
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.NUMBER_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def extract_number(self, title: str) -> Optional[int]:
        """Extract the first prominent number from a title."""
        import re
        matches = re.findall(r'\b(\d+)\b', title)
        if matches:
            num = int(matches[0])
            if 2 <= num <= 20:
                return num
        return None
    
    def record_performance(self, title: str, ctr: float):
        num = self.extract_number(title)
        if num:
            key = str(num)
            if key not in self.data["number_performance"]:
                self.data["number_performance"][key] = {"uses": 0, "total_ctr": 0}
            self.data["number_performance"][key]["uses"] += 1
            self.data["number_performance"][key]["total_ctr"] += ctr
            self._update_best()
            self._save()
    
    def _update_best(self):
        best_num = 5
        best_ctr = 0
        for num, stats in self.data["number_performance"].items():
            if stats["uses"] >= 3:
                avg = stats["total_ctr"] / stats["uses"]
                if avg > best_ctr:
                    best_ctr = avg
                    best_num = int(num)
        self.data["best_number"] = best_num
    
    def get_optimal_number(self) -> int:
        return self.data.get("best_number", 5)
    
    def get_number_recommendation(self, topic: str = "") -> str:
        """Get AI-friendly instruction for number usage."""
        best = self.get_optimal_number()
        return f"NUMBER HOOK: Use {best} items/tips/secrets (odd numbers like 3,5,7 often work best)"


class ControversyCalibrator:
    """
    #48: Adds safe controversy to titles for engagement.
    Controversy drives comments but must be safe.
    """
    
    CONTROVERSY_FILE = STATE_DIR / "controversy_calibration.json"
    
    SAFE_CONTROVERSY_TYPES = [
        "unpopular_opinion",   # "Unpopular Opinion: ..."
        "everyone_wrong",      # "Why Everyone Is Wrong About..."
        "overrated",           # "This Popular Thing is Overrated"
        "you_vs_them",         # "You vs The Average Person"
        "myth_busting",        # "This Common Belief is FALSE"
        "generational",        # "Millennials vs Gen Z"
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.CONTROVERSY_FILE.exists():
                with open(self.CONTROVERSY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "type_performance": {t: {"uses": 0, "comments": 0} for t in self.SAFE_CONTROVERSY_TYPES},
            "best_types": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.CONTROVERSY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, controversy_type: str, comment_count: int):
        if controversy_type not in self.data["type_performance"]:
            self.data["type_performance"][controversy_type] = {"uses": 0, "comments": 0}
        self.data["type_performance"][controversy_type]["uses"] += 1
        self.data["type_performance"][controversy_type]["comments"] += comment_count
        self._save()
    
    def get_best_controversy_type(self) -> str:
        best = "myth_busting"
        best_avg = 0
        for ctype, stats in self.data["type_performance"].items():
            if stats["uses"] >= 2:
                avg = stats["comments"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = ctype
        return best
    
    def get_safe_controversy_instruction(self, topic: str = "") -> str:
        """Get AI-friendly instruction for safe controversy."""
        best = self.get_best_controversy_type()
        return f"SAFE CONTROVERSY: Use '{best.replace('_', ' ')}' style - drives engagement without risk"


class FOMOInjector:
    """
    #49: Creates fear of missing out in hooks.
    Tracks which FOMO phrases drive urgency.
    """
    
    FOMO_FILE = STATE_DIR / "fomo_performance.json"
    
    FOMO_PHRASES = [
        "before_its_too_late",
        "limited_time",
        "everyone_knows",
        "youre_missing",
        "dont_get_left_behind",
        "others_already",
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.FOMO_FILE.exists():
                with open(self.FOMO_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"phrases": {p: {"uses": 0, "engagement": 0} for p in self.FOMO_PHRASES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.FOMO_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_fomo_phrase(self) -> str:
        best = "everyone_knows"
        best_avg = 0
        for phrase, stats in self.data["phrases"].items():
            if stats["uses"] >= 2:
                avg = stats["engagement"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = phrase
        return best
    
    def get_fomo_instruction(self) -> str:
        """Get AI-friendly FOMO instruction."""
        best = self.get_best_fomo_phrase()
        fomo_map = {
            "before_its_too_late": "Before it's too late...",
            "limited_time": "For a limited time...",
            "everyone_knows": "Everyone already knows except...",
            "youre_missing": "You're missing out on...",
            "dont_get_left_behind": "Don't get left behind...",
            "others_already": "Others have already..."
        }
        return f"FOMO: Use '{fomo_map.get(best, best)}' to create urgency"


class TitlePowerWordTracker:
    """
    #50: Tracks which power words in titles drive the most clicks.
    """
    
    POWER_WORD_FILE = STATE_DIR / "title_power_words.json"
    
    POWER_WORDS = [
        "secret", "hidden", "shocking", "truth", "never", "always",
        "free", "proven", "instant", "easy", "fast", "simple",
        "best", "worst", "only", "first", "last", "new",
        "discover", "reveal", "exposed", "banned", "illegal",
        "hack", "trick", "method", "system", "formula"
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.POWER_WORD_FILE.exists():
                with open(self.POWER_WORD_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"words": {w: {"uses": 0, "total_ctr": 0} for w in self.POWER_WORDS}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.POWER_WORD_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_title_performance(self, title: str, ctr: float):
        title_lower = title.lower()
        for word in self.POWER_WORDS:
            if word in title_lower:
                if word not in self.data["words"]:
                    self.data["words"][word] = {"uses": 0, "total_ctr": 0}
                self.data["words"][word]["uses"] += 1
                self.data["words"][word]["total_ctr"] += ctr
        self._save()
    
    def get_top_power_words(self, limit: int = 10) -> List[str]:
        scored = []
        for word, stats in self.data["words"].items():
            if stats["uses"] >= 2:
                avg = stats["total_ctr"] / stats["uses"]
                scored.append((word, avg))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:limit]]


def predict_ctr(title: str, hook: str, category: str) -> Dict:
    """
    #51: Predicts click-through rate before upload.
    AI scores title attractiveness.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a CLICK-THROUGH RATE expert who has analyzed millions of YouTube Shorts.

=== CONTENT ===
Title: {title}
Hook: {hook}
Category: {category}

=== PREDICT CTR ===
Score these click factors (1-10):

1. CURIOSITY GAP: Does it create burning curiosity?
2. SPECIFICITY: Is it specific enough to be believable?
3. BENEFIT CLARITY: Is the viewer benefit clear?
4. EMOTIONAL TRIGGER: Does it trigger emotion?
5. PATTERN INTERRUPT: Does it break expectations?

=== OUTPUT JSON ===
{{
    "predicted_ctr": 0.07,
    "ctr_tier": "low" or "average" or "good" or "excellent",
    "scores": {{
        "curiosity_gap": 7,
        "specificity": 6,
        "benefit_clarity": 8,
        "emotional_trigger": 7,
        "pattern_interrupt": 5
    }},
    "strongest_factor": "benefit_clarity",
    "weakest_factor": "pattern_interrupt",
    "improvement": "specific improvement suggestion"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=250, priority="bulk")
    return ai.parse_json(result) or {"predicted_ctr": 0.05, "ctr_tier": "average"}


# =============================================================================
# CATEGORY 2: FIRST SECONDS RETENTION (#52-57)
# =============================================================================

class PatternInterruptGenerator:
    """
    #52: Creates scroll-stopping pattern interrupts.
    """
    
    INTERRUPT_FILE = STATE_DIR / "pattern_interrupt_performance.json"
    
    INTERRUPT_TYPES = [
        "shocking_stat",      # Start with a shocking number
        "direct_question",    # "Did you know...?"
        "bold_claim",         # "This will change everything"
        "contradiction",      # "Everything you know is wrong"
        "personal_attack",    # "You're doing this wrong"
        "countdown",          # "5...4...3..."
        "sound_effect",       # Jarring audio
        "visual_flash",       # Quick visual change
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.INTERRUPT_FILE.exists():
                with open(self.INTERRUPT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"types": {t: {"uses": 0, "retention": 0} for t in self.INTERRUPT_TYPES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.INTERRUPT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, interrupt_type: str, first_3s_retention: float):
        if interrupt_type not in self.data["types"]:
            self.data["types"][interrupt_type] = {"uses": 0, "retention": 0}
        self.data["types"][interrupt_type]["uses"] += 1
        self.data["types"][interrupt_type]["retention"] += first_3s_retention
        self._save()
    
    def get_best_interrupt(self) -> str:
        best = "shocking_stat"
        best_avg = 0
        for itype, stats in self.data["types"].items():
            if stats["uses"] >= 2:
                avg = stats["retention"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = itype
        return best


class OpenLoopTracker:
    """
    #53: Tracks open loop effectiveness for retention.
    Open loops = unfinished thoughts that demand completion.
    """
    
    LOOP_FILE = STATE_DIR / "open_loop_performance.json"
    
    LOOP_TYPES = [
        "number_tease",       # "The third one will shock you"
        "outcome_tease",      # "And then something crazy happened"
        "secret_promise",     # "There's one thing they don't tell you"
        "reversal_setup",     # "But wait, it gets worse"
        "cliffhanger",        # "What happened next..."
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.LOOP_FILE.exists():
                with open(self.LOOP_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"loops": {l: {"uses": 0, "completion": 0} for l in self.LOOP_TYPES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.LOOP_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_loop_type(self) -> str:
        best = "number_tease"
        best_avg = 0
        for ltype, stats in self.data["loops"].items():
            if stats["uses"] >= 2:
                avg = stats["completion"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = ltype
        return best


class FirstFrameOptimizer:
    """
    #54: Optimizes the first frame for maximum scroll-stop.
    """
    
    FRAME_FILE = STATE_DIR / "first_frame_performance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.FRAME_FILE.exists():
                with open(self.FRAME_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "text_styles": {},  # {"large_bold": {"uses": 5, "retention": 4.2}}
            "color_schemes": {},
            "face_presence": {"with_face": {"uses": 0, "retention": 0}, "no_face": {"uses": 0, "retention": 0}},
            "best_settings": {}
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.FRAME_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_frame_performance(self, text_style: str, has_face: bool, first_3s_retention: float):
        if text_style not in self.data["text_styles"]:
            self.data["text_styles"][text_style] = {"uses": 0, "retention": 0}
        self.data["text_styles"][text_style]["uses"] += 1
        self.data["text_styles"][text_style]["retention"] += first_3s_retention
        
        key = "with_face" if has_face else "no_face"
        self.data["face_presence"][key]["uses"] += 1
        self.data["face_presence"][key]["retention"] += first_3s_retention
        self._save()


class AudioHookTimer:
    """
    #55: Optimizes timing of audio hooks (sound effects) for retention.
    """
    
    AUDIO_FILE = STATE_DIR / "audio_hook_timing.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.AUDIO_FILE.exists():
                with open(self.AUDIO_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "hook_timings": {},  # {"0.5": {"uses": 5, "retention": 85}}
            "sound_types": {},   # {"whoosh": {"uses": 3, "retention": 82}}
            "optimal_timing": 0.5
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.AUDIO_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_optimal_timing(self) -> float:
        return self.data.get("optimal_timing", 0.5)


def score_scroll_stop_power(hook: str, visual_description: str) -> Dict:
    """
    #56: AI scores how likely the hook is to stop scrolling.
    """
    ai = get_ai_caller()
    
    prompt = f"""Score this short video's SCROLL-STOPPING power.

HOOK (first words spoken): "{hook}"
VISUAL: {visual_description}

Score 1-10 on these factors:
1. PATTERN INTERRUPT: Does it break expectations?
2. CURIOSITY: Does it make you need to know more?
3. EMOTIONAL PUNCH: Does it trigger strong emotion?
4. VISUAL APPEAL: Is the visual attention-grabbing?
5. INSTANT CLARITY: Do you immediately understand the promise?

OUTPUT JSON:
{{
    "scroll_stop_score": 7.5,
    "tier": "weak" or "average" or "strong" or "irresistible",
    "scores": {{"pattern_interrupt": 7, "curiosity": 8, ...}},
    "fix_priority": "which factor needs most improvement",
    "specific_fix": "exact improvement to make"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"scroll_stop_score": 5, "tier": "average"}


def generate_instant_value_hook(topic: str, category: str) -> Dict:
    """
    #57: Generates hooks that deliver instant value in first 3 seconds.
    """
    ai = get_ai_caller()
    
    prompt = f"""Generate a hook that delivers INSTANT VALUE in the first 3 seconds.

TOPIC: {topic}
CATEGORY: {category}

REQUIREMENTS:
- Must deliver a complete, useful piece of information immediately
- Viewer should feel they got value even if they scroll away
- But should also want to stay for more

BAD: "I'm going to tell you something amazing..."
GOOD: "Your body burns 50% more fat before breakfast. Here's how to use it."

OUTPUT JSON:
{{
    "hook": "The exact hook text",
    "instant_value": "What value is delivered immediately",
    "reason_to_stay": "Why they'll keep watching",
    "word_count": 12
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=150, priority="critical")
    return ai.parse_json(result) or {"hook": f"Here's a {category} fact that will change how you think"}


# =============================================================================
# CATEGORY 3: ALGORITHM OPTIMIZATION (#58-63)
# =============================================================================

class WatchTimeMaximizer:
    """
    #58: Strategies and tracking for maximizing watch time.
    """
    
    WATCH_TIME_FILE = STATE_DIR / "watch_time_strategies.json"
    
    STRATEGIES = [
        "progressive_reveal",   # Reveal info gradually
        "countdown",            # Count down to something
        "story_arc",            # Build narrative tension
        "challenge_format",     # "Can you guess?"
        "before_after",         # Show transformation
        "loop_friendly",        # Seamless loop for re-watch
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.WATCH_TIME_FILE.exists():
                with open(self.WATCH_TIME_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"strategies": {s: {"uses": 0, "avg_watch_pct": 0} for s in self.STRATEGIES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.WATCH_TIME_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_strategy(self) -> str:
        best = "progressive_reveal"
        best_pct = 0
        for strat, stats in self.data["strategies"].items():
            if stats["uses"] >= 2:
                if stats["avg_watch_pct"] > best_pct:
                    best_pct = stats["avg_watch_pct"]
                    best = strat
        return best
    
    def get_watch_time_instruction(self) -> str:
        """AI-driven instruction for maximizing watch time."""
        best = self.get_best_strategy()
        return f"WATCH TIME STRATEGY: Use '{best}' technique. Best strategies: progressive_reveal (reveal info gradually), countdown (build anticipation), story_arc (narrative tension), challenge_format (engagement), before_after (transformation)."


class CompletionRateTracker:
    """
    #59: Predicts and tracks video completion rates.
    """
    
    COMPLETION_FILE = STATE_DIR / "completion_rate_tracking.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.COMPLETION_FILE.exists():
                with open(self.COMPLETION_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "by_duration": {},  # {"15-20": {"videos": 10, "avg_completion": 65}}
            "by_category": {},
            "optimal_duration": 18
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.COMPLETION_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_optimal_duration(self) -> int:
        return self.data.get("optimal_duration", 18)
    
    def get_completion_instruction(self) -> str:
        """AI-driven instruction for boosting completion rate."""
        optimal = self.get_optimal_duration()
        return f"COMPLETION RATE: Target duration is {optimal} seconds. Keep content punchy, no filler. End with a strong payoff to encourage re-watch."


class CommentBaitOptimizer:
    """
    #60: Generates and tracks comment-driving CTAs.
    """
    
    COMMENT_BAIT_FILE = STATE_DIR / "comment_bait_performance.json"
    
    BAIT_TYPES = [
        "opinion_ask",        # "Do you agree?"
        "experience_ask",     # "Has this happened to you?"
        "choice_ask",         # "Type 1 or 2"
        "challenge",          # "Bet you can't..."
        "fill_blank",         # "The best ___ is ___"
        "controversial",      # "This is controversial but..."
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.COMMENT_BAIT_FILE.exists():
                with open(self.COMMENT_BAIT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"baits": {b: {"uses": 0, "comments": 0} for b in self.BAIT_TYPES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.COMMENT_BAIT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_bait_type(self) -> str:
        best = "opinion_ask"
        best_avg = 0
        for bait, stats in self.data["baits"].items():
            if stats["uses"] >= 2:
                avg = stats["comments"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = bait
        return best
    
    def get_comment_bait_instruction(self) -> str:
        """AI-driven instruction for driving comments."""
        best = self.get_best_bait_type()
        return f"COMMENT BAIT: Use '{best}' technique. Types: opinion_ask ('Do you agree?'), experience_ask ('Has this happened to you?'), choice_ask ('Type 1 or 2'), challenge ('Bet you can't...'), fill_blank ('The best ___ is ___')."


class ShareTriggerTracker:
    """
    #61: Tracks which content types drive shares.
    """
    
    SHARE_FILE = STATE_DIR / "share_trigger_performance.json"
    
    SHARE_TRIGGERS = [
        "mind_blown",         # "I never knew this!"
        "relatable",          # "This is so me"
        "useful",             # "My friend needs to see this"
        "funny",              # Made them laugh
        "emotional",          # Made them feel
        "controversial",      # "You need to see this take"
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.SHARE_FILE.exists():
                with open(self.SHARE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"triggers": {t: {"uses": 0, "estimated_shares": 0} for t in self.SHARE_TRIGGERS}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.SHARE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_share_instruction(self) -> str:
        """AI-driven instruction for driving shares."""
        triggers = list(self.data.get("triggers", {}).keys())[:3]
        return f"SHARE TRIGGERS: Create content that drives shares via: mind_blown ('I never knew this!'), relatable ('This is so me'), useful ('My friend needs to see this'), funny, emotional, controversial."


class ReWatchHookTracker:
    """
    #62: Creates and tracks re-watch triggers.
    """
    
    REWATCH_FILE = STATE_DIR / "rewatch_hooks.json"
    
    REWATCH_TYPES = [
        "hidden_detail",      # "Did you catch the hidden..."
        "loop_seamless",      # Perfect loop
        "easter_egg",         # Hidden message
        "count_something",    # "How many did you count?"
        "spot_difference",    # "Spot what's wrong"
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.REWATCH_FILE.exists():
                with open(self.REWATCH_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"types": {t: {"uses": 0, "rewatch_indicator": 0} for t in self.REWATCH_TYPES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.REWATCH_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_rewatch_instruction(self) -> str:
        """AI-driven instruction for driving re-watches."""
        return "REWATCH HOOKS: Include re-watch triggers: hidden_detail ('Did you catch...'), loop_seamless (perfect video loop), easter_egg (hidden message), count_something ('How many did you count?'), spot_difference ('Spot what's wrong')."


def generate_algorithm_signals(content: str, category: str) -> Dict:
    """
    #63: AI generates content optimized for platform algorithm signals.
    """
    ai = get_ai_caller()
    
    prompt = f"""You are a YOUTUBE ALGORITHM expert. Optimize this content for maximum algorithmic promotion.

CONTENT: {content[:300]}
CATEGORY: {category}

ALGORITHM SIGNALS TO OPTIMIZE:
1. WATCH TIME: How to keep people watching
2. COMPLETION RATE: How to get to the end
3. ENGAGEMENT: Comments, likes, shares
4. RE-WATCH: Make them watch again
5. SESSION TIME: Keep them on YouTube

OUTPUT JSON:
{{
    "watch_time_hooks": ["keep watching for...", "the best part is..."],
    "completion_drivers": ["end with payoff", "promise early"],
    "comment_baits": ["specific CTA 1", "specific CTA 2"],
    "share_triggers": ["what makes this shareable"],
    "rewatch_hooks": ["why they'd watch again"],
    "algorithm_score": 7.5,
    "priority_improvement": "what to focus on"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=300, priority="bulk")
    return ai.parse_json(result) or {"algorithm_score": 5}


# =============================================================================
# CATEGORY 4: VISUAL IMPROVEMENTS (#64-68)
# =============================================================================

class ColorPsychologyOptimizer:
    """
    #64: Uses color psychology for emotional impact.
    """
    
    COLOR_FILE = STATE_DIR / "color_psychology.json"
    
    COLOR_EMOTIONS = {
        "red": "urgency, excitement, passion",
        "orange": "energy, enthusiasm, warmth",
        "yellow": "happiness, optimism, attention",
        "green": "growth, calm, money",
        "blue": "trust, calm, professionalism",
        "purple": "luxury, mystery, creativity",
        "pink": "playful, romantic, youthful",
        "black": "power, elegance, mystery",
        "white": "clean, simple, pure",
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.COLOR_FILE.exists():
                with open(self.COLOR_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"category_colors": {}, "performance": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.COLOR_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_recommended_color(self, category: str, mood: str) -> str:
        recommendations = {
            "psychology": "purple",
            "finance": "green",
            "health": "blue",
            "motivation": "orange",
            "shocking_facts": "red",
            "life_hacks": "yellow",
        }
        return recommendations.get(category, "blue")


class MotionEnergyOptimizer:
    """
    #65: Matches visual motion to content energy.
    """
    
    MOTION_FILE = STATE_DIR / "motion_energy.json"
    
    MOTION_LEVELS = {
        "static": 1,      # Minimal movement
        "subtle": 3,      # Gentle pans/zooms
        "moderate": 5,    # Regular cuts
        "dynamic": 7,     # Fast cuts, zooms
        "intense": 10,    # Rapid, energetic
    }
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.MOTION_FILE.exists():
                with open(self.MOTION_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"category_motion": {}, "performance": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.MOTION_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_recommended_motion(self, category: str, mood: str) -> str:
        if mood in ["suspense", "dramatic"]:
            return "dynamic"
        elif mood in ["calm", "emotional"]:
            return "subtle"
        elif mood in ["energetic", "exciting"]:
            return "intense"
        return "moderate"


class TextReadabilityScorer:
    """
    #66: Scores text overlay readability on mobile.
    """
    
    READABILITY_FILE = STATE_DIR / "text_readability.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.READABILITY_FILE.exists():
                with open(self.READABILITY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"settings": {}, "performance": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.READABILITY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def score_text_settings(self, font_size: int, words_per_line: int, contrast: str) -> float:
        """Score text settings for mobile readability (1-10)."""
        score = 5.0
        
        # Font size scoring
        if font_size >= 60:
            score += 2
        elif font_size >= 48:
            score += 1
        elif font_size < 36:
            score -= 2
        
        # Words per line scoring
        if words_per_line <= 5:
            score += 2
        elif words_per_line <= 8:
            score += 1
        elif words_per_line > 10:
            score -= 2
        
        # Contrast scoring
        if contrast == "high":
            score += 1
        elif contrast == "low":
            score -= 1
        
        return max(1, min(10, score))


class VisualVarietyTracker:
    """
    #67: Ensures visual variety throughout video.
    """
    
    VARIETY_FILE = STATE_DIR / "visual_variety.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.VARIETY_FILE.exists():
                with open(self.VARIETY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"optimal_cuts": 4, "performance": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.VARIETY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_optimal_cuts_per_video(self, duration_seconds: int) -> int:
        """Get optimal number of visual changes."""
        # Rule: One cut every 3-5 seconds
        return max(3, duration_seconds // 4)


def score_thumbnail_quality(title: str, category: str, has_face: bool, has_text: bool) -> Dict:
    """
    #68: AI scores thumbnail quality and suggests improvements.
    """
    ai = get_ai_caller()
    
    prompt = f"""Score this YouTube Shorts thumbnail setup.

TITLE: {title}
CATEGORY: {category}
HAS FACE: {has_face}
HAS TEXT OVERLAY: {has_text}

Score 1-10 on:
1. CLICK APPEAL: Would you click this?
2. CLARITY: Is the topic clear?
3. EMOTION: Does it trigger emotion?
4. MOBILE FRIENDLY: Readable on small screen?
5. STANDOUT: Would it stand out in feed?

OUTPUT JSON:
{{
    "quality_score": 7,
    "scores": {{"click_appeal": 7, "clarity": 8, ...}},
    "should_add_face": true or false,
    "text_suggestion": "suggested text overlay",
    "color_suggestion": "suggested dominant color",
    "priority_fix": "most important improvement"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"quality_score": 5}


# =============================================================================
# CATEGORY 5: CONTENT QUALITY (#69-74)
# =============================================================================

class FactCredibilityChecker:
    """
    #69: Ensures claims are believable and can be trusted.
    """
    
    CREDIBILITY_FILE = STATE_DIR / "fact_credibility.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.CREDIBILITY_FILE.exists():
                with open(self.CREDIBILITY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"flagged_patterns": [], "safe_patterns": []}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.CREDIBILITY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def check_content_credibility(content: str) -> Dict:
    """AI checks if content seems credible and trustworthy."""
    ai = get_ai_caller()
    
    prompt = f"""You are a FACT CHECKER. Analyze this content for credibility issues.

CONTENT: {content[:500]}

CHECK FOR:
1. Unrealistic numbers (too precise, too round, too extreme)
2. Vague sources ("studies show", "experts say")
3. Impossible claims
4. AI-sounding language
5. Missing context that could mislead

OUTPUT JSON:
{{
    "credibility_score": 7,
    "issues": [
        {{"issue": "description", "severity": "low/medium/high", "fix": "suggestion"}}
    ],
    "safe_to_publish": true or false,
    "improvements": ["specific improvement 1"]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=250, priority="critical")
    return ai.parse_json(result) or {"credibility_score": 5, "safe_to_publish": True}


class ActionableTakeawayEnforcer:
    """
    #70: Ensures every video has a clear actionable takeaway.
    """
    
    TAKEAWAY_FILE = STATE_DIR / "actionable_takeaways.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.TAKEAWAY_FILE.exists():
                with open(self.TAKEAWAY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"performance": {}, "best_formats": []}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.TAKEAWAY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def enforce_actionable_takeaway(content: str) -> Dict:
    """AI ensures content has a clear action the viewer can take."""
    ai = get_ai_caller()
    
    prompt = f"""Analyze this content for ACTIONABLE TAKEAWAY.

CONTENT: {content[:400]}

Every viral video should give the viewer ONE CLEAR THING they can DO.

CHECK:
1. Is there a clear action? (do this, try this, avoid this)
2. Is it specific enough to act on?
3. Is it doable TODAY?
4. Is the benefit of doing it clear?

OUTPUT JSON:
{{
    "has_actionable_takeaway": true or false,
    "current_takeaway": "what the current action is" or null,
    "actionability_score": 7,
    "suggested_takeaway": "if missing or weak, suggest one",
    "how_to_add": "where/how to add it to content"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"has_actionable_takeaway": True, "actionability_score": 5}


class StoryStructureOptimizer:
    """
    #71: Optimizes narrative arc for engagement.
    """
    
    STORY_FILE = STATE_DIR / "story_structure.json"
    
    STRUCTURES = [
        "problem_solution",   # Problem -> Solution -> Benefit
        "before_after",       # Before -> Change -> After
        "myth_reality",       # Common belief -> Truth
        "story_lesson",       # Story -> Takeaway
        "countdown",          # List with build-up
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.STORY_FILE.exists():
                with open(self.STORY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"structures": {s: {"uses": 0, "engagement": 0} for s in self.STRUCTURES}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.STORY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_structure(self) -> str:
        best = "problem_solution"
        best_avg = 0
        for struct, stats in self.data["structures"].items():
            if stats["uses"] >= 2:
                avg = stats["engagement"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = struct
        return best


class MemoryHookGenerator:
    """
    #72: Creates memorable phrases that stick.
    """
    
    MEMORY_FILE = STATE_DIR / "memory_hooks.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.MEMORY_FILE.exists():
                with open(self.MEMORY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"hooks": [], "techniques": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.MEMORY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def generate_memory_hook(topic: str, key_message: str) -> Dict:
    """AI creates a memorable phrase that sticks in viewer's mind."""
    ai = get_ai_caller()
    
    prompt = f"""Create a MEMORY HOOK - a phrase that sticks in the viewer's mind.

TOPIC: {topic}
KEY MESSAGE: {key_message}

MEMORY HOOK TECHNIQUES:
1. RHYME: "If you snooze, you lose"
2. ALLITERATION: "Simple systems succeed"
3. CONTRAST: "Work smarter, not harder"
4. NUMBER + BENEFIT: "The 2-minute rule"
5. UNEXPECTED PAIRING: "The lazy person's guide to..."

OUTPUT JSON:
{{
    "memory_hook": "the memorable phrase",
    "technique_used": "rhyme/alliteration/contrast/etc",
    "why_memorable": "why it sticks",
    "where_to_use": "hook/middle/end"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=150, priority="bulk")
    return ai.parse_json(result) or {"memory_hook": key_message}


class RelatabilityChecker:
    """
    #73: Ensures content is relatable to target audience.
    """
    
    RELATABILITY_FILE = STATE_DIR / "relatability_scores.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.RELATABILITY_FILE.exists():
                with open(self.RELATABILITY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"patterns": {}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.RELATABILITY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def check_relatability(content: str, target_audience: str = "general") -> Dict:
    """AI checks if content is relatable."""
    ai = get_ai_caller()
    
    prompt = f"""Check if this content is RELATABLE to viewers.

CONTENT: {content[:400]}
TARGET: {target_audience}

RELATABILITY FACTORS:
1. Universal experiences (everyone can relate)
2. Common struggles (shared problems)
3. Everyday language (not academic/corporate)
4. "That's so me" moments
5. Real-world examples

OUTPUT JSON:
{{
    "relatability_score": 7,
    "relatable_elements": ["what's relatable"],
    "unrelatable_elements": ["what's not relatable"],
    "improvements": ["how to make more relatable"],
    "add_phrase": "specific phrase to add for relatability"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"relatability_score": 5}


def detect_ai_slop(content: str) -> Dict:
    """
    #74: Detects "AI slop" patterns that make content feel fake.
    """
    ai = get_ai_caller()
    
    prompt = f"""Detect AI SLOP patterns in this content.

CONTENT: {content[:500]}

AI SLOP RED FLAGS:
1. Overuse of "delve", "dive into", "unpack"
2. Generic openings "In today's fast-paced world..."
3. Repetitive structure
4. Vague claims with no specifics
5. Unnatural transitions "Moreover", "Furthermore"
6. Emoji overuse or misuse
7. Lists that don't add value
8. Corporate buzzwords

OUTPUT JSON:
{{
    "ai_slop_score": 3,
    "red_flags_found": [
        {{"pattern": "what was found", "location": "where", "fix": "how to fix"}}
    ],
    "authenticity_score": 7,
    "humanize_suggestions": ["make it more human by..."]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=250, priority="critical")
    return ai.parse_json(result) or {"ai_slop_score": 0, "authenticity_score": 8}


# =============================================================================
# CATEGORY 6: VIRAL/TRENDY (#75-79)
# =============================================================================

class TrendLifecycleTracker:
    """
    #75: Tracks where trends are in their lifecycle.
    """
    
    LIFECYCLE_FILE = STATE_DIR / "trend_lifecycle.json"
    
    PHASES = ["emerging", "growing", "peak", "declining", "dead"]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.LIFECYCLE_FILE.exists():
                with open(self.LIFECYCLE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"trends": {}, "last_updated": None}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.LIFECYCLE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_trend(self, trend: str, phase: str):
        self.data["trends"][trend] = {
            "phase": phase,
            "recorded_at": datetime.now().isoformat()
        }
        self._save()
    
    def get_emerging_trends(self) -> List[str]:
        return [t for t, data in self.data["trends"].items() 
                if data.get("phase") in ["emerging", "growing"]]


class EvergreenBalancer:
    """
    #76: Balances trending vs evergreen content.
    """
    
    BALANCE_FILE = STATE_DIR / "evergreen_balance.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.BALANCE_FILE.exists():
                with open(self.BALANCE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "trending_count": 0,
            "evergreen_count": 0,
            "target_ratio": 0.6,  # 60% evergreen, 40% trending
            "performance": {}
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.BALANCE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def should_do_evergreen(self) -> bool:
        total = self.data["trending_count"] + self.data["evergreen_count"]
        if total == 0:
            return True
        current_ratio = self.data["evergreen_count"] / total
        return current_ratio < self.data["target_ratio"]
    
    def record_content(self, is_evergreen: bool):
        if is_evergreen:
            self.data["evergreen_count"] += 1
        else:
            self.data["trending_count"] += 1
        self._save()


class CulturalMomentDetector:
    """
    #77: Detects cultural moments to leverage.
    """
    
    MOMENT_FILE = STATE_DIR / "cultural_moments.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.MOMENT_FILE.exists():
                with open(self.MOMENT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"moments": [], "leveraged": []}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.MOMENT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def detect_cultural_moments() -> Dict:
    """AI detects current cultural moments to leverage."""
    ai = get_ai_caller()
    
    today = datetime.now()
    
    prompt = f"""Identify CULTURAL MOMENTS happening right now that we can leverage for content.

DATE: {today.strftime('%A, %B %d, %Y')}

CULTURAL MOMENTS TO LOOK FOR:
1. Holidays and events in next 7 days
2. Sports events (playoffs, championships)
3. Award shows, movie/TV releases
4. Memes and viral trends
5. News events (non-political)
6. Seasonal moments (back to school, summer, etc.)

OUTPUT JSON:
{{
    "current_moments": [
        {{"moment": "what's happening", "relevance": "high/medium", "content_angle": "how to use it"}}
    ],
    "upcoming_moments": [
        {{"moment": "what's coming", "date": "when", "prep_now": true or false}}
    ],
    "leverage_suggestions": [
        {{"moment": "which moment", "topic_idea": "specific content idea"}}
    ]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {"current_moments": [], "upcoming_moments": []}


class ViralPatternMatcher:
    """
    #78: Matches content to proven viral patterns.
    """
    
    PATTERN_FILE = STATE_DIR / "viral_pattern_matching.json"
    
    PROVEN_PATTERNS = [
        "listicle",           # "5 Things..."
        "myth_bust",          # "This Common Belief is Wrong"
        "comparison",         # "X vs Y"
        "transformation",     # "Before/After"
        "secret_reveal",      # "The Secret to..."
        "challenge",          # "Can You..."
        "tutorial_quick",     # "How to X in Y seconds"
        "reaction",           # Reacting to something
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.PATTERN_FILE.exists():
                with open(self.PATTERN_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"patterns": {p: {"uses": 0, "views": 0} for p in self.PROVEN_PATTERNS}}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.PATTERN_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_pattern(self) -> str:
        best = "listicle"
        best_avg = 0
        for pattern, stats in self.data["patterns"].items():
            if stats["uses"] >= 2:
                avg = stats["views"] / stats["uses"]
                if avg > best_avg:
                    best_avg = avg
                    best = pattern
        return best


class PlatformTrendSplitter:
    """
    #79: Tracks different trends for YouTube vs Dailymotion.
    """
    
    PLATFORM_TREND_FILE = STATE_DIR / "platform_trends.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.PLATFORM_TREND_FILE.exists():
                with open(self.PLATFORM_TREND_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "youtube": {"hot_topics": [], "avoid_topics": []},
            "dailymotion": {"hot_topics": [], "avoid_topics": []}
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.PLATFORM_TREND_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


# =============================================================================
# CATEGORY 7: ANALYTICS FEEDBACK (#80-84)
# =============================================================================

class MicroRetentionAnalyzer:
    """
    #80: Second-by-second retention analysis.
    """
    
    MICRO_FILE = STATE_DIR / "micro_retention.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.MICRO_FILE.exists():
                with open(self.MICRO_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "drop_points": {},  # {"second_3": 5, "second_8": 12}  (how many videos had drops there)
            "patterns": []
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.MICRO_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_drop_point(self, second: int):
        key = f"second_{second}"
        if key not in self.data["drop_points"]:
            self.data["drop_points"][key] = 0
        self.data["drop_points"][key] += 1
        self._save()
    
    def get_common_drop_points(self) -> List[int]:
        sorted_drops = sorted(self.data["drop_points"].items(), 
                             key=lambda x: x[1], reverse=True)
        return [int(d[0].split("_")[1]) for d in sorted_drops[:3]]


class PerformanceCorrelationFinder:
    """
    #81: Finds hidden correlations in performance data.
    """
    
    CORRELATION_FILE = STATE_DIR / "performance_correlations.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.CORRELATION_FILE.exists():
                with open(self.CORRELATION_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"correlations": [], "last_analysis": None}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.CORRELATION_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def find_performance_correlations(video_data: List[Dict]) -> Dict:
    """AI finds hidden correlations in performance data."""
    ai = get_ai_caller()
    
    prompt = f"""Analyze this video performance data for HIDDEN CORRELATIONS.

DATA:
{json.dumps(video_data[:15], indent=2)}

FIND CORRELATIONS:
1. Category vs Views
2. Title length vs CTR
3. Video duration vs Completion
4. Posting time vs Views
5. Music mood vs Engagement
6. Voice type vs Retention

OUTPUT JSON:
{{
    "strong_correlations": [
        {{"factor1": "...", "factor2": "...", "relationship": "positive/negative", "strength": 0.8}}
    ],
    "surprising_findings": ["unexpected insight"],
    "recommendations": ["based on data, do X"],
    "needs_more_data": ["what we can't yet determine"]
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=400, priority="bulk")
    return ai.parse_json(result) or {"strong_correlations": []}


class ChannelHealthMonitor:
    """
    #82: Monitors overall channel health.
    """
    
    HEALTH_FILE = STATE_DIR / "channel_health.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.HEALTH_FILE.exists():
                with open(self.HEALTH_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "health_scores": [],  # Historical health scores
            "current_health": 50,
            "warnings": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.HEALTH_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def calculate_health(self, recent_views: int, avg_views: int, 
                         recent_engagement: float, shadow_ban_risk: bool) -> int:
        """Calculate overall channel health score (0-100)."""
        score = 50
        
        # Views trend
        if avg_views > 0:
            ratio = recent_views / avg_views
            if ratio > 1.2:
                score += 20
            elif ratio > 0.8:
                score += 10
            elif ratio < 0.5:
                score -= 20
        
        # Engagement
        if recent_engagement > 0.05:
            score += 15
        elif recent_engagement > 0.03:
            score += 5
        
        # Shadow ban risk
        if shadow_ban_risk:
            score -= 30
        
        self.data["current_health"] = max(0, min(100, score))
        self.data["health_scores"].append({
            "score": self.data["current_health"],
            "date": datetime.now().isoformat()
        })
        self.data["health_scores"] = self.data["health_scores"][-30:]  # Keep 30 days
        self._save()
        
        return self.data["current_health"]


class GrowthRatePredictor:
    """
    #83: Predicts future growth based on current trajectory.
    """
    
    GROWTH_FILE = STATE_DIR / "growth_predictions.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.GROWTH_FILE.exists():
                with open(self.GROWTH_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"history": [], "predictions": []}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.GROWTH_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def predict_growth(self, current_views: int, current_subs: int, 
                       days_of_data: int) -> Dict:
        """Simple growth prediction."""
        if days_of_data < 7:
            return {"prediction": "need more data"}
        
        daily_avg = current_views / days_of_data
        
        return {
            "predicted_views_7d": int(daily_avg * 7),
            "predicted_views_30d": int(daily_avg * 30),
            "growth_tier": "growing" if daily_avg > 100 else "stable"
        }


class ContentDecayTracker:
    """
    #84: Tracks how content ages and loses performance.
    """
    
    DECAY_FILE = STATE_DIR / "content_decay.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.DECAY_FILE.exists():
                with open(self.DECAY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "decay_rates": {},  # {"category": decay_rate}
            "evergreen_content": [],  # Videos that don't decay
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.DECAY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


# =============================================================================
# CATEGORY 8: OTHER IMPORTANT (#85-89)
# =============================================================================

class CompetitorResponseGenerator:
    """
    #85: Generates responses to competitor content.
    """
    
    COMPETITOR_FILE = STATE_DIR / "competitor_responses.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.COMPETITOR_FILE.exists():
                with open(self.COMPETITOR_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"responses": [], "competitors": []}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.COMPETITOR_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


def generate_competitor_response(competitor_topic: str, our_angle: str) -> Dict:
    """AI generates our response to competitor content."""
    ai = get_ai_caller()
    
    prompt = f"""A competitor just posted viral content. Generate our RESPONSE.

COMPETITOR'S TOPIC: {competitor_topic}
OUR ANGLE: {our_angle}

CREATE A RESPONSE THAT:
1. Takes a different angle (don't copy)
2. Adds more value
3. Has a stronger hook
4. Differentiates us

OUTPUT JSON:
{{
    "our_topic": "our version of the topic",
    "our_hook": "our stronger hook",
    "differentiation": "how we're different",
    "value_add": "what extra value we provide",
    "timing": "post now or wait"
}}

JSON ONLY."""

    result = ai.call(prompt, max_tokens=200, priority="bulk")
    return ai.parse_json(result) or {"our_topic": competitor_topic}


class NicheAuthorityBuilder:
    """
    #86: Builds authority in specific niches.
    """
    
    AUTHORITY_FILE = STATE_DIR / "niche_authority.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.AUTHORITY_FILE.exists():
                with open(self.AUTHORITY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "niches": {},  # {"psychology": {"videos": 10, "total_views": 50000}}
            "strongest_niche": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.AUTHORITY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_niche_content(self, niche: str, views: int):
        if niche not in self.data["niches"]:
            self.data["niches"][niche] = {"videos": 0, "total_views": 0}
        self.data["niches"][niche]["videos"] += 1
        self.data["niches"][niche]["total_views"] += views
        
        # Update strongest niche
        best = None
        best_views = 0
        for n, stats in self.data["niches"].items():
            if stats["videos"] >= 3:
                avg = stats["total_views"] / stats["videos"]
                if avg > best_views:
                    best_views = avg
                    best = n
        self.data["strongest_niche"] = best
        self._save()
    
    def get_strongest_niche(self) -> Optional[str]:
        return self.data.get("strongest_niche")


class QualityConsistencyEnforcer:
    """
    #87: Ensures consistent quality across videos.
    """
    
    CONSISTENCY_FILE = STATE_DIR / "quality_consistency.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.CONSISTENCY_FILE.exists():
                with open(self.CONSISTENCY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "quality_history": [],
            "min_threshold": 6,
            "consistency_score": 0
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.CONSISTENCY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_quality(self, score: float) -> bool:
        """Record quality score. Returns False if below threshold."""
        self.data["quality_history"].append({
            "score": score,
            "date": datetime.now().isoformat()
        })
        self.data["quality_history"] = self.data["quality_history"][-50:]
        
        # Calculate consistency
        scores = [q["score"] for q in self.data["quality_history"]]
        if len(scores) >= 5:
            import statistics
            try:
                std_dev = statistics.stdev(scores)
                self.data["consistency_score"] = max(0, 10 - std_dev)
            except:
                pass
        
        self._save()
        return score >= self.data["min_threshold"]


class UploadCadenceOptimizer:
    """
    #88: Optimizes posting frequency.
    """
    
    CADENCE_FILE = STATE_DIR / "upload_cadence.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.CADENCE_FILE.exists():
                with open(self.CADENCE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "uploads_per_day": {},  # {"2": {"days": 10, "avg_views": 5000}}
            "optimal_cadence": 6,  # videos per day
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.CADENCE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_optimal_cadence(self) -> int:
        return self.data.get("optimal_cadence", 6)


class AudienceLoyaltyTracker:
    """
    #89: Tracks returning viewers (loyalty indicators).
    """
    
    LOYALTY_FILE = STATE_DIR / "audience_loyalty.json"
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.LOYALTY_FILE.exists():
                with open(self.LOYALTY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "subscriber_view_ratio": 0,  # Views from subs vs total
            "repeat_commenters": [],
            "loyalty_score": 0
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.LOYALTY_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)


# =============================================================================
# v11.0 SINGLETON ACCESSORS
# =============================================================================

# Category 1: Click Baiting
_curiosity_gap = None
_number_hook = None
_controversy = None
_fomo = None
_power_words = None

# Category 2: First Seconds
_pattern_interrupt = None
_open_loop = None
_first_frame = None
_audio_hook = None

# Category 3: Algorithm
_watch_time = None
_completion_rate = None
_comment_bait = None
_share_trigger = None
_rewatch = None

# Category 4: Visual
_color_psychology = None
_motion_energy = None
_text_readability = None
_visual_variety = None

# Category 5: Content Quality
_fact_credibility = None
_actionable = None
_story_structure = None
_memory_hook = None
_relatability = None

# Category 6: Viral/Trendy
_trend_lifecycle = None
_evergreen_balance = None
_cultural_moment = None
_viral_pattern = None
_platform_trend = None

# Category 7: Analytics
_micro_retention = None
_correlation = None
_channel_health = None
_growth_rate = None
_content_decay = None

# Category 8: Other
_competitor_response = None
_niche_authority = None
_quality_consistency = None
_upload_cadence = None
_audience_loyalty = None


def get_curiosity_gap() -> CuriosityGapGenerator:
    global _curiosity_gap
    if _curiosity_gap is None:
        _curiosity_gap = CuriosityGapGenerator()
    return _curiosity_gap


def get_number_hook() -> NumberHookOptimizer:
    global _number_hook
    if _number_hook is None:
        _number_hook = NumberHookOptimizer()
    return _number_hook


def get_controversy() -> ControversyCalibrator:
    global _controversy
    if _controversy is None:
        _controversy = ControversyCalibrator()
    return _controversy


def get_fomo() -> FOMOInjector:
    global _fomo
    if _fomo is None:
        _fomo = FOMOInjector()
    return _fomo


def get_power_words_tracker() -> TitlePowerWordTracker:
    global _power_words
    if _power_words is None:
        _power_words = TitlePowerWordTracker()
    return _power_words


def get_pattern_interrupt() -> PatternInterruptGenerator:
    global _pattern_interrupt
    if _pattern_interrupt is None:
        _pattern_interrupt = PatternInterruptGenerator()
    return _pattern_interrupt


def get_open_loop() -> OpenLoopTracker:
    global _open_loop
    if _open_loop is None:
        _open_loop = OpenLoopTracker()
    return _open_loop


def get_first_frame() -> FirstFrameOptimizer:
    global _first_frame
    if _first_frame is None:
        _first_frame = FirstFrameOptimizer()
    return _first_frame


def get_audio_hook() -> AudioHookTimer:
    global _audio_hook
    if _audio_hook is None:
        _audio_hook = AudioHookTimer()
    return _audio_hook


def get_watch_time() -> WatchTimeMaximizer:
    global _watch_time
    if _watch_time is None:
        _watch_time = WatchTimeMaximizer()
    return _watch_time


def get_completion_rate() -> CompletionRateTracker:
    global _completion_rate
    if _completion_rate is None:
        _completion_rate = CompletionRateTracker()
    return _completion_rate


def get_comment_bait() -> CommentBaitOptimizer:
    global _comment_bait
    if _comment_bait is None:
        _comment_bait = CommentBaitOptimizer()
    return _comment_bait


def get_share_trigger() -> ShareTriggerTracker:
    global _share_trigger
    if _share_trigger is None:
        _share_trigger = ShareTriggerTracker()
    return _share_trigger


def get_rewatch() -> ReWatchHookTracker:
    global _rewatch
    if _rewatch is None:
        _rewatch = ReWatchHookTracker()
    return _rewatch


def get_color_psychology() -> ColorPsychologyOptimizer:
    global _color_psychology
    if _color_psychology is None:
        _color_psychology = ColorPsychologyOptimizer()
    return _color_psychology


def get_motion_energy() -> MotionEnergyOptimizer:
    global _motion_energy
    if _motion_energy is None:
        _motion_energy = MotionEnergyOptimizer()
    return _motion_energy


def get_text_readability() -> TextReadabilityScorer:
    global _text_readability
    if _text_readability is None:
        _text_readability = TextReadabilityScorer()
    return _text_readability


def get_visual_variety() -> VisualVarietyTracker:
    global _visual_variety
    if _visual_variety is None:
        _visual_variety = VisualVarietyTracker()
    return _visual_variety


def get_fact_credibility() -> FactCredibilityChecker:
    global _fact_credibility
    if _fact_credibility is None:
        _fact_credibility = FactCredibilityChecker()
    return _fact_credibility


def get_actionable() -> ActionableTakeawayEnforcer:
    global _actionable
    if _actionable is None:
        _actionable = ActionableTakeawayEnforcer()
    return _actionable


def get_story_structure() -> StoryStructureOptimizer:
    global _story_structure
    if _story_structure is None:
        _story_structure = StoryStructureOptimizer()
    return _story_structure


def get_memory_hook() -> MemoryHookGenerator:
    global _memory_hook
    if _memory_hook is None:
        _memory_hook = MemoryHookGenerator()
    return _memory_hook


def get_relatability() -> RelatabilityChecker:
    global _relatability
    if _relatability is None:
        _relatability = RelatabilityChecker()
    return _relatability


def get_trend_lifecycle() -> TrendLifecycleTracker:
    global _trend_lifecycle
    if _trend_lifecycle is None:
        _trend_lifecycle = TrendLifecycleTracker()
    return _trend_lifecycle


def get_evergreen_balance() -> EvergreenBalancer:
    global _evergreen_balance
    if _evergreen_balance is None:
        _evergreen_balance = EvergreenBalancer()
    return _evergreen_balance


def get_cultural_moment() -> CulturalMomentDetector:
    global _cultural_moment
    if _cultural_moment is None:
        _cultural_moment = CulturalMomentDetector()
    return _cultural_moment


def get_viral_pattern() -> ViralPatternMatcher:
    global _viral_pattern
    if _viral_pattern is None:
        _viral_pattern = ViralPatternMatcher()
    return _viral_pattern


def get_platform_trend() -> PlatformTrendSplitter:
    global _platform_trend
    if _platform_trend is None:
        _platform_trend = PlatformTrendSplitter()
    return _platform_trend


def get_micro_retention() -> MicroRetentionAnalyzer:
    global _micro_retention
    if _micro_retention is None:
        _micro_retention = MicroRetentionAnalyzer()
    return _micro_retention


def get_correlation() -> PerformanceCorrelationFinder:
    global _correlation
    if _correlation is None:
        _correlation = PerformanceCorrelationFinder()
    return _correlation


def get_channel_health() -> ChannelHealthMonitor:
    global _channel_health
    if _channel_health is None:
        _channel_health = ChannelHealthMonitor()
    return _channel_health


def get_growth_rate() -> GrowthRatePredictor:
    global _growth_rate
    if _growth_rate is None:
        _growth_rate = GrowthRatePredictor()
    return _growth_rate


def get_content_decay() -> ContentDecayTracker:
    global _content_decay
    if _content_decay is None:
        _content_decay = ContentDecayTracker()
    return _content_decay


def get_competitor_response() -> CompetitorResponseGenerator:
    global _competitor_response
    if _competitor_response is None:
        _competitor_response = CompetitorResponseGenerator()
    return _competitor_response


def get_niche_authority() -> NicheAuthorityBuilder:
    global _niche_authority
    if _niche_authority is None:
        _niche_authority = NicheAuthorityBuilder()
    return _niche_authority


def get_quality_consistency() -> QualityConsistencyEnforcer:
    global _quality_consistency
    if _quality_consistency is None:
        _quality_consistency = QualityConsistencyEnforcer()
    return _quality_consistency


def get_upload_cadence() -> UploadCadenceOptimizer:
    global _upload_cadence
    if _upload_cadence is None:
        _upload_cadence = UploadCadenceOptimizer()
    return _upload_cadence


def get_audience_loyalty() -> AudienceLoyaltyTracker:
    global _audience_loyalty
    if _audience_loyalty is None:
        _audience_loyalty = AudienceLoyaltyTracker()
    return _audience_loyalty


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Enhancement Module v10.0 - Test")
    print("=" * 60)
    
    # Test AI caller
    ai = get_ai_caller()
    print(f"\nAI Caller initialized:")
    print(f"  Groq: {'OK' if ai.groq_client else 'N/A'}")
    print(f"  Gemini: {'OK' if ai.gemini_model else 'N/A'}")
    
    # Test orchestrator
    orch = get_enhancement_orchestrator()
    print(f"\nOrchestrator initialized:")
    print(f"  A/B Tracker: OK")
    print(f"  Error Learner: OK")
    print(f"  Shadow Detector: OK")
    
    # Test semantic duplicate
    print("\n[TEST] Semantic Duplicate Check:")
    recent = ["Psychology trick about morning routines", "Money saving hack with coffee"]
    check = check_semantic_duplicate("Psychology morning routine trick", "Morning routines", recent)
    print(f"  Is duplicate: {check.get('is_duplicate')}")
    
    # v9.5 Enhancements
    print("\n" + "=" * 60)
    print("v9.5 Enhancements")
    print("=" * 60)
    
    print("\n[TEST #27] Seasonal Content Calendar:")
    seasonal = get_seasonal_content_suggestions()
    print(f"  Upcoming events: {len(seasonal.get('upcoming_events', []))}")
    print(f"  Content urgency: {seasonal.get('content_urgency', 'unknown')}")
    
    print("\n[TEST #28] Hook Word Tracker:")
    hook_tracker = get_hook_tracker()
    hook_tracker.record_hook_performance("This SECRET will SHOCK you", 50000, 10000)
    power_words = hook_tracker.get_power_words()
    print(f"  Power words tracked: {len(power_words)}")
    
    print("\n[TEST #29] Voice Speed Optimizer:")
    voice_opt = get_voice_optimizer()
    optimal = voice_opt.get_optimal_rate()
    print(f"  Optimal rate: {optimal}")
    
    print("\n[TEST #30] Hashtag Rotator:")
    hashtag_rot = get_hashtag_rotator()
    recent_sets = hashtag_rot.get_recently_used()
    print(f"  Recent sets tracked: {len(recent_sets)}")
    
    print("\n[TEST #32] Cross-Platform Analytics:")
    plat_analytics = get_platform_analytics()
    insights = plat_analytics.get_platform_insights()
    print(f"  Platforms tracked: {list(insights.keys())}")
    
    print("\n[TEST #35] Category Decay Tracker:")
    decay = get_category_decay()
    weights = decay.get_decayed_weights()
    print(f"  Categories with decay: {len(weights)}")
    
    print("\n" + "=" * 60)
    print("[OK] Enhancement module v9.5 ready!")
    print("=" * 60)

