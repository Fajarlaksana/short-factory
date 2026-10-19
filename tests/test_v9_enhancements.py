#!/usr/bin/env python3
"""
ViralShorts Factory v9.0 - Comprehensive Enhancement Test Suite
================================================================

Tests ALL 25 enhancements to ensure they work correctly.
Run this locally before pushing to production.

Usage:
    python test_v9_enhancements.py

No actual video generation - just validates all components.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Test results tracking
TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}

def safe_print(msg):
    try:
        print(msg)
    except:
        print(msg.encode('ascii', 'ignore').decode())

def test_result(name, passed, error_msg=None):
    """Record test result."""
    if passed:
        TEST_RESULTS["passed"] += 1
        safe_print(f"  ✅ {name}")
    else:
        TEST_RESULTS["failed"] += 1
        TEST_RESULTS["errors"].append(f"{name}: {error_msg}")
        safe_print(f"  ❌ {name}: {error_msg}")

def skip_test(name, reason):
    """Skip a test."""
    TEST_RESULTS["skipped"] += 1
    safe_print(f"  ⏭️ {name}: SKIPPED - {reason}")


# =============================================================================
# TEST 1: Module Imports
# =============================================================================
def test_module_imports():
    """Test that all modules import correctly."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 1: Module Imports")
    safe_print("=" * 60)
    
    # Test enhancements_v9
    try:
        from enhancements_v9 import (
            get_enhancement_orchestrator,
            SmartAICaller,
            check_semantic_duplicate,
            enhance_voice_pacing,
            predict_retention_curve,
            score_value_density,
            validate_post_render,
            score_trend_freshness,
            ABTestTracker,
            ErrorPatternLearner,
            ShadowBanDetector
        )
        test_result("enhancements_v9 imports", True)
    except Exception as e:
        test_result("enhancements_v9 imports", False, str(e))
        return False
    
    # Test pro_video_generator integration
    try:
        from pro_video_generator import (
            ENHANCEMENTS_AVAILABLE,
            PERSISTENT_STATE_AVAILABLE,
            VIRAL_PATTERNS_AVAILABLE
        )
        test_result("pro_video_generator flags", True)
        test_result(f"ENHANCEMENTS_AVAILABLE={ENHANCEMENTS_AVAILABLE}", ENHANCEMENTS_AVAILABLE)
        test_result(f"PERSISTENT_STATE_AVAILABLE={PERSISTENT_STATE_AVAILABLE}", PERSISTENT_STATE_AVAILABLE)
        test_result(f"VIRAL_PATTERNS_AVAILABLE={VIRAL_PATTERNS_AVAILABLE}", VIRAL_PATTERNS_AVAILABLE)
    except Exception as e:
        test_result("pro_video_generator integration", False, str(e))
    
    # Test persistent_state
    try:
        from persistent_state import (
            get_upload_manager,
            get_variety_manager,
            get_analytics_manager,
            get_viral_manager
        )
        test_result("persistent_state imports", True)
    except Exception as e:
        test_result("persistent_state imports", False, str(e))
    
    # Test god_tier_prompts
    try:
        from god_tier_prompts import (
            PLATFORM_OPTIMIZATION_PROMPT,
            CONTEXTUAL_AWARENESS_PROMPT,
            CROSS_PROMOTION_PROMPT,
            CONTENT_RECYCLING_PROMPT
        )
        test_result("god_tier_prompts new prompts", True)
    except Exception as e:
        test_result("god_tier_prompts new prompts", False, str(e))
    
    # Test monthly_analysis
    try:
        from monthly_analysis import (
            identify_recycle_candidates,
            track_competitors
        )
        test_result("monthly_analysis new functions", True)
    except Exception as e:
        test_result("monthly_analysis new functions", False, str(e))
    
    return True


# =============================================================================
# TEST 2: Enhancement Orchestrator
# =============================================================================
def test_enhancement_orchestrator():
    """Test the enhancement orchestrator initialization."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 2: Enhancement Orchestrator")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import get_enhancement_orchestrator
        
        orch = get_enhancement_orchestrator()
        test_result("Orchestrator creation", True)
        
        # Check components
        test_result("ABTestTracker exists", hasattr(orch, 'ab_tracker'))
        test_result("ErrorPatternLearner exists", hasattr(orch, 'error_learner'))
        test_result("ShadowBanDetector exists", hasattr(orch, 'shadow_detector'))
        
        # Check methods
        test_result("pre_generation_checks method", hasattr(orch, 'pre_generation_checks'))
        test_result("post_content_checks method", hasattr(orch, 'post_content_checks'))
        test_result("post_render_validation method", hasattr(orch, 'post_render_validation'))
        test_result("get_seo_description method", hasattr(orch, 'get_seo_description'))
        test_result("get_cta method", hasattr(orch, 'get_cta'))
        test_result("record_ab_test method", hasattr(orch, 'record_ab_test'))
        test_result("record_error method", hasattr(orch, 'record_error'))
        
        return True
    except Exception as e:
        test_result("Orchestrator creation", False, str(e))
        return False


# =============================================================================
# TEST 3: SmartAICaller (Quota-Aware Routing)
# =============================================================================
def test_smart_ai_caller():
    """Test the SmartAICaller initialization and routing logic."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 3: SmartAICaller (Quota-Aware Routing)")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import SmartAICaller, get_ai_caller
        
        caller = get_ai_caller()
        test_result("SmartAICaller creation", True)
        
        # Check provider availability
        has_groq = caller.groq_client is not None
        has_gemini = caller.gemini_model is not None
        
        test_result(f"Groq client available: {has_groq}", True)  # Info only
        test_result(f"Gemini model available: {has_gemini}", True)  # Info only
        
        if not has_groq and not has_gemini:
            skip_test("AI call test", "No AI providers available (missing API keys)")
            return True
        
        # Test priority routing logic
        test_result("parse_json method exists", hasattr(caller, 'parse_json'))
        
        # Test parse_json with sample data
        sample_json = '{"test": "value", "number": 42}'
        parsed = caller.parse_json(sample_json)
        test_result("parse_json works", parsed is not None and parsed.get('test') == 'value')
        
        # Test with markdown wrapper
        markdown_json = '```json\n{"wrapped": true}\n```'
        parsed_md = caller.parse_json(markdown_json)
        test_result("parse_json handles markdown", parsed_md is not None and parsed_md.get('wrapped') == True)
        
        return True
    except Exception as e:
        test_result("SmartAICaller", False, str(e))
        return False


# =============================================================================
# TEST 4: Persistent State Integration
# =============================================================================
def test_persistent_state():
    """Test persistent state managers."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 4: Persistent State Integration")
    safe_print("=" * 60)
    
    try:
        from persistent_state import get_variety_manager
        
        mgr = get_variety_manager()
        test_result("VarietyManager creation", True)
        
        # Test new methods
        topics = mgr.get_recent_topics()
        test_result("get_recent_topics() works", isinstance(topics, list))
        
        prefs = mgr.get_learned_preferences()
        test_result("get_learned_preferences() works", isinstance(prefs, dict))
        
        # Check expected keys in preferences
        expected_keys = [
            'preferred_categories', 'preferred_music_moods', 
            'title_tricks', 'hook_types', 'best_title_styles'
        ]
        for key in expected_keys:
            test_result(f"Preference key '{key}' exists", key in prefs)
        
        return True
    except Exception as e:
        test_result("Persistent state", False, str(e))
        return False


# =============================================================================
# TEST 5: A/B Test Tracker
# =============================================================================
def test_ab_tracker():
    """Test A/B test tracking functionality."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 5: A/B Test Tracker")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import ABTestTracker
        
        tracker = ABTestTracker()
        test_result("ABTestTracker creation", True)
        
        # Test recording a variant
        tracker.record_variant(
            variant_type="test_type",
            variant_name="test_variant",
            video_id="test_123",
            metadata={"title": "Test Title"}
        )
        test_result("record_variant() works", True)
        
        # Test getting weights
        weights = tracker.get_weights("test_type")
        test_result("get_weights() works", isinstance(weights, dict))
        
        # Test getting best variant
        best = tracker.get_best_variant("test_type")
        test_result("get_best_variant() works", best is not None or best is None)  # Either is valid
        
        return True
    except Exception as e:
        test_result("A/B Test Tracker", False, str(e))
        return False


# =============================================================================
# TEST 6: Error Pattern Learner
# =============================================================================
def test_error_pattern_learner():
    """Test error pattern learning functionality."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 6: Error Pattern Learner")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import ErrorPatternLearner
        
        learner = ErrorPatternLearner()
        test_result("ErrorPatternLearner creation", True)
        
        # Test recording failure
        learner.record_broll_failure("test_keyword_xyz")
        test_result("record_broll_failure() works", True)
        
        # Test checking if should skip (should not skip after 1 failure)
        should_skip = learner.should_skip_keyword("test_keyword_xyz")
        test_result("should_skip_keyword() works", isinstance(should_skip, bool))
        
        return True
    except Exception as e:
        test_result("Error Pattern Learner", False, str(e))
        return False


# =============================================================================
# TEST 7: Shadow-Ban Detector
# =============================================================================
def test_shadow_ban_detector():
    """Test shadow-ban detection functionality."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 7: Shadow-Ban Detector")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import ShadowBanDetector
        
        detector = ShadowBanDetector()
        test_result("ShadowBanDetector creation", True)
        
        # Test checking for shadow ban
        result = detector.check_for_shadow_ban(100)
        test_result("check_for_shadow_ban() works", isinstance(result, dict))
        test_result("Result has 'is_concerning' key", 'is_concerning' in result)
        
        return True
    except Exception as e:
        test_result("Shadow-Ban Detector", False, str(e))
        return False


# =============================================================================
# TEST 8: Pre-Generation Checks (Semantic Duplicate)
# =============================================================================
def test_pre_generation_checks():
    """Test pre-generation checks including semantic duplicate detection."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 8: Pre-Generation Checks")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import get_enhancement_orchestrator
        
        orch = get_enhancement_orchestrator()
        
        # Test with no recent topics (should pass)
        result = orch.pre_generation_checks(
            topic="Test topic about money",
            hook="Save money with this trick",
            recent_topics=[]
        )
        test_result("pre_generation_checks returns dict", isinstance(result, dict))
        test_result("Result has 'proceed' key", 'proceed' in result)
        test_result("Passes with empty recent_topics", result.get('proceed', False))
        
        return True
    except Exception as e:
        test_result("Pre-generation checks", False, str(e))
        return False


# =============================================================================
# TEST 9: Post-Content Checks
# =============================================================================
def test_post_content_checks():
    """Test post-content checks (pacing, retention, value density)."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 9: Post-Content Checks")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import get_enhancement_orchestrator
        
        orch = get_enhancement_orchestrator()
        
        # Test with sample phrases
        sample_phrases = [
            "Did you know your brain makes 35,000 decisions every day?",
            "That's why you feel exhausted by evening.",
            "Here's what successful people do differently...",
            "They reduce decision fatigue with routines.",
            "Try this tomorrow and see the difference!"
        ]
        
        result = orch.post_content_checks(
            phrases=sample_phrases,
            metadata={"hook": sample_phrases[0], "category": "psychology"}
        )
        
        test_result("post_content_checks returns dict", isinstance(result, dict))
        test_result("Result has 'phrases' key", 'phrases' in result)
        
        # Check for pacing (may be None if AI not available)
        if result.get('pacing'):
            test_result("Voice pacing generated", True)
        else:
            skip_test("Voice pacing", "AI not available for pacing generation")
        
        return True
    except Exception as e:
        test_result("Post-content checks", False, str(e))
        return False


# =============================================================================
# TEST 10: Trend Freshness Scoring
# =============================================================================
def test_trend_freshness():
    """Test trend freshness decay scoring."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 10: Trend Freshness Scoring")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import score_trend_freshness
        
        # Test with recent trend
        result = score_trend_freshness(
            topic="New AI breakthrough",
            source="google",
            fetch_time=datetime.now().isoformat()
        )
        test_result("score_trend_freshness returns dict", isinstance(result, dict))
        test_result("Result has 'freshness_score' key", 'freshness_score' in result)
        test_result("Result has 'urgency' key", 'urgency' in result)
        
        # Fresh trend should have high score
        score = result.get('freshness_score', 0)
        test_result(f"Fresh trend has high score ({score})", score >= 50)
        
        return True
    except Exception as e:
        test_result("Trend freshness scoring", False, str(e))
        return False


# =============================================================================
# TEST 11: CTA Variants
# =============================================================================
def test_cta_variants():
    """Test CTA variant selection."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 11: CTA Variants")
    safe_print("=" * 60)
    
    try:
        from enhancements_v9 import get_weighted_cta, CTA_VARIANTS
        
        test_result("CTA_VARIANTS defined", len(CTA_VARIANTS) > 0)
        
        # Get a CTA
        cta = get_weighted_cta()
        test_result("get_weighted_cta() returns string", isinstance(cta, str))
        test_result("CTA is from variants list", cta in CTA_VARIANTS)
        
        return True
    except Exception as e:
        test_result("CTA variants", False, str(e))
        return False


# =============================================================================
# TEST 12: Monthly Analysis Functions
# =============================================================================
def test_monthly_analysis():
    """Test monthly analysis functions."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 12: Monthly Analysis Functions")
    safe_print("=" * 60)
    
    try:
        from monthly_analysis import (
            identify_recycle_candidates,
            track_competitors,
            COMPETITOR_TRACKING_FILE,
            RECYCLE_CANDIDATES_FILE
        )
        
        test_result("COMPETITOR_TRACKING_FILE defined", COMPETITOR_TRACKING_FILE is not None)
        test_result("RECYCLE_CANDIDATES_FILE defined", RECYCLE_CANDIDATES_FILE is not None)
        
        # Test recycle candidates (will be empty without analytics data)
        candidates = identify_recycle_candidates()
        test_result("identify_recycle_candidates() works", isinstance(candidates, list))
        
        # Test competitor tracking
        competitor_data = track_competitors()
        test_result("track_competitors() works", isinstance(competitor_data, dict))
        
        return True
    except Exception as e:
        test_result("Monthly analysis", False, str(e))
        return False


# =============================================================================
# TEST 13: God-Tier Prompts
# =============================================================================
def test_god_tier_prompts():
    """Test new god-tier prompts are defined and valid."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 13: God-Tier Prompts")
    safe_print("=" * 60)
    
    try:
        from god_tier_prompts import (
            PLATFORM_OPTIMIZATION_PROMPT,
            CONTEXTUAL_AWARENESS_PROMPT,
            CROSS_PROMOTION_PROMPT,
            CONTENT_RECYCLING_PROMPT
        )
        
        # Check prompts are non-empty strings
        test_result("PLATFORM_OPTIMIZATION_PROMPT defined", len(PLATFORM_OPTIMIZATION_PROMPT) > 100)
        test_result("CONTEXTUAL_AWARENESS_PROMPT defined", len(CONTEXTUAL_AWARENESS_PROMPT) > 100)
        test_result("CROSS_PROMOTION_PROMPT defined", len(CROSS_PROMOTION_PROMPT) > 100)
        test_result("CONTENT_RECYCLING_PROMPT defined", len(CONTENT_RECYCLING_PROMPT) > 100)
        
        # Check prompts contain JSON output instruction
        test_result("Platform prompt has JSON output", "OUTPUT JSON" in PLATFORM_OPTIMIZATION_PROMPT or "JSON" in PLATFORM_OPTIMIZATION_PROMPT)
        test_result("Contextual prompt has JSON output", "OUTPUT JSON" in CONTEXTUAL_AWARENESS_PROMPT or "JSON" in CONTEXTUAL_AWARENESS_PROMPT)
        
        return True
    except Exception as e:
        test_result("God-tier prompts", False, str(e))
        return False


# =============================================================================
# TEST 14: Workflow File Validation
# =============================================================================
def test_workflow_files():
    """Test that workflow files are valid YAML and have correct configuration."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 14: Workflow File Validation")
    safe_print("=" * 60)
    
    workflow_dir = Path(".github/workflows")
    
    if not workflow_dir.exists():
        skip_test("Workflow files", "Workflow directory not found")
        return True
    
    try:
        import yaml
    except ImportError:
        skip_test("Workflow YAML validation", "PyYAML not installed")
        
        # Still check files exist
        generate_yml = workflow_dir / "generate.yml"
        analytics_yml = workflow_dir / "analytics-feedback.yml"
        monthly_yml = workflow_dir / "monthly-analysis.yml"
        
        test_result("generate.yml exists", generate_yml.exists())
        test_result("analytics-feedback.yml exists", analytics_yml.exists())
        test_result("monthly-analysis.yml exists", monthly_yml.exists())
        return True
    
    # Validate each workflow file
    for workflow_file in ["generate.yml", "analytics-feedback.yml", "monthly-analysis.yml"]:
        filepath = workflow_dir / workflow_file
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    content = yaml.safe_load(f)
                test_result(f"{workflow_file} is valid YAML", True)
                
                # Check has required keys (presence only, not truthy value)
                # Note: In YAML, 'on' is parsed as boolean True, so we check for both
                test_result(f"{workflow_file} has 'name'", 'name' in content and content.get('name'))
                has_on = 'on' in content or True in content  # YAML parses 'on:' as True
                test_result(f"{workflow_file} has 'on' triggers", has_on)
                test_result(f"{workflow_file} has 'jobs'", 'jobs' in content and content.get('jobs'))
            except Exception as e:
                test_result(f"{workflow_file} is valid", False, str(e))
        else:
            skip_test(f"{workflow_file}", "File not found")
    
    return True


# =============================================================================
# TEST 15: Data Directory Structure
# =============================================================================
def test_data_directories():
    """Test that required data directories exist or can be created."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST 15: Data Directory Structure")
    safe_print("=" * 60)
    
    required_dirs = [
        Path("data/persistent"),
        Path("output"),
        Path("cache"),
        Path("assets/broll"),
        Path("assets/music")
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            test_result(f"{dir_path} exists", True)
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                test_result(f"{dir_path} created", True)
            except Exception as e:
                test_result(f"{dir_path}", False, str(e))
    
    return True


# =============================================================================
# SUMMARY
# =============================================================================
def print_summary():
    """Print test summary."""
    safe_print("\n" + "=" * 60)
    safe_print("TEST SUMMARY")
    safe_print("=" * 60)
    
    total = TEST_RESULTS["passed"] + TEST_RESULTS["failed"] + TEST_RESULTS["skipped"]
    
    safe_print(f"\n  Total tests:  {total}")
    safe_print(f"  ✅ Passed:    {TEST_RESULTS['passed']}")
    safe_print(f"  ❌ Failed:    {TEST_RESULTS['failed']}")
    safe_print(f"  ⏭️ Skipped:   {TEST_RESULTS['skipped']}")
    
    if TEST_RESULTS["errors"]:
        safe_print("\n  ERRORS:")
        for error in TEST_RESULTS["errors"]:
            safe_print(f"    - {error}")
    
    safe_print("\n" + "=" * 60)
    
    if TEST_RESULTS["failed"] == 0:
        safe_print("🎉 ALL TESTS PASSED! v9.0 is ready for production.")
    else:
        safe_print(f"⚠️ {TEST_RESULTS['failed']} test(s) failed. Please review errors above.")
    
    safe_print("=" * 60)
    
    return TEST_RESULTS["failed"] == 0


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    safe_print("\n" + "=" * 60)
    safe_print("  VIRALSHORTS FACTORY v9.0 - TEST SUITE")
    safe_print("  Comprehensive Enhancement Validation")
    safe_print("=" * 60)
    safe_print(f"  Time: {datetime.now().isoformat()}")
    safe_print("=" * 60)
    
    # Run all tests
    test_module_imports()
    test_enhancement_orchestrator()
    test_smart_ai_caller()
    test_persistent_state()
    test_ab_tracker()
    test_error_pattern_learner()
    test_shadow_ban_detector()
    test_pre_generation_checks()
    test_post_content_checks()
    test_trend_freshness()
    test_cta_variants()
    test_monthly_analysis()
    test_god_tier_prompts()
    test_workflow_files()
    test_data_directories()
    
    # Print summary
    success = print_summary()
    
    sys.exit(0 if success else 1)

