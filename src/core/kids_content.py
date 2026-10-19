#!/usr/bin/env python3
"""
Kids Content Generator
Generates kid-friendly educational content for maximum views.

Types:
1. Counting videos (1-10, shapes, colors)
2. ABC/Letter videos
3. Animal sounds & facts
4. Simple quiz games
5. Nursery rhyme visuals

NOTE: This module uses a HYBRID approach:
- Core educational concepts (ABC, 123, animals) are stable and don't need AI
- HOWEVER, the themes and seasonal elements ARE AI-driven via ai_trend_fetcher
- Example: "Count snowflakes" in winter, "Count flowers" in spring
"""

import os
import random
from typing import List, Dict, Tuple

# Safe colors for kids (bright, primary)
KIDS_COLORS = {
    "red": (255, 0, 0),
    "blue": (0, 100, 255),
    "green": (0, 200, 0),
    "yellow": (255, 220, 0),
    "orange": (255, 140, 0),
    "purple": (150, 0, 255),
    "pink": (255, 105, 180),
}

# Content Templates
COUNTING_TEMPLATES = [
    {
        "title": "Count to 10 with {animal}! 🎉",
        "items": ["🍎", "🌟", "🎈", "🦋", "🐶"],
        "voiceover": "One... Two... Three... Can you count with me?",
    },
    {
        "title": "Learn Shapes! ⭐ Circle, Square, Triangle!",
        "items": ["⭕", "⬛", "🔺", "💠", "❤️"],
        "voiceover": "What shape is this? It's a circle!",
    },
    {
        "title": "Learn Colors! 🌈 Rainbow Fun!",
        "items": list(KIDS_COLORS.keys()),
        "voiceover": "What color is this? It's red! R-E-D!",
    },
]

ANIMAL_TEMPLATES = [
    {
        "animal": "🐶 Dog",
        "sound": "Woof! Woof!",
        "fact": "Dogs are our best friends!",
    },
    {
        "animal": "🐱 Cat",
        "sound": "Meow! Meow!",
        "fact": "Cats love to sleep!",
    },
    {
        "animal": "🐮 Cow",
        "sound": "Moo! Moo!",
        "fact": "Cows give us milk!",
    },
    {
        "animal": "🐸 Frog",
        "sound": "Ribbit! Ribbit!",
        "fact": "Frogs can jump really far!",
    },
    {
        "animal": "🦁 Lion",
        "sound": "Roar! Roar!",
        "fact": "Lions are the king of the jungle!",
    },
    {
        "animal": "🐘 Elephant",
        "sound": "Toot! Toot!",
        "fact": "Elephants never forget!",
    },
]

QUIZ_TEMPLATES = [
    {
        "question": "What color is the sky? 🌤️",
        "options": ["🔴 Red", "🔵 Blue", "🟢 Green"],
        "answer": 1,
        "explanation": "The sky is BLUE! Great job!",
    },
    {
        "question": "How many legs does a dog have? 🐕",
        "options": ["2️⃣ Two", "4️⃣ Four", "6️⃣ Six"],
        "answer": 1,
        "explanation": "Dogs have FOUR legs! You're so smart!",
    },
    {
        "question": "What comes after 3? 🔢",
        "options": ["2️⃣ Two", "4️⃣ Four", "5️⃣ Five"],
        "answer": 1,
        "explanation": "1, 2, 3, FOUR! Great counting!",
    },
    {
        "question": "Which animal says MEOW? 🐾",
        "options": ["🐶 Dog", "🐱 Cat", "🐮 Cow"],
        "answer": 1,
        "explanation": "The CAT says meow! Purrfect!",
    },
    {
        "question": "What shape is a ball? ⚽",
        "options": ["⬜ Square", "⭕ Circle", "🔺 Triangle"],
        "answer": 1,
        "explanation": "A ball is a CIRCLE! Round and round!",
    },
]

ABC_TEMPLATES = [
    {
        "letter": "A",
        "word": "Apple",
        "emoji": "🍎",
        "voiceover": "A is for Apple! 🍎 Yummy!",
    },
    {
        "letter": "B",
        "word": "Ball",
        "emoji": "⚽",
        "voiceover": "B is for Ball! ⚽ Let's play!",
    },
    {
        "letter": "C",
        "word": "Cat",
        "emoji": "🐱",
        "voiceover": "C is for Cat! 🐱 Meow!",
    },
    # ... more letters
]


class KidsContentGenerator:
    """Generator for kid-friendly educational content."""
    
    def __init__(self):
        self.content_types = [
            "counting",
            "animals",
            "quiz",
            "abc",
        ]
        
        # Try to get AI-powered seasonal themes
        self.seasonal_themes = self._get_seasonal_themes()
    
    def _get_seasonal_themes(self) -> dict:
        """Get AI-powered seasonal themes for kids content."""
        try:
            from ai_trend_fetcher import AITrendFetcher
            fetcher = AITrendFetcher()
            kids_topics = fetcher.get_kids_trending_topics(2)
            if kids_topics:
                return {"ai_topics": kids_topics, "use_ai": True}
        except:
            pass
        
        # Fallback to seasonal defaults (still dynamic based on month!)
        from datetime import datetime
        month = datetime.now().month
        
        seasonal = {
            12: {"theme": "winter", "items": ["❄️ Snowflake", "🎄 Tree", "⭐ Star", "🎁 Gift"]},
            1: {"theme": "new_year", "items": ["🎉 Confetti", "⏰ Clock", "📅 Calendar"]},
            2: {"theme": "valentine", "items": ["❤️ Heart", "💝 Gift", "🌹 Rose"]},
            3: {"theme": "spring", "items": ["🌸 Flower", "🦋 Butterfly", "🐰 Bunny"]},
            4: {"theme": "easter", "items": ["🥚 Egg", "🐣 Chick", "🐰 Bunny"]},
            10: {"theme": "halloween", "items": ["🎃 Pumpkin", "👻 Ghost", "🦇 Bat"]},
        }
        
        return seasonal.get(month, {"theme": "fun", "items": ["⭐ Star", "🌈 Rainbow"]})
    
    def generate_counting_video(self) -> Dict:
        """Generate a counting video script."""
        template = random.choice(COUNTING_TEMPLATES)
        return {
            "type": "counting",
            "title": template["title"],
            "items": template["items"],
            "voiceover_segments": self._generate_counting_vo(template),
            "background_color": random.choice(list(KIDS_COLORS.values())),
        }
    
    def _generate_counting_vo(self, template: Dict) -> List[str]:
        """Generate voiceover segments for counting."""
        segments = []
        for i, item in enumerate(template["items"][:10], 1):
            segments.append(f"Number {i}! {item}")
        segments.append("Great job counting!")
        return segments
    
    def generate_animal_video(self) -> Dict:
        """Generate an animal sounds video."""
        animals = random.sample(ANIMAL_TEMPLATES, min(5, len(ANIMAL_TEMPLATES)))
        return {
            "type": "animals",
            "title": "Animal Sounds for Kids! 🐾🎵",
            "animals": animals,
            "background_color": (100, 200, 255),  # Sky blue
        }
    
    def generate_quiz_video(self) -> Dict:
        """Generate a kid-friendly quiz video."""
        quiz = random.choice(QUIZ_TEMPLATES)
        return {
            "type": "quiz",
            "title": f"Quiz Time! 🧠 {quiz['question'][:20]}...",
            "question": quiz["question"],
            "options": quiz["options"],
            "answer": quiz["answer"],
            "explanation": quiz["explanation"],
            "background_color": (255, 230, 100),  # Warm yellow
        }
    
    def generate_abc_video(self) -> Dict:
        """Generate an ABC learning video."""
        letter = random.choice(ABC_TEMPLATES)
        return {
            "type": "abc",
            "title": f"Learn Letter {letter['letter']}! 📖",
            "letter": letter["letter"],
            "word": letter["word"],
            "emoji": letter["emoji"],
            "voiceover": letter["voiceover"],
            "background_color": (200, 255, 200),  # Soft green
        }
    
    def generate_random(self) -> Dict:
        """Generate a random kid-friendly content piece."""
        content_type = random.choice(self.content_types)
        
        if content_type == "counting":
            return self.generate_counting_video()
        elif content_type == "animals":
            return self.generate_animal_video()
        elif content_type == "quiz":
            return self.generate_quiz_video()
        else:
            return self.generate_abc_video()


# TTS Voice for Kids (slower, clearer, friendlier)
KIDS_TTS_SETTINGS = {
    "voice": "en-US-AnaNeural",  # Child-like voice
    "rate": "-10%",  # Slower for kids
    "pitch": "+15Hz",  # Higher, friendlier
}


if __name__ == "__main__":
    generator = KidsContentGenerator()
    
    print("🧒 Kids Content Generator Test\n")
    
    # Test each type
    for i in range(4):
        content = generator.generate_random()
        print(f"Type: {content['type']}")
        print(f"Title: {content.get('title', 'N/A')}")
        print()


