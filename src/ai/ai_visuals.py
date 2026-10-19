#!/usr/bin/env python3
"""
AI Visual Generator
Uses HuggingFace FLUX to generate dynamic visuals instead of hardcoded ones.
v17.5: Updated to use huggingface_hub library (REST API deprecated)
"""

import os
from pathlib import Path
from typing import Optional
from PIL import Image
import hashlib

# HuggingFace settings
HF_TOKEN = os.getenv("HF_TOKEN", "") or os.getenv("HUGGINGFACE_API_KEY", "")
HF_MODEL = "black-forest-labs/FLUX.1-schnell"

# Cache directory for generated visuals
VISUALS_CACHE = Path("./assets/ai_visuals")
VISUALS_CACHE.mkdir(parents=True, exist_ok=True)


def generate_visual(prompt: str, size: tuple = (512, 512), 
                   cache: bool = True) -> Optional[Image.Image]:
    """
    Generate a visual using HuggingFace FLUX via huggingface_hub library.
    
    Args:
        prompt: Text description of the visual
        size: Output image size (width, height)
        cache: Whether to cache the result
        
    Returns:
        PIL Image or None if failed
    """
    if not HF_TOKEN:
        print("   [!] No HF_TOKEN/HUGGINGFACE_API_KEY, cannot generate AI visuals")
        return None
    
    # Create cache key from prompt
    cache_key = hashlib.md5(prompt.encode()).hexdigest()[:12]
    cache_path = VISUALS_CACHE / f"{cache_key}.png"
    
    # Check cache first
    if cache and cache_path.exists():
        print(f"   [OK] Using cached AI visual: {cache_key}")
        return Image.open(cache_path)
    
    try:
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=HF_TOKEN)
        
        print(f"   [*] Generating AI visual: {prompt[:50]}...")
        
        # Use text_to_image method (new API)
        img = client.text_to_image(
            prompt=prompt,
            model=HF_MODEL,
            width=size[0],
            height=size[1]
        )
        
        # Resize if needed
        if img.size != size:
            img = img.resize(size, Image.LANCZOS)
        
        # Cache the result
        if cache:
            img.save(cache_path, "PNG")
            print(f"   [OK] Cached AI visual: {cache_key}")
        
        return img
            
    except Exception as e:
        print(f"   [!] AI visual generation failed: {e}")
        return None


def generate_vs_badge(theme_colors: tuple = (255, 100, 100), 
                      style: str = "gaming") -> Optional[Image.Image]:
    """
    Generate a dynamic VS badge using AI.
    
    Args:
        theme_colors: RGB color tuple for theme
        style: Visual style (gaming, neon, elegant, fire)
    """
    style_prompts = {
        "gaming": "gaming VS icon, glowing neon, esports style, dramatic lighting, transparent background",
        "neon": "neon VS symbol, cyberpunk style, glowing electric blue and pink, dark background",
        "elegant": "elegant VS badge, gold and black, premium quality, minimalist design",
        "fire": "VS text on fire, dramatic flames, epic battle, black background",
        "retro": "retro 80s VS icon, synthwave colors, vintage gaming aesthetic",
    }
    
    prompt = style_prompts.get(style, style_prompts["gaming"])
    prompt = f"{prompt}, centered, isolated, high contrast, vector art style"
    
    return generate_visual(prompt, size=(256, 256))


def generate_countdown_visual(number: int, style: str = "neon") -> Optional[Image.Image]:
    """
    Generate a countdown number visual.
    """
    style_prompts = {
        "neon": f"large glowing neon number {number}, pink and blue gradient, dark background, centered",
        "fire": f"number {number} made of fire, dramatic flames, black background, centered",
        "ice": f"frozen number {number}, ice and frost effect, cold blue, centered",
        "gold": f"golden 3D number {number}, luxury premium style, dark background, centered",
    }
    
    prompt = style_prompts.get(style, style_prompts["neon"])
    return generate_visual(prompt, size=(256, 256))


def generate_option_label(label: str, style: str = "modern") -> Optional[Image.Image]:
    """
    Generate a dynamic option label (A, B, etc).
    """
    styles = {
        "modern": f"modern option {label} badge, glassmorphism, gradient, centered",
        "gaming": f"gaming option {label} icon, RGB lights, esports style, centered",
        "minimal": f"minimal {label} letter, clean typography, subtle shadow, centered",
    }
    
    prompt = styles.get(style, styles["modern"])
    return generate_visual(prompt, size=(128, 128))


def generate_hook_visual(topic: str) -> Optional[Image.Image]:
    """
    Generate a hook/intro visual based on the topic.
    
    This creates unique thumbnails for each video topic.
    """
    prompt = f"dramatic thumbnail for '{topic}', viral youtube style, eye-catching, question mark, neon glow, centered"
    return generate_visual(prompt, size=(512, 512))


# Testing
if __name__ == "__main__":
    print("Testing AI Visual Generator...")
    
    # Test VS badge
    vs = generate_vs_badge(style="neon")
    if vs:
        vs.save("test_vs_badge.png")
        print("✅ VS badge generated!")
    
    # Test countdown
    cd = generate_countdown_visual(3, style="fire")
    if cd:
        cd.save("test_countdown.png")
        print("✅ Countdown generated!")









