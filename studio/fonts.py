"""Make sure the caption/title fonts are present (downloaded once, OFL licensed)."""
import requests

from . import config
from .log import log


def ensure_fonts():
    for family, filename, url in config.FONTS.values():
        path = config.FONTS_DIR / filename
        if path.exists() and path.stat().st_size > 10000:
            continue
        log(f"[fonts] downloading {family}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
