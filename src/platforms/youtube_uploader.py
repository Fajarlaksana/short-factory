#!/usr/bin/env python3
"""
YouTube Upload Module for ViralShorts
Automatically uploads generated videos to YouTube
"""

import os
import time
import json
import random
from pathlib import Path

# Google API
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Video categories
CATEGORY_ENTERTAINMENT = '24'
CATEGORY_EDUCATION = '27'
CATEGORY_PEOPLE_BLOGS = '22'


def get_youtube_client():
    """Create authenticated YouTube client using refresh token."""
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube credentials. Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
    
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    # Refresh the token
    credentials.refresh(Request())
    
    return build('youtube', 'v3', credentials=credentials)


def generate_title(question: dict) -> str:
    """Generate an engaging title for the video."""
    templates = [
        "Would You Rather: {a} OR {b}? 🤔",
        "{a} vs {b} - Which Would YOU Choose? 🔥",
        "99% Get This WRONG! {a} or {b}? 😱",
        "The HARDEST Choice: {a} vs {b} 💭",
        "{a} OR {b}? Vote NOW! 📊",
    ]
    
    template = random.choice(templates)
    
    # Shorten options if too long
    a = question['option_a'][:30] + "..." if len(question['option_a']) > 30 else question['option_a']
    b = question['option_b'][:30] + "..." if len(question['option_b']) > 30 else question['option_b']
    
    title = template.format(a=a, b=b)
    
    # Ensure title is under 100 characters
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title


def generate_description(question: dict) -> str:
    """Generate SEO-optimized description."""
    return f"""🤔 Would You Rather...

Option A: {question['option_a']}
Option B: {question['option_b']}

Vote in the comments! Which one would YOU choose?

📊 Results: {question.get('percentage_a', 50)}% chose A, {100 - question.get('percentage_a', 50)}% chose B

#shorts #wouldyourather #quiz #viral #trending #poll #vote #challenge

---
🔔 Subscribe for daily Would You Rather questions!
👍 Like if you want more!
💬 Comment your choice below!
"""


def generate_tags() -> list:
    """Generate relevant tags."""
    return [
        "would you rather",
        "shorts",
        "quiz",
        "viral",
        "trending",
        "poll",
        "vote",
        "challenge",
        "questions",
        "fun",
        "entertainment",
        "daily quiz",
        "brain teaser",
        "would you rather challenge",
        "this or that"
    ]


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list = None,
    category_id: str = CATEGORY_ENTERTAINMENT,
    privacy: str = "public",
    made_for_kids: bool = False
) -> dict:
    """
    Upload video to YouTube.
    
    Args:
        video_path: Path to video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags
        category_id: YouTube category ID
        privacy: 'public', 'private', or 'unlisted'
        made_for_kids: Whether video is made for kids
    
    Returns:
        dict with video ID and URL
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    youtube = get_youtube_client()
    
    body = {
        'snippet': {
            'title': title[:100],
            'description': description[:5000],
            'tags': tags or generate_tags(),
            'categoryId': category_id,
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': made_for_kids,
        }
    }
    
    # Create media upload object
    media = MediaFileUpload(
        video_path,
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024*1024  # 1MB chunks
    )
    
    print(f"📤 Uploading: {title}")
    print(f"   File: {video_path}")
    
    # Execute upload with retry
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    retries = 0
    max_retries = 3
    
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Progress: {progress}%")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504] and retries < max_retries:
                retries += 1
                wait_time = 2 ** retries
                print(f"   ⚠️ Server error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
    video_id = response['id']
    video_url = f"https://youtube.com/shorts/{video_id}"
    
    print(f"✅ Upload complete!")
    print(f"   Video ID: {video_id}")
    print(f"   URL: {video_url}")
    
    # Log the upload
    try:
        from content_log import log_upload
        log_upload(video_id, video_url, title)
    except Exception as e:
        print(f"   (Logging skipped: {e})")
    
    return {
        'id': video_id,
        'url': video_url,
        'title': title
    }


def upload_quiz_video(video_path: str, question: dict, privacy: str = "public") -> dict:
    """
    Upload a Would You Rather video with auto-generated metadata.
    """
    title = generate_title(question)
    description = generate_description(question)
    tags = generate_tags()
    
    return upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy=privacy
    )


if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py <video_path> [question_json]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        question = json.loads(sys.argv[2])
    else:
        question = {
            "option_a": "Test Option A",
            "option_b": "Test Option B",
            "percentage_a": 50
        }
    
    result = upload_quiz_video(video_path, question)
    print(json.dumps(result, indent=2))

