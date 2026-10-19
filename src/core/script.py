#!/usr/bin/env python3
"""
QuizBot - Autonomous "Would You Rather" Video Generator for YouTube Shorts
Zero-Cost Stack: edge-tts + moviepy + local assets
"""

import asyncio
import json
import os
import random
import sys
from pathlib import Path

import edge_tts
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    CompositeAudioClip,
    concatenate_audioclips,
    vfx
)
from moviepy.video.fx.all import loop


# ============ CONFIGURATION ============
OUTPUT_DIR = Path("./output")
ASSETS_DIR = Path("./assets")
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
SFX_DIR = ASSETS_DIR / "sfx"
FONTS_DIR = ASSETS_DIR / "fonts"
QUESTIONS_FILE = Path("./questions.json")

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 24
VIDEO_DURATION = 60  # seconds

# Voice settings
VOICE = "en-US-ChristopherNeural"
VOICE_RATE = "-5%"  # Slightly slower for clarity

# Colors (RGB tuples)
OPTION_A_COLOR = (220, 53, 69)   # Red
OPTION_B_COLOR = (0, 123, 255)   # Blue
VS_CIRCLE_COLOR = (255, 193, 7)  # Yellow/Gold
TEXT_COLOR = (255, 255, 255)     # White


def ensure_directories():
    """Create necessary directories if they don't exist."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    BACKGROUNDS_DIR.mkdir(exist_ok=True)
    SFX_DIR.mkdir(exist_ok=True)
    FONTS_DIR.mkdir(exist_ok=True)


def load_random_question() -> dict:
    """Load a random question from questions.json."""
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"Questions file not found: {QUESTIONS_FILE}")
    
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    return random.choice(questions)


async def generate_voiceover(text: str, output_path: str, retries: int = 5) -> float:
    """Generate voiceover using edge-tts with retry logic. Returns duration in seconds."""
    last_error = None
    
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=VOICE_RATE)
            await communicate.save(output_path)
            
            # Get audio duration
            audio = AudioFileClip(output_path)
            duration = audio.duration
            audio.close()
            return duration
            
        except Exception as e:
            last_error = e
            print(f"   ⚠️ TTS attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 30  # 30, 60, 90, 120 seconds
                print(f"   Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
    
    raise last_error if last_error else Exception("TTS generation failed")


def get_background_video() -> VideoFileClip:
    """Load and prepare a random background video."""
    # Get all video files from backgrounds directory
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    background_files = [
        f for f in BACKGROUNDS_DIR.iterdir() 
        if f.suffix.lower() in video_extensions
    ]
    
    if not background_files:
        # Create a simple gradient background if no videos found
        print("⚠️ No background videos found. Creating solid color background.")
        return ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
            color=(30, 30, 40)
        ).set_duration(VIDEO_DURATION)
    
    # Pick random background
    bg_path = random.choice(background_files)
    print(f"📹 Using background: {bg_path.name}")
    
    # Load and resize video
    bg_clip = VideoFileClip(str(bg_path))
    
    # Resize to fill screen (center crop)
    bg_ratio = bg_clip.w / bg_clip.h
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    
    if bg_ratio > target_ratio:
        # Video is wider, scale by height
        new_height = VIDEO_HEIGHT
        new_width = int(VIDEO_HEIGHT * bg_ratio)
    else:
        # Video is taller, scale by width
        new_width = VIDEO_WIDTH
        new_height = int(VIDEO_WIDTH / bg_ratio)
    
    bg_clip = bg_clip.resize((new_width, new_height))
    
    # Center crop
    x_center = new_width // 2
    y_center = new_height // 2
    bg_clip = bg_clip.crop(
        x_center=x_center, y_center=y_center,
        width=VIDEO_WIDTH, height=VIDEO_HEIGHT
    )
    
    # Loop to required duration
    if bg_clip.duration < VIDEO_DURATION:
        n_loops = int(VIDEO_DURATION / bg_clip.duration) + 1
        bg_clip = bg_clip.loop(n=n_loops)
    
    bg_clip = bg_clip.subclip(0, VIDEO_DURATION)
    
    return bg_clip


def create_option_panel(text: str, color: tuple, width: int, height: int, 
                        font_size: int = 70, position: str = "top") -> CompositeVideoClip:
    """Create a semi-transparent option panel with text."""
    # Background panel (semi-transparent)
    panel_color = tuple(int(c * 0.8) for c in color)
    panel = ColorClip(size=(width, height), color=panel_color)
    panel = panel.set_opacity(0.85)
    
    # Wrap text for long options
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 25:  # Approximate character limit per line
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(' '.join(current_line))
                current_line = []
    if current_line:
        lines.append(' '.join(current_line))
    
    wrapped_text = '\n'.join(lines)
    
    # Text
    try:
        text_clip = TextClip(
            wrapped_text,
            fontsize=font_size,
            font="Arial-Bold",
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(width - 80, None),
            align='center'
        )
    except Exception:
        # Fallback if Arial-Bold not available
        text_clip = TextClip(
            wrapped_text,
            fontsize=font_size,
            font="Arial",
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(width - 80, None),
            align='center'
        )
    
    text_clip = text_clip.set_position(('center', 'center'))
    
    # Combine panel and text
    composite = CompositeVideoClip([panel, text_clip], size=(width, height))
    
    return composite


def create_vs_circle(size: int = 150) -> CompositeVideoClip:
    """Create a VS circle element."""
    # Circle background
    circle = ColorClip(size=(size, size), color=VS_CIRCLE_COLOR)
    
    # VS text
    vs_text = TextClip(
        "VS",
        fontsize=60,
        font="Arial-Bold",
        color='black',
        stroke_color='white',
        stroke_width=1
    ).set_position(('center', 'center'))
    
    composite = CompositeVideoClip([circle, vs_text], size=(size, size))
    
    return composite


def create_percentage_reveal(percentage_a: int, width: int, height: int) -> CompositeVideoClip:
    """Create the percentage reveal overlay."""
    percentage_b = 100 - percentage_a
    
    # Top percentage (Option A)
    top_text = TextClip(
        f"{percentage_a}%",
        fontsize=120,
        font="Arial-Bold",
        color='white',
        stroke_color='black',
        stroke_width=4
    ).set_position(('center', height // 4 - 60))
    
    # Bottom percentage (Option B)
    bottom_text = TextClip(
        f"{percentage_b}%",
        fontsize=120,
        font="Arial-Bold",
        color='white',
        stroke_color='black',
        stroke_width=4
    ).set_position(('center', 3 * height // 4 - 60))
    
    composite = CompositeVideoClip(
        [top_text, bottom_text],
        size=(width, height)
    )
    
    return composite


def create_timer_text(seconds: int) -> TextClip:
    """Create countdown timer text."""
    return TextClip(
        f"⏱️ {seconds}",
        fontsize=50,
        font="Arial",
        color='white',
        stroke_color='black',
        stroke_width=2
    )


async def generate_video(question: dict, output_filename: str = None):
    """Generate a complete Would You Rather video."""
    print("\n🎬 Starting video generation...")
    
    # Extract question data
    option_a = question['option_a']
    option_b = question['option_b']
    percentage_a = question.get('percentage_a', random.randint(30, 70))
    
    # Generate voiceover text
    voiceover_text = f"Would you rather... {option_a}... or... {option_b}? Vote now!"
    
    print(f"📝 Question: Would you rather...")
    print(f"   A: {option_a}")
    print(f"   B: {option_b}")
    
    # Generate voiceover
    voiceover_path = str(OUTPUT_DIR / "temp_voiceover.mp3")
    print("🎤 Generating voiceover...")
    voiceover_duration = await generate_voiceover(voiceover_text, voiceover_path)
    print(f"   Duration: {voiceover_duration:.1f}s")
    
    # Load voiceover
    voiceover = AudioFileClip(voiceover_path)
    
    # Get background video
    print("🖼️ Loading background...")
    background = get_background_video()
    
    # Create option panels
    panel_height = VIDEO_HEIGHT // 2 - 75  # Leave room for VS circle
    
    option_a_panel = create_option_panel(
        option_a, OPTION_A_COLOR, 
        VIDEO_WIDTH, panel_height
    ).set_position(('center', 0))
    
    option_b_panel = create_option_panel(
        option_b, OPTION_B_COLOR,
        VIDEO_WIDTH, panel_height
    ).set_position(('center', VIDEO_HEIGHT // 2 + 75))
    
    # Create VS circle
    vs_circle = create_vs_circle(150).set_position(('center', 'center'))
    
    # Create percentage reveal
    percentage_overlay = create_percentage_reveal(
        percentage_a, VIDEO_WIDTH, VIDEO_HEIGHT
    )
    
    # Timeline:
    # 0-voiceover_end: Show question with voiceover
    # voiceover_end to reveal_time: Countdown/thinking time
    # reveal_time onwards: Show percentages
    
    question_show_time = voiceover_duration + 1  # When question fully shown
    thinking_time = 5  # Seconds to think before reveal
    reveal_time = question_show_time + thinking_time
    
    # Ensure video is long enough
    total_duration = min(VIDEO_DURATION, reveal_time + 10)
    
    # Set durations
    background = background.subclip(0, total_duration)
    option_a_panel = option_a_panel.set_duration(total_duration)
    option_b_panel = option_b_panel.set_duration(total_duration)
    vs_circle = vs_circle.set_duration(total_duration)
    
    # Percentage reveal appears after thinking time
    percentage_overlay = (percentage_overlay
        .set_start(reveal_time)
        .set_duration(total_duration - reveal_time)
        .crossfadein(0.5))
    
    # Add "Results!" text
    results_text = (TextClip(
        "RESULTS!",
        fontsize=80,
        font="Arial-Bold",
        color=(255, 215, 0),  # Gold
        stroke_color='black',
        stroke_width=3
    )
    .set_position(('center', VIDEO_HEIGHT // 2 - 40))
    .set_start(reveal_time)
    .set_duration(total_duration - reveal_time)
    .crossfadein(0.3))
    
    print("🎨 Compositing video...")
    
    # Composite all elements
    final_video = CompositeVideoClip([
        background,
        option_a_panel,
        option_b_panel,
        vs_circle,
        percentage_overlay,
        results_text
    ], size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    
    final_video = final_video.set_duration(total_duration)
    
    # Set audio - voiceover starts at 0.5s for better timing
    voiceover = voiceover.set_start(0.5)
    
    # Try to load sound effects if available
    audio_clips = [voiceover]
    
    tick_sfx_path = SFX_DIR / "tick.mp3"
    ding_sfx_path = SFX_DIR / "ding.mp3"
    
    if tick_sfx_path.exists():
        tick = AudioFileClip(str(tick_sfx_path)).set_start(reveal_time - 3)
        audio_clips.append(tick)
    
    if ding_sfx_path.exists():
        ding = AudioFileClip(str(ding_sfx_path)).set_start(reveal_time)
        audio_clips.append(ding)
    
    # Combine audio
    final_audio = CompositeAudioClip(audio_clips)
    final_video = final_video.set_audio(final_audio)
    
    # Generate output filename
    if output_filename is None:
        import hashlib
        import time
        hash_input = f"{option_a}{option_b}{time.time()}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        output_filename = f"wyr_{short_hash}.mp4"
    
    output_path = OUTPUT_DIR / output_filename
    
    print(f"🎥 Rendering video to {output_path}...")
    
    # Render video
    final_video.write_videofile(
        str(output_path),
        fps=VIDEO_FPS,
        codec='libx264',
        audio_codec='aac',
        preset='ultrafast',  # Fast rendering
        threads=4,
        logger=None  # Suppress moviepy progress bar
    )
    
    # Cleanup temp files
    if os.path.exists(voiceover_path):
        os.remove(voiceover_path)
    
    # Close clips to free memory
    final_video.close()
    background.close()
    voiceover.close()
    
    print(f"\n✅ Video generated successfully!")
    print(f"📁 Output: {output_path}")
    print(f"⏱️ Duration: {total_duration:.1f} seconds")
    
    return str(output_path)


async def batch_generate(count: int = 5):
    """Generate multiple videos in batch."""
    print(f"\n🚀 Batch generating {count} videos...")
    
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Shuffle and pick questions
    random.shuffle(questions)
    selected = questions[:count]
    
    generated = []
    for i, question in enumerate(selected, 1):
        print(f"\n{'='*50}")
        print(f"📹 Generating video {i}/{count}")
        print(f"{'='*50}")
        
        try:
            output = await generate_video(question)
            generated.append(output)
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            continue
    
    print(f"\n🎉 Batch complete! Generated {len(generated)}/{count} videos.")
    return generated


def main():
    """Main entry point."""
    ensure_directories()
    
    # Check for questions file
    if not QUESTIONS_FILE.exists():
        print("❌ Error: questions.json not found!")
        print("   Please create a questions.json file with your Would You Rather questions.")
        print("   See the sample format in the README.")
        sys.exit(1)
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            asyncio.run(batch_generate(count))
        elif sys.argv[1] == "--help":
            print("QuizBot - Would You Rather Video Generator")
            print("\nUsage:")
            print("  python script.py           Generate a single random video")
            print("  python script.py --batch N Generate N videos")
            print("  python script.py --help    Show this help message")
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information.")
    else:
        # Generate single video
        question = load_random_question()
        asyncio.run(generate_video(question))


if __name__ == "__main__":
    main()

