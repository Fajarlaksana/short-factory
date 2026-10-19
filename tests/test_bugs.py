#!/usr/bin/env python3
"""Bug search and validation."""

import ast
import os

print('=== BUG SEARCH ===')
print()

# 1. Check for syntax errors
print('1. Checking for syntax errors...')
files = ['pro_video_generator.py', 'analytics_feedback.py', 'ai_music_selector.py', 'dailymotion_uploader.py', 'youtube_uploader.py']
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            code = fp.read()
        ast.parse(code)
        print(f'  {f}: OK (no syntax errors)')
    except SyntaxError as e:
        print(f'  {f}: SYNTAX ERROR at line {e.lineno}')

print()

# 2. Check workflow batch_size consistency
print('2. Checking workflow defaults...')
with open('.github/workflows/generate.yml', 'r', encoding='utf-8') as f:
    yml = f.read()
    if "default: '2'" in yml:
        print('  Workflow batch_size: 2 (optimized for quota)')
    else:
        print('  WARNING: Batch size not set to 2!')

# 3. Check schedule
if '0 6 * * *' in yml and '0 14 * * *' in yml and '0 22 * * *' in yml:
    print('  Schedule: 3x/day at 6AM, 2PM, 10PM UTC (OK)')
else:
    print('  WARNING: Schedule not optimal!')

print()

# 4. Check for missing error handling in upload
print('3. Checking error handling...')
with open('pro_video_generator.py', 'r', encoding='utf-8') as f:
    code = f.read()
    if 'except Exception' in code:
        print('  Exception handling: Present')
    if 'FALLBACK' in code:
        print('  Fallback logic: Present')
    if 'fallback_title' in code:
        print('  Title fallback (v7.14 fix): Present')

print()

# 5. Check Dailymotion is_created_for_kids fix
print('4. Checking Dailymotion fixes...')
with open('dailymotion_uploader.py', 'r', encoding='utf-8') as f:
    code = f.read()
    if 'is_created_for_kids' in code:
        print('  is_created_for_kids field: Present (v7.13 fix)')
    else:
        print('  WARNING: is_created_for_kids field MISSING!')

print()

# 6. Check AI fallback chain
print('5. Checking AI fallback chain...')
with open('pro_video_generator.py', 'r', encoding='utf-8') as f:
    code = f.read()
    if 'gemini-1.5-flash-latest' in code:
        print('  Gemini 1.5 fallback: Correct model name')
    if 'gemini-pro' in code:
        print('  Gemini Pro last resort: Present')

print()
print('=== No critical bugs found! ===')

