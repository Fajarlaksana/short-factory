#!/usr/bin/env python3
"""
Content Logger - Tracks all uploaded content
Stores URLs and metadata in a JSON log file
"""

import os
import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("content_log.json")


def load_log() -> dict:
    """Load existing log or create new one."""
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return {"videos": [], "total_uploads": 0}


def save_log(log: dict):
    """Save log to file."""
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


def log_upload(
    video_id: str,
    video_url: str,
    title: str,
    question: dict = None,
    status: str = "success"
):
    """Log a video upload."""
    log = load_log()
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "video_id": video_id,
        "url": video_url,
        "title": title,
        "status": status,
    }
    
    if question:
        entry["question"] = question
    
    log["videos"].append(entry)
    log["total_uploads"] += 1
    log["last_upload"] = entry["timestamp"]
    
    save_log(log)
    
    print(f"📝 Logged: {video_url}")
    return entry


def get_recent_uploads(count: int = 10) -> list:
    """Get recent uploads."""
    log = load_log()
    return log["videos"][-count:]


def get_stats() -> dict:
    """Get upload statistics."""
    log = load_log()
    
    return {
        "total_uploads": log.get("total_uploads", 0),
        "last_upload": log.get("last_upload"),
        "recent": log["videos"][-5:] if log["videos"] else []
    }


def export_urls(output_file: str = "all_video_urls.txt"):
    """Export all video URLs to a text file."""
    log = load_log()
    
    with open(output_file, 'w') as f:
        f.write(f"# All ViralShorts Videos - {datetime.utcnow().isoformat()}\n\n")
        for video in log["videos"]:
            f.write(f"{video['url']} | {video['title']}\n")
    
    print(f"📁 Exported {len(log['videos'])} URLs to {output_file}")


if __name__ == "__main__":
    stats = get_stats()
    print(f"📊 Upload Stats:")
    print(f"   Total: {stats['total_uploads']}")
    print(f"   Last: {stats['last_upload']}")
    print(f"\n📹 Recent Uploads:")
    for v in stats['recent']:
        print(f"   • {v['url']}")



