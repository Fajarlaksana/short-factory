"""Paths, model lists and per-language settings for the studio pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = ROOT / "output" / "studio"
DATA_DIR = ROOT / "data" / "studio"
CACHE_DIR = ROOT / "cache" / "studio"
BROLL_CACHE = CACHE_DIR / "broll"
FONTS_DIR = ROOT / "assets" / "studio" / "fonts"
MUSIC_DIR = ROOT / "assets" / "music_library"
HISTORY_FILE = DATA_DIR / "history.json"

for _d in (OUTPUT_DIR, DATA_DIR, CACHE_DIR, BROLL_CACHE, FONTS_DIR, MUSIC_DIR):
    _d.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT, FPS = 1080, 1920, 30

# Script length: ~140 words of narration is roughly 50 seconds
TARGET_WORDS = (120, 150)
BEATS = (7, 9)

# Seconds per shot: long beats get several clips so the picture keeps moving
MAX_SHOT_SECONDS = 3.5

# Text models, tried in order. Gemini first (JSON mode + vision), Groq as backup.
GEMINI_TEXT_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]
GROQ_TEXT_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]
# Writing quality matters most for scripts: these go first for script/fact-check/adaptation
STRONG_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash", "openai/gpt-oss-120b"]

# TTS models. 3.x models take a [bracketed] style tag; 2.5 takes a "Say ...:" prefix.
# 2.5 first: measured far fewer glitches/dropouts than the 3.x TTS models on long narration
TTS_MODELS = [
    "gemini-2.5-flash-preview-tts",
    "gemini-3.1-flash-tts-preview",
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
]
TTS_STYLE = "confident, energetic business documentary narrator, natural conversational pacing"

LANGUAGES = {
    "en": {
        "name": "English",
        "wiki": "en",
        "voice": "Charon",
        "edge_voice": "en-US-AndrewMultilingualNeural",
        "cta": "Follow for more business breakdowns.",
    },
    "id": {
        "name": "Bahasa Indonesia",
        "wiki": "id",
        "voice": "Charon",
        "edge_voice": "id-ID-ArdiNeural",
        "cta": "Follow untuk bedah bisnis lainnya.",
    },
}

# Fonts (SIL Open Font License, from github.com/google/fonts)
FONTS = {
    "caption": ("Poppins Black", "Poppins-Black.ttf",
                "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Black.ttf"),
    "title": ("Anton", "Anton-Regular.ttf",
              "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"),
    # Clean "news explainer" look for kinetic text and thumbnails
    "kinetic": ("Poppins ExtraBold", "Poppins-ExtraBold.ttf",
                "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf"),
    "kinetic_italic": ("Poppins ExtraBold Italic", "Poppins-ExtraBoldItalic.ttf",
                       "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBoldItalic.ttf"),
}

# Word-by-word karaoke captions at the bottom. Off by default: the kinetic headline at the top
# (motion.py) carries the key words, like popular Indonesian explainer channels.
KARAOKE_CAPTIONS = False

MUSIC_MOODS = ["documentary", "corporate", "tension", "upbeat", "lofi"]

# Subtle synthetic whoosh/impact under the opening headline (relative to the voice)
SFX_ENABLED = True
SFX_VOLUME = 0.35

# Thumbnail: clean news-style headline over a photo. The split (top vs bottom) layout is off by
# default because it often pairs weak/odd labels.
THUMB_SPLIT = False
