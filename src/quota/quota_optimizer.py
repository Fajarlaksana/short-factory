#!/usr/bin/env python3
"""
ViralShorts Factory - Quota Optimizer v16.6
============================================

This module optimizes API quota usage by:
1. Caching reusable data (trending topics, categories)
2. Dynamically fetching available free models
3. Tracking usage per provider/model

PRINCIPLE: Call AI APIs as FEW times as possible while maintaining quality.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Persistent storage directory
CACHE_DIR = Path("data/persistent")
CACHE_FILE = CACHE_DIR / "quota_cache.json"

def safe_print(text):
    """Print safely regardless of encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))


class QuotaOptimizer:
    """
    Optimizes API quota usage through intelligent caching.
    
    CACHED DATA (refreshed daily):
    - Trending categories (from AI)
    - Trending topics (from AI)
    - Available free models (from OpenRouter API)
    
    This saves MANY API calls by reusing data for all 6 daily videos.
    """
    
    # Cache TTL in seconds
    TTL_CATEGORIES = 24 * 3600  # 24 hours
    TTL_TOPICS = 12 * 3600      # 12 hours
    TTL_MODELS = 6 * 3600       # 6 hours (reduced - models can change)
    
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk."""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "trending_categories": {"data": None, "timestamp": 0},
            "trending_topics": {"data": None, "timestamp": 0},
            "openrouter_free_models": {"data": None, "timestamp": 0},
            "groq_models": {"data": None, "timestamp": 0},
            "gemini_models": {"data": None, "timestamp": 0}
        }
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            safe_print(f"[!] Cache save failed: {e}")
    
    def _is_valid(self, key: str, ttl: int) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache or not self.cache[key].get("data"):
            return False
        return (time.time() - self.cache[key].get("timestamp", 0)) < ttl
    
    def clear_model_cache(self, provider: str = None):
        """
        Clear stale model cache. Call this when you get a 404 error.
        
        Args:
            provider: "gemini", "groq", "openrouter", or None for all
        """
        if provider is None or provider == "gemini":
            self.cache["gemini_models"] = {"data": None, "timestamp": 0}
        if provider is None or provider == "groq":
            self.cache["groq_models"] = {"data": None, "timestamp": 0}
        if provider is None or provider == "openrouter":
            self.cache["openrouter_free_models"] = {"data": None, "timestamp": 0}
        self._save_cache()
        safe_print(f"[CACHE] Cleared model cache for: {provider or 'all'}")
    
    # ========================================================================
    # TRENDING CATEGORIES - Cached for 24 hours
    # ========================================================================
    def get_trending_categories(self, fetch_func=None) -> List[str]:
        """
        Get trending categories from cache or fetch fresh.
        
        Args:
            fetch_func: Optional function to call if cache expired
        
        Returns:
            List of trending category names
        """
        if self._is_valid("trending_categories", self.TTL_CATEGORIES):
            safe_print("[CACHE] Using cached trending categories (saves API call)")
            return self.cache["trending_categories"]["data"]
        
        # Default fallback categories
        default_categories = [
            "ai_trends", "psychology", "money_hacks", "productivity",
            "health_tips", "tech_news", "life_hacks", "motivation",
            "science_facts", "crypto_news", "travel_hacks", "relationship_tips"
        ]
        
        if fetch_func:
            try:
                fresh = fetch_func()
                if fresh and len(fresh) >= 5:
                    self.cache["trending_categories"] = {
                        "data": fresh,
                        "timestamp": time.time()
                    }
                    self._save_cache()
                    safe_print(f"[CACHE] Saved {len(fresh)} trending categories")
                    return fresh
            except Exception as e:
                safe_print(f"[!] Category fetch failed: {e}")
        
        return default_categories
    
    # ========================================================================
    # TRENDING TOPICS - Cached for 12 hours
    # ========================================================================
    def get_trending_topics(self, category: str, fetch_func=None) -> List[str]:
        """
        Get trending topics for a category from cache or fetch fresh.
        
        This is BATCH fetched - get multiple topics at once to save calls.
        """
        cache_key = f"topics_{category}"
        
        if cache_key in self.cache and self._is_valid(cache_key, self.TTL_TOPICS):
            safe_print(f"[CACHE] Using cached topics for {category}")
            return self.cache[cache_key]["data"]
        
        if fetch_func:
            try:
                # Fetch multiple topics at once (batch to save quota)
                topics = fetch_func(category, count=10)  # Get 10 topics
                if topics:
                    self.cache[cache_key] = {
                        "data": topics,
                        "timestamp": time.time()
                    }
                    self._save_cache()
                    return topics
            except:
                pass
        
        return []
    
    # ========================================================================
    # GROQ MODELS - Dynamic discovery with LAZY LOADING
    # ========================================================================
    def get_groq_models(self, api_key: str = None, force_refresh: bool = False) -> List[str]:
        """
        Get available Groq models dynamically.
        
        Uses Groq API to discover available models.
        Cached for 24 hours.
        
        LAZY LOADING: Only fetches when current model fails, not on every call.
        Set force_refresh=True when a model returns 404.
        """
        if not force_refresh and self._is_valid("groq_models", self.TTL_MODELS):
            safe_print("[CACHE] Using cached Groq models")
            return self.cache["groq_models"]["data"]
        
        if force_refresh:
            safe_print("[CACHE] Force refreshing Groq models (model not found)")
        
        # v17.9.12: NO hardcoded fallbacks! All via API discovery.
        
        if not api_key:
            safe_print("[!] No GROQ_API_KEY - cannot discover models")
            # Return empty - caller should handle gracefully
            return []
        
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            # Get ONLY active models from API (no hardcoding!)
            models_response = client.models.list()
            
            # Extract active model IDs
            available_models = []
            for model in models_response.data:
                if hasattr(model, 'id'):
                    model_id = model.id
                    # Check if model is active (if the API provides this info)
                    is_active = getattr(model, 'active', True)
                    if is_active:
                        available_models.append(model_id)
            
            if available_models:
                self.cache["groq_models"] = {
                    "data": available_models[:10],
                    "timestamp": time.time()
                }
                self._save_cache()
                safe_print(f"[CACHE] Found {len(available_models)} Groq models via API")
                return available_models[:10]
                
        except Exception as e:
            safe_print(f"[!] Groq model discovery failed: {e}")
        
        # Return empty - caller should try OpenRouter or other fallback
        safe_print("[!] Groq: No models discovered, will use fallback provider")
        return []
    
    # ========================================================================
    # GEMINI MODELS - Dynamic discovery with free tier priority
    # ========================================================================
    def get_gemini_models(self, api_key: str = None, force_refresh: bool = False) -> List[str]:
        """
        v17.9.13: Get available Gemini models, sorted by ACTUAL QUOTA (highest first).
        
        Strategy:
        1. Query API for available models
        2. Check quota cache for each model (from previous 429 errors)
        3. Test unknown models to discover quota
        4. Sort by quota descending
        5. Skip models with low quota (<50/day)
        
        LAZY LOADING: Set force_refresh=True when a model returns 404.
        """
        if not force_refresh and self._is_valid("gemini_models", self.TTL_MODELS):
            safe_print("[CACHE] Using cached Gemini models")
            return self.cache["gemini_models"]["data"]
        
        if force_refresh:
            safe_print("[CACHE] Force refreshing Gemini models (model not found)")
        
        if not api_key:
            safe_print("[!] No GEMINI_API_KEY - cannot discover models")
            return []
        
        try:
            import google.generativeai as genai
            import requests
            genai.configure(api_key=api_key)
            
            # Step 1: List all available models from API
            models = genai.list_models()
            
            # Get models that support generateContent
            candidate_models = []
            for model in models:
                model_name = model.name.replace("models/", "")
                if "generateContent" in getattr(model, "supported_generation_methods", []):
                    candidate_models.append(model_name)
            
            safe_print(f"[CACHE] Found {len(candidate_models)} Gemini models via API")
            
            # Step 2: Load quota cache (from previous 429 errors) with freshness check
            quota_cache_file = Path("data/persistent/model_cache/actual_quotas.json")
            quota_cache = {}
            QUOTA_TTL_HOURS = 24  # Re-check quotas daily
            try:
                if quota_cache_file.exists():
                    with open(quota_cache_file, 'r') as f:
                        raw_cache = json.load(f)
                    # Filter to only fresh entries
                    for key, value in raw_cache.items():
                        if "_discovered_at" in key:
                            continue
                        discovered_key = f"{key}_discovered_at"
                        if discovered_key in raw_cache:
                            try:
                                discovered_at = datetime.fromisoformat(raw_cache[discovered_key])
                                age_hours = (datetime.now() - discovered_at).total_seconds() / 3600
                                if age_hours < QUOTA_TTL_HOURS:
                                    quota_cache[key] = value
                            except:
                                pass
            except:
                pass
            
            # Step 3: Score models by quota
            models_with_quota = []
            tested_count = 0
            MAX_TESTS = 5  # Limit test calls to save quota
            
            for model_name in candidate_models:
                # Check cached quota first
                if model_name in quota_cache:
                    quota = quota_cache[model_name]
                    if quota >= 50:  # Skip low-quota models
                        models_with_quota.append((model_name, quota))
                        safe_print(f"   {model_name}: {quota}/day (cached)")
                    continue
                
                # Test model to discover quota (limited)
                if tested_count < MAX_TESTS:
                    try:
                        test_response = requests.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
                            json={"contents": [{"parts": [{"text": "1"}]}], "generationConfig": {"maxOutputTokens": 1}},
                            timeout=10
                        )
                        tested_count += 1
                        
                        # Check rate limit headers
                        daily_limit = test_response.headers.get("x-ratelimit-limit-requests-per-day")
                        if daily_limit:
                            quota = int(daily_limit)
                        elif test_response.status_code == 429:
                            # Parse quota from error
                            import re
                            match = re.search(r'quota_value[:\s]+(\d+)', test_response.text)
                            quota = int(match.group(1)) if match else 20  # Assume low if 429
                            quota_cache[model_name] = quota
                        elif test_response.status_code == 200:
                            quota = 500  # Assume decent if works
                        else:
                            quota = 0  # Skip this model
                        
                        if quota >= 50:
                            models_with_quota.append((model_name, quota))
                            quota_cache[model_name] = quota
                            safe_print(f"   {model_name}: {quota}/day (discovered)")
                    except Exception as e:
                        safe_print(f"   {model_name}: Error testing - {e}")
            
            # Save updated quota cache
            try:
                quota_cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(quota_cache_file, 'w') as f:
                    json.dump(quota_cache, f, indent=2)
            except:
                pass
            
            # Step 4: Sort by quota (highest first)
            models_with_quota.sort(key=lambda x: x[1], reverse=True)
            sorted_models = [m[0] for m in models_with_quota]
            
            if sorted_models:
                safe_print(f"[MODEL] Best Gemini: {sorted_models[0]} ({models_with_quota[0][1]}/day)")
                self.cache["gemini_models"] = {
                    "data": sorted_models,
                    "quotas": {m[0]: m[1] for m in models_with_quota},
                    "timestamp": time.time()
                }
                self._save_cache()
                return sorted_models
                
        except Exception as e:
            safe_print(f"[!] Gemini model discovery failed: {e}")
        
        # Return empty - caller should try OpenRouter or other fallback
        safe_print("[!] Gemini: No high-quota models found, will use fallback provider")
        return []
    
    # ========================================================================
    # OPENROUTER FREE MODELS - Cached for 24 hours
    # ========================================================================
    def get_openrouter_free_models(self, api_key: str = None, force_refresh: bool = False) -> List[str]:
        """
        Get list of free OpenRouter models from API.
        
        This queries the /models endpoint to find models with `:free` suffix.
        Cached for 24 hours to avoid wasting the limited 50 req/day quota.
        
        LAZY LOADING: Set force_refresh=True when a model returns 404.
        """
        if not force_refresh and self._is_valid("openrouter_free_models", self.TTL_MODELS):
            safe_print("[CACHE] Using cached OpenRouter free models")
            return self.cache["openrouter_free_models"]["data"]
        
        if force_refresh:
            safe_print("[CACHE] Force refreshing OpenRouter models (model not found)")
        
        # Default fallback models (known free models as of 2024)
        default_models = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free",
            "huggingfaceh4/zephyr-7b-beta:free",
            "openchat/openchat-7b:free"
        ]
        
        if not api_key:
            return default_models
        
        try:
            import requests
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json().get("data", [])
                # Filter for free models (have :free suffix or pricing = 0)
                free_models = []
                for model in models_data:
                    model_id = model.get("id", "")
                    if ":free" in model_id.lower():
                        free_models.append(model_id)
                    elif model.get("pricing", {}).get("prompt", "1") == "0":
                        free_models.append(model_id)
                
                if free_models:
                    self.cache["openrouter_free_models"] = {
                        "data": free_models[:10],  # Keep top 10
                        "timestamp": time.time()
                    }
                    self._save_cache()
                    safe_print(f"[CACHE] Found {len(free_models)} free OpenRouter models")
                    return free_models[:10]
        except Exception as e:
            safe_print(f"[!] OpenRouter model fetch failed: {e}")
        
        return default_models
    
    # ========================================================================
    # HUGGINGFACE MODELS - Dynamic discovery
    # ========================================================================
    def get_huggingface_models(self, api_key: str = None, force_refresh: bool = False) -> List[str]:
        """
        Get available HuggingFace text-generation models.
        
        Uses HuggingFace API to discover popular instruction-tuned models.
        Cached for 6 hours.
        """
        if not force_refresh and self._is_valid("huggingface_models", self.TTL_MODELS):
            safe_print("[CACHE] Using cached HuggingFace models")
            return self.cache["huggingface_models"]["data"]
        
        # Default fallback models - NON-GATED models only!
        # Note: meta-llama and mistralai models are GATED (require license acceptance)
        default_models = [
            "HuggingFaceH4/zephyr-7b-beta",      # Non-gated, good quality
            "google/gemma-2-2b-it",               # Non-gated, Google
            "Qwen/Qwen2.5-1.5B-Instruct",         # Non-gated, small & fast
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0", # Non-gated, very fast
            "microsoft/Phi-3-mini-4k-instruct",   # Non-gated, Microsoft
        ]
        
        if not api_key:
            return default_models
        
        try:
            import requests
            # Query HuggingFace for popular text-generation models
            response = requests.get(
                "https://huggingface.co/api/models",
                params={
                    "pipeline_tag": "text-generation",
                    "sort": "downloads",
                    "direction": -1,
                    "limit": 50,
                    "filter": "conversational"
                },
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15
            )
            
            if response.status_code == 200:
                models_data = response.json()
                # Filter for instruction-tuned, NON-GATED models that support inference
                good_models = []
                for model in models_data:
                    model_id = model.get("modelId", "")
                    # Skip gated models (require license acceptance)
                    if model.get("gated"):
                        continue
                    # Skip models that require special auth
                    if "meta-llama" in model_id.lower() or "mistralai" in model_id.lower():
                        continue
                    # Prefer instruction-tuned models
                    if any(kw in model_id.lower() for kw in ["instruct", "chat", "-it", "zephyr"]):
                        # Check if inference is available
                        if model.get("inference") != "error":
                            good_models.append(model_id)
                
                if good_models:
                    self.cache["huggingface_models"] = {
                        "data": good_models[:10],  # Keep top 10
                        "timestamp": time.time()
                    }
                    self._save_cache()
                    safe_print(f"[CACHE] Found {len(good_models)} HuggingFace models")
                    return good_models[:10]
        except Exception as e:
            safe_print(f"[!] HuggingFace model discovery failed: {e}")
        
        return default_models
    
    # ========================================================================
    # QUOTA STATUS
    # ========================================================================
    def print_status(self):
        """Print cache status."""
        safe_print("\n=== QUOTA OPTIMIZER STATUS ===")
        for key, value in self.cache.items():
            if isinstance(value, dict) and "timestamp" in value:
                age = time.time() - value.get("timestamp", 0)
                age_str = f"{int(age/3600)}h ago" if age > 3600 else f"{int(age/60)}m ago"
                data_size = len(value.get("data", [])) if value.get("data") else 0
                safe_print(f"  {key}: {data_size} items ({age_str})")
        safe_print("================================\n")


# Singleton instance
_optimizer = None

def get_quota_optimizer() -> QuotaOptimizer:
    """Get singleton QuotaOptimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = QuotaOptimizer()
    return _optimizer


# ========================================================================
# DYNAMIC SCHEDULE ADVISOR
# ========================================================================

class ScheduleAdvisor:
    """
    AI-driven schedule recommendations for periodic workflows.
    
    GitHub cron schedules are fixed, but workflows can check this advisor
    to decide IF they should actually run on a given trigger.
    
    LEARNING: Analyzes performance data to recommend optimal frequencies.
    """
    
    SCHEDULE_FILE = CACHE_DIR / "schedule_advisor.json"
    
    # Default recommendations (AI will update based on learning)
    DEFAULTS = {
        "analytics_feedback": {
            "frequency": "twice_weekly",  # Could be: daily, twice_weekly, weekly, biweekly
            "skip_if_no_new_videos": True,
            "min_videos_for_analysis": 5
        },
        "monthly_analysis": {
            "frequency": "biweekly",  # Could be: weekly, biweekly, monthly
            "skip_if_no_views": True
        },
        "model_refresh": {
            "frequency": "daily",  # How often to refresh available AI models
            "lazy_load": True  # Only refresh when a model fails
        }
    }
    
    def __init__(self):
        self.recommendations = self._load()
    
    def _load(self) -> Dict:
        try:
            if self.SCHEDULE_FILE.exists():
                with open(self.SCHEDULE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return self.DEFAULTS.copy()
    
    def _save(self):
        try:
            with open(self.SCHEDULE_FILE, 'w') as f:
                json.dump(self.recommendations, f, indent=2)
        except:
            pass
    
    def should_run(self, workflow: str, context: Dict = None) -> bool:
        """
        Check if a workflow should run based on AI recommendations.
        
        Args:
            workflow: Name of workflow (e.g., 'analytics_feedback')
            context: Current context (e.g., {'videos_since_last': 3})
        
        Returns:
            True if workflow should execute, False to skip
        """
        rec = self.recommendations.get(workflow, {})
        context = context or {}
        
        # Check skip conditions
        if rec.get("skip_if_no_new_videos") and context.get("videos_since_last", 0) == 0:
            safe_print(f"[SCHEDULE] Skipping {workflow}: No new videos")
            return False
        
        if rec.get("skip_if_no_views") and context.get("total_views", 0) == 0:
            safe_print(f"[SCHEDULE] Skipping {workflow}: No views yet")
            return False
        
        min_videos = rec.get("min_videos_for_analysis", 0)
        if context.get("total_videos", 0) < min_videos:
            safe_print(f"[SCHEDULE] Skipping {workflow}: Need {min_videos} videos")
            return False
        
        return True
    
    def update_from_performance(self, metrics: Dict):
        """
        AI-driven update of schedule recommendations based on performance.
        
        Called by analytics workflow after analyzing performance data.
        """
        # Example learning: If videos are getting more views lately, 
        # increase analytics frequency to learn faster
        avg_views = metrics.get("avg_views_per_video", 0)
        
        if avg_views > 1000:
            # High performance - analyze more frequently
            self.recommendations["analytics_feedback"]["frequency"] = "daily"
            safe_print("[SCHEDULE] Increasing analytics to daily (high performance)")
        elif avg_views > 100:
            self.recommendations["analytics_feedback"]["frequency"] = "twice_weekly"
        else:
            self.recommendations["analytics_feedback"]["frequency"] = "weekly"
        
        self._save()
    
    def get_frequency(self, workflow: str) -> str:
        """Get recommended frequency for a workflow."""
        return self.recommendations.get(workflow, {}).get("frequency", "weekly")


def get_schedule_advisor() -> ScheduleAdvisor:
    """Get singleton ScheduleAdvisor instance."""
    global _schedule_advisor
    if '_schedule_advisor' not in globals() or _schedule_advisor is None:
        _schedule_advisor = ScheduleAdvisor()
    return _schedule_advisor


# ========================================================================
# HARDCODING PREVENTION
# ========================================================================

HARDCODE_WARNINGS = """
================================================================================
HARDCODING PREVENTION GUIDE - ViralShorts Factory
================================================================================

RULE: Never hardcode what can be AI-driven or dynamically fetched.

EXCEPTIONS (where hardcoding is acceptable):
1. SEED lists - Initial values for AI to expand upon
2. FALLBACK data - When AI fails (must be dynamic/random selection from seeds)
3. Configuration - API endpoints, timeouts, rate limits

ALWAYS USE:
- QuotaOptimizer for trending categories/topics (cached, not hardcoded)
- Dynamic model discovery for OpenRouter models
- Random selection from seed lists for fallbacks

RED FLAGS (never do these):
- Hardcoded topic like "psychology" always used
- Hardcoded video title templates
- Hardcoded model versions without fallback
- Hardcoded timestamps or dates

GOOD PATTERNS:
- random.choice(seed_list) for fallbacks
- AI-generated with seed list as examples
- Cached data with TTL + fresh fetch
================================================================================
"""

def check_for_hardcoding(code: str) -> List[str]:
    """
    Check code for potential hardcoding issues.
    
    Returns list of warnings.
    """
    import re
    warnings = []
    
    # Patterns that suggest hardcoding
    patterns = [
        (r"'psychology'(?!.*random)", "Hardcoded 'psychology' without random selection"),
        (r"topic.*=.*['\"].*['\"]", "Potentially hardcoded topic"),
        (r"category.*=.*['\"](?!.*random)", "Potentially hardcoded category"),
        (r"gemini-2\.0-flash-exp", "Using experimental model with no free quota"),
    ]
    
    for pattern, warning in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append(warning)
    
    return warnings


# =============================================================================
# CENTRALIZED MODEL GETTERS - ALL FILES MUST USE THESE
# =============================================================================

def get_best_gemini_model(api_key: str = None, for_rest_api: bool = False) -> str:
    """
    Get the best available Gemini model with free quota.
    
    DYNAMIC DISCOVERY: Queries the API to find models with quota.
    Falls back through multiple models if one fails.
    
    Args:
        api_key: Gemini API key (uses env if not provided)
        for_rest_api: If True, returns model name for REST API calls (e.g., URL construction)
    
    Returns:
        Best model name string (e.g., "gemini-2.5-flash" or could be "gemini-2.0-flash" if available)
    
    Usage:
        from src.quota.quota_optimizer import get_best_gemini_model
        model = genai.GenerativeModel(get_best_gemini_model())
    """
    optimizer = get_quota_optimizer()
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    
    # Get dynamically discovered models (cached for 24h)
    models = optimizer.get_gemini_models(api_key=api_key)
    
    if models:
        return models[0]  # Return best available
    
    # Ultimate fallback (should never reach here)
    return "gemini-2.5-flash"


def get_best_groq_model(api_key: str = None) -> str:
    """
    Get the best available Groq model.
    
    DYNAMIC DISCOVERY: Queries the API to find available models.
    Prioritizes large versatile models.
    
    Returns:
        Best model name string (e.g., "llama-3.3-70b-versatile")
    """
    optimizer = get_quota_optimizer()
    api_key = api_key or os.getenv("GROQ_API_KEY")
    
    models = optimizer.get_groq_models(api_key=api_key)
    
    if models:
        return models[0]
    
    return "llama-3.3-70b-versatile"


def get_gemini_model_for_rest_api(api_key: str = None) -> str:
    """
    Get Gemini model name formatted for REST API URL construction.
    
    Example: Returns "gemini-2.5-flash" for use in URLs like:
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    """
    return get_best_gemini_model(api_key=api_key)


if __name__ == "__main__":
    # Test the optimizer
    optimizer = get_quota_optimizer()
    optimizer.print_status()
    
    # Get categories
    categories = optimizer.get_trending_categories()
    print(f"Categories: {categories[:5]}...")
    
    # Test dynamic model getters
    print(f"\nBest Gemini model: {get_best_gemini_model()}")
    print(f"Best Groq model: {get_best_groq_model()}")
    
    # Print hardcoding guide
    print(HARDCODE_WARNINGS)

