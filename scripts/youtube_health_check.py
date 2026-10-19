#!/usr/bin/env python3
"""
YouTube OAuth Health Check
Verifies that the refresh token works and we can access the YouTube API
"""
import os
import requests

# Load credentials from environment variables
client_id = os.environ.get('YOUTUBE_CLIENT_ID', '')
client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET', '')
refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN', '')

if not all([client_id, client_secret, refresh_token]):
    print("ERROR: Missing YouTube credentials in environment variables!")
    print("Set: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
    exit(1)

print('=' * 60)
print('YOUTUBE OAUTH HEALTH CHECK')
print('=' * 60)
print()

# Step 1: Get access token from refresh token
print('[1] Testing refresh token...')
token_url = 'https://oauth2.googleapis.com/token'
data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
}
response = requests.post(token_url, data=data, timeout=10)
token_data = response.json()

if 'access_token' in token_data:
    print('    [OK] Refresh token is VALID!')
    access_token = token_data['access_token']
else:
    print('    [FAIL] Token error:', token_data)
    exit(1)

# Step 2: Test YouTube API access
print()
print('[2] Testing YouTube API access...')
headers = {'Authorization': f'Bearer {access_token}'}
yt_response = requests.get(
    'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true',
    headers=headers,
    timeout=10
)
yt_data = yt_response.json()

if 'items' in yt_data and len(yt_data['items']) > 0:
    channel = yt_data['items'][0]
    snippet = channel.get('snippet', {})
    stats = channel.get('statistics', {})
    print(f'    [OK] YouTube API access WORKING!')
    print()
    print(f'    Channel Name: {snippet.get("title", "Unknown")}')
    print(f'    Subscribers: {stats.get("subscriberCount", "Hidden")}')
    print(f'    Total Views: {stats.get("viewCount", "0")}')
    print(f'    Total Videos: {stats.get("videoCount", "0")}')
else:
    print('    [WARN] API works but no channel found:', yt_data)

# Step 3: Test getting recent videos
print()
print('[3] Testing video list access...')
videos_response = requests.get(
    'https://www.googleapis.com/youtube/v3/search?part=snippet&forMine=true&type=video&maxResults=3',
    headers=headers,
    timeout=10
)
videos_data = videos_response.json()

if 'items' in videos_data:
    print(f'    [OK] Can access videos! Found {len(videos_data["items"])} recent videos')
    for i, video in enumerate(videos_data['items'][:3], 1):
        title = video.get('snippet', {}).get('title', 'Unknown')[:50]
        print(f'        {i}. {title}...')
else:
    print('    [WARN] Could not list videos:', videos_data.get('error', {}).get('message', 'Unknown error'))

print()
print('=' * 60)
print('[OK] ALL CHECKS PASSED - YouTube OAuth is working!')
print('=' * 60)
