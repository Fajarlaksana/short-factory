#!/usr/bin/env python3
"""Wrapper for monthly_analysis from src/analytics/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'analytics'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'quota'))
from src.analytics.monthly_analysis import main
if __name__ == "__main__":
    main()

