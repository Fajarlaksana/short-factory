#!/usr/bin/env python3
"""
ViralShorts Factory - Prompts Registry v17.9.9
===============================================

CENTRAL REGISTRY of all prompts used in the system.

Purpose:
1. Single source of truth for all prompts
2. Used by SmartModelRouter to optimize model selection
3. Updated when prompts are added/modified
4. Enables prompt-level analytics and optimization

Usage:
    from src.ai.prompts_registry import get_prompts_registry, PromptInfo
    
    registry = get_prompts_registry()
    all_prompts = registry.get_all_prompts()
    creative_prompts = registry.get_prompts_by_type("creative")

Auto-update:
    The registry can scan source files to discover new prompts.
    Run: registry.scan_and_update()
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# State directory
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = STATE_DIR / "prompts_registry.json"


@dataclass
class PromptInfo:
    """Information about a prompt."""
    name: str  # Unique identifier (e.g., "VIRAL_TOPIC_PROMPT")
    type: str  # "creative", "evaluation", "simple", "analysis"
    source_file: str  # File where prompt is defined
    description: str  # What this prompt does
    complexity: str  # "simple", "medium", "complex"
    avg_tokens: int  # Typical token usage
    best_model: Optional[str]  # Best model for this prompt (learned)
    success_rate: float  # Historical success rate
    avg_quality: float  # Average quality score when used
    last_used: Optional[str]  # ISO timestamp
    times_used: int  # Usage count


# =============================================================================
# DEFAULT PROMPTS REGISTRY
# =============================================================================

DEFAULT_PROMPTS = [
    # === CREATIVE PROMPTS (Need human-like creativity) ===
    PromptInfo(
        name="VIRAL_TOPIC_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Generates viral video topic ideas with hooks and content",
        complexity="complex",
        avg_tokens=2000,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.95,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="MASTER_GENERATION_PROMPT",
        type="creative",
        source_file="src/ai/master_content_generator.py",
        description="Generates 10/10 quality video content with hardcoded checks",
        complexity="complex",
        avg_tokens=1500,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.92,
        avg_quality=9.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="VOICEOVER_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Creates natural-sounding voiceover scripts",
        complexity="medium",
        avg_tokens=600,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.95,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="ENGAGEMENT_REPLY_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Generates human-like comment reply templates",
        complexity="medium",
        avg_tokens=600,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.90,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="SERIES_CONTINUATION_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Plans sequel content for successful videos",
        complexity="medium",
        avg_tokens=700,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.88,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CONTENT_RECYCLING_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Resurrects failed content with new angles",
        complexity="medium",
        avg_tokens=700,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.85,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    
    # === EVALUATION PROMPTS (Need structured output) ===
    PromptInfo(
        name="MASTER_EVALUATION_PROMPT",
        type="evaluation",
        source_file="src/ai/master_evaluator.py",
        description="Comprehensive quality scoring with 7 dimensions",
        complexity="complex",
        avg_tokens=1500,
        best_model="gemini:gemini-2.0-flash",
        success_rate=0.95,
        avg_quality=9.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CONTENT_EVALUATION_PROMPT",
        type="evaluation",
        source_file="src/ai/master_prompts.py",
        description="Evaluates content for viral potential",
        complexity="medium",
        avg_tokens=800,
        best_model="gemini:gemini-2.0-flash",
        success_rate=0.93,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="VIRAL_VELOCITY_PROMPT",
        type="evaluation",
        source_file="src/ai/master_prompts.py",
        description="Predicts video viral velocity and view counts",
        complexity="medium",
        avg_tokens=800,
        best_model="gemini:gemini-2.0-flash",
        success_rate=0.88,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="COMMENT_SENTIMENT_PROMPT",
        type="evaluation",
        source_file="src/ai/master_prompts.py",
        description="Analyzes comment sentiment and extracts insights",
        complexity="simple",
        avg_tokens=400,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.95,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    
    # === SIMPLE PROMPTS (Speed matters most) ===
    PromptInfo(
        name="BROLL_KEYWORDS_PROMPT",
        type="simple",
        source_file="src/ai/master_prompts.py",
        description="Extracts B-roll search keywords from content",
        complexity="simple",
        avg_tokens=500,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.98,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="DESCRIPTION_SEO_PROMPT",
        type="simple",
        source_file="src/ai/master_prompts.py",
        description="Generates SEO-optimized video descriptions",
        complexity="simple",
        avg_tokens=400,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.97,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="THUMBNAIL_TEXT_PROMPT",
        type="simple",
        source_file="src/ai/master_prompts.py",
        description="Creates thumbnail text overlays",
        complexity="simple",
        avg_tokens=400,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.96,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="HASHTAG_GENERATION",
        type="simple",
        source_file="src/ai/ai_hashtag_generator.py",
        description="Generates relevant hashtags for videos",
        complexity="simple",
        avg_tokens=200,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.99,
        avg_quality=7.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="PLATFORM_OPTIMIZATION_PROMPT",
        type="simple",
        source_file="src/ai/master_prompts.py",
        description="Optimizes content for specific platform",
        complexity="simple",
        avg_tokens=600,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.94,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    
    # === ANALYSIS PROMPTS (Need deep reasoning) ===
    PromptInfo(
        name="ANALYTICS_DEEP_DIVE_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Deep analysis of video performance data",
        complexity="complex",
        avg_tokens=1200,
        best_model="gemini:gemini-2.5-pro",
        success_rate=0.85,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CHANNEL_GROWTH_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Strategic channel growth planning",
        complexity="complex",
        avg_tokens=1500,
        best_model="gemini:gemini-2.5-pro",
        success_rate=0.82,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="COMPETITOR_GAP_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Finds content gaps from competitor analysis",
        complexity="complex",
        avg_tokens=1200,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.80,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="SEASONAL_CALENDAR_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Identifies seasonal content opportunities",
        complexity="medium",
        avg_tokens=800,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.90,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CATEGORY_DECAY_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Tracks category performance over time",
        complexity="medium",
        avg_tokens=600,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.88,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="HOOK_WORD_ANALYSIS_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Analyzes hook word performance patterns",
        complexity="medium",
        avg_tokens=500,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.92,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    
    # === ADDITIONAL PROMPTS (v17.9.40 - Complete Registry) ===
    PromptInfo(
        name="BROLL_RELEVANCE_PROMPT",
        type="evaluation",
        source_file="src/ai/master_prompts.py",
        description="Scores B-roll relevance to video content",
        complexity="simple",
        avg_tokens=400,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.93,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="EMOTIONAL_ARC_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Designs emotional journey for video",
        complexity="complex",
        avg_tokens=800,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.88,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CONTEXTUAL_AWARENESS_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Checks cultural sensitivity and timing",
        complexity="medium",
        avg_tokens=600,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.90,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CROSS_PROMOTION_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Generates cross-platform content strategy",
        complexity="medium",
        avg_tokens=700,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.85,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CLICKBAIT_OPTIMIZATION_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Optimizes titles for maximum click-through",
        complexity="medium",
        avg_tokens=600,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.92,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="FIRST_SECONDS_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Optimizes first 3 seconds for retention",
        complexity="complex",
        avg_tokens=800,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.90,
        avg_quality=9.0,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="ALGORITHM_OPTIMIZATION_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Optimizes for YouTube algorithm signals",
        complexity="complex",
        avg_tokens=900,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.85,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="VISUAL_OPTIMIZATION_PROMPT",
        type="creative",
        source_file="src/ai/master_prompts.py",
        description="Optimizes visual design for short-form",
        complexity="medium",
        avg_tokens=700,
        best_model="gemini:gemini-2.5-flash",
        success_rate=0.88,
        avg_quality=7.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="CONTENT_QUALITY_PROMPT",
        type="evaluation",
        source_file="src/ai/master_prompts.py",
        description="Ensures content value and believability",
        complexity="complex",
        avg_tokens=900,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.90,
        avg_quality=8.5,
        last_used=None,
        times_used=0
    ),
    PromptInfo(
        name="VIRAL_TREND_PROMPT",
        type="analysis",
        source_file="src/ai/master_prompts.py",
        description="Analyzes viral trends for content opportunities",
        complexity="complex",
        avg_tokens=900,
        best_model="groq:llama-3.3-70b-versatile",
        success_rate=0.87,
        avg_quality=8.0,
        last_used=None,
        times_used=0
    ),
]


class PromptsRegistry:
    """
    Central registry of all prompts in the system.
    
    Features:
    - Stores prompt metadata and performance stats
    - Updates best_model based on actual performance
    - Scans source files to discover new prompts
    - Provides data to SmartModelRouter
    """
    
    def __init__(self):
        self.prompts: Dict[str, PromptInfo] = {}
        self._load()
    
    def _load(self):
        """Load registry from file or use defaults."""
        try:
            if REGISTRY_FILE.exists():
                with open(REGISTRY_FILE, 'r') as f:
                    data = json.load(f)
                    for prompt_data in data.get("prompts", []):
                        prompt = PromptInfo(**prompt_data)
                        self.prompts[prompt.name] = prompt
                print(f"[REGISTRY] Loaded {len(self.prompts)} prompts from cache")
            else:
                self._use_defaults()
        except Exception as e:
            print(f"[REGISTRY] Load failed: {e}, using defaults")
            self._use_defaults()
    
    def _use_defaults(self):
        """Use default prompts."""
        for prompt in DEFAULT_PROMPTS:
            self.prompts[prompt.name] = prompt
        self._save()
        print(f"[REGISTRY] Initialized with {len(self.prompts)} default prompts")
    
    def _save(self):
        """Save registry to file."""
        try:
            data = {
                "version": "17.9.9",
                "updated_at": datetime.now().isoformat(),
                "prompts": [asdict(p) for p in self.prompts.values()]
            }
            with open(REGISTRY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[REGISTRY] Save failed: {e}")
    
    def get_all_prompts(self) -> List[PromptInfo]:
        """Get all registered prompts."""
        return list(self.prompts.values())
    
    def get_prompt(self, name: str) -> Optional[PromptInfo]:
        """Get a specific prompt by name."""
        return self.prompts.get(name)
    
    def get_prompts_by_type(self, prompt_type: str) -> List[PromptInfo]:
        """Get all prompts of a specific type."""
        return [p for p in self.prompts.values() if p.type == prompt_type]
    
    def record_usage(self, prompt_name: str, model_used: str, 
                     success: bool, quality_score: float = None):
        """
        Record prompt usage for learning.
        
        Args:
            prompt_name: Name of the prompt used
            model_used: Model that was used (e.g., "groq:llama-3.3-70b")
            success: Whether the call succeeded
            quality_score: Quality of the result (1-10)
        """
        prompt = self.prompts.get(prompt_name)
        if not prompt:
            return
        
        # Update stats
        prompt.times_used += 1
        prompt.last_used = datetime.now().isoformat()
        
        if success:
            # Update success rate (moving average)
            old_rate = prompt.success_rate
            prompt.success_rate = 0.9 * old_rate + 0.1 * 1.0
            
            # Update quality (moving average)
            if quality_score:
                old_quality = prompt.avg_quality
                prompt.avg_quality = 0.9 * old_quality + 0.1 * quality_score
                
                # If this model gave better quality, consider it for best_model
                if quality_score > old_quality + 0.5:
                    prompt.best_model = model_used
        else:
            prompt.success_rate = 0.9 * prompt.success_rate + 0.1 * 0.0
        
        # Save periodically
        if prompt.times_used % 10 == 0:
            self._save()
    
    def get_best_model_for_prompt(self, prompt_name: str) -> Optional[str]:
        """Get the best model for a specific prompt."""
        prompt = self.prompts.get(prompt_name)
        if prompt:
            return prompt.best_model
        return None
    
    def get_model_recommendations(self) -> Dict[str, str]:
        """Get model recommendations for all prompts."""
        return {
            p.name: p.best_model 
            for p in self.prompts.values() 
            if p.best_model
        }
    
    def scan_and_update(self):
        """
        Scan source files to discover new prompts.
        
        Looks for patterns like:
        - *_PROMPT = \"\"\"...
        - def generate_*(
        """
        print("[REGISTRY] Scanning for new prompts...")
        
        # Directories to scan
        scan_dirs = [
            "src/ai",
            "src/enhancements"
        ]
        
        prompt_pattern = re.compile(r'([A-Z_]+_PROMPT)\s*=\s*["\']', re.MULTILINE)
        
        discovered = 0
        for scan_dir in scan_dirs:
            dir_path = Path(scan_dir)
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.glob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    matches = prompt_pattern.findall(content)
                    
                    for match in matches:
                        if match not in self.prompts:
                            # New prompt discovered!
                            self.prompts[match] = PromptInfo(
                                name=match,
                                type="simple",  # Default, will be refined
                                source_file=str(py_file),
                                description="Auto-discovered prompt",
                                complexity="medium",
                                avg_tokens=500,
                                best_model=None,
                                success_rate=0.5,
                                avg_quality=5.0,
                                last_used=None,
                                times_used=0
                            )
                            discovered += 1
                except Exception as e:
                    pass
        
        if discovered > 0:
            self._save()
            print(f"[REGISTRY] Discovered {discovered} new prompts")
        else:
            print("[REGISTRY] No new prompts found")
    
    def get_summary(self) -> Dict:
        """Get registry summary."""
        by_type = {}
        for prompt in self.prompts.values():
            by_type[prompt.type] = by_type.get(prompt.type, 0) + 1
        
        return {
            "total_prompts": len(self.prompts),
            "by_type": by_type,
            "avg_success_rate": sum(p.success_rate for p in self.prompts.values()) / max(1, len(self.prompts)),
            "avg_quality": sum(p.avg_quality for p in self.prompts.values()) / max(1, len(self.prompts)),
            "most_used": max(self.prompts.values(), key=lambda p: p.times_used).name if self.prompts else None
        }


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

_registry = None


def get_prompts_registry() -> PromptsRegistry:
    """Get the global PromptsRegistry instance."""
    global _registry
    if _registry is None:
        _registry = PromptsRegistry()
    return _registry


def get_best_model_for_prompt(prompt_name: str) -> Optional[str]:
    """Convenience function."""
    return get_prompts_registry().get_best_model_for_prompt(prompt_name)


def record_prompt_usage(prompt_name: str, model_used: str, 
                        success: bool, quality: float = None):
    """Convenience function."""
    get_prompts_registry().record_usage(prompt_name, model_used, success, quality)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PROMPTS REGISTRY TEST")
    print("=" * 60)
    
    registry = get_prompts_registry()
    
    # Print summary
    summary = registry.get_summary()
    print(f"\nTotal prompts: {summary['total_prompts']}")
    print(f"By type: {summary['by_type']}")
    print(f"Avg success rate: {summary['avg_success_rate']:.0%}")
    print(f"Avg quality: {summary['avg_quality']:.1f}/10")
    
    # Print all prompts
    print("\n" + "-" * 60)
    print("ALL REGISTERED PROMPTS:")
    print("-" * 60)
    
    for prompt_type in ["creative", "evaluation", "simple", "analysis"]:
        prompts = registry.get_prompts_by_type(prompt_type)
        print(f"\n{prompt_type.upper()} ({len(prompts)}):")
        for p in prompts:
            print(f"  - {p.name}")
            print(f"    Best model: {p.best_model}")
            print(f"    Quality: {p.avg_quality}/10")
    
    # Test model recommendations
    print("\n" + "-" * 60)
    print("MODEL RECOMMENDATIONS:")
    print("-" * 60)
    
    recommendations = registry.get_model_recommendations()
    for prompt, model in list(recommendations.items())[:10]:
        print(f"  {prompt} -> {model}")
    
    print("\n" + "=" * 60)

