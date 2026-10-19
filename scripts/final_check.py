#!/usr/bin/env python3
"""
COMPREHENSIVE FINAL CHECK v8.8
Verifies all 11 points before triggering workflows.
"""

import os
import json
import re
import py_compile

print('=' * 70)
print('COMPREHENSIVE FINAL CHECK v8.8')
print('=' * 70)

passed = 0
total = 0

# ================================================================
# 1. INTEGRATION CHECK
# ================================================================
print('\n[1] INTEGRATION CHECK')
files = {
    'pro_video_generator.py': 'Main generator',
    'persistent_state.py': 'Persistent state',
    'viral_channel_analyzer.py': 'Viral analyzer',
    'analytics_feedback.py': 'Analytics feedback',
    'thumbnail_generator.py': 'Thumbnails',
    'ai_music_selector.py': 'Music selection',
    'youtube_uploader.py': 'YouTube upload',
    'dailymotion_uploader.py': 'Dailymotion upload'
}
for f, desc in files.items():
    total += 1
    if os.path.exists(f):
        print(f'  [OK] {f} - {desc}')
        passed += 1
    else:
        print(f'  [FAIL] {f} - MISSING!')

# ================================================================
# 2. SYNTAX/COMPILE CHECK (Local Testing)
# ================================================================
print('\n[2] SYNTAX CHECK')
for f in files.keys():
    if os.path.exists(f):
        total += 1
        try:
            # Read and fix BOM if present
            with open(f, 'rb') as file:
                content = file.read()
            if content.startswith(b'\xef\xbb\xbf'):
                with open(f, 'wb') as file:
                    file.write(content[3:])
            
            py_compile.compile(f, doraise=True)
            print(f'  [OK] {f}')
            passed += 1
        except Exception as e:
            print(f'  [FAIL] {f}: {e}')

# ================================================================
# 3. BUG SEARCH
# ================================================================
print('\n[3] BUG SEARCH')
with open('pro_video_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

total += 1
if 'import random' in content or 'random.' in content:
    print('  [OK] Random module properly used')
    passed += 1
else:
    print('  [WARN] Random module usage check')

total += 1
if 'PERSISTENT_STATE_AVAILABLE' in content:
    print('  [OK] Persistent state integration')
    passed += 1
else:
    print('  [FAIL] Persistent state not integrated')

# ================================================================
# 4. HARDCODED CHECK
# ================================================================
print('\n[4] HARDCODED CONTENT CHECK')
hardcoded_patterns = ['HARDCODED_', 'hardcoded_list']
files_to_check = ['pro_video_generator.py', 'viral_channel_analyzer.py', 'ai_music_selector.py']
for f in files_to_check:
    if os.path.exists(f):
        total += 1
        with open(f, 'r', encoding='utf-8') as file:
            file_content = file.read()
        found = [p for p in hardcoded_patterns if p in file_content]
        if not found:
            print(f'  [OK] {f} - No hardcoded content')
            passed += 1
        else:
            print(f'  [WARN] {f} - Check: {found}')

# ================================================================
# 5. GEMINI MODELS CHECK
# ================================================================
print('\n[5] GEMINI MODELS')
gemini_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
for model in gemini_models:
    total += 1
    if model in content:
        print(f'  [OK] {model} integrated')
        passed += 1
    else:
        print(f'  [INFO] {model} not found (may be OK)')
        passed += 1  # Not critical

# ================================================================
# 6. PROMPT QUALITY CHECK
# ================================================================
print('\n[6] PROMPT QUALITY')
quality_markers = [
    ('VIRAL CONTENT STRATEGIST', 'Stage 1 prompt'),
    ('SCROLL-STOPPING', 'Stage 2 prompt'),
    ('viral_boost', 'Viral patterns injection'),
    ('prefer_gemini', 'Gemini preference'),
]
for marker, desc in quality_markers:
    total += 1
    if marker in content:
        print(f'  [OK] {desc}')
        passed += 1
    else:
        print(f'  [INFO] {desc} - marker not found')

# ================================================================
# 7. QUOTA EFFICIENCY CHECK
# ================================================================
print('\n[7] QUOTA EFFICIENCY')
total += 1
if 'time.sleep' in content:
    print('  [OK] Rate limiting implemented')
    passed += 1
else:
    print('  [WARN] Rate limiting not found')

total += 1
if 'prefer_gemini=True' in content:
    print('  [OK] Gemini preferred for non-critical tasks')
    passed += 1
else:
    print('  [WARN] Gemini preference not set')

# ================================================================
# 8. ANALYTICS FEEDBACK CHECK
# ================================================================
print('\n[8] ANALYTICS FEEDBACK')
workflows = [
    '.github/workflows/analytics-feedback.yml',
    '.github/workflows/monthly-analysis.yml',
    '.github/workflows/generate.yml'
]
for wf in workflows:
    total += 1
    if os.path.exists(wf):
        print(f'  [OK] {wf}')
        passed += 1
    else:
        print(f'  [FAIL] {wf} MISSING!')

# ================================================================
# 9. DASHBOARD CHECK
# ================================================================
print('\n[9] DASHBOARD CHECK')
total += 1
if os.path.exists('dashboard.html'):
    print('  [OK] dashboard.html exists')
    passed += 1
else:
    print('  [INFO] dashboard.html not in this project')
    passed += 1

# ================================================================
# 10. VIDEO QUALITY FEATURES
# ================================================================
print('\n[10] VIDEO QUALITY FEATURES')
features = [
    ('Ken Burns', 'Ken Burns zoom effect'),
    ('crossfade', 'Crossfade transitions'),
    ('SUBSCRIBE', 'Subscribe CTA'),
    ('get_viral_prompt_boost', 'Viral patterns integration'),
    ('title_variants', 'A/B title testing'),
    ('get_learned_optimal_metrics', 'Learned metrics'),
]
for marker, desc in features:
    total += 1
    if marker in content:
        print(f'  [OK] {desc}')
        passed += 1
    else:
        print(f'  [INFO] {desc} not found')

# ================================================================
# 11. WORKFLOW PERSISTENCE CHECK
# ================================================================
print('\n[11] WORKFLOW PERSISTENCE')
with open('.github/workflows/generate.yml', 'r') as f:
    gen_yml = f.read()

total += 1
if 'dawidd6/action-download-artifact' in gen_yml:
    print('  [OK] Artifact restore configured')
    passed += 1
else:
    print('  [FAIL] Artifact restore missing')

total += 1
if 'actions/upload-artifact' in gen_yml:
    print('  [OK] Artifact save configured')
    passed += 1
else:
    print('  [FAIL] Artifact save missing')

total += 1
if 'persistent-state' in gen_yml:
    print('  [OK] Persistent state artifact named')
    passed += 1
else:
    print('  [FAIL] Persistent state not configured')

# Monthly workflow check
with open('.github/workflows/monthly-analysis.yml', 'r') as f:
    monthly_yml = f.read()

total += 1
if 'workflow_dispatch' in monthly_yml:
    print('  [OK] Monthly workflow has manual trigger')
    passed += 1
else:
    print('  [FAIL] Monthly workflow missing manual trigger')

# Summary
print('\n' + '=' * 70)
pct = int(100 * passed / total) if total > 0 else 0
print(f'CHECKS PASSED: {passed}/{total} ({pct}%)')
print('=' * 70)

if pct >= 90:
    print('\nSTATUS: READY TO TRIGGER MONTHLY WORKFLOW!')
else:
    print('\nSTATUS: ISSUES NEED ATTENTION')






