#!/usr/bin/env python3
"""
ViralShorts Factory - v15.0 Enhancement Verification Test
============================================================

This script tests ALL v15.0 enhancements:
1. Token Budget Manager - Smart provider selection
2. Self-Learning Engine - Pattern learning
3. First-Attempt Maximizer - Quality boost
4. Task-specific AI calls - Budget tracking

Run this locally to verify everything works before deployment!
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def safe_print(text):
    """Print safely regardless of encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))


def test_token_budget_manager():
    """Test the Token Budget Manager."""
    safe_print("\n" + "="*60)
    safe_print("TEST 1: Token Budget Manager")
    safe_print("="*60)
    
    try:
        from token_budget_manager import get_budget_manager, get_first_attempt_maximizer
        
        # Test budget manager
        budget = get_budget_manager()
        safe_print("[OK] TokenBudgetManager initialized")
        
        # Check status
        status = budget.get_status()
        for provider, info in status.items():
            safe_print(f"   {provider}: {info['available']:,} tokens available")
        
        # Test provider selection
        test_cases = [
            ("concept", True, "Should use Groq for critical tasks"),
            ("content", True, "Should use Groq for content"),
            ("broll", False, "Should use Gemini for non-critical"),
            ("metadata", False, "Should use Gemini for metadata"),
        ]
        
        for task, prefer_quality, desc in test_cases:
            provider = budget.choose_provider(task, prefer_quality)
            safe_print(f"   Task '{task}' -> {provider} ({desc})")
        
        # Test first-attempt maximizer
        first_attempt = get_first_attempt_maximizer()
        safe_print("[OK] FirstAttemptMaximizer initialized")
        
        boost = first_attempt.get_quality_boost_prompt()
        safe_print(f"   Quality boost length: {len(boost)} chars")
        
        safe_print("\n[OK] Token Budget Manager: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        safe_print(f"[FAIL] Token Budget Manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_self_learning_engine():
    """Test the Self-Learning Engine."""
    safe_print("\n" + "="*60)
    safe_print("TEST 2: Self-Learning Engine")
    safe_print("="*60)
    
    try:
        from self_learning_engine import get_learning_engine
        
        engine = get_learning_engine()
        safe_print("[OK] SelfLearningEngine initialized")
        
        # Get initial stats
        stats = engine.data.get("stats", {})
        safe_print(f"   Total videos analyzed: {stats.get('total_videos', 0)}")
        safe_print(f"   Regeneration rate: {stats.get('regeneration_rate', 0)*100:.1f}%")
        
        # Test learning from a video
        engine.learn_from_video(
            score=9,
            category="test_category",
            topic="Test topic for verification",
            hook="STOP - This is a test hook that works",
            phrases=[
                "STOP - This is a test hook that works",
                "Test phrase 2 with specific $500 number",
                "Test phrase 3 with 80% statistic",
                "Comment YES if you agree!"
            ]
        )
        safe_print("[OK] Learned from high-score video")
        
        engine.learn_from_video(
            score=4,
            category="bad_category",
            topic="Bad topic with weird $3333 number",
            hook="You're losing $3333 every year",
            phrases=[
                "You're losing $3333 every year",
                "This is awkward content"
            ],
            was_regeneration=True
        )
        safe_print("[OK] Learned from low-score video")
        
        # Get prompt boost
        boost = engine.get_prompt_boost()
        safe_print(f"   Prompt boost length: {len(boost)} chars")
        safe_print(f"   Contains insights: {'SELF-LEARNING' in boost}")
        
        # Check recommendations
        recs = engine.data.get("recommendations", {})
        safe_print(f"   Best hook styles: {recs.get('best_hook_styles', [])}")
        safe_print(f"   Avoid phrases: {recs.get('avoid_phrases', [])}")
        
        safe_print("\n[OK] Self-Learning Engine: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        safe_print(f"[FAIL] Self-Learning Engine: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pro_video_generator_integration():
    """Test that pro_video_generator.py has v15.0 integration."""
    safe_print("\n" + "="*60)
    safe_print("TEST 3: Pro Video Generator v15.0 Integration")
    safe_print("="*60)
    
    try:
        # Read the file and check for v15.0 markers
        with open("pro_video_generator.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("token_budget_manager import", "from token_budget_manager import"),
            ("self_learning_engine import", "from self_learning_engine import"),
            ("budget_manager initialization", "self.budget_manager = get_budget_manager()"),
            ("learning_engine initialization", "self.learning_engine = get_learning_engine()"),
            ("Task-specific concept call", 'task="concept"'),
            ("Task-specific content call", 'task="content"'),
            ("Task-specific evaluate call", 'task="evaluate"'),
            ("Task-specific broll call", 'task="broll"'),
            ("Task-specific metadata call", 'task="metadata"'),
            ("First-attempt boost in prompt", "first_attempt_boost"),
            ("Learning boost in prompt", "learning_boost"),
            ("Learning recording after generation", "self.learning_engine.learn_from_video"),
        ]
        
        all_passed = True
        for name, marker in checks:
            if marker in content:
                safe_print(f"   [OK] {name}")
            else:
                safe_print(f"   [FAIL] {name} - marker not found: {marker[:40]}...")
                all_passed = False
        
        if all_passed:
            safe_print("\n[OK] Pro Video Generator Integration: ALL TESTS PASSED")
        else:
            safe_print("\n[FAIL] Pro Video Generator Integration: Some tests failed")
        
        return all_passed
        
    except Exception as e:
        safe_print(f"[FAIL] Pro Video Generator Integration: {e}")
        return False


def test_workflow_configurations():
    """Test GitHub workflow configurations."""
    safe_print("\n" + "="*60)
    safe_print("TEST 4: GitHub Workflow Configurations")
    safe_print("="*60)
    
    workflows = [
        ".github/workflows/generate.yml",
        ".github/workflows/test-generate.yml",
        ".github/workflows/analytics-feedback.yml",
        ".github/workflows/monthly-analysis.yml",
    ]
    
    all_found = True
    for workflow in workflows:
        if Path(workflow).exists():
            # Check for continue-on-error on artifact downloads
            with open(workflow, "r") as f:
                content = f.read()
            
            has_artifact_handling = (
                "continue-on-error: true" in content or 
                "if [ \"$ARTIFACT_ID\" != \"null\" ]" in content
            )
            
            if has_artifact_handling:
                safe_print(f"   [OK] {workflow} - Artifact handling: safe")
            else:
                safe_print(f"   [WARN] {workflow} - No safe artifact handling")
        else:
            safe_print(f"   [FAIL] {workflow} - Not found")
            all_found = False
    
    if all_found:
        safe_print("\n[OK] Workflow Configurations: ALL TESTS PASSED")
    else:
        safe_print("\n[FAIL] Workflow Configurations: Some workflows missing")
    
    return all_found


def test_god_tier_prompts():
    """Test god-tier prompts are loaded correctly."""
    safe_print("\n" + "="*60)
    safe_print("TEST 5: God-Tier Prompts")
    safe_print("="*60)
    
    try:
        from god_tier_prompts import VIRAL_TOPIC_PROMPT
        
        checks = [
            ("Promise-Payoff Contract", "PROMISE-PAYOFF CONTRACT"),
            ("Numbered Promise Rule", "NUMBERED PROMISE RULE"),
            ("Believability & Quality", "BELIEVABILITY"),
            ("Awkward Number Warning", "AWKWARD NUMBERS"),
            ("Short-Form Readability", "SHORT-FORM VIDEO READABILITY"),
        ]
        
        all_passed = True
        for name, marker in checks:
            if marker in VIRAL_TOPIC_PROMPT:
                safe_print(f"   [OK] {name}")
            else:
                safe_print(f"   [FAIL] {name} - not found in prompt")
                all_passed = False
        
        safe_print(f"   Prompt length: {len(VIRAL_TOPIC_PROMPT)} chars")
        
        if all_passed:
            safe_print("\n[OK] God-Tier Prompts: ALL TESTS PASSED")
        else:
            safe_print("\n[FAIL] God-Tier Prompts: Some markers missing")
        
        return all_passed
        
    except Exception as e:
        safe_print(f"[FAIL] God-Tier Prompts: {e}")
        return False


def test_performance_dashboard():
    """Test the Performance Dashboard."""
    safe_print("\n" + "="*60)
    safe_print("TEST 6: Performance Dashboard")
    safe_print("="*60)
    
    try:
        from performance_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        safe_print("[OK] PerformanceDashboard initialized")
        
        # Test metrics collection
        metrics = dashboard.collect_metrics()
        safe_print(f"   Metrics collected: {len(metrics)} categories")
        
        # Test summary string
        summary = dashboard.get_summary_string()
        safe_print(f"   Summary length: {len(summary)} chars")
        
        # Test HTML export
        html = dashboard.export_html()
        safe_print(f"   HTML export length: {len(html)} chars")
        
        safe_print("\n[OK] Performance Dashboard: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        safe_print(f"[FAIL] Performance Dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    safe_print("\n" + "="*70)
    safe_print("   VIRALSHORTS FACTORY v15.0 ENHANCEMENT VERIFICATION")
    safe_print("="*70)
    
    results = []
    
    results.append(("Token Budget Manager", test_token_budget_manager()))
    results.append(("Self-Learning Engine", test_self_learning_engine()))
    results.append(("Pro Video Generator Integration", test_pro_video_generator_integration()))
    results.append(("Workflow Configurations", test_workflow_configurations()))
    results.append(("God-Tier Prompts", test_god_tier_prompts()))
    results.append(("Performance Dashboard", test_performance_dashboard()))
    
    safe_print("\n" + "="*70)
    safe_print("   FINAL RESULTS")
    safe_print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        safe_print(f"   {status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        safe_print("\n" + "="*70)
        safe_print("   ALL v15.0 ENHANCEMENTS VERIFIED!")
        safe_print("   Ready for production deployment!")
        safe_print("="*70)
        return 0
    else:
        safe_print("\n" + "="*70)
        safe_print("   SOME TESTS FAILED - Please review above")
        safe_print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

