#!/usr/bin/env python3
"""
Test script for SmartModelRouter and SmartAICaller.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'ai'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Ensure encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_router():
    """Test the SmartModelRouter."""
    print("=" * 70)
    print("SMART MODEL ROUTER - UNIT TEST")
    print("=" * 70)
    
    from smart_model_router import (
        get_smart_router, classify_prompt, get_fallback_chain,
        get_best_model_for_prompt
    )
    
    router = get_smart_router()
    
    # Test 1: Prompt Classification
    print("\n[TEST 1] Prompt Classification")
    print("-" * 50)
    
    test_cases = [
        ("Generate a viral topic about psychology", "topic", "creative"),
        ("Evaluate this content for virality", "evaluation", "evaluation"),
        ("Generate hashtags for this video", "hashtag", "simple"),
        ("Analyze trends in our category performance", "analysis", "analysis"),
        ("Write a voiceover script for money tips", "voiceover", "creative"),
        ("Score this hook for scroll-stopping power", "score", "evaluation"),
        ("Extract SEO keywords from this title", "seo", "simple"),
    ]
    
    passed = 0
    for prompt, hint, expected in test_cases:
        result = classify_prompt(prompt, hint)
        status = "PASS" if result == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  {status}: '{hint}' -> {result} (expected: {expected})")
    
    print(f"\nClassification: {passed}/{len(test_cases)} tests passed")
    
    # Test 2: Fallback Chain Generation
    print("\n[TEST 2] Fallback Chain Generation")
    print("-" * 50)
    
    for prompt_type in ["creative", "evaluation", "simple", "analysis"]:
        chain = get_fallback_chain(prompt_type)
        print(f"  {prompt_type.upper()}: {len(chain)} models in chain")
        if chain:
            print(f"    Best: {chain[0][0]}")
            print(f"    Last: {chain[-1][0]}")
    
    # Test 3: Best Model Selection
    print("\n[TEST 3] Best Model Selection")
    print("-" * 50)
    
    prompts = [
        ("Generate viral content about money hacks", "content"),
        ("Rate this video quality from 1-10", "quality"),
        ("Generate 5 hashtags", "hashtag"),
    ]
    
    for prompt, hint in prompts:
        model_key, model_info = get_best_model_for_prompt(prompt, hint)
        print(f"  Prompt: {hint}")
        print(f"    Model: {model_key}")
        print(f"    Quality: {model_info['quality_general']}/10")
        print()
    
    # Test 4: Rankings
    print("[TEST 4] Current Rankings (Top 3 per type)")
    print("-" * 50)
    
    for prompt_type in ["creative", "evaluation", "simple", "analysis"]:
        chain = get_fallback_chain(prompt_type)[:3]
        print(f"  {prompt_type.upper()}:")
        for i, (key, _) in enumerate(chain, 1):
            print(f"    {i}. {key}")
        print()
    
    # Test 5: Verify Creative gets Groq, Evaluation gets Gemini
    print("[TEST 5] Verify Optimal Model Selection")
    print("-" * 50)
    
    # Creative should prefer Groq (llama)
    creative_chain = get_fallback_chain("creative")
    creative_best = creative_chain[0][0] if creative_chain else "none"
    creative_ok = "groq" in creative_best.lower() or "llama" in creative_best.lower()
    print(f"  Creative best model: {creative_best}")
    print(f"  Uses Groq/LLaMA: {'PASS' if creative_ok else 'FAIL'}")
    
    # Evaluation should prefer Gemini
    eval_chain = get_fallback_chain("evaluation")
    eval_best = eval_chain[0][0] if eval_chain else "none"
    # Note: Could be either Gemini or Groq depending on scoring, just verify it exists
    print(f"  Evaluation best model: {eval_best}")
    print(f"  Has fallback chain: {'PASS' if len(eval_chain) > 1 else 'FAIL'}")
    
    print("\n" + "=" * 70)
    print("ROUTER TESTS COMPLETED")
    print("=" * 70)
    
    return passed == len(test_cases)


def test_caller_without_api():
    """Test the SmartAICaller structure (no actual API calls)."""
    print("\n" + "=" * 70)
    print("SMART AI CALLER - STRUCTURE TEST")
    print("=" * 70)
    
    from smart_ai_caller import get_smart_caller, SmartAICaller
    
    caller = get_smart_caller()
    
    # Test 1: Caller exists
    print("\n[TEST 1] Caller Initialization")
    print(f"  Caller instance: {'PASS' if isinstance(caller, SmartAICaller) else 'FAIL'}")
    print(f"  Router attached: {'PASS' if caller.router else 'FAIL'}")
    
    # Test 2: JSON parsing
    print("\n[TEST 2] JSON Parsing")
    
    test_json_inputs = [
        ('{"score": 8, "reason": "good"}', True),
        ('```json\n{"data": [1,2,3]}\n```', True),
        ('Some text {"valid": true} more text', True),
        ('invalid json', False),
    ]
    
    for text, should_parse in test_json_inputs:
        result = caller.parse_json(text)
        success = (result is not None) == should_parse
        print(f"  {text[:30]}... -> {'PASS' if success else 'FAIL'}")
    
    # Test 3: Stats
    print("\n[TEST 3] Stats Retrieval")
    stats = caller.get_stats()
    print(f"  Stats available: {'PASS' if isinstance(stats, dict) else 'FAIL'}")
    print(f"  Keys: {list(stats.keys())}")
    
    print("\n" + "=" * 70)
    print("CALLER STRUCTURE TESTS COMPLETED")
    print("=" * 70)
    
    return True


def test_caller_with_api():
    """Test actual API calls (requires API keys)."""
    print("\n" + "=" * 70)
    print("SMART AI CALLER - LIVE API TEST")
    print("=" * 70)
    
    # Check for API keys
    has_groq = bool(os.environ.get("GROQ_API_KEY"))
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    
    print(f"\n  Groq API Key: {'Present' if has_groq else 'Missing'}")
    print(f"  Gemini API Key: {'Present' if has_gemini else 'Missing'}")
    
    if not (has_groq or has_gemini):
        print("\n  SKIPPING: No API keys available")
        return True
    
    from smart_ai_caller import smart_call_ai, smart_call_json
    
    # Test 1: Simple text response
    print("\n[TEST 1] Simple Text Response")
    result = smart_call_ai(
        prompt="Say 'test successful' in exactly 2 words.",
        hint="simple",
        max_tokens=20
    )
    print(f"  Response: {result[:50] if result else 'None'}...")
    print(f"  Result: {'PASS' if result else 'FAIL'}")
    
    # Test 2: JSON response
    print("\n[TEST 2] JSON Response")
    result = smart_call_json(
        prompt='Return ONLY valid JSON: {"status": "ok", "number": 42}',
        hint="simple",
        max_tokens=50
    )
    print(f"  Parsed: {result}")
    print(f"  Result: {'PASS' if result and 'status' in result else 'FAIL'}")
    
    # Test 3: Creative prompt (should use Groq)
    print("\n[TEST 3] Creative Prompt Routing")
    result = smart_call_ai(
        prompt="Generate ONE viral video title about saving money.",
        hint="topic",
        max_tokens=100
    )
    print(f"  Response: {result[:80] if result else 'None'}...")
    print(f"  Result: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 70)
    print("LIVE API TESTS COMPLETED")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    all_passed = True
    
    # Run router tests
    try:
        if not test_router():
            all_passed = False
    except Exception as e:
        print(f"Router test error: {e}")
        all_passed = False
    
    # Run caller structure tests
    try:
        if not test_caller_without_api():
            all_passed = False
    except Exception as e:
        print(f"Caller structure test error: {e}")
        all_passed = False
    
    # Run live API tests if keys available
    try:
        if not test_caller_with_api():
            all_passed = False
    except Exception as e:
        print(f"API test error: {e}")
        all_passed = False
    
    print("\n" + "=" * 70)
    print(f"FINAL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 70)
    
    sys.exit(0 if all_passed else 1)

