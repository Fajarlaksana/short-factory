#!/usr/bin/env python3
"""
ViralShorts Factory - AI Comment Response Generator v17.8
===========================================================

Generates engaging responses to viewer comments.
Builds community and boosts engagement.
"""

import os
from src.ai.model_helper import get_dynamic_gemini_model
import json
import re
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

COMMENT_FILE = STATE_DIR / "comment_responses.json"


class AICommentResponseGenerator:
    """Generates responses to viewer comments."""
    
    # Response templates by comment type
    TEMPLATES = {
        "positive": [
            "Thanks for watching! Glad you found this helpful!",
            "Appreciate the support! More content coming!",
            "Happy you enjoyed it! What topic should I cover next?",
            "Love the energy! Thanks for commenting!",
        ],
        "question": [
            "Great question! Let me explain...",
            "Good thinking! Here's the answer:",
            "I get this a lot! The key is...",
            "Excellent question - I'll make a video on this!",
        ],
        "negative": [
            "Thanks for sharing your perspective!",
            "I appreciate the feedback. Different views are welcome!",
            "Interesting point! What would you suggest instead?",
        ],
        "request": [
            "Great idea! I'll add it to my content list!",
            "Love this suggestion! Stay tuned!",
            "On it! This is a great topic for a future video!",
        ]
    }
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if COMMENT_FILE.exists():
                with open(COMMENT_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "responses": [],
            "templates": self.TEMPLATES,
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(COMMENT_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_response(self, comment: str, video_topic: str = None) -> Dict:
        """
        Generate a response to a comment.
        
        Returns response with sentiment analysis.
        """
        # Classify comment
        sentiment = self._classify_comment(comment)
        
        # Try AI response
        ai_response = self._generate_with_ai(comment, sentiment, video_topic)
        
        if ai_response:
            safe_print(f"   [COMMENT] AI-generated response")
            return {
                "comment": comment,
                "sentiment": sentiment,
                "response": ai_response,
                "ai_generated": True
            }
        
        # Use template
        template = random.choice(self.TEMPLATES.get(sentiment, self.TEMPLATES["positive"]))
        
        return {
            "comment": comment,
            "sentiment": sentiment,
            "response": template,
            "ai_generated": False
        }
    
    def _classify_comment(self, comment: str) -> str:
        """Classify comment sentiment/type."""
        comment_lower = comment.lower()
        
        # Check for questions
        if "?" in comment or any(w in comment_lower for w in ["how", "what", "why", "when", "where"]):
            return "question"
        
        # Check for requests
        if any(w in comment_lower for w in ["please", "can you", "make a video", "do a video", "cover"]):
            return "request"
        
        # Check for negative
        if any(w in comment_lower for w in ["bad", "wrong", "hate", "terrible", "disagree", "fake", "lie", "don't agree", "not agree", "stupid", "dumb"]):
            return "negative"
        
        # Default to positive
        return "positive"
    
    def _generate_with_ai(self, comment: str, sentiment: str, 
                         video_topic: str) -> Optional[str]:
        """Generate with AI."""
        prompt = f"""Generate a brief, engaging reply to this YouTube comment.

COMMENT: "{comment}"
SENTIMENT: {sentiment}
{f'VIDEO TOPIC: {video_topic}' if video_topic else ''}

RULES:
1. Keep it SHORT (1-2 sentences max)
2. Be friendly and genuine
3. Encourage further engagement if appropriate
4. Don't be defensive if negative
5. Ask a follow-up question if it fits
6. No emojis unless they're essential

Return ONLY the response text, no quotes."""

        result = self._call_ai(prompt)
        if result:
            return result.strip('"').strip()
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                safe_print(f"   [!] Gemini error: {e}")
        
        if self.groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def generate_batch_responses(self, comments: List[str], 
                                video_topic: str = None) -> List[Dict]:
        """Generate responses for multiple comments."""
        return [self.generate_response(c, video_topic) for c in comments]
    
    def get_engagement_boosters(self) -> List[str]:
        """Get phrases that boost comment engagement."""
        return [
            "What do you think?",
            "Have you tried this?",
            "Let me know in the comments!",
            "Drop your experience below!",
            "Do you agree?",
            "What would you add?",
            "Share your thoughts!",
        ]
    
    def get_pinnable_comment(self, video_topic: str) -> str:
        """Generate a pinnable comment for the video creator."""
        starters = [
            f"What's your experience with {video_topic}? Comment below!",
            f"Did this change how you think about {video_topic}? Let me know!",
            f"Tag someone who needs to hear this about {video_topic}!",
            f"Save this for later and share with a friend!",
        ]
        return random.choice(starters)


# Singleton
_comment_generator = None


def get_comment_generator() -> AICommentResponseGenerator:
    """Get singleton generator."""
    global _comment_generator
    if _comment_generator is None:
        _comment_generator = AICommentResponseGenerator()
    return _comment_generator


def generate_comment_response(comment: str, **kwargs) -> Dict:
    """Convenience function."""
    return get_comment_generator().generate_response(comment, **kwargs)


if __name__ == "__main__":
    safe_print("Testing AI Comment Response Generator...")
    
    generator = get_comment_generator()
    
    # Test comments
    comments = [
        "This is so helpful! Thank you!",
        "How do I apply this to my life?",
        "Can you make a video about morning routines?",
        "I don't agree with this at all."
    ]
    
    safe_print("\nComment Responses:")
    safe_print("-" * 50)
    
    for comment in comments:
        result = generator.generate_response(comment, "productivity tips")
        safe_print(f"\nComment: \"{comment}\"")
        safe_print(f"Sentiment: {result['sentiment']}")
        safe_print(f"Response: {result['response']}")
        safe_print(f"AI Generated: {result['ai_generated']}")
    
    # Test pinnable comment
    safe_print(f"\nPinnable Comment:")
    pin = generator.get_pinnable_comment("success habits")
    safe_print(f"  {pin}")
    
    # Test engagement boosters
    safe_print(f"\nEngagement Boosters:")
    for booster in generator.get_engagement_boosters()[:3]:
        safe_print(f"  - {booster}")
    
    safe_print("\nTest complete!")


