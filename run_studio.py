#!/usr/bin/env python3
"""ViralShorts Studio - business case-study Shorts in English and Indonesian.

Examples:
  python run_studio.py                       # AI picks a topic, renders EN + ID
  python run_studio.py --topic "Costco"      # specific company / idea
  python run_studio.py --lang en --count 3   # three English-only videos
"""
import argparse
import sys
import traceback

import env_loader  # noqa: F401 - loads API keys from .env for local runs
from studio.log import log
from studio.pipeline import make_video


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", help="company or idea to cover (default: AI picks)")
    parser.add_argument("--lang", nargs="+", default=["en", "id"], choices=["en", "id"])
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--keep-work", action="store_true", help="keep intermediate files for debugging")
    args = parser.parse_args()

    done, failed = [], 0
    for i in range(args.count):
        log(f"########## VIDEO {i + 1}/{args.count}")
        try:
            done.append(make_video(args.topic if i == 0 else None, args.lang, args.keep_work))
        except Exception as e:
            failed += 1
            log(f"[!] video {i + 1} failed: {e}")
            traceback.print_exc()
    log(f"Finished: {len(done)} ok, {failed} failed")
    for folder in done:
        log(f"  {folder}")
    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
