#!/usr/bin/env python3
"""
Script to refresh Smart Model Router rankings.
Called by the weekly refresh-ai-patterns workflow.
"""

import sys
import os

# Add paths
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src')

try:
    from smart_model_router import get_smart_router
    
    print("=" * 60)
    print("SMART MODEL ROUTER REFRESH")
    print("=" * 60)
    
    router = get_smart_router()
    
    # Force refresh rankings
    router.refresh_rankings()
    
    # Print summary
    stats = router.get_stats()
    print(f"\nLast refresh: {stats['last_refresh']}")
    print(f"Models discovered: Check rankings below")
    
    # Print rankings
    router.print_rankings()
    
    print("\n[OK] Smart Model Router rankings refreshed!")
    
except Exception as e:
    print(f"[ERROR] Failed to refresh model router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

