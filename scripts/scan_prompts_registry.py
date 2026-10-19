#!/usr/bin/env python3
"""
Script to scan and update the prompts registry.
Called by the weekly refresh-ai-patterns workflow.
"""

import sys
import os

# Add paths
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src')

try:
    from prompts_registry import get_prompts_registry
    
    print("=" * 60)
    print("PROMPTS REGISTRY SCAN")
    print("=" * 60)
    
    registry = get_prompts_registry()
    
    # Scan for new prompts
    registry.scan_and_update()
    
    # Print summary
    summary = registry.get_summary()
    print(f"\nTotal prompts: {summary['total_prompts']}")
    print(f"By type: {summary['by_type']}")
    print(f"Avg quality: {summary['avg_quality']:.1f}/10")
    
    print("\n[OK] Prompts registry updated!")
    
except Exception as e:
    print(f"[ERROR] Failed to update prompts registry: {e}")
    sys.exit(1)

