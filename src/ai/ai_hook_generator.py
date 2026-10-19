#!/usr/bin/env python3
"""
ViralShorts Factory - AI Hook Generator v17.8
==============================================

Generates scroll-stopping hooks using AI.

Hooks are THE most important part of a short video:
- First 0.5-1.5 seconds determine if viewer stays
- Must create curiosity gap
- Must promise value
- Must stop the scroll

This module:
1. Uses AI to generate hooks based on topic/category
2. Learns from hook performance
3. Generates variations for A/B testing
"""

import os
from src.ai.model_helper import get_dynamic_gemini_model
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

HOOK_PERFORMANCE_FILE = STATE_DIR / "hook_performance.json"


class AIHookGenerator:
    """
    Generates viral hooks using AI and learns from performance.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if HOOK_PERFORMANCE_FILE.exists():
                with open(HOOK_PERFORMANCE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "generated_hooks": [],  # All hooks we've generated
            "performance": {},      # hook_hash -> {views, likes, ctr}
            "best_patterns": [],    # Patterns that work
            "worst_patterns": [],   # Patterns to avoid
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(HOOK_PERFORMANCE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def generate_hook(self, topic: str, category: str, 
                     style: str = "auto") -> str:
        """
        Generate a scroll-stopping hook for a topic.
        
        Args:
            topic: The video topic
            category: Content category (psychology, money, etc.)
            style: Hook style (question, statement, challenge, pattern_interrupt, auto)
        
        Returns:
            The generated hook text
        """
        # First try: Get from learned best patterns
        learned_hook = self._try_learned_pattern(topic, category)
        if learned_hook:
            safe_print(f"   [HOOK] Using learned pattern")
            return learned_hook
        
        # Second try: Generate with AI
        ai_hook = self._generate_with_ai(topic, category, style)
        if ai_hook:
            safe_print(f"   [HOOK] AI-generated hook")
            return ai_hook
        
        # Fallback: Simple template
        return self._fallback_hook(topic, category)
    
    def _try_learned_pattern(self, topic: str, category: str) -> Optional[str]:
        """
        v17.9.15: Apply learned best-performing patterns from analytics.
        
        Uses real performance data to create hooks with proven patterns.
        """
        if not self.data.get("best_patterns"):
            return None
        
        # Need at least 3 successful patterns to have confidence
        best_patterns = self.data.get("best_patterns", [])
        if len(best_patterns) < 3:
            return None
        
        # Get pattern performance data
        performance = self.data.get("performance", {})
        
        # Find patterns with high engagement
        high_performers = []
        for hook_hash, perf in performance.items():
            if perf.get("views", 0) > 1000 or perf.get("ctr", 0) > 0.05:
                high_performers.append(perf)
        
        if not high_performers:
            return None
        
        # Analyze successful hooks to find common patterns
        import random
        
        # v17.9.15: Use AI to adapt proven patterns to new topic
        try:
            best_hook_examples = [p.get("hook", "") for p in high_performers if p.get("hook")][:3]
            if best_hook_examples:
                # Use AI to create variation based on successful patterns
                prompt = f"""Based on these PROVEN viral hooks:
{chr(10).join(f'- "{h}"' for h in best_hook_examples)}

Create a NEW hook for this topic using the SAME patterns but different words:
Topic: {topic}
Category: {category}

Keep the same structure and psychological triggers.
Return ONLY the new hook (7-10 words max), no explanation."""
                
                result = self._call_gemini(prompt)
                if result and len(result.split()) <= 12:
                    safe_print(f"   [HOOK] Applied learned pattern!")
                    return self._clean_hook(result)
        except:
            pass
        
        return None
    
    def _generate_with_ai(self, topic: str, category: str, 
                         style: str) -> Optional[str]:
        """
        v17.9.17: HYBRID MASTER-GENERIC PROMPT with dynamic context injection.
        
        Architecture:
        1. Generic prompt (works standalone without any data)
        2. Context injection (learned patterns as EXAMPLES to guide AI)
        3. AI generates BETTER response using context as guidance
        
        Never hardcode patterns - always let AI generate with context!
        """
        
        # v17.9.17: Build CONTEXT section (injected as examples, not rules)
        context_section = self._build_context_section()
        
        prompt = f"""You are a viral content expert who creates scroll-stopping hooks.
Your hooks have generated billions of views across YouTube Shorts and TikTok.

===== YOUR TASK =====
Create ONE irresistible hook for this video that will make viewers STOP scrolling.

Topic: {topic}
Category: {category}

===== UNDERSTANDING WHAT WORKS =====
The most viral hooks share these psychological principles:
1. PATTERN INTERRUPT: Break the viewer's scroll with unexpected words
2. CURIOSITY GAP: Make them NEED to know what comes next
3. IDENTITY CHALLENGE: Make them question if they're doing something wrong
4. SPECIFIC NUMBERS: Concrete data feels more believable than vague claims
5. SHORT & PUNCHY: 7-12 words maximum - every word must earn its place

===== WHAT MAKES HOOKS SCORE HIGH =====
Our algorithm measures:
- Does it stop the scroll? (pattern interrupt words)
- Does it create curiosity? (questions, mysteries)
- Is it specific? (numbers, not vague claims)
- Is it short enough for mobile? (10 words or less ideal)
{context_section}

===== GENERATE =====
Create ONE hook for "{topic}" that applies these principles.
The hook should feel authentic and human, not robotic or formulaic.
Adapt the principles to this specific topic - don't just follow a template.

Return ONLY the hook text (7-12 words max), no quotes, no explanation."""

        result = self._call_gemini(prompt)
        if result:
            return self._clean_hook(result)
        
        result = self._call_groq(prompt)
        if result:
            return self._clean_hook(result)
        
        return None
    
    def _build_context_section(self) -> str:
        """
        v17.9.17: Build context section from learned data.
        
        This is INJECTED as examples/guidance, not as rules to follow exactly.
        The AI uses this context to generate BETTER responses.
        """
        sections = []
        
        # Get dynamic triggers from learning engine
        triggers = self._get_dynamic_triggers()
        
        # Get learned patterns from our performance data
        best_hooks = self.data.get("best_patterns", [])
        worst_hooks = self.data.get("worst_patterns", [])
        
        # Get high-performing hooks from our history
        high_performers = []
        for key, perf in self.data.get("performance", {}).items():
            if perf.get("ctr", 0) > 0.05 or perf.get("views", 0) > 1000:
                hook = perf.get("hook", "")
                if hook and len(hook) > 10:
                    high_performers.append(hook[:60])
        
        # Build context based on what data we have
        if high_performers or best_hooks:
            sections.append("\n===== EXAMPLES THAT WORKED (from our channel) =====")
            examples = high_performers[:3] if high_performers else best_hooks[:3]
            for ex in examples:
                sections.append(f'- "{ex}"')
            sections.append("(Use these as INSPIRATION, not templates to copy)")
        
        if triggers.get("source") != "none_available":
            hook_triggers = triggers.get("hook_triggers", [])
            power_words = triggers.get("power_words", [])
            
            if hook_triggers or power_words:
                sections.append("\n===== PATTERNS TRENDING NOW (from AI analysis) =====")
                if hook_triggers:
                    sections.append(f"Current viral triggers: {', '.join(hook_triggers[:5])}")
                if power_words:
                    sections.append(f"High-CTR power words: {', '.join(power_words[:5])}")
        
        if worst_hooks:
            sections.append("\n===== PATTERNS TO AVOID (underperformed) =====")
            sections.append(f"These didn't work: {', '.join(worst_hooks[:3])}")
        
        if triggers.get("avoid_words"):
            sections.append(f"Avoid these words: {', '.join(triggers.get('avoid_words', [])[:5])}")
        
        return "\n".join(sections) if sections else ""
    
    def _get_dynamic_triggers(self) -> Dict:
        """
        v18.6: Get dynamic triggers from all learning sources.
        NO HARDCODING - all from analytics/aggressive mode learning!
        
        Sources (in priority order):
        1. self_learning_engine (if available)
        2. variety_state.json (aggressive mode learning)
        3. viral_patterns.json (virality research)
        """
        result = {
            "source": "none_available",
            "hook_triggers": [],
            "power_words": [],
            "avoid_words": [],
            "hook_templates": [],
            "contrarian_insights": []
        }
        
        # 1. Try learning engine
        try:
            from self_learning_engine import get_learning_engine
            engine = get_learning_engine()
            data = engine.get_viral_triggers()
            if data.get("source") != "none_available":
                return data
        except:
            pass
        
        # 2. Load from variety_state.json (aggressive mode)
        try:
            variety_file = STATE_DIR / "variety_state.json"
            if variety_file.exists():
                with open(variety_file, 'r') as f:
                    variety = json.load(f)
                
                result["source"] = "variety_state"
                
                # Hook templates from virality research
                result["hook_templates"] = variety.get("hook_templates", [])
                result["hook_triggers"] = variety.get("psych_triggers", [])
                
                # Patterns and mistakes
                patterns = variety.get("all_patterns", [])
                if patterns:
                    # Extract power words from patterns
                    power_words = []
                    for p in patterns:
                        words = re.findall(r'\b\w+\b', str(p).lower())
                        power_words.extend([w for w in words if len(w) > 3 and w not in ["the", "that", "this", "with", "from", "have", "your", "what", "when", "where", "which"]])
                    result["power_words"] = list(set(power_words))[:10]
                
                result["avoid_words"] = variety.get("avoid", [])
                result["contrarian_insights"] = variety.get("contrarian_insights", [])
        except:
            pass
        
        # 3. Load from viral_patterns.json (virality research)
        try:
            viral_file = STATE_DIR / "viral_patterns.json"
            if viral_file.exists():
                with open(viral_file, 'r') as f:
                    viral = json.load(f)
                
                if not result["hook_templates"]:
                    result["hook_templates"] = viral.get("hook_patterns", [])
                if not result["hook_triggers"]:
                    result["hook_triggers"] = viral.get("psychological_triggers", [])
                
                if result["source"] == "none_available":
                    result["source"] = "viral_patterns"
        except:
            pass
        
        return result

        # Try Gemini first (more creative)
        hook = self._call_gemini(prompt)
        if hook:
            return self._clean_hook(hook)
        
        # Try Groq
        hook = self._call_groq(prompt)
        if hook:
            return self._clean_hook(hook)
        
        return None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API with HIGH-QUALITY model for hooks."""
        if not self.gemini_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            
            # v17.9.15: Use high-quality model for hooks (critical task)
            try:
                from model_helper import get_high_quality_model
                model_name = get_high_quality_model("gemini")
            except ImportError:
                try:
                    from src.ai.model_helper import get_high_quality_model
                    model_name = get_high_quality_model("gemini")
                except:
                    model_name = None
            
            # Fall back to regular model if pro not available
            if not model_name:
                model_name = get_dynamic_gemini_model()
            
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            safe_print(f"   [!] Gemini error: {e}")
            return None
    
    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API."""
        if not self.groq_key:
            return None
        try:
            from groq import Groq
            # v17.9.10: Dynamic model selection with proper fallback
            try:
                from model_helper import get_dynamic_groq_model
                model = get_dynamic_groq_model()
            except ImportError:
                try:
                    from src.ai.model_helper import get_dynamic_groq_model
                    model = get_dynamic_groq_model()
                except ImportError:
                    model = "llama-3.3-70b-versatile"  # Emergency fallback only
            
            client = Groq(api_key=self.groq_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.9  # Higher temperature for creativity
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            safe_print(f"   [!] Groq error: {e}")
            return None
    
    def _clean_hook(self, hook: str) -> str:
        """Clean and validate hook text."""
        # Remove quotes
        hook = hook.strip('"\'')
        
        # Remove newlines
        hook = hook.replace('\n', ' ').strip()
        
        # Truncate if too long (max 20 words)
        words = hook.split()
        if len(words) > 20:
            hook = ' '.join(words[:20]) + "..."
        
        return hook
    
    def _fallback_hook(self, topic: str, category: str) -> str:
        """Generate a simple fallback hook."""
        templates = [
            f"The truth about {topic} nobody talks about",
            f"Why {topic} is changing everything",
            f"STOP - you need to know this about {topic}",
            f"What they don't teach you about {topic}",
        ]
        import random
        return random.choice(templates)
    
    def generate_variations(self, base_hook: str, count: int = 3) -> List[str]:
        """
        Generate variations of a hook for A/B testing.
        """
        prompt = f"""Create {count} variations of this hook for A/B testing.
Each variation should have the same meaning but different style/wording.

Original: "{base_hook}"

Return ONLY the variations, one per line, no numbers or bullets."""

        result = self._call_gemini(prompt) or self._call_groq(prompt)
        
        if result:
            variations = [self._clean_hook(v) for v in result.strip().split('\n') if v.strip()]
            return variations[:count]
        
        return [base_hook]  # Return original if AI fails
    
    def record_performance(self, hook: str, views: int, likes: int):
        """Record hook performance for learning."""
        hook_hash = hash(hook) % 1000000  # Simple hash
        
        self.data["performance"][str(hook_hash)] = {
            "hook": hook,
            "views": views,
            "likes": likes,
            "ctr": likes / max(views, 1),
            "recorded": datetime.now().isoformat()
        }
        
        # Add to generated hooks
        if hook not in self.data["generated_hooks"]:
            self.data["generated_hooks"].append(hook)
        
        self._save()
    
    def get_best_hooks(self, count: int = 5) -> List[Dict]:
        """Get the best performing hooks."""
        if not self.data.get("performance"):
            return []
        
        sorted_hooks = sorted(
            self.data["performance"].values(),
            key=lambda x: x.get("views", 0),
            reverse=True
        )
        
        return sorted_hooks[:count]


# Singleton
_hook_generator = None


def get_hook_generator() -> AIHookGenerator:
    """Get the singleton hook generator."""
    global _hook_generator
    if _hook_generator is None:
        _hook_generator = AIHookGenerator()
    return _hook_generator


def generate_hook(topic: str, category: str) -> str:
    """Convenience function to generate a hook."""
    return get_hook_generator().generate_hook(topic, category)


if __name__ == "__main__":
    # Test
    safe_print("Testing AI Hook Generator...")
    
    gen = get_hook_generator()
    
    # Test hook generation
    topics = [
        ("Why successful people wake up at 5 AM", "productivity"),
        ("The psychology of first impressions", "psychology"),
        ("How to save $500 per month", "money"),
    ]
    
    for topic, cat in topics:
        hook = gen.generate_hook(topic, cat)
        safe_print(f"\nTopic: {topic}")
        safe_print(f"Hook: {hook}")
    
    safe_print("\nTest complete!")


