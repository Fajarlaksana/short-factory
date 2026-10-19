#!/usr/bin/env python3
"""
ViralShorts Factory - Smart Orchestrator v15.0
=================================================

This module orchestrates all v15.0 intelligent systems:
1. Token Budget Manager - Smart provider selection
2. Self-Learning Engine - Pattern learning
3. Quota Monitor - Real-time quota tracking
4. First-Attempt Maximizer - Quality boost

It provides a single interface for the video generator to use all these systems.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# State directory
STATE_DIR = Path("data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

ORCHESTRATOR_FILE = STATE_DIR / "smart_orchestrator.json"


class SmartOrchestrator:
    """
    Orchestrates all v15.0 intelligent systems.
    
    Provides:
    - Unified quota/budget management
    - Combined learning insights
    - Smart scheduling
    - Performance tracking
    """
    
    def __init__(self):
        # Initialize all systems
        self.budget_manager = None
        self.first_attempt = None
        self.learning_engine = None
        self.quota_monitor = None
        
        self._init_systems()
        self.session_data = self._load()
    
    def _init_systems(self):
        """Initialize all v15.0 systems."""
        try:
            from token_budget_manager import get_budget_manager, get_first_attempt_maximizer
            self.budget_manager = get_budget_manager()
            self.first_attempt = get_first_attempt_maximizer()
            print("[Orchestrator] Token Budget Manager initialized")
        except Exception as e:
            print(f"[Orchestrator] Token Budget Manager failed: {e}")
        
        try:
            from self_learning_engine import get_learning_engine
            self.learning_engine = get_learning_engine()
            print("[Orchestrator] Self-Learning Engine initialized")
        except Exception as e:
            print(f"[Orchestrator] Self-Learning Engine failed: {e}")
        
        try:
            from quota_monitor import get_quota_monitor
            self.quota_monitor = get_quota_monitor()
            print("[Orchestrator] Quota Monitor initialized")
        except Exception as e:
            print(f"[Orchestrator] Quota Monitor failed: {e}")
    
    def _load(self) -> Dict:
        """Load session data from disk."""
        try:
            if ORCHESTRATOR_FILE.exists():
                with open(ORCHESTRATOR_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "session_start": datetime.now(timezone.utc).isoformat(),
            "videos_generated": 0,
            "total_tokens_used": 0,
            "avg_quality_score": 0.0,
            "regeneration_count": 0,
            "provider_usage": {"groq": 0, "gemini": 0, "openrouter": 0}
        }
    
    def _save(self):
        """Save session data to disk."""
        try:
            with open(ORCHESTRATOR_FILE, 'w') as f:
                json.dump(self.session_data, f, indent=2)
        except:
            pass
    
    def can_generate_video(self) -> Tuple[bool, str]:
        """
        Check if we can generate a video right now.
        
        Returns:
            (can_generate, reason)
        """
        if self.quota_monitor:
            rec = self.quota_monitor.get_scheduling_recommendation()
            if rec["can_run_now"]:
                return True, f"Provider {rec['best_provider']} available"
            else:
                return False, rec["reason"]
        
        if self.budget_manager:
            videos = self.budget_manager.estimate_videos_remaining()
            if videos > 0:
                return True, f"{videos} videos possible"
            else:
                return False, "Token budget exhausted"
        
        return True, "No quota monitoring available"
    
    def get_best_provider(self, task: str) -> str:
        """
        Get the best provider for a task.
        
        Args:
            task: Task type (concept, content, evaluate, broll, metadata)
        
        Returns:
            Provider name
        """
        if self.budget_manager:
            return self.budget_manager.choose_provider(task)
        
        if self.quota_monitor:
            provider = self.quota_monitor.get_best_provider()
            if provider:
                return provider
        
        return "gemini"  # Default fallback
    
    def get_prompt_enhancements(self) -> str:
        """
        Get combined prompt enhancements from all learning systems.
        
        Returns:
            Combined prompt boost string
        """
        boosts = []
        
        if self.first_attempt:
            boost = self.first_attempt.get_quality_boost_prompt()
            if boost:
                boosts.append(boost)
        
        if self.learning_engine:
            boost = self.learning_engine.get_prompt_boost()
            if boost:
                boosts.append(boost)
        
        if not boosts:
            return ""
        
        return "\n".join(boosts)
    
    def record_video_result(self, 
                             score: int,
                             category: str,
                             topic: str,
                             hook: str,
                             phrases: List[str],
                             was_regeneration: bool,
                             tokens_used: int,
                             provider: str):
        """
        Record a video generation result to all learning systems.
        """
        # Update session data
        self.session_data["videos_generated"] += 1
        self.session_data["total_tokens_used"] += tokens_used
        if was_regeneration:
            self.session_data["regeneration_count"] += 1
        
        # Update average score
        count = self.session_data["videos_generated"]
        old_avg = self.session_data["avg_quality_score"]
        self.session_data["avg_quality_score"] = (old_avg * (count - 1) + score) / count
        
        # Track provider usage
        if provider in self.session_data["provider_usage"]:
            self.session_data["provider_usage"][provider] += 1
        
        self._save()
        
        # Record to first-attempt maximizer
        if self.first_attempt:
            self.first_attempt.record_result(
                score=score,
                category=category,
                hook=hook,
                was_regeneration=was_regeneration
            )
        
        # Record to learning engine
        if self.learning_engine:
            self.learning_engine.learn_from_video(
                score=score,
                category=category,
                topic=topic,
                hook=hook,
                phrases=phrases,
                was_regeneration=was_regeneration
            )
        
        # Record token usage
        if self.budget_manager:
            self.budget_manager.record_usage(provider, tokens_used)
        
        if self.quota_monitor:
            self.quota_monitor.record_usage(provider, tokens_used)
        
        print(f"[Orchestrator] Recorded video result: score={score}, tokens={tokens_used}")
    
    def record_api_error(self, provider: str, error_type: str, retry_seconds: int = 60):
        """Record an API error (e.g., 429)."""
        if self.budget_manager and error_type == "429":
            self.budget_manager.record_429(provider, retry_seconds)
        
        if self.quota_monitor and error_type == "429":
            self.quota_monitor.record_429(provider, retry_seconds)
    
    def get_session_summary(self) -> str:
        """Get a summary of the current session."""
        lines = [
            "=" * 60,
            "SMART ORCHESTRATOR - SESSION SUMMARY",
            "=" * 60,
            f"  Videos Generated: {self.session_data['videos_generated']}",
            f"  Tokens Used: {self.session_data['total_tokens_used']:,}",
            f"  Avg Quality Score: {self.session_data['avg_quality_score']:.1f}/10",
            f"  Regeneration Count: {self.session_data['regeneration_count']}",
            "",
            "  Provider Usage:",
        ]
        
        for provider, count in self.session_data["provider_usage"].items():
            lines.append(f"    {provider}: {count}")
        
        lines.append("=" * 60)
        
        # Add quota status if available
        if self.quota_monitor:
            lines.append(self.quota_monitor.get_status_summary())
        
        return "\n".join(lines)
    
    def get_recommendations(self) -> Dict:
        """Get recommendations for next video generation."""
        rec = {
            "can_generate": True,
            "reason": "",
            "best_provider": "gemini",
            "videos_possible": 0,
            "avoid_categories": [],
            "recommended_categories": [],
        }
        
        can_gen, reason = self.can_generate_video()
        rec["can_generate"] = can_gen
        rec["reason"] = reason
        rec["best_provider"] = self.get_best_provider("concept")
        
        if self.budget_manager:
            rec["videos_possible"] = self.budget_manager.estimate_videos_remaining()
        
        if self.learning_engine:
            rec["avoid_categories"] = self.learning_engine.data["stats"].get("worst_categories", [])
            rec["recommended_categories"] = self.learning_engine.get_recommended_categories()
        
        return rec


# Singleton
_orchestrator = None

def get_orchestrator() -> SmartOrchestrator:
    """Get the singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SmartOrchestrator()
    return _orchestrator


if __name__ == "__main__":
    # Test the orchestrator
    orch = get_orchestrator()
    
    print(orch.get_session_summary())
    
    print("\nRecommendations:")
    rec = orch.get_recommendations()
    for key, value in rec.items():
        print(f"  {key}: {value}")
    
    print("\nPrompt Enhancements:")
    print(orch.get_prompt_enhancements()[:500] + "..." if len(orch.get_prompt_enhancements()) > 500 else orch.get_prompt_enhancements())

