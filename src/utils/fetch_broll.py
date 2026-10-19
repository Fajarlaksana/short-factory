#!/usr/bin/env python3
"""Fetch B-roll videos from Pexels API."""
import os
import requests
import random
import time


def fetch_broll_videos():
    """Download B-roll videos from Pexels API."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        print('⚠️ No Pexels API key, will use gradient backgrounds')
        return
    
    # v17.9.3: Rate limiting for Pexels (200 req/hour = 18s between calls)
    try:
        from src.ai.model_helper import get_rate_limits
        PEXELS_DELAY = get_rate_limits().get("pexels", 18.0)
    except ImportError:
        PEXELS_DELAY = 18.0  # 200 requests/hour = 1 every 18 seconds
    
    # Create broll directory
    broll_dir = 'assets/broll'
    os.makedirs(broll_dir, exist_ok=True)
    
    headers = {'Authorization': api_key}
    
    # v17.6: Category-specific B-roll for better content matching
    # These are organized by our most popular content categories
    CATEGORY_BROLL = {
        'psychology': [
            'person thinking deeply', 'brain visualization', 'meditation mindfulness',
            'stressed person working', 'happy person smiling'
        ],
        'money': [
            'money bills counting', 'stock market trading', 'business success celebration',
            'piggy bank savings', 'entrepreneur working laptop'
        ],
        'productivity': [
            'person typing laptop', 'organized desk workspace', 'morning routine coffee',
            'to do list checking', 'time management clock'
        ],
        'health': [
            'healthy food salad', 'person exercising gym', 'running outdoor fitness',
            'yoga stretching', 'sleeping peacefully'
        ],
        'relationships': [
            'couple holding hands', 'friends laughing together', 'family dinner table',
            'conversation coffee shop', 'emotional connection'
        ],
        'generic': [
            'abstract motion', 'colorful particles', 'neon lights',
            'geometric patterns', 'gradient flow'
        ]
    }
    
    # Get queries from multiple categories for variety
    all_queries = []
    for category in ['psychology', 'money', 'productivity', 'generic']:
        all_queries.extend(CATEGORY_BROLL.get(category, [])[:2])
    
    # Shuffle for variety
    import random
    random.shuffle(all_queries)
    queries = all_queries[:10]  # Take top 10
    
    downloaded = 0
    for query in queries:
        if downloaded >= 10:  # v17.6: Increased from 3 to 10 for more variety
            break
        
        # v17.9.3: Rate limiting - wait between API calls
        time.sleep(PEXELS_DELAY)
            
        try:
            # Search for portrait/vertical videos
            url = f'https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=5'
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f'⚠️ API error for {query}: {response.status_code}')
                continue
            
            videos = response.json().get('videos', [])
            if not videos:
                print(f'⚠️ No videos found for: {query}')
                continue
            
            # Pick a random video
            video = random.choice(videos)
            video_files = video.get('video_files', [])
            
            # Find best quality (720p+)
            best = None
            for vf in video_files:
                height = vf.get('height', 0)
                if height >= 720:
                    if best is None or height < best.get('height', 9999):
                        best = vf
            
            if not best and video_files:
                best = video_files[0]
            
            if best:
                video_url = best.get('link')
                filename = query.replace(' ', '_').replace("'", "") + '.mp4'
                output_path = os.path.join(broll_dir, filename)
                
                print(f'📥 Downloading: {query}...')
                vid_response = requests.get(video_url, timeout=60)
                
                with open(output_path, 'wb') as f:
                    f.write(vid_response.content)
                
                # Verify file is valid
                if os.path.getsize(output_path) > 100000:  # At least 100KB
                    print(f'✅ Downloaded: {filename} ({os.path.getsize(output_path) / 1024 / 1024:.1f} MB)')
                    downloaded += 1
                else:
                    print(f'⚠️ File too small, removing: {filename}')
                    os.remove(output_path)
                    
        except Exception as e:
            print(f'⚠️ Error fetching {query}: {e}')
            continue
    
    # List downloaded files
    print('\n📁 B-roll files:')
    if os.path.exists(broll_dir):
        for f in os.listdir(broll_dir):
            filepath = os.path.join(broll_dir, f)
            if os.path.isfile(filepath):
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                print(f'  - {f} ({size_mb:.1f} MB)')
    else:
        print('  (none)')
    
    print(f'\n✅ Downloaded {downloaded} B-roll videos')


if __name__ == '__main__':
    fetch_broll_videos()










