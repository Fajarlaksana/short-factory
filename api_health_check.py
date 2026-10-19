#!/usr/bin/env python3
"""Wrapper for api_health_check from src/utils/"""
import sys, os
import env_loader  # noqa: F401 - loads API keys from .env for local runs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'quota'))
from src.utils.api_health_check import main
if __name__ == "__main__":
    main()

