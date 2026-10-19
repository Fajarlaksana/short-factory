#!/usr/bin/env python3
"""
ViralShorts Factory - Competitor Gap Analyzer v17.8
=====================================================

Analyzes gaps between your content and competitors.
Uses AI to identify opportunities for differentiation.
"""

import os
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

GAP_FILE = STATE_DIR / "competitor_gaps.json"


class CompetitorGapAnalyzer:
    """Analyzes competitor content and identifies gaps."""
    
    # Common competitor patterns (will be expanded by AI)
    COMMON_PATTERNS = {
        "hooks": ["question", "shock", "story", "statistic", "challenge"],
        "formats": ["list", "how-to", "myth-bust", "comparison", "reaction"],
        "ctas": ["comment", "like", "follow", "share", "save"]
    }
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if GAP_FILE.exists():
                with open(GAP_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "competitors": [],
            "gaps": [],
            "opportunities": [],
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(GAP_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_gap(self, our_content: Dict, competitor_topic: str,
                   competitor_performance: Dict = None) -> Dict:
        """
        Analyze gap between our content and competitor.
        
        Args:
            our_content: Our video content
            competitor_topic: What the competitor is covering
            competitor_performance: Optional performance metrics
        
        Returns:
            Gap analysis with opportunities
        """
        # Try AI analysis
        ai_result = self._analyze_with_ai(our_content, competitor_topic, competitor_performance)
        
        if ai_result:
            safe_print("   [GAP] AI-analyzed competitor gap")
            return ai_result
        
        # Fallback to rule-based
        return self._fallback_analysis(our_content, competitor_topic)
    
    def _analyze_with_ai(self, our_content: Dict, competitor_topic: str,
                        competitor_performance: Dict) -> Optional[Dict]:
        """Analyze with AI."""
        our_hook = our_content.get("hook", "")
        our_category = our_content.get("category", "general")
        
        prompt = f"""Analyze the competitive gap and suggest differentiation.

OUR CONTENT:
- Category: {our_category}
- Hook: {our_hook}

COMPETITOR:
- Topic: {competitor_topic}
- Performance: {json.dumps(competitor_performance) if competitor_performance else 'Unknown'}

ANALYZE:
1. What gap exists between our content and theirs?
2. How can we differentiate?
3. What unique angle can we take?
4. What value can we add that they missed?

Return JSON:
{{
  "gap_type": "topic|angle|depth|format|hook",
  "gap_description": "What they cover that we don't",
  "differentiation": "How to stand out",
  "unique_angle": "Our unique perspective",
  "value_add": "Extra value we can provide",
  "urgency": "high|medium|low",
  "suggested_topic": "A specific topic we should cover"
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
                model = genai.GenerativeModel('gemini-2.5-flash')
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
                    max_tokens=300,
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
    
    def _fallback_analysis(self, our_content: Dict, competitor_topic: str) -> Dict:
        """Rule-based fallback analysis."""
        our_category = our_content.get("category", "general")
        our_hook = our_content.get("hook", "")
        
        # Simple gap detection
        gaps = []
        
        # Check topic coverage
        if competitor_topic.lower() not in our_hook.lower():
            gaps.append("Topic not covered in our hook")
        
        # Generate suggestions
        return {
            "gap_type": "topic",
            "gap_description": f"Competitor covers: {competitor_topic}",
            "differentiation": "Take a contrarian or deeper angle",
            "unique_angle": f"Expert perspective on {our_category}",
            "value_add": "Actionable steps they don't provide",
            "urgency": "medium",
            "suggested_topic": f"Deep dive: {competitor_topic}"
        }
    
    def identify_opportunities(self, category: str) -> List[Dict]:
        """
        Identify opportunities based on category gaps.
        
        Returns list of opportunity dicts.
        """
        opportunities = []
        
        # Category-specific gaps
        category_gaps = {
            "psychology": [
                {"gap": "Cognitive biases in daily life", "angle": "practical examples"},
                {"gap": "Dark psychology ethics", "angle": "balanced view"},
                {"gap": "Body language micro-expressions", "angle": "detection guide"}
            ],
            "money": [
                {"gap": "Inflation-proof investments", "angle": "2026 strategies"},
                {"gap": "Side hustle automation", "angle": "AI tools"},
                {"gap": "Debt elimination speed", "angle": "psychological hacks"}
            ],
            "productivity": [
                {"gap": "AI productivity tools", "angle": "real workflow demos"},
                {"gap": "Focus without medication", "angle": "natural methods"},
                {"gap": "Remote work optimization", "angle": "environment design"}
            ],
            "motivation": [
                {"gap": "Sustainable motivation", "angle": "systems over feelings"},
                {"gap": "Comeback stories", "angle": "actionable lessons"},
                {"gap": "Mental toughness training", "angle": "daily exercises"}
            ]
        }
        
        gaps = category_gaps.get(category, [])
        
        for gap in gaps:
            opportunities.append({
                "category": category,
                "gap": gap["gap"],
                "suggested_angle": gap["angle"],
                "priority": "high" if len(opportunities) < 2 else "medium"
            })
        
        return opportunities
    
    def record_competitor(self, name: str, topics: List[str], 
                         avg_views: int = 0):
        """Record a competitor for tracking."""
        competitor = {
            "name": name,
            "topics": topics,
            "avg_views": avg_views,
            "added": datetime.now().isoformat()
        }
        
        # Avoid duplicates
        if not any(c["name"] == name for c in self.data["competitors"]):
            self.data["competitors"].append(competitor)
            self._save()


# Singleton
_gap_analyzer = None


def get_gap_analyzer() -> CompetitorGapAnalyzer:
    """Get singleton analyzer."""
    global _gap_analyzer
    if _gap_analyzer is None:
        _gap_analyzer = CompetitorGapAnalyzer()
    return _gap_analyzer


def analyze_competitor_gap(our_content: Dict, competitor_topic: str, **kwargs) -> Dict:
    """Convenience function."""
    return get_gap_analyzer().analyze_gap(our_content, competitor_topic, **kwargs)


if __name__ == "__main__":
    safe_print("Testing Competitor Gap Analyzer...")
    
    analyzer = get_gap_analyzer()
    
    # Test gap analysis
    our_content = {
        "hook": "Why successful people wake up at 5 AM",
        "category": "productivity",
        "topic": "morning routines"
    }
    
    competitor_topic = "Evening routines that boost productivity"
    
    result = analyzer.analyze_gap(our_content, competitor_topic)
    
    safe_print(f"\nGap Analysis:")
    safe_print("-" * 40)
    safe_print(f"Gap Type: {result.get('gap_type')}")
    safe_print(f"Description: {result.get('gap_description')}")
    safe_print(f"Differentiation: {result.get('differentiation')}")
    safe_print(f"Unique Angle: {result.get('unique_angle')}")
    safe_print(f"Urgency: {result.get('urgency')}")
    safe_print(f"Suggested Topic: {result.get('suggested_topic')}")
    
    # Test opportunities
    safe_print(f"\nOpportunities for 'productivity':")
    opps = analyzer.identify_opportunities("productivity")
    for opp in opps[:3]:
        safe_print(f"  - {opp['gap']} ({opp['suggested_angle']})")
    
    safe_print("\nTest complete!")

