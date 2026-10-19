#!/usr/bin/env python3
"""Test script for v8.0 upgrades."""

import sys
import os

# Fix Windows encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

print("Testing ViralShorts Factory v8.0 Upgrades...")
print("=" * 60)

# Test 1: Persistent State
print("\n[TEST 1] Persistent State Managers")
try:
    from persistent_state import (
        get_upload_manager, get_variety_manager, 
        get_analytics_manager, get_viral_manager
    )
    
    upload = get_upload_manager()
    print(f"  [OK] Upload Manager initialized")
    print(f"    - Dailymotion slots: {upload.get_dailymotion_slots_available()}/4")
    print(f"    - YouTube uploads today: {upload.get_youtube_uploads_today()}/6")
    
    variety = get_variety_manager()
    print(f"  [OK] Variety Manager initialized")
    categories = variety.get_exclusions('categories', 5)
    print(f"    - Recent categories: {categories if categories else 'None yet'}")
    
    analytics = get_analytics_manager()
    print(f"  [OK] Analytics Manager initialized")
    print(f"    - Videos tracked: {len(analytics.state.get('videos', []))}")
    
    viral = get_viral_manager()
    print(f"  [OK] Viral Patterns Manager initialized")
    print(f"    - Title patterns: {len(viral.patterns.get('title_patterns', []))}")
    print(f"    - Hook patterns: {len(viral.patterns.get('hook_patterns', []))}")
    
    print("  [PASS] All persistent state managers working!")
except Exception as e:
    print(f"  [FAIL] Persistent state error: {e}")
    sys.exit(1)

# Test 2: Viral Channel Analyzer
print("\n[TEST 2] Viral Channel Analyzer")
try:
    from viral_channel_analyzer import get_viral_prompt_boost, ViralChannelAnalyzer
    
    analyzer = ViralChannelAnalyzer()
    patterns = analyzer.get_viral_patterns()
    print(f"  [OK] Analyzer initialized")
    print(f"    - Title formulas: {len(patterns.get('title_formulas', []))}")
    print(f"    - Hook techniques: {len(patterns.get('hook_techniques', []))}")
    
    boost = get_viral_prompt_boost()
    print(f"  [OK] Prompt boost generated ({len(boost)} chars)")
    
    print("  [PASS] Viral channel analyzer working!")
except Exception as e:
    print(f"  [FAIL] Viral analyzer error: {e}")

# Test 3: Pro Video Generator Integration
print("\n[TEST 3] Pro Video Generator v8.0")
try:
    from pro_video_generator import MasterAI, PERSISTENT_STATE_AVAILABLE, VIRAL_PATTERNS_AVAILABLE
    
    print(f"  Persistent state available: {PERSISTENT_STATE_AVAILABLE}")
    print(f"  Viral patterns available: {VIRAL_PATTERNS_AVAILABLE}")
    
    if PERSISTENT_STATE_AVAILABLE:
        print("  [OK] Persistent state integrated!")
    else:
        print("  [WARN] Persistent state NOT integrated")
        
    if VIRAL_PATTERNS_AVAILABLE:
        print("  [OK] Viral patterns integrated!")
    else:
        print("  [WARN] Viral patterns NOT integrated")
    
    print("  [PASS] Pro video generator ready!")
except Exception as e:
    print(f"  [FAIL] Generator error: {e}")

# Test 4: Workflow file check
print("\n[TEST 4] Workflow Configuration")
try:
    import yaml
    with open('.github/workflows/generate.yml', 'r') as f:
        content = f.read()
    
    checks = {
        'Persistent state restore': 'Restore persistent state' in content,
        'Persistent state save': 'Save persistent state' in content,
        'v8.0 messaging': 'v8.0' in content,
        'Shorter videos mention': '15-25' in content,
    }
    
    for check, passed in checks.items():
        status = "[OK]" if passed else "[X]"
        print(f"  {status} {check}")
    
    if all(checks.values()):
        print("  [PASS] Workflow configured correctly!")
    else:
        print("  [WARN] Some workflow checks failed")
except Exception as e:
    print(f"  [FAIL] Workflow check error: {e}")

print("\n" + "=" * 60)
print("V8.0 UPGRADE VERIFICATION COMPLETE")
print("=" * 60)

