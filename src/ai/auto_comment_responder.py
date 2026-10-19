#!/usr/bin/env python3
"""
ViralShorts Factory - Auto Comment Responder v17.9.51
======================================================

Automatically generates engaging responses to comments.
Increases engagement signals for YouTube algorithm.

Features:
- Sentiment analysis of comments
- Personalized response generation
- Engagement-boosting replies
- Troll/spam detection
- Follow-up question generation

Why this matters:
- Comments with replies get 3x more engagement
- Active comment sections boost video visibility
- Responding within 1 hour has 5x impact
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from src.ai.smart_ai_caller import smart_call_ai
except ImportError:
    smart_call_ai = None


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
RESPONSES_FILE = STATE_DIR / "comment_responses.json"


class AutoCommentResponder:
    """
    Generates engaging comment responses automatically.
    """
    
    # Response templates by comment type
    RESPONSE_TEMPLATES = {
        "positive": [
            "Thank you so much! {personalized}",
            "Really appreciate that! {follow_up}",
            "Glad you found it helpful! {cta}",
            "This made my day! {personalized}",
            "You're awesome! {follow_up}"
        ],
        "question": [
            "Great question! {answer}",
            "Love that you asked! {answer} {follow_up}",
            "{answer} Let me know if you want a full video on this!",
            "I get this question a lot! {answer}"
        ],
        "negative": [
            "I appreciate your perspective! {clarification}",
            "Thanks for the feedback! {improvement}",
            "That's a fair point. {explanation}",
            "I hear you! {acknowledgment}"
        ],
        "request": [
            "Great idea! Adding it to the list!",
            "Love this suggestion! Will definitely consider it!",
            "You read my mind! Already working on something like this!",
            "Thanks for the request! Stay tuned!"
        ],
        "neutral": [
            "Thanks for watching! {follow_up}",
            "Appreciate you being here! {cta}",
            "So glad you found this! {personalized}"
        ]
    }
    
    # Engagement-boosting CTAs
    ENGAGEMENT_CTAS = [
        "What's your experience with this?",
        "Would you like to see more on this topic?",
        "What should I cover next?",
        "Drop a like if this was helpful!",
        "Share this with someone who needs it!",
        "Any questions? I'll answer below!"
    ]
    
    # Follow-up questions to boost engagement
    FOLLOW_UP_QUESTIONS = [
        "What's your biggest challenge with this?",
        "Have you tried this yourself?",
        "What topic should I cover next?",
        "What's your favorite tip from this video?",
        "How would you apply this in your life?"
    ]
    
    # Spam/troll indicators
    SPAM_INDICATORS = [
        "check out my", "subscribe to my", "follow me",
        "link in bio", "dm me", "free money", "crypto giveaway",
        "I make $", "work from home", "click here"
    ]
    
    TROLL_PATTERNS = [
        r"(fake|liar|scam|stupid|dumb|idiot)",
        r"(hate|worst|terrible|garbage|trash)",
        r"🤡|💩|👎"
    ]
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if RESPONSES_FILE.exists():
                with open(RESPONSES_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "responses_generated": [],
            "sentiment_distribution": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(RESPONSES_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_response(self, comment: str, video_topic: str = None,
                          commenter_name: str = None) -> Dict:
        """
        Generate an engaging response to a comment.
        
        Args:
            comment: The comment text
            video_topic: Topic of the video (for context)
            commenter_name: Name of commenter (for personalization)
        
        Returns:
            Dict with response and metadata
        """
        # Analyze comment
        analysis = self._analyze_comment(comment)
        
        # Check for spam/troll
        if analysis["is_spam"] or analysis["is_troll"]:
            return {
                "should_respond": False,
                "reason": "spam" if analysis["is_spam"] else "troll",
                "recommendation": "Ignore or delete this comment"
            }
        
        # Generate response
        response_text = self._generate_response_text(
            comment, analysis, video_topic, commenter_name
        )
        
        result = {
            "should_respond": True,
            "response": response_text,
            "sentiment": analysis["sentiment"],
            "comment_type": analysis["type"],
            "personalization_used": commenter_name is not None,
            "engagement_potential": self._calculate_engagement_potential(analysis)
        }
        
        # Record for learning
        self._record_response(comment, response_text, analysis)
        
        return result
    
    def _analyze_comment(self, comment: str) -> Dict:
        """Analyze comment for sentiment and type."""
        comment_lower = comment.lower()
        
        # Check for spam
        is_spam = any(ind in comment_lower for ind in self.SPAM_INDICATORS)
        
        # Check for troll
        is_troll = any(re.search(p, comment_lower) for p in self.TROLL_PATTERNS)
        
        # Detect sentiment
        positive_words = ["love", "great", "amazing", "awesome", "helpful", 
                         "thank", "best", "excellent", "perfect", "genius"]
        negative_words = ["hate", "bad", "wrong", "terrible", "disagree",
                         "waste", "boring", "useless"]
        
        positive_count = sum(1 for w in positive_words if w in comment_lower)
        negative_count = sum(1 for w in negative_words if w in comment_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect comment type
        if "?" in comment:
            comment_type = "question"
        elif any(w in comment_lower for w in ["please", "can you", "make a", "video about"]):
            comment_type = "request"
        elif sentiment == "positive":
            comment_type = "positive"
        elif sentiment == "negative":
            comment_type = "negative"
        else:
            comment_type = "neutral"
        
        return {
            "sentiment": sentiment,
            "type": comment_type,
            "is_spam": is_spam,
            "is_troll": is_troll,
            "word_count": len(comment.split()),
            "has_question": "?" in comment
        }
    
    def _generate_response_text(self, comment: str, analysis: Dict,
                                 video_topic: str, commenter_name: str) -> str:
        """Generate the response text."""
        import random
        
        comment_type = analysis["type"]
        templates = self.RESPONSE_TEMPLATES.get(comment_type, 
                                                 self.RESPONSE_TEMPLATES["neutral"])
        
        # Try AI generation first
        if smart_call_ai and analysis["word_count"] > 5:
            ai_response = self._generate_ai_response(comment, analysis, video_topic)
            if ai_response:
                # Add personalization
                if commenter_name:
                    ai_response = f"@{commenter_name} {ai_response}"
                return ai_response
        
        # Fallback to template
        template = random.choice(templates)
        
        # Fill in placeholders
        response = template.format(
            personalized=random.choice(self.FOLLOW_UP_QUESTIONS),
            follow_up=random.choice(self.FOLLOW_UP_QUESTIONS),
            cta=random.choice(self.ENGAGEMENT_CTAS),
            answer="That's a great point!",
            clarification="I appreciate you sharing that perspective.",
            improvement="Always looking to improve!",
            explanation="There's definitely nuance to this topic.",
            acknowledgment="Thanks for the honest feedback."
        )
        
        # Add personalization
        if commenter_name:
            response = f"@{commenter_name} {response}"
        
        return response
    
    def _generate_ai_response(self, comment: str, analysis: Dict,
                               video_topic: str) -> Optional[str]:
        """Generate response using AI."""
        prompt = f"""Generate a friendly, engaging response to this YouTube comment.

Comment: "{comment}"
Sentiment: {analysis['sentiment']}
Comment Type: {analysis['type']}
Video Topic: {video_topic or 'general content'}

Requirements:
1. Maximum 50 words
2. Be warm and appreciative
3. If it's a question, provide a helpful brief answer
4. Include a follow-up question or call-to-action
5. Sound natural, not robotic
6. No emojis
7. Be conversational

Return ONLY the response text, nothing else."""

        try:
            result = smart_call_ai(prompt, hint="creative", max_tokens=80)
            if result:
                response = result.strip().strip('"\'')
                if len(response) < 200:  # Sanity check
                    return response
        except Exception as e:
            safe_print(f"[COMMENT] AI error: {e}")
        
        return None
    
    def _calculate_engagement_potential(self, analysis: Dict) -> str:
        """Calculate engagement potential of responding."""
        score = 0
        
        # Questions have high potential
        if analysis["type"] == "question":
            score += 3
        
        # Positive comments build community
        if analysis["sentiment"] == "positive":
            score += 2
        
        # Longer comments = engaged viewers
        if analysis["word_count"] > 10:
            score += 1
        
        # Negative (non-troll) can be turned around
        if analysis["sentiment"] == "negative" and not analysis["is_troll"]:
            score += 1
        
        if score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    def _record_response(self, comment: str, response: str, analysis: Dict):
        """Record response for learning."""
        record = {
            "comment": comment[:100],
            "response": response[:100],
            "sentiment": analysis["sentiment"],
            "type": analysis["type"],
            "timestamp": datetime.now().isoformat()
        }
        self.data["responses_generated"].append(record)
        
        # Update sentiment distribution
        sentiment = analysis["sentiment"]
        self.data["sentiment_distribution"][sentiment] = (
            self.data["sentiment_distribution"].get(sentiment, 0) + 1
        )
        
        # Keep only last 500
        self.data["responses_generated"] = self.data["responses_generated"][-500:]
        self._save()
    
    def batch_respond(self, comments: List[Dict], video_topic: str = None) -> List[Dict]:
        """
        Generate responses for multiple comments.
        
        Args:
            comments: List of {text, author} dicts
            video_topic: Video topic for context
        
        Returns:
            List of response dicts
        """
        responses = []
        
        for comment in comments:
            response = self.generate_response(
                comment.get("text", ""),
                video_topic,
                comment.get("author")
            )
            response["original_comment"] = comment.get("text", "")[:50]
            responses.append(response)
        
        # Sort by engagement potential
        priority = {"high": 0, "medium": 1, "low": 2}
        responses.sort(
            key=lambda x: priority.get(x.get("engagement_potential", "low"), 3)
        )
        
        return responses
    
    def get_stats(self) -> Dict:
        """Get comment response statistics."""
        return {
            "total_responses": len(self.data.get("responses_generated", [])),
            "sentiment_distribution": self.data.get("sentiment_distribution", {}),
            "last_updated": self.data.get("last_updated")
        }


# Global instance
_responder = None

def get_responder() -> AutoCommentResponder:
    global _responder
    if _responder is None:
        _responder = AutoCommentResponder()
    return _responder

def generate_comment_response(comment: str, video_topic: str = None) -> Dict:
    """Generate a response to a comment."""
    return get_responder().generate_response(comment, video_topic)


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("AUTO COMMENT RESPONDER - TEST")
    safe_print("=" * 60)
    
    responder = AutoCommentResponder()
    
    # Test comments
    test_comments = [
        "This is amazing! I learned so much!",
        "Can you make a video about morning routines?",
        "I disagree with point #3, but overall good content",
        "What's the best time to practice this?",
        "check out my channel for more tips!!!"  # spam
    ]
    
    for comment in test_comments:
        safe_print(f"\nComment: {comment}")
        response = responder.generate_response(comment, "productivity tips")
        if response["should_respond"]:
            safe_print(f"Response: {response['response']}")
            safe_print(f"Engagement Potential: {response['engagement_potential']}")
        else:
            safe_print(f"Skip: {response['reason']}")
