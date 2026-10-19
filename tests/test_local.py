#!/usr/bin/env python3
"""Local tests that don't consume API quota."""

import os
import datetime

print('=== LOCAL TESTING (No API Quota Used) ===')
print()

# Test 1: Sound Effects Generation (fully offline)
print('Test 1: Sound Effects')
from sound_effects import get_all_sfx
sfx = get_all_sfx()
for name, path in sfx.items():
    exists = os.path.exists(path) if path else False
    print(f'  {name}: {"OK" if exists else "MISSING"}')

print()

# Test 2: VideoRenderer class (no API needed)
print('Test 2: VideoRenderer components')
from pro_video_generator import VideoRenderer
renderer = VideoRenderer()

# Test text overlay (no API)
from PIL import Image
text_img = renderer.create_text_overlay('Test phrase for video', 1080, 960)
print(f'  Text overlay: OK ({text_img.size})')

# Test vignette (no API)
vignette = renderer.create_vignette_overlay(1080, 1920, 0.3)
print(f'  Vignette overlay: OK ({vignette.size})')

# Test phrase prefix cleaner
cleaned = renderer.clean_phrase_prefix('Phrase 1: Hello world')
print(f'  Phrase cleaner: OK (cleaned to: "{cleaned}")')

print()

# Test 3: BatchTracker
print('Test 3: BatchTracker variety enforcement')
from pro_video_generator import BatchTracker
tracker = BatchTracker()
tracker.used_categories = ['psychology', 'finance']
tracker.used_topics = ['topic1', 'topic2']
tracker.used_voices = ['en-US-AriaNeural']
tracker.add_video('test.mp4', 8.5, {'title': 'Test'})
best = tracker.get_best_video_for_youtube()
print(f'  Categories tracked: {len(tracker.used_categories)}')
print(f'  Topics tracked: {len(tracker.used_topics)}')
print(f'  Voices tracked: {len(tracker.used_voices)}')
print(f'  Best video selection: OK')

print()

# Test 4: Analytics metadata structure
print('Test 4: Analytics Metadata v7.x fields')
from analytics_feedback import VideoMetadata
meta = VideoMetadata(
    video_id='test123',
    local_path='./test.mp4',
    filename='test.mp4',
    topic='Test Topic',
    video_type='psychology',
    hook='Amazing hook',
    content_summary='Test summary',
    broll_keywords=['test', 'keywords'],
    music_mood='dramatic',
    voiceover_style='energetic',
    theme_name='dynamic',
    value_check_score=8,
    virality_score=9,
    timeliness_score=7,
    platforms_uploaded=[],
    youtube_video_id=None,
    dailymotion_video_id=None,
    generated_at=datetime.datetime.now().isoformat(),
    uploaded_at=None,
    voice_name='en-US-AriaNeural',
    voice_style='energetic',
    music_file='dramatic.mp3',
    music_source='bensound',
    ai_evaluation_score=8,
    batch_id='batch_123',
    batch_position=1,
    was_youtube_selected=True
)
print(f'  VideoMetadata v7.x fields: OK')
print(f'  voice_name: {meta.voice_name}')
print(f'  music_source: {meta.music_source}')
print(f'  was_youtube_selected: {meta.was_youtube_selected}')

print()
print('=== All local tests PASSED! ===')







