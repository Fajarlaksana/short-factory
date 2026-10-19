"""Background music from a local, hand-picked library (assets/music_library/<mood>/*.mp3)."""
import json
import random
from typing import Optional

from . import config
from .log import log

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
RECENT_FILE = config.DATA_DIR / "recent_music.json"


def _tracks(folder):
    return [p for p in folder.rglob("*") if p.suffix.lower() in AUDIO_EXT] if folder.exists() else []


def pick(mood: str) -> Optional[str]:
    """Pick a track for the mood, falling back to any mood; avoids the last few used."""
    candidates = _tracks(config.MUSIC_DIR / (mood or "documentary")) or _tracks(config.MUSIC_DIR)
    if not candidates:
        log("[music] library is empty - add tracks to assets/music_library/<mood>/ (see README there)")
        return None
    try:
        recent = json.loads(RECENT_FILE.read_text(encoding="utf-8"))
    except Exception:
        recent = []
    fresh = [p for p in candidates if str(p) not in recent] or candidates
    track = random.choice(fresh)
    RECENT_FILE.write_text(json.dumps(([str(track)] + recent)[:5]), encoding="utf-8")
    log(f"[music] {track.relative_to(config.MUSIC_DIR)}")
    return str(track)
