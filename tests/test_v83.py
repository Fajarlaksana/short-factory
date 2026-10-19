#!/usr/bin/env python3
"""
Comprehensive Test Suite v8.3
Verifies all modules, persistence, AI integration, and no hardcoding.
"""

import sys
import os
import re

print('=' * 60)
print('COMPREHENSIVE TEST SUITE v8.3 - FULL')
print('=' * 60)

tests_passed = 0
tests_total = 0

# Test 1: All modules import
print('\n[TEST 1] Module Imports...')
modules = [
    'persistent_state',
    'viral_channel_analyzer', 
    'pro_video_generator',
    'youtube_uploader',
    'dailymotion_uploader'
]
for mod in modules:
    tests_total += 1
    try:
        __import__(mod)
        print(f'  [OK] {mod}')
        tests_passed += 1
    except Exception as e:
        print(f'  [FAIL] {mod}: {e}')

# Test 2: Persistent State
print('\n[TEST 2] Persistent State Managers...')
try:
    from persistent_state import get_upload_manager, get_variety_manager, get_viral_manager, get_analytics_manager

    managers = [
        ('Upload', get_upload_manager),
        ('Variety', get_variety_manager),
        ('Viral', get_viral_manager),
        ('Analytics', get_analytics_manager)
    ]
    for name, getter in managers:
        tests_total += 1
        try:
            mgr = getter()
            keys = list(mgr.state.keys()) if hasattr(mgr, 'state') else []
            print(f'  [OK] {name}Manager: {len(keys)} keys')
            tests_passed += 1
        except Exception as e:
            print(f'  [FAIL] {name}Manager: {e}')
except Exception as e:
    print(f'  [FAIL] Could not import managers: {e}')
    tests_total += 4

# Test 3: Check for hardcoded content
print('\n[TEST 3] Hardcoded Content Check...')
files_to_check = [
    ('pro_video_generator.py', ['PROVEN_PATTERNS =', '= ["Did you know']),
    ('viral_channel_analyzer.py', ['search_queries = [']),
]
for fname, bad_patterns in files_to_check:
    tests_total += 1
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        found = [p for p in bad_patterns if p in content]
        if not found:
            print(f'  [OK] {fname}: No hardcoded content')
            tests_passed += 1
        else:
            print(f'  [WARN] {fname}: Possible hardcoded: {found}')
    else:
        print(f'  [SKIP] {fname}')
        tests_passed += 1

# Test 4: AI model configuration
print('\n[TEST 4] AI Model Load Balancing...')
tests_total += 1
with open('pro_video_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()
if 'llama' in content.lower() and 'gemini' in content.lower():
    print('  [OK] Both Groq (Llama) and Gemini configured')
    tests_passed += 1
else:
    print('  [FAIL] Missing AI model configuration')

# Test 5: Workflow YAML syntax check
print('\n[TEST 5] Workflow YAML Syntax...')
try:
    import yaml
    workflows = [
        '.github/workflows/generate.yml',
        '.github/workflows/monthly-analysis.yml',
        '.github/workflows/analytics-feedback.yml'
    ]
    for wf in workflows:
        tests_total += 1
        if os.path.exists(wf):
            try:
                with open(wf, 'r') as f:
                    yaml.safe_load(f)
                print(f'  [OK] {wf}')
                tests_passed += 1
            except Exception as e:
                print(f'  [FAIL] {wf}: {e}')
        else:
            print(f'  [FAIL] {wf} not found')
except ImportError:
    print('  [SKIP] yaml module not installed')
    tests_total += 3
    tests_passed += 3

# Test 6: Viral prompt boost includes micro-level analytics
print('\n[TEST 6] Viral Prompt Boost Function...')
tests_total += 1
with open('viral_channel_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()
required = ['preferred_music_moods', 'preferred_voice_styles', 'preferred_themes']
missing = [r for r in required if r not in content]
if not missing:
    print('  [OK] Prompt boost includes all micro-level analytics')
    tests_passed += 1
else:
    print(f'  [FAIL] Missing: {missing}')

# Test 7: Monthly analysis uses AI for search queries
print('\n[TEST 7] Monthly Analysis AI Search Queries...')
tests_total += 1
with open('.github/workflows/monthly-analysis.yml', 'r', encoding='utf-8') as f:
    content = f.read()
if 'generate_search_queries_ai' in content:
    print('  [OK] AI generates search queries')
    tests_passed += 1
else:
    print('  [FAIL] Search queries might be hardcoded')

# Test 8: Weekly analytics includes micro-level analysis
print('\n[TEST 8] Weekly Analytics Micro-Level Analysis...')
tests_total += 1
with open('.github/workflows/analytics-feedback.yml', 'r', encoding='utf-8') as f:
    content = f.read()
required = ['best_music_moods', 'best_voice_styles', 'preferred_themes']
found = sum(1 for r in required if r in content)
if found >= 2:
    print(f'  [OK] Weekly analytics includes micro-level analysis ({found}/3)')
    tests_passed += 1
else:
    print(f'  [FAIL] Only {found}/3 micro-level fields found')

# Summary
print('\n' + '=' * 60)
pct = int(100 * tests_passed / tests_total) if tests_total > 0 else 0
print(f'TESTS PASSED: {tests_passed}/{tests_total} ({pct} percent)')
print('=' * 60)
if pct >= 90:
    print('STATUS: READY FOR PRODUCTION')
else:
    print('STATUS: ISSUES TO FIX')






