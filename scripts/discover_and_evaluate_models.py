#!/usr/bin/env python3
"""
ViralShorts Factory - Comprehensive Model Discovery & Evaluation
=================================================================

This script performs COMPLETE model discovery from all providers and shows:
1. ALL available models with their quotas and rate limits
2. Categorization: PRODUCTION, CRITICAL, BACKUP, TEST_SYSTEM, TEST_PROMPTS
3. What models will be used for what steps in which workflows
4. Rate limit analysis with safety margins
5. Quota pool summary (reserved vs available)

Run this in GitHub Actions (has API keys) to see full picture.

v17.9.33 - Zero 429 Error Edition
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def safe_print(msg: str):
    """Print with encoding fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())


# =============================================================================
# RATE LIMIT CONFIGURATION (with 10% safety margin)
# =============================================================================

RATE_LIMIT_MARGIN = 1.10  # 10% safety margin

# Known provider defaults (used when model-specific limits unknown)
PROVIDER_DEFAULTS = {
    "gemini": {"req_per_min": 15, "daily_quota": 1500},  # Flash defaults
    "groq": {"req_per_min": 30, "daily_quota": 14400},   # Shared across all models!
    "openrouter": {"req_per_min": 60, "daily_quota": 10000},  # Free tier
    "huggingface": {"req_per_min": 100, "daily_quota": 2400},
}

# Model-specific rate limits (more accurate than defaults)
MODEL_RATE_LIMITS = {
    # Gemini Pro models - VERY LIMITED (5 req/min)
    "gemini-1.5-pro": {"req_per_min": 5, "daily_quota": 50},
    "gemini-2.0-pro": {"req_per_min": 2, "daily_quota": 50},
    "gemini-2.5-pro": {"req_per_min": 2, "daily_quota": 25},
    
    # Gemini Flash models - Higher throughput (15 req/min)
    "gemini-1.5-flash": {"req_per_min": 15, "daily_quota": 1500},
    "gemini-2.0-flash": {"req_per_min": 15, "daily_quota": 500},
    "gemini-2.0-flash-lite": {"req_per_min": 30, "daily_quota": 1500},
    
    # Groq - All share 14,400/day quota!
    "llama-3.3-70b-versatile": {"req_per_min": 30, "daily_quota": 14400, "shared_quota": True},
    "llama-3.1-8b-instant": {"req_per_min": 60, "daily_quota": 14400, "shared_quota": True},
    "gemma2-9b-it": {"req_per_min": 30, "daily_quota": 14400, "shared_quota": True},
    "mixtral-8x7b-32768": {"req_per_min": 30, "daily_quota": 14400, "shared_quota": True},
    
    # OpenRouter free tier
    "meta-llama/llama-3.2-3b-instruct:free": {"req_per_min": 20, "daily_quota": 200},
    "google/gemma-2-9b-it:free": {"req_per_min": 20, "daily_quota": 200},
}


def calculate_safe_delay(req_per_min: int) -> float:
    """Calculate delay with 10% safety margin."""
    base_delay = 60.0 / req_per_min
    return round(base_delay * RATE_LIMIT_MARGIN, 2)


def get_model_rate_info(model_name: str, provider: str = None) -> Dict:
    """Get rate limit info for a model with safety margin applied."""
    # Check model-specific limits first
    for known_model, limits in MODEL_RATE_LIMITS.items():
        if known_model in model_name.lower():
            req_per_min = limits["req_per_min"]
            return {
                "req_per_min": req_per_min,
                "daily_quota": limits["daily_quota"],
                "base_delay": 60.0 / req_per_min,
                "safe_delay": calculate_safe_delay(req_per_min),
                "shared_quota": limits.get("shared_quota", False),
                "source": "model_specific"
            }
    
    # Fall back to provider defaults
    if provider and provider in PROVIDER_DEFAULTS:
        defaults = PROVIDER_DEFAULTS[provider]
        req_per_min = defaults["req_per_min"]
        return {
            "req_per_min": req_per_min,
            "daily_quota": defaults["daily_quota"],
            "base_delay": 60.0 / req_per_min,
            "safe_delay": calculate_safe_delay(req_per_min),
            "shared_quota": False,
            "source": "provider_default"
        }
    
    # Unknown - use conservative defaults
    return {
        "req_per_min": 5,
        "daily_quota": 100,
        "base_delay": 12.0,
        "safe_delay": 13.2,
        "shared_quota": False,
        "source": "unknown_conservative"
    }


# =============================================================================
# MODEL QUALITY SCORING
# =============================================================================

def get_model_quality_score(model_name: str, model_info: Dict = None) -> float:
    """Calculate quality score 0-10 based on model properties."""
    score = 5.0
    model_lower = model_name.lower()
    
    # Size score (40%)
    size_score = 5.0
    if "70b" in model_lower or "72b" in model_lower:
        size_score = 10.0
    elif "32b" in model_lower or "34b" in model_lower:
        size_score = 8.5
    elif "13b" in model_lower or "14b" in model_lower:
        size_score = 7.0
    elif "8b" in model_lower or "9b" in model_lower:
        size_score = 6.0
    elif "3b" in model_lower or "4b" in model_lower:
        size_score = 4.0
    
    # Tier score (35%)
    tier_score = 5.0
    if "ultra" in model_lower:
        tier_score = 10.0
    elif "pro" in model_lower:
        tier_score = 8.5
    elif "flash" in model_lower or "turbo" in model_lower:
        tier_score = 5.5
    elif "lite" in model_lower or "mini" in model_lower:
        tier_score = 3.0
    
    # Context score (15%)
    context_score = 5.0
    if model_info:
        context = model_info.get("inputTokenLimit", 0) or model_info.get("context_window", 0)
        if context >= 1000000:
            context_score = 10.0
        elif context >= 128000:
            context_score = 9.0
        elif context >= 32000:
            context_score = 7.0
    
    # Version score (10%)
    version_score = 5.0
    if "2.5" in model_lower or "3.0" in model_lower:
        version_score = 9.0
    elif "2.0" in model_lower:
        version_score = 7.0
    elif "1.5" in model_lower:
        version_score = 6.0
    
    return round((size_score * 0.40) + (tier_score * 0.35) + (context_score * 0.15) + (version_score * 0.10), 1)


# =============================================================================
# MODEL DISCOVERY - ALL PROVIDERS
# =============================================================================

@dataclass
class DiscoveredModel:
    provider: str
    model_id: str
    display_name: str
    quality_score: float
    req_per_min: int
    daily_quota: int
    safe_delay: float
    shared_quota: bool
    context_length: int
    is_text_gen: bool
    category: str = ""  # Will be assigned later


def discover_gemini_models() -> List[DiscoveredModel]:
    """Discover all Gemini models via API."""
    models = []
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        safe_print("[WARN] No GEMINI_API_KEY - skipping Gemini discovery")
        return models
    
    try:
        resp = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("models", []):
                name = m.get("name", "").replace("models/", "")
                
                # Skip non-text-generation models
                supported = m.get("supportedGenerationMethods", [])
                if "generateContent" not in supported:
                    continue
                
                rate_info = get_model_rate_info(name, "gemini")
                context = m.get("inputTokenLimit", 0)
                
                models.append(DiscoveredModel(
                    provider="gemini",
                    model_id=name,
                    display_name=m.get("displayName", name),
                    quality_score=get_model_quality_score(name, m),
                    req_per_min=rate_info["req_per_min"],
                    daily_quota=rate_info["daily_quota"],
                    safe_delay=rate_info["safe_delay"],
                    shared_quota=False,
                    context_length=context,
                    is_text_gen=True
                ))
                
        safe_print(f"[OK] Discovered {len(models)} Gemini models")
    except Exception as e:
        safe_print(f"[ERROR] Gemini discovery failed: {e}")
    
    return models


def discover_groq_models() -> List[DiscoveredModel]:
    """Discover all Groq models via API."""
    models = []
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        safe_print("[WARN] No GROQ_API_KEY - skipping Groq discovery")
        return models
    
    try:
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("data", []):
                model_id = m.get("id", "")
                
                # Filter out non-text-generation (TTS, whisper, etc.)
                id_lower = model_id.lower()
                is_text_gen = any(x in id_lower for x in ["llama", "mixtral", "gemma", "qwen"]) and \
                              not any(x in id_lower for x in ["whisper", "tts", "audio", "speech", "orpheus"])
                
                if not is_text_gen:
                    continue
                
                rate_info = get_model_rate_info(model_id, "groq")
                context = m.get("context_window", 8192)
                
                models.append(DiscoveredModel(
                    provider="groq",
                    model_id=model_id,
                    display_name=model_id,
                    quality_score=get_model_quality_score(model_id, m),
                    req_per_min=rate_info["req_per_min"],
                    daily_quota=rate_info["daily_quota"],
                    safe_delay=rate_info["safe_delay"],
                    shared_quota=True,  # All Groq models share quota!
                    context_length=context,
                    is_text_gen=True
                ))
                
        safe_print(f"[OK] Discovered {len(models)} Groq text-gen models")
    except Exception as e:
        safe_print(f"[ERROR] Groq discovery failed: {e}")
    
    return models


def discover_openrouter_models() -> List[DiscoveredModel]:
    """Discover OpenRouter free models via API."""
    models = []
    
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("data", []):
                model_id = m.get("id", "")
                
                # Only include free models
                pricing = m.get("pricing", {})
                if float(pricing.get("prompt", "1")) > 0:
                    continue
                
                context = m.get("context_length", 4096)
                
                models.append(DiscoveredModel(
                    provider="openrouter",
                    model_id=model_id,
                    display_name=m.get("name", model_id),
                    quality_score=get_model_quality_score(model_id, m),
                    req_per_min=20,  # Free tier limit
                    daily_quota=200,  # Conservative estimate
                    safe_delay=calculate_safe_delay(20),
                    shared_quota=False,
                    context_length=context,
                    is_text_gen=True
                ))
                
        safe_print(f"[OK] Discovered {len(models)} OpenRouter free models")
    except Exception as e:
        safe_print(f"[ERROR] OpenRouter discovery failed: {e}")
    
    return models


# =============================================================================
# MODEL CATEGORIZATION
# =============================================================================

def categorize_models(all_models: List[DiscoveredModel]) -> Dict[str, List[DiscoveredModel]]:
    """
    Categorize all discovered models into usage categories.
    
    Categories:
    1. PRODUCTION_HIGH_THROUGHPUT: High quota + high throughput (>= 15 req/min)
       - Used for: bulk content generation, scripts, CTAs
    
    2. PRODUCTION_LOW_THROUGHPUT: High quality but limited throughput (< 15 req/min)
       - Used for: critical tasks like hooks, quality scoring
    
    3. BACKUP: High quality models as backup for production
       - Used when primary models hit rate limits
    
    4. TEST_PROMPTS: Medium quality for testing prompts
       - Used in test workflow for prompt validation
    
    5. TEST_SYSTEM: Low quality for system testing
       - Used in test workflow for infrastructure checks
    
    6. BONUS: Leftover quota that would be wasted
       - Used in aggressive mode for extra analytics
    """
    categories = {
        "PRODUCTION_HIGH_THROUGHPUT": [],
        "PRODUCTION_LOW_THROUGHPUT": [],
        "BACKUP": [],
        "TEST_PROMPTS": [],
        "TEST_SYSTEM": [],
        "BONUS": [],
    }
    
    for model in all_models:
        score = model.quality_score
        rpm = model.req_per_min
        quota = model.daily_quota
        
        # Skip shared quota models from PRODUCTION (Groq)
        # They're useful as backup/fallback only
        if model.shared_quota:
            if score >= 7.0:
                model.category = "BACKUP"
                categories["BACKUP"].append(model)
            else:
                model.category = "BONUS"
                categories["BONUS"].append(model)
            continue
        
        # High quota production models
        if quota >= 200:
            if rpm >= 15 and score >= 6.0:
                model.category = "PRODUCTION_HIGH_THROUGHPUT"
                categories["PRODUCTION_HIGH_THROUGHPUT"].append(model)
            elif score >= 7.0:
                model.category = "PRODUCTION_LOW_THROUGHPUT"
                categories["PRODUCTION_LOW_THROUGHPUT"].append(model)
            elif score >= 5.0:
                model.category = "BACKUP"
                categories["BACKUP"].append(model)
            else:
                model.category = "TEST_SYSTEM"
                categories["TEST_SYSTEM"].append(model)
        # Low quota - test or bonus
        elif quota >= 25:
            if score >= 7.0:
                model.category = "PRODUCTION_LOW_THROUGHPUT"
                categories["PRODUCTION_LOW_THROUGHPUT"].append(model)
            elif score >= 5.0:
                model.category = "TEST_PROMPTS"
                categories["TEST_PROMPTS"].append(model)
            else:
                model.category = "TEST_SYSTEM"
                categories["TEST_SYSTEM"].append(model)
        else:
            model.category = "BONUS"
            categories["BONUS"].append(model)
    
    # Sort each category by quality score
    for cat in categories:
        categories[cat].sort(key=lambda m: m.quality_score, reverse=True)
    
    return categories


# =============================================================================
# WORKFLOW STEP ASSIGNMENTS
# =============================================================================

def get_step_model_assignments(categories: Dict[str, List[DiscoveredModel]]) -> Dict[str, Dict]:
    """
    Determine which models will be used for which workflow steps.
    
    Returns a mapping of workflow:step -> primary model + fallback chain
    """
    assignments = {}
    
    # Get best models from each category
    high_tp = categories.get("PRODUCTION_HIGH_THROUGHPUT", [])
    low_tp = categories.get("PRODUCTION_LOW_THROUGHPUT", [])
    backups = categories.get("BACKUP", [])
    
    # Video Generation Workflow Steps
    assignments["generate.yml"] = {
        "topic_generation": {
            "primary": high_tp[0] if high_tp else None,
            "fallback": [m for m in (high_tp[1:2] + backups[:2])] if high_tp else backups[:2],
            "why": "Needs creativity, uses high-throughput models for bulk generation"
        },
        "script_writing": {
            "primary": high_tp[0] if high_tp else None,
            "fallback": [m for m in (high_tp[1:2] + backups[:2])] if high_tp else backups[:2],
            "why": "Creative task, needs good language model"
        },
        "hook_generation": {
            "primary": low_tp[0] if low_tp else (high_tp[0] if high_tp else None),
            "fallback": [m for m in (low_tp[1:2] + high_tp[:1])] if low_tp else high_tp[:2],
            "why": "Critical for engagement - uses best quality model even if slow"
        },
        "cta_generation": {
            "primary": high_tp[0] if high_tp else None,
            "fallback": backups[:2],
            "why": "Less critical, uses high-throughput for speed"
        },
        "quality_scoring": {
            "primary": low_tp[0] if low_tp else (high_tp[0] if high_tp else None),
            "fallback": [m for m in (low_tp[1:2] + high_tp[:1])] if low_tp else high_tp[:2],
            "why": "Needs reasoning ability for accurate scoring"
        },
    }
    
    # Analytics Workflow
    assignments["analytics-feedback.yml"] = {
        "performance_analysis": {
            "primary": low_tp[0] if low_tp else (high_tp[0] if high_tp else None),
            "fallback": high_tp[:2] if high_tp else backups[:2],
            "why": "Needs deep reasoning for pattern analysis"
        },
        "trend_detection": {
            "primary": high_tp[0] if high_tp else None,
            "fallback": backups[:2],
            "why": "Can use faster model for trend processing"
        },
    }
    
    # Pre-work Workflow
    assignments["pre-work.yml"] = {
        "concept_generation": {
            "primary": high_tp[0] if high_tp else None,
            "fallback": backups[:2],
            "why": "Bulk generation of concepts uses high-throughput"
        },
        "concept_evaluation": {
            "primary": low_tp[0] if low_tp else (high_tp[0] if high_tp else None),
            "fallback": high_tp[:2] if high_tp else backups[:2],
            "why": "Quality filtering needs better reasoning"
        },
    }
    
    # Test Workflow (uses non-production models)
    test_prompts = categories.get("TEST_PROMPTS", [])
    test_system = categories.get("TEST_SYSTEM", [])
    assignments["test-systems-dry-run.yml"] = {
        "prompt_testing": {
            "primary": test_prompts[0] if test_prompts else None,
            "fallback": test_prompts[1:3] if len(test_prompts) > 1 else [],
            "why": "Uses leftover quota to validate prompts work"
        },
        "system_testing": {
            "primary": test_system[0] if test_system else (test_prompts[0] if test_prompts else None),
            "fallback": test_system[1:3] if len(test_system) > 1 else [],
            "why": "Uses lowest-tier models for infrastructure checks"
        },
    }
    
    return assignments


# =============================================================================
# QUOTA POOL ANALYSIS
# =============================================================================

def calculate_quota_pools(categories: Dict[str, List[DiscoveredModel]]) -> Dict:
    """Calculate quota pools - reserved for production vs available for bonus."""
    
    # Estimate daily production needs
    DAILY_PRODUCTION_NEEDS = {
        "video_generation": 50,  # ~50 AI calls per video * 6 videos
        "analytics": 20,
        "pre_work": 30,
    }
    
    total_production_need = sum(DAILY_PRODUCTION_NEEDS.values()) * 1.10  # 10% margin
    
    # Calculate available quota per category
    pool_summary = {
        "production_reserved": {},
        "bonus_available": {},
        "total_daily_need": int(total_production_need),
    }
    
    # Production high-throughput
    high_tp = categories.get("PRODUCTION_HIGH_THROUGHPUT", [])
    if high_tp:
        total_quota = sum(m.daily_quota for m in high_tp if not m.shared_quota)
        reserved = min(total_quota, int(total_production_need * 0.7))  # 70% of needs
        pool_summary["production_reserved"]["high_throughput"] = reserved
        pool_summary["bonus_available"]["high_throughput"] = total_quota - reserved
    
    # Production low-throughput (for critical tasks)
    low_tp = categories.get("PRODUCTION_LOW_THROUGHPUT", [])
    if low_tp:
        total_quota = sum(m.daily_quota for m in low_tp if not m.shared_quota)
        reserved = min(total_quota, int(total_production_need * 0.3))  # 30% of needs
        pool_summary["production_reserved"]["low_throughput"] = reserved
        pool_summary["bonus_available"]["low_throughput"] = total_quota - reserved
    
    # Backup pool (Groq shared quota)
    backups = categories.get("BACKUP", [])
    if backups:
        # Groq has 14,400 shared quota
        shared = [m for m in backups if m.shared_quota]
        if shared:
            pool_summary["production_reserved"]["groq_backup"] = 100  # Reserve some for fallback
            pool_summary["bonus_available"]["groq_backup"] = 14400 - 100
    
    # OpenRouter bonus
    bonus = categories.get("BONUS", [])
    openrouter_bonus = sum(m.daily_quota for m in bonus if m.provider == "openrouter")
    pool_summary["bonus_available"]["openrouter"] = openrouter_bonus
    
    return pool_summary


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report(all_models: List[DiscoveredModel], 
                   categories: Dict[str, List[DiscoveredModel]],
                   assignments: Dict[str, Dict],
                   quota_pools: Dict):
    """Generate comprehensive report."""
    
    print("\n" + "=" * 80)
    print("  VIRALSHORTS FACTORY - MODEL DISCOVERY & EVALUATION REPORT")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("=" * 80)
    
    # Summary
    print("\n" + "-" * 40)
    print("  DISCOVERY SUMMARY")
    print("-" * 40)
    print(f"  Total models discovered: {len(all_models)}")
    for provider in ["gemini", "groq", "openrouter"]:
        count = len([m for m in all_models if m.provider == provider])
        print(f"    - {provider.upper()}: {count}")
    
    # Categories
    print("\n" + "-" * 40)
    print("  MODEL CATEGORIES")
    print("-" * 40)
    
    for cat_name, models in categories.items():
        if not models:
            continue
        print(f"\n  [{cat_name}] ({len(models)} models)")
        print("  " + "-" * 70)
        print(f"  {'Model':<40} {'Score':>6} {'RPM':>5} {'Delay':>7} {'Quota':>7}")
        print("  " + "-" * 70)
        for m in models[:5]:  # Show top 5
            print(f"  {m.model_id[:40]:<40} {m.quality_score:>6.1f} {m.req_per_min:>5} {m.safe_delay:>6.1f}s {m.daily_quota:>7}")
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more")
    
    # Rate Limit Analysis
    print("\n" + "-" * 40)
    print("  RATE LIMIT ANALYSIS (10% Safety Margin Applied)")
    print("-" * 40)
    print(f"  {'Model':<35} {'Base Delay':>12} {'Safe Delay':>12} {'Margin':>8}")
    print("  " + "-" * 70)
    
    for m in all_models:
        if m.provider in ["gemini", "groq"]:
            base = 60.0 / m.req_per_min
            print(f"  {m.model_id[:35]:<35} {base:>10.1f}s {m.safe_delay:>10.1f}s {'+10%':>8}")
    
    # Workflow Assignments
    print("\n" + "-" * 40)
    print("  WORKFLOW -> STEP -> MODEL ASSIGNMENTS")
    print("-" * 40)
    
    for workflow, steps in assignments.items():
        print(f"\n  {workflow}")
        print("  " + "=" * 60)
        for step, info in steps.items():
            primary = info["primary"]
            fallbacks = info["fallback"]
            print(f"\n    {step}:")
            if primary:
                print(f"      PRIMARY: {primary.provider}:{primary.model_id}")
                print(f"               (score={primary.quality_score}, delay={primary.safe_delay}s)")
            else:
                print(f"      PRIMARY: None available!")
            if fallbacks:
                fb_str = ", ".join([f"{m.model_id}" for m in fallbacks[:2]])
                print(f"      FALLBACK: {fb_str}")
            print(f"      REASON: {info['why']}")
    
    # Quota Pools
    print("\n" + "-" * 40)
    print("  QUOTA POOL SUMMARY")
    print("-" * 40)
    print(f"\n  Daily Production Need: ~{quota_pools['total_daily_need']} API calls (with 10% margin)")
    
    print("\n  RESERVED FOR PRODUCTION:")
    reserved = quota_pools.get("production_reserved", {})
    for pool, amount in reserved.items():
        print(f"    - {pool}: {amount} calls/day")
    
    print("\n  AVAILABLE FOR BONUS (Aggressive Mode):")
    bonus = quota_pools.get("bonus_available", {})
    total_bonus = 0
    for pool, amount in bonus.items():
        print(f"    - {pool}: {amount} calls/day")
        total_bonus += amount
    print(f"\n  TOTAL BONUS POOL: {total_bonus} calls/day")
    
    # 429 Prevention Summary
    print("\n" + "-" * 40)
    print("  429 ERROR PREVENTION")
    print("-" * 40)
    print("""
  With 10% safety margin on all delays:
  - gemini-1.5-flash: 4.0s -> 4.4s (15 RPM)
  - gemini-1.5-pro:   12.0s -> 13.2s (5 RPM)
  - gemini-2.0-pro:   30.0s -> 33.0s (2 RPM)
  - groq models:      2.0s -> 2.2s (30 RPM)
  
  Expected 429 errors: ZERO (if delays are properly applied)
    """)
    
    print("\n" + "=" * 80)
    print("  END OF REPORT")
    print("=" * 80 + "\n")
    
    # Save report as JSON
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_models": len(all_models),
        "categories": {
            cat: [{"model": m.model_id, "provider": m.provider, "score": m.quality_score, 
                   "safe_delay": m.safe_delay, "quota": m.daily_quota}
                  for m in models]
            for cat, models in categories.items()
        },
        "quota_pools": quota_pools,
        "rate_limit_margin": "10%"
    }
    
    os.makedirs("test_output", exist_ok=True)
    with open("test_output/model_discovery_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    print("[OK] Report saved to test_output/model_discovery_report.json")


# =============================================================================
# MAIN
# =============================================================================

def main():
    safe_print("\n[START] Comprehensive Model Discovery & Evaluation")
    safe_print("=" * 60)
    
    # Discover all models
    all_models = []
    
    safe_print("\n[1/3] Discovering models from all providers...")
    all_models.extend(discover_gemini_models())
    all_models.extend(discover_groq_models())
    all_models.extend(discover_openrouter_models())
    
    if not all_models:
        safe_print("\n[ERROR] No models discovered! Check API keys.")
        safe_print("  Set: GEMINI_API_KEY, GROQ_API_KEY environment variables")
        return 1
    
    safe_print(f"\n[OK] Total: {len(all_models)} models discovered")
    
    # Categorize
    safe_print("\n[2/3] Categorizing models...")
    categories = categorize_models(all_models)
    for cat, models in categories.items():
        safe_print(f"  {cat}: {len(models)} models")
    
    # Assignments
    safe_print("\n[3/3] Determining workflow step assignments...")
    assignments = get_step_model_assignments(categories)
    
    # Quota pools
    quota_pools = calculate_quota_pools(categories)
    
    # Generate report
    generate_report(all_models, categories, assignments, quota_pools)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
