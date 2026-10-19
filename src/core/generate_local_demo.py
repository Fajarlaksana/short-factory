#!/usr/bin/env python3
"""
Generate FULL-QUALITY demo videos locally.

Run with: python generate_local_demo.py --groq YOUR_GROQ_KEY
"""

import asyncio
import os
import sys
import argparse
import random
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate local demo videos with full quality")
    parser.add_argument("--groq", required=True, help="Your GROQ API key (gsk_...)")
    parser.add_argument("--count", type=int, default=2, help="Number of videos to generate")
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["GROQ_API_KEY"] = args.groq
    os.environ["PEXELS_API_KEY"] = "OjsBhrmg2dDB5Pg1F4xJmlbvxt483A7eUzJfEh4NJYA0tO3kv2esmacN"
    
    print("=" * 60)
    print("ViralShorts Factory - FULL QUALITY Local Demo")
    print("=" * 60)
    print(f"GROQ API: {'Set' if os.environ.get('GROQ_API_KEY') else 'Missing'}")
    print(f"Pexels API: {'Set' if os.environ.get('PEXELS_API_KEY') else 'Missing'}")
    print(f"Videos to generate: {args.count}")
    print("=" * 60)
    
    asyncio.run(generate_videos(args.count))


async def generate_videos(count: int):
    """Generate videos with full AI and B-roll support."""
    
    # Import after setting env vars
    from master_prompts import MasterContentGenerator, strip_emojis
    from dynamic_video_generator import DynamicVideoGenerator
    from groq import Groq
    
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize AI
    print("\n[1] Initializing AI...")
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("ERROR: GROQ_API_KEY not set!")
        return
    
    client = Groq(api_key=groq_key)
    
    # Test AI connection
    try:
        test = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'OK' in one word"}],
            max_tokens=10
        )
        print(f"   [OK] AI Connected: {test.choices[0].message.content}")
    except Exception as e:
        print(f"   [ERROR] AI Connection failed: {e}")
        return
    
    # Generate topics with master prompts
    print("\n[2] Generating viral topics with master prompts...")
    gen = MasterContentGenerator()
    gen.groq_client = client
    
    topics = gen.generate_viral_topics(count)
    
    if not topics:
        print("   [ERROR] No topics generated!")
        return
    
    print(f"   [OK] Generated {len(topics)} topics")
    
    # Initialize video generator with enhancements
    print("\n[3] Initializing video generator...")
    video_gen = DynamicVideoGenerator(enable_enhancements=True)
    
    # Generate each video
    generated = []
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*50}")
        print(f"[Video {i}/{count}]")
        print(f"   Topic: {topic.get('topic', 'Unknown')}")
        print(f"   Type: {topic.get('video_type', 'Unknown')}")
        print(f"   Hook: {topic.get('hook', '')[:50]}...")
        print(f"   B-roll: {topic.get('broll_keywords', [])}")
        print(f"   Music: {topic.get('music_mood', 'dramatic')}")
        
        output_path = str(output_dir / f"fullquality_{topic.get('video_type', 'fact')}_{random.randint(1000, 9999)}.mp4")
        
        try:
            success = await video_gen.generate_dynamic_video(topic, output_path)
            if success:
                generated.append(output_path)
                print(f"   [OK] Created: {output_path}")
            else:
                print(f"   [FAIL] Generation failed")
        except Exception as e:
            print(f"   [ERROR] {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Videos created: {len(generated)}/{count}")
    
    for path in generated:
        print(f"   -> {path}")
    
    if generated:
        print(f"\nOpening output folder...")
        os.system(f'explorer "{output_dir}"')


if __name__ == "__main__":
    main()




