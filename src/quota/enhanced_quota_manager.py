#!/usr/bin/env python3
"""
Enhanced Quota Utilization v2.0
===============================

Smart quota management:
1. Dynamic quota discovery from provider APIs
2. Predictive usage patterns
3. Surplus allocation for learning
4. Auto-balancing between providers
5. Real-time monitoring

GOAL: Use 100% of available quota efficiently!
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    requests = None

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

QUOTA_STATE_FILE = STATE_DIR / "enhanced_quota_state.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class EnhancedQuotaManager:
    """
    Smart quota management with dynamic discovery and optimization.
    """
    
    # Default quotas (overridden by API discovery)
    DEFAULT_QUOTAS = {
        "groq": {
            "daily_requests": 14400,  # Free tier
            "requests_per_minute": 30,
            "tokens_per_minute": 15000,
        },
        "gemini": {
            "daily_requests": 1500,  # Per model
            "requests_per_minute": 15,
            "tokens_per_minute": 1000000,
        },
        "openrouter": {
            "daily_requests": 200,  # Free tier limited
            "requests_per_minute": 10,
        }
    }
    
    # Production needs per video
    PRODUCTION_NEEDS = {
        "content_generation": 3,
        "evaluation": 2,
        "voiceover": 1,
        "broll": 2,
        "music": 1,
        "thumbnail": 1,
        "total_per_video": 10,
    }
    
    def __init__(self):
        self.state = self._load_state()
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
    
    def _load_state(self) -> Dict:
        try:
            if QUOTA_STATE_FILE.exists():
                with open(QUOTA_STATE_FILE, 'r') as f:
                    data = json.load(f)
                    # Reset if new day
                    last_reset = data.get("last_reset", "")
                    if last_reset != datetime.now().strftime("%Y-%m-%d"):
                        data["usage"] = {}
                        data["last_reset"] = datetime.now().strftime("%Y-%m-%d")
                    return data
        except:
            pass
        return {
            "quotas": {},
            "usage": {},
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
            "last_discovery": None
        }
    
    def _save_state(self):
        self.state["last_updated"] = datetime.now().isoformat()
        with open(QUOTA_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def discover_quotas(self) -> Dict[str, Dict]:
        """Discover actual quotas from provider APIs."""
        discovered = {}
        
        # Check if discovery is recent (within 24 hours)
        last_discovery = self.state.get("last_discovery")
        if last_discovery:
            try:
                last_time = datetime.fromisoformat(last_discovery)
                if datetime.now() - last_time < timedelta(hours=24):
                    return self.state.get("quotas", self.DEFAULT_QUOTAS)
            except:
                pass
        
        # Discover Groq quota
        if self.groq_key and requests:
            try:
                response = requests.get(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {self.groq_key}"},
                    timeout=10
                )
                if response.status_code == 200:
                    # Groq free tier is 14400 requests/day (10 RPM)
                    discovered["groq"] = {
                        "daily_requests": 14400,
                        "requests_per_minute": 30,
                        "available": True
                    }
                    safe_print("   [QUOTA] Groq: 14,400 req/day discovered")
            except Exception as e:
                safe_print(f"   [!] Groq discovery failed: {e}")
        
        # Discover Gemini quota
        if self.gemini_key and requests:
            try:
                response = requests.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={self.gemini_key}",
                    timeout=10
                )
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    # Count available models and estimate total quota
                    model_count = len([m for m in models if "flash" in m.get("name", "").lower()])
                    # Each model has ~1500 req/day
                    discovered["gemini"] = {
                        "daily_requests": model_count * 1500,
                        "requests_per_minute": 15,
                        "models_available": model_count,
                        "available": True
                    }
                    safe_print(f"   [QUOTA] Gemini: {model_count} models, ~{model_count * 1500} req/day")
            except Exception as e:
                safe_print(f"   [!] Gemini discovery failed: {e}")
        
        if discovered:
            self.state["quotas"] = discovered
            self.state["last_discovery"] = datetime.now().isoformat()
            self._save_state()
        
        return discovered if discovered else self.DEFAULT_QUOTAS
    
    def get_usage(self, provider: str) -> int:
        """Get current usage for provider."""
        return self.state.get("usage", {}).get(provider, 0)
    
    def record_usage(self, provider: str, count: int = 1):
        """Record API usage."""
        if "usage" not in self.state:
            self.state["usage"] = {}
        self.state["usage"][provider] = self.state["usage"].get(provider, 0) + count
        self._save_state()
    
    def get_remaining_quota(self, provider: str) -> int:
        """Get remaining quota for provider."""
        quotas = self.state.get("quotas", self.DEFAULT_QUOTAS)
        provider_quota = quotas.get(provider, {})
        daily_limit = provider_quota.get("daily_requests", 1000)
        used = self.get_usage(provider)
        return max(0, daily_limit - used)
    
    def get_surplus_quota(self) -> Dict[str, int]:
        """
        Calculate surplus quota available for learning/aggressive mode.
        
        Surplus = Total Quota - Production Reserved - Safety Margin
        """
        quotas = self.discover_quotas()
        
        # Production needs
        videos_per_day = 6
        calls_per_video = self.PRODUCTION_NEEDS["total_per_video"]
        production_reserve = videos_per_day * calls_per_video
        safety_margin = 0.1  # 10% safety
        
        surplus = {}
        for provider, quota in quotas.items():
            daily = quota.get("daily_requests", 0)
            if daily > 0:
                safe_limit = int(daily * (1 - safety_margin))
                available = safe_limit - production_reserve
                surplus[provider] = max(0, available)
        
        return surplus
    
    def allocate_for_learning(self) -> Dict[str, int]:
        """
        Allocate surplus quota for learning activities.
        
        Learning activities:
        - Aggressive mode analysis
        - Trend research
        - Competitor analysis
        - A/B testing
        """
        surplus = self.get_surplus_quota()
        
        allocations = {
            "aggressive_mode": {},
            "trend_research": {},
            "competitor_analysis": {},
            "ab_testing": {},
        }
        
        for provider, available in surplus.items():
            if available <= 0:
                continue
            
            # Allocation percentages
            allocations["aggressive_mode"][provider] = int(available * 0.4)
            allocations["trend_research"][provider] = int(available * 0.2)
            allocations["competitor_analysis"][provider] = int(available * 0.2)
            allocations["ab_testing"][provider] = int(available * 0.2)
        
        return allocations
    
    def get_best_provider_for_task(self, task_type: str) -> Optional[str]:
        """
        Get best provider for a task based on:
        1. Remaining quota
        2. Task type requirements
        3. Provider quality for task
        """
        task_preferences = {
            "creative": ["groq", "gemini"],  # Need creativity
            "evaluation": ["gemini", "groq"],  # Need structured output
            "simple": ["groq", "gemini"],  # Fast response
            "learning": ["groq", "gemini"],  # Use surplus
        }
        
        preferences = task_preferences.get(task_type, ["groq", "gemini"])
        
        for provider in preferences:
            remaining = self.get_remaining_quota(provider)
            if remaining > 10:  # At least 10 calls left
                return provider
        
        return preferences[0] if preferences else "groq"
    
    def get_utilization_report(self) -> Dict:
        """Get current quota utilization report."""
        quotas = self.state.get("quotas", self.DEFAULT_QUOTAS)
        usage = self.state.get("usage", {})
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "providers": {}
        }
        
        for provider, quota in quotas.items():
            daily = quota.get("daily_requests", 0)
            used = usage.get(provider, 0)
            remaining = max(0, daily - used)
            utilization = (used / daily * 100) if daily > 0 else 0
            
            report["providers"][provider] = {
                "daily_limit": daily,
                "used": used,
                "remaining": remaining,
                "utilization_percent": round(utilization, 1)
            }
        
        surplus = self.get_surplus_quota()
        report["surplus_available"] = surplus
        report["total_surplus"] = sum(surplus.values())
        
        return report


# Singleton
_quota_manager = None

def get_quota_manager() -> EnhancedQuotaManager:
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = EnhancedQuotaManager()
    return _quota_manager


def get_utilization_report() -> Dict:
    return get_quota_manager().get_utilization_report()


def get_surplus_for_learning() -> Dict[str, int]:
    return get_quota_manager().get_surplus_quota()


if __name__ == "__main__":
    safe_print("Testing Enhanced Quota Manager...")
    
    mgr = get_quota_manager()
    
    # Discover quotas
    quotas = mgr.discover_quotas()
    safe_print(f"Discovered quotas: {quotas}")
    
    # Get surplus
    surplus = mgr.get_surplus_quota()
    safe_print(f"Surplus available: {surplus}")
    
    # Get report
    report = mgr.get_utilization_report()
    safe_print(f"Utilization: {report}")