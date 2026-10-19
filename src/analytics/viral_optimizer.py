#!/usr/bin/env python3
"""
ViralShorts Factory - VIRAL OPTIMIZATION ENGINE
Maximizes views, engagement, and growth through proven techniques.

Research-backed strategies:
1. Hashtag optimization (platform-specific)
2. Title SEO for discoverability
3. Hook psychology for scroll-stopping
4. Sharability triggers
5. Save-worthy content markers
6. Subscribe-bait techniques
"""

import os
import re
import random
from datetime import datetime
from typing import Dict, List, Optional

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


# =============================================================================
# HASHTAG STRATEGIES (Platform-Specific)
# =============================================================================

class HashtagOptimizer:
    """Generate optimal hashtags for each platform."""
    
    # YouTube Shorts - 3-5 hashtags work best (last one appears as category)
    YOUTUBE_TRENDING = [
        "#shorts", "#viral", "#trending", "#fyp", "#foryou",
        "#facts", "#didyouknow", "#mindblown", "#psychology",
        "#money", "#motivation", "#lifehack", "#scary", "#creepy"
    ]
    
    # Topic-specific hashtag maps
    TOPIC_HASHTAGS = {
        "psychology": ["#psychology", "#mindset", "#brain", "#humanmind", "#behavior"],
        "money": ["#money", "#finance", "#investing", "#wealth", "#millionaire"],
        "scary": ["#scary", "#creepy", "#horror", "#disturbing", "#darkfacts"],
        "life_hack": ["#lifehack", "#productivity", "#success", "#tips", "#hack"],
        "health": ["#health", "#wellness", "#fitness", "#healthtips", "#body"],
        "mind_blow": ["#mindblown", "#facts", "#science", "#amazing", "#wow"],
    }
    
    @classmethod
    def get_youtube_hashtags(cls, video_type: str, topic: str = "") -> List[str]:
        """Get optimized YouTube hashtags (3-5 recommended)."""
        hashtags = ["#shorts"]  # Always include
        
        # Add topic-specific
        for key, tags in cls.TOPIC_HASHTAGS.items():
            if key in video_type.lower() or key in topic.lower():
                hashtags.extend(tags[:2])
                break
        
        # Add trending
        hashtags.extend(random.sample(["#viral", "#trending", "#fyp"], 2))
        
        # Limit to 5 unique
        return list(dict.fromkeys(hashtags))[:5]
    
    @classmethod
    def get_dailymotion_hashtags(cls, video_type: str, topic: str = "") -> List[str]:
        """Get optimized Dailymotion tags (up to 10)."""
        tags = ["viral", "shorts", "facts", "trending"]
        
        # Add topic-specific
        for key, topic_tags in cls.TOPIC_HASHTAGS.items():
            if key in video_type.lower() or key in topic.lower():
                tags.extend([t.replace("#", "") for t in topic_tags[:3]])
                break
        
        return list(dict.fromkeys(tags))[:10]


# =============================================================================
# TITLE OPTIMIZATION (SEO + Click-Bait Balance)
# =============================================================================

class TitleOptimizer:
    """Generate click-worthy titles that also rank in search."""
    
    # Power words that increase CTR
    POWER_WORDS = [
        "SECRET", "SHOCKING", "INSANE", "BRUTAL", "HIDDEN",
        "NEVER", "ALWAYS", "WARNING", "PROOF", "REVEALED"
    ]
    
    # SEO keywords that get searched
    SEO_KEYWORDS = {
        "psychology": ["psychology fact", "mind trick", "brain hack", "human behavior"],
        "money": ["money tip", "wealth secret", "rich people", "financial hack"],
        "scary": ["scary fact", "disturbing truth", "creepy", "dark secret"],
        "life_hack": ["life hack", "productivity tip", "success secret", "daily habit"],
        "health": ["health tip", "body hack", "wellness secret", "healthy habit"],
    }
    
    @classmethod
    def generate_title(cls, hook: str, video_type: str) -> str:
        """Generate an optimized title from the hook."""
        # Clean the hook
        title = hook.strip()
        
        # Remove emojis
        title = re.sub(r'[^\w\s.,!?\'"-]', '', title)
        
        # Ensure it ends with impact
        if not title.endswith(('!', '?', '...')):
            if '?' not in title:
                title = title.rstrip('.') + '!'
        
        # Capitalize key words
        for word in cls.POWER_WORDS:
            if word.lower() in title.lower():
                title = re.sub(rf'\b{word}\b', word, title, flags=re.IGNORECASE)
        
        # Keep under 100 chars for YouTube (shows full title)
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title
    
    @classmethod
    def generate_description(cls, content: str, hashtags: List[str], cta: str = "") -> str:
        """Generate an SEO-optimized description."""
        # First 100 chars most important for SEO
        desc = content[:200].strip()
        
        # Add CTA
        if cta:
            desc += f"\n\n{cta}"
        
        # Add engagement bait
        desc += "\n\n💬 Comment your thoughts below!"
        desc += "\n👆 Follow for more mind-blowing content!"
        
        # Add hashtags
        desc += "\n\n" + " ".join(hashtags)
        
        return desc


# =============================================================================
# VIRAL PSYCHOLOGY TRIGGERS
# =============================================================================

class ViralPsychology:
    """Psychological triggers that make content go viral."""
    
    # Emotions that drive sharing (Jonah Berger's research)
    VIRAL_EMOTIONS = {
        "awe": "Makes them feel small in a big universe - they MUST share",
        "anger": "Injustice or frustration - they share to validate feelings",
        "anxiety": "Worry or fear - they share to warn others",
        "surprise": "Unexpected twist - they share to surprise friends too",
        "joy": "Positive feeling - they share to spread good vibes"
    }
    
    # Social currency triggers
    SOCIAL_CURRENCY = [
        "insider_knowledge",  # Makes sharer look smart
        "remarkable_stat",    # Easy to remember and repeat
        "practical_value",    # Useful to others
        "story_worthy",       # Worth telling at dinner
        "identity_signal"     # Shows what kind of person they are
    ]
    
    @classmethod
    def enhance_for_sharing(cls, content: str) -> str:
        """Add elements that make content more shareable."""
        # Ensure there's a remarkable stat
        if not re.search(r'\d+%|\d+ (times|percent|million|billion)', content):
            # AI should add this, but flag if missing
            pass
        
        return content
    
    @classmethod
    def enhance_for_saving(cls, content: str) -> str:
        """Add elements that make viewers save the video."""
        # Save triggers: actionable steps, reference information, things to remember
        save_triggers = [
            "Remember this:",
            "Save this for later:",
            "Here's what to do:",
            "Step-by-step:",
            "The formula is:",
        ]
        # Content should naturally include these
        return content


# =============================================================================
# SUBSCRIBE TRIGGERS
# =============================================================================

class SubscribeTriggers:
    """Techniques to convert viewers to subscribers."""
    
    # End screen CTAs (spoken in video)
    END_CTAS = [
        "Follow for more secrets most people never learn",
        "If this blew your mind, you'll love what's next",
        "Part 2 drops tomorrow - don't miss it",
        "Follow to learn something new every day",
        "Comment which topic you want next",
    ]
    
    # Description CTAs
    DESC_CTAS = [
        "🔔 Follow for daily mind-blowing facts!",
        "💡 New life-changing content every day!",
        "🧠 Subscribe for your daily dose of knowledge!",
    ]
    
    @classmethod
    def get_video_cta(cls, video_type: str) -> str:
        """Get a CTA optimized for the video type."""
        type_ctas = {
            "psychology": "Follow to understand the human mind better",
            "money": "Follow for wealth-building secrets",
            "scary": "Follow if you dare to learn more dark truths",
            "life_hack": "Follow for daily life-changing tips",
            "health": "Follow for more health secrets",
        }
        
        for key, cta in type_ctas.items():
            if key in video_type.lower():
                return cta
        
        return random.choice(cls.END_CTAS)


# =============================================================================
# AI-POWERED TITLE GENERATOR
# =============================================================================

def generate_viral_title_ai(hook: str, content: str, video_type: str) -> Dict:
    """Use AI to generate the most viral title and description."""
    if not HAS_GROQ:
        return {
            "title": TitleOptimizer.generate_title(hook, video_type),
            "description": content[:200],
            "hashtags": HashtagOptimizer.get_youtube_hashtags(video_type)
        }
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "title": TitleOptimizer.generate_title(hook, video_type),
            "description": content[:200],
            "hashtags": HashtagOptimizer.get_youtube_hashtags(video_type)
        }
    
    try:
        client = Groq(api_key=api_key)
        
        # v16.8: DYNAMIC MODEL - No hardcoded model names
        try:
            from quota_optimizer import get_quota_optimizer
            optimizer = get_quota_optimizer()
            groq_models = optimizer.get_groq_models(api_key)
            model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
        except:
            model_to_use = "llama-3.3-70b-versatile"
        
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[{
                "role": "user",
                "content": f"""You are a YouTube SEO expert with 10M+ subscribers.

Create the PERFECT title and description for this video:

HOOK: {hook}
CONTENT: {content}
TYPE: {video_type}

Requirements:
1. TITLE (max 80 chars): 
   - Must create CURIOSITY GAP (makes them need to watch)
   - Include a NUMBER if possible
   - Use POWER WORDS (shocking, secret, never, always)
   - Searchable keywords for SEO
   
2. DESCRIPTION (max 300 chars):
   - First 100 chars = most important (shows in search)
   - Include relevant keywords
   - Add engagement prompt
   
3. HASHTAGS: Exactly 5 YouTube hashtags

Return JSON only:
{{
    "title": "Your optimized title here",
    "description": "Your SEO description here",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
}}"""
            }],
            max_tokens=300,
            temperature=0.7
        )
        
        import json
        result = json.loads(response.choices[0].message.content.strip())
        return result
        
    except Exception as e:
        print(f"[!] AI title generation failed: {e}")
        return {
            "title": TitleOptimizer.generate_title(hook, video_type),
            "description": content[:200],
            "hashtags": HashtagOptimizer.get_youtube_hashtags(video_type)
        }


# =============================================================================
# MAIN OPTIMIZER CLASS
# =============================================================================

class ViralOptimizer:
    """Main class that combines all optimization techniques."""
    
    def __init__(self):
        self.hashtag_optimizer = HashtagOptimizer()
        self.title_optimizer = TitleOptimizer()
    
    def optimize_video(self, hook: str, content: str, video_type: str, 
                       platform: str = "youtube") -> Dict:
        """Optimize a video for maximum viral potential."""
        
        # Generate AI-optimized metadata
        metadata = generate_viral_title_ai(hook, content, video_type)
        
        # Platform-specific adjustments
        if platform == "dailymotion":
            metadata["tags"] = HashtagOptimizer.get_dailymotion_hashtags(video_type)
        
        # Add subscribe CTA
        metadata["cta"] = SubscribeTriggers.get_video_cta(video_type)
        
        # Add full description with all elements
        full_desc = TitleOptimizer.generate_description(
            content,
            metadata.get("hashtags", []),
            metadata.get("cta", "")
        )
        metadata["full_description"] = full_desc
        
        return metadata


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    optimizer = ViralOptimizer()
    
    result = optimizer.optimize_video(
        hook="Your brain makes 35,000 decisions daily",
        content="Each decision depletes mental energy. By 3pm, your willpower is nearly gone. That's why you make poor food choices at night. Solution: Make important decisions before noon.",
        video_type="psychology_fact"
    )
    
    print("Title:", result.get("title"))
    print("Hashtags:", result.get("hashtags"))
    print("CTA:", result.get("cta"))




