#!/usr/bin/env python3
"""
Upload the latest video to Dailymotion ONLY (skip YouTube)
Used for maximizing Dailymotion uploads since it has higher daily limits
"""

import os
import sys
import json
import glob

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dailymotion_uploader import DailymotionUploader


def main():
    # Find the latest generated video
    video_files = glob.glob('output/*.mp4')
    if not video_files:
        print("[!] No videos found in output/")
        return
    
    # Sort by modification time, get latest
    latest_video = max(video_files, key=os.path.getmtime)
    meta_path = latest_video.replace('.mp4', '_meta.json')
    
    print(f"[*] Uploading to Dailymotion: {latest_video}")
    
    # Default metadata
    title = 'Amazing Fact'
    description = 'Follow for more amazing content!'
    tags = ['shorts', 'viral', 'facts']
    
    # Load metadata if available
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                data = json.load(f)
                metadata = data.get('metadata', {})
                title = metadata.get('title', title)[:100]
                description = metadata.get('description', description)
                raw_tags = metadata.get('hashtags', tags)
                tags = [h.replace('#', '') for h in raw_tags if h]
        except Exception as e:
            print(f"[!] Could not load metadata: {e}")
    
    # Upload to Dailymotion
    dm = DailymotionUploader()
    if not dm.is_configured:
        print("[!] Dailymotion not configured - skipping")
        return
    
    try:
        result = dm.upload_video(
            video_path=latest_video,
            title=title,
            description=description,
            tags=tags[:5],  # Dailymotion tag limit
            channel='lifestyle'
        )
        print(f"[OK] Dailymotion upload successful: {result}")
    except Exception as e:
        print(f"[!] Dailymotion upload failed: {e}")


if __name__ == '__main__':
    main()

