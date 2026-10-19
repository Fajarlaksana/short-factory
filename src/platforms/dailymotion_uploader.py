#!/usr/bin/env python3
"""
ViralShorts Factory - Dailymotion Uploader
FULLY AUTONOMOUS video upload to Dailymotion.

=============================================================================
DAILYMOTION SHORTS SUPPORT - WHAT YOU NEED TO KNOW
=============================================================================

Q: Does Dailymotion have "Shorts" like YouTube/TikTok?
A: Sort of! Dailymotion supports vertical videos (9:16 aspect ratio) but doesn't
   have a dedicated "Shorts" section like YouTube. However:
   
   - Vertical videos ARE supported and play well on mobile
   - Short videos (< 60 seconds) work fine
   - They get good visibility on mobile app
   - Same content can be uploaded as YouTube/TikTok

Q: Should we upload the same content as YouTube?
A: YES! The same vertical short videos work on Dailymotion. Benefits:
   - More reach with same content
   - Dailymotion has ~400M monthly users
   - Lower competition than YouTube
   - Monetization available

Q: Daily upload limits?
A: Free tier: ~50 uploads per day (more than enough!)

=============================================================================
SETUP INSTRUCTIONS
=============================================================================

1. Create account at dailymotion.com
2. Go to: https://www.dailymotion.com/settings/developer
3. Create an API Key
4. Set GitHub Secrets:
   - DAILYMOTION_API_KEY (client ID)
   - DAILYMOTION_API_SECRET (client secret)
   - DAILYMOTION_USERNAME (your login email)
   - DAILYMOTION_PASSWORD (your password)

Note: API key and secret are already set! You just need to add:
- DAILYMOTION_USERNAME
- DAILYMOTION_PASSWORD
"""

import os
import requests
from typing import Optional, Dict
from pathlib import Path


def safe_print(msg: str):
    """Print with fallback for Windows encoding issues."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Remove emojis for Windows compatibility
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '', msg)
        print(clean)


class DailymotionUploader:
    """Upload videos to Dailymotion autonomously."""
    
    AUTH_URL = "https://api.dailymotion.com/oauth/token"
    UPLOAD_URL = "https://api.dailymotion.com/file/upload"
    VIDEO_URL = "https://api.dailymotion.com/me/videos"
    
    def __init__(self):
        self.api_key = os.environ.get("DAILYMOTION_API_KEY")
        self.api_secret = os.environ.get("DAILYMOTION_API_SECRET")
        self.username = os.environ.get("DAILYMOTION_USERNAME")
        self.password = os.environ.get("DAILYMOTION_PASSWORD")
        self.access_token = None
        
        self.is_configured = all([
            self.api_key, self.api_secret, self.username, self.password
        ])
    
    def check_connectivity(self) -> Dict:
        """
        Check Dailymotion connectivity WITHOUT using upload quota.
        Just tests authentication - doesn't upload anything.
        """
        if not self.is_configured:
            return {"status": "not_configured", "message": "Missing credentials"}
        
        try:
            # Just test authentication
            response = requests.post(self.AUTH_URL, data={
                "grant_type": "password",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
                "username": self.username,
                "password": self.password,
                "scope": "manage_videos"
            }, timeout=15)
            
            data = response.json()
            
            if response.status_code == 200 and "access_token" in data:
                self.access_token = data["access_token"]
                return {
                    "status": "ok",
                    "message": "Dailymotion connected",
                    "has_token": True
                }
            else:
                error = data.get("error_description", data.get("error", "Unknown"))
                return {
                    "status": "auth_failed",
                    "message": f"Auth failed: {error}"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def authenticate(self) -> bool:
        """Get access token."""
        if not self.is_configured:
            safe_print("[X] Dailymotion not configured")
            return False
        
        try:
            response = requests.post(self.AUTH_URL, data={
                "grant_type": "password",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
                "username": self.username,
                "password": self.password,
                "scope": "manage_videos"
            }, timeout=30)
            
            data = response.json()
            
            if response.status_code == 200 and "access_token" in data:
                self.access_token = data["access_token"]
                safe_print(f"[OK] Dailymotion authenticated (token length: {len(self.access_token)})")
                return True
            else:
                error = data.get("error_description", data.get("error", response.text[:200]))
                safe_print(f"[X] Dailymotion auth failed: {error}")
                return False
                
        except requests.exceptions.Timeout:
            safe_print("[X] Dailymotion auth timeout")
            return False
        except Exception as e:
            safe_print(f"[X] Auth error: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str,
                    tags: list = None, channel: str = "lifestyle", 
                    ai_generated: bool = False) -> Optional[str]:
        """
        Upload video to Dailymotion.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            channel: Dailymotion channel category
            
        Returns:
            Video ID if successful, None otherwise
        """
        if not self.access_token:
            if not self.authenticate():
                return None
        
        video_path = Path(video_path)
        if not video_path.exists():
            safe_print(f"[X] Video not found: {video_path}")
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            # Step 1: Get upload URL
            safe_print(f"[*] Getting upload URL...")
            response = requests.get(self.UPLOAD_URL, headers=headers)
            
            if response.status_code != 200:
                safe_print(f"[X] Failed to get upload URL: {response.text[:100]}")
                return None
            
            upload_data = response.json()
            upload_url = upload_data.get("upload_url")
            
            # Step 2: Upload the file
            safe_print(f"[*] Uploading {video_path.name}...")
            with open(video_path, "rb") as f:
                files = {"file": (video_path.name, f, "video/mp4")}
                response = requests.post(upload_url, files=files, timeout=300)
            
            if response.status_code != 200:
                safe_print(f"[X] Upload failed: {response.text[:100]}")
                return None
            
            file_url = response.json().get("url")
            
            # Step 3: Create video entry
            safe_print(f"[*] Creating video entry...")
            
            # Clean and format tags properly
            if tags:
                clean_tags = [t.replace('#', '').strip() for t in tags if t.strip()]
                # Dailymotion requires tags without special chars
                clean_tags = [t for t in clean_tags if t.isalnum() or ' ' in t]
                tags_str = ",".join(clean_tags[:10])  # Max 10 tags
            else:
                tags_str = "viral,shorts,trending,facts"
            
            # Simplified video data - some fields may cause 403
            video_data = {
                "url": file_url,
                "title": title[:100],  # Keep shorter for safety
                "tags": tags_str,
                "channel": "lifestyle",  # Use fixed channel
                "published": "true",
                "is_created_for_kids": "false",  # Required field! (v7.13 fix)
            }
            
            # Only add description if not empty
            if description:
                # Remove special chars that might cause issues
                clean_desc = description[:500].replace('\n', ' ').strip()
                video_data["description"] = clean_desc
            
            response = requests.post(
                self.VIDEO_URL,
                headers=headers,
                data=video_data,
                timeout=60  # Add timeout
            )
            
            if response.status_code in [200, 201]:
                video_id = response.json().get("id")
                video_url = f"https://www.dailymotion.com/video/{video_id}"
                safe_print(f"[OK] Uploaded to Dailymotion: {video_url}")
                return video_id
            else:
                # Log FULL error for debugging
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text[:200])
                    error_code = error_data.get('error', {}).get('code', response.status_code)
                    safe_print(f"[X] Dailymotion error {error_code}: {error_msg}")
                except:
                    safe_print(f"[X] Failed to create video (HTTP {response.status_code}): {response.text[:200]}")
                return None
                
        except Exception as e:
            safe_print(f"[X] Upload error: {e}")
            return None
    
    def get_upload_limit_status(self) -> Dict:
        """Check daily upload limits."""
        if not self.access_token:
            if not self.authenticate():
                return {"error": "Not authenticated"}
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                "https://api.dailymotion.com/me?fields=limits",
                headers=headers
            )
            return response.json()
        except:
            return {"error": "Failed to get limits"}


def upload_to_dailymotion(video_path: str, title: str, 
                          description: str, tags: list = None) -> Optional[str]:
    """Convenience function for uploading."""
    uploader = DailymotionUploader()
    if uploader.is_configured:
        return uploader.upload_video(video_path, title, description, tags)
    else:
        print("⚠️ Dailymotion not configured. Set these env vars:")
        print("   DAILYMOTION_API_KEY")
        print("   DAILYMOTION_API_SECRET")
        print("   DAILYMOTION_USERNAME")
        print("   DAILYMOTION_PASSWORD")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📺 Dailymotion Uploader - Setup Check")
    print("=" * 60)
    
    uploader = DailymotionUploader()
    
    if uploader.is_configured:
        print("✅ Dailymotion is configured!")
        if uploader.authenticate():
            limits = uploader.get_upload_limit_status()
            print(f"📊 Account limits: {limits}")
    else:
        print("""
❌ Dailymotion NOT configured

To set up:
1. Create account at dailymotion.com
2. Go to: https://www.dailymotion.com/settings/developer
3. Click "Create a new API key"
4. Set these environment variables:

   DAILYMOTION_API_KEY=your_key
   DAILYMOTION_API_SECRET=your_secret
   DAILYMOTION_USERNAME=your_email
   DAILYMOTION_PASSWORD=your_password

5. Add to GitHub Secrets for workflow automation
""")

