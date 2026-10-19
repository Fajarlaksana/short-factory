"""
Boost Optimizer - Legitimate methods to maximize content reach
All methods are platform-compliant and ethical!
"""
import random
from datetime import datetime
from typing import List, Dict, Any


class TitleOptimizer:
    """Generate viral, SEO-optimized titles using AI patterns."""
    
    # Proven viral patterns for Would You Rather
    VIRAL_PATTERNS = [
        "Would You Rather: {option_a} OR {option_b}? 🤔",
        "{option_a} vs {option_b} - Which Would YOU Choose? 🔥",
        "IMPOSSIBLE Choice: {option_a} or {option_b}? 😱",
        "99% Get This WRONG! {option_a} vs {option_b} 🧠",
        "This Will BREAK Your Brain: {option_a} OR {option_b}? 💥",
        "Would You Rather {option_a}... or {option_b}? (HARD) 😰",
        "EVERYONE Fails This! {option_a} vs {option_b} 🎯",
    ]
    
    @staticmethod
    def generate_title(option_a: str, option_b: str) -> str:
        """Generate an optimized viral title."""
        # Shorten options if too long
        if len(option_a) > 40:
            option_a = option_a[:37] + "..."
        if len(option_b) > 40:
            option_b = option_b[:37] + "..."
        
        pattern = random.choice(TitleOptimizer.VIRAL_PATTERNS)
        return pattern.format(option_a=option_a, option_b=option_b)


class HashtagOptimizer:
    """Generate optimized hashtags for maximum discoverability."""
    
    # Core hashtags (always include)
    CORE_HASHTAGS = [
        "#shorts",
        "#wouldyourather", 
        "#quiz",
        "#viral",
    ]
    
    # Rotating hashtags (vary for freshness)
    ROTATING_HASHTAGS = [
        ["#challenge", "#fun", "#trending", "#fyp"],
        ["#game", "#choice", "#decide", "#opinion"],
        ["#thisorthat", "#pick", "#question", "#vote"],
        ["#brain", "#think", "#hard", "#impossible"],
        ["#entertainment", "#comedy", "#funny", "#crazy"],
    ]
    
    # Day-specific hashtags
    DAY_HASHTAGS = {
        0: ["#MondayMotivation", "#MondayMood"],
        1: ["#TuesdayThoughts", "#TuesdayVibes"],
        2: ["#WednesdayWisdom", "#HumpDay"],
        3: ["#ThursdayThoughts", "#ThrowbackThursday"],
        4: ["#FridayFeeling", "#FridayVibes", "#TGIF"],
        5: ["#SaturdayVibes", "#WeekendMood"],
        6: ["#SundayFunday", "#SundayVibes"],
    }
    
    @staticmethod
    def generate_hashtags(include_day_tag: bool = True) -> List[str]:
        """
        Generate optimized hashtag set.
        
        v17.9.11: Uses LEARNED hashtags first (from analytics performance),
        then falls back to default hashtags if no learned data.
        """
        tags = ["#shorts"]  # Always include
        
        # v17.9.11: TRY LEARNED HASHTAGS FIRST
        try:
            from src.analytics.self_learning_engine import get_learning_engine
            engine = get_learning_engine()
            learned_tags = engine.get_best_hashtags()
            if learned_tags and len(learned_tags) >= 3:
                # Use learned hashtags (they performed well!)
                tags.extend([t for t in learned_tags if t not in tags][:4])
        except:
            pass
        
        # Fill in with defaults if not enough learned tags
        if len(tags) < 4:
            tags.extend([t for t in HashtagOptimizer.CORE_HASHTAGS if t not in tags])
        
        # Add rotating hashtags for variety
        if len(tags) < 6:
            rotating = random.choice(HashtagOptimizer.ROTATING_HASHTAGS)
            tags.extend([t for t in rotating[:2] if t not in tags])
        
        # Add day-specific hashtag
        if include_day_tag and len(tags) < 8:
            day = datetime.now().weekday()
            day_tags = HashtagOptimizer.DAY_HASHTAGS.get(day, [])
            if day_tags:
                tags.append(random.choice(day_tags))
        
        return tags[:8]  # Keep under 8 hashtags


class DescriptionOptimizer:
    """Generate engaging, algorithm-friendly descriptions."""
    
    TEMPLATES = [
        """🤔 Would you rather {option_a} OR {option_b}?

Vote in the comments! 👇
A = {option_a}
B = {option_b}

{hashtags}

📱 Follow for daily quizzes!
🔔 Like & Subscribe for more!""",

        """This is IMPOSSIBLE to answer! 😱

{option_a} vs {option_b}

💬 Comment your choice below!
❤️ Like if you chose A
💙 Share if you chose B

{hashtags}""",

        """HARDEST choice ever! 🧠

Would YOU rather:
👉 {option_a}
OR
👉 {option_b}

Drop your answer in the comments! 💬

{hashtags}

New quizzes daily! 🎯""",
    ]
    
    @staticmethod
    def generate_description(option_a: str, option_b: str) -> str:
        """Generate an optimized description."""
        template = random.choice(DescriptionOptimizer.TEMPLATES)
        hashtags = " ".join(HashtagOptimizer.generate_hashtags())
        
        return template.format(
            option_a=option_a,
            option_b=option_b,
            hashtags=hashtags
        )


class PostingScheduler:
    """Optimize posting times for maximum engagement."""
    
    # Peak engagement hours (UTC) by day
    PEAK_HOURS = {
        # Weekdays: Morning, lunch, evening
        0: [7, 12, 18, 21],  # Monday
        1: [7, 12, 18, 21],  # Tuesday
        2: [7, 12, 18, 21],  # Wednesday
        3: [7, 12, 18, 21],  # Thursday
        4: [7, 12, 17, 22],  # Friday - earlier evening, later night
        # Weekends: Later mornings, more evening
        5: [9, 13, 17, 21],  # Saturday
        6: [10, 14, 18, 20], # Sunday
    }
    
    @staticmethod
    def get_optimal_delay() -> int:
        """Get delay in seconds to reach next optimal posting window."""
        now = datetime.utcnow()
        day = now.weekday()
        hour = now.hour
        
        peak_hours = PostingScheduler.PEAK_HOURS[day]
        
        # Find next peak hour
        for peak in peak_hours:
            if peak > hour:
                delay_hours = peak - hour
                # Add randomness (0-30 min)
                return delay_hours * 3600 + random.randint(0, 1800)
        
        # No more peaks today, return small random delay
        return random.randint(0, 1800)
    
    @staticmethod
    def is_good_posting_time() -> bool:
        """Check if now is a good time to post."""
        now = datetime.utcnow()
        day = now.weekday()
        hour = now.hour
        
        peak_hours = PostingScheduler.PEAK_HOURS[day]
        # Consider within 1 hour of peak as good
        for peak in peak_hours:
            if abs(peak - hour) <= 1:
                return True
        return False


class ContentVariety:
    """Ensure content variety to avoid repetition detection."""
    
    @staticmethod
    def vary_cta() -> str:
        """Generate varied call-to-action."""
        ctas = [
            "Comment your choice! 👇",
            "What would YOU pick? 💬",
            "Drop your answer below! 👇",
            "Vote in comments! 🗳️",
            "Tell us your choice! 💭",
            "Which one? Let us know! 👇",
            "A or B? Comment! 🤔",
        ]
        return random.choice(ctas)
    
    @staticmethod
    def vary_intro() -> str:
        """Generate varied video intro text."""
        intros = [
            "Would you rather...",
            "Here's a tough one!",
            "Choose wisely...",
            "This is impossible!",
            "Can you decide?",
            "Pick one!",
            "The hardest choice...",
        ]
        return random.choice(intros)


# Singleton optimizer instance
_optimizer = None

def get_optimizer():
    """Get or create optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = {
            "title": TitleOptimizer(),
            "hashtag": HashtagOptimizer(),
            "description": DescriptionOptimizer(),
            "scheduler": PostingScheduler(),
            "variety": ContentVariety(),
        }
    return _optimizer


def optimize_content(option_a: str, option_b: str) -> Dict[str, Any]:
    """
    Generate fully optimized content metadata.
    
    Returns dict with:
    - title: Viral title
    - description: Engagement-optimized description
    - tags: SEO hashtags
    - is_peak_time: Whether now is optimal for posting
    """
    return {
        "title": TitleOptimizer.generate_title(option_a, option_b),
        "description": DescriptionOptimizer.generate_description(option_a, option_b),
        "tags": HashtagOptimizer.generate_hashtags(),
        "is_peak_time": PostingScheduler.is_good_posting_time(),
        "cta": ContentVariety.vary_cta(),
        "intro": ContentVariety.vary_intro(),
    }


if __name__ == "__main__":
    # Test
    result = optimize_content(
        "Have unlimited money but no friends",
        "Have amazing friends but always be broke"
    )
    
    print("=== Optimized Content ===")
    print(f"\nTitle: {result['title']}")
    print(f"\nDescription:\n{result['description']}")
    print(f"\nTags: {result['tags']}")
    print(f"\nPeak time: {result['is_peak_time']}")
    print(f"CTA: {result['cta']}")
    print(f"Intro: {result['intro']}")











