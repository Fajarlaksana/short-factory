#!/usr/bin/env python3
"""
ViralShorts Factory - AI Model Intelligence v17.8
===================================================

Intelligent model selection based on task type.

Different models are better at different tasks:
- Gemini: Great at long-form content, analysis
- Groq (Llama 3.3): Fast, good at structured output
- OpenRouter: Access to GPT, Claude when needed
- HuggingFace: Good for specific fine-tuned tasks

This module learns which models perform best for each task type
and routes requests accordingly.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import re


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_INTELLIGENCE_FILE = STATE_DIR / "model_intelligence.json"


# Task types and their characteristics
TASK_TYPES = {
    "concept_generation": {
        "description": "Generate video concepts and topics",
        "needs": ["creativity", "trend_awareness"],
        "default_provider": "gemini",  # More creative
        "tokens_typical": 300
    },
    "content_writing": {
        "description": "Write video scripts and phrases",
        "needs": ["creativity", "conciseness", "viral_knowledge"],
        "default_provider": "gemini",  # Best at writing
        "tokens_typical": 500
    },
    "quality_evaluation": {
        "description": "Evaluate content quality and score",
        "needs": ["analysis", "structured_output"],
        "default_provider": "groq",  # Fast, good at structured
        "tokens_typical": 400
    },
    "metadata_generation": {
        "description": "Generate titles, descriptions, tags",
        "needs": ["seo_knowledge", "conciseness"],
        "default_provider": "groq",  # Fast, structured
        "tokens_typical": 200
    },
    "pattern_generation": {
        "description": "Generate viral patterns and templates",
        "needs": ["creativity", "viral_knowledge", "structured_output"],
        "default_provider": "gemini",  # Better creativity
        "tokens_typical": 1500
    },
    "trend_analysis": {
        "description": "Analyze trends and predict virality",
        "needs": ["analysis", "current_events"],
        "default_provider": "gemini",  # Better world knowledge
        "tokens_typical": 500
    },
    "competitor_analysis": {
        "description": "Analyze competitor content",
        "needs": ["analysis", "strategy"],
        "default_provider": "gemini",  # Better at analysis
        "tokens_typical": 400
    },
    "thumbnail_concept": {
        "description": "Generate thumbnail text concepts",
        "needs": ["creativity", "conciseness"],
        "default_provider": "groq",  # Fast enough
        "tokens_typical": 150
    }
}


class ModelIntelligence:
    """
    Learns and tracks which models perform best for each task type.
    """
    
    def __init__(self):
        self.data = self._load()
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    def _load(self) -> Dict:
        try:
            if MODEL_INTELLIGENCE_FILE.exists():
                with open(MODEL_INTELLIGENCE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "performance": {},  # task_type -> {provider -> {calls, avg_latency, success_rate}}
            "preferences": {},  # Override defaults based on learning
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(MODEL_INTELLIGENCE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_best_provider_for_task(self, task_type: str) -> str:
        """
        Get the best provider for a specific task type.
        
        Priority:
        1. Learned preference (if enough data)
        2. Task-specific default
        3. Available provider fallback
        """
        # Check learned preferences
        if task_type in self.data.get("preferences", {}):
            pref = self.data["preferences"][task_type]
            if self._is_provider_available(pref):
                return pref
        
        # Check task-specific default
        task_info = TASK_TYPES.get(task_type, {})
        default = task_info.get("default_provider", "gemini")
        
        if self._is_provider_available(default):
            return default
        
        # Fallback to any available
        return self._get_first_available_provider()
    
    def _is_provider_available(self, provider: str) -> bool:
        """Check if a provider has API key."""
        if provider == "gemini":
            return bool(self.gemini_key)
        elif provider == "groq":
            return bool(self.groq_key)
        elif provider == "openrouter":
            return bool(self.openrouter_key)
        return False
    
    def _get_first_available_provider(self) -> str:
        """Get first available provider."""
        if self.gemini_key:
            return "gemini"
        elif self.groq_key:
            return "groq"
        elif self.openrouter_key:
            return "openrouter"
        return "gemini"  # Default even if no key
    
    def record_performance(self, task_type: str, provider: str, 
                          latency_ms: float, success: bool):
        """Record a task performance metric."""
        if "performance" not in self.data:
            self.data["performance"] = {}
        
        if task_type not in self.data["performance"]:
            self.data["performance"][task_type] = {}
        
        if provider not in self.data["performance"][task_type]:
            self.data["performance"][task_type][provider] = {
                "calls": 0,
                "total_latency_ms": 0,
                "successes": 0
            }
        
        stats = self.data["performance"][task_type][provider]
        stats["calls"] += 1
        stats["total_latency_ms"] += latency_ms
        if success:
            stats["successes"] += 1
        
        # Update preference if we have enough data
        self._maybe_update_preference(task_type)
        
        self._save()
    
    def _maybe_update_preference(self, task_type: str):
        """Update preference based on performance data."""
        if task_type not in self.data["performance"]:
            return
        
        task_stats = self.data["performance"][task_type]
        
        best_provider = None
        best_score = 0
        
        for provider, stats in task_stats.items():
            if stats["calls"] < 5:  # Need at least 5 calls to judge
                continue
            
            success_rate = stats["successes"] / stats["calls"]
            avg_latency = stats["total_latency_ms"] / stats["calls"]
            
            # Score = success_rate * 100 - (latency_penalty)
            # Lower latency is better, normalize to ~0-20 penalty
            latency_penalty = min(avg_latency / 100, 20)
            score = success_rate * 100 - latency_penalty
            
            if score > best_score:
                best_score = score
                best_provider = provider
        
        if best_provider:
            if "preferences" not in self.data:
                self.data["preferences"] = {}
            self.data["preferences"][task_type] = best_provider
    
    def get_task_info(self, task_type: str) -> Dict:
        """Get information about a task type."""
        info = TASK_TYPES.get(task_type, {})
        info["recommended_provider"] = self.get_best_provider_for_task(task_type)
        
        # Add performance stats if available
        if task_type in self.data.get("performance", {}):
            info["performance"] = self.data["performance"][task_type]
        
        return info


# Singleton
_model_intelligence = None


def get_model_intelligence() -> ModelIntelligence:
    """Get the singleton model intelligence instance."""
    global _model_intelligence
    if _model_intelligence is None:
        _model_intelligence = ModelIntelligence()
    return _model_intelligence


def get_provider_for_task(task_type: str) -> str:
    """Convenience function to get best provider for a task."""
    return get_model_intelligence().get_best_provider_for_task(task_type)


def record_task_performance(task_type: str, provider: str, 
                           latency_ms: float, success: bool):
    """Convenience function to record task performance."""
    get_model_intelligence().record_performance(task_type, provider, latency_ms, success)


if __name__ == "__main__":
    # Test
    safe_print("Testing Model Intelligence...")
    
    mi = get_model_intelligence()
    
    for task in TASK_TYPES.keys():
        provider = mi.get_best_provider_for_task(task)
        safe_print(f"  {task}: {provider}")
    
    # Simulate some performance data
    mi.record_performance("quality_evaluation", "groq", 150, True)
    mi.record_performance("quality_evaluation", "groq", 120, True)
    mi.record_performance("quality_evaluation", "gemini", 450, True)
    
    safe_print("\nAfter recording:")
    for task in ["quality_evaluation", "content_writing"]:
        info = mi.get_task_info(task)
        safe_print(f"  {task}: {info.get('recommended_provider')}")
    
    safe_print("\nTest complete!")

