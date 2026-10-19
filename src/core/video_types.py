#!/usr/bin/env python3
"""
ViralShorts Factory - Multiple Video Types
Supports various viral content formats beyond just "Would You Rather"

Video Types:
1. WYR (Would You Rather) - Original quiz format
2. SCARY_FACTS - Creepy/disturbing facts that go viral
3. MONEY_FACTS - Financial facts that make people share
4. AI_QUOTES - Motivational/philosophical AI-generated quotes
5. KIDS - Educational content for children
"""

import os
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class VideoType(Enum):
    WYR = "would_you_rather"
    SCARY_FACTS = "scary_facts"
    MONEY_FACTS = "money_facts"
    AI_QUOTES = "ai_quotes"
    KIDS = "kids"


@dataclass
class VideoContent:
    """Unified content structure for all video types."""
    video_type: VideoType
    title: str
    hook: str  # First 1-2 seconds text
    main_text: str  # Primary content
    secondary_text: Optional[str] = None  # For WYR option B, or subtitle
    voiceover_script: str = ""
    broll_keywords: List[str] = None
    music_mood: str = "dramatic"
    percentage_a: int = 0  # Only for WYR
    percentage_b: int = 0  # Only for WYR
    call_to_action: str = "Follow for more!"  # CTA for engagement


# =============================================================================
# SCARY FACTS - Creepy content that makes people share
# =============================================================================

SCARY_FACTS_TEMPLATES = [
    {
        "hook": "This will keep you up tonight... 😱",
        "fact": "The average person walks past 36 murderers in their lifetime",
        "keywords": ["dark city", "crowd", "night"],
        "source": "FBI Statistics"
    },
    {
        "hook": "Scientists can't explain this... 👽",
        "fact": "There's a radio signal from space that repeats every 16 days and we don't know what's sending it",
        "keywords": ["space", "galaxy", "radio telescope"],
        "source": "NASA"
    },
    {
        "hook": "You've been lied to... 🕳️",
        "fact": "We've only explored 5% of the ocean. The other 95% could contain ANYTHING",
        "keywords": ["deep ocean", "underwater", "dark water"],
        "source": "NOAA"
    },
    {
        "hook": "This happened while you slept... 😨",
        "fact": "Your brain paralyzes your body during sleep so you don't act out your dreams",
        "keywords": ["sleeping person", "brain", "night"],
        "source": "Sleep Research"
    },
    {
        "hook": "They're watching you... 👁️",
        "fact": "Your phone can detect your emotions through how you type and swipe",
        "keywords": ["phone", "technology", "surveillance"],
        "source": "MIT Research"
    },
    {
        "hook": "This is happening RIGHT NOW... ⏰",
        "fact": "A neutron star could be heading toward Earth and we wouldn't know until it's too late",
        "keywords": ["neutron star", "space", "earth"],
        "source": "Astronomy"
    },
    {
        "hook": "You can't unsee this... 🔍",
        "fact": "There are more bacteria in your mouth right now than there are people on Earth",
        "keywords": ["microscope", "bacteria", "science"],
        "source": "Biology"
    },
    {
        "hook": "Nobody talks about this... 🤫",
        "fact": "Butterflies drink blood when they can't find fruit",
        "keywords": ["butterfly", "nature", "dark"],
        "source": "Entomology"
    },
]

# =============================================================================
# MONEY FACTS - Financial facts that make people share
# =============================================================================

MONEY_FACTS_TEMPLATES = [
    {
        "hook": "The rich don't want you to know this... 💰",
        "fact": "The top 1% own more wealth than the bottom 50% of the entire world combined",
        "keywords": ["money", "wealth", "luxury"],
        "source": "Oxfam"
    },
    {
        "hook": "This changed everything... 📈",
        "fact": "If you invested $1000 in Bitcoin in 2010, you'd have $400 million today",
        "keywords": ["bitcoin", "cryptocurrency", "money"],
        "source": "Financial Data"
    },
    {
        "hook": "Your bank is hiding this... 🏦",
        "fact": "Banks make money from your deposits while paying you almost nothing in interest",
        "keywords": ["bank", "money", "vault"],
        "source": "Banking"
    },
    {
        "hook": "Why are you still working?... 💼",
        "fact": "Passive income from dividends could replace your salary in 10-15 years of smart investing",
        "keywords": ["investing", "stocks", "growth"],
        "source": "Investment Research"
    },
    {
        "hook": "The shocking truth about money... 💵",
        "fact": "90% of the world's money only exists as digital numbers, not physical cash",
        "keywords": ["digital", "money", "technology"],
        "source": "Central Banks"
    },
    {
        "hook": "They don't teach this in school... 📚",
        "fact": "Compound interest can turn $500/month into over $1 million in 30 years",
        "keywords": ["growth", "compound", "wealth"],
        "source": "Mathematics"
    },
    {
        "hook": "This is why you're still broke... 😤",
        "fact": "The average millionaire has 7 streams of income, not just one job",
        "keywords": ["millionaire", "success", "money"],
        "source": "Wealth Studies"
    },
    {
        "hook": "Start doing THIS today... 🚀",
        "fact": "People who write down their financial goals are 42% more likely to achieve them",
        "keywords": ["goals", "success", "writing"],
        "source": "Psychology"
    },
]

# =============================================================================
# AI QUOTES - Motivational/philosophical content
# =============================================================================

AI_QUOTES_TEMPLATES = [
    {
        "hook": "This quote will change your life... ✨",
        "quote": "The only person you should try to be better than is the person you were yesterday",
        "author": "Ancient Wisdom",
        "keywords": ["sunrise", "motivation", "growth"]
    },
    {
        "hook": "Read this every morning... 🌅",
        "quote": "Your comfort zone is a beautiful place, but nothing ever grows there",
        "author": "Life Philosophy",
        "keywords": ["nature", "growth", "beautiful"]
    },
    {
        "hook": "Stop scrolling and read this... 📱",
        "quote": "In a world of algorithms, be human. In a world of noise, be silent. In a world of chaos, be calm",
        "author": "Modern Wisdom",
        "keywords": ["peace", "nature", "calm"]
    },
    {
        "hook": "This hits different... 💭",
        "quote": "The graveyard is the richest place on earth, full of books never written and dreams never chased",
        "author": "Reflection",
        "keywords": ["dreams", "sky", "motivation"]
    },
    {
        "hook": "Save this for later... 🔖",
        "quote": "The best time to plant a tree was 20 years ago. The second best time is now",
        "author": "Chinese Proverb",
        "keywords": ["tree", "nature", "growth"]
    },
    {
        "hook": "Remember this when you feel like quitting... 💪",
        "quote": "Rock bottom became the solid foundation on which I rebuilt my life",
        "author": "J.K. Rowling",
        "keywords": ["strength", "building", "rising"]
    },
    {
        "hook": "This truth hurts... 🎯",
        "quote": "You're not stuck. You're just committed to patterns that no longer serve you",
        "author": "Psychology",
        "keywords": ["patterns", "freedom", "change"]
    },
    {
        "hook": "Mindset is everything... 🧠",
        "quote": "The mind is everything. What you think, you become",
        "author": "Buddha",
        "keywords": ["mind", "meditation", "peace"]
    },
]


# =============================================================================
# Content Generator
# =============================================================================

class MultiTypeContentGenerator:
    """Generate content for any video type."""
    
    def __init__(self):
        self.video_types = list(VideoType)
        
        # Import kids content if available
        try:
            from kids_content import KidsContentGenerator
            self.kids_gen = KidsContentGenerator()
        except ImportError:
            self.kids_gen = None
    
    def generate_scary_fact(self) -> VideoContent:
        """Generate a scary fact video content."""
        template = random.choice(SCARY_FACTS_TEMPLATES)
        return VideoContent(
            video_type=VideoType.SCARY_FACTS,
            title=f"😱 {template['fact'][:50]}...",
            hook=template["hook"],
            main_text=template["fact"],
            secondary_text=f"Source: {template.get('source', 'Research')}",
            voiceover_script=f"{template['hook']} {template['fact']}",
            broll_keywords=template.get("keywords", ["dark", "mysterious"]),
            music_mood="suspense"
        )
    
    def generate_money_fact(self) -> VideoContent:
        """Generate a money fact video content."""
        template = random.choice(MONEY_FACTS_TEMPLATES)
        return VideoContent(
            video_type=VideoType.MONEY_FACTS,
            title=f"💰 {template['fact'][:50]}...",
            hook=template["hook"],
            main_text=template["fact"],
            secondary_text=f"Source: {template.get('source', 'Research')}",
            voiceover_script=f"{template['hook']} {template['fact']}",
            broll_keywords=template.get("keywords", ["money", "wealth"]),
            music_mood="motivational"
        )
    
    def generate_quote(self) -> VideoContent:
        """Generate an AI quote video content."""
        template = random.choice(AI_QUOTES_TEMPLATES)
        return VideoContent(
            video_type=VideoType.AI_QUOTES,
            title=f"✨ {template['quote'][:50]}...",
            hook=template["hook"],
            main_text=template["quote"],
            secondary_text=f"— {template.get('author', 'Unknown')}",
            voiceover_script=f"{template['hook']} {template['quote']}",
            broll_keywords=template.get("keywords", ["nature", "motivation"]),
            music_mood="inspirational"
        )
    
    def generate_kids_content(self) -> Optional[VideoContent]:
        """Generate kids educational content."""
        if not self.kids_gen:
            return None
        
        content = self.kids_gen.generate_random()
        
        if content["type"] == "quiz":
            return VideoContent(
                video_type=VideoType.KIDS,
                title=content.get("title", "Fun Quiz! 🎉"),
                hook="Can you answer this? 🤔",
                main_text=content.get("question", "What's the answer?"),
                secondary_text=str(content.get("options", [])),
                voiceover_script=f"Hey kids! {content.get('question', '')}",
                broll_keywords=["colorful", "cartoon", "fun"],
                music_mood="fun"
            )
        elif content["type"] == "animals":
            animals = content.get("animals", [])
            if animals:
                animal = random.choice(animals)
                return VideoContent(
                    video_type=VideoType.KIDS,
                    title=f"Animal Sounds! {animal.get('animal', '🐾')}",
                    hook="What sound does this animal make? 🎵",
                    main_text=animal.get("animal", "Animal"),
                    secondary_text=animal.get("sound", "???"),
                    voiceover_script=f"What sound does the {animal.get('animal', 'animal')} make? {animal.get('sound', '')}!",
                    broll_keywords=["animals", "nature", "cute"],
                    music_mood="fun"
                )
        
        # Default kids content
        return VideoContent(
            video_type=VideoType.KIDS,
            title="Learning is Fun! 📚",
            hook="Let's learn together! 🎉",
            main_text="ABC 123",
            voiceover_script="Hey kids! Let's learn something new today!",
            broll_keywords=["colorful", "education", "fun"],
            music_mood="fun"
        )
    
    def generate_wyr(self, option_a: str, option_b: str, 
                     percent_a: int = None) -> VideoContent:
        """Generate Would You Rather content."""
        if percent_a is None:
            percent_a = random.randint(30, 70)
        percent_b = 100 - percent_a
        
        return VideoContent(
            video_type=VideoType.WYR,
            title=f"🧠 {option_a[:30]} vs {option_b[:30]}",
            hook="This one's IMPOSSIBLE! 🤯",
            main_text=option_a,
            secondary_text=option_b,
            voiceover_script=f"Would you rather... {option_a}... or... {option_b}?",
            broll_keywords=self._extract_keywords(f"{option_a} {option_b}"),
            music_mood="dramatic",
            percentage_a=percent_a,
            percentage_b=percent_b
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract B-roll keywords from text."""
        # Simple keyword extraction - could use AI for better results
        keywords = []
        topic_words = {
            "money": ["money", "wealth", "rich", "million", "dollar"],
            "travel": ["travel", "fly", "world", "vacation"],
            "food": ["food", "eat", "restaurant", "cook"],
            "technology": ["phone", "computer", "tech", "future"],
            "nature": ["nature", "forest", "ocean", "mountain"],
        }
        
        text_lower = text.lower()
        for topic, words in topic_words.items():
            if any(w in text_lower for w in words):
                keywords.append(topic)
        
        return keywords if keywords else ["abstract", "colorful", "motion"]
    
    def generate_random(self, exclude_types: List[VideoType] = None) -> VideoContent:
        """Generate random content from any type."""
        available_types = [t for t in self.video_types 
                         if exclude_types is None or t not in exclude_types]
        
        video_type = random.choice(available_types)
        
        if video_type == VideoType.SCARY_FACTS:
            return self.generate_scary_fact()
        elif video_type == VideoType.MONEY_FACTS:
            return self.generate_money_fact()
        elif video_type == VideoType.AI_QUOTES:
            return self.generate_quote()
        elif video_type == VideoType.KIDS:
            return self.generate_kids_content() or self.generate_quote()
        else:
            # Default to random WYR
            options = [
                ("Have unlimited money", "Have unlimited time"),
                ("Know how you die", "Know when you die"),
                ("Be famous", "Be rich"),
            ]
            opt = random.choice(options)
            return self.generate_wyr(opt[0], opt[1])


# =============================================================================
# Video Weights for Production
# =============================================================================

# Recommended distribution for maximum virality
VIDEO_TYPE_WEIGHTS = {
    VideoType.WYR: 30,          # Original format, proven
    VideoType.SCARY_FACTS: 25,  # High engagement
    VideoType.MONEY_FACTS: 25,  # High shares
    VideoType.AI_QUOTES: 15,    # Good filler
    VideoType.KIDS: 5,          # Separate channel recommended
}


def get_weighted_random_type() -> VideoType:
    """Get a random video type based on weights."""
    types = list(VIDEO_TYPE_WEIGHTS.keys())
    weights = list(VIDEO_TYPE_WEIGHTS.values())
    return random.choices(types, weights=weights, k=1)[0]


if __name__ == "__main__":
    generator = MultiTypeContentGenerator()
    
    print("🎬 Multi-Type Content Generator Test\n")
    print("=" * 60)
    
    # Test each type
    for vtype in VideoType:
        print(f"\n📹 {vtype.value.upper()}")
        
        if vtype == VideoType.WYR:
            content = generator.generate_wyr("Be invisible", "Read minds")
        elif vtype == VideoType.SCARY_FACTS:
            content = generator.generate_scary_fact()
        elif vtype == VideoType.MONEY_FACTS:
            content = generator.generate_money_fact()
        elif vtype == VideoType.AI_QUOTES:
            content = generator.generate_quote()
        elif vtype == VideoType.KIDS:
            content = generator.generate_kids_content()
        
        if content:
            print(f"   Hook: {content.hook}")
            print(f"   Main: {content.main_text[:60]}...")
            print(f"   Music: {content.music_mood}")
            print(f"   Keywords: {content.broll_keywords}")






