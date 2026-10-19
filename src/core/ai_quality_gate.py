#!/usr/bin/env python3
"""
ViralShorts Factory - AI Quality Gate v17.8
=============================================

Comprehensive quality gate that must be passed before video generation.
Uses all AI modules to ensure high-quality content.
"""

import os
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, 'src')
sys.path.insert(0, 'src/ai')
sys.path.insert(0, 'src/analytics')
sys.path.insert(0, 'src/core')


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# Import analyzers
try:
    from virality_calculator import get_virality_calculator
    VIRAL_CALC = True
except ImportError:
    VIRAL_CALC = False

try:
    from retention_predictor import get_retention_predictor
    RETENTION = True
except ImportError:
    RETENTION = False

try:
    from engagement_predictor import get_engagement_predictor
    ENGAGEMENT = True
except ImportError:
    ENGAGEMENT = False

try:
    from script_analyzer import get_script_analyzer
    SCRIPT = True
except ImportError:
    SCRIPT = False

try:
    from ai_content_quality_checker import get_quality_checker
    AI_QUALITY = True
except ImportError:
    AI_QUALITY = False


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

GATE_FILE = STATE_DIR / "quality_gate_history.json"


class AIQualityGate:
    """
    Comprehensive quality gate for content.
    Content must pass all checks to proceed.
    """
    
    # Minimum thresholds
    THRESHOLDS = {
        "virality": 55,       # Minimum virality score
        "retention": 50,      # Minimum retention prediction
        "engagement": 40,     # Minimum engagement score
        "script": 50,         # Minimum script quality
        "overall": 50         # Minimum overall score
    }
    
    def __init__(self, strict: bool = False):
        self.strict = strict  # If True, all checks must pass
        self.data = self._load()
    
    def _load(self) -> Dict:
        try:
            if GATE_FILE.exists():
                with open(GATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "checks": [],
            "pass_rate": 0,
            "avg_score": 0,
            "last_updated": None
        }
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(GATE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def check(self, content: Dict) -> Tuple[bool, Dict]:
        """
        Run quality gate check on content.
        
        Args:
            content: Dict with hook, phrases, cta, topic, category
        
        Returns:
            Tuple of (passed: bool, report: dict)
        """
        checks = {}
        scores = []
        issues = []
        
        safe_print("\n[QUALITY GATE] Running checks...")
        
        # 1. Virality Check
        if VIRAL_CALC:
            calc = get_virality_calculator()
            virality = calc.calculate_virality(content)
            score = virality.get("overall_score", 0)
            checks["virality"] = {
                "score": score,
                "threshold": self.THRESHOLDS["virality"],
                "passed": score >= self.THRESHOLDS["virality"],
                "grade": virality.get("grade", "?")
            }
            scores.append(score)
            if not checks["virality"]["passed"]:
                issues.extend(virality.get("recommendations", []))
            safe_print(f"   [1/5] Virality: {score:.1f} ({virality.get('grade', '?')})")
        
        # 2. Retention Check
        if RETENTION:
            pred = get_retention_predictor()
            retention = pred.predict_retention(content)
            score = retention.get("overall_retention", 0)
            checks["retention"] = {
                "score": score,
                "threshold": self.THRESHOLDS["retention"],
                "passed": score >= self.THRESHOLDS["retention"]
            }
            scores.append(score)
            if not checks["retention"]["passed"]:
                issues.extend(retention.get("recommendations", []))
            safe_print(f"   [2/5] Retention: {score:.1f}%")
        
        # 3. Engagement Check
        if ENGAGEMENT:
            pred = get_engagement_predictor()
            engagement = pred.predict_engagement(content)
            score = engagement.get("overall_engagement", 0)
            checks["engagement"] = {
                "score": score,
                "threshold": self.THRESHOLDS["engagement"],
                "passed": score >= self.THRESHOLDS["engagement"]
            }
            scores.append(score)
            if not checks["engagement"]["passed"]:
                issues.extend(engagement.get("recommendations", []))
            safe_print(f"   [3/5] Engagement: {score:.1f}")
        
        # 4. Script Analysis
        if SCRIPT:
            analyzer = get_script_analyzer()
            analysis = analyzer.analyze_script(content)
            score = analysis.get("overall_score", 0)
            checks["script"] = {
                "score": score,
                "threshold": self.THRESHOLDS["script"],
                "passed": score >= self.THRESHOLDS["script"],
                "grade": analysis.get("grade", "?")
            }
            scores.append(score)
            if not checks["script"]["passed"]:
                issues.extend(analysis.get("suggestions", []))
            safe_print(f"   [4/5] Script: {score:.1f} ({analysis.get('grade', '?')})")
        
        # 5. AI Quality Check
        if AI_QUALITY:
            checker = get_quality_checker()
            quality = checker.check_content(content)
            score = quality.get("score", 5) * 10  # Convert to 0-100
            checks["ai_quality"] = {
                "score": score,
                "threshold": self.THRESHOLDS["overall"],
                "passed": score >= self.THRESHOLDS["overall"],
                "verdict": quality.get("verdict", "UNKNOWN")
            }
            scores.append(score)
            if not checks["ai_quality"]["passed"]:
                issues.extend(quality.get("suggestions", []))
            safe_print(f"   [5/5] AI Quality: {score:.1f} ({quality.get('verdict', '?')})")
        
        # Calculate overall
        overall = sum(scores) / len(scores) if scores else 0
        
        # Determine pass/fail
        if self.strict:
            passed = all(c.get("passed", False) for c in checks.values())
        else:
            passed = overall >= self.THRESHOLDS["overall"]
        
        # Create report
        report = {
            "passed": passed,
            "overall_score": round(overall, 1),
            "checks": checks,
            "issues": list(dict.fromkeys(issues))[:5],  # Top 5 unique issues
            "checks_run": len(checks),
            "checks_passed": sum(1 for c in checks.values() if c.get("passed", False)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Record history
        self._record_check(report)
        
        # Print result
        status = "PASSED" if passed else "FAILED"
        safe_print(f"\n[QUALITY GATE] {status} ({overall:.1f}/100)")
        
        if not passed and issues:
            safe_print("\n[QUALITY GATE] Top Issues:")
            for issue in issues[:3]:
                safe_print(f"   - {issue}")
        
        return passed, report
    
    def _record_check(self, report: Dict):
        """Record check in history."""
        self.data["checks"].append({
            "passed": report["passed"],
            "score": report["overall_score"],
            "timestamp": report["timestamp"]
        })
        
        # Keep last 100
        self.data["checks"] = self.data["checks"][-100:]
        
        # Update stats
        if self.data["checks"]:
            self.data["pass_rate"] = sum(1 for c in self.data["checks"] if c["passed"]) / len(self.data["checks"])
            self.data["avg_score"] = sum(c["score"] for c in self.data["checks"]) / len(self.data["checks"])
        
        self._save()
    
    def get_stats(self) -> Dict:
        """Get gate statistics."""
        return {
            "total_checks": len(self.data["checks"]),
            "pass_rate": round(self.data.get("pass_rate", 0) * 100, 1),
            "avg_score": round(self.data.get("avg_score", 0), 1)
        }
    
    def adjust_thresholds(self, new_thresholds: Dict):
        """Adjust quality thresholds."""
        for key, value in new_thresholds.items():
            if key in self.THRESHOLDS:
                self.THRESHOLDS[key] = value
                safe_print(f"   [GATE] Adjusted {key} threshold to {value}")


# Singleton
_quality_gate = None


def get_quality_gate(strict: bool = False) -> AIQualityGate:
    """Get quality gate."""
    global _quality_gate
    if _quality_gate is None:
        _quality_gate = AIQualityGate(strict)
    return _quality_gate


def check_content_quality(content: Dict, strict: bool = False) -> Tuple[bool, Dict]:
    """Convenience function."""
    return get_quality_gate(strict).check(content)


if __name__ == "__main__":
    safe_print("Testing AI Quality Gate...")
    safe_print("=" * 60)
    
    gate = get_quality_gate(strict=False)
    
    # Test content
    content = {
        "hook": "STOP - This will change how you think about money",
        "phrases": [
            "Most people save money wrong.",
            "Here are 3 things wealthy people do differently.",
            "First, they pay themselves first.",
            "Second, they invest before spending.",
            "Third, they have multiple income streams."
        ],
        "cta": "Which one will you try? Comment below!",
        "topic": "wealth building habits",
        "category": "money"
    }
    
    passed, report = gate.check(content)
    
    safe_print(f"\n{'='*60}")
    safe_print("QUALITY GATE REPORT")
    safe_print(f"{'='*60}")
    safe_print(f"Result: {'PASSED' if passed else 'FAILED'}")
    safe_print(f"Overall Score: {report['overall_score']}/100")
    safe_print(f"Checks Run: {report['checks_run']}")
    safe_print(f"Checks Passed: {report['checks_passed']}/{report['checks_run']}")
    
    if report['issues']:
        safe_print(f"\nIssues to Address:")
        for issue in report['issues']:
            safe_print(f"  - {issue}")
    
    # Stats
    stats = gate.get_stats()
    safe_print(f"\nGate Statistics:")
    safe_print(f"  Total Checks: {stats['total_checks']}")
    safe_print(f"  Pass Rate: {stats['pass_rate']}%")
    safe_print(f"  Avg Score: {stats['avg_score']}")
    
    safe_print(f"\n{'='*60}")
    safe_print("Test complete!")

