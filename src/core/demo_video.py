#!/usr/bin/env python3
"""
Demo video generator to showcase v3.0 enhancements locally.
"""

import asyncio
import os
import random
from pathlib import Path

# Set Pexels key
os.environ["PEXELS_API_KEY"] = "OjsBhrmg2dDB5Pg1F4xJmlbvxt483A7eUzJfEh4NJYA0tO3kv2esmacN"

async def generate_demo_video():
    print("=" * 60)
    print("ViralShorts Factory - v3.0 Demo Video Generator")
    print("=" * 60)
    
    # Import generator
    from dynamic_video_generator import DynamicVideoGenerator
    
    # Sample viral content (pre-written to avoid AI dependency)
    demo_topics = [
        {
            "topic": "Psychology Hack",
            "video_type": "psychology_fact",
            "hook": "Your brain deletes 90% of your memories while you sleep",
            "content": "Every night, your brain decides what to keep and what to erase. Studies show emotional memories survive, but boring ones get deleted. This is why you remember your first kiss but not what you had for lunch last Tuesday. Want to remember more? Link new info to strong emotions.",
            "broll_keywords": ["brain neural network", "person sleeping", "memory flashback", "studying learning"],
            "music_mood": "suspense",
            "the_payoff": "Link new information to emotions to remember better",
            "call_to_action": "What's your earliest memory?",
            "_source": "demo"
        },
        {
            "topic": "Money Secret",
            "video_type": "money_fact",
            "hook": "Rich people buy time, poor people buy things",
            "content": "Warren Buffett pays someone to mow his lawn. Why? Because his hour is worth $400,000. If you make $20/hour and spend 3 hours cleaning, that's $60. Pay someone $40 to clean, then use those 3 hours to build a side hustle. That's how wealth compounds.",
            "broll_keywords": ["wealthy businessman", "money growing", "time clock", "investment growth"],
            "music_mood": "inspirational",
            "the_payoff": "Calculate your hourly rate and outsource tasks below it",
            "call_to_action": "What would you outsource first?",
            "_source": "demo"
        },
        {
            "topic": "Scary Truth",
            "video_type": "scary_fact",
            "hook": "You've walked past 36 murderers in your lifetime",
            "content": "Based on FBI statistics and average life encounters, the math is disturbing. In a city of 1 million, there are roughly 50 active killers. Over 80 years of walking past strangers, the probability is near certain. That person on the subway? You'll never know.",
            "broll_keywords": ["dark street walking", "crowd strangers", "suspenseful shadow", "city night"],
            "music_mood": "dramatic",
            "the_payoff": "The statistical reality of urban living",
            "call_to_action": "Does this change how you see strangers?",
            "_source": "demo"
        }
    ]
    
    # Pick one random topic
    topic = random.choice(demo_topics)
    
    print(f"\n📹 Generating: {topic['topic']}")
    print(f"   Type: {topic['video_type']}")
    print(f"   Hook: {topic['hook']}")
    print(f"   Mood: {topic['music_mood']}")
    
    # Initialize generator with v3.0 enhancements
    gen = DynamicVideoGenerator(enable_enhancements=True)
    
    # Generate video
    output_path = f"./output/demo_{topic['video_type']}_{random.randint(1000, 9999)}.mp4"
    
    print(f"\n🎬 Generating with v3.0 enhancements:")
    print(f"   ✓ TikTok-style captions")
    print(f"   ✓ Progress bar overlay")
    print(f"   ✓ Ken Burns zoom")
    print(f"   ✓ Vignette effect")
    print(f"   ✓ Per-phrase B-roll")
    
    success = await gen.generate_dynamic_video(topic, output_path)
    
    if success:
        print(f"\n✅ VIDEO CREATED: {output_path}")
        print(f"   Open this file to see the v3.0 quality!")
        return output_path
    else:
        print(f"\n❌ Generation failed")
        return None


if __name__ == "__main__":
    result = asyncio.run(generate_demo_video())
    if result:
        print(f"\n🎉 Success! Watch: {result}")




