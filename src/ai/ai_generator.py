#!/usr/bin/env python3
"""
AI-Powered Question Generator - MULTI-PROVIDER (Groq + Gemini)
Generates viral "Would You Rather" questions using multiple FREE AI APIs
Maximizes free tier usage across providers!
"""

import os
import json
import random
import time
from typing import List, Dict, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_best_gemini_model
except ImportError:
    def get_best_gemini_model(api_key=None):
        return "gemini-2.5-flash"  # Fallback only if import fails


def get_groq_client():
    """Get Groq client if available."""
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key or not GROQ_AVAILABLE:
        return None
    return Groq(api_key=api_key)


def get_gemini_model():
    """Get Gemini model if available - uses DYNAMIC model selection."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or not GEMINI_AVAILABLE:
        return None
    try:
        genai.configure(api_key=api_key)
        # DYNAMIC MODEL SELECTION - no hardcoded model names
        model_name = get_best_gemini_model(api_key)
        return genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"[!] Gemini init failed: {e}")
        return None


def generate_with_gemini(prompt: str, count: int = 10) -> List[Dict]:
    """Generate questions using Google Gemini."""
    model = get_gemini_model()
    if not model:
        return []
    
    try:
        full_prompt = f"""{prompt}

Generate {count} questions. Return ONLY a valid JSON array, no markdown:
[{{"option_a": "...", "option_b": "...", "percentage_a": 50}}]"""
        
        response = model.generate_content(full_prompt)
        content = response.text.strip()
        
        # Clean up response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        questions = json.loads(content)
        print(f"✅ Gemini generated {len(questions)} questions!")
        return questions
    except Exception as e:
        print(f"⚠️ Gemini generation failed: {e}")
        return []


def generate_viral_questions(count: int = 10, category: str = "general") -> List[Dict]:
    """
    Use Groq AI to generate viral Would You Rather questions.
    
    Categories: general, money, superpowers, social, tech, life
    """
    client = get_groq_client()
    
    if not client:
        print("⚠️ Groq not available. Using fallback questions.")
        return []
    
    category_prompts = {
        "general": "diverse and thought-provoking",
        "money": "about wealth, success, and financial decisions",
        "superpowers": "about supernatural abilities and powers",
        "social": "about relationships, fame, and social situations",
        "tech": "about technology, AI, and the future",
        "life": "about life choices, career, and personal growth"
    }
    
    category_desc = category_prompts.get(category, category_prompts["general"])
    
    prompt = f"""You are an expert at creating viral "Would You Rather" questions for YouTube Shorts.

Generate {count} "Would You Rather" questions that are {category_desc}.

Requirements for VIRAL questions (based on data analysis):
1. Both options must be genuinely difficult to choose between (50/50 split)
2. Options should trigger emotional response or deep thinking
3. Questions should be relatable to a wide audience
4. Include some with surprising/counterintuitive elements
5. Make them conversation starters that people want to share
6. Avoid controversial political/religious topics
7. Each option should be 5-15 words for readability

For each question, also estimate what percentage would choose option A (be realistic, 30-70 range).

Return ONLY valid JSON array (no markdown):
[
  {{"option_a": "...", "option_b": "...", "percentage_a": 45}},
  {{"option_a": "...", "option_b": "...", "percentage_a": 52}}
]"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a viral content expert. Return ONLY valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        questions = json.loads(content)
        
        print(f"✅ Generated {len(questions)} AI questions!")
        return questions
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        return []


def generate_trending_questions() -> List[Dict]:
    """Generate questions based on current trends."""
    client = get_groq_client()
    
    if not client:
        return []
    
    prompt = """Generate 5 "Would You Rather" questions based on what's trending RIGHT NOW:
- AI and technology
- Work from home vs office
- Social media and influencers
- Climate and environment
- Gaming and entertainment

Make them relevant to what young people (18-35) are talking about NOW.

Return ONLY valid JSON array:
[{"option_a": "...", "option_b": "...", "percentage_a": 50}]"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        return json.loads(content)
        
    except Exception as e:
        print(f"❌ Trending generation failed: {e}")
        return []


def refresh_questions_file(output_path: str = "questions.json", count: int = 50):
    """
    Refresh the questions.json file with AI-generated questions.
    Uses BOTH Groq and Gemini for maximum variety!
    Maximizes free tier usage across all providers.
    """
    print("🤖 MAXIMIZED AI Generation - Using all free providers...")
    
    all_questions = []
    
    # ===== GROQ (30 req/min = lots of capacity) =====
    print("\n📊 Phase 1: Groq AI (Primary)")
    categories = ["general", "money", "superpowers", "social", "tech", "life"]
    groq_per_category = max(5, (count // 2) // len(categories))
    
    for category in categories:
        questions = generate_viral_questions(groq_per_category, category)
        all_questions.extend(questions)
        time.sleep(get_smart_delay("default", "groq") if "get_smart_delay" in dir() else 0.5)  # Rate limit protection
    
    # ===== GEMINI (60 req/min = even more capacity) =====
    print("\n📊 Phase 2: Google Gemini (High Quality)")
    gemini_prompts = [
        "Create unique 'Would You Rather' questions about modern life, technology, and social media",
        "Generate funny and absurd 'Would You Rather' scenarios that make people laugh",
        "Create deep philosophical 'Would You Rather' questions about life choices and values",
        "Generate 'Would You Rather' questions about superpowers, magic, and fantasy scenarios",
        "Create 'Would You Rather' questions about money, success, and career tradeoffs",
    ]
    
    gemini_per_prompt = max(5, (count // 2) // len(gemini_prompts))
    for prompt in gemini_prompts:
        gemini_qs = generate_with_gemini(prompt, gemini_per_prompt)
        all_questions.extend(gemini_qs)
        time.sleep(get_smart_delay("default", "groq") if "get_smart_delay" in dir() else 1)  # Rate limit protection
    
    # Add trending questions from Groq
    trending = generate_trending_questions()
    all_questions.extend(trending)
    
    # Deduplicate based on options
    seen = set()
    unique_questions = []
    for q in all_questions:
        key = (q.get('option_a', '').lower(), q.get('option_b', '').lower())
        if key not in seen and len(key[0]) > 5 and len(key[1]) > 5:
            seen.add(key)
            unique_questions.append(q)
    
    # Shuffle for variety
    random.shuffle(unique_questions)
    
    # Take requested count
    unique_questions = unique_questions[:count]
    
    if unique_questions:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_questions, f, indent=2)
        print(f"\n✅ MAXIMIZED: Saved {len(unique_questions)} unique questions!")
        print(f"   📁 Output: {output_path}")
    else:
        print("⚠️ No AI questions generated. Keeping existing file.")
    
    # Apply content filter
    try:
        from trending_content import TrendingContentGenerator
        filtered = TrendingContentGenerator.filter_questions(unique_questions)
        print(f"   🛡️ Content filter: {len(unique_questions)} → {len(filtered)} questions")
        return filtered
    except Exception as e:
        print(f"   ⚠️ Filter not applied: {e}")
        return unique_questions


if __name__ == "__main__":
    import sys
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    questions = refresh_questions_file(count=count)
    
    print(f"\n📊 Sample questions generated:")
    for q in questions[:3]:
        print(f"  • {q['option_a']} OR {q['option_b']}?")



