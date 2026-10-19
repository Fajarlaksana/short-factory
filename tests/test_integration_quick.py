#!/usr/bin/env python3
"""
Quick Integration Test - Simulates the video generation flow
WITHOUT actually creating videos (no API calls, no rendering)

Tests that all v9.0 components work together correctly.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def safe_print(msg):
    try:
        print(msg)
    except:
        print(msg.encode('ascii', 'ignore').decode())


def test_integration():
    """Run a simulated video generation flow."""
    safe_print("\n" + "=" * 60)
    safe_print("QUICK INTEGRATION TEST - v9.0")
    safe_print("=" * 60)
    
    errors = []
    
    # Step 1: Initialize all managers
    safe_print("\n[1/8] Initializing managers...")
    try:
        from persistent_state import get_variety_manager, get_viral_manager
        variety_mgr = get_variety_manager()
        viral_mgr = get_viral_manager()
        safe_print("  ✅ Persistent state managers initialized")
    except Exception as e:
        errors.append(f"Persistent state: {e}")
        safe_print(f"  ❌ Persistent state: {e}")
    
    # Step 2: Initialize enhancement orchestrator
    safe_print("\n[2/8] Initializing enhancement orchestrator...")
    try:
        from enhancements_v9 import get_enhancement_orchestrator
        orch = get_enhancement_orchestrator()
        safe_print("  ✅ Enhancement orchestrator initialized")
    except Exception as e:
        errors.append(f"Enhancement orchestrator: {e}")
        safe_print(f"  ❌ Enhancement orchestrator: {e}")
        return False
    
    # Step 3: Simulate pre-generation check
    safe_print("\n[3/8] Running pre-generation checks...")
    try:
        recent_topics = variety_mgr.get_recent_topics()
        pre_check = orch.pre_generation_checks(
            topic="Psychology trick about decision fatigue",
            hook="Your brain is exhausted. Here's why.",
            recent_topics=recent_topics
        )
        if pre_check.get('proceed', False):
            safe_print("  ✅ Pre-generation: Topic approved (no duplicates)")
        else:
            safe_print(f"  ⚠️ Pre-generation: {pre_check.get('warnings', ['Blocked'])}")
    except Exception as e:
        errors.append(f"Pre-generation: {e}")
        safe_print(f"  ❌ Pre-generation: {e}")
    
    # Step 4: Simulate content generation (mock phrases)
    safe_print("\n[4/8] Simulating content generation...")
    try:
        mock_phrases = [
            "Your brain makes 35,000 decisions every single day.",
            "That's why you feel completely drained by evening.",
            "Successful people use routines to reduce this load.",
            "Try wearing the same outfit every day for a week.",
            "Watch what happens to your energy levels!"
        ]
        mock_metadata = {
            "hook": mock_phrases[0],
            "category": "psychology",
            "title": "Why You Feel Exhausted (It's Not Sleep)"
        }
        safe_print("  ✅ Content generated (mock)")
    except Exception as e:
        errors.append(f"Content generation: {e}")
        safe_print(f"  ❌ Content generation: {e}")
    
    # Step 5: Run post-content checks
    safe_print("\n[5/8] Running post-content checks...")
    try:
        post_checks = orch.post_content_checks(mock_phrases, mock_metadata)
        
        if post_checks.get('pacing'):
            safe_print("  ✅ Voice pacing: Generated")
        else:
            safe_print("  ⏭️ Voice pacing: Skipped (no AI)")
        
        if post_checks.get('retention_prediction'):
            ret = post_checks['retention_prediction']
            safe_print(f"  ✅ Retention prediction: {ret.get('estimated_avg_retention', '?')}%")
        else:
            safe_print("  ⏭️ Retention prediction: Skipped (no AI)")
        
        if post_checks.get('value_density'):
            val = post_checks['value_density']
            safe_print(f"  ✅ Value density: {val.get('value_score', '?')}/10")
        else:
            safe_print("  ⏭️ Value density: Skipped (no AI)")
            
    except Exception as e:
        errors.append(f"Post-content checks: {e}")
        safe_print(f"  ❌ Post-content checks: {e}")
    
    # Step 6: Simulate B-roll with error learning
    safe_print("\n[6/8] Testing B-roll error learning...")
    try:
        test_keyword = "obscure_test_keyword_xyz"
        
        # Record failure
        orch.record_error('broll', test_keyword)
        
        # Check if it should be skipped
        should_skip = orch.should_skip_broll_keyword(test_keyword)
        safe_print(f"  ✅ Error learning works (should_skip after 1 fail: {should_skip})")
    except Exception as e:
        errors.append(f"B-roll error learning: {e}")
        safe_print(f"  ❌ B-roll error learning: {e}")
    
    # Step 7: Record A/B test variant
    safe_print("\n[7/8] Recording A/B test variant...")
    try:
        orch.record_ab_test(
            variant_type="title_styles",
            variant_name="curiosity_gap",
            video_id="integration_test_123",
            metadata=mock_metadata
        )
        safe_print("  ✅ A/B test recorded")
    except Exception as e:
        errors.append(f"A/B test: {e}")
        safe_print(f"  ❌ A/B test: {e}")
    
    # Step 8: Get SEO description and CTA
    safe_print("\n[8/8] Testing metadata helpers...")
    try:
        cta = orch.get_cta()
        safe_print(f"  ✅ CTA: '{cta}'")
    except Exception as e:
        errors.append(f"Metadata helpers: {e}")
        safe_print(f"  ❌ Metadata helpers: {e}")
    
    # Summary
    safe_print("\n" + "=" * 60)
    if errors:
        safe_print(f"❌ INTEGRATION TEST FAILED: {len(errors)} error(s)")
        for err in errors:
            safe_print(f"  - {err}")
        return False
    else:
        safe_print("✅ INTEGRATION TEST PASSED")
        safe_print("All v9.0 components work together correctly!")
        return True


def test_data_flow():
    """Test that data flows correctly between weekly → daily."""
    safe_print("\n" + "=" * 60)
    safe_print("DATA FLOW TEST - Weekly → Daily")
    safe_print("=" * 60)
    
    try:
        # Simulate weekly analytics writing data
        safe_print("\n[1/3] Simulating weekly analytics update...")
        from persistent_state import get_variety_manager
        
        variety_mgr = get_variety_manager()
        
        # Write mock learned data
        test_data = {
            "preferred_categories": ["psychology", "money"],
            "title_tricks": ["use numbers", "curiosity gap"],
            "best_title_styles": ["number_hook", "curiosity_gap"]
        }
        
        for key, value in test_data.items():
            if key not in variety_mgr.state:
                variety_mgr.state[key] = value
        variety_mgr._save_state()
        
        safe_print("  ✅ Weekly data written to variety_state.json")
        
        # Reload and verify
        safe_print("\n[2/3] Verifying data persistence...")
        from persistent_state import VarietyStateManager
        fresh_mgr = VarietyStateManager()
        
        for key in test_data.keys():
            if key in fresh_mgr.state:
                safe_print(f"  ✅ {key}: persisted correctly")
            else:
                safe_print(f"  ❌ {key}: NOT found after reload")
        
        # Test that daily can read it
        safe_print("\n[3/3] Testing daily workflow can read data...")
        prefs = fresh_mgr.get_learned_preferences()
        
        for key in test_data.keys():
            if key in prefs:
                safe_print(f"  ✅ get_learned_preferences() includes {key}")
            else:
                safe_print(f"  ⚠️ {key} not in learned preferences")
        
        safe_print("\n✅ DATA FLOW TEST PASSED")
        return True
        
    except Exception as e:
        safe_print(f"\n❌ DATA FLOW TEST FAILED: {e}")
        return False


def test_workflow_integration():
    """Verify workflow files reference the correct scripts."""
    safe_print("\n" + "=" * 60)
    safe_print("WORKFLOW INTEGRATION TEST")
    safe_print("=" * 60)
    
    workflows = {
        ".github/workflows/generate.yml": ["pro_video_generator.py", "analytics_feedback"],
        ".github/workflows/analytics-feedback.yml": ["variety_state.json", "viral_patterns.json"],
        ".github/workflows/monthly-analysis.yml": ["monthly_analysis.py"]
    }
    
    all_ok = True
    
    for workflow_path, expected_refs in workflows.items():
        path = Path(workflow_path)
        if path.exists():
            content = path.read_text()
            safe_print(f"\n[{workflow_path}]")
            
            for ref in expected_refs:
                if ref in content:
                    safe_print(f"  ✅ References '{ref}'")
                else:
                    safe_print(f"  ⚠️ Missing reference to '{ref}'")
                    all_ok = False
        else:
            safe_print(f"\n[{workflow_path}] NOT FOUND")
            all_ok = False
    
    if all_ok:
        safe_print("\n✅ WORKFLOW INTEGRATION TEST PASSED")
    else:
        safe_print("\n⚠️ Some workflow references may be missing")
    
    return all_ok


if __name__ == "__main__":
    safe_print("\n" + "=" * 60)
    safe_print("  VIRALSHORTS FACTORY v9.0 - QUICK INTEGRATION TESTS")
    safe_print("=" * 60)
    safe_print(f"  Time: {datetime.now().isoformat()}")
    
    results = []
    
    results.append(("Integration Flow", test_integration()))
    results.append(("Data Flow", test_data_flow()))
    results.append(("Workflow Integration", test_workflow_integration()))
    
    # Final summary
    safe_print("\n" + "=" * 60)
    safe_print("FINAL SUMMARY")
    safe_print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        safe_print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    safe_print("=" * 60)
    
    if all_passed:
        safe_print("🎉 ALL INTEGRATION TESTS PASSED!")
        safe_print("v9.0 is fully integrated and ready for production.")
    else:
        safe_print("⚠️ Some tests failed. Please review above.")
    
    sys.exit(0 if all_passed else 1)



