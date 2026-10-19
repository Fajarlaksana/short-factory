#!/usr/bin/env python3
"""
Error Recovery Module v1.0
==========================

Provides intelligent error recovery for common failure scenarios:
1. API quota exhaustion
2. Network timeouts
3. Rate limiting
4. Model unavailability
5. Invalid responses

GOAL: System should recover gracefully from any error.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Callable, Any

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

ERROR_PATTERNS_FILE = STATE_DIR / "error_patterns.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class ErrorRecovery:
    """
    Intelligent error recovery with learning.
    """
    
    # Error classification
    ERROR_TYPES = {
        "quota": ["429", "quota", "rate limit", "exceeded"],
        "network": ["timeout", "connection", "network", "ssl", "socket"],
        "auth": ["401", "403", "unauthorized", "forbidden", "api key"],
        "server": ["500", "502", "503", "504", "internal server error"],
        "model": ["404", "not found", "deprecated", "unavailable"],
        "invalid": ["invalid", "malformed", "parse", "json"],
    }
    
    # Recovery strategies
    STRATEGIES = {
        "quota": {"wait": 60, "fallback": True, "retry": False},
        "network": {"wait": 5, "fallback": False, "retry": True, "max_retries": 3},
        "auth": {"wait": 0, "fallback": True, "retry": False},
        "server": {"wait": 30, "fallback": True, "retry": True, "max_retries": 2},
        "model": {"wait": 0, "fallback": True, "retry": False},
        "invalid": {"wait": 0, "fallback": True, "retry": False},
    }
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        try:
            if ERROR_PATTERNS_FILE.exists():
                with open(ERROR_PATTERNS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "error_counts": {},
            "recovery_success": {},
            "last_errors": []
        }
    
    def _save_patterns(self):
        self.patterns["last_updated"] = datetime.now().isoformat()
        with open(ERROR_PATTERNS_FILE, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def classify_error(self, error: str) -> str:
        """Classify error into type."""
        error_lower = error.lower()
        
        for error_type, keywords in self.ERROR_TYPES.items():
            for keyword in keywords:
                if keyword in error_lower:
                    return error_type
        
        return "unknown"
    
    def get_recovery_strategy(self, error: str) -> Dict:
        """Get recovery strategy for error."""
        error_type = self.classify_error(error)
        strategy = self.STRATEGIES.get(error_type, {
            "wait": 5, "fallback": True, "retry": True, "max_retries": 1
        })
        strategy["error_type"] = error_type
        return strategy
    
    def record_error(self, error: str, provider: str, model: str = ""):
        """Record error for learning."""
        error_type = self.classify_error(error)
        
        # Update counts
        if error_type not in self.patterns["error_counts"]:
            self.patterns["error_counts"][error_type] = 0
        self.patterns["error_counts"][error_type] += 1
        
        # Track recent errors
        self.patterns["last_errors"].append({
            "type": error_type,
            "provider": provider,
            "model": model,
            "error": error[:200],
            "time": datetime.now().isoformat()
        })
        
        # Keep only last 50 errors
        self.patterns["last_errors"] = self.patterns["last_errors"][-50:]
        
        self._save_patterns()
    
    def record_recovery(self, error_type: str, success: bool, strategy_used: str):
        """Record recovery outcome."""
        key = f"{error_type}:{strategy_used}"
        
        if key not in self.patterns["recovery_success"]:
            self.patterns["recovery_success"][key] = {"success": 0, "failure": 0}
        
        if success:
            self.patterns["recovery_success"][key]["success"] += 1
        else:
            self.patterns["recovery_success"][key]["failure"] += 1
        
        self._save_patterns()
    
    def execute_with_recovery(self, operation: Callable, 
                              fallback: Callable = None,
                              provider: str = "unknown") -> Any:
        """
        Execute operation with automatic error recovery.
        
        Args:
            operation: Main function to execute
            fallback: Fallback function if main fails
            provider: Provider name for logging
        
        Returns:
            Result from operation or fallback
        """
        try:
            result = operation()
            return result
        except Exception as e:
            error_str = str(e)
            strategy = self.get_recovery_strategy(error_str)
            self.record_error(error_str, provider)
            
            safe_print(f"   [RECOVERY] {strategy['error_type']} error: {error_str[:50]}...")
            
            # Apply strategy
            if strategy.get("wait", 0) > 0:
                safe_print(f"   [RECOVERY] Waiting {strategy['wait']}s...")
                time.sleep(strategy["wait"])
            
            if strategy.get("retry"):
                max_retries = strategy.get("max_retries", 1)
                for attempt in range(max_retries):
                    try:
                        safe_print(f"   [RECOVERY] Retry {attempt + 1}/{max_retries}...")
                        result = operation()
                        self.record_recovery(strategy["error_type"], True, "retry")
                        return result
                    except:
                        if strategy.get("wait", 0) > 0:
                            time.sleep(strategy["wait"] * (attempt + 1))
            
            if strategy.get("fallback") and fallback:
                try:
                    safe_print("   [RECOVERY] Using fallback...")
                    result = fallback()
                    self.record_recovery(strategy["error_type"], True, "fallback")
                    return result
                except Exception as fe:
                    self.record_recovery(strategy["error_type"], False, "fallback")
                    raise fe
            
            self.record_recovery(strategy["error_type"], False, "none")
            raise
    
    def get_health_report(self) -> Dict:
        """Get system health report based on errors."""
        recent_errors = [e for e in self.patterns.get("last_errors", [])
                        if datetime.fromisoformat(e["time"]) > datetime.now() - timedelta(hours=24)]
        
        report = {
            "last_24h_errors": len(recent_errors),
            "error_breakdown": {},
            "recovery_rates": {},
            "problematic_providers": []
        }
        
        # Count by type
        for error in recent_errors:
            error_type = error.get("type", "unknown")
            report["error_breakdown"][error_type] = report["error_breakdown"].get(error_type, 0) + 1
        
        # Calculate recovery rates
        for key, counts in self.patterns.get("recovery_success", {}).items():
            total = counts.get("success", 0) + counts.get("failure", 0)
            if total > 0:
                rate = counts["success"] / total
                report["recovery_rates"][key] = f"{rate:.0%}"
        
        # Find problematic providers
        provider_errors = {}
        for error in recent_errors:
            provider = error.get("provider", "unknown")
            provider_errors[provider] = provider_errors.get(provider, 0) + 1
        
        for provider, count in sorted(provider_errors.items(), key=lambda x: x[1], reverse=True):
            if count >= 3:  # 3+ errors in 24h is problematic
                report["problematic_providers"].append(f"{provider} ({count} errors)")
        
        return report


# Singleton
_recovery = None

def get_error_recovery() -> ErrorRecovery:
    global _recovery
    if _recovery is None:
        _recovery = ErrorRecovery()
    return _recovery


def with_recovery(operation: Callable, fallback: Callable = None, 
                  provider: str = "unknown") -> Any:
    """Convenience wrapper for error recovery."""
    return get_error_recovery().execute_with_recovery(operation, fallback, provider)


if __name__ == "__main__":
    safe_print("Testing Error Recovery...")
    
    recovery = get_error_recovery()
    
    # Test classification
    test_errors = [
        "429 Rate limit exceeded",
        "Connection timeout after 30s",
        "401 Unauthorized",
        "Model not found",
        "Invalid JSON response"
    ]
    
    for error in test_errors:
        error_type = recovery.classify_error(error)
        strategy = recovery.get_recovery_strategy(error)
        safe_print(f"  {error[:30]}... -> {error_type}: wait={strategy.get('wait')}s, fallback={strategy.get('fallback')}")
    
    # Get health report
    report = recovery.get_health_report()
    safe_print(f"\nHealth Report: {report}")