#!/usr/bin/env python3
"""
ViralShorts Factory - AI Thumbnail Generator
=============================================

Generates eye-catching thumbnails for videos using:
1. AI-generated text overlays
2. Dynamic backgrounds
3. Emotion-triggering elements
4. Platform-optimized sizing
"""

import os
import re
from typing import Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random


# =============================================================================
# THUMBNAIL GENERATOR
# =============================================================================

class AIThumbnailGenerator:
    """
    Generate viral thumbnails with AI-optimized elements.
    
    Thumbnail psychology:
    - Bold, contrasting text
    - Expressive faces/emojis
    - Curiosity gaps
    - Bright colors
    """
    
    THUMBNAIL_SIZES = {
        "youtube": (1280, 720),
        "tiktok": (1080, 1920),
        "dailymotion": (1280, 720),
        "instagram": (1080, 1080),
    }
    
    # High-impact color schemes (tested for CTR)
    COLOR_SCHEMES = {
        "fire": {
            "background": ["#FF4500", "#FF6347"],
            "text": "#FFFFFF",
            "accent": "#FFFF00",
        },
        "electric": {
            "background": ["#0066FF", "#00CCFF"],
            "text": "#FFFFFF",
            "accent": "#00FF00",
        },
        "gold": {
            "background": ["#1a1a2e", "#16213e"],
            "text": "#FFD700",
            "accent": "#FFA500",
        },
        "viral": {
            "background": ["#FF0050", "#7C3AED"],
            "text": "#FFFFFF",
            "accent": "#00FFFF",
        },
        "money": {
            "background": ["#0D4D00", "#00A600"],
            "text": "#FFFFFF",
            "accent": "#FFD700",
        },
    }
    
    # Font paths
    FONT_PATHS = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    
    def __init__(self, groq_key: str = None):
        self.groq_key = groq_key or os.environ.get("GROQ_API_KEY")
        self.font_path = next((f for f in self.FONT_PATHS if os.path.exists(f)), None)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _generate_ai_headline(self, topic: str, hook: str) -> str:
        """Use AI to generate the most clickable thumbnail text."""
        if not self.groq_key:
            # Fallback to rule-based
            return self._rule_based_headline(topic, hook)
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            prompt = f"""Create a thumbnail headline for a viral short video.

Topic: {topic}
Hook: {hook}

Rules:
1. Maximum 5-7 words
2. Use ALL CAPS for emphasis
3. Create curiosity gap
4. Include power words (SECRET, SHOCKING, TRUTH, HIDDEN)
5. Must be emotionally triggering

Return ONLY the headline text, nothing else."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().strip('"')
            
        except Exception as e:
            print(f"AI headline error: {e}")
            return self._rule_based_headline(topic, hook)
    
    def _rule_based_headline(self, topic: str, hook: str) -> str:
        """Generate headline using rules when AI unavailable."""
        power_words = ["SHOCKING", "SECRET", "HIDDEN TRUTH", "YOU WON'T BELIEVE"]
        
        # Extract key phrase
        words = hook.split()[:4]
        base = " ".join(words).upper()
        
        return f"{random.choice(power_words)}: {base}..."
    
    def _create_gradient_background(self, size: Tuple[int, int], 
                                   colors: list) -> Image.Image:
        """Create a gradient background."""
        width, height = size
        img = Image.new('RGB', size)
        
        color1 = self._hex_to_rgb(colors[0])
        color2 = self._hex_to_rgb(colors[1])
        
        for y in range(height):
            ratio = y / height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        
        return img
    
    def _add_text_with_outline(self, img: Image.Image, text: str,
                               position: Tuple[int, int],
                               font: ImageFont,
                               text_color: str,
                               outline_color: str = "#000000",
                               outline_width: int = 3) -> Image.Image:
        """Add text with outline effect."""
        draw = ImageDraw.Draw(img)
        x, y = position
        
        text_color_rgb = self._hex_to_rgb(text_color)
        outline_rgb = self._hex_to_rgb(outline_color)
        
        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_rgb)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color_rgb)
        
        return img
    
    def generate(self, topic: str, hook: str, content: str,
                video_type: str = "facts",
                platform: str = "youtube",
                output_path: str = None) -> Optional[str]:
        """
        Generate a viral thumbnail.
        
        Returns path to the generated thumbnail.
        """
        # Get size for platform
        size = self.THUMBNAIL_SIZES.get(platform, (1280, 720))
        
        # Select color scheme based on video type
        scheme_map = {
            "money": "money",
            "psychology": "viral",
            "life_hack": "electric",
            "scary": "fire",
            "facts": "gold",
        }
        scheme_name = scheme_map.get(video_type, "gold")
        scheme = self.COLOR_SCHEMES[scheme_name]
        
        # Create background
        img = self._create_gradient_background(size, scheme["background"])
        
        # Add some visual interest (diagonal stripes)
        draw = ImageDraw.Draw(img, 'RGBA')
        for i in range(-size[1], size[0], 50):
            draw.line([(i, 0), (i + size[1], size[1])], 
                     fill=(255, 255, 255, 30), width=20)
        
        # Generate headline
        headline = self._generate_ai_headline(topic, hook)
        
        # Split into lines (max 2)
        words = headline.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        
        # Load font
        try:
            # Size based on thumbnail dimensions
            font_size = size[0] // 10
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate positions (centered)
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        # Draw lines
        for i, line in enumerate([line1, line2]):
            if not line:
                continue
            
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = center_x - text_width // 2
            y = center_y - text_height + (i * text_height * 1.5)
            
            img = self._add_text_with_outline(
                img, line, (x, int(y)),
                font, scheme["text"], "#000000", 4
            )
        
        # Add accent elements (corner badges)
        accent_color = self._hex_to_rgb(scheme["accent"])
        
        # "NEW" badge top-left
        badge_font_size = size[0] // 20
        try:
            badge_font = ImageFont.truetype(self.font_path, badge_font_size)
        except:
            badge_font = font
        
        badge_text = "NEW"
        draw.rectangle([10, 10, 120, 60], fill=accent_color)
        draw.text((25, 15), badge_text, font=badge_font, fill=(0, 0, 0))
        
        # Save
        if output_path is None:
            output_path = f"thumbnail_{video_type}_{random.randint(1000, 9999)}.png"
        
        img.save(output_path, "PNG", quality=95)
        print(f"[OK] Thumbnail saved: {output_path}")
        
        return output_path


# =============================================================================
# A/B TESTING FRAMEWORK
# =============================================================================

class ABTestingFramework:
    """
    A/B testing for video elements.
    
    Tracks performance of different:
    - Thumbnails
    - Titles
    - Hooks
    - Video types
    
    Uses analytics feedback to optimize.
    """
    
    def __init__(self, data_path: str = "data/ab_tests.json"):
        self.data_path = data_path
        self.tests = self._load_tests()
    
    def _load_tests(self) -> Dict:
        """Load existing test data."""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "title_tests": {},
            "thumbnail_tests": {},
            "hook_tests": {},
            "video_type_tests": {},
        }
    
    def _save_tests(self):
        """Save test data."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump(self.tests, f, indent=2)
    
    def record_variant(self, test_type: str, variant_id: str, 
                      video_id: str, metadata: Dict):
        """Record a test variant."""
        if test_type not in self.tests:
            self.tests[test_type] = {}
        
        if variant_id not in self.tests[test_type]:
            self.tests[test_type][variant_id] = {
                "videos": [],
                "total_views": 0,
                "total_likes": 0,
                "avg_ctr": 0,
            }
        
        self.tests[test_type][variant_id]["videos"].append({
            "video_id": video_id,
            "metadata": metadata,
            "created": datetime.now().isoformat() if 'datetime' in dir() else str(os.times())
        })
        
        self._save_tests()
    
    def update_performance(self, video_id: str, views: int, likes: int, ctr: float = 0):
        """Update performance metrics for a video."""
        for test_type in self.tests:
            for variant_id in self.tests[test_type]:
                variant = self.tests[test_type][variant_id]
                for video in variant["videos"]:
                    if video["video_id"] == video_id:
                        video["views"] = views
                        video["likes"] = likes
                        video["ctr"] = ctr
                        
                        # Update totals
                        variant["total_views"] = sum(
                            v.get("views", 0) for v in variant["videos"]
                        )
                        variant["total_likes"] = sum(
                            v.get("likes", 0) for v in variant["videos"]
                        )
        
        self._save_tests()
    
    def get_best_variant(self, test_type: str) -> Optional[str]:
        """Get the best performing variant for a test type."""
        if test_type not in self.tests:
            return None
        
        variants = self.tests[test_type]
        if not variants:
            return None
        
        # Sort by average views per video
        best = max(
            variants.items(),
            key=lambda x: x[1]["total_views"] / max(len(x[1]["videos"]), 1)
        )
        
        return best[0]
    
    def generate_report(self) -> str:
        """Generate A/B testing report."""
        report = ["=" * 60, "A/B TESTING REPORT", "=" * 60]
        
        for test_type, variants in self.tests.items():
            if not variants:
                continue
            
            report.append(f"\n{test_type.upper().replace('_', ' ')}:")
            report.append("-" * 40)
            
            sorted_variants = sorted(
                variants.items(),
                key=lambda x: x[1]["total_views"],
                reverse=True
            )
            
            for variant_id, data in sorted_variants[:5]:
                video_count = len(data["videos"])
                avg_views = data["total_views"] / max(video_count, 1)
                
                report.append(
                    f"  {variant_id[:30]}: {video_count} videos, "
                    f"{data['total_views']} total views, {avg_views:.0f} avg"
                )
        
        return "\n".join(report)


# Need to import for ABTestingFramework
import json
from datetime import datetime


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI Thumbnail Generator Test")
    print("=" * 60)
    
    generator = AIThumbnailGenerator()
    
    # Test thumbnail generation
    output = generator.generate(
        topic="psychology_fact",
        hook="Your brain makes 35000 decisions every single day",
        content="This is why you feel mentally exhausted by evening...",
        video_type="psychology",
        platform="youtube"
    )
    
    if output:
        print(f"[OK] Thumbnail generated: {output}")
    
    # Test A/B framework
    print("\n" + "=" * 60)
    print("A/B Testing Framework Test")
    print("=" * 60)
    
    ab = ABTestingFramework("data/test_ab.json")
    
    # Record some test variants
    ab.record_variant("title_tests", "question_style", "vid123", {"title": "Why does X?"})
    ab.record_variant("title_tests", "shocking_style", "vid124", {"title": "SHOCKING: X revealed"})
    
    # Update performance
    ab.update_performance("vid123", views=1000, likes=50)
    ab.update_performance("vid124", views=2000, likes=80)
    
    # Get best
    best = ab.get_best_variant("title_tests")
    print(f"Best title variant: {best}")
    
    # Generate report
    print(ab.generate_report())




