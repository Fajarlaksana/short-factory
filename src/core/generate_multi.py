#!/usr/bin/env python3
"""
ViralShorts Factory - Multi-Type Video Generator
Generates various types of viral content videos.

Usage:
    python generate_multi.py --type scary_facts --count 1
    python generate_multi.py --type money_facts --count 2
    python generate_multi.py --type ai_quotes --count 1
    python generate_multi.py --type kids --count 1
    python generate_multi.py --type random --count 3  # Mix of types
"""

import os
import sys
import asyncio
import argparse
import random
from pathlib import Path
from typing import Dict, List, Optional

# Import our modules
from video_types import (
    VideoType, VideoContent, MultiTypeContentGenerator,
    get_weighted_random_type, VIDEO_TYPE_WEIGHTS
)

# Import core generation components from script_v2
try:
    from script_v2 import (
        generate_voiceover_v2, create_gradient_background,
        create_option_panel_image, create_vs_badge, create_cta_text,
        create_percentage_reveal_frame, pil_to_moviepy_clip,
        get_multiple_broll_clips, VIDEO_WIDTH, VIDEO_HEIGHT,
        THEMES, VideoTheme
    )
    HAS_V2 = True
except ImportError as e:
    print(f"⚠️ Could not import script_v2: {e}")
    HAS_V2 = False

from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, CompositeAudioClip
)
import moviepy.video.fx.all as vfx

from PIL import Image, ImageDraw, ImageFont

# Import background music
try:
    from background_music import get_background_music
    HAS_MUSIC = True
except ImportError:
    HAS_MUSIC = False
    print("⚠️ Background music module not available")

# Import AI trend detector
try:
    from ai_trend_detector import get_ai_suggested_video, get_multiple_ai_suggestions, TrendingTopic
    HAS_AI_TRENDS = True
except ImportError:
    HAS_AI_TRENDS = False

# Import master prompts
try:
    from master_prompts import MasterContentGenerator, strip_emojis as strip_emojis_master
    HAS_MASTER = True
except ImportError:
    HAS_MASTER = False

# Import DYNAMIC video generator (per-phrase B-roll!)
try:
    from dynamic_video_generator import DynamicVideoGenerator
    HAS_DYNAMIC_GEN = True
    print("✅ DynamicVideoGenerator loaded - per-phrase B-roll enabled!")
except ImportError as e:
    HAS_DYNAMIC_GEN = False
    print(f"⚠️ DynamicVideoGenerator not available: {e}")

# Import VIRAL OPTIMIZER (AI-powered titles, hashtags, SEO)
try:
    from viral_optimizer import ViralOptimizer, generate_viral_title_ai
    HAS_VIRAL_OPT = True
    print("✅ ViralOptimizer loaded - AI titles/hashtags enabled!")
except ImportError as e:
    HAS_VIRAL_OPT = False
    print(f"⚠️ ViralOptimizer not available: {e}")

# Import AI EVALUATOR (content quality check before generation)
try:
    from ai_evaluator import AIEvaluator
    HAS_EVALUATOR = True
    print("✅ AIEvaluator loaded - quality checks enabled!")
except ImportError as e:
    HAS_EVALUATOR = False
    print(f"⚠️ AIEvaluator not available: {e}")

# Import VALUE DELIVERY checker
try:
    from viral_video_science import ValueDeliveryChecker
    HAS_VALUE_CHECK = True
    print("✅ ValueDeliveryChecker loaded - empty promise detection enabled!")
except ImportError as e:
    HAS_VALUE_CHECK = False
    print(f"⚠️ ValueDeliveryChecker not available: {e}")

# Import PLATFORM SAFETY (anti-ban measures)
try:
    from platform_safety import AntiBanSystem, PLATFORM_SPECS
    HAS_ANTI_BAN = True
    print("✅ AntiBanSystem loaded - anti-ban measures enabled!")
except ImportError as e:
    HAS_ANTI_BAN = False
    print(f"⚠️ AntiBanSystem not available: {e}")

# Import ANALYTICS FEEDBACK (learning from views)
try:
    from analytics_feedback import FeedbackLoopController
    HAS_ANALYTICS = True
    print("✅ FeedbackLoopController loaded - learning enabled!")
except ImportError as e:
    HAS_ANALYTICS = False
    print(f"⚠️ FeedbackLoopController not available: {e}")


# Output directory
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Type-Specific Generators
# =============================================================================

async def generate_fact_video(content: VideoContent, output_path: str) -> bool:
    """
    Generate a fact-based video (scary facts, money facts, psychology facts, life hacks).
    
    USES DYNAMIC VIDEO GENERATOR for:
    - Per-phrase B-roll changes (more engaging!)
    - AI-generated B-roll keywords for each phrase
    - Smooth transitions between segments
    """
    print(f"\n🎬 Generating {content.video_type.value} video...")
    print(f"   Hook: {content.hook}")
    print(f"   Content: {content.main_text[:50]}...")
    
    # =========================================================================
    # USE DYNAMIC VIDEO GENERATOR (per-phrase B-roll!)
    # =========================================================================
    if HAS_DYNAMIC_GEN:
        try:
            print("   🎯 Using DynamicVideoGenerator (per-phrase B-roll!)")
            
            # Prepare topic dict for dynamic generator
            topic = {
                "hook": content.hook,
                "content": content.main_text,
                "video_type": content.video_type.value,
                "broll_keywords": content.broll_keywords or [],
                "music_mood": content.music_mood or "suspense",
                "call_to_action": content.call_to_action or "Follow for more!"
            }
            
            # Create dynamic generator and generate
            video_gen = DynamicVideoGenerator()
            success = await video_gen.generate_dynamic_video(topic, output_path)
            
            if success:
                print(f"   ✅ Generated with per-phrase B-roll: {output_path}")
                return True
            else:
                print("   ⚠️ Dynamic generator failed, falling back to basic...")
        except Exception as e:
            print(f"   ⚠️ Dynamic generator error: {e}, falling back to basic...")
            import traceback
            traceback.print_exc()
    
    # =========================================================================
    # FALLBACK: Basic generation (if dynamic fails)
    # =========================================================================
    try:
        themes_list = list(THEMES.values())
        
        if content.video_type == VideoType.SCARY_FACTS:
            theme = next((t for t in themes_list if "night" in t.name.lower()), random.choice(themes_list))
        elif content.video_type == VideoType.MONEY_FACTS:
            theme = next((t for t in themes_list if "gold" in t.name.lower() or "sunset" in t.name.lower()), random.choice(themes_list))
        else:
            theme = random.choice(themes_list)
        
        print(f"   🎨 Theme: {theme.name} (fallback mode)")
        
        voiceover_path = OUTPUT_DIR / "temp_vo.mp3"
        duration = await generate_voiceover_v2(content.voiceover_script, str(voiceover_path))
        total_duration = max(duration + 5, 15)
        
        if content.broll_keywords and len(content.broll_keywords) >= 3:
            broll_clips = get_multiple_broll_clips(
                {"option_a": " ".join(content.broll_keywords), "option_b": ""},
                count=3
            )
        else:
            broll_clips = get_multiple_broll_clips(
                {"option_a": content.main_text, "option_b": ""},
                count=3
            )
        
        if broll_clips:
            processed = []
            for clip_path in broll_clips[:3]:
                if os.path.exists(clip_path):
                    clip = VideoFileClip(clip_path)
                    clip = clip.resize((VIDEO_WIDTH, VIDEO_HEIGHT))
                    if processed:
                        clip = clip.crossfadein(0.5)
                    processed.append(clip)
            
            if processed:
                if processed[0].duration >= total_duration:
                    bg_clip = processed[0].subclip(0, total_duration)
                else:
                    bg_clip = concatenate_videoclips(processed, method="compose", padding=-0.5)
                    if bg_clip.duration < total_duration:
                        bg_clip = processed[0].loop(duration=total_duration)
                    bg_clip = bg_clip.subclip(0, total_duration)
                bg_clip = bg_clip.fx(vfx.colorx, 0.5)
            else:
                bg_clip = None
        else:
            bg_clip = None
        
        if bg_clip is None:
            gradient_img = create_gradient_background(VIDEO_WIDTH, VIDEO_HEIGHT, theme.background_gradient)
            bg_clip = pil_to_moviepy_clip(gradient_img, total_duration)
        
        hook_img = create_fact_overlay(content.hook, VIDEO_WIDTH, 200, theme, "hook")
        fact_img = create_fact_overlay(content.main_text, VIDEO_WIDTH, 600, theme, "fact")
        source_img = create_fact_overlay(content.secondary_text or "", VIDEO_WIDTH, 100, theme, "source")
        
        hook_clip = pil_to_moviepy_clip(hook_img, 3).set_position(('center', 100)).set_start(0)
        fact_clip = pil_to_moviepy_clip(fact_img, total_duration - 3).set_position(('center', 'center')).set_start(3)
        source_clip = pil_to_moviepy_clip(source_img, 3).set_position(('center', VIDEO_HEIGHT - 200)).set_start(total_duration - 3)
        
        vo_clip = AudioFileClip(str(voiceover_path))
        
        music_clip = None
        if HAS_MUSIC:
            music_path = get_background_music(content.music_mood)
            if music_path and os.path.exists(music_path):
                try:
                    music_clip = AudioFileClip(music_path)
                    music_clip = music_clip.volumex(0.15)
                except Exception:
                    pass
        
        video = CompositeVideoClip([bg_clip, hook_clip, fact_clip, source_clip], size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        actual_duration = min(total_duration, vo_clip.duration + 3)
        video = video.set_duration(actual_duration)
        
        if music_clip:
            if music_clip.duration < actual_duration:
                music_clip = music_clip.loop(duration=actual_duration)
            music_clip = music_clip.subclip(0, actual_duration)
            final_audio = CompositeAudioClip([
                vo_clip.set_duration(min(vo_clip.duration, actual_duration)),
                music_clip
            ])
            video = video.set_audio(final_audio)
        else:
            video = video.set_audio(vo_clip.set_duration(min(vo_clip.duration, actual_duration)))
        
        video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)
        print(f"   ✅ Generated (fallback): {output_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def generate_quote_video(content: VideoContent, output_path: str) -> bool:
    """Generate a quote/motivational video."""
    print(f"\n🎬 Generating quote video...")
    print(f"   Quote: {content.main_text[:50]}...")
    
    try:
        themes_list = list(THEMES.values())
        theme = random.choice(themes_list)
        
        # Generate voiceover
        voiceover_path = OUTPUT_DIR / "temp_vo.mp3"
        duration = await generate_voiceover_v2(content.voiceover_script, str(voiceover_path))
        
        total_duration = max(duration + 3, 12)
        
        # Get calming B-roll
        broll_clips = get_multiple_broll_clips(
            {"option_a": " ".join(content.broll_keywords or ["nature", "calm"]), "option_b": ""},
            count=2
        )
        
        # Create background
        if broll_clips and os.path.exists(broll_clips[0]):
            bg_clip = VideoFileClip(broll_clips[0])
            bg_clip = bg_clip.resize((VIDEO_WIDTH, VIDEO_HEIGHT))
            if bg_clip.duration < total_duration:
                bg_clip = bg_clip.loop(n=int(total_duration / bg_clip.duration) + 1)
            bg_clip = bg_clip.subclip(0, total_duration)
            bg_clip = bg_clip.fx(vfx.colorx, 0.6)
        else:
            gradient_img = create_gradient_background(VIDEO_WIDTH, VIDEO_HEIGHT, theme.background_gradient)
            bg_clip = pil_to_moviepy_clip(gradient_img, total_duration)
        
        # Create quote text
        quote_img = create_quote_overlay(content.main_text, content.secondary_text or "", VIDEO_WIDTH, VIDEO_HEIGHT)
        quote_clip = pil_to_moviepy_clip(quote_img, total_duration).set_position('center')
        
        # Hook
        hook_img = create_fact_overlay(content.hook, VIDEO_WIDTH, 150, theme, "hook")
        hook_clip = pil_to_moviepy_clip(hook_img, 2).set_position(('center', 50)).set_start(0)
        
        # Compose
        vo_clip = AudioFileClip(str(voiceover_path))
        
        # Get background music
        music_clip = None
        if HAS_MUSIC:
            music_path = get_background_music("inspirational")
            if music_path and os.path.exists(music_path):
                try:
                    music_clip = AudioFileClip(music_path)
                    music_clip = music_clip.volumex(0.15)
                    print(f"   🎵 Added inspirational music")
                except Exception as e:
                    print(f"   ⚠️ Music error: {e}")
        
        video = CompositeVideoClip([
            bg_clip,
            quote_clip,
            hook_clip,
        ], size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        
        # Set duration to match voiceover
        actual_duration = min(total_duration, vo_clip.duration + 3)
        video = video.set_duration(actual_duration)
        
        # Mix audio
        if music_clip:
            if music_clip.duration < actual_duration:
                music_clip = music_clip.loop(duration=actual_duration)
            music_clip = music_clip.subclip(0, actual_duration)
            final_audio = CompositeAudioClip([
                vo_clip.set_duration(min(vo_clip.duration, actual_duration)),
                music_clip
            ])
            video = video.set_audio(final_audio)
        else:
            video = video.set_audio(vo_clip.set_duration(min(vo_clip.duration, actual_duration)))
        
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=4
        )
        
        print(f"   ✅ Generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# =============================================================================
# Helper Functions
# =============================================================================

def strip_emojis(text: str) -> str:
    """Remove emojis from text to avoid rendering issues."""
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()


def create_fact_overlay(text: str, width: int, height: int, 
                        theme: VideoTheme, style: str = "fact") -> Image.Image:
    """Create MODERN text overlay for facts with effects."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Strip emojis to avoid square symbols
    text = strip_emojis(text)
    
    # Load MODERN fonts - prioritize bold, impactful fonts
    try:
        # Modern font priority list (most impactful first)
        font_candidates = [
            "C:/Windows/Fonts/impact.ttf",       # Bold, impactful
            "C:/Windows/Fonts/BAUHS93.TTF",      # Bauhaus - modern
            "C:/Windows/Fonts/GOTHIC.TTF",       # Century Gothic
            "C:/Windows/Fonts/seguibl.ttf",      # Segoe UI Black
            "C:/Windows/Fonts/arialbd.ttf",      # Fallback
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        font_path = next((f for f in font_candidates if os.path.exists(f)), None)
        
        if style == "hook":
            font_size = 56  # Bigger for hooks
        elif style == "source":
            font_size = 28
        else:
            font_size = 44
            
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Word wrap
    words = text.split()
    lines = []
    current_line = []
    max_width = width - 80
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    
    # Draw text with MODERN effects (multiple shadows for glow)
    y = 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        
        # Outer glow (multiple layers for blur effect)
        glow_color = theme.option_a_gradient[0] if style == "hook" else (100, 200, 255)
        for offset in [5, 4, 3]:
            alpha = 40 + (5 - offset) * 20
            draw.text((x + offset, y + offset), line, fill=(*glow_color, alpha), font=font)
            draw.text((x - offset, y - offset), line, fill=(*glow_color, alpha), font=font)
            draw.text((x + offset, y - offset), line, fill=(*glow_color, alpha), font=font)
            draw.text((x - offset, y + offset), line, fill=(*glow_color, alpha), font=font)
        
        # Dark shadow for depth
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 200), font=font)
        
        # Main text (bright white or accent color)
        if style == "hook":
            color = (255, 100, 150)  # Pink/red for hooks - attention grabbing
        else:
            color = (255, 255, 255)
        draw.text((x, y), line, fill=(*color, 255), font=font)
        
        y += bbox[3] - bbox[1] + 15  # More spacing
    
    return img


def create_quote_overlay(quote: str, author: str, width: int, height: int) -> Image.Image:
    """Create a MODERN, beautiful quote overlay."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Strip emojis
    quote = strip_emojis(quote)
    author = strip_emojis(author)
    
    try:
        # Modern font choices
        font_candidates = [
            "C:/Windows/Fonts/GOTHICB.TTF",   # Century Gothic Bold
            "C:/Windows/Fonts/BAUHS93.TTF",   # Bauhaus
            "C:/Windows/Fonts/seguibl.ttf",   # Segoe UI Black
            "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
        font_path = next((f for f in font_candidates if os.path.exists(f)), None)
        font_quote = ImageFont.truetype(font_path, 50) if font_path else ImageFont.load_default()
        font_author = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    except:
        font_quote = ImageFont.load_default()
        font_author = ImageFont.load_default()
    
    # Word wrap quote
    words = quote.split()
    lines = []
    current_line = []
    max_width = width - 100
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_quote)
        if bbox[2] - bbox[0] > max_width:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    
    # Calculate total height
    line_height = 60
    total_text_height = len(lines) * line_height + 50
    start_y = (height - total_text_height) // 2
    
    # Draw quote marks
    draw.text((50, start_y - 80), '"', fill=(255, 255, 255, 100), font=font_quote)
    
    # Draw lines
    y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        x = (width - (bbox[2] - bbox[0])) // 2
        
        # Shadow
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 150), font=font_quote)
        draw.text((x, y), line, fill=(255, 255, 255, 255), font=font_quote)
        
        y += line_height
    
    # Draw author
    if author:
        bbox = draw.textbbox((0, 0), author, font=font_author)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x + 2, y + 22), author, fill=(0, 0, 0, 150), font=font_author)
        draw.text((x, y + 20), author, fill=(200, 200, 200, 255), font=font_author)
    
    return img


# =============================================================================
# Main
# =============================================================================

async def generate_from_ai_topic(topic) -> bool:
    """Generate video from AI-suggested topic."""
    
    # Convert AI topic to VideoContent
    content = VideoContent(
        video_type=VideoType.SCARY_FACTS,  # Will be overridden
        title=topic.topic,
        hook=topic.hook,
        main_text=topic.content,
        secondary_text=topic.secondary_content,
        voiceover_script=f"{topic.hook} {topic.content}",
        broll_keywords=topic.broll_keywords or ["abstract", "motion"],
        music_mood=topic.music_mood
    )
    
    output_path = str(OUTPUT_DIR / f"ai_{topic.video_type}_{random.randint(1000, 9999)}.mp4")
    
    # Route to appropriate generator based on video_type
    if topic.video_type in ["scary_fact", "money_fact", "psychology_fact", "history_fact", "life_hack"]:
        return await generate_fact_video(content, output_path)
    elif topic.video_type == "quote":
        return await generate_quote_video(content, output_path)
    elif topic.video_type == "would_you_rather":
        from script_v2 import generate_professional_video_v2
        return await generate_professional_video_v2(
            {"option_a": content.main_text, "option_b": content.secondary_text or "",
             "percentage_a": 60},
            output_path
        )
    else:
        # Default to fact video
        return await generate_fact_video(content, output_path)


async def main():
    parser = argparse.ArgumentParser(description="ViralShorts Factory - Multi-Type Generator")
    parser.add_argument("--type", choices=["wyr", "scary_facts", "money_facts", "ai_quotes", "kids", "random", "ai"],
                        default="ai", help="Video type (use 'ai' for AI-suggested topics)")
    parser.add_argument("--count", type=int, default=1, help="Number of videos")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--no-upload", action="store_true", dest="no_upload", help="Skip upload (test mode)")
    
    args = parser.parse_args()
    
    # Determine if we should upload
    should_upload = args.upload and not args.no_upload
    
    print("=" * 60)
    print("🎬 ViralShorts Factory - AI-Powered Generator")
    print("=" * 60)
    
    generated = 0
    
    # AI MODE - Use MASTER prompts for best results
    if args.type == "ai":
        print("\n🧠 MASTER AI Mode: Maximum viral potential...")
        
        if HAS_MASTER:
            gen = MasterContentGenerator()
            # Initialize client
            import os as os_module
            api_key = os_module.environ.get("GROQ_API_KEY")
            if api_key:
                try:
                    from groq import Groq
                    gen.client = Groq(api_key=api_key)
                except:
                    pass
            
            if gen.client:
                topics = gen.generate_viral_topics(args.count)
                
                # Initialize value checker
                value_checker = None
                if HAS_VALUE_CHECK:
                    value_checker = ValueDeliveryChecker()
                    print("   ✅ Value delivery checker active!")
                
                for i, topic in enumerate(topics, 1):
                    print(f"\n📹 Video {i}/{args.count}")
                    print(f"   🎯 Topic: {topic.get('topic', 'N/A')}")
                    print(f"   📊 Type: {topic.get('video_type', 'N/A')}")
                    print(f"   🧠 Triggers: {topic.get('psychological_triggers', [])}")
                    print(f"   🎬 B-roll: {topic.get('broll_keywords', [])}")
                    print(f"   💡 Why viral: {topic.get('why_viral', 'N/A')}")
                    
                    # VALUE CHECK: Ensure content delivers real value, not empty promises
                    if value_checker and HAS_VALUE_CHECK:
                        content_to_check = f"{topic.get('hook', '')} {topic.get('content', '')}"
                        check = value_checker.check_content(content_to_check)
                        if not check.get('delivers_value', True):
                            print(f"   ⚠️ VALUE CHECK FAILED: {check.get('issues', [])}")
                            print(f"   🔄 Skipping this topic (empty promises detected)")
                            continue
                        else:
                            print(f"   ✅ Value check passed: {check.get('value_score', 0)}/10")
                    
                    # Convert to VideoContent
                    content = VideoContent(
                        video_type=VideoType.SCARY_FACTS,
                        title=strip_emojis(topic.get("topic", "")),
                        hook=strip_emojis(topic.get("hook", "")),
                        main_text=strip_emojis(topic.get("content", "")),
                        secondary_text=None,
                        voiceover_script=strip_emojis(f"{topic.get('hook', '')} {topic.get('content', '')}"),
                        broll_keywords=topic.get("broll_keywords", []),
                        music_mood=topic.get("music_mood", "dramatic"),
                        call_to_action=topic.get("call_to_action", "Follow for more!")
                    )
                    
                    output_path = str(OUTPUT_DIR / f"viral_{topic.get('video_type', 'fact')}_{random.randint(1000, 9999)}.mp4")
                    success = await generate_fact_video(content, output_path)
                    if success:
                        generated += 1
                        
                        # RECORD METADATA for analytics feedback (v3.0)
                        if HAS_ANALYTICS:
                            try:
                                from analytics_feedback import FeedbackLoopController
                                feedback = FeedbackLoopController()
                                
                                # Calculate phrase/word count
                                full_content = f"{topic.get('hook', '')} {topic.get('content', '')}"
                                word_count = len(full_content.split())
                                phrase_count = len([p for p in full_content.split('.') if p.strip()])
                                
                                # Record with v3.0 generation metadata
                                generation_data = {
                                    "trend_source": topic.get("_source", "ai"),  # Track where topic came from
                                    "has_captions": True,  # v3.0 feature
                                    "caption_style": "tiktok",
                                    "has_progress_bar": True,  # v3.0 feature
                                    "progress_bar_style": "gradient",
                                    "has_ken_burns_zoom": True,  # v3.0 feature
                                    "zoom_intensity": 0.03,
                                    "has_vignette": True,  # v3.0 feature
                                    "has_particles": False,  # Optional
                                    "phrase_count": phrase_count,
                                    "total_word_count": word_count,
                                    "viral_optimizer_used": HAS_VIRAL_OPT,
                                    "ai_title_generated": HAS_VIRAL_OPT,
                                    "ai_hashtags_generated": HAS_VIRAL_OPT,
                                }
                                
                                video_id = Path(output_path).stem
                                feedback.record_video_generation(
                                    video_id=video_id,
                                    local_path=output_path,
                                    topic_data=topic,
                                    generation_data=generation_data
                                )
                                print(f"   [OK] Metadata recorded for analytics")
                            except Exception as me:
                                print(f"   [!] Metadata recording failed: {me}")
            else:
                print("⚠️ No AI client, falling back to basic AI trends")
                # Fallback to old method
                if HAS_AI_TRENDS:
                    ai_topics = get_multiple_ai_suggestions(args.count)
                    for i, topic in enumerate(ai_topics, 1):
                        success = await generate_from_ai_topic(topic)
                        if success:
                            generated += 1
        else:
            print("⚠️ Master prompts not available, using basic AI")
            if HAS_AI_TRENDS:
                ai_topics = get_multiple_ai_suggestions(args.count)
                for i, topic in enumerate(ai_topics, 1):
                    success = await generate_from_ai_topic(topic)
                    if success:
                        generated += 1
    
    else:
        # Manual mode - use specified type
        generator = MultiTypeContentGenerator()
        
        for i in range(args.count):
            print(f"\n📹 Video {i+1}/{args.count}")
            
            # Get content based on type
            if args.type == "random":
                vtype = get_weighted_random_type()
            else:
                vtype = VideoType(args.type)
            
            if vtype == VideoType.SCARY_FACTS:
                content = generator.generate_scary_fact()
            elif vtype == VideoType.MONEY_FACTS:
                content = generator.generate_money_fact()
            elif vtype == VideoType.AI_QUOTES:
                content = generator.generate_quote()
            elif vtype == VideoType.KIDS:
                content = generator.generate_kids_content()
            else:
                content = generator.generate_wyr("Have unlimited money", "Have unlimited time")
            
            if not content:
                print("   ⚠️ Could not generate content")
                continue
            
            # Generate video
            output_path = str(OUTPUT_DIR / f"{vtype.value}_{random.randint(1000, 9999)}.mp4")
            
            if vtype in [VideoType.SCARY_FACTS, VideoType.MONEY_FACTS]:
                success = await generate_fact_video(content, output_path)
            elif vtype == VideoType.AI_QUOTES:
                success = await generate_quote_video(content, output_path)
            else:
                # Use WYR generator from script_v2
                from script_v2 import generate_professional_video_v2
                success = await generate_professional_video_v2(
                    {"option_a": content.main_text, "option_b": content.secondary_text or "",
                     "percentage_a": content.percentage_a or 60},
                    output_path
                )
            
            if success:
                generated += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Generated {generated}/{args.count} videos")
    print(f"{'=' * 60}")
    
    # Track generated videos THIS RUN (to avoid uploading old ones)
    import glob
    import time
    
    # Get only videos created in the last 30 minutes (this run)
    current_time = time.time()
    all_videos = glob.glob(str(OUTPUT_DIR / "*.mp4"))
    videos_this_run = []
    for v in all_videos:
        if os.path.exists(v):
            mtime = os.path.getmtime(v)
            if current_time - mtime < 1800:  # 30 minutes
                videos_this_run.append(v)
    
    print(f"   📁 Videos this run: {len(videos_this_run)}")
    
    # Upload if requested
    if should_upload and len(videos_this_run) > 0:
        print("\n📤 Uploading videos to platforms...")
        
        # Initialize analytics feedback (learning from performance)
        feedback_controller = None
        if HAS_ANALYTICS:
            feedback_controller = FeedbackLoopController()
            print("   📊 Analytics feedback active - learning from performance!")
        
        # Initialize viral optimizer for better titles
        viral_opt = None
        if HAS_VIRAL_OPT:
            viral_opt = ViralOptimizer()
            print("   🎯 Using AI-powered titles and hashtags!")
        
        # Initialize anti-ban system
        anti_ban = None
        if HAS_ANTI_BAN:
            anti_ban = AntiBanSystem()
            print("   🛡️ Anti-ban measures active!")
        
        uploaded_count = 0
        
        # Track already uploaded videos to prevent duplicates
        uploaded_videos_file = OUTPUT_DIR / ".uploaded_videos.txt"
        already_uploaded = set()
        if uploaded_videos_file.exists():
            already_uploaded = set(uploaded_videos_file.read_text().strip().split('\n'))
        
        # Map video types to Dailymotion channels
        DM_CHANNEL_MAP = {
            'psychology': 'lifestyle',
            'life': 'lifestyle', 
            'money': 'news',
            'scary': 'fun',
            'mind': 'lifestyle',
            'fact': 'lifestyle',
            'wyr': 'fun',
            'quiz': 'fun'
        }
        
        for video_path in videos_this_run:
            filename = os.path.basename(video_path)
            
            # Skip already uploaded videos (duplicate prevention)
            # Check with platform prefix to track per-platform uploads
            yt_key = f"youtube:{filename}"
            dm_key = f"dailymotion:{filename}"
            
            if yt_key in already_uploaded and dm_key in already_uploaded:
                print(f"   [SKIP] Already uploaded to both platforms: {filename}")
                continue
            
            # Extract topic info from filename for better title
            base_name = filename.replace('.mp4', '').replace('_', ' ')
            parts = base_name.split()
            video_type = parts[1] if len(parts) > 1 else 'fact'  # viral_psychology_fact -> psychology
            
            # Determine Dailymotion channel based on video type
            dm_channel = 'lifestyle'  # Default
            for key, channel in DM_CHANNEL_MAP.items():
                if key in video_type.lower() or key in filename.lower():
                    dm_channel = channel
                    break
            
            # Use AI to generate viral title if available
            if viral_opt and HAS_VIRAL_OPT:
                try:
                    # Create a richer prompt from video type
                    content_hints = {
                        'psychology': 'psychological facts about human behavior and mind',
                        'life': 'life hacks and productivity tips',
                        'money': 'money saving tips and financial wisdom',
                        'scary': 'mind-blowing scary facts',
                        'mind': 'mind-blowing revelations',
                    }
                    hint = content_hints.get(video_type, 'viral trending facts')
                    
                    metadata = generate_viral_title_ai(
                        hook=f"Discover {video_type} secrets that will change your life",
                        content=f"This video reveals fascinating {hint}. Watch until the end for the most surprising part!",
                        video_type=video_type
                    )
                    title = metadata.get('title', f"This {video_type.title()} Fact Will Blow Your Mind")[:100]
                    description = metadata.get('description', 'Follow for more mind-blowing content!')[:5000]
                    hashtags = metadata.get('hashtags', ['#shorts', '#viral', '#facts', '#trending', '#fyp'])
                    tags = [h.replace('#', '').strip() for h in hashtags if h]
                    
                    # Add more relevant tags
                    extra_tags = ['shorts', 'viral', 'trending', 'fyp', video_type, 'facts', 'mindblown']
                    tags = list(set(tags + extra_tags))[:20]
                    
                except Exception as e:
                    print(f"   ⚠️ AI title failed, using smart fallback: {e}")
                    title = f"This {video_type.title()} Fact Will Change How You Think"[:100]
                    description = f"Discover amazing {video_type} insights! Follow for more viral content! #shorts #viral #{video_type}"
                    tags = ["shorts", "viral", "facts", "trending", "fyp", video_type, "mindblown"]
            else:
                title = f"This {video_type.title()} Fact Will Blow Your Mind"[:100]
                description = f"Discover amazing insights! Follow for more! #shorts #viral #{video_type}"
                tags = ["shorts", "viral", "facts", "trending", "fyp", video_type]
            
            # Anti-ban delay between uploads
            if anti_ban and HAS_ANTI_BAN and uploaded_count > 0:
                delay = anti_ban.get_random_delay()
                print(f"   ⏳ Anti-ban delay: {delay:.1f}s")
                time.sleep(delay)
            
            # YouTube Upload
            yt_video_id = None
            if yt_key not in already_uploaded:
                try:
                    from youtube_uploader import upload_to_youtube
                    print(f"\n   [YT] Uploading to YouTube: {title}")
                    result = upload_to_youtube(
                        video_path,
                        title=title,
                        description=description,
                        tags=tags
                    )
                    if result:
                        print(f"   [OK] YouTube: {result}")
                        uploaded_count += 1
                        yt_video_id = result.get('id') if isinstance(result, dict) else str(result)
                        # Mark as uploaded with platform prefix (prevents duplicates)
                        with open(uploaded_videos_file, 'a') as f:
                            f.write(f"{yt_key}\n")
                        already_uploaded.add(yt_key)  # Update in-memory too!
                        
                        # Record to analytics feedback system
                        if feedback_controller:
                            try:
                                feedback_controller.record_upload(filename, "youtube", yt_video_id)
                            except Exception as fe:
                                print(f"   [!] Analytics recording failed: {fe}")
                except Exception as e:
                    print(f"   [!] YouTube upload error: {e}")
            else:
                print(f"   [SKIP] Already on YouTube: {filename}")
            # Dailymotion Upload (with anti-ban delay)
            if dm_key not in already_uploaded:
                if anti_ban and HAS_ANTI_BAN:
                    delay = anti_ban.get_random_delay()
                    print(f"   [WAIT] Anti-ban delay: {delay:.1f}s")
                    time.sleep(delay)
                
                try:
                    from dailymotion_uploader import DailymotionUploader
                    dm = DailymotionUploader()
                    if dm.is_configured:
                        # Check connectivity first (no quota used)
                        conn = dm.check_connectivity()
                        if conn.get('status') == 'ok':
                            print(f"\n   [DM] Uploading to Dailymotion: {title}")
                            print(f"      Channel: {dm_channel}, Tags: {len(tags)}")
                            dm_result = dm.upload_video(
                                video_path,
                                title=title,
                                description=description,
                                tags=tags,
                                channel=dm_channel,  # Proper category!
                                ai_generated=False  # User preference: no AI disclosure
                            )
                            if dm_result:
                                print(f"   [OK] Dailymotion: {dm_result}")
                                # Mark as uploaded with platform prefix (prevents duplicates)
                                with open(uploaded_videos_file, 'a') as f:
                                    f.write(f"{dm_key}\n")
                                already_uploaded.add(dm_key)  # Update in-memory too!
                                
                                # Record to analytics feedback system
                                if feedback_controller:
                                    try:
                                        feedback_controller.record_upload(filename, "dailymotion", dm_result)
                                    except Exception as fe:
                                        print(f"   [!] Dailymotion analytics recording failed: {fe}")
                        else:
                            print(f"   [!] Dailymotion: {conn.get('message')}")
                    else:
                        print("   [!] Dailymotion not configured")
                except Exception as e:
                    print(f"   [!] Dailymotion upload error: {e}")
            else:
                print(f"   [SKIP] Already on Dailymotion: {filename}")
    
    elif not should_upload:
        print("\n📁 Videos saved locally (upload skipped)")


if __name__ == "__main__":
    asyncio.run(main())

