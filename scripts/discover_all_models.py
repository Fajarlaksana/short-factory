#!/usr/bin/env python3
"""
Comprehensive Model Discovery & Categorization Script
=====================================================

Discovers ALL available models from ALL providers and shows:
1. Model quotas and rate limits
2. Categorization (production high/low throughput, backup, bonus)
3. What model is assigned to what task
4. Available bonus quota for aggressive mode

Run locally to review the model selection system.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def safe_print(msg: str):
    """Print with encoding fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())


def discover_models():
    """Run comprehensive model discovery."""
    safe_print("\n" + "=" * 70)
    safe_print("  COMPREHENSIVE MODEL DISCOVERY")
    safe_print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    safe_print("=" * 70)
    
    # Check API keys
    keys = {
        "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
        "GROQ_API_KEY": bool(os.environ.get("GROQ_API_KEY")),
        "OPENROUTER_API_KEY": bool(os.environ.get("OPENROUTER_API_KEY")),
    }
    
    safe_print("\n  API Keys:")
    for key, available in keys.items():
        status = "[OK]" if available else "[X]"
        safe_print(f"    {status} {key}")
    
    # Import model helper
    try:
        from src.ai.model_helper import (
            get_dynamic_gemini_model,
            get_dynamic_groq_model,
            get_all_models,
            get_model_quality_score,
            get_model_rate_limit,
            MODEL_RATE_LIMITS,
            _discover_gemini_models,
            _discover_groq_models,
            _is_model_usable,
        )
        safe_print("\n  [OK] Model helper imported successfully")
    except ImportError as e:
        safe_print(f"\n  [ERROR] Failed to import model helper: {e}")
        return
    
    # =========================================================================
    # GEMINI MODELS
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  GEMINI MODELS")
    safe_print("-" * 70)
    
    gemini_models = _discover_gemini_models()
    safe_print(f"\n  Found {len(gemini_models)} Gemini models:")
    
    gemini_data = []
    for model in gemini_models[:10]:  # Top 10
        is_usable, quota = _is_model_usable(model, "gemini")
        score = get_model_quality_score(model)
        rate_info = get_model_rate_limit(model, "gemini")
        
        gemini_data.append({
            "model": model,
            "quota": quota,
            "score": score,
            "rate_limit": rate_info.get("req_per_min", "?"),
            "delay": rate_info.get("delay", "?"),
            "throughput": rate_info.get("throughput", "unknown"),
        })
        
        safe_print(f"\n    {model}")
        safe_print(f"      Quota: {quota}/day | Rate: {rate_info.get('req_per_min', '?')}/min")
        safe_print(f"      Quality: {score} | Throughput: {rate_info.get('throughput', 'unknown')}")
        safe_print(f"      Delay: {rate_info.get('delay', '?')}s between calls")
    
    # =========================================================================
    # GROQ MODELS
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  GROQ MODELS")
    safe_print("-" * 70)
    
    groq_models = _discover_groq_models()
    safe_print(f"\n  Found {len(groq_models)} Groq models:")
    
    groq_data = []
    for model in groq_models[:10]:
        score = get_model_quality_score(model)
        rate_info = get_model_rate_limit(model, "groq")
        
        groq_data.append({
            "model": model,
            "score": score,
            "rate_limit": rate_info.get("req_per_min", 30),
            "throughput": rate_info.get("throughput", "high"),
        })
        
        safe_print(f"\n    {model}")
        safe_print(f"      Quality: {score} | Rate: {rate_info.get('req_per_min', 30)}/min")
        safe_print(f"      Throughput: {rate_info.get('throughput', 'high')}")
    
    # =========================================================================
    # MODEL CATEGORIZATION
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  MODEL CATEGORIZATION")
    safe_print("-" * 70)
    
    # Categorize by throughput
    high_throughput = []
    low_throughput = []
    backup = []
    bonus = []
    
    for data in gemini_data:
        if data["throughput"] == "high":
            high_throughput.append(f"gemini:{data['model']}")
        elif data["throughput"] in ["medium", "low"]:
            if data["score"] >= 7.0:
                low_throughput.append(f"gemini:{data['model']}")
            else:
                backup.append(f"gemini:{data['model']}")
    
    for data in groq_data:
        if data["throughput"] == "high":
            high_throughput.append(f"groq:{data['model']}")
        else:
            backup.append(f"groq:{data['model']}")
    
    safe_print(f"\n  PRODUCTION - High Throughput ({len(high_throughput)}):")
    for m in high_throughput[:5]:
        safe_print(f"    - {m}")
    
    safe_print(f"\n  PRODUCTION - Low Throughput ({len(low_throughput)}):")
    for m in low_throughput[:5]:
        safe_print(f"    - {m}")
    
    safe_print(f"\n  BACKUP ({len(backup)}):")
    for m in backup[:5]:
        safe_print(f"    - {m}")
    
    # =========================================================================
    # TASK ASSIGNMENTS
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  TASK ASSIGNMENTS (What model for what)")
    safe_print("-" * 70)
    
    assignments = {
        "CRITICAL TASKS (need quality, use low-throughput high-quality)": [
            "hook_generation",
            "quality_evaluation",
            "god_tier_scoring",
            "title_optimization",
        ],
        "BULK TASKS (need speed, use high-throughput)": [
            "topic_suggestion",
            "description_generation",
            "script_generation",
            "hashtag_generation",
        ],
        "ANALYTICS (use bonus quota in aggressive mode)": [
            "virality_analysis",
            "self_learning",
            "competitor_analysis",
        ],
    }
    
    for category, tasks in assignments.items():
        safe_print(f"\n  {category}:")
        for task in tasks:
            if "CRITICAL" in category:
                model = low_throughput[0] if low_throughput else high_throughput[0] if high_throughput else "N/A"
            elif "BULK" in category:
                model = high_throughput[0] if high_throughput else low_throughput[0] if low_throughput else "N/A"
            else:
                model = backup[0] if backup else "N/A"
            safe_print(f"    {task}: {model}")
    
    # =========================================================================
    # QUOTA BUDGET
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  DAILY QUOTA BUDGET")
    safe_print("-" * 70)
    
    # Calculate totals
    total_gemini_quota = sum(d["quota"] for d in gemini_data)
    
    safe_print(f"\n  AVAILABLE:")
    safe_print(f"    Gemini: ~{total_gemini_quota}/day across {len(gemini_data)} models")
    safe_print(f"    Groq: ~500/day (shared token pool)")
    safe_print(f"    OpenRouter: ~1000/day (free models)")
    
    production_needs = 6 * 15  # 6 videos * 15 calls
    analytics_needs = 20
    total_needs = production_needs + analytics_needs
    
    safe_print(f"\n  PRODUCTION NEEDS (6 videos/day):")
    safe_print(f"    Video generation: {production_needs} calls")
    safe_print(f"    Analytics: {analytics_needs} calls")
    safe_print(f"    TOTAL: {total_needs} calls")
    
    free_quota = total_gemini_quota - total_needs
    safe_print(f"\n  FREE FOR AGGRESSIVE MODE: {max(0, free_quota)} calls")
    
    if free_quota > 100:
        safe_print(f"\n  [OK] AGGRESSIVE MODE VIABLE!")
    else:
        safe_print(f"\n  [!] Limited bonus quota")
    
    # =========================================================================
    # RATE LIMITS TABLE
    # =========================================================================
    safe_print("\n" + "-" * 70)
    safe_print("  KNOWN RATE LIMITS (from MODEL_RATE_LIMITS)")
    safe_print("-" * 70)
    
    safe_print(f"\n  {'Model':<30} {'Req/min':<10} {'Delay':<10} {'Throughput':<12}")
    safe_print("  " + "-" * 62)
    for model, info in MODEL_RATE_LIMITS.items():
        if model.startswith("_"):
            continue
        safe_print(f"  {model:<30} {info['req_per_min']:<10} {info['delay']:<10.1f} {info['throughput']:<12}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "gemini_models": gemini_data,
        "groq_models": groq_data,
        "categories": {
            "high_throughput": high_throughput,
            "low_throughput": low_throughput,
            "backup": backup,
        },
        "quota_budget": {
            "total_available": total_gemini_quota,
            "production_needs": total_needs,
            "free_for_aggressive": max(0, free_quota),
        }
    }
    
    report_path = project_root / "data" / "persistent" / "model_discovery_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    safe_print(f"\n  Report saved to: {report_path}")
    safe_print("\n" + "=" * 70)
    safe_print("  DISCOVERY COMPLETE")
    safe_print("=" * 70)
    
    return report


if __name__ == "__main__":
    discover_models()
