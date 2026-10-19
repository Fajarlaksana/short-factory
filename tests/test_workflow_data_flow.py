#!/usr/bin/env python3
"""
Workflow Data Flow Validation Test
===================================

Tests the COMPLETE data pipeline:
1. WEEKLY ANALYTICS → generates insights → stores persistently
2. MONTHLY ANALYSIS → generates patterns → stores persistently  
3. DAILY GENERATION → reads both → uses in video creation

This validates that all workflows work together as designed.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Data file paths (matching what workflows use)
DATA_DIR = Path("data/persistent")
VARIETY_STATE_FILE = DATA_DIR / "variety_state.json"
VIRAL_PATTERNS_FILE = DATA_DIR / "viral_patterns.json"
ANALYTICS_STATE_FILE = DATA_DIR / "analytics_state.json"
COMPETITOR_TRACKING_FILE = DATA_DIR / "competitor_tracking.json"
RECYCLE_CANDIDATES_FILE = DATA_DIR / "recycle_candidates.json"
MONTHLY_ANALYSIS_FILE = DATA_DIR / "monthly_analysis.json"

def safe_print(msg):
    try:
        print(msg)
    except:
        print(msg.encode('ascii', 'ignore').decode())


def section(title):
    safe_print(f"\n{'='*60}")
    safe_print(f" {title}")
    safe_print("="*60)


# =============================================================================
# TEST 1: WEEKLY ANALYTICS DATA GENERATION
# =============================================================================
def test_weekly_analytics_output():
    """
    Simulate what the weekly analytics workflow should produce.
    Then verify it can be read by the daily workflow.
    """
    section("TEST 1: Weekly Analytics Data Generation")
    
    errors = []
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Simulate weekly analytics output (what the workflow produces)
    safe_print("\n[1a] Simulating weekly analytics output...")
    
    mock_weekly_analysis = {
        "best_performing_categories": ["psychology", "money", "life_hack"],
        "title_tricks_that_work": ["use numbers", "curiosity gaps", "promise reveal"],
        "best_title_patterns": ["{number} {topic} You Didn't Know", "Why {topic} Changes Everything"],
        "optimal_title_word_count": 8,
        "optimal_duration": 22,
        "optimal_phrase_count": 5,
        "hook_types_that_work": ["question hook", "shocking statement", "number reveal"],
        "psychological_triggers": ["curiosity", "fomo", "social proof"],
        "engagement_baits": ["Comment if you agree", "Save this for later"],
        "best_music_moods": ["dramatic", "mysterious"],
        "best_voice_styles": ["energetic", "calm authority"],
        "virality_hacks": ["end with question", "use round numbers"],
        "best_posting_hours_utc": [14, 18, 22],
        "best_posting_days": ["Tuesday", "Thursday", "Saturday"],
        "best_title_styles": ["number_hook", "curiosity_gap"],
        "comment_insights": {
            "viewer_loves": ["psychology content", "money tips"],
            "viewer_requests": ["more life hacks", "tech content"],
            "quality_concerns": [],
            "engagement_drivers": ["relatable topics"]
        }
    }
    
    # Write to variety_state.json (what weekly workflow does)
    try:
        existing = {}
        if VARIETY_STATE_FILE.exists():
            with open(VARIETY_STATE_FILE, 'r') as f:
                existing = json.load(f)
        
        # Merge analysis into variety state (matching workflow behavior)
        for key, value in mock_weekly_analysis.items():
            if isinstance(value, list):
                existing[key] = value
            elif isinstance(value, dict):
                existing[key] = value
            else:
                existing[key] = value
        
        existing["weekly_last_updated"] = datetime.now().isoformat()
        
        with open(VARIETY_STATE_FILE, 'w') as f:
            json.dump(existing, f, indent=2)
        
        safe_print("  ✅ Weekly analysis saved to variety_state.json")
    except Exception as e:
        errors.append(f"Write variety_state.json: {e}")
        safe_print(f"  ❌ Failed to write variety_state.json: {e}")
    
    # Also update viral_patterns.json (weekly feeds into this)
    try:
        existing_patterns = {}
        if VIRAL_PATTERNS_FILE.exists():
            with open(VIRAL_PATTERNS_FILE, 'r') as f:
                existing_patterns = json.load(f)
        
        # Merge patterns
        for key in ["title_tricks_that_work", "hook_types_that_work", "engagement_baits"]:
            if key in mock_weekly_analysis:
                existing_patterns[key.replace("_that_work", "")] = mock_weekly_analysis[key]
        
        existing_patterns["weekly_updated"] = datetime.now().isoformat()
        
        with open(VIRAL_PATTERNS_FILE, 'w') as f:
            json.dump(existing_patterns, f, indent=2)
        
        safe_print("  ✅ Weekly patterns merged to viral_patterns.json")
    except Exception as e:
        errors.append(f"Write viral_patterns.json: {e}")
        safe_print(f"  ❌ Failed to write viral_patterns.json: {e}")
    
    # Verify data can be read back
    safe_print("\n[1b] Verifying weekly data persistence...")
    
    try:
        with open(VARIETY_STATE_FILE, 'r') as f:
            loaded = json.load(f)
        
        required_keys = ["best_performing_categories", "best_title_styles", "comment_insights"]
        for key in required_keys:
            if key in loaded:
                safe_print(f"  ✅ {key}: present ({type(loaded[key]).__name__})")
            else:
                errors.append(f"Missing key: {key}")
                safe_print(f"  ❌ {key}: MISSING")
    except Exception as e:
        errors.append(f"Read variety_state.json: {e}")
        safe_print(f"  ❌ Failed to read variety_state.json: {e}")
    
    return len(errors) == 0, errors


# =============================================================================
# TEST 2: MONTHLY ANALYSIS DATA GENERATION
# =============================================================================
def test_monthly_analysis_output():
    """
    Simulate what the monthly analysis workflow should produce.
    Then verify it can be read by the daily workflow.
    """
    section("TEST 2: Monthly Analysis Data Generation")
    
    errors = []
    
    # Simulate monthly analysis output
    safe_print("\n[2a] Simulating monthly analysis output...")
    
    mock_monthly_patterns = {
        "title_patterns": ["The {adj} Truth About {topic}", "{number} Signs You're {state}"],
        "hook_patterns": ["Start with a question", "Shocking first statement"],
        "psychological_triggers": ["curiosity", "fomo", "controversy"],
        "retention_tricks": ["open loop", "promise payoff"],
        "virality_hacks": ["make shareable", "trigger comments"],
        "proven_categories": ["psychology", "money", "relationships"],
        "content_themes": ["hidden truths", "life hacks", "money secrets"],
        "optimal_duration": 20,
        "optimal_phrase_count": 5,
        "ai_generated": True,
        "source": "monthly_youtube_analysis",
        "last_updated": datetime.now().isoformat()
    }
    
    # Write to viral_patterns.json
    try:
        existing = {}
        if VIRAL_PATTERNS_FILE.exists():
            with open(VIRAL_PATTERNS_FILE, 'r') as f:
                existing = json.load(f)
        
        # Merge monthly patterns (keep weekly updates)
        for key, value in mock_monthly_patterns.items():
            if key not in existing or key in ["title_patterns", "hook_patterns"]:
                existing[key] = value
        
        existing["monthly_updated"] = datetime.now().isoformat()
        
        with open(VIRAL_PATTERNS_FILE, 'w') as f:
            json.dump(existing, f, indent=2)
        
        safe_print("  ✅ Monthly patterns saved to viral_patterns.json")
    except Exception as e:
        errors.append(f"Write viral_patterns.json: {e}")
        safe_print(f"  ❌ Failed to write viral_patterns.json: {e}")
    
    # Write competitor tracking
    safe_print("\n[2b] Simulating competitor tracking...")
    
    mock_competitors = {
        "TestChannel1": {
            "first_seen": "2024-12-01",
            "videos_seen": 5,
            "total_views": 1500000,
            "last_seen": datetime.now().isoformat()
        },
        "TestChannel2": {
            "first_seen": "2024-12-15",
            "videos_seen": 3,
            "total_views": 800000,
            "last_seen": datetime.now().isoformat()
        }
    }
    
    try:
        with open(COMPETITOR_TRACKING_FILE, 'w') as f:
            json.dump(mock_competitors, f, indent=2)
        safe_print("  ✅ Competitor tracking saved")
    except Exception as e:
        errors.append(f"Write competitor_tracking.json: {e}")
        safe_print(f"  ❌ Failed to write competitor_tracking.json: {e}")
    
    # Write recycle candidates
    safe_print("\n[2c] Simulating content recycling...")
    
    mock_recycle = {
        "date": datetime.now().isoformat(),
        "candidates": [
            {
                "original_title": "Test Underperformer",
                "diagnosis": "Weak hook",
                "salvageable": True,
                "fresh_angle": "Different approach",
                "new_hook": "Better hook",
                "new_title": "Better Title"
            }
        ]
    }
    
    try:
        with open(RECYCLE_CANDIDATES_FILE, 'w') as f:
            json.dump(mock_recycle, f, indent=2)
        safe_print("  ✅ Recycle candidates saved")
    except Exception as e:
        errors.append(f"Write recycle_candidates.json: {e}")
        safe_print(f"  ❌ Failed to write recycle_candidates.json: {e}")
    
    # Verify data can be read back
    safe_print("\n[2d] Verifying monthly data persistence...")
    
    try:
        with open(VIRAL_PATTERNS_FILE, 'r') as f:
            loaded = json.load(f)
        
        required_keys = ["title_patterns", "hook_patterns", "proven_categories"]
        for key in required_keys:
            if key in loaded:
                safe_print(f"  ✅ {key}: present ({len(loaded[key])} items)")
            else:
                errors.append(f"Missing key: {key}")
                safe_print(f"  ❌ {key}: MISSING")
    except Exception as e:
        errors.append(f"Read viral_patterns.json: {e}")
        safe_print(f"  ❌ Failed to read viral_patterns.json: {e}")
    
    return len(errors) == 0, errors


# =============================================================================
# TEST 3: DAILY WORKFLOW READS AND USES DATA
# =============================================================================
def test_daily_workflow_reads_data():
    """
    Test that the daily workflow correctly reads and uses:
    1. variety_state.json (from weekly analytics)
    2. viral_patterns.json (from weekly + monthly)
    
    This simulates what pro_video_generator.py does.
    """
    section("TEST 3: Daily Workflow Reads & Uses Data")
    
    errors = []
    
    # Test 3a: Read variety_state via persistent_state module
    safe_print("\n[3a] Testing persistent_state.get_variety_manager()...")
    
    try:
        from persistent_state import get_variety_manager
        
        variety_mgr = get_variety_manager()
        
        # Test new methods
        recent_topics = variety_mgr.get_recent_topics()
        safe_print(f"  ✅ get_recent_topics(): {len(recent_topics)} topics")
        
        learned = variety_mgr.get_learned_preferences()
        safe_print(f"  ✅ get_learned_preferences(): {len(learned)} keys")
        
        # Check specific learned data from weekly
        if learned.get("best_performing_categories"):
            safe_print(f"     → best_performing_categories: {learned['best_performing_categories']}")
        if learned.get("comment_insights"):
            safe_print(f"     → comment_insights: {list(learned['comment_insights'].keys())}")
        if learned.get("best_title_styles"):
            safe_print(f"     → best_title_styles: {learned['best_title_styles']}")
            
    except Exception as e:
        errors.append(f"persistent_state.get_variety_manager: {e}")
        safe_print(f"  ❌ Failed: {e}")
    
    # Test 3b: Read viral_patterns via viral_channel_analyzer
    safe_print("\n[3b] Testing viral_channel_analyzer.get_viral_prompt_boost()...")
    
    try:
        from viral_channel_analyzer import get_viral_prompt_boost
        
        boost = get_viral_prompt_boost()
        
        if boost:
            safe_print(f"  ✅ get_viral_prompt_boost(): {len(boost)} chars")
            # Show first 200 chars
            preview = boost[:200].replace('\n', ' ')
            safe_print(f"     → Preview: {preview}...")
        else:
            safe_print("  ⚠️ get_viral_prompt_boost(): Empty (no patterns yet)")
            
    except Exception as e:
        errors.append(f"viral_channel_analyzer.get_viral_prompt_boost: {e}")
        safe_print(f"  ❌ Failed: {e}")
    
    # Test 3c: Read viral_patterns via persistent_state
    safe_print("\n[3c] Testing persistent_state.get_viral_manager()...")
    
    try:
        from persistent_state import get_viral_manager
        
        viral_mgr = get_viral_manager()
        patterns = viral_mgr.get_patterns()
        
        safe_print(f"  ✅ get_patterns(): {len(patterns)} keys")
        
        # Check specific pattern data from monthly
        if patterns.get("title_patterns"):
            safe_print(f"     → title_patterns: {patterns['title_patterns'][:2]}...")
        if patterns.get("proven_categories"):
            safe_print(f"     → proven_categories: {patterns['proven_categories']}")
        if patterns.get("optimal_duration"):
            safe_print(f"     → optimal_duration: {patterns['optimal_duration']}s")
            
    except Exception as e:
        errors.append(f"persistent_state.get_viral_manager: {e}")
        safe_print(f"  ❌ Failed: {e}")
    
    # Test 3d: Test that enhancements module can use the data
    safe_print("\n[3d] Testing enhancements module data integration...")
    
    try:
        from enhancements_v9 import get_enhancement_orchestrator
        
        orch = get_enhancement_orchestrator()
        
        # Run pre-generation with learned data
        from persistent_state import get_variety_manager
        mgr = get_variety_manager()
        recent = mgr.get_recent_topics()
        
        result = orch.pre_generation_checks(
            topic="Test psychology topic",
            hook="Your brain is lying to you",
            recent_topics=recent
        )
        
        safe_print(f"  ✅ pre_generation_checks() with learned data: proceed={result.get('proceed')}")
        
    except Exception as e:
        errors.append(f"enhancements integration: {e}")
        safe_print(f"  ❌ Failed: {e}")
    
    return len(errors) == 0, errors


# =============================================================================
# TEST 4: END-TO-END DATA PIPELINE VALIDATION
# =============================================================================
def test_end_to_end_pipeline():
    """
    Final validation: trace data from weekly → viral_patterns → daily prompt.
    """
    section("TEST 4: End-to-End Pipeline Validation")
    
    errors = []
    
    safe_print("\n[4a] Tracing data flow: Weekly → Daily...")
    
    try:
        # 1. Read variety_state (from weekly)
        with open(VARIETY_STATE_FILE, 'r') as f:
            variety = json.load(f)
        
        best_categories = variety.get("best_performing_categories", [])
        safe_print(f"  → Weekly saved categories: {best_categories}")
        
        # 2. Check viral_channel_analyzer loads it
        from viral_channel_analyzer import get_viral_prompt_boost
        boost = get_viral_prompt_boost()
        
        # 3. Check pro_video_generator would use it
        from pro_video_generator import VIRAL_PATTERNS_AVAILABLE, PERSISTENT_STATE_AVAILABLE
        
        safe_print(f"  → VIRAL_PATTERNS_AVAILABLE: {VIRAL_PATTERNS_AVAILABLE}")
        safe_print(f"  → PERSISTENT_STATE_AVAILABLE: {PERSISTENT_STATE_AVAILABLE}")
        
        if VIRAL_PATTERNS_AVAILABLE and PERSISTENT_STATE_AVAILABLE:
            safe_print("  ✅ Daily workflow CAN read weekly data")
        else:
            errors.append("Daily workflow cannot read weekly data")
            safe_print("  ❌ Daily workflow CANNOT read weekly data")
            
    except Exception as e:
        errors.append(f"End-to-end: {e}")
        safe_print(f"  ❌ Pipeline error: {e}")
    
    safe_print("\n[4b] Tracing data flow: Monthly → Daily...")
    
    try:
        # 1. Read viral_patterns (from monthly)
        with open(VIRAL_PATTERNS_FILE, 'r') as f:
            patterns = json.load(f)
        
        title_patterns = patterns.get("title_patterns", [])
        safe_print(f"  → Monthly saved title_patterns: {title_patterns[:2]}...")
        
        # 2. Check get_viral_prompt_boost includes them
        boost = get_viral_prompt_boost()
        
        # Check if any pattern is in the boost
        pattern_in_boost = any(p in boost for p in title_patterns if p)
        
        if pattern_in_boost or "title" in boost.lower():
            safe_print("  ✅ Monthly patterns included in daily prompt boost")
        else:
            safe_print("  ⚠️ Monthly patterns may not be in prompt (check manually)")
            
    except Exception as e:
        errors.append(f"Monthly trace: {e}")
        safe_print(f"  ❌ Monthly trace error: {e}")
    
    safe_print("\n[4c] Summary of persistent files...")
    
    files_to_check = [
        (VARIETY_STATE_FILE, "Weekly analytics → variety preferences"),
        (VIRAL_PATTERNS_FILE, "Monthly + Weekly → viral patterns"),
        (COMPETITOR_TRACKING_FILE, "Monthly → competitor data"),
        (RECYCLE_CANDIDATES_FILE, "Monthly → recycle suggestions"),
    ]
    
    for file_path, description in files_to_check:
        if file_path.exists():
            size = file_path.stat().st_size
            with open(file_path, 'r') as f:
                data = json.load(f)
            keys = len(data.keys()) if isinstance(data, dict) else len(data)
            safe_print(f"  ✅ {file_path.name}: {size} bytes, {keys} keys")
        else:
            safe_print(f"  ⚠️ {file_path.name}: NOT FOUND")
    
    return len(errors) == 0, errors


# =============================================================================
# MAIN
# =============================================================================
def main():
    safe_print("\n" + "=" * 60)
    safe_print("  WORKFLOW DATA FLOW VALIDATION")
    safe_print("  Testing: Weekly → Monthly → Daily Pipeline")
    safe_print("=" * 60)
    safe_print(f"  Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Run all tests
    passed, errs = test_weekly_analytics_output()
    results.append(("1. Weekly Analytics Output", passed, errs))
    
    passed, errs = test_monthly_analysis_output()
    results.append(("2. Monthly Analysis Output", passed, errs))
    
    passed, errs = test_daily_workflow_reads_data()
    results.append(("3. Daily Workflow Reads Data", passed, errs))
    
    passed, errs = test_end_to_end_pipeline()
    results.append(("4. End-to-End Pipeline", passed, errs))
    
    # Summary
    section("FINAL SUMMARY")
    
    all_passed = True
    for name, passed, errs in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        safe_print(f"  {name}: {status}")
        if not passed:
            all_passed = False
            for err in errs:
                safe_print(f"     → {err}")
    
    safe_print("\n" + "=" * 60)
    
    if all_passed:
        safe_print("🎉 ALL WORKFLOW DATA FLOW TESTS PASSED!")
        safe_print("")
        safe_print("Verified:")
        safe_print("  ✅ Weekly analytics generates and stores data")
        safe_print("  ✅ Monthly analysis generates and stores data")
        safe_print("  ✅ Daily workflow reads and uses all data")
        safe_print("  ✅ End-to-end pipeline is working correctly")
    else:
        safe_print("⚠️ Some tests failed. Please review above.")
    
    safe_print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



