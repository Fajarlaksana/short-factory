#!/usr/bin/env python3
"""Test VarietyStateManager with AI-first architecture."""

import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/utils')
sys.path.insert(0, 'src/ai')

from persistent_state import get_variety_manager

def main():
    print('Testing VarietyStateManager...')
    
    vm = get_variety_manager()
    
    # Test _get_ai_categories
    categories = vm._get_ai_categories()
    print(f'Categories: {categories}')
    print(f'Count: {len(categories)}')
    
    # Test get_category_weights
    weights = vm.get_category_weights()
    print(f'Weights: {weights}')
    
    if categories and len(categories) > 0:
        print('TEST PASSED!')
    else:
        print('TEST FAILED - No categories returned')
        sys.exit(1)

if __name__ == "__main__":
    main()

