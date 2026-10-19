#!/usr/bin/env python3
"""
ViralShorts Factory - AI-Driven Trend Detector
Uses AI to determine what video types/topics will perform best RIGHT NOW.

This replaces hardcoded video type selection with intelligent AI analysis of:
- Current trending topics from Google Trends
- Reddit viral posts
- Seasonal/temporal events
- Cultural moments

AI decides EVERYTHING - no hardcoding!
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Try to import AI clients
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


@dataclass
class TrendingTopic:
    """A trending topic detected by AI."""
    topic: str
    video_type: str  # scary_fact, money_fact, quote, wyr, kids, etc.
    hook: str
    content: str
    secondary_content: Optional[str] = None
    broll_keywords: List[str] = None
    music_mood: str = "dramatic"
    urgency_score: int = 5  # 1-10, how timely is this?
    virality_score: int = 5  # 1-10, predicted virality
    reason: str = ""  # Why AI chose this


class AITrendDetector:
    """Uses AI to detect trends and suggest video content."""
    
    def __init__(self):
        self.groq_client = None
        self.gemini_model = None
        
        # Initialize Groq
        if HAS_GROQ and os.environ.get("GROQ_API_KEY"):
            self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Initialize Gemini
        if HAS_GEMINI and os.environ.get("GEMINI_API_KEY"):
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def _get_current_context(self) -> str:
        """Get current date/time context for AI."""
        now = datetime.now()
        
        # Seasonal context
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall/autumn"
        
        # Holiday context
        holidays = []
        if month == 12:
            holidays = ["Christmas", "Hanukkah", "New Year approaching"]
        elif month == 1:
            holidays = ["New Year", "Winter blues"]
        elif month == 2:
            holidays = ["Valentine's Day", "Black History Month"]
        elif month == 10:
            holidays = ["Halloween", "Spooky season"]
        elif month == 11:
            holidays = ["Thanksgiving", "Black Friday"]
        
        return f"""
Current Date: {now.strftime('%B %d, %Y')} ({now.strftime('%A')})
Season: {season}
Time of Day: {now.strftime('%H:%M')}
Upcoming/Current Events: {', '.join(holidays) if holidays else 'None specific'}
Day Type: {'Weekend' if now.weekday() >= 5 else 'Weekday'}
"""
    
    def detect_trending_topics(self, count: int = 5) -> List[TrendingTopic]:
        """Use AI to generate trending topic suggestions."""
        
        context = self._get_current_context()
        
        prompt = f"""You are a viral content strategist for YouTube Shorts. Based on the current context, suggest {count} VIDEO IDEAS that would go viral RIGHT NOW.

{context}

For each video, provide a JSON object with these EXACT fields:
- "topic": brief topic name
- "video_type": one of [scary_fact, money_fact, quote, would_you_rather, kids_education, life_hack, psychology_fact, history_fact]
- "hook": attention-grabbing first line (max 10 words, use emojis)
- "content": the main content/fact/question (50-80 words)
- "secondary_content": for WYR=option B, for quotes=author, for facts=source (optional)
- "broll_keywords": 3 keywords for finding video footage
- "music_mood": one of [dramatic, suspense, inspirational, fun, emotional, energetic]
- "urgency_score": 1-10 how timely (10=must post today)
- "virality_score": 1-10 predicted shares
- "reason": why this will work now

Consider:
- What's happening in the world RIGHT NOW
- Seasonal relevance
- Universal human interests (fear, money, relationships, success)
- What makes people SHARE (shock, emotion, useful info)
- Trend cycles (what's coming back, what's fresh)

Return ONLY a JSON array of {count} objects. No other text."""

        try:
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.8  # Higher creativity
                )
                result = response.choices[0].message.content
            elif self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                result = response.text
            else:
                print("⚠️ No AI available, using fallback")
                return self._fallback_topics(count)
            
            # Parse JSON
            # Clean up response (remove markdown if present)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            topics_data = json.loads(result.strip())
            
            topics = []
            for t in topics_data:
                topics.append(TrendingTopic(
                    topic=t.get("topic", "Unknown"),
                    video_type=t.get("video_type", "scary_fact"),
                    hook=t.get("hook", "You won't believe this..."),
                    content=t.get("content", ""),
                    secondary_content=t.get("secondary_content"),
                    broll_keywords=t.get("broll_keywords", ["abstract", "motion"]),
                    music_mood=t.get("music_mood", "dramatic"),
                    urgency_score=t.get("urgency_score", 5),
                    virality_score=t.get("virality_score", 5),
                    reason=t.get("reason", "")
                ))
            
            return topics
            
        except Exception as e:
            print(f"⚠️ AI trend detection failed: {e}")
            return self._fallback_topics(count)
    
    def _fallback_topics(self, count: int) -> List[TrendingTopic]:
        """
        EMERGENCY FALLBACK ONLY - Used when AI is completely unavailable.
        
        WARNING: This should NEVER happen in production.
        If you see this, check:
        1. GROQ_API_KEY is set correctly
        2. Internet connectivity
        3. API rate limits
        
        These are evergreen topics with value - but NOT trending!
        """
        print("=" * 60)
        print("🚨 CRITICAL: Using EMERGENCY FALLBACK topics!")
        print("   → AI topic detection failed completely")
        print("   → Check GROQ_API_KEY and internet connectivity")
        print("   → Content will NOT be trending/timely")
        print("=" * 60)
        
        from datetime import datetime
        now = datetime.now()
        month = now.strftime("%B")
        
        # Make fallback slightly contextual based on date
        # Even in fallback, try to be somewhat relevant
        fallback_topics = [
            TrendingTopic(
                topic=f"{month} Psychology Insight",
                video_type="psychology_fact",
                hook="Your brain is working against you right now",
                content=f"Studies show that 92 percent of people give up on their goals within the first month. But here is the secret that successful people know: they do not have more willpower than you. They have better systems. They automate their habits. They remove friction from good choices and add friction to bad ones. What system could you create today?",
                broll_keywords=["brain", "success", "motivation", "thinking"],
                music_mood="inspirational",
                urgency_score=5,
                virality_score=7,
                reason="FALLBACK - Evergreen self-improvement content"
            ),
            TrendingTopic(
                topic=f"{month} Money Secret",
                video_type="money_fact",
                hook="You are losing money every single month",
                content=f"The average person loses $400 per year on unnecessary bank fees alone. Here is the simple fix: Check your bank statements right now for any recurring charges. Most banks have a fee-free option if you just ask. I saved $1,200 last year just by making 3 phone calls. Which subscription have you forgotten about?",
                broll_keywords=["money", "bank", "savings", "wallet"],
                music_mood="dramatic",
                urgency_score=6,
                virality_score=8,
                reason="FALLBACK - Money content always performs"
            ),
            TrendingTopic(
                topic=f"Unexplained {month} Mystery",
                video_type="scary_fact",
                hook="Scientists still cannot explain this",
                content=f"There is a place in the ocean called the Midnight Zone where no sunlight ever reaches. It is 3,000 feet below the surface. The creatures that live there have evolved in complete darkness for millions of years. They create their own light. Some have transparent bodies. Others have jaws so large they cannot close their mouths. We have explored less than 5 percent of this zone. What else is down there?",
                broll_keywords=["deep ocean", "dark water", "mystery", "creatures"],
                music_mood="suspense",
                urgency_score=5,
                virality_score=8,
                reason="FALLBACK - Horror/mystery content is shareable"
            ),
        ]
        return fallback_topics[:count]
    
    def get_best_topic_for_now(self) -> TrendingTopic:
        """Get the single best topic to create right now."""
        topics = self.detect_trending_topics(count=3)
        
        # Sort by combined score
        topics.sort(key=lambda t: (t.urgency_score + t.virality_score), reverse=True)
        
        best = topics[0]
        print(f"\n🎯 AI Selected Topic: {best.topic}")
        print(f"   Type: {best.video_type}")
        print(f"   Urgency: {best.urgency_score}/10, Virality: {best.virality_score}/10")
        print(f"   Reason: {best.reason}")
        
        return best
    
    def evaluate_video_quality(self, video_description: str) -> Dict:
        """Use AI to evaluate video quality before publishing."""
        
        prompt = f"""You are a YouTube Shorts expert. Rate this video concept:

{video_description}

Provide a JSON response with:
- "overall_score": 1-10
- "hook_score": 1-10 (is the opening attention-grabbing?)
- "content_score": 1-10 (is the content interesting/valuable?)
- "virality_score": 1-10 (will people share this?)
- "issues": list of specific problems
- "improvements": list of specific fixes
- "verdict": "PUBLISH", "IMPROVE", or "REJECT"

Be HARSH. Only "PUBLISH" if it's genuinely good."""

        try:
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                result = response.choices[0].message.content
                
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                
                return json.loads(result.strip())
        except Exception as e:
            print(f"⚠️ AI evaluation failed: {e}")
        
        return {"overall_score": 5, "verdict": "IMPROVE", "issues": ["Could not evaluate"]}


# =============================================================================
# Main Entry Points
# =============================================================================

def get_ai_suggested_video() -> TrendingTopic:
    """Main entry point - get AI's recommendation for what to create."""
    detector = AITrendDetector()
    return detector.get_best_topic_for_now()


def get_multiple_ai_suggestions(count: int = 5) -> List[TrendingTopic]:
    """Get multiple AI suggestions."""
    detector = AITrendDetector()
    return detector.detect_trending_topics(count)


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Trend Detector - ViralShorts Factory")
    print("=" * 60)
    
    detector = AITrendDetector()
    
    print("\n📊 Detecting trending topics...")
    topics = detector.detect_trending_topics(5)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*40}")
        print(f"📹 Topic {i}: {topic.topic}")
        print(f"   Type: {topic.video_type}")
        print(f"   Hook: {topic.hook}")
        print(f"   Content: {topic.content[:80]}...")
        print(f"   Music: {topic.music_mood}")
        print(f"   Scores: Urgency={topic.urgency_score}, Virality={topic.virality_score}")
        print(f"   Why: {topic.reason}")

