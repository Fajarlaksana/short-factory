#!/usr/bin/env python3
"""
ViralShorts Factory - AI Topic Suggester v17.8
===============================================

Suggests topics based on:
1. Historical performance data
2. Current trends
3. Audience interests
4. Content gaps

NO HARDCODED TOPICS - Everything is AI-generated!
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

TOPIC_SUGGESTIONS_FILE = STATE_DIR / "topic_suggestions.json"


class AITopicSuggester:
    """
    Suggests viral topics using AI and performance data.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if TOPIC_SUGGESTIONS_FILE.exists():
                with open(TOPIC_SUGGESTIONS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "suggestions": [],
            "performance_insights": {},
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(TOPIC_SUGGESTIONS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_suggestions(self, count: int = 5, 
                       category: str = None,
                       avoid_recent: List[str] = None) -> List[Dict]:
        """
        Get AI-generated topic suggestions.
        
        Args:
            count: Number of topics to suggest
            category: Optional category filter
            avoid_recent: Topics to avoid (recently used)
        
        Returns:
            List of topic dicts with topic, category, hook_idea
        """
        # Get performance insights
        performance = self._get_performance_insights()
        
        # Generate with AI
        suggestions = self._generate_with_ai(count, category, avoid_recent, performance)
        
        if suggestions:
            self.data["suggestions"] = suggestions
            self._save()
            return suggestions
        
        # Fallback: Generate without performance data
        return self._generate_simple(count, category)
    
    def _get_performance_insights(self) -> Dict:
        """
        Get insights from historical performance and aggressive mode learning.
        
        v18.6: FIXED - Now reads from correct paths that aggressive mode saves to:
        - variety_state.json: learned_weights, do_more, avoid, hook_templates
        - self_learning.json: patterns (hooks), do_more, avoid
        - viral_patterns.json: title_patterns, hook_patterns
        """
        insights = {}
        
        # 1. Load variety_state (primary learning storage from aggressive mode)
        try:
            variety_file = STATE_DIR / "variety_state.json"
            if variety_file.exists():
                with open(variety_file, 'r') as f:
                    variety = json.load(f)
                
                # v18.6: Read from CORRECT paths (what aggressive mode saves)
                # Learned category weights
                learned_weights = variety.get("learned_weights", {})
                if learned_weights and isinstance(learned_weights, dict):
                    sorted_cats = sorted(learned_weights.keys(), 
                                       key=lambda x: learned_weights[x].get("weight", 0) if isinstance(learned_weights[x], dict) else 0, 
                                       reverse=True)
                    insights["best_categories"] = sorted_cats[:5]
                
                # Preferred categories and subcategories
                insights["preferred_categories"] = variety.get("preferred_categories", [])
                insights["preferred_subcategories"] = variety.get("preferred_subcategories", [])
                
                # Actionable insights from aggressive mode
                insights["do_more"] = variety.get("do_more", [])[:5]
                insights["avoid"] = variety.get("avoid", [])[:5]
                
                # Hook templates from virality research
                insights["hook_templates"] = variety.get("hook_templates", [])
                insights["contrarian_insights"] = variety.get("contrarian_insights", [])[:3]
                
                # All patterns and mistakes
                insights["all_patterns"] = variety.get("all_patterns", [])[:10]
                insights["all_mistakes"] = variety.get("all_mistakes", [])[:5]
                
                # Recent usage to avoid repetition
                insights["recent_categories"] = variety.get("categories", [])[-10:]
                insights["recent_topics"] = variety.get("topics", [])[-10:]
        except:
            pass
        
        # 2. Load self_learning.json (hook patterns with success data)
        try:
            learning_file = STATE_DIR / "self_learning.json"
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    learning = json.load(f)
                
                # Get hook patterns sorted by success
                patterns = learning.get("patterns", {})
                hooks = patterns.get("hooks", [])
                if hooks:
                    sorted_hooks = sorted(hooks, key=lambda x: x.get("success_count", 0), reverse=True)
                    insights["best_hooks"] = [h.get("value") for h in sorted_hooks[:5] if h.get("value")]
                    
                    # Extract avoid phrases from low-performing hooks
                    worst_hooks = sorted(hooks, key=lambda x: x.get("failure_count", 0), reverse=True)
                    insights["avoid_phrases"] = [h.get("value") for h in worst_hooks[:5] if h.get("value")]
        except:
            pass
        
        # 3. Load viral_patterns.json (general viral patterns)
        try:
            viral_file = STATE_DIR / "viral_patterns.json"
            if viral_file.exists():
                with open(viral_file, 'r') as f:
                    viral = json.load(f)
                
                insights["title_patterns"] = viral.get("title_patterns", [])[:5]
                insights["hook_patterns"] = viral.get("hook_patterns", [])[:5]
                insights["psych_triggers"] = viral.get("psychological_triggers", [])[:5]
        except:
            pass
        
        return insights
    
    def _generate_with_ai(self, count: int, category: str,
                         avoid_recent: List[str], performance: Dict) -> List[Dict]:
        """Generate topics with AI."""
        now = datetime.now()
        
        # v18.6: Build comprehensive context from all learning sources
        best_cats = performance.get("best_categories", performance.get("preferred_categories", []))
        hook_templates = performance.get("hook_templates", [])
        do_more = performance.get("do_more", [])
        avoid_list = performance.get("avoid", [])
        psych_triggers = performance.get("psych_triggers", [])
        contrarian = performance.get("contrarian_insights", [])
        
        prompt = f"""You are a viral content strategist.

TASK: Generate {count} viral video topics for YouTube Shorts.

CURRENT CONTEXT:
- Date: {now.strftime("%B %d, %Y")}
- Day: {now.strftime("%A")}
- Category filter: {category if category else "any"}

PERFORMANCE INSIGHTS (from our analytics):
- Best performing categories: {best_cats[:5] if best_cats else ["psychology", "money", "productivity"]}
- Best hook styles: {performance.get("best_hooks", [])}
- Hook templates that work: {hook_templates[:3] if hook_templates else []}
- Do MORE of: {do_more[:3] if do_more else []}
- Avoid topics like: {avoid_recent if avoid_recent else "none"}
- Topics/styles to AVOID: {avoid_list[:3] if avoid_list else []}
- Recent topics (don't repeat): {performance.get("recent_topics", [])[-5:]}

PSYCHOLOGICAL TRIGGERS THAT WORK:
{psych_triggers[:5] if psych_triggers else ["curiosity gap", "identity challenge", "FOMO"]}

CONTRARIAN ANGLES (unexpected takes that went viral):
{contrarian[:2] if contrarian else []}

REQUIREMENTS:
1. Topics must be SPECIFIC (not vague)
2. Topics must have clear value proposition
3. Topics must work for 15-30 second videos
4. Topics must be evergreen or currently trending
5. Use the psychological triggers and hook templates above

Return JSON array:
[{{"topic": "specific topic", "category": "category", "hook_idea": "scroll-stopping hook", "value": "what viewer learns"}}]

JSON ONLY."""

        result = self._call_ai(prompt)
        
        if result:
            return self._parse_suggestions(result)
        
        return []
    
    def _call_ai(self, prompt: str) -> Optional[str]:
        """Call AI (Gemini first, then Groq)."""
        # Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(get_dynamic_gemini_model())
                response = model.generate_content(prompt)
                return response.text
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
                    max_tokens=800,
                    temperature=0.9
                )
                return response.choices[0].message.content
            except Exception as e:
                safe_print(f"   [!] Groq error: {e}")
        
        return None
    
    def _parse_suggestions(self, result: str) -> List[Dict]:
        """Parse AI response to suggestions list."""
        try:
            # Extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            # Find array
            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception as e:
            safe_print(f"   [!] Parse error: {e}")
        
        return []
    
    def _generate_simple(self, count: int, category: str) -> List[Dict]:
        """Simple topic generation without AI."""
        # This is a fallback - should rarely be used
        templates = [
            {"topic": "Psychology facts that explain everyday behavior", "category": "psychology"},
            {"topic": "Money habits of successful people", "category": "money"},
            {"topic": "Productivity tips that actually work", "category": "productivity"},
            {"topic": "Health myths debunked by science", "category": "health"},
            {"topic": "Communication tricks for better relationships", "category": "relationships"},
        ]
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        return templates[:count]
    
    def record_topic_performance(self, topic: str, category: str, 
                                views: int, likes: int):
        """Record how a topic performed for learning."""
        if "performance_insights" not in self.data:
            self.data["performance_insights"] = {}
        
        key = f"{category}:{hash(topic) % 10000}"
        self.data["performance_insights"][key] = {
            "topic": topic,
            "category": category,
            "views": views,
            "likes": likes,
            "ctr": likes / max(views, 1),
            "recorded": datetime.now().isoformat()
        }
        
        self._save()


# Singleton
_topic_suggester = None


def get_topic_suggester() -> AITopicSuggester:
    """Get the singleton topic suggester."""
    global _topic_suggester
    if _topic_suggester is None:
        _topic_suggester = AITopicSuggester()
    return _topic_suggester


def get_topic_suggestions(count: int = 5, category: str = None) -> List[Dict]:
    """Convenience function to get topic suggestions."""
    return get_topic_suggester().get_suggestions(count, category)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Topic Suggester...")
    
    suggester = get_topic_suggester()
    
    # Test suggestion generation
    suggestions = suggester.get_suggestions(count=3)
    
    safe_print(f"\nGenerated {len(suggestions)} suggestions:")
    for s in suggestions:
        safe_print(f"  - {s.get('topic', 'N/A')}")
        safe_print(f"    Category: {s.get('category', 'N/A')}")
        safe_print(f"    Hook: {s.get('hook_idea', 'N/A')}")
    
    safe_print("\nTest complete!")


