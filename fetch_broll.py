#!/usr/bin/env python3
"""Wrapper for fetch_broll from src/utils/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'utils'))
from src.utils.fetch_broll import fetch_broll_videos
if __name__ == "__main__":
    fetch_broll_videos()

