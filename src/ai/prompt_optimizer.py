#!/usr/bin/env python3
"""
Prompt Optimizer v1.0
=====================

Optimizes prompts for:
1. Token efficiency (shorter = cheaper)
2. Response quality (better structure = better output)
3. Model-specific tuning
4. Dynamic context injection
5. Performance tracking

NO HARDCODED CONTEXT - Everything dynamic!
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_PERF_FILE = STATE_DIR / "prompt_performance.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class PromptOptimizer:
    """
    Optimizes prompts dynamically based on performance.
    """
    
    def __init__(self):
        self.performance = self._load_performance()
    
    def _load_performance(self) -> Dict:
        try:
            if PROMPT_PERF_FILE.exists():
                with open(PROMPT_PERF_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "prompts": {},
            "model_performance": {},
            "optimization_history": []
        }
    
    def _save_performance(self):
        self.performance["last_updated"] = datetime.now().isoformat()
        with open(PROMPT_PERF_FILE, 'w') as f:
            json.dump(self.performance, f, indent=2)
    
    def get_dynamic_context(self) -> Dict:
        """Get current dynamic context for prompt injection."""
        now = datetime.now()
        
        # Season
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        return {
            "current_date": now.strftime("%B %d, %Y"),
            "current_year": now.year,
            "day_of_week": now.strftime("%A"),
            "season": season,
            "is_weekend": now.weekday() >= 5,
            "month": now.strftime("%B"),
            "hour": now.hour,
            "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"
        }
    
    def inject_context(self, prompt: str) -> str:
        """Inject dynamic context into prompt placeholders."""
        context = self.get_dynamic_context()
        
        # Replace common placeholders
        replacements = {
            "{date}": context["current_date"],
            "{year}": str(context["current_year"]),
            "{day}": context["day_of_week"],
            "{day_of_week}": context["day_of_week"],
            "{season}": context["season"],
            "{month}": context["month"],
            "{current_date}": context["current_date"],
            "{current_year}": str(context["current_year"]),
            "this year": str(context["current_year"]),
            "next year": str(context["current_year"] + 1),
        }
        
        result = prompt
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def optimize_for_model(self, prompt: str, model: str) -> str:
        """Optimize prompt for specific model characteristics."""
        model_lower = model.lower()
        
        # Model-specific optimizations
        if "llama" in model_lower:
            # Llama prefers explicit JSON formatting
            if "JSON" in prompt and "```json" not in prompt:
                prompt = prompt.replace("Return JSON:", "Return valid JSON (no markdown):")
        
        elif "gemini" in model_lower:
            # Gemini handles longer contexts well
            pass
        
        elif "mistral" in model_lower or "mixtral" in model_lower:
            # Mixtral prefers structured prompts
            pass
        
        return prompt
    
    def compress_prompt(self, prompt: str, target_reduction: float = 0.2) -> str:
        """
        Compress prompt to reduce token usage.
        
        Techniques:
        1. Remove redundant whitespace
        2. Shorten common phrases
        3. Remove unnecessary examples (keep essential)
        """
        import re
        
        # Remove excessive whitespace
        result = re.sub(r'\n{3,}', '\n\n', prompt)
        result = re.sub(r' {2,}', ' ', result)
        
        # Common phrase shortenings
        shortenings = [
            ("You are a", "You're a"),
            ("You are an", "You're an"),
            ("that is", "that's"),
            ("it is", "it's"),
            ("do not", "don't"),
            ("does not", "doesn't"),
            ("cannot", "can't"),
            ("will not", "won't"),
            ("For example:", "Example:"),
            ("For instance:", "Example:"),
        ]
        
        for long, short in shortenings:
            result = result.replace(long, short)
        
        return result
    
    def record_performance(self, prompt_name: str, model: str, 
                          success: bool, quality_score: float = None,
                          tokens_used: int = None):
        """Record prompt performance for optimization."""
        key = f"{prompt_name}:{model}"
        
        if key not in self.performance["prompts"]:
            self.performance["prompts"][key] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "total_quality": 0,
                "total_tokens": 0
            }
        
        perf = self.performance["prompts"][key]
        perf["attempts"] += 1
        
        if success:
            perf["successes"] += 1
            if quality_score:
                perf["total_quality"] += quality_score
        else:
            perf["failures"] += 1
        
        if tokens_used:
            perf["total_tokens"] += tokens_used
        
        # Calculate averages
        perf["success_rate"] = perf["successes"] / perf["attempts"]
        if perf["successes"] > 0:
            perf["avg_quality"] = perf["total_quality"] / perf["successes"]
            perf["avg_tokens"] = perf["total_tokens"] / perf["attempts"]
        
        perf["last_used"] = datetime.now().isoformat()
        
        self._save_performance()
    
    def get_best_model_for_prompt(self, prompt_name: str) -> Optional[str]:
        """Get best performing model for a prompt type."""
        best_model = None
        best_score = 0
        
        for key, perf in self.performance.get("prompts", {}).items():
            if key.startswith(f"{prompt_name}:"):
                model = key.split(":")[1]
                score = perf.get("success_rate", 0) * perf.get("avg_quality", 5)
                
                if score > best_score:
                    best_score = score
                    best_model = model
        
        return best_model
    
    def get_optimization_suggestions(self, prompt_name: str) -> List[str]:
        """Get suggestions to improve prompt performance."""
        suggestions = []
        
        # Analyze performance
        for key, perf in self.performance.get("prompts", {}).items():
            if not key.startswith(f"{prompt_name}:"):
                continue
            
            if perf.get("success_rate", 1) < 0.8:
                suggestions.append(f"Low success rate ({perf['success_rate']:.0%}) - consider simplifying output format")
            
            if perf.get("avg_tokens", 0) > 1500:
                suggestions.append(f"High token usage ({perf['avg_tokens']:.0f}) - consider compressing prompt")
            
            if perf.get("avg_quality", 10) < 6:
                suggestions.append(f"Low quality score ({perf['avg_quality']:.1f}) - add more specific examples")
        
        return suggestions


# Singleton
_optimizer = None

def get_prompt_optimizer() -> PromptOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = PromptOptimizer()
    return _optimizer


def optimize_prompt(prompt: str, model: str = None) -> str:
    """Convenience function to optimize a prompt."""
    opt = get_prompt_optimizer()
    result = opt.inject_context(prompt)
    if model:
        result = opt.optimize_for_model(result, model)
    return result


if __name__ == "__main__":
    safe_print("Testing Prompt Optimizer...")
    
    opt = get_prompt_optimizer()
    
    # Test context injection
    test_prompt = "Generate viral content for {date}. The year is {year}."
    result = opt.inject_context(test_prompt)
    safe_print(f"Injected: {result}")
    
    # Test compression
    long_prompt = "You are a    content creator.   You are an expert.\n\n\n\nFor example: this is an example."
    compressed = opt.compress_prompt(long_prompt)
    safe_print(f"Compressed: {compressed}")