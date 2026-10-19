#!/usr/bin/env python3
"""
Weekly AI Pattern Refresh Script
=================================

This script is called by the refresh-ai-patterns workflow to
regenerate viral patterns using AI.

v17.8: AI-first architecture - patterns come from AI, not hardcoded.
"""

import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')

from ai_pattern_generator import get_pattern_generator


def main():
    print('=== AI PATTERN REFRESH ===')
    gen = get_pattern_generator()
    
    # Always regenerate in this workflow
    print('Generating new patterns with AI...')
    patterns = gen.generate_patterns_with_ai()
    
    source = patterns.get('patterns_source', 'unknown')
    ai_gen = patterns.get('ai_generated', False)
    title_count = len(patterns.get('title_patterns', []))
    hook_count = len(patterns.get('hook_patterns', []))
    bait_count = len(patterns.get('engagement_baits', []))
    
    print(f'Source: {source}')
    print(f'AI Generated: {ai_gen}')
    print(f'Title Patterns: {title_count}')
    print(f'Hook Patterns: {hook_count}')
    print(f'Engagement Baits: {bait_count}')
    
    if patterns.get('title_patterns'):
        print(f'Sample: {patterns["title_patterns"][0]}')
    
    print('=== REFRESH COMPLETE ===')
    
    # Inform but don't fail - next run will try again
    if title_count == 0:
        print('INFO: No new patterns generated (will retry next week)')
    else:
        print(f'SUCCESS: Generated {title_count} new patterns!')


if __name__ == "__main__":
    main()

