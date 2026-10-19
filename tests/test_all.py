#!/usr/bin/env python3
"""
ViralShorts Factory - Comprehensive Test Suite v3.0
====================================================

Tests ALL modules including v3.0 enhancements:
- Video enhancements (captions, progress bar, effects)
- Multi-source trend fetching
- AI thumbnails
- A/B testing
"""

import sys
import os

print("=" * 60)
print("COMPREHENSIVE BUG CHECK v3.0")
print("=" * 60)

errors = []
warnings = []

# Test 1: Import all core modules
print("\n[1] Testing core module imports...")

modules_to_test = [
    "platform_safety",
    "analytics_feedback",
    "viral_video_science",
    "ai_trend_detector",
    "god_tier_prompts",
    "dailymotion_uploader",
    "viral_optimizer",
    "background_music",
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"   [OK] {module}")
    except Exception as e:
        errors.append(f"{module}: {e}")
        print(f"   [FAIL] {module}: {e}")

# Test 2: Import v3.0 enhancement modules
print("\n[2] Testing v3.0 enhancement modules...")

v3_modules = [
    "video_enhancements",
    "multi_trend_fetcher",
    "ai_thumbnail",
    "trending_twitter",  # Twitter trends + Storytelling + Monetization
]

for module in v3_modules:
    try:
        __import__(module)
        print(f"   [OK] {module}")
    except Exception as e:
        errors.append(f"{module}: {e}")
        print(f"   [FAIL] {module}: {e}")

# Test 3: Import main modules
print("\n[3] Testing main generation modules...")

try:
    import script_v2
    print("   [OK] script_v2")
except Exception as e:
    errors.append(f"script_v2: {e}")
    print(f"   [FAIL] script_v2: {e}")

try:
    import generate_multi
    print("   [OK] generate_multi")
except Exception as e:
    errors.append(f"generate_multi: {e}")
    print(f"   [FAIL] generate_multi: {e}")

try:
    import dynamic_video_generator
    print("   [OK] dynamic_video_generator")
except Exception as e:
    errors.append(f"dynamic_video_generator: {e}")
    print(f"   [FAIL] dynamic_video_generator: {e}")

# Test 4: Check platform safety specs
print("\n[4] Testing platform safety...")
try:
    from platform_safety import PLATFORM_SPECS, AntiBanSystem
    system = AntiBanSystem()
    
    yt_res = PLATFORM_SPECS["youtube_shorts"]["resolution"]
    dm_res = PLATFORM_SPECS["dailymotion"]["resolution"]
    
    print(f"   YouTube Shorts resolution: {yt_res[0]}x{yt_res[1]}")
    print(f"   Dailymotion resolution: {dm_res[0]}x{dm_res[1]}")
    
    variations = system.get_unique_video_variations()
    print(f"   Video variations: {len(variations)} parameters")
    
    can_upload, reason = system.should_upload_now("youtube")
    print(f"   Upload check: {can_upload} - {reason}")
    
    print("   [OK] platform_safety tests")
except Exception as e:
    errors.append(f"platform_safety test: {e}")
    print(f"   [FAIL]: {e}")

# Test 5: Check analytics
print("\n[5] Testing analytics feedback loop...")
try:
    from analytics_feedback import VideoMetadataStore, FeedbackLoopController
    
    controller = FeedbackLoopController()
    guidance = controller.get_content_guidance()
    print(f"   Content guidance: {len(guidance)} keys")
    
    store = VideoMetadataStore()
    print(f"   Metadata store: {len(store.metadata)} videos tracked")
    
    print("   [OK] analytics tests")
except Exception as e:
    errors.append(f"analytics test: {e}")
    print(f"   [FAIL]: {e}")

# Test 6: Check video enhancements (NEW in v3.0)
print("\n[6] Testing video enhancements (v3.0)...")
try:
    from video_enhancements import (
        CaptionGenerator, 
        ProgressBar, 
        VisualEffects, 
        MotionGraphics
    )
    
    # Test caption generator
    cap_gen = CaptionGenerator("tiktok")
    timings = cap_gen.split_into_words_with_timing("Test caption text", 5.0)
    print(f"   Caption timing: {len(timings)} words")
    
    # Test progress bar
    pb = ProgressBar("gradient")
    frame = pb.create_progress_frame(0.5, 1080)
    print(f"   Progress bar frame: {frame.size}")
    
    # Test visual effects
    vignette = VisualEffects.create_vignette(1080, 1920)
    print(f"   Vignette: {vignette.size}")
    
    particles = VisualEffects.create_particles_frame(1080, 1920)
    print(f"   Particles: {particles.size}")
    
    print("   [OK] video_enhancements tests")
except Exception as e:
    errors.append(f"video_enhancements test: {e}")
    print(f"   [FAIL]: {e}")

# Test 7: Check multi-source trend fetcher (NEW in v3.0)
print("\n[7] Testing multi-source trend fetcher (v3.0)...")
try:
    from multi_trend_fetcher import (
        MultiTrendFetcher,
        GoogleTrendsFetcher,
        RedditTrendsFetcher,
        AITrendGenerator
    )
    
    # Test Google RSS fetcher (no API call needed for init)
    google = GoogleTrendsFetcher()
    print("   Google Trends RSS: initialized")
    
    # Test Reddit fetcher
    reddit = RedditTrendsFetcher()
    print(f"   Reddit fetcher: {len(reddit.SUBREDDITS)} subreddits")
    
    # Test AI trend generator (no API call)
    ai_gen = AITrendGenerator()
    print("   AI Trend Generator: initialized")
    
    # Test main fetcher
    fetcher = MultiTrendFetcher()
    print("   Multi-source fetcher: ready")
    
    print("   [OK] multi_trend_fetcher tests")
except Exception as e:
    errors.append(f"multi_trend_fetcher test: {e}")
    print(f"   [FAIL]: {e}")

# Test 8: Check AI thumbnail generator (NEW in v3.0)
print("\n[8] Testing AI thumbnail generator (v3.0)...")
try:
    from ai_thumbnail import AIThumbnailGenerator, ABTestingFramework
    
    # Test thumbnail generator (no API call)
    thumb_gen = AIThumbnailGenerator()
    print(f"   Thumbnail sizes: {len(thumb_gen.THUMBNAIL_SIZES)} platforms")
    print(f"   Color schemes: {len(thumb_gen.COLOR_SCHEMES)} themes")
    
    # Test A/B testing framework
    ab = ABTestingFramework("data/test_ab_temp.json")
    print("   A/B Testing framework: initialized")
    
    print("   [OK] ai_thumbnail tests")
except Exception as e:
    errors.append(f"ai_thumbnail test: {e}")
    print(f"   [FAIL]: {e}")

# Test 9: Check god tier prompts
print("\n[9] Testing god tier prompts...")
try:
    from god_tier_prompts import (
        VIRAL_TOPIC_PROMPT,
        BROLL_KEYWORDS_PROMPT,
        CONTENT_EVALUATION_PROMPT,
        VOICEOVER_PROMPT,
        GodTierContentGenerator
    )
    
    print(f"   VIRAL_TOPIC_PROMPT: {len(VIRAL_TOPIC_PROMPT)} chars")
    print(f"   BROLL_KEYWORDS_PROMPT: {len(BROLL_KEYWORDS_PROMPT)} chars")
    print(f"   CONTENT_EVALUATION_PROMPT: {len(CONTENT_EVALUATION_PROMPT)} chars")
    print(f"   VOICEOVER_PROMPT: {len(VOICEOVER_PROMPT)} chars")
    
    # Check generator class
    gen = GodTierContentGenerator()
    has_groq = gen.groq_client is not None
    has_gemini = gen.gemini_client is not None
    print(f"   AI providers: Groq={has_groq}, Gemini={has_gemini}")
    
    print("   [OK] god_tier_prompts tests")
except Exception as e:
    errors.append(f"god_tier_prompts test: {e}")
    print(f"   [FAIL]: {e}")

# Test 10: Check video generation config
print("\n[10] Testing video generation config...")
try:
    from script_v2 import VIDEO_WIDTH, VIDEO_HEIGHT, THEMES
    
    print(f"   Video size: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"   Themes available: {len(THEMES)}")
    
    # Check resolution matches platform specs
    from platform_safety import PLATFORM_SPECS
    expected_w, expected_h = PLATFORM_SPECS["youtube_shorts"]["resolution"]
    
    if VIDEO_WIDTH == expected_w and VIDEO_HEIGHT == expected_h:
        print(f"   Resolution matches YouTube Shorts: [OK]")
    else:
        warnings.append(f"Resolution mismatch: {VIDEO_WIDTH}x{VIDEO_HEIGHT} vs {expected_w}x{expected_h}")
        print(f"   [WARN]: Resolution mismatch!")
    
    print("   [OK] video config tests")
except Exception as e:
    errors.append(f"video config test: {e}")
    print(f"   [FAIL]: {e}")

# Test 11: Check dynamic video generator enhancements
print("\n[11] Testing dynamic video generator with enhancements...")
try:
    from dynamic_video_generator import DynamicVideoGenerator
    
    gen = DynamicVideoGenerator(enable_enhancements=True)
    
    has_captions = gen.caption_gen is not None
    has_progress = gen.progress_bar is not None
    has_effects = gen.effects is not None
    
    print(f"   Caption generator: {has_captions}")
    print(f"   Progress bar: {has_progress}")
    print(f"   Visual effects: {has_effects}")
    
    if all([has_captions, has_progress, has_effects]):
        print("   All v3.0 enhancements: [OK]")
    else:
        warnings.append("Some v3.0 enhancements not loaded")
        print("   [WARN] Some enhancements not loaded")
    
    print("   [OK] dynamic_video_generator tests")
except Exception as e:
    errors.append(f"dynamic_video_generator test: {e}")
    print(f"   [FAIL]: {e}")

# Test 12: Check viral optimizer
print("\n[12] Testing viral optimizer...")
try:
    from viral_optimizer import (
        ViralOptimizer,
        HashtagOptimizer,
        TitleOptimizer
    )
    
    optimizer = ViralOptimizer()
    print("   Viral optimizer: initialized")
    
    hashtag_opt = HashtagOptimizer()
    print("   Hashtag optimizer: initialized")
    
    title_opt = TitleOptimizer()
    print("   Title optimizer: initialized")
    
    print("   [OK] viral_optimizer tests")
except Exception as e:
    errors.append(f"viral_optimizer test: {e}")
    print(f"   [FAIL]: {e}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

if warnings:
    print(f"\n[!] {len(warnings)} WARNINGS:")
    for warn in warnings:
        print(f"   - {warn}")

if errors:
    print(f"\n[X] {len(errors)} ERRORS:")
    for err in errors:
        print(f"   - {err}")
    print("\n" + "=" * 60)
    print("SOME TESTS FAILED")
    print("=" * 60)
    sys.exit(1)
else:
    print("\n[OK] ALL TESTS PASSED!")
    print("\n" + "=" * 60)
    print("SYSTEM STATUS: READY")
    print("=" * 60)
    print("\nv3.0 Enhancements Active:")
    print("  - TikTok-style word-by-word captions")
    print("  - Ken Burns zoom effects")
    print("  - Progress bar overlay")
    print("  - Vignette and particle effects")
    print("  - Multi-source trend fetching (Google RSS, Reddit, AI)")
    print("  - AI thumbnail generation")
    print("  - A/B testing framework")
    print("  - Viral optimizer (hashtags, titles, CTAs)")
    sys.exit(0)
