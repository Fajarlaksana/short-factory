#!/usr/bin/env python3
"""
Analyze Gemini quota usage across workflow runs.
"""

import os
import re
import sys
from datetime import datetime

# Fix console encoding for Unicode
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Get all log files with timestamps
logs = []
import sys
# Handle running from different directories
if os.path.exists('logs_analysis'):
    logs_dir = 'logs_analysis'
elif os.path.exists('../logs_analysis'):
    logs_dir = '../logs_analysis'
else:
    print("logs_analysis directory not found!")
    sys.exit(1)

print(f"Analyzing logs in: {os.path.abspath(logs_dir)}")

for f in os.listdir(logs_dir):
    if f.endswith('.txt') and f.startswith('run_'):
        path = os.path.join(logs_dir, f)
        # Try UTF-16 first (GitHub logs), then UTF-8
        try:
            with open(path, 'r', encoding='utf-16', errors='ignore') as file:
                content = file.read()
        except:
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            # Find timestamp
            match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', content)
            if match:
                timestamp = match.group(1)
                # Count 429s
                gemini_429 = len(re.findall(r'gemini failed: 429', content, re.IGNORECASE))
                logs.append({
                    'file': f,
                    'time': timestamp,
                    'gemini_429': gemini_429
                })

# Sort by time
logs.sort(key=lambda x: x['time'])

print('=== CHRONOLOGICAL LOG ANALYSIS ===')
print()
print('Run | Time             | Gemini 429s | Cumulative Est.')
print('-' * 58)

cumulative_calls = 0
calls_per_run = 8  # Estimated

for i, log in enumerate(logs):
    cumulative_calls += calls_per_run
    status = '429!' if log['gemini_429'] > 0 else 'OK'
    time_short = log['time'][:16]
    print(f" {i+1:2} | {time_short} | {log['gemini_429']:2} errors    | ~{cumulative_calls:3} calls [{status}]")

print()
print('=== MATHEMATICAL ANALYSIS ===')
print()
print(f'Total runs analyzed: {len(logs)}')
print(f'Calls per run (estimate): {calls_per_run}')
print(f'Total calls for all runs: {len(logs) * calls_per_run}')
print()

# Count runs with 429s
runs_with_429 = sum(1 for log in logs if log['gemini_429'] > 0)
print(f'Runs with Gemini 429s: {runs_with_429}/{len(logs)}')

# Find when 429s started
first_429_run = next((i for i, log in enumerate(logs) if log['gemini_429'] > 0), None)
if first_429_run is not None:
    print(f'First 429 at run: #{first_429_run + 1}')
    print(f'Estimated cumulative calls at failure: ~{(first_429_run + 1) * calls_per_run}')
    
print()
print('=== GEMINI FREE TIER LIMITS ===')
print()
print('gemini-2.0-flash-exp:')
print('  - Per-minute: 10 requests')
print('  - Per-day: 1,000 requests')
print()
print('gemini-1.5-flash:')
print('  - Per-minute: 15 requests')  
print('  - Per-day: 1,500 requests')
print()

# Calculate if we exceeded
total_runs = len(logs)
total_calls = total_runs * calls_per_run

print(f'Our usage: {total_calls} calls across {total_runs} runs')
print()

if runs_with_429 > 0:
    print('CONCLUSION: Some runs hit 429 errors.')
    print('This indicates the per-minute limit was likely exceeded,')
    print('OR Gemini quota was already exhausted from external usage.')
else:
    print('CONCLUSION: All runs completed without 429 errors.')

