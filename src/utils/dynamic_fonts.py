#!/usr/bin/env python3
"""
Dynamic Font Manager for ViralShorts Factory
=============================================

PROBLEM: Hardcoded font paths fail on different systems
SOLUTION: Download free fonts dynamically and cache them

Uses Google Fonts (free, open source) with automatic download.
"""

import os
import requests
from pathlib import Path
from typing import Optional, List, Dict

# Font cache directory
FONTS_DIR = Path("./assets/fonts")
FONTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# FREE FONTS with direct download URLs (from Google Fonts CDN)
# All fonts are Open Font License (OFL) - completely free!
FREE_FONTS = {
    # Bold, impactful fonts for short videos
    "bebas-neue": {
        "name": "Bebas Neue",
        "url": "https://fonts.gstatic.com/s/bebasneue/v14/JTUSjIg69CK48gW7PXoo9Wdhyzbi.ttf",
        "style": "bold_impact"
    },
    "oswald-bold": {
        "name": "Oswald Bold",
        "url": "https://fonts.gstatic.com/s/oswald/v53/TK3_WkUHHAIjg75cFRf3bXL8LICs1xZosUZiYQ.ttf",
        "style": "bold_impact"
    },
    "anton": {
        "name": "Anton",
        "url": "https://fonts.gstatic.com/s/anton/v25/1Ptgg87LROyAm3Kz-C8.ttf",
        "style": "bold_impact"
    },
    "montserrat-bold": {
        "name": "Montserrat Bold",
        "url": "https://fonts.gstatic.com/s/montserrat/v26/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCuM70w-Y3tcoqK5.ttf",
        "style": "modern"
    },
    "roboto-bold": {
        "name": "Roboto Bold",
        "url": "https://fonts.gstatic.com/s/roboto/v32/KFOlCnqEu92Fr1MmWUlfBBc4AMP6lQ.ttf",
        "style": "modern"
    },
    "poppins-bold": {
        "name": "Poppins Bold",
        "url": "https://fonts.gstatic.com/s/poppins/v21/pxiByp8kv8JHgFVrLCz7Z1JlFd2JQEl8qw.ttf",
        "style": "modern"
    },
    "nunito-bold": {
        "name": "Nunito Bold",
        "url": "https://fonts.gstatic.com/s/nunito/v26/XRXI3I6Li01BKofiOc5wtlZ2di8HDLshdTk3j77e.ttf",
        "style": "friendly"
    },
    "bangers": {
        "name": "Bangers",
        "url": "https://fonts.gstatic.com/s/bangers/v24/FeVQS0BTqb0h60ACH5Q.ttf",
        "style": "fun_comic"
    },
    "permanent-marker": {
        "name": "Permanent Marker",
        "url": "https://fonts.gstatic.com/s/permanentmarker/v16/Fh4uPib9Iyv2ucM6pGQMWimMp004La2Cfw.ttf",
        "style": "handwritten"
    },
    "archivo-black": {
        "name": "Archivo Black",
        "url": "https://fonts.gstatic.com/s/archivoblack/v21/HTxqL289NzCGg4MzN6KJ7eW6OYuP_x7yx3A.ttf",
        "style": "bold_impact"
    }
}

# Fallback to system fonts if downloads fail
SYSTEM_FONT_PATHS = {
    "windows": [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ],
    "darwin": [  # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
}


class DynamicFontManager:
    """Manages dynamic font downloading and caching."""
    
    def __init__(self):
        self.cached_fonts: Dict[str, str] = {}
        self._load_cached_fonts()
    
    def _load_cached_fonts(self):
        """Load already cached fonts."""
        for font_file in FONTS_DIR.glob("*.ttf"):
            font_name = font_file.stem
            self.cached_fonts[font_name] = str(font_file)
    
    def download_font(self, font_key: str) -> Optional[str]:
        """Download a font from Google Fonts CDN."""
        if font_key not in FREE_FONTS:
            return None
        
        font_info = FREE_FONTS[font_key]
        font_path = FONTS_DIR / f"{font_key}.ttf"
        
        # Check cache
        if font_path.exists() and font_path.stat().st_size > 1000:
            return str(font_path)
        
        try:
            safe_print(f"   [*] Downloading font: {font_info['name']}...")
            response = requests.get(font_info["url"], timeout=30)
            
            if response.status_code == 200:
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                
                if font_path.stat().st_size > 1000:
                    safe_print(f"   [OK] Font cached: {font_key}")
                    self.cached_fonts[font_key] = str(font_path)
                    return str(font_path)
        except Exception as e:
            safe_print(f"   [!] Font download failed: {e}")
        
        return None
    
    def get_best_font(self, style: str = "bold_impact") -> str:
        """
        Get the best available font for the specified style.
        Downloads if necessary.
        
        Styles: bold_impact, modern, friendly, fun_comic, handwritten
        """
        # Priority: Downloaded fonts > System fonts
        
        # Try to get a font matching the style
        style_fonts = [k for k, v in FREE_FONTS.items() if v.get("style") == style]
        
        # Try each font in order
        for font_key in style_fonts:
            # Check cache first
            if font_key in self.cached_fonts:
                font_path = self.cached_fonts[font_key]
                if os.path.exists(font_path):
                    return font_path
            
            # Try to download
            font_path = self.download_font(font_key)
            if font_path:
                return font_path
        
        # Try any cached font
        for font_path in self.cached_fonts.values():
            if os.path.exists(font_path):
                return font_path
        
        # Fall back to system fonts
        return self._get_system_font()
    
    def _get_system_font(self) -> str:
        """Get a system font as fallback."""
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            paths = SYSTEM_FONT_PATHS["windows"]
        elif system == "darwin":
            paths = SYSTEM_FONT_PATHS["darwin"]
        else:
            paths = SYSTEM_FONT_PATHS["linux"]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Ultimate fallback
        return paths[0] if paths else ""
    
    def get_impact_font(self) -> str:
        """Get a bold, impactful font for video text."""
        return self.get_best_font("bold_impact")
    
    def get_modern_font(self) -> str:
        """Get a modern, clean font."""
        return self.get_best_font("modern")
    
    def get_fun_font(self) -> str:
        """Get a fun, playful font."""
        return self.get_best_font("fun_comic")
    
    def ensure_fonts_available(self) -> List[str]:
        """
        Pre-download essential fonts.
        Call this during setup to ensure fonts are available.
        """
        downloaded = []
        essential = ["bebas-neue", "oswald-bold", "anton", "montserrat-bold"]
        
        for font_key in essential:
            path = self.download_font(font_key)
            if path:
                downloaded.append(font_key)
        
        return downloaded


# Global font manager instance
_font_manager = None

def get_font_manager() -> DynamicFontManager:
    """Get or create the font manager singleton."""
    global _font_manager
    if _font_manager is None:
        _font_manager = DynamicFontManager()
    return _font_manager


def get_best_font(style: str = "bold_impact") -> str:
    """
    Convenience function to get the best font for a style.
    
    Usage:
        font_path = get_best_font("bold_impact")
        font = ImageFont.truetype(font_path, 64)
    """
    return get_font_manager().get_best_font(style)


def get_impact_font() -> str:
    """Get a bold, impactful font for video text overlays."""
    return get_font_manager().get_impact_font()


def get_font_by_key(font_key: str) -> Optional[str]:
    """
    Get a specific font by its key name.
    This is used by the AI-selected font system.
    
    Args:
        font_key: One of the keys from FREE_FONTS (e.g., "bebas-neue", "poppins-bold")
    
    Returns:
        Path to the font file, or None if download fails
    """
    manager = get_font_manager()
    
    # Check if already cached
    if font_key in manager.cached_fonts:
        font_path = manager.cached_fonts[font_key]
        if os.path.exists(font_path):
            return font_path
    
    # Try to download
    return manager.download_font(font_key)


if __name__ == "__main__":
    print("Testing Dynamic Font Manager...")
    
    manager = DynamicFontManager()
    
    # Pre-download essential fonts
    print("\nDownloading essential fonts...")
    downloaded = manager.ensure_fonts_available()
    print(f"Downloaded: {downloaded}")
    
    # Test getting fonts by style
    print("\nTesting font retrieval...")
    for style in ["bold_impact", "modern", "fun_comic", "friendly"]:
        font_path = manager.get_best_font(style)
        exists = os.path.exists(font_path) if font_path else False
        print(f"  {style}: {font_path} (exists: {exists})")





