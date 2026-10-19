#!/usr/bin/env python3
"""
Background Music Fetcher - Gets free, copyright-safe music
Uses REAL working sources with verified URLs
"""
import os
import random
import requests
from pathlib import Path
from typing import Optional, List

MUSIC_DIR = Path("./assets/music")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# BENSOUND - Reliable free music with proper CDN
# EXPANDED LIBRARY - 40+ tracks across 10 moods for maximum variety
BENSOUND_MUSIC = {
    # === UPBEAT / FUN ===
    "fun": [
        "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
        "https://www.bensound.com/bensound-music/bensound-cute.mp3",
        "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
        "https://www.bensound.com/bensound-music/bensound-jazzyfrenchy.mp3",
        "https://www.bensound.com/bensound-music/bensound-littleidea.mp3",
    ],
    "upbeat": [
        "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
        "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
        "https://www.bensound.com/bensound-music/bensound-buddy.mp3",
        "https://www.bensound.com/bensound-music/bensound-groovyhiphop.mp3",
        "https://www.bensound.com/bensound-music/bensound-jazzcomedy.mp3",
    ],
    # === DRAMATIC / INTENSE ===
    "dramatic": [
        "https://www.bensound.com/bensound-music/bensound-epic.mp3",
        "https://www.bensound.com/bensound-music/bensound-actionable.mp3",
        "https://www.bensound.com/bensound-music/bensound-instinct.mp3",
        "https://www.bensound.com/bensound-music/bensound-betterdays.mp3",
    ],
    "intense": [
        "https://www.bensound.com/bensound-music/bensound-actionable.mp3",
        "https://www.bensound.com/bensound-music/bensound-epic.mp3",
        "https://www.bensound.com/bensound-music/bensound-extremeaction.mp3",
        "https://www.bensound.com/bensound-music/bensound-punky.mp3",
    ],
    # === ENERGETIC ===
    "energetic": [
        "https://www.bensound.com/bensound-music/bensound-energy.mp3",
        "https://www.bensound.com/bensound-music/bensound-dubstep.mp3",
        "https://www.bensound.com/bensound-music/bensound-moose.mp3",
        "https://www.bensound.com/bensound-music/bensound-dance.mp3",
        "https://www.bensound.com/bensound-music/bensound-funkyelement.mp3",
        "https://www.bensound.com/bensound-music/bensound-popdance.mp3",
    ],
    # === CHILL / RELAXING ===
    "chill": [
        "https://www.bensound.com/bensound-music/bensound-dreams.mp3",
        "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
        "https://www.bensound.com/bensound-music/bensound-relaxing.mp3",
        "https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3",
        "https://www.bensound.com/bensound-music/bensound-tenderness.mp3",
        "https://www.bensound.com/bensound-music/bensound-tomorrow.mp3",
    ],
    # === MYSTERIOUS / SUSPENSE ===
    "mystery": [
        "https://www.bensound.com/bensound-music/bensound-deepblue.mp3",
        "https://www.bensound.com/bensound-music/bensound-scifi.mp3",
        "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
        "https://www.bensound.com/bensound-music/bensound-newdawn.mp3",
    ],
    "mysterious": [
        "https://www.bensound.com/bensound-music/bensound-deepblue.mp3",
        "https://www.bensound.com/bensound-music/bensound-scifi.mp3",
        "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
    ],
    # === INSPIRATIONAL / MOTIVATIONAL ===
    "inspirational": [
        "https://www.bensound.com/bensound-music/bensound-energy.mp3",
        "https://www.bensound.com/bensound-music/bensound-inspire.mp3",
        "https://www.bensound.com/bensound-music/bensound-newdawn.mp3",
        "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3",
        "https://www.bensound.com/bensound-music/bensound-goinghigher.mp3",
    ],
    # === CORPORATE / PROFESSIONAL ===
    "professional": [
        "https://www.bensound.com/bensound-music/bensound-thejazzpiano.mp3",
        "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3",
        "https://www.bensound.com/bensound-music/bensound-corporate.mp3",
        "https://www.bensound.com/bensound-music/bensound-photoalbum.mp3",
    ],
    # === EMOTIONAL / CINEMATIC ===
    "emotional": [
        "https://www.bensound.com/bensound-music/bensound-memories.mp3",
        "https://www.bensound.com/bensound-music/bensound-sadday.mp3",
        "https://www.bensound.com/bensound-music/bensound-pianomoment.mp3",
        "https://www.bensound.com/bensound-music/bensound-love.mp3",
    ],
    # === TECHNOLOGY / MODERN ===
    "tech": [
        "https://www.bensound.com/bensound-music/bensound-scifi.mp3",
        "https://www.bensound.com/bensound-music/bensound-dubstep.mp3",
        "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
        "https://www.bensound.com/bensound-music/bensound-highoctane.mp3",
    ],
}

# Backup: Mixkit (also reliable, CC0) - EXPANDED
MIXKIT_MUSIC = {
    "fun": "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3",
    "upbeat": "https://assets.mixkit.co/music/preview/mixkit-raising-me-higher-34.mp3",
    "dramatic": "https://assets.mixkit.co/music/preview/mixkit-epic-cinematic-trailer-101.mp3",
    "intense": "https://assets.mixkit.co/music/preview/mixkit-driving-ambition-32.mp3",
    "energetic": "https://assets.mixkit.co/music/preview/mixkit-hip-hop-02-738.mp3",
    "chill": "https://assets.mixkit.co/music/preview/mixkit-serene-view-443.mp3",
    "mystery": "https://assets.mixkit.co/music/preview/mixkit-complicated-712.mp3",
    "mysterious": "https://assets.mixkit.co/music/preview/mixkit-complicated-712.mp3",
    "inspirational": "https://assets.mixkit.co/music/preview/mixkit-a-very-happy-christmas-897.mp3",
    "emotional": "https://assets.mixkit.co/music/preview/mixkit-life-is-a-dream-837.mp3",
    "tech": "https://assets.mixkit.co/music/preview/mixkit-games-worldbeat-466.mp3",
    "professional": "https://assets.mixkit.co/music/preview/mixkit-sleepy-cat-135.mp3",
}

# NOTE: Removed pydub tone generation - it sounded like broken radio!
# Better to have NO music than bad generated tones.


def get_background_music(mood: str = "fun", duration: float = 45) -> Optional[str]:
    """
    Fetch REAL background music matching the mood.
    Returns path to downloaded MP3 or None.
    NO GENERATED TONES - only real music or nothing.
    """
    print(f"   🎵 Getting {mood} background music...")
    
    # Check for cached music first
    cached = _get_cached_music(mood)
    if cached:
        print(f"   ✅ Using cached music: {Path(cached).name}")
        return cached
    
    # Try Bensound (reliable, royalty-free)
    bensound_urls = BENSOUND_MUSIC.get(mood, BENSOUND_MUSIC.get("fun", []))
    random.shuffle(bensound_urls)
    
    for url in bensound_urls:
        try:
            music_path = _download_music(url, mood)
            if music_path:
                print(f"   ✅ Got Bensound music")
                return music_path
        except Exception as e:
            print(f"   ⚠️ Bensound download failed: {e}")
            continue
    
    # Try Mixkit backup (CC0, reliable CDN)
    mixkit_url = MIXKIT_MUSIC.get(mood, MIXKIT_MUSIC.get("fun"))
    if mixkit_url:
        try:
            music_path = _download_music(mixkit_url, mood)
            if music_path:
                print(f"   ✅ Got Mixkit music")
                return music_path
        except Exception as e:
            print(f"   ⚠️ Mixkit download failed: {e}")
    
    # Last resort: Use any cached music
    all_cached = list(MUSIC_DIR.glob("**/*.mp3"))
    valid_cached = [f for f in all_cached if f.stat().st_size > 50000]  # At least 50KB
    if valid_cached:
        chosen = random.choice(valid_cached)
        print(f"   ⚠️ Using fallback cached: {chosen.name}")
        return str(chosen)
    
    # NO GENERATED TONES - better to have no music than broken radio sound
    print("   ⚠️ No background music available (skipping - better than bad audio)")
    return None


def _get_cached_music(mood: str) -> Optional[str]:
    """Check for cached music files."""
    mood_dir = MUSIC_DIR / mood
    if mood_dir.exists():
        mp3_files = list(mood_dir.glob("*.mp3"))
        if mp3_files:
            # Only use files > 10KB (valid mp3)
            valid = [f for f in mp3_files if f.stat().st_size > 10000]
            if valid:
                return str(random.choice(valid))
    
    # Check general music folder
    mp3_files = list(MUSIC_DIR.glob("*.mp3"))
    valid = [f for f in mp3_files if f.stat().st_size > 10000]
    if valid:
        return str(random.choice(valid))
    
    return None


def _download_music(url: str, mood: str) -> Optional[str]:
    """Download and cache music file."""
    try:
        mood_dir = MUSIC_DIR / mood
        mood_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from URL
        filename = url.split("/")[-1].replace("%20", "_")
        if not filename.endswith(".mp3"):
            filename += ".mp3"
        
        music_path = mood_dir / filename
        
        # Check cache
        if music_path.exists() and music_path.stat().st_size > 10000:
            return str(music_path)
        
        # Download with timeout
        print(f"   🎵 Downloading: {filename}...")
        response = requests.get(url, timeout=30, stream=True, 
                               headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code != 200:
            print(f"   ⚠️ HTTP {response.status_code} for {url}")
            return None
        
        with open(music_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if music_path.exists() and music_path.stat().st_size > 10000:
            print(f"   ✅ Downloaded: {filename}")
            return str(music_path)
        else:
            # Delete invalid file
            if music_path.exists():
                music_path.unlink()
            return None
        
    except Exception as e:
        print(f"   ⚠️ Music download error: {e}")
        return None


def get_mood_for_question(option_a: str, option_b: str) -> str:
    """Determine the mood based on question content."""
    text = f"{option_a} {option_b}".lower()
    
    if any(word in text for word in ["money", "rich", "million", "billion", "wealthy", "salary"]):
        return "energetic"
    elif any(word in text for word in ["die", "death", "never", "forever", "scary", "horror", "ghost"]):
        return "dramatic"
    elif any(word in text for word in ["super", "power", "fly", "invisible", "magic", "teleport"]):
        return "fun"
    elif any(word in text for word in ["love", "relationship", "friend", "family", "date"]):
        return "chill"
    elif any(word in text for word in ["secret", "mystery", "hidden", "unknown"]):
        return "mystery"
    else:
        return "fun"


if __name__ == "__main__":
    # Test
    print("Testing background music fetcher...")
    for mood in ["fun", "dramatic", "energetic"]:
        print(f"\n--- Testing mood: {mood} ---")
        music = get_background_music(mood)
        print(f"Result: {music}")
