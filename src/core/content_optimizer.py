#!/usr/bin/env python3
"""
ViralShorts Factory - Integrated Content Optimizer v17.8
==========================================================

Brings all AI modules together for comprehensive content optimization.

Workflow:
1. Analyze input content
2. Run all optimizers
3. Calculate virality score
4. Return optimized content with recommendations
"""

import os
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


# Import all modules with fallbacks
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src/analytics')

try:
    from ai_hook_generator import get_hook_generator
    HOOK_GEN_AVAILABLE = True
except ImportError:
    HOOK_GEN_AVAILABLE = False

try:
    from ai_cta_generator import get_cta_generator
    CTA_GEN_AVAILABLE = True
except ImportError:
    CTA_GEN_AVAILABLE = False

try:
    from ai_title_optimizer import get_title_optimizer
    TITLE_OPT_AVAILABLE = True
except ImportError:
    TITLE_OPT_AVAILABLE = False

try:
    from ai_description_generator import get_description_generator
    DESC_GEN_AVAILABLE = True
except ImportError:
    DESC_GEN_AVAILABLE = False

try:
    from ai_hashtag_generator import get_hashtag_generator
    HASHTAG_GEN_AVAILABLE = True
except ImportError:
    HASHTAG_GEN_AVAILABLE = False

try:
    from ai_thumbnail_text import get_thumbnail_optimizer
    THUMB_OPT_AVAILABLE = True
except ImportError:
    THUMB_OPT_AVAILABLE = False

try:
    from retention_predictor import get_retention_predictor
    RETENTION_AVAILABLE = True
except ImportError:
    RETENTION_AVAILABLE = False

try:
    from engagement_predictor import get_engagement_predictor
    ENGAGE_AVAILABLE = True
except ImportError:
    ENGAGE_AVAILABLE = False

try:
    from virality_calculator import get_virality_calculator
    VIRAL_AVAILABLE = True
except ImportError:
    VIRAL_AVAILABLE = False

try:
    from script_analyzer import get_script_analyzer
    SCRIPT_AVAILABLE = True
except ImportError:
    SCRIPT_AVAILABLE = False


class ContentOptimizer:
    """
    Integrated content optimizer using all AI modules.
    """
    
    def __init__(self):
        self.modules_available = {
            "hook_generator": HOOK_GEN_AVAILABLE,
            "cta_generator": CTA_GEN_AVAILABLE,
            "title_optimizer": TITLE_OPT_AVAILABLE,
            "description_generator": DESC_GEN_AVAILABLE,
            "hashtag_generator": HASHTAG_GEN_AVAILABLE,
            "thumbnail_optimizer": THUMB_OPT_AVAILABLE,
            "retention_predictor": RETENTION_AVAILABLE,
            "engagement_predictor": ENGAGE_AVAILABLE,
            "virality_calculator": VIRAL_AVAILABLE,
            "script_analyzer": SCRIPT_AVAILABLE
        }
    
    def optimize(self, content: Dict) -> Dict:
        """
        Optimize content using all available modules.
        
        Args:
            content: Dict with hook, phrases, cta, topic, category
        
        Returns:
            Dict with original, optimized, predictions, and recommendations
        """
        hook = content.get("hook", "")
        phrases = content.get("phrases", [])
        cta = content.get("cta", "")
        topic = content.get("topic", "")
        category = content.get("category", "general")
        title = content.get("title", "")
        
        result = {
            "original": content.copy(),
            "optimized": content.copy(),
            "predictions": {},
            "recommendations": [],
            "modules_used": [],
            "improvements": []
        }
        
        # 1. Analyze original script
        if SCRIPT_AVAILABLE:
            analyzer = get_script_analyzer()
            original_analysis = analyzer.analyze_script(content)
            result["predictions"]["original_script_score"] = original_analysis["overall_score"]
            result["modules_used"].append("script_analyzer")
        
        # 2. Optimize hook if weak
        if HOOK_GEN_AVAILABLE and len(hook) < 10:
            gen = get_hook_generator()
            new_hook = gen.generate_hook(topic or category, category)
            if new_hook and len(new_hook) > len(hook):
                result["optimized"]["hook"] = new_hook
                result["improvements"].append(f"Hook improved: '{hook[:20]}...' -> '{new_hook[:30]}...'")
            result["modules_used"].append("hook_generator")
        
        # 3. Optimize CTA if weak
        if CTA_GEN_AVAILABLE:
            gen = get_cta_generator()
            cta_lower = cta.lower() if cta else ""
            if not cta or not any(w in cta_lower for w in ["comment", "like", "share"]):
                new_cta = gen.generate_cta(topic or category, category)
                if new_cta:
                    result["optimized"]["cta"] = new_cta
                    result["improvements"].append(f"CTA improved")
            result["modules_used"].append("cta_generator")
        
        # 4. Generate title if missing
        if TITLE_OPT_AVAILABLE and not title:
            opt = get_title_optimizer()
            new_title = opt.optimize_title(topic or category, category)
            if new_title:
                result["optimized"]["title"] = new_title
                result["improvements"].append(f"Title generated: '{new_title}'")
            result["modules_used"].append("title_optimizer")
        
        # 5. Generate description
        if DESC_GEN_AVAILABLE:
            gen = get_description_generator()
            desc = gen.generate_description(
                title=result["optimized"].get("title", topic),
                topic=topic,
                category=category,
                hook=result["optimized"]["hook"]
            )
            result["optimized"]["description"] = desc
            result["modules_used"].append("description_generator")
        
        # 6. Generate hashtags
        if HASHTAG_GEN_AVAILABLE:
            gen = get_hashtag_generator()
            hashtags = gen.generate_hashtags(topic or category, category)
            result["optimized"]["hashtags"] = hashtags
            result["modules_used"].append("hashtag_generator")
        
        # 7. Generate thumbnail text
        if THUMB_OPT_AVAILABLE:
            opt = get_thumbnail_optimizer()
            thumb = opt.generate_thumbnail_text(
                result["optimized"].get("title", topic),
                topic,
                category
            )
            result["optimized"]["thumbnail"] = thumb
            result["modules_used"].append("thumbnail_optimizer")
        
        # 8. Predict retention
        if RETENTION_AVAILABLE:
            pred = get_retention_predictor()
            retention = pred.predict_retention(result["optimized"])
            result["predictions"]["retention"] = retention
            result["modules_used"].append("retention_predictor")
            
            if retention.get("overall_retention", 0) < 60:
                result["recommendations"].extend(retention.get("recommendations", []))
        
        # 9. Predict engagement
        if ENGAGE_AVAILABLE:
            pred = get_engagement_predictor()
            engagement = pred.predict_engagement(result["optimized"])
            result["predictions"]["engagement"] = engagement
            result["modules_used"].append("engagement_predictor")
            
            if engagement.get("overall_engagement", 0) < 50:
                result["recommendations"].extend(engagement.get("recommendations", []))
        
        # 10. Calculate virality
        if VIRAL_AVAILABLE:
            calc = get_virality_calculator()
            virality = calc.calculate_virality(result["optimized"])
            result["predictions"]["virality"] = virality
            result["modules_used"].append("virality_calculator")
            
            result["recommendations"].extend(virality.get("recommendations", []))
        
        # Remove duplicate recommendations
        result["recommendations"] = list(dict.fromkeys(result["recommendations"]))
        
        # Summary
        result["summary"] = self._generate_summary(result)
        
        return result
    
    def _generate_summary(self, result: Dict) -> Dict:
        """Generate optimization summary."""
        virality = result["predictions"].get("virality", {})
        retention = result["predictions"].get("retention", {})
        engagement = result["predictions"].get("engagement", {})
        
        return {
            "modules_used": len(result["modules_used"]),
            "improvements_made": len(result["improvements"]),
            "virality_score": virality.get("overall_score", 0),
            "virality_grade": virality.get("grade", "?"),
            "retention_score": retention.get("overall_retention", 0),
            "engagement_score": engagement.get("overall_engagement", 0),
            "recommendation_count": len(result["recommendations"])
        }
    
    def quick_score(self, content: Dict) -> Dict:
        """
        Quick scoring without optimization.
        
        Returns just the scores without modifying content.
        """
        scores = {}
        
        if SCRIPT_AVAILABLE:
            analyzer = get_script_analyzer()
            analysis = analyzer.analyze_script(content)
            scores["script"] = analysis["overall_score"]
        
        if VIRAL_AVAILABLE:
            calc = get_virality_calculator()
            virality = calc.calculate_virality(content)
            scores["virality"] = virality["overall_score"]
            scores["grade"] = virality["grade"]
        
        if RETENTION_AVAILABLE:
            pred = get_retention_predictor()
            retention = pred.predict_retention(content)
            scores["retention"] = retention["overall_retention"]
        
        if ENGAGE_AVAILABLE:
            pred = get_engagement_predictor()
            engagement = pred.predict_engagement(content)
            scores["engagement"] = engagement["overall_engagement"]
        
        # Overall
        valid_scores = [v for v in scores.values() if isinstance(v, (int, float))]
        scores["overall"] = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        return scores
    
    def get_module_status(self) -> Dict:
        """Get status of all modules."""
        return self.modules_available


# Singleton
_content_optimizer = None


def get_content_optimizer() -> ContentOptimizer:
    """Get singleton optimizer."""
    global _content_optimizer
    if _content_optimizer is None:
        _content_optimizer = ContentOptimizer()
    return _content_optimizer


def optimize_content(content: Dict) -> Dict:
    """Convenience function."""
    return get_content_optimizer().optimize(content)


def quick_score(content: Dict) -> Dict:
    """Convenience function for quick scoring."""
    return get_content_optimizer().quick_score(content)


if __name__ == "__main__":
    # Test
    safe_print("Testing Integrated Content Optimizer...")
    safe_print("=" * 60)
    
    optimizer = get_content_optimizer()
    
    # Check module status
    status = optimizer.get_module_status()
    available = sum(1 for v in status.values() if v)
    safe_print(f"Modules available: {available}/{len(status)}")
    for name, avail in status.items():
        icon = "[OK]" if avail else "[--]"
        safe_print(f"  {icon} {name}")
    
    # Test content
    content = {
        "hook": "Here's something interesting",
        "phrases": [
            "First, you need to understand this.",
            "Second, apply these simple steps.",
            "Third, watch the results happen."
        ],
        "cta": "",  # Intentionally weak
        "topic": "productivity and success habits",
        "category": "productivity",
        "title": ""  # Missing
    }
    
    safe_print(f"\n{'='*60}")
    safe_print("OPTIMIZING CONTENT...")
    safe_print(f"{'='*60}")
    
    result = optimizer.optimize(content)
    
    # Display results
    safe_print(f"\nSUMMARY:")
    safe_print(f"  Modules Used: {result['summary']['modules_used']}")
    safe_print(f"  Improvements: {result['summary']['improvements_made']}")
    safe_print(f"  Virality: {result['summary']['virality_score']}/100 ({result['summary']['virality_grade']})")
    safe_print(f"  Retention: {result['summary']['retention_score']}%")
    safe_print(f"  Engagement: {result['summary']['engagement_score']}/100")
    
    safe_print(f"\nIMPROVEMENTS MADE:")
    for imp in result["improvements"]:
        safe_print(f"  - {imp}")
    
    safe_print(f"\nOPTIMIZED CONTENT:")
    safe_print(f"  Hook: {result['optimized'].get('hook', 'N/A')[:50]}...")
    safe_print(f"  Title: {result['optimized'].get('title', 'N/A')}")
    safe_print(f"  CTA: {result['optimized'].get('cta', 'N/A')}")
    safe_print(f"  Hashtags: {result['optimized'].get('hashtags', [])}")
    
    safe_print(f"\nRECOMMENDATIONS:")
    for rec in result["recommendations"][:5]:
        safe_print(f"  - {rec}")
    
    safe_print(f"\n{'='*60}")
    safe_print("Test complete!")

