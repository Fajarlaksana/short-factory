#!/usr/bin/env python3
"""Test the AI Pattern Generator."""

import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')

from ai_pattern_generator import get_pattern_generator

def main():
    print('Testing AI Pattern Generator...')
    gen = get_pattern_generator()
    
    print(f'Needs refresh: {gen.needs_refresh()}')
    print(f'Current source: {gen.patterns.get("patterns_source", "unknown")}')
    
    # Test with actual AI call (if keys available)
    if gen.groq_key or gen.gemini_key:
        print('API keys found - generating patterns with AI...')
        patterns = gen.generate_patterns_with_ai()
        print(f'Generated: {len(patterns.get("title_patterns", []))} title patterns')
        print(f'Source: {patterns.get("patterns_source")}')
        if patterns.get('title_patterns'):
            print(f'Sample title: {patterns["title_patterns"][0]}')
        if patterns.get('hook_patterns'):
            print(f'Sample hook: {patterns["hook_patterns"][0]}')
        print('TEST PASSED!')
    else:
        print('No API keys - would use fallback')
        print('TEST SKIPPED (no keys)')

if __name__ == "__main__":
    main()

