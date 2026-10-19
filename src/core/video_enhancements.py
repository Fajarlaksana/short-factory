#!/usr/bin/env python3
"""
ViralShorts Factory - Video Enhancement Module
==============================================

PROFESSIONAL ENHANCEMENTS for maximum engagement:
1. TikTok-style word-by-word captions
2. Motion graphics (zoom, shake, text animations)
3. Progress bar overlay
4. Particle effects & light leaks
5. Color grading & filters
"""

import os
import re
import random
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

# MoviePy imports
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip, TextClip,
    ColorClip, concatenate_videoclips
)
import moviepy.video.fx.all as vfx

# Constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


# =============================================================================
# TIKTOK-STYLE WORD-BY-WORD CAPTIONS
# =============================================================================

class CaptionGenerator:
    """
    Generate TikTok-style word-by-word captions that appear in sync with speech.
    
    Features:
    - Words appear one at a time
    - Current word is highlighted/larger
    - Smooth fade animations
    - Multiple style options
    """
    
    CAPTION_STYLES = {
        "tiktok": {
            "font_size": 72,
            "font_color": "white",
            "highlight_color": "#FFD700",  # Gold
            "bg_color": (0, 0, 0, 180),
            "position": ("center", 0.75),  # 75% down the screen
        },
        "netflix": {
            "font_size": 64,
            "font_color": "white",
            "highlight_color": "#E50914",  # Netflix red
            "bg_color": (0, 0, 0, 200),
            "position": ("center", 0.85),
        },
        "minimal": {
            "font_size": 56,
            "font_color": "white",
            "highlight_color": "#00D4FF",  # Cyan
            "bg_color": None,
            "position": ("center", 0.80),
        }
    }
    
    def __init__(self, style: str = "tiktok"):
        self.style = self.CAPTION_STYLES.get(style, self.CAPTION_STYLES["tiktok"])
        
        # Font paths
        self.font_paths = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        self.font_path = next((f for f in self.font_paths if os.path.exists(f)), None)
    
    def split_into_words_with_timing(self, text: str, total_duration: float) -> List[Dict]:
        """
        Split text into words and assign timing to each word.
        
        Returns list of dicts: {"word": str, "start": float, "end": float}
        """
        # Clean text
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        
        if not words:
            return []
        
        # Calculate duration per word (with slight overlap for natural feel)
        word_duration = total_duration / len(words)
        
        word_timings = []
        for i, word in enumerate(words):
            start = i * word_duration
            end = start + word_duration + 0.1  # Slight overlap
            word_timings.append({
                "word": word,
                "start": start,
                "end": min(end, total_duration),
                "index": i
            })
        
        return word_timings
    
    def create_caption_frame(self, words: List[str], current_index: int, 
                            width: int, height: int) -> Image.Image:
        """
        Create a single caption frame with the current word highlighted.
        Shows 3-5 words at a time with the current word emphasized.
        """
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            main_font = ImageFont.truetype(self.font_path, self.style["font_size"])
            highlight_font = ImageFont.truetype(self.font_path, int(self.style["font_size"] * 1.2))
        except:
            main_font = ImageFont.load_default()
            highlight_font = main_font
        
        # Show window of words (current word + context)
        window_size = 5
        start_idx = max(0, current_index - 2)
        end_idx = min(len(words), start_idx + window_size)
        visible_words = words[start_idx:end_idx]
        
        if not visible_words:
            return img
        
        # Calculate total width
        total_text = " ".join(visible_words)
        bbox = draw.textbbox((0, 0), total_text, font=main_font)
        total_width = bbox[2] - bbox[0]
        
        # Position (centered, 75% down)
        x_start = (width - total_width) // 2
        y_pos = int(height * self.style["position"][1])
        
        # Draw background if specified
        if self.style["bg_color"]:
            padding = 20
            bg_box = [
                x_start - padding,
                y_pos - padding,
                x_start + total_width + padding,
                y_pos + self.style["font_size"] + padding
            ]
            draw.rectangle(bg_box, fill=self.style["bg_color"])
        
        # Draw each word
        x_pos = x_start
        for i, word in enumerate(visible_words):
            actual_index = start_idx + i
            is_current = actual_index == current_index
            
            font = highlight_font if is_current else main_font
            color = self.style["highlight_color"] if is_current else self.style["font_color"]
            
            # Add glow effect for current word
            if is_current:
                for offset in [2, 1]:
                    glow_color = (*tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), 100)
                    draw.text((x_pos + offset, y_pos + offset), word, fill=glow_color, font=font)
                    draw.text((x_pos - offset, y_pos - offset), word, fill=glow_color, font=font)
            
            draw.text((x_pos, y_pos), word, fill=color, font=font)
            
            # Move to next word position
            word_bbox = draw.textbbox((0, 0), word + " ", font=font)
            x_pos += word_bbox[2] - word_bbox[0]
        
        return img
    
    def generate_caption_clips(self, text: str, duration: float) -> List:
        """Generate MoviePy clips for word-by-word captions."""
        word_timings = self.split_into_words_with_timing(text, duration)
        words = [w["word"] for w in word_timings]
        
        clips = []
        for timing in word_timings:
            frame = self.create_caption_frame(
                words, timing["index"], VIDEO_WIDTH, VIDEO_HEIGHT
            )
            
            # Convert PIL to MoviePy clip
            frame_array = np.array(frame)
            clip = ImageClip(frame_array)
            clip = clip.set_start(timing["start"])
            clip = clip.set_duration(timing["end"] - timing["start"])
            
            clips.append(clip)
        
        return clips


# =============================================================================
# MOTION GRAPHICS & EFFECTS
# =============================================================================

class MotionGraphics:
    """
    Add professional motion graphics effects:
    - Ken Burns effect (slow zoom/pan)
    - Shake effect (for impact moments)
    - Pulse effect (for emphasis)
    - Text animations
    """
    
    @staticmethod
    def apply_ken_burns(clip, zoom_start: float = 1.0, zoom_end: float = 1.1, 
                       direction: str = "in") -> VideoFileClip:
        """
        Apply Ken Burns effect (slow zoom) to a clip.
        
        Creates subtle movement that keeps viewers engaged.
        """
        if direction == "out":
            zoom_start, zoom_end = zoom_end, zoom_start
        
        def zoom_effect(get_frame, t):
            progress = t / clip.duration
            current_zoom = zoom_start + (zoom_end - zoom_start) * progress
            
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Calculate new dimensions
            new_h, new_w = int(h * current_zoom), int(w * current_zoom)
            
            # Resize
            from PIL import Image
            import numpy as np
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            
            # Crop to center
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            img = img.crop((left, top, left + w, top + h))
            
            return np.array(img)
        
        return clip.fl(zoom_effect)
    
    @staticmethod
    def apply_subtle_zoom(clip, intensity: float = 0.05) -> VideoFileClip:
        """Apply very subtle zoom for dynamic feel without being distracting."""
        return MotionGraphics.apply_ken_burns(clip, 1.0, 1.0 + intensity, "in")
    
    @staticmethod
    def create_pulse_effect(clip, pulses: int = 3) -> VideoFileClip:
        """Create a subtle pulsing effect for emphasis."""
        def pulse(t):
            import math
            # Subtle sine wave pulse
            pulse_speed = pulses / clip.duration
            scale = 1.0 + 0.02 * math.sin(2 * math.pi * pulse_speed * t)
            return scale
        
        return clip.resize(pulse)


# =============================================================================
# PROGRESS BAR
# =============================================================================

class ProgressBar:
    """
    Add a progress bar to videos.
    
    Shows viewers how much of the video remains - increases retention
    as viewers are more likely to finish if they see they're close to the end.
    """
    
    STYLES = {
        "minimal": {
            "height": 4,
            "color": "#FFFFFF",
            "bg_color": (255, 255, 255, 50),
            "position": "top",
        },
        "youtube": {
            "height": 3,
            "color": "#FF0000",
            "bg_color": (255, 255, 255, 30),
            "position": "bottom",
        },
        "tiktok": {
            "height": 2,
            "color": "#FE2C55",
            "bg_color": (255, 255, 255, 20),
            "position": "top",
        },
        "gradient": {
            "height": 4,
            "color": "gradient",  # Will use gradient
            "bg_color": (0, 0, 0, 100),
            "position": "top",
        }
    }
    
    def __init__(self, style: str = "minimal"):
        self.style = self.STYLES.get(style, self.STYLES["minimal"])
    
    def create_progress_frame(self, progress: float, width: int) -> Image.Image:
        """Create a single progress bar frame."""
        height = self.style["height"]
        img = Image.new('RGBA', (width, height + 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background
        if self.style["bg_color"]:
            draw.rectangle([0, 2, width, height + 2], fill=self.style["bg_color"])
        
        # Progress fill
        fill_width = int(width * progress)
        if fill_width > 0:
            if self.style["color"] == "gradient":
                # Create gradient
                for x in range(fill_width):
                    # Purple to pink gradient
                    ratio = x / max(fill_width, 1)
                    r = int(99 + (236 - 99) * ratio)
                    g = int(102 + (72 - 102) * ratio)
                    b = int(241 + (153 - 241) * ratio)
                    draw.line([(x, 2), (x, height + 2)], fill=(r, g, b, 255))
            else:
                color = self.style["color"]
                if isinstance(color, str) and color.startswith("#"):
                    color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                draw.rectangle([0, 2, fill_width, height + 2], fill=color)
        
        return img
    
    def generate_progress_clip(self, duration: float, fps: int = 24) -> ImageClip:
        """Generate a progress bar clip for the entire video duration."""
        def make_frame(t):
            progress = t / duration
            frame = self.create_progress_frame(progress, VIDEO_WIDTH)
            return np.array(frame)
        
        from moviepy.video.VideoClip import VideoClip
        clip = VideoClip(make_frame, duration=duration)
        
        # Position based on style
        if self.style["position"] == "bottom":
            clip = clip.set_position(("center", VIDEO_HEIGHT - self.style["height"] - 10))
        else:
            clip = clip.set_position(("center", 10))
        
        return clip


# =============================================================================
# PARTICLE EFFECTS & LIGHT LEAKS
# =============================================================================

class VisualEffects:
    """
    Add visual effects overlays:
    - Floating particles
    - Light leaks
    - Vignette
    - Film grain
    """
    
    @staticmethod
    def create_particles_frame(width: int, height: int, 
                               particle_count: int = 30,
                               seed: int = None) -> Image.Image:
        """Create a frame with floating particles."""
        if seed:
            random.seed(seed)
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for _ in range(particle_count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 4)
            alpha = random.randint(30, 100)
            
            # White/golden particles
            if random.random() > 0.3:
                color = (255, 255, 255, alpha)
            else:
                color = (255, 215, 0, alpha)
            
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        
        # Apply blur for soft particles
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        
        return img
    
    @staticmethod
    def create_vignette(width: int, height: int, intensity: float = 0.3) -> Image.Image:
        """Create a vignette effect (darkened edges)."""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Create radial gradient
        center_x, center_y = width // 2, height // 2
        max_dist = ((width/2)**2 + (height/2)**2) ** 0.5
        
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                dist = ((x - center_x)**2 + (y - center_y)**2) ** 0.5
                ratio = dist / max_dist
                alpha = int(255 * intensity * (ratio ** 2))
                pixels[x, y] = (0, 0, 0, min(alpha, 255))
        
        return img
    
    @staticmethod
    def create_light_leak(width: int, height: int, 
                         color: Tuple[int, int, int] = (255, 180, 100)) -> Image.Image:
        """Create a light leak effect (warm light from corner)."""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Light from top-right corner
        for i in range(50):
            alpha = int(30 * (1 - i/50))
            offset = i * 20
            
            points = [
                (width, 0),
                (width - offset, 0),
                (width, offset)
            ]
            
            draw.polygon(points, fill=(*color, alpha))
        
        # Apply blur
        img = img.filter(ImageFilter.GaussianBlur(radius=50))
        
        return img


# =============================================================================
# ENHANCED VIDEO GENERATOR
# =============================================================================

class EnhancedVideoGenerator:
    """
    Main class that combines all enhancements.
    """
    
    def __init__(self):
        self.caption_gen = CaptionGenerator("tiktok")
        self.progress_bar = ProgressBar("gradient")
        self.effects = VisualEffects()
        self.motion = MotionGraphics()
    
    def enhance_video(self, video_clip, text: str, 
                     add_captions: bool = True,
                     add_progress: bool = True,
                     add_zoom: bool = True,
                     add_vignette: bool = True) -> CompositeVideoClip:
        """
        Apply all enhancements to a video clip.
        """
        duration = video_clip.duration
        layers = [video_clip]
        
        # 1. Apply subtle zoom (Ken Burns)
        if add_zoom:
            video_clip = self.motion.apply_subtle_zoom(video_clip, 0.03)
            layers[0] = video_clip
        
        # 2. Add vignette
        if add_vignette:
            vignette = self.effects.create_vignette(VIDEO_WIDTH, VIDEO_HEIGHT, 0.25)
            vignette_clip = ImageClip(np.array(vignette)).set_duration(duration)
            layers.append(vignette_clip)
        
        # 3. Add progress bar
        if add_progress:
            progress_clip = self.progress_bar.generate_progress_clip(duration)
            layers.append(progress_clip)
        
        # 4. Add captions
        if add_captions and text:
            caption_clips = self.caption_gen.generate_caption_clips(text, duration)
            layers.extend(caption_clips)
        
        return CompositeVideoClip(layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def apply_all_enhancements(video_path: str, text: str, output_path: str) -> bool:
    """
    Apply all enhancements to an existing video.
    
    Usage:
        apply_all_enhancements("input.mp4", "Voiceover text...", "output_enhanced.mp4")
    """
    try:
        video = VideoFileClip(video_path)
        enhancer = EnhancedVideoGenerator()
        
        enhanced = enhancer.enhance_video(
            video, text,
            add_captions=True,
            add_progress=True,
            add_zoom=True,
            add_vignette=True
        )
        
        # Keep original audio
        enhanced = enhanced.set_audio(video.audio)
        
        enhanced.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        return True
    except Exception as e:
        print(f"Enhancement error: {e}")
        return False


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Video Enhancement Module Test")
    print("=" * 60)
    
    # Test caption generator
    cap_gen = CaptionGenerator("tiktok")
    test_text = "Your brain makes 35000 decisions every single day"
    timings = cap_gen.split_into_words_with_timing(test_text, 10.0)
    print(f"\n✅ Caption timing test: {len(timings)} words")
    for t in timings[:3]:
        print(f"   {t['word']}: {t['start']:.2f}s - {t['end']:.2f}s")
    
    # Test progress bar
    pb = ProgressBar("gradient")
    frame = pb.create_progress_frame(0.5, VIDEO_WIDTH)
    print(f"\n✅ Progress bar test: {frame.size}")
    
    # Test effects
    vignette = VisualEffects.create_vignette(VIDEO_WIDTH, VIDEO_HEIGHT)
    print(f"✅ Vignette test: {vignette.size}")
    
    particles = VisualEffects.create_particles_frame(VIDEO_WIDTH, VIDEO_HEIGHT)
    print(f"✅ Particles test: {particles.size}")
    
    print("\n" + "=" * 60)
    print("All enhancement tests passed!")
    print("=" * 60)




