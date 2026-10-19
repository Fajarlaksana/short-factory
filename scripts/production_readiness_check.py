#!/usr/bin/env python3
"""
ViralShorts Factory - Production Readiness Check v15.0
=========================================================

This script checks ALL requirements for production deployment:
1. Environment variables / API keys
2. v15.0 system health
3. Quota availability
4. Learning engine state
5. File structure
6. Dependencies

Run this before deploying to ensure everything works!
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def safe_print(text):
    """Print safely regardless of encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))


def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check required environment variables."""
    issues = []
    
    required = {
        "GROQ_API_KEY": "Groq AI (primary LLM)",
        "GEMINI_API_KEY": "Google Gemini (fallback LLM)",
        "PEXELS_API_KEY": "Pexels (B-roll videos)",
    }
    
    optional = {
        "OPENROUTER_API_KEY": "OpenRouter (backup LLM - RECOMMENDED)",
        "YOUTUBE_CLIENT_ID": "YouTube OAuth",
        "YOUTUBE_CLIENT_SECRET": "YouTube OAuth",
        "YOUTUBE_REFRESH_TOKEN": "YouTube OAuth",
        "DAILYMOTION_API_KEY": "Dailymotion upload",
        "REDDIT_CLIENT_ID": "Reddit trends",
        "REDDIT_CLIENT_SECRET": "Reddit trends",
    }
    
    safe_print("\nEnvironment Variables:")
    safe_print("-" * 60)
    
    all_required_present = True
    for key, desc in required.items():
        value = os.environ.get(key)
        if value:
            safe_print(f"  [OK] {key} - {desc}")
        else:
            safe_print(f"  [MISSING] {key} - {desc} (REQUIRED)")
            issues.append(f"Missing required: {key}")
            all_required_present = False
    
    for key, desc in optional.items():
        value = os.environ.get(key)
        if value:
            safe_print(f"  [OK] {key} - {desc}")
        else:
            safe_print(f"  [WARN] {key} - {desc} (optional)")
    
    return all_required_present, issues


def check_v15_systems() -> Tuple[bool, List[str]]:
    """Check v15.0 systems."""
    issues = []
    all_ok = True
    
    safe_print("\nv15.0 Systems:")
    safe_print("-" * 60)
    
    # Token Budget Manager
    try:
        from token_budget_manager import get_budget_manager
        budget = get_budget_manager()
        videos = budget.estimate_videos_remaining()
        safe_print(f"  [OK] Token Budget Manager - {videos} videos remaining")
    except Exception as e:
        safe_print(f"  [FAIL] Token Budget Manager - {e}")
        issues.append(f"Token Budget Manager failed: {e}")
        all_ok = False
    
    # Self-Learning Engine
    try:
        from self_learning_engine import get_learning_engine
        engine = get_learning_engine()
        count = engine.data['stats']['total_videos']
        safe_print(f"  [OK] Self-Learning Engine - {count} videos analyzed")
    except Exception as e:
        safe_print(f"  [FAIL] Self-Learning Engine - {e}")
        issues.append(f"Self-Learning Engine failed: {e}")
        all_ok = False
    
    # Quota Monitor
    try:
        from quota_monitor import get_quota_monitor
        monitor = get_quota_monitor()
        rec = monitor.get_scheduling_recommendation()
        safe_print(f"  [OK] Quota Monitor - {rec['best_provider']} available")
    except Exception as e:
        safe_print(f"  [FAIL] Quota Monitor - {e}")
        issues.append(f"Quota Monitor failed: {e}")
        all_ok = False
    
    # Performance Dashboard
    try:
        from performance_dashboard import get_dashboard
        dashboard = get_dashboard()
        safe_print(f"  [OK] Performance Dashboard")
    except Exception as e:
        safe_print(f"  [FAIL] Performance Dashboard - {e}")
        issues.append(f"Performance Dashboard failed: {e}")
        all_ok = False
    
    return all_ok, issues


def check_quota_availability() -> Tuple[bool, List[str]]:
    """Check if we can generate videos now."""
    issues = []
    
    safe_print("\nQuota Availability:")
    safe_print("-" * 60)
    
    try:
        from quota_monitor import get_quota_monitor
        monitor = get_quota_monitor()
        rec = monitor.get_scheduling_recommendation()
        
        if rec['can_run_now']:
            safe_print(f"  [OK] Can generate now - {rec['videos_possible']} videos possible")
            safe_print(f"  [OK] Best provider: {rec['best_provider']}")
            return True, []
        else:
            safe_print(f"  [WARN] Cannot generate now - {rec['reason']}")
            if rec['recommended_wait'] > 0:
                mins = rec['recommended_wait'] // 60
                safe_print(f"  [INFO] Wait time: {mins} minutes")
            issues.append(f"Cannot generate: {rec['reason']}")
            return False, issues
    except Exception as e:
        safe_print(f"  [FAIL] Could not check quota: {e}")
        return False, [str(e)]


def check_file_structure() -> Tuple[bool, List[str]]:
    """Check required files and directories."""
    issues = []
    
    safe_print("\nFile Structure:")
    safe_print("-" * 60)
    
    required_files = [
        "pro_video_generator.py",
        "god_tier_prompts.py",
        "enhancements_v9.py",
        "enhancements_v12.py",
        "token_budget_manager.py",
        "self_learning_engine.py",
        "quota_monitor.py",
        "requirements.txt",
    ]
    
    required_dirs = [
        "data",
        "data/persistent",
        ".github/workflows",
    ]
    
    all_ok = True
    
    for f in required_files:
        if Path(f).exists():
            safe_print(f"  [OK] {f}")
        else:
            safe_print(f"  [MISSING] {f}")
            issues.append(f"Missing file: {f}")
            all_ok = False
    
    for d in required_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        safe_print(f"  [OK] {d}/")
    
    return all_ok, issues


def check_dependencies() -> Tuple[bool, List[str]]:
    """Check Python dependencies."""
    issues = []
    
    safe_print("\nPython Dependencies:")
    safe_print("-" * 60)
    
    required_modules = [
        ("moviepy", "Video editing"),
        ("PIL", "Image processing"),
        ("edge_tts", "Text-to-speech"),
        ("groq", "Groq API"),
        ("google.generativeai", "Gemini API"),
        ("requests", "HTTP client"),
        ("numpy", "Numerical operations"),
    ]
    
    all_ok = True
    
    for module, desc in required_modules:
        try:
            __import__(module)
            safe_print(f"  [OK] {module} - {desc}")
        except ImportError:
            safe_print(f"  [MISSING] {module} - {desc}")
            issues.append(f"Missing module: {module}")
            all_ok = False
    
    return all_ok, issues


def run_full_check() -> bool:
    """Run all checks and return overall status."""
    safe_print("\n" + "=" * 70)
    safe_print("   VIRALSHORTS FACTORY - PRODUCTION READINESS CHECK")
    safe_print("=" * 70)
    
    all_issues = []
    
    # Run all checks
    env_ok, env_issues = check_environment_variables()
    all_issues.extend(env_issues)
    
    v15_ok, v15_issues = check_v15_systems()
    all_issues.extend(v15_issues)
    
    quota_ok, quota_issues = check_quota_availability()
    all_issues.extend(quota_issues)
    
    files_ok, file_issues = check_file_structure()
    all_issues.extend(file_issues)
    
    deps_ok, dep_issues = check_dependencies()
    all_issues.extend(dep_issues)
    
    # Summary
    safe_print("\n" + "=" * 70)
    safe_print("   SUMMARY")
    safe_print("=" * 70)
    
    if all_issues:
        safe_print(f"\nIssues Found ({len(all_issues)}):")
        for issue in all_issues:
            safe_print(f"  - {issue}")
        
        # Check if we can still proceed
        critical = [i for i in all_issues if "REQUIRED" in i or "failed" in i.lower()]
        if critical:
            safe_print("\n[FAIL] Critical issues prevent production deployment")
            return False
        else:
            safe_print("\n[WARN] Non-critical issues found, can proceed with caution")
            return True
    else:
        safe_print("\n[OK] All checks passed!")
        safe_print("[OK] Ready for production deployment!")
        return True


if __name__ == "__main__":
    success = run_full_check()
    sys.exit(0 if success else 1)




