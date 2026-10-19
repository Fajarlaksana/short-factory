#!/usr/bin/env python3
"""
Thumbnail Generator for ViralShorts Factory v8.5
=================================================

100% AI-DRIVEN Thumbnails:
- AI generates thumbnail headline (not just shortened topic)
- AI selects color scheme based on content emotion
- AI suggests visual style elements
- High-CTR optimization

FREE: Uses PIL + Groq AI (no paid image services)
"""

import os
import random
import requests
import json
import re
from pathlib import Path
from typing import Optional, Tuple, Dict

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL not available")
    Image = None

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_gemini_model_for_rest_api
except ImportError:
    def get_gemini_model_for_rest_api(api_key=None):
        return "gemini-2.5-flash"  # Fallback only if import fails


# Thumbnail settings
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# Color schemes mapped to emotions/content types
# AI will select based on content analysis
COLOR_SCHEMES = {
    "shocking": {"bg": (180, 20, 20), "text": (255, 255, 255), "accent": (255, 200, 0)},
    "mysterious": {"bg": (20, 20, 60), "text": (255, 255, 255), "accent": (150, 100, 255)},
    "money": {"bg": (20, 80, 40), "text": (255, 255, 255), "accent": (255, 215, 0)},
    "psychology": {"bg": (60, 20, 80), "text": (255, 255, 255), "accent": (255, 100, 255)},
    "motivation": {"bg": (255, 140, 0), "text": (0, 0, 0), "accent": (255, 255, 255)},
    "facts": {"bg": (30, 30, 30), "text": (255, 255, 0), "accent": (0, 200, 255)},
    "scary": {"bg": (10, 10, 10), "text": (255, 0, 0), "accent": (255, 255, 255)},
    "health": {"bg": (0, 120, 100), "text": (255, 255, 255), "accent": (200, 255, 200)},
    "default": {"bg": (30, 30, 30), "text": (255, 255, 0), "accent": (255, 50, 50)},
}

def get_ai_thumbnail_concept(topic: str, category: str, gemini_key: str = None) -> Dict:
    """
    AI generates the thumbnail concept using GEMINI (free tokens!).
    
    v8.7: Uses Gemini instead of Groq - we have free Gemini quota to spare!
    
    Returns: {headline, color_mood, emphasis_word}
    """
    if not gemini_key:
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    prompt = f"""Create a HIGH-CTR YouTube thumbnail concept for this video:

Topic: {topic}
Category: {category}

Generate:
1. HEADLINE: A punchy 3-5 word text that makes people CLICK (not the full topic!)
   - Use power words: SECRET, TRUTH, NEVER, ALWAYS, WHY, HOW
   - Use numbers if relevant
   - Create curiosity gap
   
2. COLOR_MOOD: Which emotion does this content evoke?
   Options: shocking, mysterious, money, psychology, motivation, facts, scary, health, default
   
3. EMPHASIS_WORD: Which ONE word should be visually emphasized (different color)?

Return JSON ONLY:
{{
    "headline": "SHORT PUNCHY TEXT",
    "color_mood": "emotion_name",
    "emphasis_word": "ONE_WORD"
}}"""

    # Try Gemini first (free quota!)
    if gemini_key:
        try:
            import time
            # DYNAMIC MODEL SELECTION - no hardcoded model names
            gemini_model = get_gemini_model_for_rest_api(gemini_key)

            # v17.9.37: DYNAMIC rate limit delay
            try:
                from src.ai.model_helper import get_smart_delay
                delay = get_smart_delay(gemini_model, "gemini")
            except ImportError:
                delay = 4.4  # Fallback
            time.sleep(delay)
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.8, "maxOutputTokens": 200}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    result = json.loads(match.group())
                    if result.get("headline"):
                        print(f"   [OK] Gemini generated thumbnail concept")
                        return result
        except Exception as e:
            print(f"   [!] Gemini thumbnail failed: {e}")
    
    # Fallback to Groq if Gemini unavailable
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    result = json.loads(match.group())
                    if result.get("headline"):
                        print(f"   [OK] Groq generated thumbnail concept (fallback)")
                        return result
        except Exception as e:
            print(f"   [!] Groq thumbnail failed: {e}")
    
    # Ultimate fallback
    return {
        "headline": shorten_for_thumbnail(topic),
        "color_mood": category.lower() if category.lower() in COLOR_SCHEMES else "default",
        "emphasis_word": ""
    }


def get_thumbnail_font(size: int = 72) -> Optional[ImageFont.FreeTypeFont]:
    """Get a bold font for thumbnails."""
    font_paths = [
        "assets/fonts/bebas-neue.ttf",
        "assets/fonts/oswald-bold.ttf",
        "assets/fonts/anton.ttf",
        "assets/fonts/archivo-black.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    try:
        return ImageFont.load_default()
    except:
        return None


def generate_thumbnail(
    topic: str,
    category: str = "",
    output_path: Optional[str] = None,
    gemini_key: str = None
) -> Optional[str]:
    """
    Generate a high-CTR thumbnail using AI.
    
    v8.5: AI generates:
    - Punchy headline (not just shortened topic)
    - Optimal color scheme based on emotion
    - Emphasis word for visual pop
    
    Args:
        topic: The video topic
        category: Video category for context
        output_path: Where to save
        groq_key: Optional API key
    
    Returns:
        Path to generated thumbnail or None
    """
    if Image is None:
        print("PIL not available for thumbnail generation")
        return None
    
    # Create output directory
    thumb_dir = Path("assets/thumbnails")
    thumb_dir.mkdir(parents=True, exist_ok=True)
    
    if not output_path:
        import hashlib
        hash_id = hashlib.md5(topic.encode()).hexdigest()[:8]
        output_path = str(thumb_dir / f"thumb_{hash_id}.png")
    
    # v8.7: AI generates the thumbnail concept using GEMINI (free tokens!)
    print(f"   [AI] Generating thumbnail concept (using Gemini)...")
    concept = get_ai_thumbnail_concept(topic, category, gemini_key)
    
    # Select color scheme based on AI analysis
    color_mood = concept.get("color_mood", "default")
    color_scheme = COLOR_SCHEMES.get(color_mood, COLOR_SCHEMES["default"])
    emphasis_word = concept.get("emphasis_word", "").upper()
    
    print(f"   [OK] Headline: {concept.get('headline', topic)}")
    print(f"   [OK] Color mood: {color_mood}")
    
    # Create thumbnail
    img = Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), color_scheme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Use AI-generated headline (not just shortened topic!)
    thumb_text = concept.get("headline", shorten_for_thumbnail(topic))
    
    # Draw text
    font_large = get_thumbnail_font(96)
    font_medium = get_thumbnail_font(48)
    
    if not font_large:
        print("No font available for thumbnail")
        return None
    
    # Calculate text position (centered)
    words = thumb_text.upper().split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_text = " ".join(current_line)
        try:
            bbox = draw.textbbox((0, 0), test_text, font=font_large)
            if bbox[2] - bbox[0] > THUMBNAIL_WIDTH - 100:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        except:
            pass
    
    if current_line:
        lines.append(" ".join(current_line))
    
    # Limit to 3 lines
    lines = lines[:3]
    
    # Draw each line centered
    line_height = 110
    total_height = len(lines) * line_height
    start_y = (THUMBNAIL_HEIGHT - total_height) // 2
    
    for i, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0, 0), line, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (THUMBNAIL_WIDTH - text_width) // 2
            y = start_y + i * line_height
            
            # Draw outline (thicker for better visibility)
            for ox in range(-5, 6, 2):
                for oy in range(-5, 6, 2):
                    draw.text((x + ox, y + oy), line, fill=(0, 0, 0), font=font_large)
            
            # v8.5: Check if this line contains the emphasis word
            if emphasis_word and emphasis_word in line:
                # Draw word-by-word with emphasis
                words = line.split()
                word_x = x
                for word in words:
                    word_bbox = draw.textbbox((0, 0), word + " ", font=font_large)
                    word_width = word_bbox[2] - word_bbox[0]
                    
                    # Use accent color for emphasis word
                    if word == emphasis_word:
                        draw.text((word_x, y), word, fill=color_scheme["accent"], font=font_large)
                    else:
                        draw.text((word_x, y), word, fill=color_scheme["text"], font=font_large)
                    
                    word_x += word_width
            else:
                # Draw entire line in text color
                draw.text((x, y), line, fill=color_scheme["text"], font=font_large)
        except Exception as e:
            print(f"Text drawing error: {e}")
    
    # Add category badge (optional)
    if category and font_medium:
        badge_text = category.upper()
        try:
            badge_bbox = draw.textbbox((0, 0), badge_text, font=font_medium)
            badge_width = badge_bbox[2] - badge_bbox[0] + 40
            badge_height = 60
            
            # Draw badge background
            badge_x = 40
            badge_y = THUMBNAIL_HEIGHT - badge_height - 40
            draw.rounded_rectangle(
                [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
                radius=10,
                fill=color_scheme["accent"]
            )
            
            # Draw badge text
            draw.text(
                (badge_x + 20, badge_y + 8),
                badge_text,
                fill=(0, 0, 0),
                font=font_medium
            )
        except:
            pass
    
    # v17.9.50: Add visual elements for higher CTR
    img = add_visual_elements(img, color_scheme, concept)
    
    # Save
    try:
        img.save(output_path, "PNG", quality=95)
        print(f"   [OK] Thumbnail saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"   [!] Thumbnail save failed: {e}")
        return None


def add_visual_elements(img: Image.Image, color_scheme: Dict, concept: Dict) -> Image.Image:
    """
    v17.9.50: Add CTR-boosting visual elements to thumbnail.
    
    Studies show these elements increase CTR by 20-40%:
    - Corner accents/glow effects
    - Subtle gradients
    - Visual hierarchy enhancers
    """
    import random
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    accent = color_scheme.get("accent", (255, 200, 0))
    
    # Add subtle corner glow effects
    try:
        # Top-left corner accent
        for i in range(50):
            alpha = int(255 * (1 - i/50) * 0.3)
            glow_color = (*accent[:3], alpha) if len(accent) == 3 else accent
            draw.ellipse(
                [-100 + i*2, -100 + i*2, 100 - i*2, 100 - i*2],
                outline=accent,
                width=2
            )
    except:
        pass  # Some PIL versions don't support alpha
    
    # Add subtle gradient overlay at bottom (for text visibility)
    try:
        for y in range(height - 100, height):
            alpha = int((y - (height - 100)) / 100 * 80)
            draw.line([(0, y), (width, y)], fill=(0, 0, 0), width=1)
    except:
        pass
    
    # Add small visual indicator based on content type
    visual_type = concept.get("visual_indicator", None)
    
    if visual_type == "arrow_up":
        # Draw upward arrow (for growth/success content)
        arrow_x = width - 80
        arrow_y = 60
        points = [
            (arrow_x, arrow_y + 40),
            (arrow_x, arrow_y),
            (arrow_x - 20, arrow_y + 20),
            (arrow_x, arrow_y),
            (arrow_x + 20, arrow_y + 20),
        ]
        draw.line(points[:2], fill=accent, width=6)
        draw.line(points[2:4], fill=accent, width=6)
        draw.line(points[3:5], fill=accent, width=6)
    
    elif visual_type == "circle_highlight":
        # Draw attention circle
        draw.ellipse(
            [width - 100, 20, width - 20, 100],
            outline=accent,
            width=4
        )
    
    # Add subtle border for professional look
    border_width = 4
    draw.rectangle(
        [border_width, border_width, width - border_width, height - border_width],
        outline=accent,
        width=border_width
    )
    
    return img


def shorten_for_thumbnail(text: str, max_words: int = 6) -> str:
    """
    Shorten text for thumbnail display.
    Keep only the most impactful words.
    """
    # Remove common filler words
    skip_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                  'would', 'could', 'should', 'may', 'might', 'can', 'this',
                  'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
                  'we', 'they', 'what', 'which', 'who', 'whom', 'when',
                  'where', 'why', 'how', 'of', 'for', 'to', 'in', 'on', 'at'}
    
    words = text.split()
    important_words = [w for w in words if w.lower() not in skip_words]
    
    if len(important_words) > max_words:
        important_words = important_words[:max_words]
    
    # If too short, use original
    if len(important_words) < 2:
        return " ".join(words[:max_words])
    
    return " ".join(important_words)


if __name__ == "__main__":
    # Test thumbnail generation
    test_topics = [
        "Why Most People Will Never Be Rich",
        "The 5 Second Rule Changed My Life",
        "Your Brain is Lying to You",
    ]
    
    for topic in test_topics:
        print(f"\nGenerating thumbnail for: {topic}")
        result = generate_thumbnail(topic, "Psychology")
        print(f"Result: {result}")


