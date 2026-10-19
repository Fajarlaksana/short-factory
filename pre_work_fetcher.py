#!/usr/bin/env python3
"""Wrapper for pre_work_fetcher from src/utils/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ai'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'quota'))
from src.utils.pre_work_fetcher import PreWorkFetcher
if __name__ == "__main__":
    fetcher = PreWorkFetcher()
    fetcher.run()

