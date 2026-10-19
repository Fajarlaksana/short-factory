#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST
Verifies ALL recent changes are properly integrated.
"""

def run_tests():
    print("=" * 60)
    print("COMPREHENSIVE INTEGRATION TEST")
    print("=" * 60)
    
    all_passed = True
    
    # TEST 1: All imports work
    print("\n[1] TESTING IMPORTS...")
    try:
        from pro_video_generator import MasterAI, generate_pro_video, ENHANCEMENTS_V12_AVAILABLE, V12_MASTER_PROMPT
        print("   - pro_video_generator imports: OK")
    except Exception as e:
        print(f"   - pro_video_generator imports: FAILED - {e}")
        all_passed = False
    
    try:
        from enhancements_v9 import get_enhancement_orchestrator, EnhancementOrchestrator
        print("   - enhancements_v9 imports: OK")
    except Exception as e:
        print(f"   - enhancements_v9 imports: FAILED - {e}")
        all_passed = False
    
    try:
        from enhancements_v12 import get_v12_complete_master_prompt
        print("   - enhancements_v12 imports: OK")
    except Exception as e:
        print(f"   - enhancements_v12 imports: FAILED - {e}")
        all_passed = False
    
    # TEST 2: V12 enhancements flag
    print("\n[2] TESTING V12 AVAILABILITY...")
    print(f"   - ENHANCEMENTS_V12_AVAILABLE: {ENHANCEMENTS_V12_AVAILABLE}")
    print(f"   - V12_MASTER_PROMPT length: {len(V12_MASTER_PROMPT)} chars")
    if not ENHANCEMENTS_V12_AVAILABLE:
        all_passed = False
    
    # TEST 3: OpenRouter integration
    print("\n[3] TESTING OPENROUTER INTEGRATION...")
    ai = MasterAI()
    print(f"   - openrouter_key exists: {bool(ai.openrouter_key)}")
    print(f"   - openrouter_available flag: {ai.openrouter_available}")
    if not ai.openrouter_available:
        print("   - WARNING: OpenRouter not available!")
        # Don't fail - it's optional
    
    # TEST 4: Orchestrator initializes all v11 classes
    print("\n[4] TESTING ORCHESTRATOR V11 CLASSES...")
    orch = get_enhancement_orchestrator()
    orch._ensure_initialized()
    
    v11_classes = [
        'curiosity_gap', 'number_hook', 'controversy', 'fomo', 'power_words',
        'pattern_interrupt', 'open_loop', 'first_frame', 'audio_hook',
        'watch_time', 'completion_rate', 'comment_bait', 'share_trigger', 'rewatch',
        'color_psychology', 'motion_energy', 'text_readability', 'visual_variety',
        'fact_credibility', 'actionable', 'story_structure', 'memory_hook', 'relatability',
        'trend_lifecycle', 'evergreen_balance', 'cultural_moment', 'viral_pattern', 'platform_trend',
        'micro_retention', 'correlation', 'channel_health', 'growth_rate', 'content_decay',
        'competitor_response', 'niche_authority', 'quality_consistency', 'upload_cadence', 'audience_loyalty'
    ]
    
    initialized_count = 0
    failed_classes = []
    for cls in v11_classes:
        if hasattr(orch, cls) and getattr(orch, cls) is not None:
            initialized_count += 1
        else:
            failed_classes.append(cls)
    
    print(f"   - V11 classes initialized: {initialized_count}/{len(v11_classes)}")
    if failed_classes:
        print(f"   - Failed to initialize: {failed_classes[:5]}...")
    
    # TEST 5: Pre-generation checks return enhancements
    print("\n[5] TESTING PRE-GENERATION CHECKS...")
    pre = orch.pre_generation_checks("productivity tips", "This will shock you", [])
    has_enhancements = "enhancements" in pre and len(pre["enhancements"]) > 0
    print(f"   - Returns enhancements dict: {has_enhancements}")
    if has_enhancements:
        keys = list(pre["enhancements"].keys())
        print(f"   - Enhancement keys ({len(keys)}): {keys[:5]}...")
    else:
        print("   - WARNING: No enhancements returned!")
    
    # TEST 6: Post-content checks return enhancements
    print("\n[6] TESTING POST-CONTENT CHECKS...")
    post = orch.post_content_checks(["Hook phrase", "Content phrase", "Payoff phrase"], {"category": "productivity"})
    has_post_enhancements = "enhancements" in post and len(post["enhancements"]) > 0
    print(f"   - Returns enhancements dict: {has_post_enhancements}")
    if has_post_enhancements:
        keys = list(post["enhancements"].keys())
        print(f"   - Enhancement keys ({len(keys)}): {keys[:5]}...")
    
    # TEST 7: OpenRouter call_ai fallback exists
    print("\n[7] TESTING OPENROUTER IN call_ai METHOD...")
    import inspect
    source = inspect.getsource(ai.call_ai)
    has_openrouter_call = "openrouter" in source.lower()
    print(f"   - OpenRouter in call_ai source: {has_openrouter_call}")
    if not has_openrouter_call:
        print("   - CRITICAL: OpenRouter fallback NOT in call_ai!")
        all_passed = False
    
    # TEST 8: V12 master prompt injected into stage1
    print("\n[8] TESTING V12 PROMPT IN STAGE1...")
    stage1_source = inspect.getsource(ai.stage1_decide_video_concept)
    has_v12_in_stage1 = "v12_guidelines" in stage1_source or "V12_MASTER_PROMPT" in stage1_source
    print(f"   - V12 guidelines in stage1: {has_v12_in_stage1}")
    if not has_v12_in_stage1:
        print("   - CRITICAL: V12 prompt not injected into stage1!")
        all_passed = False
    
    # TEST 9: Analytics feedback tracks new fields
    print("\n[9] TESTING ANALYTICS TRACKING FIELDS...")
    # Check if the code tracks selected_font, sfx_plan, etc.
    with open("pro_video_generator.py", "r", encoding="utf-8") as f:
        pvg_source = f.read()
    tracks_font = "'selected_font'" in pvg_source or '"selected_font"' in pvg_source
    tracks_sfx = "'sfx_plan'" in pvg_source or '"sfx_plan"' in pvg_source
    tracks_promise = "'promise_fixed'" in pvg_source or '"promise_fixed"' in pvg_source
    print(f"   - Tracks selected_font: {tracks_font}")
    print(f"   - Tracks sfx_plan: {tracks_sfx}")
    print(f"   - Tracks promise_fixed: {tracks_promise}")
    
    # TEST 10: Workflow schedules updated
    print("\n[10] TESTING WORKFLOW SCHEDULES...")
    try:
        with open(".github/workflows/analytics-feedback.yml", "r") as f:
            af_content = f.read()
        has_2x_weekly = "0,3" in af_content  # Sunday + Wednesday
        print(f"   - Analytics feedback 2x/week: {has_2x_weekly}")
        
        with open(".github/workflows/monthly-analysis.yml", "r") as f:
            ma_content = f.read()
        has_biweekly = "1,15" in ma_content  # 1st and 15th
        print(f"   - Monthly analysis bi-weekly: {has_biweekly}")
    except Exception as e:
        print(f"   - Could not check workflows: {e}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL CRITICAL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - SEE ABOVE")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    run_tests()

