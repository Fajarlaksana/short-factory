#!/usr/bin/env python3
"""
ViralShorts Factory - Platform Safety & Anti-Ban System
=========================================================

COMPREHENSIVE MEASURES TO AVOID DETECTION AND BANS:

This module implements all the techniques needed to appear as a legitimate
content creator rather than an automated bot.

STRATEGIES IMPLEMENTED:
1. Random timing (already in workflow - 0-45 min delay)
2. Video fingerprinting (unique variations in each video)
3. Natural metadata variation
4. Upload pattern randomization
5. Content diversity requirements
6. Platform-specific optimizations
"""

import os
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path


# =============================================================================
# VIDEO SPECIFICATIONS BY PLATFORM
# =============================================================================

PLATFORM_SPECS = {
    "youtube_shorts": {
        "resolution": (1080, 1920),  # 9:16 aspect ratio
        "max_duration": 60,  # seconds
        "min_duration": 15,  # seconds (recommended for better reach)
        "fps": 30,  # frames per second
        "bitrate": "8M",  # 8 Mbps recommended
        "codec": "libx264",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "format": "mp4",
        "max_file_size": 256 * 1024 * 1024,  # 256 MB
    },
    "dailymotion": {
        "resolution": (1080, 1920),  # Vertical works
        "max_duration": 3600,  # 60 minutes
        "min_duration": 1,
        "fps": 30,
        "bitrate": "10M",
        "codec": "libx264",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "format": "mp4",
        "max_file_size": 4 * 1024 * 1024 * 1024,  # 4 GB
    },
    "tiktok": {
        "resolution": (1080, 1920),
        "max_duration": 180,  # 3 minutes
        "min_duration": 3,
        "fps": 30,
        "bitrate": "6M",
        "codec": "libx264",
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "format": "mp4",
        "max_file_size": 287 * 1024 * 1024,  # 287 MB
    }
}


# =============================================================================
# ANTI-BAN STRATEGIES
# =============================================================================

class AntiBanSystem:
    """
    Comprehensive anti-ban measures for automated content.
    
    Key Principles:
    1. NEVER look like a bot
    2. Vary EVERYTHING possible
    3. Respect platform limits
    4. Mimic human behavior patterns
    """
    
    def __init__(self):
        self.daily_upload_count = 0
        self.last_upload_time = None
        self.upload_history = []
        
        # Platform limits (conservative to be safe)
        self.platform_limits = {
            "youtube": {"daily": 10, "hourly": 2},  # Conservative limits
            "dailymotion": {"daily": 30, "hourly": 5},
            "tiktok": {"daily": 50, "hourly": 10},
        }
    
    # -------------------------------------------------------------------------
    # TIMING STRATEGIES
    # -------------------------------------------------------------------------
    
    def get_random_delay(self, min_seconds: int = 0, max_seconds: int = 2700) -> int:
        """
        Generate random delay to avoid predictable patterns.
        
        Default: 0-45 minutes (already implemented in workflow)
        """
        return random.randint(min_seconds, max_seconds)
    
    def get_optimal_upload_time(self) -> Dict:
        """
        Get optimal upload time based on human behavior patterns.
        
        Peak times (when humans upload):
        - Weekdays: 6-9 AM, 12-2 PM, 6-10 PM
        - Weekends: 9 AM - 11 PM
        
        We add randomness to mimic natural human variation.
        """
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        if is_weekend:
            # Weekend - more flexible hours
            peak_hours = list(range(9, 23))  # 9 AM to 11 PM
        else:
            # Weekday - office breaks and evening
            peak_hours = [7, 8, 12, 13, 18, 19, 20, 21]
        
        # Add some randomness (+/- 30 minutes)
        random_minutes = random.randint(-30, 30)
        
        return {
            "optimal_hour": random.choice(peak_hours),
            "random_offset_minutes": random_minutes,
            "is_weekend": is_weekend,
        }
    
    def should_upload_now(self, platform: str) -> Tuple[bool, str]:
        """
        Check if we should upload now or wait.
        
        Returns (should_upload, reason)
        """
        limits = self.platform_limits.get(platform, {"daily": 5, "hourly": 1})
        
        # Check daily limit
        if self.daily_upload_count >= limits["daily"]:
            return False, f"Daily limit reached ({limits['daily']} videos)"
        
        # Check hourly spacing (at least 20-40 minutes between uploads)
        if self.last_upload_time:
            min_gap = timedelta(minutes=random.randint(20, 40))
            if datetime.now() - self.last_upload_time < min_gap:
                return False, "Too soon since last upload"
        
        return True, "OK to upload"
    
    # -------------------------------------------------------------------------
    # VIDEO FINGERPRINTING (Make each video unique)
    # -------------------------------------------------------------------------
    
    def get_unique_video_variations(self) -> Dict:
        """
        Generate slight variations to make each video unique.
        
        This prevents detection of "duplicate" or "template" content.
        """
        return {
            # Slight color variations
            "brightness": random.uniform(0.95, 1.05),
            "contrast": random.uniform(0.95, 1.05),
            "saturation": random.uniform(0.95, 1.05),
            
            # Audio variations
            "volume": random.uniform(0.95, 1.0),
            "music_volume": random.uniform(0.10, 0.15),
            
            # Timing variations
            "intro_delay": random.uniform(0.1, 0.3),  # seconds
            "outro_delay": random.uniform(0.2, 0.5),
            
            # Visual variations
            "text_position_offset": (random.randint(-5, 5), random.randint(-5, 5)),
            "font_size_variation": random.randint(-2, 2),
        }
    
    def generate_unique_hash(self, content: str) -> str:
        """Generate unique identifier for tracking."""
        timestamp = datetime.now().isoformat()
        random_salt = str(random.randint(1000, 9999))
        return hashlib.md5(f"{content}{timestamp}{random_salt}".encode()).hexdigest()[:8]
    
    # -------------------------------------------------------------------------
    # METADATA VARIATION
    # -------------------------------------------------------------------------
    
    def generate_varied_title(self, base_title: str, variations: List[str] = None) -> str:
        """
        Generate title variations to avoid pattern detection.
        
        Uses AI-style variations while keeping the meaning.
        """
        # Add emojis randomly (different each time)
        emojis = ["🔥", "⚡", "🚀", "💡", "🎯", "✨", "🌟", "💪", "🧠", "⭐"]
        
        # Random formatting variations
        formats = [
            f"{base_title}",
            f"{random.choice(emojis)} {base_title}",
            f"{base_title} {random.choice(emojis)}",
            f"{random.choice(emojis)} {base_title} {random.choice(emojis)}",
        ]
        
        return random.choice(formats)
    
    def generate_varied_description(self, base_description: str) -> str:
        """
        Generate description variations.
        """
        # Add varied CTAs
        ctas = [
            "\n\n💬 Comment your thoughts below!",
            "\n\n👇 Drop a comment with your experience!",
            "\n\n🤔 What do you think? Let me know!",
            "\n\n📢 Share this with someone who needs to see it!",
            "\n\n⚡ Follow for more content like this!",
        ]
        
        # Add varied hashtag sets
        hashtag_sets = [
            "#shorts #viral #trending #fyp",
            "#shorts #facts #mindblown #amazing",
            "#shorts #lifehack #tips #motivation",
            "#shorts #psychology #brain #success",
            "#shorts #money #finance #wealth",
        ]
        
        return f"{base_description}{random.choice(ctas)}\n\n{random.choice(hashtag_sets)}"
    
    def generate_varied_tags(self, base_tags: List[str]) -> List[str]:
        """
        Generate tag variations.
        """
        # Core tags that should always be included
        core_tags = base_tags[:5]
        
        # Random additional tags
        additional = [
            "trending", "viral", "fyp", "foryou", "explore",
            "motivation", "inspiration", "facts", "knowledge",
            "lifehacks", "tips", "howto", "learn", "education"
        ]
        
        # Mix it up
        random.shuffle(additional)
        varied_tags = core_tags + random.sample(additional, 5)
        
        return list(set(varied_tags))  # Remove duplicates
    
    # -------------------------------------------------------------------------
    # CONTENT DIVERSITY
    # -------------------------------------------------------------------------
    
    def ensure_content_diversity(self, recent_topics: List[str], new_topic: str) -> bool:
        """
        Ensure we're not uploading too similar content.
        
        Returns True if the new topic is diverse enough.
        """
        if not recent_topics:
            return True
        
        # Simple check: topic shouldn't be identical to recent ones
        if new_topic.lower() in [t.lower() for t in recent_topics[-5:]]:
            return False
        
        return True
    
    # -------------------------------------------------------------------------
    # UPLOAD TRACKING
    # -------------------------------------------------------------------------
    
    def record_upload(self, platform: str, video_id: str, title: str):
        """Record an upload for tracking and limits."""
        self.daily_upload_count += 1
        self.last_upload_time = datetime.now()
        self.upload_history.append({
            "platform": platform,
            "video_id": video_id,
            "title": title,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_daily_stats(self) -> Dict:
        """Get today's upload statistics."""
        return {
            "uploads_today": self.daily_upload_count,
            "last_upload": self.last_upload_time.isoformat() if self.last_upload_time else None,
            "history": self.upload_history[-10:],  # Last 10 uploads
        }


# =============================================================================
# VIDEO SPECIFICATION VALIDATOR
# =============================================================================

def validate_video_specs(video_path: str, platform: str = "youtube_shorts") -> Dict:
    """
    Validate that a video meets platform specifications.
    
    Returns dict with validation results and any issues.
    """
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["youtube_shorts"])
    issues = []
    
    path = Path(video_path)
    if not path.exists():
        return {"valid": False, "issues": ["File not found"]}
    
    # Check file size
    file_size = path.stat().st_size
    if file_size > specs["max_file_size"]:
        issues.append(f"File too large: {file_size / (1024*1024):.1f}MB > {specs['max_file_size'] / (1024*1024):.1f}MB")
    
    # Try to get video info using ffprobe (if available)
    try:
        import subprocess
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            # Check duration
            duration = float(info.get("format", {}).get("duration", 0))
            if duration > specs["max_duration"]:
                issues.append(f"Video too long: {duration:.1f}s > {specs['max_duration']}s")
            if duration < specs["min_duration"]:
                issues.append(f"Video too short: {duration:.1f}s < {specs['min_duration']}s")
            
            # Check resolution
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = stream.get("width", 0)
                    height = stream.get("height", 0)
                    expected_w, expected_h = specs["resolution"]
                    
                    if width != expected_w or height != expected_h:
                        issues.append(f"Resolution mismatch: {width}x{height} vs {expected_w}x{expected_h}")
                    
                    # Check FPS
                    fps_str = stream.get("r_frame_rate", "0/1")
                    fps = eval(fps_str) if "/" in fps_str else float(fps_str)
                    if abs(fps - specs["fps"]) > 1:
                        issues.append(f"FPS mismatch: {fps:.1f} vs {specs['fps']}")
    except FileNotFoundError:
        # ffprobe not available - skip detailed checks
        pass
    except Exception as e:
        issues.append(f"Validation error: {str(e)}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "platform": platform,
        "file_size_mb": file_size / (1024 * 1024),
    }


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'PLATFORM_SPECS',
    'AntiBanSystem',
    'validate_video_specs',
]


if __name__ == "__main__":
    print("=" * 60)
    print("🛡️ Platform Safety & Anti-Ban System")
    print("=" * 60)
    
    system = AntiBanSystem()
    
    print("\n📋 Platform Specifications:")
    for platform, specs in PLATFORM_SPECS.items():
        print(f"\n{platform}:")
        print(f"   Resolution: {specs['resolution'][0]}x{specs['resolution'][1]}")
        print(f"   Max Duration: {specs['max_duration']}s")
        print(f"   FPS: {specs['fps']}")
        print(f"   Max File Size: {specs['max_file_size'] / (1024*1024):.0f} MB")
    
    print("\n🎲 Random Variations Example:")
    variations = system.get_unique_video_variations()
    for key, value in variations.items():
        print(f"   {key}: {value}")
    
    print("\n📝 Title Variations:")
    base_title = "Your Brain is Lying to You"
    for _ in range(3):
        print(f"   {system.generate_varied_title(base_title)}")
    
    print("\n⏰ Optimal Upload Time:")
    timing = system.get_optimal_upload_time()
    print(f"   Hour: {timing['optimal_hour']}:00 (offset: {timing['random_offset_minutes']} min)")








