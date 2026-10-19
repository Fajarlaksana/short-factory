#!/usr/bin/env python3
"""
ViralShorts Factory - Multi-Platform Uploader
Uploads videos to multiple platforms simultaneously.

Supported Platforms:
- YouTube (via existing youtube_uploader.py)
- TikTok (via unofficial API)
- Instagram Reels (via Meta Graph API)
- Rumble (via web automation - no public API)

Note: Some platforms require manual setup or have rate limits.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try imports
try:
    from youtube_uploader import YouTubeUploader
    HAS_YOUTUBE = True
except ImportError:
    HAS_YOUTUBE = False


@dataclass
class UploadResult:
    """Result of an upload attempt."""
    platform: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class VideoMetadata:
    """Metadata for video upload."""
    title: str
    description: str
    tags: List[str]
    video_path: str
    thumbnail_path: Optional[str] = None
    is_short: bool = True  # For YouTube Shorts
    is_kids: bool = False  # For kids content


class MultiPlatformUploader:
    """Upload videos to multiple platforms."""
    
    def __init__(self):
        self.results: List[UploadResult] = []
        
        # Platform configurations
        self.platforms = {
            "youtube": {
                "enabled": HAS_YOUTUBE and os.environ.get("YOUTUBE_REFRESH_TOKEN"),
                "uploader": self._upload_youtube
            },
            "tiktok": {
                "enabled": os.environ.get("TIKTOK_SESSION_ID"),  # Requires session cookie
                "uploader": self._upload_tiktok
            },
            "instagram": {
                "enabled": os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
                "uploader": self._upload_instagram
            },
            "rumble": {
                "enabled": False,  # No public API - requires web automation
                "uploader": self._upload_rumble
            }
        }
    
    async def upload_all(self, metadata: VideoMetadata) -> List[UploadResult]:
        """Upload to all enabled platforms."""
        self.results = []
        
        print(f"\n{'='*60}")
        print(f"📤 Multi-Platform Upload: {metadata.title[:40]}...")
        print(f"{'='*60}")
        
        for platform, config in self.platforms.items():
            if config["enabled"]:
                print(f"\n📱 Uploading to {platform.upper()}...")
                try:
                    result = await config["uploader"](metadata)
                    self.results.append(result)
                    if result.success:
                        print(f"   ✅ Success: {result.url}")
                    else:
                        print(f"   ❌ Failed: {result.error}")
                except Exception as e:
                    self.results.append(UploadResult(
                        platform=platform,
                        success=False,
                        error=str(e)
                    ))
                    print(f"   ❌ Error: {e}")
            else:
                print(f"\n⏭️ Skipping {platform} (not configured)")
        
        return self.results
    
    async def _upload_youtube(self, metadata: VideoMetadata) -> UploadResult:
        """Upload to YouTube."""
        try:
            uploader = YouTubeUploader()
            
            # Prepare tags for Shorts
            tags = metadata.tags + ["shorts", "viralshorts"]
            
            video_id = uploader.upload_video(
                video_path=metadata.video_path,
                title=metadata.title[:100],  # YouTube title limit
                description=f"{metadata.description}\n\n#shorts #viral",
                tags=tags[:30],  # YouTube tag limit
                category_id="22",  # People & Blogs
                privacy_status="public"
            )
            
            if video_id:
                return UploadResult(
                    platform="youtube",
                    success=True,
                    video_id=video_id,
                    url=f"https://youtube.com/shorts/{video_id}"
                )
            else:
                return UploadResult(
                    platform="youtube",
                    success=False,
                    error="Upload returned no video ID"
                )
                
        except Exception as e:
            return UploadResult(
                platform="youtube",
                success=False,
                error=str(e)
            )
    
    async def _upload_tiktok(self, metadata: VideoMetadata) -> UploadResult:
        """
        Upload to TikTok.
        
        NOTE: TikTok doesn't have an official public API for uploads.
        Options:
        1. Use TikTok's Creator Portal (manual)
        2. Use browser automation (selenium)
        3. Use third-party services (paid)
        
        For now, this saves the video for manual upload.
        """
        try:
            # Create TikTok-ready folder
            tiktok_dir = Path("./output/tiktok_queue")
            tiktok_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy video with metadata
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = tiktok_dir / f"tiktok_{timestamp}.mp4"
            shutil.copy(metadata.video_path, dest_path)
            
            # Save caption for manual upload
            caption = f"{metadata.title}\n\n"
            caption += " ".join([f"#{tag}" for tag in metadata.tags[:10]])
            caption_path = tiktok_dir / f"tiktok_{timestamp}_caption.txt"
            caption_path.write_text(caption)
            
            return UploadResult(
                platform="tiktok",
                success=True,
                url=str(dest_path),
                error="Queued for manual upload (no API)"
            )
            
        except Exception as e:
            return UploadResult(
                platform="tiktok",
                success=False,
                error=str(e)
            )
    
    async def _upload_instagram(self, metadata: VideoMetadata) -> UploadResult:
        """
        Upload to Instagram Reels.
        
        Requires Meta Graph API access token with publish permissions.
        Steps to get token:
        1. Create Facebook App at developers.facebook.com
        2. Add Instagram Graph API
        3. Get long-lived access token
        4. Set INSTAGRAM_ACCESS_TOKEN env var
        """
        access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
        
        if not access_token or not ig_user_id:
            return UploadResult(
                platform="instagram",
                success=False,
                error="Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID"
            )
        
        try:
            import requests
            
            # Step 1: Upload video to container
            # Note: Instagram requires video to be hosted on a public URL
            # For local files, we'd need to upload to a temp hosting service first
            
            # Create Instagram-ready folder for manual upload
            ig_dir = Path("./output/instagram_queue")
            ig_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = ig_dir / f"ig_reel_{timestamp}.mp4"
            shutil.copy(metadata.video_path, dest_path)
            
            # Save caption
            caption = f"{metadata.title}\n\n"
            caption += " ".join([f"#{tag}" for tag in metadata.tags[:20]])
            caption_path = ig_dir / f"ig_reel_{timestamp}_caption.txt"
            caption_path.write_text(caption)
            
            return UploadResult(
                platform="instagram",
                success=True,
                url=str(dest_path),
                error="Queued for manual upload (API requires public URL hosting)"
            )
            
        except Exception as e:
            return UploadResult(
                platform="instagram",
                success=False,
                error=str(e)
            )
    
    async def _upload_rumble(self, metadata: VideoMetadata) -> UploadResult:
        """
        Upload to Rumble.
        
        Rumble has no public API. Options:
        1. Manual upload via web interface
        2. Browser automation (Selenium/Playwright)
        
        For now, this queues for manual upload.
        """
        try:
            rumble_dir = Path("./output/rumble_queue")
            rumble_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = rumble_dir / f"rumble_{timestamp}.mp4"
            shutil.copy(metadata.video_path, dest_path)
            
            # Save metadata
            meta_path = rumble_dir / f"rumble_{timestamp}_meta.json"
            with open(meta_path, 'w') as f:
                json.dump({
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags
                }, f, indent=2)
            
            return UploadResult(
                platform="rumble",
                success=True,
                url=str(dest_path),
                error="Queued for manual upload (no public API)"
            )
            
        except Exception as e:
            return UploadResult(
                platform="rumble",
                success=False,
                error=str(e)
            )
    
    def get_summary(self) -> str:
        """Get upload summary."""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        summary = f"\n{'='*60}\n"
        summary += f"📊 Upload Summary\n"
        summary += f"{'='*60}\n"
        summary += f"✅ Successful: {len(successful)}\n"
        for r in successful:
            summary += f"   - {r.platform}: {r.url}\n"
        summary += f"❌ Failed: {len(failed)}\n"
        for r in failed:
            summary += f"   - {r.platform}: {r.error}\n"
        
        return summary


# =============================================================================
# Platform Setup Instructions
# =============================================================================

PLATFORM_SETUP = """
🔧 PLATFORM SETUP INSTRUCTIONS
==============================

📺 YOUTUBE (Already configured)
   - Uses existing YouTube OAuth credentials
   - YOUTUBE_REFRESH_TOKEN environment variable

📱 TIKTOK
   - No public upload API exists
   - Videos are queued in output/tiktok_queue/
   - Manual upload required via TikTok app or web

📸 INSTAGRAM REELS
   - Requires Meta Business Suite access
   - Steps:
     1. Create app at developers.facebook.com
     2. Add Instagram Graph API product
     3. Get access token with 'instagram_content_publish' permission
     4. Set INSTAGRAM_ACCESS_TOKEN env var
   - Videos are queued in output/instagram_queue/

🎬 RUMBLE
   - No public API
   - Videos are queued in output/rumble_queue/
   - Manual upload at rumble.com

🔑 RECOMMENDED FREE ALTERNATIVES:
   - Buffer (free tier) - Schedule to multiple platforms
   - Later.com - Instagram scheduling
   - TubeBuddy - YouTube optimization
"""


async def upload_video_everywhere(video_path: str, title: str, 
                                  description: str, tags: List[str] = None) -> List[UploadResult]:
    """Convenience function to upload a video to all platforms."""
    uploader = MultiPlatformUploader()
    metadata = VideoMetadata(
        title=title,
        description=description,
        tags=tags or ["viral", "shorts", "trending"],
        video_path=video_path
    )
    
    results = await uploader.upload_all(metadata)
    print(uploader.get_summary())
    
    return results


if __name__ == "__main__":
    print(PLATFORM_SETUP)
    
    # Test with a sample video if exists
    test_video = "./output/test.mp4"
    if os.path.exists(test_video):
        asyncio.run(upload_video_everywhere(
            test_video,
            "Test Video",
            "Testing multi-platform upload",
            ["test", "demo"]
        ))
    else:
        print("\nNo test video found. Run a video generator first.")








