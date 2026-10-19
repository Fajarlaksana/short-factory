#!/usr/bin/env python3
"""
Enhanced Integration Module v1.0
================================

Integrates all enhanced modules:
- Dynamic sound effects
- Enhanced topic selection
- Enhanced B-roll
- Enhanced music
- Robustness layer
- Quota optimization
- Prompt optimization

This module provides a unified interface to all enhancements.
"""

import os
from typing import Dict, Optional, List


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class EnhancedVideoFactory:
    """
    Unified interface to all enhanced modules.
    """
    
    def __init__(self):
        self._sfx_selector = None
        self._topic_selector = None
        self._broll_selector = None
        self._music_selector = None
        self._quota_manager = None
        self._prompt_optimizer = None
        self._robustness = None
    
    @property
    def sfx_selector(self):
        if self._sfx_selector is None:
            try:
                from src.utils.dynamic_sound_effects import DynamicSoundEffectSelector
                self._sfx_selector = DynamicSoundEffectSelector()
            except ImportError:
                safe_print("[!] Dynamic SFX not available")
        return self._sfx_selector
    
    @property
    def topic_selector(self):
        if self._topic_selector is None:
            try:
                from src.ai.enhanced_topic_selector import EnhancedTopicSelector
                self._topic_selector = EnhancedTopicSelector()
            except ImportError:
                safe_print("[!] Enhanced topic selector not available")
        return self._topic_selector
    
    @property
    def broll_selector(self):
        if self._broll_selector is None:
            try:
                from src.ai.enhanced_broll_selector import EnhancedBRollSelector
                self._broll_selector = EnhancedBRollSelector()
            except ImportError:
                safe_print("[!] Enhanced B-roll selector not available")
        return self._broll_selector
    
    @property
    def music_selector(self):
        if self._music_selector is None:
            try:
                from src.ai.enhanced_music_selector import EnhancedMusicSelector
                self._music_selector = EnhancedMusicSelector()
            except ImportError:
                safe_print("[!] Enhanced music selector not available")
        return self._music_selector
    
    @property
    def quota_manager(self):
        if self._quota_manager is None:
            try:
                from src.quota.enhanced_quota_manager import EnhancedQuotaManager
                self._quota_manager = EnhancedQuotaManager()
            except ImportError:
                safe_print("[!] Enhanced quota manager not available")
        return self._quota_manager
    
    @property
    def prompt_optimizer(self):
        if self._prompt_optimizer is None:
            try:
                from src.ai.prompt_optimizer import PromptOptimizer
                self._prompt_optimizer = PromptOptimizer()
            except ImportError:
                safe_print("[!] Prompt optimizer not available")
        return self._prompt_optimizer
    
    def get_topics(self, count: int = 5, category: str = None) -> List[Dict]:
        """Get AI-generated viral topics."""
        if self.topic_selector:
            return self.topic_selector.generate_topics(count, category)
        return []
    
    def get_music(self, content: str, category: str, mood: str = "dramatic") -> Optional[str]:
        """Get AI-selected music for content."""
        if self.music_selector:
            return self.music_selector.get_music_for_content(content, category, mood)
        return None
    
    def get_broll(self, content: str, category: str, mood: str = "dramatic") -> Optional[str]:
        """Get AI-selected B-roll for content."""
        if self.broll_selector:
            return self.broll_selector.get_broll_for_content(content, category, mood)
        return None
    
    def get_sfx(self, content: str, category: str, moment: str) -> Optional[str]:
        """Get AI-selected sound effect."""
        if self.sfx_selector:
            return self.sfx_selector.get_sfx_for_moment(content, category, moment)
        return None
    
    def optimize_prompt(self, prompt: str, model: str = None) -> str:
        """Optimize a prompt with context injection."""
        if self.prompt_optimizer:
            result = self.prompt_optimizer.inject_context(prompt)
            if model:
                result = self.prompt_optimizer.optimize_for_model(result, model)
            return result
        return prompt
    
    def get_quota_status(self) -> Dict:
        """Get current quota utilization."""
        if self.quota_manager:
            return self.quota_manager.get_utilization_report()
        return {}
    
    def check_health(self) -> Dict:
        """Check system health status."""
        status = {
            "topics": self.topic_selector is not None,
            "music": self.music_selector is not None,
            "broll": self.broll_selector is not None,
            "sfx": self.sfx_selector is not None,
            "quota": self.quota_manager is not None,
            "prompts": self.prompt_optimizer is not None,
        }
        status["all_healthy"] = all(status.values())
        return status


# Singleton
_factory = None

def get_enhanced_factory() -> EnhancedVideoFactory:
    global _factory
    if _factory is None:
        _factory = EnhancedVideoFactory()
    return _factory


# Convenience functions
def get_viral_topics(count: int = 5, category: str = None) -> List[Dict]:
    return get_enhanced_factory().get_topics(count, category)

def get_ai_music(content: str, category: str, mood: str = "dramatic") -> Optional[str]:
    return get_enhanced_factory().get_music(content, category, mood)

def get_ai_broll(content: str, category: str, mood: str = "dramatic") -> Optional[str]:
    return get_enhanced_factory().get_broll(content, category, mood)

def get_ai_sfx(content: str, category: str, moment: str) -> Optional[str]:
    return get_enhanced_factory().get_sfx(content, category, moment)

def optimize_ai_prompt(prompt: str, model: str = None) -> str:
    return get_enhanced_factory().optimize_prompt(prompt, model)


if __name__ == "__main__":
    safe_print("Testing Enhanced Integration...")
    
    factory = get_enhanced_factory()
    
    # Check health
    health = factory.check_health()
    safe_print(f"System health: {health}")
    
    # Get quota status
    quota = factory.get_quota_status()
    safe_print(f"Quota status: {quota}")
    
    safe_print("Integration test complete!")