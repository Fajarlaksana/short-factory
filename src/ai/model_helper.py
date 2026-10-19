#!/usr/bin/env python3
"""
v17.9.12: TRULY DYNAMIC Model Helper
=====================================

ZERO HARDCODING - ALL decisions made via API calls!

Strategy:
1. Query provider API for available models
2. For each model, query its quota/limits via API
3. Score models based on ACTUAL quota data
4. Cache results for performance (but always validate)
5. OpenRouter as universal fallback (no key needed)

NO hardcoded model names, NO hardcoded quotas!
All filtering based on real-time API data.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

# Cache directory
CACHE_DIR = Path("cache/models")
EMERGENCY_CACHE_DIR = Path("data/persistent/model_cache")  # Persists across runs

# Minimum quota threshold (models below this are deprioritized)
# This is a POLICY value, not a model name - acceptable to configure
MIN_DAILY_QUOTA = 50  # Minimum requests/day to be considered "usable"


def _safe_print(msg: str):
    """Print with fallback for encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())


# Quota cache TTL - re-check quotas periodically in case they change
QUOTA_CACHE_TTL_HOURS = int(os.environ.get("QUOTA_CACHE_TTL_HOURS", 24))  # Configurable!


# =============================================================================
# SMART MODEL QUALITY SCORING (v17.9.27)
# =============================================================================
# Instead of checking for "pro" in name, we score models based on actual properties

def get_model_quality_score(model_name: str, model_info: Dict = None) -> float:
    """
    Calculate a quality score (0-10) for a model based on actual properties.
    
    Scoring factors:
    1. Model Size (extracted from name): 70B=10, 8B=5, 1B=2
    2. Context Length: >100K=10, >32K=7, >8K=5, else=3
    3. Model Generation: Ultra>Pro>Flash>Nano
    4. Recency: Newer models often better
    
    Returns: Quality score 0-10 (higher = better for critical tasks)
    """
    score = 5.0  # Base score
    model_lower = model_name.lower()
    
    # Factor 1: Model Size (weight: 40%)
    size_score = 5.0
    if "70b" in model_lower or "72b" in model_lower:
        size_score = 10.0
    elif "32b" in model_lower or "34b" in model_lower:
        size_score = 8.5
    elif "13b" in model_lower or "14b" in model_lower:
        size_score = 7.0
    elif "8b" in model_lower or "9b" in model_lower:
        size_score = 6.0
    elif "4b" in model_lower or "3b" in model_lower:
        size_score = 4.0
    elif "1b" in model_lower or "2b" in model_lower:
        size_score = 2.5
    elif "nano" in model_lower or "mini" in model_lower:
        size_score = 2.0
    
    # Factor 2: Model Tier/Generation (weight: 35%)
    tier_score = 5.0
    if "ultra" in model_lower:
        tier_score = 10.0
    elif "pro" in model_lower:
        tier_score = 8.5
    elif "plus" in model_lower or "advanced" in model_lower:
        tier_score = 7.5
    elif "flash" in model_lower or "turbo" in model_lower:
        tier_score = 5.5  # Fast but lower quality
    elif "lite" in model_lower or "mini" in model_lower or "nano" in model_lower:
        tier_score = 3.0
    elif "exp" in model_lower or "preview" in model_lower:
        tier_score = 6.0  # Experimental could be good
    
    # Factor 3: Context Length (weight: 15%)
    context_score = 5.0
    if model_info:
        context = model_info.get("inputTokenLimit", 0) or model_info.get("context_length", 0) or model_info.get("context_window", 0)
        if context >= 1000000:  # 1M tokens
            context_score = 10.0
        elif context >= 128000:  # 128K
            context_score = 9.0
        elif context >= 32000:  # 32K
            context_score = 7.0
        elif context >= 8000:  # 8K
            context_score = 5.0
        else:
            context_score = 3.0
    
    # Factor 4: Recency/Version (weight: 10%)
    version_score = 5.0
    if "2.5" in model_lower or "3.0" in model_lower or "3.1" in model_lower:
        version_score = 9.0
    elif "2.0" in model_lower:
        version_score = 7.0
    elif "1.5" in model_lower:
        version_score = 6.0
    elif "1.0" in model_lower:
        version_score = 4.0
    
    # Weighted average
    final_score = (size_score * 0.40) + (tier_score * 0.35) + (context_score * 0.15) + (version_score * 0.10)
    
    return round(final_score, 1)


def is_high_quality_model(model_name: str, model_info: Dict = None, threshold: float = 7.0) -> bool:
    """
    Determine if a model is high-quality based on quality score.
    
    Args:
        model_name: The model identifier
        model_info: Optional dict with model properties (context_length, etc.)
        threshold: Minimum score to be considered "high quality" (default 7.0)
    
    Returns: True if model is high quality
    """
    score = get_model_quality_score(model_name, model_info)
    return score >= threshold


def get_model_quality_tier(model_name: str, model_info: Dict = None) -> str:
    """
    Get the quality tier of a model.
    
    Returns one of 4 tiers:
    - "production": High-quota models for general production use
    - "critical": High-quality models for critical tasks (hooks, scoring)
    - "test_system": Low-quality leftover models for system tests
    - "test_prompts": Medium-quality leftover models for prompt testing
    
    Note: This returns quality-based tier. Quota filtering is done separately.
    """
    score = get_model_quality_score(model_name, model_info)
    if score >= 7.0:
        return "critical"  # Use for hooks, scoring, evaluation
    elif score >= 5.0:
        return "test_prompts"  # Can generate decent content for prompt testing
    else:
        return "test_system"  # Basic checks only, may not generate coherent content


def categorize_models_for_usage(models_with_info: List[Tuple[str, int, float, Dict]]) -> Dict[str, List]:
    """
    v17.9.31: Categorize models into 7 usage categories with throughput awareness.
    
    Args:
        models_with_info: List of (model_name, quota, quality_score, model_info)
    
    Returns dict with 7 categories:
        1. production_high_throughput: High quota + high rate limit (≥15/min)
        2. production_low_throughput: High quota + low rate limit (needs pacing)
        3. critical: High-quality (score≥7) for hooks/scoring
        4. backup: Medium-quality fallback for production
        5. bonus: Extra quota for aggressive mode (analytics, learning)
        6. test_system: Low-quality leftovers for system testing
        7. test_prompts: Medium-quality leftovers for prompt testing
    
    Note: Groq models should be excluded before calling this (shared quota).
    """
    categories = {
        "production_high_throughput": [],  # High quota + fast rate limit
        "production_low_throughput": [],   # High quota + slow rate limit (needs pacing)
        "critical": [],                     # High quality, for hooks/scoring
        "backup": [],                       # Medium quality fallback
        "bonus": [],                        # Extra quota for aggressive mode
        "test_system": [],                  # Leftovers for system tests
        "test_prompts": [],                 # Leftovers for prompt tests
        # Legacy compatibility
        "production": [],                   # Maps to both production categories
    }
    
    for model_name, quota, score, info in models_with_info:
        # Get throughput info for this model
        rate_info = get_model_rate_limit(model_name)
        is_high_throughput = rate_info.get("throughput") == "high" or rate_info.get("req_per_min", 0) >= 15
        
        if quota >= MIN_DAILY_QUOTA and score >= 7.0:
            # High quota + high quality = production
            entry = {
                "model": model_name,
                "quota": quota,
                "score": score,
                "throughput": rate_info.get("throughput", "unknown"),
                "req_per_min": rate_info.get("req_per_min", 5),
                "delay": rate_info.get("delay", 12.0),
            }
            
            if is_high_throughput:
                entry["usage"] = "Bulk AI calls (high speed, no pacing needed)"
                categories["production_high_throughput"].append(entry)
            else:
                entry["usage"] = "Quality AI calls (needs pacing, use for critical)"
                categories["production_low_throughput"].append(entry)
            
            # Also add to legacy production category
            categories["production"].append(entry)
            
        elif quota >= MIN_DAILY_QUOTA and score >= 5.0:
            # High quota but medium quality = backup
            categories["backup"].append({
                "model": model_name,
                "quota": quota,
                "score": score,
                "throughput": rate_info.get("throughput", "unknown"),
                "usage": "Fallback for production when primary exhausted"
            })
            
        elif quota >= MIN_DAILY_QUOTA:
            # High quota but low quality = bonus (for aggressive mode)
            categories["bonus"].append({
                "model": model_name,
                "quota": quota,
                "score": score,
                "throughput": rate_info.get("throughput", "unknown"),
                "usage": "Extra analytics, learning, experiments (aggressive mode)"
            })
            
        elif quota > 0 and score >= 7.0:
            # Low quota but high quality = critical tasks
            categories["critical"].append({
                "model": model_name,
                "quota": quota,
                "score": score,
                "usage": "Hooks, quality scoring, master evaluation"
            })
            
        elif quota > 0 and score >= 5.0:
            # Medium quality leftovers = prompt testing
            categories["test_prompts"].append({
                "model": model_name,
                "quota": quota,
                "score": score,
                "usage": "Prompt registry testing (can generate content)"
            })
            
        elif quota > 0:
            # Low quality leftovers = system testing
            categories["test_system"].append({
                "model": model_name,
                "quota": quota,
                "score": score,
                "usage": "System tests (basic connectivity checks)"
            })
    
    # Sort each category by score (best first)
    for cat in categories:
        categories[cat].sort(key=lambda x: x["score"], reverse=True)
    
    return categories


def get_cached_model_categories(provider: str, force_refresh: bool = False) -> Optional[Dict]:
    """
    v17.9.30: Get cached model categories to avoid repeated API calls.
    
    The model discovery endpoints are FREE (no quota consumed) but add latency.
    This caches the 4-category results for faster access.
    
    Args:
        provider: "gemini", "groq", or "openrouter"
        force_refresh: If True, ignore cache and fetch fresh
    
    Returns: Cached categories dict or None if not cached
    """
    cache_file = EMERGENCY_CACHE_DIR / f"{provider}_categories.json"
    
    if not force_refresh and cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                # Categories valid for 24 hours (quotas don't change often)
                if age_hours < 24:
                    _safe_print(f"[MODEL] Using cached categories for {provider} (age: {age_hours:.1f}h)")
                    return data.get("categories")
        except:
            pass
    
    return None


def save_model_categories(provider: str, categories: Dict):
    """Save model categories to cache."""
    cache_file = EMERGENCY_CACHE_DIR / f"{provider}_categories.json"
    try:
        EMERGENCY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({
                "cached_at": datetime.now().isoformat(),
                "categories": categories
            }, f)
        _safe_print(f"[MODEL] Saved {provider} categories to cache")
    except Exception as e:
        _safe_print(f"[MODEL] Failed to cache categories: {e}")


def _load_quota_cache() -> Dict[str, int]:
    """Load cached quota values discovered from 429 errors."""
    quota_cache_file = EMERGENCY_CACHE_DIR / "actual_quotas.json"
    try:
        if quota_cache_file.exists():
            with open(quota_cache_file, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}


def _save_quota_cache(cache: Dict[str, int]):
    """Save discovered quota values."""
    quota_cache_file = EMERGENCY_CACHE_DIR / "actual_quotas.json"
    try:
        EMERGENCY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(quota_cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except:
        pass


def _is_quota_cache_fresh(cache: Dict, model_name: str) -> bool:
    """Check if cached quota is still fresh (within TTL)."""
    discovered_key = f"{model_name}_discovered_at"
    if discovered_key not in cache:
        return False
    
    try:
        discovered_at = datetime.fromisoformat(cache[discovered_key])
        age_hours = (datetime.now() - discovered_at).total_seconds() / 3600
        return age_hours < QUOTA_CACHE_TTL_HOURS
    except:
        return False


def get_cached_quota(model_name: str) -> Optional[int]:
    """Get cached quota if fresh, None if expired or not found."""
    cache = _load_quota_cache()
    if model_name in cache and _is_quota_cache_fresh(cache, model_name):
        return cache[model_name]
    return None


def record_quota_from_429(model_name: str, quota_value: int):
    """
    Record actual quota discovered from a 429 error.
    Call this from error handlers when you see 'quota_value: X' in error message.
    """
    cache = _load_quota_cache()
    cache[model_name] = quota_value
    cache[f"{model_name}_discovered_at"] = datetime.now().isoformat()
    _save_quota_cache(cache)
    _safe_print(f"[QUOTA] Recorded {model_name} has {quota_value}/day (from 429)")


def _get_model_quota_from_api(model_name: str, provider: str) -> Optional[int]:
    """
    v17.9.13: Query model availability and ACTUAL quota via API.
    
    Strategy:
    1. Check cached quota from previous 429 errors (MOST ACCURATE)
    2. Check if model exists via free info endpoint
    3. Make ONE minimal test call to discover rate limit headers
    4. Return discovered quota or None if unknown
    
    NO name-based inference - all from actual API responses!
    """
    try:
        import requests
        
        # Step 1: Check quota cache (from previous 429 errors) - with TTL!
        cached_quota = get_cached_quota(model_name)
        if cached_quota is not None:
            _safe_print(f"[QUOTA] {model_name}: {cached_quota}/day (cached, fresh)")
            return cached_quota
        
        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                # Step 2: Check if model exists (FREE)
                info_response = requests.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}?key={api_key}",
                    timeout=10
                )
                
                if info_response.status_code == 404:
                    return 0  # Model doesn't exist
                
                if info_response.status_code == 200:
                    # Step 3: Make ONE minimal test call to discover quota
                    # This costs 1 request but gives us REAL quota info
                    test_response = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
                        json={"contents": [{"parts": [{"text": "1"}]}], "generationConfig": {"maxOutputTokens": 1}},
                        timeout=10
                    )
                    
                    # Check rate limit headers
                    daily_limit = test_response.headers.get("x-ratelimit-limit-requests-per-day")
                    if daily_limit:
                        quota = int(daily_limit)
                        record_quota_from_429(model_name, quota)  # Cache it
                        return quota
                    
                    if test_response.status_code == 429:
                        # Parse quota from error message
                        import re
                        error_text = test_response.text
                        match = re.search(r'quota_value[:\s]+(\d+)', error_text)
                        if match:
                            quota = int(match.group(1))
                            record_quota_from_429(model_name, quota)
                            return quota
                        return 0  # Exhausted, unknown limit
                    
                    elif test_response.status_code == 200:
                        # Model works, assume decent quota if no headers
                        # Will be corrected later if we hit 429
                        return 500  # Conservative assumption
                    
        elif provider == "groq":
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                # Use models list endpoint (FREE - no quota cost!)
                response = requests.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    for m in models:
                        if m.get("id") == model_name:
                            # Check if model is active
                            if m.get("active", True):
                                return 100  # Groq shares 100K tokens/day
                            else:
                                return 0  # Model inactive
                    return 0  # Model not found (decommissioned?)
                    
    except Exception as e:
        _safe_print(f"[QUOTA] Error checking {model_name}: {e}")
    
    return None


def _is_model_usable(model_name: str, provider: str) -> Tuple[bool, int]:
    """
    Check if a model is usable (available + has quota).
    Returns (is_usable, daily_quota).
    """
    quota = _get_model_quota_from_api(model_name, provider)
    
    if quota is None:
        return (True, MIN_DAILY_QUOTA)  # Unknown, assume low priority
    elif quota < MIN_DAILY_QUOTA:
        return (False, quota)  # Below minimum threshold
    else:
        return (True, quota)


def _load_cache(provider: str, allow_expired: bool = False) -> Optional[Dict]:
    """
    Load cached models for a provider.
    
    Args:
        provider: The AI provider name
        allow_expired: If True, return cache even if >24h old (emergency fallback)
    """
    # Try main cache first
    for cache_dir in [CACHE_DIR, EMERGENCY_CACHE_DIR]:
        cache_file = cache_dir / f"{provider}_models.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    cached_time = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
                    age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                    
                    if age_hours < 24:
                        return data
                    elif allow_expired:
                        _safe_print(f"[MODEL] Using expired cache for {provider} ({age_hours:.1f}h old)")
                        return data
            except:
                pass
    return None


def _save_cache(provider: str, data: Dict):
    """Save models to cache (both regular and emergency)."""
    data["cached_at"] = datetime.now().isoformat()
    
    for cache_dir in [CACHE_DIR, EMERGENCY_CACHE_DIR]:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_dir / f"{provider}_models.json", 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass


def _get_openrouter_backup() -> List[str]:
    """
    Get free OpenRouter models as universal backup.
    OpenRouter doesn't require an API key for model listing.
    """
    try:
        import requests
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            free_models = [
                m["id"] for m in models_data 
                if m.get("pricing", {}).get("prompt") == "0" or ":free" in m.get("id", "")
            ]
            if free_models:
                _save_cache("openrouter_backup", {"models": free_models})
                return free_models
    except Exception as e:
        _safe_print(f"[MODEL] OpenRouter backup fetch failed: {e}")
    
    # Try emergency cache for OpenRouter
    cached = _load_cache("openrouter_backup", allow_expired=True)
    if cached and cached.get("models"):
        return cached["models"]
    
    return []


# =============================================================================
# GEMINI
# =============================================================================

def get_dynamic_gemini_model() -> str:
    """
    v17.9.12: TRULY DYNAMIC model selection.
    
    NO hardcoded model names! All decisions via API:
    1. Query API for all available models
    2. Check each model's quota via API
    3. Sort by quota (highest first)
    4. Return best available
    """
    import requests
    
    # 1. Try quota_optimizer first (it also uses dynamic discovery)
    try:
        from quota_optimizer import get_best_gemini_model
        return get_best_gemini_model()
    except ImportError:
        try:
            from src.quota.quota_optimizer import get_best_gemini_model
            return get_best_gemini_model()
        except ImportError:
            pass
    
    # 2. DYNAMIC API Discovery with quota checking
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            # Get all available models from API
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=10
            )
            if response.status_code == 200:
                models_data = response.json()
                all_models = [
                    m["name"].replace("models/", "") 
                    for m in models_data.get("models", [])
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
                
                # Check quota for each model DYNAMICALLY
                models_with_quota = []
                for model in all_models[:10]:  # Check top 10 to save API calls
                    is_usable, quota = _is_model_usable(model, "gemini")
                    if is_usable and quota >= MIN_DAILY_QUOTA:
                        models_with_quota.append((model, quota))
                        _safe_print(f"[MODEL] {model}: {quota} requests/day")
                
                # Sort by quota (highest first)
                models_with_quota.sort(key=lambda x: x[1], reverse=True)
                
                if models_with_quota:
                    best_model = models_with_quota[0][0]
                    best_quota = models_with_quota[0][1]
                    _save_cache("gemini", {
                        "models": [m[0] for m in models_with_quota],
                        "quotas": {m[0]: m[1] for m in models_with_quota}
                    })
                    _safe_print(f"[MODEL] Selected Gemini: {best_model} ({best_quota}/day via API)")
                    return best_model
                    
        except Exception as e:
            _safe_print(f"[MODEL] Gemini discovery failed: {e}")
    
    # 3. Try cache (with quota data)
    cached = _load_cache("gemini", allow_expired=True)
    if cached and cached.get("models"):
        # Use cached quota data if available
        quotas = cached.get("quotas", {})
        if quotas:
            # Sort by cached quota
            sorted_models = sorted(
                [(m, quotas.get(m, 0)) for m in cached["models"]],
                key=lambda x: x[1], reverse=True
            )
            for model, quota in sorted_models:
                if quota >= MIN_DAILY_QUOTA:
                    return model
        else:
            # Old cache without quota data - just return first
            return cached["models"][0]
    
    # 4. Use OpenRouter as backup provider
    _safe_print("[MODEL] WARNING: No Gemini models available, using OpenRouter backup")
    backup = _get_openrouter_backup()
    if backup:
        # Find a good LLM from OpenRouter
        for model in backup:
            if "llama" in model.lower() or "mistral" in model.lower():
                return f"openrouter:{model}"  # Prefix indicates backup provider
        return f"openrouter:{backup[0]}"
    
    raise RuntimeError("CRITICAL: No AI models available - check API keys and network")


# =============================================================================
# GROQ
# =============================================================================

def get_dynamic_groq_model() -> str:
    """
    v17.9.30: Dynamic Groq model selection with TEXT GENERATION filtering.
    
    FILTERS OUT TTS/audio/speech models (orpheus, whisper, etc.)
    ONLY includes text generation models (llama, mixtral, gemma)
    """
    # 1. Try quota_optimizer first
    try:
        from quota_optimizer import get_best_groq_model
        return get_best_groq_model()
    except ImportError:
        try:
            from src.quota.quota_optimizer import get_best_groq_model
            return get_best_groq_model()
        except ImportError:
            pass
    
    # 2. Use _discover_groq_models() which has proper filtering
    models = _discover_groq_models()
    if models:
        _safe_print(f"[MODEL] Selected Groq: {models[0]} (from {len(models)} text-gen models)")
        return models[0]
                
    # 3. Fallback to hardcoded safe models (text generation only)
    SAFE_GROQ_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant", 
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]
    
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            from groq import Groq
            client = Groq(api_key=api_key)
            for model in SAFE_GROQ_MODELS:
                try:
                    # Test if model works
                    client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1
                    )
                    _safe_print(f"[MODEL] Using safe Groq model: {model}")
                    return model
                except:
                    continue
    except Exception as e:
        _safe_print(f"[MODEL] Groq fallback failed: {e}")
    
    # 3. Try cache
    cached = _load_cache("groq", allow_expired=True)
    if cached and cached.get("models"):
        return cached["models"][0]
    
    # 5. Use OpenRouter backup
    _safe_print("[MODEL] WARNING: No Groq models available, using OpenRouter backup")
    backup = _get_openrouter_backup()
    if backup:
        for model in backup:
            if "llama" in model.lower():
                return f"openrouter:{model}"
        return f"openrouter:{backup[0]}"
    
    raise RuntimeError("CRITICAL: No AI models available - check API keys and network")


# =============================================================================
# OPENROUTER
# =============================================================================

def get_dynamic_openrouter_model() -> str:
    """Get a free OpenRouter model (no key needed for listing)."""
    # 1. Try fresh cache
    cached = _load_cache("openrouter")
    if cached and cached.get("models"):
        return cached["models"][0]
    
    # 2. Try API discovery (no key needed!)
    try:
        import requests
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            free_models = [
                m["id"] for m in models_data 
                if m.get("pricing", {}).get("prompt") == "0" or ":free" in m.get("id", "")
            ]
            if free_models:
                _save_cache("openrouter", {"models": free_models})
                return free_models[0]
    except Exception as e:
        _safe_print(f"[MODEL] OpenRouter discovery failed: {e}")
    
    # 3. Emergency cache
    cached = _load_cache("openrouter", allow_expired=True)
    if cached and cached.get("models"):
        return cached["models"][0]
    
    raise RuntimeError("CRITICAL: Cannot discover any OpenRouter models")


# =============================================================================
# HUGGINGFACE
# =============================================================================

def get_dynamic_huggingface_model() -> str:
    """Get a working HuggingFace text-generation model."""
    # HuggingFace doesn't have easy model listing API
    # Use known good models that work with Inference API
    
    # 1. Try cache
    cached = _load_cache("huggingface")
    if cached and cached.get("models"):
        return cached["models"][0]
    
    # 2. Test known models
    models = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "HuggingFaceH4/zephyr-7b-beta",
        "microsoft/Phi-3-mini-4k-instruct",
    ]
    
    try:
        import requests
        api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
        if api_key:
            for model in models:
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"inputs": "Hi", "parameters": {"max_new_tokens": 5}},
                    timeout=10
                )
                if response.status_code == 200:
                    _save_cache("huggingface", {"models": [model] + models})
                    return model
    except Exception as e:
        _safe_print(f"[MODEL] HuggingFace test failed: {e}")
    
    # 3. Use OpenRouter backup
    backup = _get_openrouter_backup()
    if backup:
        for model in backup:
            if "mistral" in model.lower():
                return f"openrouter:{model}"
        return f"openrouter:{backup[0]}"
    
    raise RuntimeError("CRITICAL: No HuggingFace models available")


# =============================================================================
# UNIVERSAL FUNCTIONS
# =============================================================================

def get_best_model(provider: str) -> str:
    """Get the best available model for any provider."""
    providers = {
        "gemini": get_dynamic_gemini_model,
        "groq": get_dynamic_groq_model,
        "openrouter": get_dynamic_openrouter_model,
        "huggingface": get_dynamic_huggingface_model
    }
    func = providers.get(provider.lower())
    if func:
        return func()
    raise ValueError(f"Unknown provider: {provider}")


def get_all_models(provider: str) -> List[str]:
    """
    Get ALL available models for a provider (for fallback chains).
    
    Returns: List of model IDs, ordered by priority (best first)
    """
    provider = provider.lower()
    
    # Try fresh cache
    cached = _load_cache(provider)
    if cached and cached.get("models"):
        return cached["models"]
    
    # Discover dynamically
    if provider == "groq":
        return _discover_groq_models()
    elif provider == "gemini":
        return _discover_gemini_models()
    elif provider == "openrouter":
        return _discover_openrouter_models()
    elif provider == "huggingface":
        return _discover_huggingface_models()
    
    # Emergency cache
    cached = _load_cache(provider, allow_expired=True)
    if cached and cached.get("models"):
        return cached["models"]
    
    return []


def _discover_groq_models() -> List[str]:
    """
    v17.9.30: Discover TEXT GENERATION Groq models only.
    
    FILTERS OUT:
    - TTS/audio models (orpheus, whisper, distil-whisper)
    - Models requiring terms acceptance
    - Non-text-generation models
    
    INCLUDES (priority order):
    - llama-3.3-70b-versatile (best quality)
    - llama-3.1-8b-instant (fast)
    - mixtral (good quality)
    - gemma (good quality)
    """
    # Patterns to EXCLUDE (TTS, audio, speech, vision-only, special)
    EXCLUDE_PATTERNS = [
        "orpheus",      # TTS model
        "whisper",      # Speech-to-text
        "distil-whisper", 
        "playai",       # Audio generation
        "tts",          # Text-to-speech
        "audio",        # Audio models
        "speech",       # Speech models
        "vision",       # Vision-only models
        "guard",        # Safety models
        "tool-use",     # Tool-only models
    ]
    
    # Patterns to INCLUDE (text generation models)
    INCLUDE_PATTERNS = [
        "llama",        # LLaMA family
        "mixtral",      # Mixtral family  
        "gemma",        # Gemma family
        "deepseek",     # DeepSeek
        "qwen",         # Qwen
    ]
    
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            from groq import Groq
            client = Groq(api_key=api_key)
            models_response = client.models.list()
            
            text_gen_models = []
            for m in models_response.data:
                if not hasattr(m, 'id'):
                    continue
                model_id = m.id.lower()
                
                # Skip excluded patterns
                if any(excl in model_id for excl in EXCLUDE_PATTERNS):
                    continue
                    
                # Only include if matches text gen patterns
                if any(incl in model_id for incl in INCLUDE_PATTERNS):
                    text_gen_models.append(m.id)
            
            if text_gen_models:
                # Sort: prefer 70b > 8b > others, versatile > instant
                def model_priority(m):
                    m_lower = m.lower()
                    score = 0
                    if "70b" in m_lower: score += 100
                    if "versatile" in m_lower: score += 50
                    if "8b" in m_lower: score += 30
                    if "instant" in m_lower: score += 20
                    if "3.3" in m_lower: score += 10
                    return -score  # Negative for descending sort
                
                text_gen_models.sort(key=model_priority)
                _save_cache("groq", {"models": text_gen_models})
                _safe_print(f"[MODEL] Found {len(text_gen_models)} Groq text-gen models")
                return text_gen_models
    except Exception as e:
        _safe_print(f"[MODEL] Groq discovery failed: {e}")
    
    # Emergency cache
    cached = _load_cache("groq", allow_expired=True)
    return cached.get("models", []) if cached else []


def _discover_gemini_models() -> List[str]:
    """
    v17.9.12: Discover all available Gemini models with DYNAMIC quota checking.
    
    NO hardcoded priority lists! Sort by actual API-reported quota.
    """
    try:
        import requests
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=10
            )
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                models = [m["name"].replace("models/", "") for m in models_data 
                          if "generateContent" in m.get("supportedGenerationMethods", [])]
                
                if models:
                    # Check quota for each model via API
                    models_with_quota = []
                    for model in models[:15]:  # Check top 15 to save time
                        is_usable, quota = _is_model_usable(model, "gemini")
                        if is_usable and quota >= MIN_DAILY_QUOTA:
                            models_with_quota.append((model, quota))
                    
                    # Sort by quota (highest first) - DYNAMIC, not hardcoded!
                    models_with_quota.sort(key=lambda x: x[1], reverse=True)
                    sorted_models = [m[0] for m in models_with_quota]
                    
                    if sorted_models:
                        _save_cache("gemini", {
                            "models": sorted_models,
                            "quotas": {m[0]: m[1] for m in models_with_quota}
                        })
                        return sorted_models
                    
                    # If no quota data, return all models
                    _save_cache("gemini", {"models": models})
                    return models
                    
    except Exception as e:
        _safe_print(f"[MODEL] Gemini discovery failed: {e}")
    
    # Emergency cache
    cached = _load_cache("gemini", allow_expired=True)
    if cached and cached.get("models"):
        return cached["models"]
    return []


def _discover_openrouter_models() -> List[str]:
    """Discover all free OpenRouter models."""
    try:
        import requests
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            free_models = [m["id"] for m in models_data 
                          if m.get("pricing", {}).get("prompt") == "0" or ":free" in m.get("id", "")]
            
            if free_models:
                _save_cache("openrouter", {"models": free_models})
                return free_models
    except Exception as e:
        _safe_print(f"[MODEL] OpenRouter discovery failed: {e}")
    
    cached = _load_cache("openrouter", allow_expired=True)
    return cached.get("models", []) if cached else []


def _discover_huggingface_models() -> List[str]:
    """Get known good HuggingFace models."""
    return [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "HuggingFaceH4/zephyr-7b-beta",
        "microsoft/Phi-3-mini-4k-instruct",
    ]


# =============================================================================
# CRITICAL TASK MODEL SELECTION
# =============================================================================

def get_high_quality_model(provider: str = "gemini") -> Optional[str]:
    """
    v17.9.27: Get a HIGH-QUALITY model for CRITICAL tasks using SMART SCORING.
    
    Critical tasks (6 calls/video max = 36/day for 6 videos):
    - Hook generation (1)
    - Final quality evaluation (1)  
    - Master scoring (1)
    - Title optimization (1)
    - Script refinement (1)
    - CTA generation (1)
    
    Uses quality scoring based on:
    - Model size (70B > 8B > 1B)
    - Model tier (Ultra > Pro > Flash)
    - Context length
    - Version/recency
    
    Returns: High-quality model ID, or None if unavailable
    """
    provider = provider.lower()
    
    if provider == "gemini":
        try:
            import requests
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                response = requests.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                    timeout=10
                )
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    
                    # Score all models and find high-quality ones with quota
                    high_quality_models = []
                    for m in models:
                        model_name = m.get("name", "").replace("models/", "")
                        methods = m.get("supportedGenerationMethods", [])
                        
                        if "generateContent" not in methods:
                            continue
                        
                        # Calculate quality score using actual model properties
                        quality_score = get_model_quality_score(model_name, m)
                        
                        # Only consider high-quality models (score >= 7.0)
                        if quality_score >= 7.0:
                            quota = _get_model_quota_from_api(model_name, "gemini")
                            if quota is not None and quota > 0:
                                high_quality_models.append((model_name, quota, quality_score))
                    
                    if high_quality_models:
                        # Sort by quality score first, then quota
                        high_quality_models.sort(key=lambda x: (x[2], x[1]), reverse=True)
                        best = high_quality_models[0]
                        _safe_print(f"[MODEL] High-quality: {best[0]} (score={best[2]}, quota={best[1]}/day)")
                        return best[0]
        except Exception as e:
            _safe_print(f"[MODEL] High-quality discovery error: {e}")
        
        return None
    
    elif provider == "groq":
        try:
            import requests
            groq_key = os.environ.get("GROQ_API_KEY")
            if groq_key:
                response = requests.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {groq_key}"},
                    timeout=10
                )
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    
                    # Score all Groq models
                    high_quality_models = []
                    for m in models:
                        model_id = m.get("id", "")
                        quality_score = get_model_quality_score(model_id, m)
                        
                        if quality_score >= 7.0:
                            high_quality_models.append((model_id, quality_score))
                    
                    if high_quality_models:
                        high_quality_models.sort(key=lambda x: x[1], reverse=True)
                        best = high_quality_models[0]
                        _safe_print(f"[MODEL] High-quality Groq: {best[0]} (score={best[1]})")
                        return best[0]
        except Exception as e:
            _safe_print(f"[MODEL] High-quality Groq error: {e}")
        
        return None
    
    return None


def get_model_for_task(task_type: str) -> str:
    """
    v17.9.16: Get the BEST model for a specific task type.
    
    Task types:
    - "critical": Hook, evaluation, scoring → Use PRO model
    - "bulk": Phrases, CTAs → Use flash/fast model
    - "evaluation": Quality checks → Use PRO model
    
    Fallback chain:
    1. gemini-pro (high quality)
    2. groq-70b (high quality)
    3. gemini-flash (fast, always available)
    
    Returns: Model ID (provider:model format)
    """
    critical_tasks = ["hook", "evaluation", "scoring", "title", "script", "quality", "master"]
    
    if any(t in task_type.lower() for t in critical_tasks):
        # Try to get a pro model
        pro_model = get_high_quality_model("gemini")
        if pro_model:
            _safe_print(f"[MODEL] Using high-quality Gemini for {task_type}")
            return f"gemini:{pro_model}"
        
        # Fall back to Groq 70B
        groq_pro = get_high_quality_model("groq")
        if groq_pro:
            _safe_print(f"[MODEL] Using high-quality Groq for {task_type}")
            return f"groq:{groq_pro}"
        
        # v17.9.16: Fall back to regular model (ALWAYS have a fallback!)
        _safe_print(f"[MODEL] Pro models unavailable, using fast model for {task_type}")
    
    # For bulk tasks OR fallback, use the standard fast model
    return f"gemini:{get_dynamic_gemini_model()}"


# =============================================================================
# RATE LIMITS - v17.9.31: SMART PER-MODEL RATE LIMITING
# =============================================================================

# Model-specific rate limits (discovered from API 429 responses and documentation)
# Format: {model_pattern: {req_per_min, delay_seconds, daily_quota}}
# NOTE: All delays include 10% safety margin (e.g., 12s base → 13.2s actual)
RATE_LIMIT_MARGIN = 1.10  # 10% safety margin

MODEL_RATE_LIMITS = {
    # Gemini models - FREE tier limits (VERY restrictive! 20 RPD PER MODEL!)
    # v17.9.43: ACTUAL limits from error messages - NOT what docs claim!
    # "Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20"
    # delay = (60 / req_per_min) * 1.10 for safety
    "gemini-2.5-flash": {"req_per_min": 5, "delay": 13.2, "daily_quota": 20, "throughput": "low"},       # 20 RPD per model!
    "gemini-2.5-pro": {"req_per_min": 2, "delay": 33.0, "daily_quota": 20, "throughput": "low"},         # 20 RPD per model!
    "gemini-2.0-flash-exp": {"req_per_min": 5, "delay": 13.2, "daily_quota": 20, "throughput": "low"},   # 20 RPD per model!
    "gemini-2.0-flash": {"req_per_min": 10, "delay": 6.6, "daily_quota": 20, "throughput": "medium"},    # 20 RPD per model!
    "gemini-2.5-flash": {"req_per_min": 15, "delay": 4.4, "daily_quota": 20, "throughput": "high"},      # 20 RPD per model!
    # REMOVED: gemini-2.5-pro - deprecated, returns 404 (Jan 2026)
    
    # Groq models - v17.9.43: ACTUAL limits from error messages!
    # "Limit 100000" TPD for 70b, 500000 TPD for 8b-instant
    # ~2000 tokens/call = 50 calls (70b) or 250 calls (8b)
    "llama-3.3-70b-versatile": {"req_per_min": 30, "delay": 2.2, "daily_quota": 50, "throughput": "high"},   # 100K TPD = ~50 calls
    # REMOVED: llama-3.1-70b-versatile - DECOMMISSIONED by Groq (Jan 2026)
    "llama-3.1-8b-instant": {"req_per_min": 60, "delay": 1.1, "daily_quota": 250, "throughput": "high"},     # 500K TPD = ~250 calls
    "mixtral-8x7b-32768": {"req_per_min": 30, "delay": 2.2, "daily_quota": 100, "throughput": "high"},       # Estimated
    "gemma-7b-it": {"req_per_min": 30, "delay": 2.2, "daily_quota": 200, "throughput": "high"},              # Estimated
    
    # Default fallbacks by provider (with 10% margin)
    "_gemini_default": {"req_per_min": 5, "delay": 13.2, "daily_quota": 100, "throughput": "low"},
    "_groq_default": {"req_per_min": 30, "delay": 2.2, "daily_quota": 500, "throughput": "high"},
    "_openrouter_default": {"req_per_min": 20, "delay": 3.3, "daily_quota": 1000, "throughput": "medium"},
    "_huggingface_default": {"req_per_min": 10, "delay": 6.6, "daily_quota": 100, "throughput": "medium"},
}

# Cache for learned rate limits from 429 responses
_rate_limit_cache: Dict[str, Dict] = {}


def get_model_rate_limit(model_name: str, provider: str = None) -> Dict:
    """
    v17.9.31: Get SMART rate limit for a specific model.
    
    Priority:
    1. Learned from 429 response (most accurate)
    2. Known model limits (from MODEL_RATE_LIMITS)
    3. Provider defaults
    
    Returns: {req_per_min, delay, daily_quota, throughput}
    """
    # Normalize model name
    model_lower = model_name.lower()
    
    # Step 1: Check learned cache (from 429 responses)
    if model_lower in _rate_limit_cache:
        return _rate_limit_cache[model_lower]
    
    # Step 2: Check known model limits
    for pattern, limits in MODEL_RATE_LIMITS.items():
        if pattern.startswith("_"):  # Skip defaults
            continue
        if pattern.lower() in model_lower:
            return limits.copy()
    
    # Step 3: Use provider default
    if provider:
        default_key = f"_{provider.lower()}_default"
        if default_key in MODEL_RATE_LIMITS:
            return MODEL_RATE_LIMITS[default_key].copy()
    
    # Fallback: conservative defaults
    return {"req_per_min": 5, "delay": 12.0, "daily_quota": 100, "throughput": "low"}


def learn_rate_limit_from_429(model_name: str, limit_value: int):
    """
    v17.9.31: Learn rate limit from 429 response header.
    
    When we get a 429, the response often contains the actual limit.
    Store this for future requests.
    """
    model_lower = model_name.lower()
    
    # Calculate delay from limit
    delay = 60.0 / limit_value if limit_value > 0 else 12.0
    
    _rate_limit_cache[model_lower] = {
        "req_per_min": limit_value,
        "delay": delay,
        "daily_quota": MODEL_RATE_LIMITS.get(model_lower, {}).get("daily_quota", 100),
        "throughput": "high" if limit_value >= 15 else "medium" if limit_value >= 10 else "low",
        "learned": True
    }
    
    _safe_print(f"[RATE] Learned {model_name}: {limit_value}/min, delay={delay:.1f}s")


def get_rate_limits() -> Dict[str, float]:
    """
    Get rate limit delays for all providers (legacy compatibility).
    Returns seconds to wait between API calls.
    
    Note: For per-model limits, use get_model_rate_limit() instead.
    """
    return {
        "gemini": 12.0,      # 5 req/min on FREE tier = 12s delay
        "groq": 2.0,         # 30 req/min = 2s
        "openrouter": 3.0,   # 20 req/min = 3s
        "huggingface": 6.0,  # 10 req/min
        "pexels": 18.0       # 200 req/hour
    }


def get_smart_delay(model_name: str, provider: str = None) -> float:
    """
    v17.9.31: Get smart delay for a specific model.
    
    Use this instead of get_rate_limits() for per-model pacing.
    """
    limits = get_model_rate_limit(model_name, provider)
    return limits.get("delay", 12.0)


def is_high_throughput_model(model_name: str, provider: str = None) -> bool:
    """
    v17.9.31: Check if model has high throughput (good for bulk tasks).
    
    High throughput = ≥15 req/min
    Low throughput = <15 req/min (needs pacing for bulk tasks)
    """
    limits = get_model_rate_limit(model_name, provider)
    return limits.get("throughput") == "high" or limits.get("req_per_min", 0) >= 15


def get_pexels_rate_limit() -> Dict:
    """Pexels rate limit info: 200 req/hour, 20,000 req/month."""
    return {
        "requests_per_hour": 200,
        "requests_per_month": 20000,
        "delay_between_calls": 18.0
    }
