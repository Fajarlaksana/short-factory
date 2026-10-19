"""Tiny console logger that never crashes on Windows code pages."""
import sys
import time


def log(msg: str):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii"
        print(line.encode(enc, errors="replace").decode(enc), flush=True)
