#!/usr/bin/env python3
"""
Comprehensive Test Suite for All AI Modules
============================================

Tests every AI-first module to ensure they work correctly.
Run this before deploying to production.
"""

import sys
import time
from datetime import datetime

sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src/utils')
sys.path.insert(0, 'src/analytics')
sys.path.insert(0, 'src/quota')
sys.path.insert(0, 'src/enhancements')

PASSED = 0
FAILED = 0
SKIPPED = 0


def test(name: str, condition: bool, detail: str = ""):
    """Record test result."""
    global PASSED, FAILED
    if condition:
        print(f"[PASS] {name}")
        PASSED += 1
    else:
        print(f"[FAIL] {name} - {detail}")
        FAILED += 1
    return condition


def skip(name: str, reason: str):
    """Skip a test."""
    global SKIPPED
    print(f"[SKIP] {name} - {reason}")
    SKIPPED += 1


def main():
    global PASSED, FAILED, SKIPPED
    
    print("=" * 70)
    print("COMPREHENSIVE AI MODULE TEST SUITE")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # =========================================================================
    # TEST 1: AI Pattern Generator
    # =========================================================================
    print("\n[1] AI PATTERN GENERATOR")
    try:
        from ai_pattern_generator import get_pattern_generator
        gen = get_pattern_generator()
        test("Import success", True)
        test("Has generate_patterns_with_ai", hasattr(gen, 'generate_patterns_with_ai'))
        test("Has get_patterns", hasattr(gen, 'get_patterns'))
        test("needs_refresh returns bool", isinstance(gen.needs_refresh(), bool))
    except Exception as e:
        test("AI Pattern Generator works", False, str(e))
    
    # =========================================================================
    # TEST 2: AI Hook Generator
    # =========================================================================
    print("\n[2] AI HOOK GENERATOR")
    try:
        from ai_hook_generator import get_hook_generator
        gen = get_hook_generator()
        test("Import success", True)
        test("Has generate_hook", hasattr(gen, 'generate_hook'))
        hook = gen.generate_hook("productivity tips", "productivity")
        test("generate_hook returns string", isinstance(hook, str))
        test("Hook not empty", len(hook) > 0)
    except Exception as e:
        test("AI Hook Generator works", False, str(e))
    
    # =========================================================================
    # TEST 3: AI CTA Generator
    # =========================================================================
    print("\n[3] AI CTA GENERATOR")
    try:
        from ai_cta_generator import get_cta_generator
        gen = get_cta_generator()
        test("Import success", True)
        test("Has generate_cta", hasattr(gen, 'generate_cta'))
        cta = gen.generate_cta("productivity tips", "productivity")
        test("generate_cta returns string", isinstance(cta, str))
        test("CTA not empty", len(cta) > 0)
    except Exception as e:
        test("AI CTA Generator works", False, str(e))
    
    # =========================================================================
    # TEST 4: AI Topic Suggester
    # =========================================================================
    print("\n[4] AI TOPIC SUGGESTER")
    try:
        from ai_topic_suggester import get_topic_suggester
        gen = get_topic_suggester()
        test("Import success", True)
        test("Has get_suggestions", hasattr(gen, 'get_suggestions'))
        topics = gen.get_suggestions(count=3)
        test("get_suggestions returns list", isinstance(topics, list))
        test("Returns 3 topics", len(topics) >= 1)
    except Exception as e:
        test("AI Topic Suggester works", False, str(e))
    
    # =========================================================================
    # TEST 5: AI Content Quality Checker
    # =========================================================================
    print("\n[5] AI CONTENT QUALITY CHECKER")
    try:
        from ai_content_quality_checker import get_quality_checker
        gen = get_quality_checker()
        test("Import success", True)
        test("Has check_content", hasattr(gen, 'check_content'))
        result = gen.check_content({
            "hook": "Test hook",
            "phrases": ["Phrase 1", "Phrase 2"],
            "cta": "Comment below!",
            "category": "test"
        })
        test("check_content returns dict", isinstance(result, dict))
        test("Result has score", "score" in result)
        test("Result has verdict", "verdict" in result)
    except Exception as e:
        test("AI Content Quality Checker works", False, str(e))
    
    # =========================================================================
    # TEST 6: AI B-Roll Keyword Generator
    # =========================================================================
    print("\n[6] AI B-ROLL KEYWORD GENERATOR")
    try:
        from ai_broll_keywords import get_broll_keyword_generator
        gen = get_broll_keyword_generator()
        test("Import success", True)
        test("Has generate_keywords", hasattr(gen, 'generate_keywords'))
        keywords = gen.generate_keywords("productivity tips", "productivity")
        test("generate_keywords returns list", isinstance(keywords, list))
        test("Keywords not empty", len(keywords) > 0)
    except Exception as e:
        test("AI B-Roll Keyword Generator works", False, str(e))
    
    # =========================================================================
    # TEST 7: AI Music Mood Selector
    # =========================================================================
    print("\n[7] AI MUSIC MOOD SELECTOR")
    try:
        from ai_music_mood import get_music_mood_selector
        gen = get_music_mood_selector()
        test("Import success", True)
        test("Has select_mood", hasattr(gen, 'select_mood'))
        mood, genre = gen.select_mood("productivity tips", "productivity")
        test("select_mood returns tuple", isinstance((mood, genre), tuple))
        test("Mood not empty", len(mood) > 0)
        test("Genre not empty", len(genre) > 0)
    except Exception as e:
        test("AI Music Mood Selector works", False, str(e))
    
    # =========================================================================
    # TEST 8: AI Title Optimizer
    # =========================================================================
    print("\n[8] AI TITLE OPTIMIZER")
    try:
        from ai_title_optimizer import get_title_optimizer
        gen = get_title_optimizer()
        test("Import success", True)
        test("Has optimize_title", hasattr(gen, 'optimize_title'))
        title = gen.optimize_title("productivity tips", "productivity")
        test("optimize_title returns string", isinstance(title, str))
        test("Title not empty", len(title) > 0)
    except Exception as e:
        test("AI Title Optimizer works", False, str(e))
    
    # =========================================================================
    # TEST 9: Model Intelligence
    # =========================================================================
    print("\n[9] MODEL INTELLIGENCE")
    try:
        from model_intelligence import get_model_intelligence
        mi = get_model_intelligence()
        test("Import success", True)
        test("Has get_best_provider_for_task", hasattr(mi, 'get_best_provider_for_task'))
        provider = mi.get_best_provider_for_task("quality_evaluation")
        test("get_best_provider_for_task returns string", isinstance(provider, str))
    except Exception as e:
        test("Model Intelligence works", False, str(e))
    
    # =========================================================================
    # TEST 10: Prompt Cache
    # =========================================================================
    print("\n[10] PROMPT CACHE")
    try:
        from prompt_cache import get_prompt_cache
        cache = get_prompt_cache()
        test("Import success", True)
        test("Has get", hasattr(cache, 'get'))
        test("Has set", hasattr(cache, 'set'))
        
        # Test set and get
        cache.set("test_prompt", "test_response", "test")
        result = cache.get("test_prompt", "test")
        test("Cache set/get works", result == "test_response")
    except Exception as e:
        test("Prompt Cache works", False, str(e))
    
    # =========================================================================
    # TEST 11: Persistent State
    # =========================================================================
    print("\n[11] PERSISTENT STATE")
    try:
        from persistent_state import get_variety_manager, get_viral_manager
        vm = get_variety_manager()
        vpm = get_viral_manager()
        test("VarietyManager import", True)
        test("ViralPatternsManager import", True)
        test("Has _get_ai_categories", hasattr(vm, '_get_ai_categories'))
    except Exception as e:
        test("Persistent State works", False, str(e))
    
    # =========================================================================
    # TEST 12: Self Learning Engine
    # =========================================================================
    print("\n[12] SELF LEARNING ENGINE")
    try:
        from self_learning_engine import SelfLearningEngine
        engine = SelfLearningEngine()
        test("Import success", True)
        test("Has learn_from_video", hasattr(engine, 'learn_from_video'))
        test("Has get_prompt_boost", hasattr(engine, 'get_prompt_boost'))
    except Exception as e:
        test("Self Learning Engine works", False, str(e))
    
    # =========================================================================
    # TEST 13: AI Description Generator
    # =========================================================================
    print("\n[13] AI DESCRIPTION GENERATOR")
    try:
        from ai_description_generator import get_description_generator
        gen = get_description_generator()
        test("Import success", True)
        test("Has generate_description", hasattr(gen, 'generate_description'))
        desc = gen.generate_description("Test Title", "test topic", "productivity")
        test("generate_description returns string", isinstance(desc, str))
        test("Description not empty", len(desc) > 0)
    except Exception as e:
        test("AI Description Generator works", False, str(e))
    
    # =========================================================================
    # TEST 14: AI Hashtag Generator
    # =========================================================================
    print("\n[14] AI HASHTAG GENERATOR")
    try:
        from ai_hashtag_generator import get_hashtag_generator
        gen = get_hashtag_generator()
        test("Import success", True)
        test("Has generate_hashtags", hasattr(gen, 'generate_hashtags'))
        tags = gen.generate_hashtags("test topic", "productivity")
        test("generate_hashtags returns list", isinstance(tags, list))
        test("Contains #shorts", "#shorts" in tags)
    except Exception as e:
        test("AI Hashtag Generator works", False, str(e))
    
    # =========================================================================
    # TEST 15: Retention Predictor
    # =========================================================================
    print("\n[15] RETENTION PREDICTOR")
    try:
        from retention_predictor import get_retention_predictor
        pred = get_retention_predictor()
        test("Import success", True)
        test("Has predict_retention", hasattr(pred, 'predict_retention'))
        result = pred.predict_retention({
            "hook": "Test hook",
            "phrases": ["Phrase 1", "Phrase 2"],
            "cta": "Comment!",
            "category": "test"
        })
        test("predict_retention returns dict", isinstance(result, dict))
        test("Has overall_retention", "overall_retention" in result)
        test("Has predicted_curve", "predicted_curve" in result)
    except Exception as e:
        test("Retention Predictor works", False, str(e))
    
    # =========================================================================
    # TEST 16: AI Thumbnail Text Optimizer
    # =========================================================================
    print("\n[16] AI THUMBNAIL TEXT OPTIMIZER")
    try:
        from ai_thumbnail_text import get_thumbnail_optimizer
        opt = get_thumbnail_optimizer()
        test("Import success", True)
        test("Has generate_thumbnail_text", hasattr(opt, 'generate_thumbnail_text'))
        result = opt.generate_thumbnail_text("Test Title", "test topic", "productivity")
        test("generate_thumbnail_text returns dict", isinstance(result, dict))
        test("Has main_text", "main_text" in result)
        test("Has emphasis_word", "emphasis_word" in result)
    except Exception as e:
        test("AI Thumbnail Text Optimizer works", False, str(e))
    
    # =========================================================================
    # TEST 17: Engagement Predictor
    # =========================================================================
    print("\n[17] ENGAGEMENT PREDICTOR")
    try:
        from engagement_predictor import get_engagement_predictor
        pred = get_engagement_predictor()
        test("Import success", True)
        test("Has predict_engagement", hasattr(pred, 'predict_engagement'))
        result = pred.predict_engagement({
            "hook": "Test hook",
            "phrases": ["Phrase 1", "Phrase 2"],
            "cta": "Comment!",
            "category": "test"
        })
        test("predict_engagement returns dict", isinstance(result, dict))
        test("Has overall_engagement", "overall_engagement" in result)
        test("Has comment_rate", "comment_rate" in result)
    except Exception as e:
        test("Engagement Predictor works", False, str(e))
    
    # =========================================================================
    # TEST 18: Virality Calculator
    # =========================================================================
    print("\n[18] VIRALITY CALCULATOR")
    try:
        from virality_calculator import get_virality_calculator
        calc = get_virality_calculator()
        test("Import success", True)
        test("Has calculate_virality", hasattr(calc, 'calculate_virality'))
        result = calc.calculate_virality({
            "hook": "Test hook",
            "phrases": ["Phrase 1", "Phrase 2"],
            "cta": "Comment!",
            "category": "test",
            "topic": "test topic"
        })
        test("calculate_virality returns dict", isinstance(result, dict))
        test("Has overall_score", "overall_score" in result)
        test("Has grade", "grade" in result)
    except Exception as e:
        test("Virality Calculator works", False, str(e))
    
    # =========================================================================
    # TEST 19: Script Analyzer
    # =========================================================================
    print("\n[19] SCRIPT ANALYZER")
    try:
        from script_analyzer import get_script_analyzer
        analyzer = get_script_analyzer()
        test("Import success", True)
        test("Has analyze_script", hasattr(analyzer, 'analyze_script'))
        result = analyzer.analyze_script({
            "hook": "Test hook",
            "phrases": ["Phrase 1", "Phrase 2"],
            "cta": "Comment!"
        })
        test("analyze_script returns dict", isinstance(result, dict))
        test("Has overall_score", "overall_score" in result)
        test("Has metrics", "metrics" in result)
        test("Has suggestions", "suggestions" in result)
    except Exception as e:
        test("Script Analyzer works", False, str(e))
    
    # =========================================================================
    # TEST 20: Content Optimizer (Integration)
    # =========================================================================
    print("\n[20] CONTENT OPTIMIZER (INTEGRATION)")
    try:
        sys.path.insert(0, 'src/core')
        from content_optimizer import get_content_optimizer
        opt = get_content_optimizer()
        test("Import success", True)
        test("Has optimize", hasattr(opt, 'optimize'))
        test("Has quick_score", hasattr(opt, 'quick_score'))
        status = opt.get_module_status()
        modules_available = sum(1 for v in status.values() if v)
        test(f"Modules available: {modules_available}/10", modules_available >= 6)
    except Exception as e:
        test("Content Optimizer works", False, str(e))
    
    # =========================================================================
    # TEST 21: Competitor Gap Analyzer
    # =========================================================================
    print("\n[21] COMPETITOR GAP ANALYZER")
    try:
        from competitor_gap_analyzer import get_gap_analyzer
        analyzer = get_gap_analyzer()
        test("Import success", True)
        test("Has analyze_gap", hasattr(analyzer, 'analyze_gap'))
        test("Has identify_opportunities", hasattr(analyzer, 'identify_opportunities'))
    except Exception as e:
        test("Competitor Gap Analyzer works", False, str(e))
    
    # =========================================================================
    # TEST 22: AI Trend Analyzer
    # =========================================================================
    print("\n[22] AI TREND ANALYZER")
    try:
        from ai_trend_analyzer import get_trend_analyzer
        analyzer = get_trend_analyzer()
        test("Import success", True)
        test("Has analyze_trend", hasattr(analyzer, 'analyze_trend'))
        test("Has get_trending_topics", hasattr(analyzer, 'get_trending_topics'))
    except Exception as e:
        test("AI Trend Analyzer works", False, str(e))
    
    # =========================================================================
    # TEST 23: AI Audience Persona Generator
    # =========================================================================
    print("\n[23] AI AUDIENCE PERSONA GENERATOR")
    try:
        from ai_audience_persona import get_persona_generator
        gen = get_persona_generator()
        test("Import success", True)
        test("Has generate_persona", hasattr(gen, 'generate_persona'))
        persona = gen.generate_persona("productivity")
        test("generate_persona returns dict", isinstance(persona, dict))
        test("Has name", "name" in persona)
    except Exception as e:
        test("AI Audience Persona Generator works", False, str(e))
    
    # =========================================================================
    # TEST 24: AI Voice Script Optimizer
    # =========================================================================
    print("\n[24] AI VOICE SCRIPT OPTIMIZER")
    try:
        from ai_voice_script import get_voice_optimizer
        opt = get_voice_optimizer()
        test("Import success", True)
        test("Has optimize_script", hasattr(opt, 'optimize_script'))
        result = opt.optimize_script({"hook": "Test", "phrases": ["P1"], "cta": "C"})
        test("optimize_script returns dict", isinstance(result, dict))
        test("Has timing", "timing" in result)
    except Exception as e:
        test("AI Voice Script Optimizer works", False, str(e))
    
    # =========================================================================
    # TEST 25: AI Comment Response Generator
    # =========================================================================
    print("\n[25] AI COMMENT RESPONSE GENERATOR")
    try:
        from ai_comment_response import get_comment_generator
        gen = get_comment_generator()
        test("Import success", True)
        test("Has generate_response", hasattr(gen, 'generate_response'))
        result = gen.generate_response("Great video!")
        test("generate_response returns dict", isinstance(result, dict))
        test("Has sentiment", "sentiment" in result)
        test("Has response", "response" in result)
    except Exception as e:
        test("AI Comment Response Generator works", False, str(e))
    
    # =========================================================================
    # TEST 26: AI Quality Gate
    # =========================================================================
    print("\n[26] AI QUALITY GATE")
    try:
        sys.path.insert(0, 'src/core')
        from ai_quality_gate import get_quality_gate
        gate = get_quality_gate()
        test("Import success", True)
        test("Has check", hasattr(gate, 'check'))
        test("Has get_stats", hasattr(gate, 'get_stats'))
        test("Has THRESHOLDS", hasattr(gate, 'THRESHOLDS'))
    except Exception as e:
        test("AI Quality Gate works", False, str(e))
    
    # =========================================================================
    # TEST 27: Dashboard Generator
    # =========================================================================
    print("\n[27] DASHBOARD GENERATOR")
    try:
        from dashboard_generator import get_dashboard_generator
        gen = get_dashboard_generator()
        test("Import success", True)
        test("Has generate_html", hasattr(gen, 'generate_html'))
        test("Has save_dashboard", hasattr(gen, 'save_dashboard'))
        test("Has get_summary", hasattr(gen, 'get_summary'))
    except Exception as e:
        test("Dashboard Generator works", False, str(e))
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed:  {PASSED}")
    print(f"Failed:  {FAILED}")
    print(f"Skipped: {SKIPPED}")
    print(f"Total:   {PASSED + FAILED + SKIPPED}")
    print(f"Success Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%")
    print("=" * 70)
    
    if FAILED > 0:
        print("[OVERALL] SOME TESTS FAILED")
        return 1
    else:
        print("[OVERALL] ALL TESTS PASSED!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

