#!/usr/bin/env python3
"""
ViralShorts Factory - Platform Integrations
Integrates with free tools for multi-platform distribution.

Services:
- ShortSync: Multi-platform upload
- Taisly: Automated reposting
- Vubli: AI scheduling + SEO
- ImagineArt: AI kids video generation (kids content only)
"""

import os
import json
import webbrowser
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


# =============================================================================
# ShortSync Integration
# =============================================================================

class ShortSyncIntegration:
    """
    ShortSync - Upload once, post everywhere
    URL: https://shortsync.app
    
    Free Tier: 10 videos/month
    Paid: Unlimited
    
    Supported: YouTube, TikTok, Instagram, Facebook, Twitter
    """
    
    API_URL = "https://api.shortsync.app"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SHORTSYNC_API_KEY")
        self.is_configured = bool(self.api_key)
    
    def open_dashboard(self):
        """Open ShortSync dashboard for manual setup."""
        webbrowser.open("https://shortsync.app/dashboard")
        print("📱 Opening ShortSync dashboard...")
        print("   1. Sign up for free account")
        print("   2. Connect your social accounts")
        print("   3. Get API key from settings")
        print("   4. Set SHORTSYNC_API_KEY env variable")
    
    def queue_video(self, video_path: str, caption: str, hashtags: List[str],
                   platforms: List[str] = None) -> Dict:
        """
        Queue video for upload to multiple platforms.
        
        Note: ShortSync requires API key for programmatic access.
        For free tier, use their web interface.
        """
        if not self.is_configured:
            # Queue for manual upload via web
            queue_dir = Path("./output/shortsync_queue")
            queue_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Copy video
            dest = queue_dir / f"sync_{timestamp}.mp4"
            shutil.copy(video_path, dest)
            
            # Save metadata
            meta = {
                "caption": caption,
                "hashtags": hashtags,
                "platforms": platforms or ["youtube", "tiktok", "instagram"],
                "status": "pending_manual_upload"
            }
            (queue_dir / f"sync_{timestamp}.json").write_text(json.dumps(meta, indent=2))
            
            return {
                "success": True,
                "method": "manual_queue",
                "path": str(dest),
                "instructions": "Upload via shortsync.app/upload"
            }
        
        # API upload (requires paid plan)
        # TODO: Implement when API key available
        return {"success": False, "error": "API not implemented yet"}


# =============================================================================
# Taisly Integration
# =============================================================================

class TaislyIntegration:
    """
    Taisly - Automated reposting
    URL: https://taisly.com
    
    Features:
    - Auto-repost successful content
    - Schedule posts for optimal times
    - Cross-platform analytics
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("TAISLY_API_KEY")
        self.is_configured = bool(self.api_key)
    
    def open_dashboard(self):
        """Open Taisly for setup."""
        webbrowser.open("https://taisly.com")
        print("📱 Opening Taisly...")
        print("   Taisly automates reposting of your best content")
    
    def schedule_repost(self, video_url: str, delay_hours: int = 24):
        """Schedule a repost of existing content."""
        if not self.is_configured:
            print("⚠️ Taisly not configured - use web interface")
            return False
        
        # TODO: API implementation
        return True


# =============================================================================
# Vubli Integration
# =============================================================================

class VubliIntegration:
    """
    Vubli - AI scheduling + SEO optimization
    URL: https://vubli.ai
    
    Features:
    - AI-generated titles, descriptions, tags
    - Optimal scheduling
    - Performance analytics
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("VUBLI_API_KEY")
        self.is_configured = bool(self.api_key)
    
    def optimize_metadata(self, video_path: str, topic: str) -> Dict:
        """Use Vubli AI to optimize video metadata."""
        # Vubli provides AI optimization - for now return template
        return {
            "title": f"😱 {topic} - You Won't Believe This! #shorts",
            "description": f"{topic}\n\n#shorts #viral #trending #fyp",
            "tags": ["shorts", "viral", "trending", "fyp", topic.lower().split()[0]],
            "best_upload_time": "6:00 PM"  # Vubli would calculate this
        }


# =============================================================================
# ImagineArt Integration (Kids Content ONLY)
# =============================================================================

class ImagineArtIntegration:
    """
    ImagineArt - AI kids video generator
    URL: https://imagine.art/features/ai-kids-video-generator
    
    USE ONLY FOR: kids_content.py
    
    Features:
    - AI-generated animations
    - Kid-safe content
    - Colorful, engaging visuals
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("IMAGINEART_API_KEY")
        self.is_configured = bool(self.api_key)
    
    def generate_kids_animation(self, script: str, style: str = "cartoon") -> Optional[str]:
        """
        Generate animated kids video.
        
        Note: ImagineArt uses web interface for generation.
        This queues the script for manual processing.
        """
        queue_dir = Path("./output/imagineart_queue")
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        script_file = queue_dir / f"kids_script_{timestamp}.txt"
        script_file.write_text(f"""
KIDS ANIMATION REQUEST
======================
Style: {style}
Script:
{script}

Instructions:
1. Go to imagine.art/features/ai-kids-video-generator
2. Paste this script
3. Select "{style}" style
4. Generate and download
5. Save to output/ folder
""")
        
        print(f"📝 Kids animation script saved: {script_file}")
        print("   Use ImagineArt web interface to generate")
        
        return str(script_file)


# =============================================================================
# Unified Integration Manager
# =============================================================================

class PlatformIntegrationManager:
    """Manage all platform integrations."""
    
    def __init__(self):
        self.shortsync = ShortSyncIntegration()
        self.taisly = TaislyIntegration()
        self.vubli = VubliIntegration()
        self.imagineart = ImagineArtIntegration()
    
    def get_status(self) -> Dict:
        """Get configuration status of all integrations."""
        return {
            "ShortSync": "✅ Configured" if self.shortsync.is_configured else "⚠️ Manual mode",
            "Taisly": "✅ Configured" if self.taisly.is_configured else "⚠️ Manual mode",
            "Vubli": "✅ Configured" if self.vubli.is_configured else "⚠️ Manual mode",
            "ImagineArt": "✅ Configured" if self.imagineart.is_configured else "⚠️ Manual mode",
        }
    
    def distribute_video(self, video_path: str, metadata: Dict) -> Dict:
        """Distribute video across all configured platforms."""
        results = {}
        
        # Optimize metadata with Vubli
        optimized = self.vubli.optimize_metadata(video_path, metadata.get("topic", ""))
        
        # Queue to ShortSync
        shortsync_result = self.shortsync.queue_video(
            video_path,
            caption=optimized["description"],
            hashtags=optimized["tags"]
        )
        results["shortsync"] = shortsync_result
        
        return results
    
    def setup_all(self):
        """Open dashboards for all services."""
        print("\n" + "="*60)
        print("🔧 PLATFORM INTEGRATION SETUP")
        print("="*60)
        
        print("\n1️⃣ ShortSync - Multi-platform upload")
        print("   URL: https://shortsync.app")
        print("   Free: 10 videos/month")
        
        print("\n2️⃣ Taisly - Automated reposting")
        print("   URL: https://taisly.com")
        print("   Free tier available")
        
        print("\n3️⃣ Vubli - AI scheduling + SEO")
        print("   URL: https://vubli.ai")
        print("   Free tier available")
        
        print("\n4️⃣ ImagineArt - AI kids videos")
        print("   URL: https://imagine.art/features/ai-kids-video-generator")
        print("   Free generation")
        
        print("\n📋 After signing up, set these environment variables:")
        print("   SHORTSYNC_API_KEY=your_key")
        print("   TAISLY_API_KEY=your_key")
        print("   VUBLI_API_KEY=your_key")
        print("   IMAGINEART_API_KEY=your_key")


if __name__ == "__main__":
    manager = PlatformIntegrationManager()
    
    print("📊 Integration Status:")
    for name, status in manager.get_status().items():
        print(f"   {name}: {status}")
    
    manager.setup_all()








