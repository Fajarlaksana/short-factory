#!/usr/bin/env python3
"""
ViralShorts Factory - Smart Model Router v17.9.9
=================================================

INTELLIGENT model selection that:
1. Routes each PROMPT TYPE to the BEST model for that type
2. Updates model rankings PERIODICALLY (weekly by default)
3. Has FALLBACK CHAINS for every prompt type
4. GUARANTEES eventual success (never runs out of quota)
5. Uses PROMPTS REGISTRY to learn optimal models per prompt

ARCHITECTURE:
- NOT hardcoded - model rankings are discovered and cached
- Periodic re-evaluation (weekly) to adapt to new models
- Prompt classification -> Model selection -> Fallback chain
- Prompts Registry tracks which models work best for which prompts

PROMPT TYPES:
- CREATIVE: Topics, scripts, hooks, CTAs (need human-like creativity)
- EVALUATION: Scoring, quality checks (need structured output)
- SIMPLE: Hashtags, keywords, SEO (speed matters most)
- ANALYSIS: Analytics, trends, strategy (need deep reasoning)
"""

import os
import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

# State directory for caching
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

ROUTER_CACHE_FILE = STATE_DIR / "smart_router_cache.json"
ROUTER_STATS_FILE = STATE_DIR / "smart_router_stats.json"


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# PROMPT TYPE DEFINITIONS
# =============================================================================

@dataclass
class PromptType:
    """Definition of a prompt type with its characteristics."""
    name: str
    keywords: List[str]  # Keywords to identify this type
    needs_creativity: bool  # High creativity needed?
    needs_structure: bool  # Structured JSON output needed?
    needs_speed: bool  # Speed over quality?
    needs_reasoning: bool  # Deep reasoning needed?
    max_tokens: int  # Typical max tokens
    priority: str  # "critical", "normal", "bulk"


# Define prompt types with their characteristics
PROMPT_TYPES = {
    "creative": PromptType(
        name="creative",
        keywords=["topic", "content", "hook", "voiceover", "cta", "script", 
                  "generation", "viral", "engagement", "reply", "series"],
        needs_creativity=True,
        needs_structure=False,
        needs_speed=False,
        needs_reasoning=False,
        max_tokens=2000,
        priority="critical"
    ),
    "evaluation": PromptType(
        name="evaluation",
        keywords=["evaluation", "evaluate", "quality", "score", "check", 
                  "gate", "velocity", "validate", "assessment"],
        needs_creativity=False,
        needs_structure=True,
        needs_speed=False,
        needs_reasoning=True,
        max_tokens=1500,
        priority="critical"
    ),
    "simple": PromptType(
        name="simple",
        keywords=["hashtag", "keyword", "seo", "description", "broll", 
                  "thumbnail", "sentiment", "tag", "metadata"],
        needs_creativity=False,
        needs_structure=True,
        needs_speed=True,
        needs_reasoning=False,
        max_tokens=500,
        priority="normal"
    ),
    "analysis": PromptType(
        name="analysis",
        keywords=["analysis", "analytics", "trend", "strategy", "growth",
                  "competitor", "deep", "insight", "correlation", "pattern"],
        needs_creativity=False,
        needs_structure=True,
        needs_speed=False,
        needs_reasoning=True,
        max_tokens=1500,
        priority="bulk"
    )
}


# =============================================================================
# MODEL DEFINITIONS (Discovered, not hardcoded)
# =============================================================================

@dataclass
class ModelInfo:
    """Information about a model."""
    provider: str  # "groq", "gemini", "openrouter", "huggingface"
    model_id: str  # Full model identifier
    daily_limit: int  # Estimated daily limit
    rate_limit: int  # Requests per minute
    delay: float  # Recommended delay between calls
    quality_general: float  # General quality (1-10)
    quality_creative: float  # Quality for creative tasks
    quality_structured: float  # Quality for structured output
    quality_speed: float  # Speed rating (1-10, 10=fastest)
    robustness: float  # Success rate (0-1)
    available: bool  # Currently available?
    # v17.9.10: Usage tracking to prevent quota exhaustion
    calls_today: int = 0  # Track calls made today
    last_call_date: str = ""  # Date of last call (YYYY-MM-DD)
    consecutive_failures: int = 0  # Track failures to deprioritize broken models


# =============================================================================
# RATE LIMIT SAFETY MARGIN (v17.9.33)
# =============================================================================
# 10% safety margin on all delays to ensure ZERO 429 errors
# 
# Formula: safe_delay = (60 / requests_per_minute) * 1.10
# Example: 15 RPM -> 4.0s base -> 4.4s with margin
#
RATE_LIMIT_MARGIN = 1.10  # 10% safety buffer


_NON_TEXT_MODEL_MARKERS = ("tts", "image", "lyria", "robotics", "computer-use", "transcribe",
                           "embedding", "deep-research", "antigravity", "banana", "customtools",
                           "veo", "imagen", "aqa", "learnlm", "guard")


def _is_text_model_name(name: str) -> bool:
    """True if the model name looks like a general text-generation model."""
    name = name.lower()
    return not any(marker in name for marker in _NON_TEXT_MODEL_MARKERS)


def _safe_delay(rpm: int) -> float:
    """Calculate delay with 10% safety margin."""
    return round((60.0 / rpm) * RATE_LIMIT_MARGIN, 1)


# Default model pool (discovered dynamically, this is fallback)
# v17.9.33: All delays now include 10% safety margin
DEFAULT_MODELS = {
    # Groq - shared 14,400/day quota across all models
    "groq:llama-3.3-70b-versatile": ModelInfo(
        provider="groq", model_id="llama-3.3-70b-versatile",
        daily_limit=300, rate_limit=30, delay=_safe_delay(30),  # 2.2s
        quality_general=8.5, quality_creative=9.0, quality_structured=8.0, quality_speed=9.0,
        robustness=0.98, available=True
    ),
    # REMOVED: llama-3.1-70b-versatile - DECOMMISSIONED by Groq (Jan 2026)
    "groq:llama-3.1-8b-instant": ModelInfo(
        provider="groq", model_id="llama-3.1-8b-instant",
        daily_limit=600, rate_limit=60, delay=_safe_delay(60),  # 1.1s
        quality_general=7.0, quality_creative=6.5, quality_structured=7.0, quality_speed=10.0,
        robustness=0.99, available=True
    ),
    # REMOVED: mixtral-8x7b-32768 - DECOMMISSIONED by Groq (Jan 2026)
    # Gemini - separate quotas per model
    "gemini:gemini-1.5-flash": ModelInfo(
        provider="gemini", model_id="gemini-1.5-flash",
        daily_limit=1500, rate_limit=15, delay=_safe_delay(15),  # 4.4s
        quality_general=7.5, quality_creative=7.0, quality_structured=8.5, quality_speed=8.0,
        robustness=0.95, available=True
    ),
    "gemini:gemini-2.0-flash": ModelInfo(
        provider="gemini", model_id="gemini-2.0-flash",
        daily_limit=500, rate_limit=15, delay=_safe_delay(15),  # 4.4s
        quality_general=8.0, quality_creative=7.5, quality_structured=9.0, quality_speed=8.0,
        robustness=0.92, available=True
    ),
    # REMOVED: gemini-1.5-pro - Returns 404 "not found for API version v1beta" (Jan 2026)
    # OpenRouter (free) - generous limits
    "openrouter:meta-llama/llama-3.2-3b-instruct:free": ModelInfo(
        provider="openrouter", model_id="meta-llama/llama-3.2-3b-instruct:free",
        daily_limit=10000, rate_limit=60, delay=_safe_delay(60),  # 1.1s
        quality_general=6.5, quality_creative=6.0, quality_structured=6.5, quality_speed=9.0,
        robustness=0.90, available=True
    ),
    "openrouter:google/gemma-2-9b-it:free": ModelInfo(
        provider="openrouter", model_id="google/gemma-2-9b-it:free",
        daily_limit=10000, rate_limit=60, delay=_safe_delay(60),  # 1.1s
        quality_general=7.0, quality_creative=6.5, quality_structured=7.0, quality_speed=8.5,
        robustness=0.88, available=True
    ),
    # HuggingFace - rate limiting is more lenient
    "huggingface:HuggingFaceH4/zephyr-7b-beta": ModelInfo(
        provider="huggingface", model_id="HuggingFaceH4/zephyr-7b-beta",
        daily_limit=2400, rate_limit=100, delay=_safe_delay(100),  # 0.7s
        quality_general=7.5, quality_creative=7.0, quality_structured=7.5, quality_speed=5.0,
        robustness=0.80, available=True
    ),
}


# =============================================================================
# SMART MODEL ROUTER
# =============================================================================

class SmartModelRouter:
    """
    Intelligently routes prompts to the best available model.
    
    Features:
    - Classifies prompts by type (creative, evaluation, simple, analysis)
    - Selects best model for each type
    - Periodic re-evaluation of model rankings (default: weekly)
    - Fallback chains guarantee eventual success
    - Tracks usage and success rates
    - v17.9.43: Per-model daily usage tracking for quota rotation
    """
    
    # How often to refresh model rankings (in seconds)
    REFRESH_INTERVAL = 24 * 3600  # 24 hours - v17.9.45: More frequent to catch deprecated models
    
    # v17.9.43: ACTUAL per-model daily quotas (from error messages)
    MODEL_DAILY_QUOTAS = {
        # Gemini: 20 RPD per model (free tier!)
        "gemini-2.5-flash": 20,
        "gemini-2.5-pro": 20,
        "gemini-2.0-flash-exp": 20,
        "gemini-2.0-flash": 20,
        "gemini-1.5-flash": 20,
        # REMOVED: gemini-1.5-pro - deprecated (404)
        # Groq: Token-based (100K for 70b, 500K for 8b)
        "llama-3.3-70b-versatile": 50,   # ~100K TPD / 2K per call
        "llama-3.1-8b-instant": 250,     # ~500K TPD / 2K per call
        "mixtral-8x7b-32768": 100,
    }
    
    def __init__(self):
        self.models = {}
        self.rankings = {}  # {prompt_type: [ordered list of model keys]}
        self.stats = {"calls": 0, "successes": 0, "fallbacks": 0}
        self.last_refresh = None
        
        # v17.9.43: Per-model usage tracking (resets daily)
        self.model_usage_today = {}  # {model_name: count}
        self.usage_date = None  # Track which day the usage is for
        
        # Load cached data or initialize
        self._load_cache()
        
        # Refresh if needed
        if self._needs_refresh():
            self.refresh_rankings()
    
    def _load_cache(self):
        """Load cached router data."""
        try:
            if ROUTER_CACHE_FILE.exists():
                with open(ROUTER_CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self.rankings = data.get("rankings", {})
                    self.last_refresh = data.get("last_refresh")
                    # Reconstruct models from cache
                    for key, model_data in data.get("models", {}).items():
                        self.models[key] = ModelInfo(**model_data)
                    safe_print(f"[ROUTER] Loaded cached rankings from {self.last_refresh}")
            else:
                self._use_defaults()
        except Exception as e:
            safe_print(f"[ROUTER] Cache load failed: {e}, using defaults")
            self._use_defaults()
        
        # Load stats
        try:
            if ROUTER_STATS_FILE.exists():
                with open(ROUTER_STATS_FILE, 'r') as f:
                    self.stats = json.load(f)
        except:
            pass
    
    def _use_defaults(self):
        """Use default model pool."""
        self.models = DEFAULT_MODELS.copy()
        self._compute_rankings()
    
    def _save_cache(self):
        """Save router data to cache."""
        try:
            data = {
                "rankings": self.rankings,
                "last_refresh": self.last_refresh,
                "models": {k: asdict(v) for k, v in self.models.items()}
            }
            with open(ROUTER_CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            safe_print(f"[ROUTER] Cache save failed: {e}")
    
    def _save_stats(self):
        """Save usage stats."""
        try:
            with open(ROUTER_STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def _needs_refresh(self) -> bool:
        """Check if rankings need refresh."""
        if not self.last_refresh:
            return True
        if not self.rankings:
            return True
        
        try:
            last = datetime.fromisoformat(self.last_refresh)
            return (datetime.now() - last).total_seconds() > self.REFRESH_INTERVAL
        except:
            return True
    
    def refresh_rankings(self):
        """
        Refresh model rankings by:
        1. Discovering available models from each provider
        2. Testing availability
        3. Computing rankings for each prompt type
        
        Called periodically (weekly by default) or on-demand.
        """
        safe_print("[ROUTER] Refreshing model rankings...")
        
        # Start with defaults
        self.models = DEFAULT_MODELS.copy()
        
        # Discover additional models from each provider
        self._discover_groq_models()
        self._discover_gemini_models()
        self._discover_openrouter_models()
        self._discover_huggingface_models()
        
        # Compute rankings for each prompt type
        self._compute_rankings()
        
        # Save to cache
        self.last_refresh = datetime.now().isoformat()
        self._save_cache()
        
        safe_print(f"[ROUTER] Rankings updated: {len(self.models)} models, "
                   f"{len(self.rankings)} prompt types")
    
    def _discover_groq_models(self):
        """
        Discover available Groq models - DYNAMIC capability detection.
        
        v18.6: DYNAMIC FILTERING (not hardcoded!)
        - Tests each model with a minimal chat completion request
        - Detects: terms_required, audio-only, non-chat models
        - Only adds models that successfully complete text generation
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return
        
        try:
            import requests
            
            # Step 1: Get list of all models
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if response.status_code != 200:
                safe_print(f"[ROUTER] Groq model list failed: {response.status_code}")
                return
            
            models_data = response.json().get("data", [])
            listed = {m.get("id", "") for m in models_data}
            # Drop hardcoded defaults this key can no longer see
            for key in [k for k, m in self.models.items()
                        if m.provider == "groq" and m.model_id not in listed]:
                del self.models[key]
            added = 0
            skipped_terms = 0
            skipped_incapable = 0
            
            for model in models_data:
                model_id = model.get("id", "")
                key = f"groq:{model_id}"
                
                if key in self.models:
                    continue  # Already have this model
                
                # Step 2: DYNAMIC capability test - make a minimal request
                # This detects: terms required, audio-only, non-chat models
                try:
                    test_response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_id,
                            "messages": [{"role": "user", "content": "Hi"}],
                            "max_tokens": 1  # Minimal to save quota
                        },
                        timeout=5
                    )
                    
                    # Check response
                    if test_response.status_code == 200:
                        # Model works for text generation!
                        # Determine quality based on model characteristics
                        is_large = any(x in model_id.lower() for x in ["70b", "405b", "32b", "maverick", "scout"])
                        is_fast = any(x in model_id.lower() for x in ["8b", "instant", "mini", "nano"])
                        
                        daily_limit = 50 if is_large else (250 if is_fast else 100)
                        quality = 8.5 if is_large else (6.5 if is_fast else 7.0)
                        
                        self.models[key] = ModelInfo(
                            provider="groq", model_id=model_id,
                            daily_limit=daily_limit, rate_limit=30, delay=_safe_delay(30),
                            quality_general=quality, quality_creative=quality,
                            quality_structured=quality, quality_speed=9.0 if is_fast else 7.0,
                            robustness=0.95, available=True
                        )
                        added += 1
                        
                    elif test_response.status_code == 400:
                        # Check if it's a terms requirement
                        error_data = test_response.json()
                        error_msg = str(error_data.get("error", {}).get("message", "")).lower()
                        
                        if "terms" in error_msg or "accept" in error_msg:
                            skipped_terms += 1
                            safe_print(f"[ROUTER] Skipped {model_id}: requires terms acceptance")
                        else:
                            # Other error - likely not a chat model
                            skipped_incapable += 1
                    else:
                        # 429 (rate limit) or other - skip but don't count as failure
                        skipped_incapable += 1
                        
                except requests.Timeout:
                    skipped_incapable += 1
                except Exception as e:
                    skipped_incapable += 1
                
                # Small delay to avoid rate limits during discovery
                time.sleep(0.1)
            
            safe_print(f"[ROUTER] Groq: Added {added}, skipped {skipped_terms} (terms), {skipped_incapable} (incapable)")
            
        except Exception as e:
            safe_print(f"[ROUTER] Groq discovery failed: {e}")
    
    def _discover_gemini_models(self):
        """Discover available Gemini models."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return
        
        try:
            import requests
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=10
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                listed = {m.get("name", "").replace("models/", "") for m in models}
                # Drop hardcoded defaults this key can no longer see
                for key in [k for k, m in self.models.items()
                            if m.provider == "gemini" and m.model_id not in listed]:
                    del self.models[key]
                for model in models:
                    name = model.get("name", "").replace("models/", "")
                    if not _is_text_model_name(name):
                        continue  # TTS / image / music / agent models can't write scripts
                    if "generateContent" in model.get("supportedGenerationMethods", []):
                        key = f"gemini:{name}"
                        if key not in self.models:
                            # Estimate stats based on model name
                            # v17.9.33: Use _safe_delay for 10% margin
                            is_flash = "flash" in name.lower()
                            is_pro = "pro" in name.lower()
                            rpm = 15 if is_flash else 5
                            if "gemma" in name.lower():
                                # Gemma writes its reasoning into the answer and runs out of
                                # tokens before the JSON - keep it as a late fallback only
                                self.models[key] = ModelInfo(
                                    provider="gemini", model_id=name,
                                    daily_limit=500, rate_limit=rpm, delay=_safe_delay(rpm),
                                    quality_general=5.0, quality_creative=5.0,
                                    quality_structured=4.0, quality_speed=5.0,
                                    robustness=0.70, available=True
                                )
                                continue
                            self.models[key] = ModelInfo(
                                provider="gemini", model_id=name,
                                daily_limit=1500 if is_flash else (50 if is_pro else 500),
                                rate_limit=rpm,
                                delay=_safe_delay(rpm),  # 4.4s for flash, 13.2s for pro
                                quality_general=7.5 if is_flash else 8.5,
                                quality_creative=7.0 if is_flash else 8.0,
                                quality_structured=8.5 if is_flash else 9.0,
                                quality_speed=8.0 if is_flash else 5.0,
                                robustness=0.95 if is_flash else 0.90,
                                available=True
                            )
                safe_print(f"[ROUTER] Discovered {len(models)} Gemini models")
        except Exception as e:
            safe_print(f"[ROUTER] Gemini discovery failed: {e}")
    
    def _discover_openrouter_models(self):
        """Discover available OpenRouter free models."""
        try:
            import requests
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                timeout=10
            )
            if response.status_code == 200:
                models = response.json().get("data", [])
                free_count = 0
                for model in models:
                    model_id = model.get("id", "")
                    # Only add free models
                    if ":free" in model_id.lower() or model.get("pricing", {}).get("prompt") == "0":
                        key = f"openrouter:{model_id}"
                        if key not in self.models:
                            # v17.9.33: Use _safe_delay for 10% margin
                            self.models[key] = ModelInfo(
                                provider="openrouter", model_id=model_id,
                                daily_limit=10000, rate_limit=60, delay=_safe_delay(60),  # 1.1s
                                quality_general=6.5, quality_creative=6.0,
                                quality_structured=6.5, quality_speed=9.0,
                                robustness=0.85, available=True
                            )
                            free_count += 1
                safe_print(f"[ROUTER] Discovered {free_count} free OpenRouter models")
        except Exception as e:
            safe_print(f"[ROUTER] OpenRouter discovery failed: {e}")
    
    def _discover_huggingface_models(self):
        """Discover available HuggingFace models (use defaults, HF has no easy listing)."""
        # HuggingFace doesn't have easy model listing, keep defaults
        pass
    
    def _compute_rankings(self):
        """
        Compute model rankings for each prompt type.
        
        Rankings are based on prompt type requirements:
        - Creative: prioritize quality_creative
        - Evaluation: prioritize quality_structured
        - Simple: prioritize quality_speed + robustness
        - Analysis: prioritize quality_general + quality_structured
        
        v17.9.10: Also considers:
        - Remaining daily quota (avoid exhausted models)
        - Consecutive failures (deprioritize failing models)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        for prompt_type_name, prompt_type in PROMPT_TYPES.items():
            scored_models = []
            
            for key, model in self.models.items():
                if not model.available:
                    continue
                
                # Calculate score based on prompt type needs
                score = 0.0
                
                if prompt_type.needs_creativity:
                    score += model.quality_creative * 2.0
                else:
                    score += model.quality_creative * 0.5
                
                if prompt_type.needs_structure:
                    score += model.quality_structured * 1.5
                else:
                    score += model.quality_structured * 0.5
                
                if prompt_type.needs_speed:
                    score += model.quality_speed * 1.5
                    score += model.daily_limit / 1000  # Bonus for high quota
                else:
                    score += model.quality_speed * 0.3
                
                if prompt_type.needs_reasoning:
                    score += model.quality_general * 1.2
                else:
                    score += model.quality_general * 0.5
                
                # Always factor in robustness
                score += model.robustness * 5.0
                
                # v17.9.10: QUOTA-AWARE SCORING
                # Penalize models that are close to exhaustion
                calls_today = model.calls_today if model.last_call_date == today else 0
                remaining_quota = max(0, model.daily_limit - calls_today)
                quota_ratio = remaining_quota / max(1, model.daily_limit)
                
                # If < 20% quota remaining, heavily penalize
                if quota_ratio < 0.2:
                    score *= 0.3  # Reduce score by 70%
                elif quota_ratio < 0.5:
                    score *= 0.7  # Reduce score by 30%
                
                # Penalize models with consecutive failures (likely broken/down)
                if model.consecutive_failures >= 3:
                    score *= 0.1  # Almost disable after 3 failures
                elif model.consecutive_failures >= 1:
                    score *= 0.5  # Reduce after any failure
                
                scored_models.append((key, score))
            
            # Sort by score (highest first)
            scored_models.sort(key=lambda x: x[1], reverse=True)
            
            # Store ranking (ordered list of model keys)
            self.rankings[prompt_type_name] = [key for key, _ in scored_models]
        
        safe_print("[ROUTER] Rankings computed for all prompt types (quota-aware)")
    
    def classify_prompt(self, prompt: str, hint: str = None) -> str:
        """
        Classify a prompt into a type.
        
        Args:
            prompt: The full prompt text
            hint: Optional hint about the prompt type
        
        Returns:
            Prompt type name ("creative", "evaluation", "simple", "analysis")
        """
        prompt_lower = prompt.lower()
        
        # If hint provided, try to match it first
        if hint:
            hint_lower = hint.lower()
            for type_name, prompt_type in PROMPT_TYPES.items():
                if any(kw in hint_lower for kw in prompt_type.keywords):
                    return type_name
        
        # Score each type based on keyword matches
        type_scores = {}
        for type_name, prompt_type in PROMPT_TYPES.items():
            score = sum(1 for kw in prompt_type.keywords if kw in prompt_lower)
            type_scores[type_name] = score
        
        # Return highest scoring type, default to "simple"
        best_type = max(type_scores, key=type_scores.get)
        if type_scores[best_type] > 0:
            return best_type
        
        return "simple"  # Default
    
    def get_model_chain(self, prompt_type: str) -> List[Tuple[str, ModelInfo]]:
        """
        Get the full fallback chain for a prompt type.
        
        Returns:
            List of (model_key, ModelInfo) tuples in priority order
        """
        if prompt_type not in self.rankings:
            prompt_type = "simple"
        
        chain = []
        for key in self.rankings.get(prompt_type, []):
            if key in self.models:
                chain.append((key, self.models[key]))
        
        # Ensure we always have at least some models
        if not chain:
            for key, model in self.models.items():
                chain.append((key, model))
        
        return chain
    
    def _is_model_exhausted(self, model_key: str, model: ModelInfo) -> bool:
        """
        v17.9.43: Check if a model has hit its daily quota.
        
        Returns True if we should skip this model and try next in chain.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Reset counter if new day
        if model.last_call_date != today:
            model.calls_today = 0
            model.last_call_date = today
            return False
        
        # Get quota for this model
        model_name = model.model_id
        quota = self.MODEL_DAILY_QUOTAS.get(model_name, 50)  # Default 50 if unknown
        
        # Leave 10% buffer for safety
        safe_quota = int(quota * 0.90)
        
        if model.calls_today >= safe_quota:
            safe_print(f"   [QUOTA] {model_name}: {model.calls_today}/{quota} - exhausted, trying next")
            return True
        
        return False
    
    def get_best_model(self, prompt: str, hint: str = None, 
                       prompt_name: str = None) -> Tuple[str, ModelInfo]:
        """
        Get the best model for a prompt.
        
        Args:
            prompt: The prompt text
            hint: Optional hint about prompt type
            prompt_name: Optional specific prompt name (e.g., "VIRAL_TOPIC_PROMPT")
        
        Returns:
            (model_key, ModelInfo) for the best model
            
        v17.9.43: Now skips exhausted models and rotates to next available
        """
        # v17.9.9: Check prompts registry for per-prompt recommendations
        if prompt_name:
            try:
                from prompts_registry import get_best_model_for_prompt
                recommended = get_best_model_for_prompt(prompt_name)
                if recommended and recommended in self.models:
                    model = self.models[recommended]
                    # v17.9.43: Check if recommended model is exhausted
                    if not self._is_model_exhausted(recommended, model):
                        return (recommended, model)
            except ImportError:
                pass
            except Exception:
                pass
        
        # Fall back to type-based selection
        prompt_type = self.classify_prompt(prompt, hint)
        chain = self.get_model_chain(prompt_type)
        
        # v17.9.43: Find first non-exhausted model in chain
        for key, model in chain:
            if not self._is_model_exhausted(key, model):
                return (key, model)
        
        # All models in chain exhausted - try any available model
        safe_print("   [QUOTA] All primary models exhausted, checking all providers...")
        for key, model in self.models.items():
            if not self._is_model_exhausted(key, model):
                return (key, model)
        
        # Ultimate fallback - return first model anyway (let API error handle it)
        safe_print("   [QUOTA] WARNING: All models appear exhausted, using first available")
        if chain:
            return chain[0]
        
        for key, model in self.models.items():
            return (key, model)
        
        # Should never reach here - use first available model
        for key, model in DEFAULT_MODELS.items():
            return (key, model)
        raise ValueError("No models available - check API keys and network connection")
    
    def mark_unavailable(self, model_key: str, reason: str = ""):
        """Disable a model that can never succeed for this key (404 / zero quota)."""
        model = self.models.get(model_key)
        if model and model.available:
            model.available = False
            for prompt_type in self.rankings:
                self.rankings[prompt_type] = [k for k in self.rankings[prompt_type] if k != model_key]
            self._save_cache()
            safe_print(f"[ROUTER] Disabled {model_key}{': ' + reason if reason else ''}")

    def record_result(self, model_key: str, success: bool, was_fallback: bool = False):
        """Record the result of a model call for stats."""
        self.stats["calls"] = self.stats.get("calls", 0) + 1
        if success:
            self.stats["successes"] = self.stats.get("successes", 0) + 1
        if was_fallback:
            self.stats["fallbacks"] = self.stats.get("fallbacks", 0) + 1
        
        # Update model-specific stats
        model_stats = self.stats.get("models", {})
        if model_key not in model_stats:
            model_stats[model_key] = {"calls": 0, "successes": 0}
        model_stats[model_key]["calls"] += 1
        if success:
            model_stats[model_key]["successes"] += 1
        self.stats["models"] = model_stats
        
        # v17.9.10: Track daily usage per model to prevent quota exhaustion
        if model_key in self.models:
            model = self.models[model_key]
            today = datetime.now().strftime("%Y-%m-%d")
            # Reset daily counter if new day
            if model.last_call_date != today:
                model.calls_today = 0
                model.last_call_date = today
            model.calls_today += 1
            # Track consecutive failures for deprioritization
            if success:
                model.consecutive_failures = 0
            else:
                model.consecutive_failures += 1
                # v17.9.45: Auto-disable models with 5+ consecutive failures (likely deprecated)
                if model.consecutive_failures >= 5:
                    model.available = False
                    safe_print(f"[ROUTER] Auto-disabled {model_key} after 5 consecutive failures")
        
        # Save periodically (every 10 calls)
        if self.stats["calls"] % 10 == 0:
            self._save_stats()
    
    def get_stats(self) -> Dict:
        """Get router statistics."""
        return {
            "total_calls": self.stats.get("calls", 0),
            "successes": self.stats.get("successes", 0),
            "fallbacks": self.stats.get("fallbacks", 0),
            "success_rate": (self.stats.get("successes", 0) / max(1, self.stats.get("calls", 1))) * 100,
            "fallback_rate": (self.stats.get("fallbacks", 0) / max(1, self.stats.get("calls", 1))) * 100,
            "models_used": len(self.stats.get("models", {})),
            "last_refresh": self.last_refresh
        }
    
    def print_rankings(self):
        """Print current rankings for debugging."""
        safe_print("\n" + "=" * 60)
        safe_print("SMART MODEL ROUTER - CURRENT RANKINGS")
        safe_print("=" * 60)
        
        for prompt_type, model_keys in self.rankings.items():
            safe_print(f"\n{prompt_type.upper()}:")
            for i, key in enumerate(model_keys[:5], 1):
                model = self.models.get(key)
                if model:
                    safe_print(f"  {i}. {key} (quality={model.quality_general}, "
                              f"robust={model.robustness:.0%})")
        
        safe_print("\n" + "=" * 60)


# =============================================================================
# GLOBAL INSTANCE & CONVENIENCE FUNCTIONS
# =============================================================================

_router = None


def get_smart_router() -> SmartModelRouter:
    """Get the global SmartModelRouter instance."""
    global _router
    if _router is None:
        _router = SmartModelRouter()
    return _router


def get_best_model_for_prompt(prompt: str, hint: str = None) -> Tuple[str, Dict]:
    """
    Convenience function to get best model for a prompt.
    
    Returns:
        (model_key, model_info_dict)
    """
    router = get_smart_router()
    key, info = router.get_best_model(prompt, hint)
    return key, asdict(info)


def get_fallback_chain(prompt_type: str) -> List[Tuple[str, Dict]]:
    """
    Get the fallback chain for a prompt type.
    
    Returns:
        List of (model_key, model_info_dict)
    """
    router = get_smart_router()
    chain = router.get_model_chain(prompt_type)
    return [(key, asdict(info)) for key, info in chain]


def classify_prompt(prompt: str, hint: str = None) -> str:
    """Classify a prompt into a type."""
    return get_smart_router().classify_prompt(prompt, hint)


def force_refresh_rankings():
    """Force a refresh of model rankings."""
    router = get_smart_router()
    router.refresh_rankings()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("SMART MODEL ROUTER TEST")
    safe_print("=" * 60)
    
    router = get_smart_router()
    
    # Print rankings
    router.print_rankings()
    
    # Test prompt classification
    test_prompts = [
        ("Generate a viral topic about psychology", "topic"),
        ("Evaluate this content for virality", "evaluation"),
        ("Generate hashtags for this video", "hashtag"),
        ("Analyze trends in our category performance", "analysis"),
    ]
    
    safe_print("\nPROMPT CLASSIFICATION TEST:")
    safe_print("-" * 60)
    
    for prompt, hint in test_prompts:
        prompt_type = router.classify_prompt(prompt, hint)
        model_key, model_info = router.get_best_model(prompt, hint)
        safe_print(f"\nPrompt: {prompt[:50]}...")
        safe_print(f"  Type: {prompt_type}")
        safe_print(f"  Best Model: {model_key}")
        safe_print(f"  Chain Length: {len(router.get_model_chain(prompt_type))}")
    
    # Print stats
    safe_print("\nROUTER STATS:")
    safe_print("-" * 60)
    stats = router.get_stats()
    for key, value in stats.items():
        safe_print(f"  {key}: {value}")
    
    safe_print("\n" + "=" * 60)
