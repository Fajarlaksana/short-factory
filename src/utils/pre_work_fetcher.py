#!/usr/bin/env python3
"""
ViralShorts Factory - Pre-Work Data Fetcher
=============================================

This script runs ONCE to fetch all data needed for video generation:
1. Trending topics (from AI)
2. Pre-generated video concepts (categories, topics, moods)
3. Voice/music suggestions

The data is saved to a JSON file that subsequent workflows can use,
SAVING 60-70% of API quota!

Architecture:
[Pre-Work Workflow] → concepts.json → [Video Generation Workflows]
     (1x/day)                              (4x/day, uses cached data)
"""

import os
import sys
import json
import random
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Suppress google.generativeai deprecation warning (will migrate to google.genai later)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

# Setup
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
CONCEPTS_FILE = DATA_DIR / "pre_generated_concepts.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class PreWorkFetcher:
    """Fetches and caches data for video generation."""
    
    def __init__(self):
        self.client = None
        self.gemini_model = None
        self._init_ai()
    
    def _init_ai(self):
        """Initialize AI clients."""
        # Groq
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=groq_key)
                safe_print("[OK] Groq initialized")
            except Exception as e:
                safe_print(f"[!] Groq init failed: {e}")
        
        # Gemini - v16.8: DYNAMIC MODEL
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                # v16.8: Get dynamic model list
                try:
                    from quota_optimizer import get_quota_optimizer
                    optimizer = get_quota_optimizer()
                    gemini_models = optimizer.get_gemini_models(gemini_key)
                    model_to_use = gemini_models[0] if gemini_models else 'gemini-2.5-flash'
                except:
                    model_to_use = 'gemini-2.5-flash'
                
                self.gemini_model = genai.GenerativeModel(model_to_use)
                self.gemini_models_list = gemini_models if 'gemini_models' in dir() else ['gemini-2.5-flash']
                safe_print(f"[OK] Gemini initialized ({model_to_use})")
            except Exception as e:
                safe_print(f"[!] Gemini init failed: {e}")
    
    def call_ai(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call AI with fallback."""
        # v16.8: DYNAMIC MODEL - No hardcoded model names
        if self.client:
            try:
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                groq_models = optimizer.get_groq_models()
                model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
            except:
                model_to_use = "llama-3.3-70b-versatile"
            
            try:
                response = self.client.chat.completions.create(
                    model=model_to_use,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.9
                )
                return response.choices[0].message.content
            except Exception as e:
                safe_print(f"[!] Groq error: {e}")
        
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                safe_print(f"[!] Gemini error: {e}")
        
        return ""
    
    def parse_json(self, text: str) -> Dict:
        """Parse JSON from AI response."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        return {}
    
    def fetch_trending_categories(self) -> List[str]:
        """AI suggests trending categories.
        v17.7.14: Now also fetches from Google Trends via multi_trend_fetcher.
        """
        safe_print("\n[1/3] Fetching trending categories...")
        
        # v17.7.14: Try to get real trending topics first
        real_trends = []
        try:
            from multi_trend_fetcher import GoogleTrendsFetcher
            gtrends = GoogleTrendsFetcher()
            topics = gtrends.fetch(region="us", count=10)
            real_trends = [t.topic for t in topics if t.topic]
            if real_trends:
                safe_print(f"   [TRENDS] Got {len(real_trends)} real trending topics from Google")
        except Exception as e:
            safe_print(f"   [!] Google Trends fetch failed: {e}")
        
        today = datetime.now().strftime("%B %d, %Y")
        
        # Include real trends in prompt if available
        trends_hint = ""
        if real_trends:
            trends_hint = f"\n\nREAL TRENDING TOPICS RIGHT NOW:\n{', '.join(real_trends[:8])}\n\nIncorporate these trends into your categories!"
        
        prompt = f"""You are a viral content strategist. Today is {today}.{trends_hint}

What are the TOP 15 trending content categories for short-form video RIGHT NOW?

Consider:
- Current events and news
- Seasonal relevance
- Social media trends
- Evergreen high-performers

Return JSON:
{{"categories": ["category1", "category2", ...]}}

JSON ONLY."""

        response = self.call_ai(prompt, 500)
        result = self.parse_json(response)
        
        categories = result.get('categories', [
            'ai_trends', 'productivity', 'psychology', 'money_hacks',
            'health_tips', 'tech_news', 'life_hacks', 'motivation'
        ])
        
        safe_print(f"   Got {len(categories)} categories")
        return categories
    
    def generate_video_concepts(self, categories: List[str], count: int = 20) -> List[Dict]:
        """Pre-generate video concepts for the day."""
        safe_print(f"\n[2/3] Pre-generating {count} video concepts...")
        
        prompt = f"""You are a viral video content creator.

Generate {count} UNIQUE video concepts for short-form content.

Categories to use: {json.dumps(categories[:10])}

For EACH concept provide:
- category: from the list
- topic: specific engaging topic
- hook: attention-grabbing first line
- voice_style: energetic/calm/mysterious/authoritative/friendly/dramatic
- music_mood: upbeat/dramatic/mysterious/inspirational/chill/intense
- target_duration: 40-50 seconds

IMPORTANT:
- Each concept must be UNIQUE
- Topics should be SPECIFIC (not generic)
- Hooks should create curiosity

Return JSON:
{{"concepts": [
    {{"category": "...", "topic": "...", "hook": "...", "voice_style": "...", "music_mood": "...", "target_duration": 30}},
    ...
]}}

JSON ONLY."""

        response = self.call_ai(prompt, 3000)
        
        # Try to parse
        try:
            if "[" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                concepts = json.loads(response[start:end])
                safe_print(f"   Generated {len(concepts)} concepts")
                return concepts
        except:
            pass
        
        result = self.parse_json(response)
        concepts = result.get('concepts', [])
        safe_print(f"   Generated {len(concepts)} concepts")
        return concepts
    
    def suggest_voice_music_pairs(self, count: int = 10) -> List[Dict]:
        """Pre-generate voice and music combinations."""
        safe_print("\n[3/3] Generating voice/music pairs...")
        
        voices = [
            'en-US-AriaNeural', 'en-US-JennyNeural', 'en-US-GuyNeural',
            'en-US-DavisNeural', 'en-AU-WilliamNeural', 'en-GB-RyanNeural',
            'en-CA-LiamNeural', 'en-US-ChristopherNeural', 'en-US-EricNeural',
            'en-US-MichelleNeural'
        ]
        
        moods = ['upbeat', 'dramatic', 'mysterious', 'inspirational', 'chill', 'intense']
        
        pairs = []
        used_voices = []
        
        for i in range(count):
            # Ensure voice variety
            available = [v for v in voices if v not in used_voices[-5:]]
            voice = random.choice(available) if available else random.choice(voices)
            mood = random.choice(moods)
            
            pairs.append({
                'voice': voice,
                'rate': random.choice(['+5%', '+8%', '+0%', '-3%']),
                'music_mood': mood
            })
            used_voices.append(voice)
        
        safe_print(f"   Generated {len(pairs)} voice/music pairs")
        return pairs
    
    def run(self) -> Dict:
        """Run the full pre-work fetch."""
        safe_print("=" * 60)
        safe_print("   PRE-WORK DATA FETCHER")
        safe_print("   Fetching data for today's video generation")
        safe_print("=" * 60)
        
        # Fetch all data
        categories = self.fetch_trending_categories()
        concepts = self.generate_video_concepts(categories, count=20)
        voice_music = self.suggest_voice_music_pairs(count=15)
        
        # Compile data
        data = {
            'generated_at': datetime.now().isoformat(),
            'valid_until': (datetime.now().replace(hour=23, minute=59)).isoformat(),
            'categories': categories,
            'concepts': concepts,
            'voice_music_pairs': voice_music,
            'concepts_used': 0,
            'pairs_used': 0
        }
        
        # Save to file
        with open(CONCEPTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        safe_print(f"\n{'=' * 60}")
        safe_print(f"   PRE-WORK COMPLETE!")
        safe_print(f"   Categories: {len(categories)}")
        safe_print(f"   Concepts: {len(concepts)}")
        safe_print(f"   Voice/Music Pairs: {len(voice_music)}")
        safe_print(f"   Saved to: {CONCEPTS_FILE}")
        safe_print(f"{'=' * 60}")
        
        return data


def get_next_concept() -> Dict:
    """Get the next unused concept from pre-generated data."""
    if not CONCEPTS_FILE.exists():
        return None
    
    with open(CONCEPTS_FILE, 'r') as f:
        data = json.load(f)
    
    concepts = data.get('concepts', [])
    used = data.get('concepts_used', 0)
    
    if used >= len(concepts):
        return None  # All concepts used
    
    concept = concepts[used]
    
    # Update usage counter
    data['concepts_used'] = used + 1
    with open(CONCEPTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return concept


def get_next_voice_music() -> Dict:
    """Get the next unused voice/music pair."""
    if not CONCEPTS_FILE.exists():
        return None
    
    with open(CONCEPTS_FILE, 'r') as f:
        data = json.load(f)
    
    pairs = data.get('voice_music_pairs', [])
    used = data.get('pairs_used', 0)
    
    if used >= len(pairs):
        used = 0  # Cycle through
    
    pair = pairs[used]
    
    # Update usage counter
    data['pairs_used'] = used + 1
    with open(CONCEPTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return pair


def has_valid_data() -> bool:
    """Check if we have valid pre-generated data."""
    if not CONCEPTS_FILE.exists():
        return False
    
    try:
        with open(CONCEPTS_FILE, 'r') as f:
            data = json.load(f)
        
        # Check if data is still valid (same day)
        generated = datetime.fromisoformat(data['generated_at'])
        if generated.date() != datetime.now().date():
            return False
        
        # Check if we have unused concepts
        concepts = data.get('concepts', [])
        used = data.get('concepts_used', 0)
        
        return used < len(concepts)
    except:
        return False


if __name__ == "__main__":
    fetcher = PreWorkFetcher()
    fetcher.run()








