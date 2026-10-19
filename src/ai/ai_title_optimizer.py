#!/usr/bin/env python3
"""
ViralShorts Factory - AI Title Optimizer v17.8
===============================================

Optimizes video titles using AI for maximum CTR.

Titles are critical for:
- YouTube algorithm (search ranking)
- Viewer click decision
- Setting expectations

This uses AI to generate and optimize titles based on performance data.
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
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

TITLE_PERFORMANCE_FILE = STATE_DIR / "title_performance.json"


class AITitleOptimizer:
    """
    Optimizes video titles using AI and performance data.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if TITLE_PERFORMANCE_FILE.exists():
                with open(TITLE_PERFORMANCE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "patterns": {},  # pattern -> {uses, avg_ctr}
            "word_counts": {},  # count -> {uses, avg_ctr}
            "keywords": {},  # keyword -> {uses, avg_ctr}
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(TITLE_PERFORMANCE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def optimize_title(self, topic: str, category: str,
                      existing_title: str = None) -> str:
        """
        Generate or optimize a title for maximum CTR.
        
        Args:
            topic: Video topic
            category: Content category
            existing_title: Optional existing title to optimize
        
        Returns:
            Optimized title
        """
        # Get performance insights
        insights = self._get_insights()
        
        # Generate with AI
        ai_title = self._generate_with_ai(topic, category, existing_title, insights)
        
        if ai_title:
            safe_print(f"   [TITLE] AI-optimized")
            return ai_title
        
        # Fallback
        return self._fallback_title(topic, category)
    
    def _get_insights(self) -> Dict:
        """Get title performance insights."""
        insights = {}
        
        # Best word count
        if self.data.get("word_counts"):
            best_wc = max(
                self.data["word_counts"].items(),
                key=lambda x: x[1].get("avg_ctr", 0) if x[1].get("uses", 0) >= 3 else 0,
                default=(5, {})
            )
            insights["best_word_count"] = int(best_wc[0]) if best_wc[1] else 5
        
        # Best patterns
        if self.data.get("patterns"):
            best_patterns = sorted(
                [(k, v) for k, v in self.data["patterns"].items() if v.get("uses", 0) >= 3],
                key=lambda x: x[1].get("avg_ctr", 0),
                reverse=True
            )[:3]
            insights["best_patterns"] = [p[0] for p in best_patterns]
        
        # Best keywords
        if self.data.get("keywords"):
            best_keywords = sorted(
                [(k, v) for k, v in self.data["keywords"].items() if v.get("uses", 0) >= 2],
                key=lambda x: x[1].get("avg_ctr", 0),
                reverse=True
            )[:5]
            insights["best_keywords"] = [k[0] for k in best_keywords]
        
        return insights
    
    def _generate_with_ai(self, topic: str, category: str,
                         existing: str, insights: Dict) -> Optional[str]:
        """Generate optimized title with AI."""
        task = "optimize this title" if existing else "create a title"
        
        prompt = f"""You are a YouTube Shorts title expert who creates click-worthy titles.

TASK: {task.upper()}

Topic: {topic}
Category: {category}
{f'Current title: {existing}' if existing else ''}

PERFORMANCE INSIGHTS:
- Best word count: {insights.get("best_word_count", "5-8 words")}
- Best patterns: {insights.get("best_patterns", ["number hook", "curiosity gap"])}
- Best keywords: {insights.get("best_keywords", ["truth", "secret", "why"])}

TITLE REQUIREMENTS:
1. 5-10 words MAX (short and punchy)
2. Create curiosity WITHOUT clickbait
3. Include number if relevant (odd numbers work better)
4. Front-load important words
5. No ALL CAPS except one emphasis word max
6. Must work for Shorts (mobile-first)

PROVEN PATTERNS:
- "The [number] [topic] Most People Miss"
- "Why [topic] Is ACTUALLY [outcome]"
- "[number] Signs You [state]"
- "I Tested [thing] for [time]"
- "The Truth About [topic]"

Return ONLY the title text, no quotes, no explanation."""

        result = self._call_ai(prompt)
        
        if result:
            return self._clean_title(result)
        
        return None
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI."""
        # Try Gemini (better for creative tasks)
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                safe_print(f"   [!] Gemini error: {e}")
        
        # Try Groq
        if self.groq_key:
            try:
                from groq import Groq
                try:
                    from quota_optimizer import get_best_groq_model
                    model = get_best_groq_model(self.groq_key)
                except ImportError:
                    try:
                        from src.ai.model_helper import get_dynamic_groq_model
                        model = get_dynamic_groq_model()
                    except:
                        model = "llama-3.3-70b-versatile"  # Emergency only
                
                client = Groq(api_key=self.groq_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.8
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean title text."""
        # Remove quotes
        title = title.strip('"\'')
        
        # Remove newlines
        title = title.replace('\n', ' ').strip()
        
        # Truncate if too long (max 60 chars)
        if len(title) > 60:
            words = title.split()
            title = ""
            for word in words:
                if len(title) + len(word) + 1 <= 60:
                    title = title + " " + word if title else word
                else:
                    break
        
        return title
    
    def _fallback_title(self, topic: str, category: str) -> str:
        """Generate fallback title."""
        templates = [
            f"The Truth About {topic}",
            f"Why {topic} Changes Everything",
            f"5 Things About {topic} You Didn't Know",
        ]
        
        import random
        return random.choice(templates)
    
    def record_performance(self, title: str, views: int, ctr: float):
        """Record title performance for learning."""
        # Record word count
        word_count = str(len(title.split()))
        if word_count not in self.data["word_counts"]:
            self.data["word_counts"][word_count] = {"uses": 0, "total_ctr": 0}
        self.data["word_counts"][word_count]["uses"] += 1
        self.data["word_counts"][word_count]["total_ctr"] += ctr
        self.data["word_counts"][word_count]["avg_ctr"] = (
            self.data["word_counts"][word_count]["total_ctr"] /
            self.data["word_counts"][word_count]["uses"]
        )
        
        # Record pattern
        pattern = self._detect_pattern(title)
        if pattern:
            if pattern not in self.data["patterns"]:
                self.data["patterns"][pattern] = {"uses": 0, "total_ctr": 0}
            self.data["patterns"][pattern]["uses"] += 1
            self.data["patterns"][pattern]["total_ctr"] += ctr
            self.data["patterns"][pattern]["avg_ctr"] = (
                self.data["patterns"][pattern]["total_ctr"] /
                self.data["patterns"][pattern]["uses"]
            )
        
        # Record keywords
        keywords = self._extract_keywords(title)
        for kw in keywords:
            if kw not in self.data["keywords"]:
                self.data["keywords"][kw] = {"uses": 0, "total_ctr": 0}
            self.data["keywords"][kw]["uses"] += 1
            self.data["keywords"][kw]["total_ctr"] += ctr
            self.data["keywords"][kw]["avg_ctr"] = (
                self.data["keywords"][kw]["total_ctr"] /
                self.data["keywords"][kw]["uses"]
            )
        
        self._save()
    
    def _detect_pattern(self, title: str) -> Optional[str]:
        """Detect title pattern."""
        patterns = [
            (r'^\d+\s+\w+', "number_start"),
            (r'why\s+', "why_question"),
            (r'how\s+to', "how_to"),
            (r'the\s+truth', "truth_reveal"),
            (r'secret', "secret"),
            (r'\?$', "question"),
            (r'i\s+tested', "personal_test"),
        ]
        
        title_lower = title.lower()
        for pattern, name in patterns:
            if re.search(pattern, title_lower):
                return name
        
        return None
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract key words from title."""
        stop_words = {"the", "a", "an", "to", "for", "of", "and", "is", "in", "on", "at", "by"}
        words = re.findall(r'\b\w{4,}\b', title.lower())
        return [w for w in words if w not in stop_words][:5]


# Singleton
_title_optimizer = None


def get_title_optimizer() -> AITitleOptimizer:
    """Get singleton title optimizer."""
    global _title_optimizer
    if _title_optimizer is None:
        _title_optimizer = AITitleOptimizer()
    return _title_optimizer


def optimize_title(topic: str, category: str, existing: str = None) -> str:
    """Convenience function to optimize title."""
    return get_title_optimizer().optimize_title(topic, category, existing)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Title Optimizer...")
    
    optimizer = get_title_optimizer()
    
    # Test title generation
    tests = [
        ("morning routines of successful people", "productivity"),
        ("psychology of first impressions", "psychology"),
        ("money mistakes in your 20s", "money"),
    ]
    
    for topic, cat in tests:
        title = optimizer.optimize_title(topic, cat)
        safe_print(f"\nTopic: {topic}")
        safe_print(f"Title: {title}")
    
    safe_print("\nTest complete!")


