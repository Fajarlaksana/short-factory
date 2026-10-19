#!/usr/bin/env python3
"""
Comprehensive AI-First Architecture Tests
==========================================

Tests all components to ensure they follow AI-first principles:
1. No hardcoded patterns
2. AI fallback is minimal and labeled
3. All data sources are from AI or analytics
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src/utils')
sys.path.insert(0, 'src/analytics')
sys.path.insert(0, 'src/enhancements')

PASSED = 0
FAILED = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASSED, FAILED
    if condition:
        print(f"[PASS] {name}")
        PASSED += 1
    else:
        print(f"[FAIL] {name} - {detail}")
        FAILED += 1
    return condition


def main():
    global PASSED, FAILED
    
    print("=" * 60)
    print("AI-FIRST ARCHITECTURE COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: viral_patterns.json structure
    print("\n[1] Testing viral_patterns.json...")
    try:
        with open("data/persistent/viral_patterns.json", 'r') as f:
            vp = json.load(f)
        test("viral_patterns.json has source field", 
             vp.get("patterns_source") is not None,
             "Missing patterns_source")
        test("viral_patterns.json is not hardcoded", 
             vp.get("patterns_source") in ["AI_GENERATED", "NEEDS_AI_GENERATION", None],
             f"Unexpected source: {vp.get('patterns_source')}")
    except Exception as e:
        test("viral_patterns.json readable", False, str(e))
    
    # Test 2: variety_state.json structure
    print("\n[2] Testing variety_state.json...")
    try:
        with open("data/persistent/variety_state.json", 'r') as f:
            vs = json.load(f)
        test("variety_state.json has source field", 
             vs.get("source") is not None,
             "Missing source")
        test("variety_state.json is analytics-based", 
             vs.get("source") == "ANALYTICS_LEARNED",
             f"Unexpected source: {vs.get('source')}")
    except Exception as e:
        test("variety_state.json readable", False, str(e))
    
    # Test 3: self_learning.json structure
    print("\n[3] Testing self_learning.json...")
    try:
        with open("data/persistent/self_learning.json", 'r') as f:
            sl = json.load(f)
        test("self_learning.json has source field", 
             sl.get("source") is not None,
             "Missing source")
        test("self_learning.json is real-analytics-only", 
             sl.get("source") == "REAL_ANALYTICS" or sl.get("awaiting_real_data"),
             f"Unexpected source: {sl.get('source')}")
        test("self_learning.json has no seeded data", 
             sl.get("stats", {}).get("total_videos", 0) == 0 or sl.get("awaiting_real_data"),
             "Appears to have seeded data")
    except Exception as e:
        test("self_learning.json readable", False, str(e))
    
    # Test 4: AI Pattern Generator
    print("\n[4] Testing AI Pattern Generator...")
    try:
        from ai_pattern_generator import get_pattern_generator, AIPatternGenerator
        gen = get_pattern_generator()
        test("AIPatternGenerator importable", True)
        test("AIPatternGenerator has generate_patterns_with_ai", 
             hasattr(gen, 'generate_patterns_with_ai'),
             "Missing method")
        test("AIPatternGenerator has get_patterns", 
             hasattr(gen, 'get_patterns'),
             "Missing method")
        test("AIPatternGenerator needs_refresh works", 
             isinstance(gen.needs_refresh(), bool),
             "needs_refresh not working")
    except Exception as e:
        test("AIPatternGenerator works", False, str(e))
    
    # Test 5: VarietyStateManager uses AI
    print("\n[5] Testing VarietyStateManager...")
    try:
        from persistent_state import get_variety_manager
        vm = get_variety_manager()
        test("VarietyStateManager importable", True)
        test("VarietyStateManager has _get_ai_categories", 
             hasattr(vm, '_get_ai_categories'),
             "Missing _get_ai_categories method")
        cats = vm._get_ai_categories()
        test("_get_ai_categories returns list", 
             isinstance(cats, list),
             f"Got {type(cats)}")
    except Exception as e:
        test("VarietyStateManager works", False, str(e))
    
    # Test 6: SelfLearningEngine
    print("\n[6] Testing SelfLearningEngine...")
    try:
        from self_learning_engine import SelfLearningEngine
        engine = SelfLearningEngine()
        test("SelfLearningEngine importable", True)
        test("SelfLearningEngine has empty default", 
             engine.data.get("source") == "REAL_ANALYTICS" or 
             engine.data.get("stats", {}).get("total_videos", 0) == 0,
             "Has seeded data")
    except Exception as e:
        test("SelfLearningEngine works", False, str(e))
    
    # Test 7: Verification script
    print("\n[7] Testing Verification Script...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/version_verification.py"],
            capture_output=True, text=True, timeout=60
        )
        test("Verification script runs", result.returncode == 0, 
             "Exit code: " + str(result.returncode))
        test("Verification passes", "PASSED" in result.stdout, 
             "Did not pass")
    except Exception as e:
        test("Verification script works", False, str(e))
    
    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {PASSED} passed, {FAILED} failed")
    print("=" * 60)
    
    if FAILED > 0:
        print("[OVERALL] SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("[OVERALL] ALL TESTS PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()

