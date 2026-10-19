#!/usr/bin/env python3
"""
ViralShorts Factory - AI-Powered Trend Fetcher
===============================================

NO HARDCODED TOPICS. EVER.

This module uses AI to dynamically determine what's trending RIGHT NOW.
The AI acts as your "trend researcher" that knows what's viral today.

Sources of trend intelligence:
1. AI's knowledge of current events (trained on recent data)
2. Seasonal/temporal context (holidays, time of year, day of week)
3. Platform-specific trending patterns (what works on Shorts)
4. Psychological triggers that are timeless but applied to current events
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class AITrendFetcher:
    """
    Fetches trending topics using AI - NO HARDCODED CONTENT.
    
    The AI is instructed to think about what's CURRENTLY trending
    and generate topics that would go viral TODAY.
    """
    
    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.client = None
        
        if self.groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_key)
            except ImportError:
                pass
    
    def get_current_context(self) -> Dict:
        """Get rich context about the current moment in time."""
        now = datetime.now()
        
        # Determine season with specifics
        month = now.month
        day = now.day
        
        # Holiday/event detection
        special_events = []
        
        # December events
        if month == 12:
            if day <= 25:
                special_events.append("Christmas approaching")
            if day >= 26:
                special_events.append("Post-Christmas, New Year approaching")
            if day == 31:
                special_events.append("New Year's Eve")
        
        # January events
        if month == 1:
            if day <= 7:
                special_events.append("New Year, resolution season")
            special_events.append("Back to work/school mood")
        
        # February
        if month == 2:
            if day <= 14:
                special_events.append("Valentine's Day approaching")
        
        # More seasonal context
        season_context = {
            1: "winter - New Year resolutions, cold weather, staying inside, self-improvement season",
            2: "winter - Valentine's Day, love/relationships, still cold, indoor activities",
            3: "spring - fresh starts, weather warming, allergies, spring cleaning, St. Patrick's Day",
            4: "spring - Easter, outdoor activities returning, April showers, tax season",
            5: "spring - Mother's Day, graduation season, summer planning, Memorial Day",
            6: "summer - vacation planning, Father's Day, warm weather, outdoor activities",
            7: "summer - peak vacation, Independence Day aftermath, beach/pool weather",
            8: "summer - back to school prep, last summer adventures, end of vacation",
            9: "fall - back to school, Labor Day, routines returning, fall weather",
            10: "fall - Halloween approaching, spooky season, fall aesthetics, pumpkin everything",
            11: "fall - Thanksgiving, gratitude, Black Friday, holiday prep starts",
            12: "winter - holiday season, Christmas, Hanukkah, end of year reflection"
        }
        
        return {
            "date": now.strftime("%B %d, %Y"),
            "day_of_week": now.strftime("%A"),
            "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening",
            "month": now.strftime("%B"),
            "year": now.year,
            "season_context": season_context.get(month, "general"),
            "special_events": special_events,
            "is_weekend": now.weekday() >= 5,
        }
    
    def fetch_trending_topics(self, count: int = 5) -> List[Dict]:
        """
        Use AI to determine what topics are trending RIGHT NOW.
        
        The AI is instructed to be a trend researcher who understands
        what content would go viral on YouTube Shorts TODAY.
        """
        if not self.client:
            print("⚠️ No AI client available for trend fetching")
            return []
        
        context = self.get_current_context()
        
        prompt = f"""You are a viral content researcher who specializes in predicting what will trend on YouTube Shorts and TikTok.

TODAY'S CONTEXT:
- Date: {context['date']} ({context['day_of_week']})
- Time: {context['time_of_day']}
- Season: {context['season_context']}
- Special events: {', '.join(context['special_events']) if context['special_events'] else 'None specifically'}
- Weekend: {'Yes' if context['is_weekend'] else 'No'}

YOUR TASK: Generate {count} video topic ideas that would go VIRAL if posted TODAY.

CRITICAL REQUIREMENTS:
1. Topics must be TIMELY - relevant to what people are thinking about RIGHT NOW
2. Topics must DELIVER VALUE - no empty promises, actual useful content
3. Topics must be SPECIFIC - include numbers, facts, actionable advice
4. Topics must be SHAREABLE - make viewers want to tell friends
5. NO generic evergreen content - think about what's on people's minds TODAY

TOPIC CATEGORIES TO CONSIDER (pick the most relevant for TODAY):
- Current events implications (how news affects daily life)
- Seasonal behaviors (what people do this time of year)
- Psychological insights (why people feel/act certain ways)
- Money/productivity (relevant to current economic climate)
- Health/wellness (seasonal health, mental health, etc.)
- Technology/AI (current developments people care about)
- Relationships (relevant to current social context)
- Mind-blowing facts (that connect to current interests)

For EACH topic, provide complete details:

{{
    "topic": "2-4 word topic name",
    "video_type": "psychology_fact|money_fact|life_hack|scary_fact|mind_blow|health_tip|tech_insight",
    "why_trending_now": "Why this is relevant specifically TODAY/this week/this season",
    "hook": "8-12 word attention grabber with SPECIFIC claim - NO EMOJIS",
    "content": "Complete script that DELIVERS value. Must include: specific numbers, the mechanism/evidence, actionable takeaway. 60-100 words. NO EMOJIS.",
    "the_value_delivered": "The ONE thing viewer learns or can do",
    "call_to_action": "Engaging question for comments",
    "broll_keywords": ["specific visual 1", "specific visual 2", "specific visual 3", "specific visual 4"],
    "music_mood": "suspense|dramatic|inspirational|energetic|emotional|uplifting",
    "virality_score": 1-10,
    "timeliness_score": 1-10
}}

Return a JSON array of {count} objects. Prioritize timeliness - what would resonate with viewers scrolling TODAY, not generic content.
No markdown, no emojis, no explanations outside JSON."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.9  # Higher creativity for trend discovery
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            topics = json.loads(result.strip())
            
            if isinstance(topics, list):
                # Strip any emojis that might have slipped through
                import re
                emoji_pattern = re.compile("["
                    u"\U0001F600-\U0001F64F"
                    u"\U0001F300-\U0001F5FF"
                    u"\U0001F680-\U0001F6FF"
                    u"\U0001F1E0-\U0001F1FF"
                    u"\U00002702-\U000027B0"
                    u"\U000024C2-\U0001F251"
                    u"\U0001f926-\U0001f937"
                    u"\U00010000-\U0010ffff"
                    u"\u2640-\u2642"
                    u"\u2600-\u2B55"
                    u"\u200d"
                    u"\u23cf"
                    u"\u23e9"
                    u"\u231a"
                    u"\ufe0f"
                    u"\u3030"
                    "]+", flags=re.UNICODE)
                
                for topic in topics:
                    for key in ["hook", "content", "topic", "call_to_action", "why_trending_now"]:
                        if key in topic and topic[key]:
                            topic[key] = emoji_pattern.sub('', str(topic[key])).strip()
                
                print(f"✅ Fetched {len(topics)} trending topics for {context['date']}")
                for t in topics:
                    print(f"   📈 {t.get('topic', 'N/A')} (timeliness: {t.get('timeliness_score', '?')}/10)")
                
                return topics
            
            return []
            
        except Exception as e:
            print(f"⚠️ Trend fetching failed: {e}")
            return []
    
    def get_kids_trending_topics(self, count: int = 3) -> List[Dict]:
        """
        Get trending topics specifically for kids content.
        Also uses AI to be relevant and timely.
        """
        if not self.client:
            return []
        
        context = self.get_current_context()
        
        prompt = f"""You are a children's educational content creator.

TODAY'S CONTEXT:
- Date: {context['date']} 
- Season: {context['season_context']}
- Special events: {', '.join(context['special_events']) if context['special_events'] else 'None'}

Generate {count} educational video ideas for KIDS (ages 3-8) that are:
1. TIMELY - connected to the current season/events
2. EDUCATIONAL - teach something valuable
3. FUN - engaging and entertaining
4. SAFE - 100% kid-appropriate

Examples of timely kids content:
- December: "Count to 10 with Snowflakes!"
- October: "Spooky Shapes! Find the Triangles!"
- Summer: "Beach Animals ABC!"

For EACH topic:
{{
    "topic": "Fun title for kids",
    "type": "counting|abc|animals|shapes|colors|quiz",
    "learning_goal": "What kids will learn",
    "why_timely": "Why this is relevant now",
    "voiceover_script": "The complete voiceover in kid-friendly language",
    "visual_elements": ["visual 1", "visual 2", "visual 3"],
    "background_style": "bright colors theme"
}}

Return JSON array. Must be 100% kid-safe!"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.8
            )
            
            result = response.choices[0].message.content
            
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result.strip())
            
        except Exception as e:
            print(f"⚠️ Kids trend fetching failed: {e}")
            return []


# Export
__all__ = ['AITrendFetcher']


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 AI Trend Fetcher - Testing")
    print("=" * 60)
    
    fetcher = AITrendFetcher()
    
    print("\n📊 Current Context:")
    context = fetcher.get_current_context()
    for key, value in context.items():
        print(f"   {key}: {value}")
    
    print("\n🔥 Fetching Trending Topics...")
    topics = fetcher.fetch_trending_topics(3)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*50}")
        print(f"📹 Topic {i}: {topic.get('topic', 'N/A')}")
        print(f"   Why trending now: {topic.get('why_trending_now', 'N/A')}")
        print(f"   Hook: {topic.get('hook', 'N/A')}")
        print(f"   Value: {topic.get('the_value_delivered', 'N/A')}")
        print(f"   Timeliness: {topic.get('timeliness_score', '?')}/10")








