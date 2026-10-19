#!/usr/bin/env python3
"""
ViralShorts Factory - AI Trend Analyzer v17.8
===============================================

Analyzes trends using AI to identify content opportunities.
"""

import os
try:
    from model_helper import get_dynamic_gemini_model
except ImportError:
    try:
        from src.ai.model_helper import get_dynamic_gemini_model
    except ImportError:
        def get_dynamic_gemini_model(): return "gemini-2.5-flash"
import json
import re
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

TREND_FILE = STATE_DIR / "ai_trends.json"


class AITrendAnalyzer:
    """Analyzes trends using AI."""
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if TREND_FILE.exists():
                with open(TREND_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "trends": [],
            "analyses": [],
            "predictions": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(TREND_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_trend(self, topic: str, category: str = "general") -> Dict:
        """
        Analyze a trend and its potential.
        
        Returns analysis with score and recommendations.
        """
        # Try AI analysis
        ai_result = self._analyze_with_ai(topic, category)
        
        if ai_result:
            safe_print(f"   [TREND] AI-analyzed: {topic[:30]}...")
            return ai_result
        
        return self._fallback_analysis(topic, category)
    
    def _analyze_with_ai(self, topic: str, category: str) -> Optional[Dict]:
        """Analyze with AI."""
        prompt = f"""Analyze this trend for YouTube Shorts content potential.

TREND: {topic}
CATEGORY: {category}

ANALYZE:
1. Is this trend rising, peaking, or declining?
2. How saturated is the content space?
3. What unique angle could stand out?
4. What's the virality potential?
5. Best content format for this trend?

Return JSON:
{{
  "trend_phase": "rising|peaking|declining",
  "saturation": "low|medium|high",
  "unique_angle": "Your suggested angle",
  "virality_potential": 1-10,
  "best_format": "list|story|how-to|comparison",
  "time_sensitivity": "urgent|normal|evergreen",
  "recommended_action": "create now|wait|skip",
  "hook_suggestion": "Example hook for this trend"
}}

JSON ONLY."""

        result = self._call_ai(prompt)
        if result:
            return self._parse_response(result)
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
                # v17.9.10: Dynamic model selection
                try:
                    from model_helper import get_dynamic_groq_model
                    model = get_dynamic_groq_model()
                except ImportError:
                    try:
                        from src.ai.model_helper import get_dynamic_groq_model
                        model = get_dynamic_groq_model()
                    except:
                        model = "llama-3.3-70b-versatile"  # Emergency fallback
                
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=250,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse JSON response."""
        try:
            match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None
    
    def _fallback_analysis(self, topic: str, category: str) -> Dict:
        """Rule-based fallback."""
        # Check for evergreen indicators
        evergreen_words = ["always", "forever", "secret", "truth", "human", "psychology"]
        is_evergreen = any(w in topic.lower() for w in evergreen_words)
        
        # Check for trending indicators
        # v17.9.17: Use current year dynamically
        from datetime import datetime
        current_year = str(datetime.now().year)
        trending_words = ["new", current_year, "latest", "breaking", "ai", "trend"]
        is_trending = any(w in topic.lower() for w in trending_words)
        
        return {
            "trend_phase": "rising" if is_trending else "stable",
            "saturation": "medium",
            "unique_angle": f"Expert breakdown of {topic}",
            "virality_potential": 7 if is_trending else 5,
            "best_format": "list",
            "time_sensitivity": "evergreen" if is_evergreen else "normal",
            "recommended_action": "create now",
            "hook_suggestion": f"The truth about {topic} that nobody talks about"
        }
    
    def get_trending_topics(self, category: str = None, count: int = 5) -> List[Dict]:
        """
        Get AI-suggested trending topics.
        """
        prompt = f"""Suggest {count} trending topics for YouTube Shorts content.
{f'Category focus: {category}' if category else 'Any category.'}

Requirements:
- Topics should be currently trending or rising
- High viral potential
- Suitable for short-form video (under 60 seconds)

Return JSON array:
[
  {{"topic": "Topic title", "category": "category", "urgency": "high|medium", "hook": "Example hook"}}
]

JSON ONLY."""

        result = self._call_ai(prompt)
        if result:
            try:
                # Find array in response
                match = re.search(r'\[[\s\S]*\]', result)
                if match:
                    return json.loads(match.group())
            except:
                pass
        
        # Fallback topics
        return [
            {"topic": "AI tools changing work", "category": "productivity", "urgency": "high", "hook": "This AI tool will change how you work"},
            {"topic": "Money habits of millennials", "category": "money", "urgency": "medium", "hook": "Why millennials are secretly wealthy"},
            {"topic": "Psychology of first impressions", "category": "psychology", "urgency": "medium", "hook": "People judge you in 3 seconds"}
        ][:count]
    
    def predict_trend_lifecycle(self, topic: str) -> Dict:
        """Predict where a trend is in its lifecycle."""
        analysis = self.analyze_trend(topic)
        
        lifecycle = {
            "rising": {"days_left": "14-30 days", "action": "Create content NOW"},
            "peaking": {"days_left": "7-14 days", "action": "Quick turnaround needed"},
            "declining": {"days_left": "0-7 days", "action": "Consider skipping or unique angle only"}
        }
        
        phase = analysis.get("trend_phase", "stable")
        
        return {
            "topic": topic,
            "phase": phase,
            **lifecycle.get(phase, {"days_left": "Unknown", "action": "Proceed with caution"})
        }


# Singleton
_trend_analyzer = None


def get_trend_analyzer() -> AITrendAnalyzer:
    """Get singleton analyzer."""
    global _trend_analyzer
    if _trend_analyzer is None:
        _trend_analyzer = AITrendAnalyzer()
    return _trend_analyzer


def analyze_trend(topic: str, category: str = "general") -> Dict:
    """Convenience function."""
    return get_trend_analyzer().analyze_trend(topic, category)


if __name__ == "__main__":
    safe_print("Testing AI Trend Analyzer...")
    
    analyzer = get_trend_analyzer()
    
    # Test trend analysis
    result = analyzer.analyze_trend("AI tools for productivity", "productivity")
    
    safe_print(f"\nTrend Analysis:")
    safe_print("-" * 40)
    safe_print(f"Phase: {result.get('trend_phase')}")
    safe_print(f"Saturation: {result.get('saturation')}")
    safe_print(f"Virality Potential: {result.get('virality_potential')}/10")
    safe_print(f"Best Format: {result.get('best_format')}")
    safe_print(f"Action: {result.get('recommended_action')}")
    safe_print(f"Hook: {result.get('hook_suggestion')}")
    
    # Test trending topics
    safe_print(f"\nAI-Suggested Trending Topics:")
    topics = analyzer.get_trending_topics("psychology", 3)
    for t in topics:
        safe_print(f"  - {t.get('topic')} ({t.get('urgency')})")
    
    # Test lifecycle
    safe_print(f"\nLifecycle Prediction:")
    lifecycle = analyzer.predict_trend_lifecycle("AI productivity tools")
    safe_print(f"  Phase: {lifecycle.get('phase')}")
    safe_print(f"  Days Left: {lifecycle.get('days_left')}")
    safe_print(f"  Action: {lifecycle.get('action')}")
    
    safe_print("\nTest complete!")


