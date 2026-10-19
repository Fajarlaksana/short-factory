#!/usr/bin/env python3
"""
Quota Pool System v1.0
======================

Tracks ACTUAL available quota across all models and providers.
Creates pools by step category with safety margins.

Pools:
1. PRODUCTION_REGULAR - High-throughput models for bulk steps
2. PRODUCTION_CRITICAL - High-quality models for important steps  
3. TESTING - Leftover quota for testing workflows
4. ANALYTICS_BONUS - Extra quota for aggressive mode

Safety: 10% margin on all quotas
"""

import os
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Persistent storage
POOL_STATE_FILE = Path("data/persistent/quota_pools.json")

# Safety margin (10%)
SAFETY_MARGIN = 0.10


@dataclass
class ModelQuota:
    """Quota info for a single model."""
    provider: str
    model: str
    daily_limit: int
    used_today: int = 0
    reserved: int = 0  # Reserved for production
    quality_score: float = 5.0
    throughput: str = "medium"  # low, medium, high
    is_shared: bool = False  # Groq models share quota
    
    @property
    def available(self) -> int:
        """Available quota after usage and reservations."""
        return max(0, self.daily_limit - self.used_today - self.reserved)
    
    @property
    def safe_limit(self) -> int:
        """Daily limit with 10% safety margin."""
        return int(self.daily_limit * (1 - SAFETY_MARGIN))


@dataclass 
class QuotaPool:
    """A pool of quota for a specific step category."""
    name: str
    total_quota: int = 0
    used: int = 0
    models: List[str] = None  # Models contributing to this pool
    
    def __post_init__(self):
        if self.models is None:
            self.models = []
    
    @property
    def available(self) -> int:
        return max(0, self.total_quota - self.used)
    
    def can_use(self, amount: int = 1) -> bool:
        return self.available >= amount
    
    def use(self, amount: int = 1) -> bool:
        if self.can_use(amount):
            self.used += amount
            return True
        return False


class QuotaPoolManager:
    """
    Manages quota pools across all providers.
    
    Tracks:
    - Per-model quota limits and usage
    - Per-pool availability
    - Daily reset
    """
    
    # Known model quotas (will be updated from API)
    # v18.6: CORRECTED quotas based on actual free-tier limits
    KNOWN_QUOTAS = {
        # Gemini models - 20 RPD PER MODEL (free tier!)
        # Total Gemini: ~100 calls/day across 5 models
        "gemini-2.5-flash": {"daily": 20, "quality": 7.5, "throughput": "low", "shared": False},
        "gemini-2.5-pro": {"daily": 20, "quality": 8.5, "throughput": "low", "shared": False},
        "gemini-2.0-flash": {"daily": 20, "quality": 7.0, "throughput": "medium", "shared": False},
        "gemini-2.0-flash-exp": {"daily": 20, "quality": 6.0, "throughput": "low", "shared": False},
        "gemini-1.5-flash": {"daily": 20, "quality": 6.5, "throughput": "high", "shared": False},
        # REMOVED: gemini-1.5-pro - deprecated, returns 404
        
        # Groq models - Token-based limits (NOT calls)
        # 70b: ~100K TPD = ~50 calls/day (2K tokens/call avg)
        # 8b: ~500K TPD = ~250 calls/day (2K tokens/call avg)
        "llama-3.3-70b-versatile": {"daily": 50, "quality": 9.0, "throughput": "medium", "shared": False},
        "llama-3.1-8b-instant": {"daily": 250, "quality": 6.0, "throughput": "high", "shared": False},
        "mixtral-8x7b-32768": {"daily": 100, "quality": 7.0, "throughput": "high", "shared": False},
        
        # OpenRouter (free models, limited capabilities)
        "openrouter:free": {"daily": 200, "quality": 4.0, "throughput": "medium", "shared": False},
    }
    
    # Production needs per video (with 10% margin)
    PRODUCTION_NEEDS = {
        "regular_steps_per_video": 12,  # Script, CTA, phrases, etc.
        "critical_steps_per_video": 3,   # Hook, quality eval, master
        "videos_per_day": 6,
    }
    
    def __init__(self):
        self.models: Dict[str, ModelQuota] = {}
        self.pools: Dict[str, QuotaPool] = {
            "PRODUCTION_REGULAR": QuotaPool("PRODUCTION_REGULAR"),
            "PRODUCTION_CRITICAL": QuotaPool("PRODUCTION_CRITICAL"),
            "TESTING": QuotaPool("TESTING"),
            "ANALYTICS_BONUS": QuotaPool("ANALYTICS_BONUS"),
        }
        self.last_reset: str = ""
        self._load_state()
        self._check_daily_reset()
    
    def _load_state(self):
        """Load state from persistent storage."""
        try:
            if POOL_STATE_FILE.exists():
                with open(POOL_STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.last_reset = data.get("last_reset", "")
                    
                    # Load models
                    for m_data in data.get("models", []):
                        mq = ModelQuota(**m_data)
                        self.models[f"{mq.provider}:{mq.model}"] = mq
                    
                    # Load pools
                    for p_name, p_data in data.get("pools", {}).items():
                        if p_name in self.pools:
                            self.pools[p_name] = QuotaPool(**p_data)
        except Exception as e:
            print(f"[QUOTA_POOL] Failed to load state: {e}")
    
    def _save_state(self):
        """Save state to persistent storage."""
        try:
            POOL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "last_reset": self.last_reset,
                "last_updated": datetime.now().isoformat(),
                "models": [asdict(m) for m in self.models.values()],
                "pools": {name: asdict(pool) for name, pool in self.pools.items()},
            }
            with open(POOL_STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[QUOTA_POOL] Failed to save state: {e}")
    
    def _check_daily_reset(self):
        """Reset counters if new day."""
        today = date.today().isoformat()
        if self.last_reset != today:
            print(f"[QUOTA_POOL] New day - resetting quotas")
            for model in self.models.values():
                model.used_today = 0
            for pool in self.pools.values():
                pool.used = 0
            self.last_reset = today
            self._recalculate_pools()
            self._save_state()
    
    def register_model(self, provider: str, model: str, daily_limit: int = None,
                       quality: float = None, throughput: str = None):
        """Register a model with its quota."""
        key = f"{provider}:{model}"
        
        # Get known values or use defaults
        known = self.KNOWN_QUOTAS.get(model, {})
        daily = daily_limit or known.get("daily", 100)
        qual = quality or known.get("quality", 5.0)
        thru = throughput or known.get("throughput", "medium")
        shared = known.get("shared", provider == "groq")
        
        self.models[key] = ModelQuota(
            provider=provider,
            model=model,
            daily_limit=daily,
            quality_score=qual,
            throughput=thru,
            is_shared=shared,
        )
        
        self._recalculate_pools()
        self._save_state()
    
    def _recalculate_pools(self):
        """Recalculate pool quotas based on registered models."""
        # Reset pools
        for pool in self.pools.values():
            pool.total_quota = 0
            pool.models = []
        
        # Calculate production needs
        videos = self.PRODUCTION_NEEDS["videos_per_day"]
        regular_needed = videos * self.PRODUCTION_NEEDS["regular_steps_per_video"]
        critical_needed = videos * self.PRODUCTION_NEEDS["critical_steps_per_video"]
        
        # Track Groq shared quota separately
        groq_total = 0
        groq_reserved = 0
        
        for key, model in self.models.items():
            safe_quota = model.safe_limit  # Apply 10% margin
            
            # Handle Groq shared quota
            if model.is_shared:
                if groq_total == 0:  # Only count once
                    groq_total = safe_quota
                continue  # Process Groq after loop
            
            # Categorize by quality and throughput
            if model.quality_score >= 7.0:
                if model.throughput in ["high", "medium"]:
                    # High quality + good throughput = regular production
                    reserve = min(regular_needed, safe_quota)
                    model.reserved = reserve
                    self.pools["PRODUCTION_REGULAR"].total_quota += reserve
                    self.pools["PRODUCTION_REGULAR"].models.append(key)
                    
                    # Remaining goes to bonus
                    remaining = safe_quota - reserve
                    if remaining > 0:
                        self.pools["ANALYTICS_BONUS"].total_quota += remaining
                        self.pools["ANALYTICS_BONUS"].models.append(key)
                else:
                    # High quality + low throughput = critical tasks
                    reserve = min(critical_needed, safe_quota)
                    model.reserved = reserve
                    self.pools["PRODUCTION_CRITICAL"].total_quota += reserve
                    self.pools["PRODUCTION_CRITICAL"].models.append(key)
                    
                    # Remaining goes to bonus
                    remaining = safe_quota - reserve
                    if remaining > 0:
                        self.pools["ANALYTICS_BONUS"].total_quota += remaining
            else:
                # Lower quality = testing
                self.pools["TESTING"].total_quota += safe_quota
                self.pools["TESTING"].models.append(key)
        
        # Add Groq to appropriate pool (high throughput, good quality)
        if groq_total > 0:
            # Reserve for production fallback
            groq_reserve = min(regular_needed // 2, groq_total)  # 50% of regular needs
            self.pools["PRODUCTION_REGULAR"].total_quota += groq_reserve
            self.pools["PRODUCTION_REGULAR"].models.append("groq:shared")
            
            # Rest goes to bonus
            remaining = groq_total - groq_reserve
            if remaining > 0:
                self.pools["ANALYTICS_BONUS"].total_quota += remaining
                self.pools["ANALYTICS_BONUS"].models.append("groq:shared")
    
    def use_quota(self, pool_name: str, amount: int = 1, model_key: str = None) -> bool:
        """
        Use quota from a pool.
        
        Args:
            pool_name: Which pool to use from
            amount: How many calls
            model_key: Optional specific model (for tracking)
        
        Returns: True if quota was available and used
        """
        self._check_daily_reset()
        
        pool = self.pools.get(pool_name)
        if not pool:
            print(f"[QUOTA_POOL] Unknown pool: {pool_name}")
            return False
        
        if pool.use(amount):
            # Track model usage if specified
            if model_key and model_key in self.models:
                self.models[model_key].used_today += amount
            self._save_state()
            return True
        
        print(f"[QUOTA_POOL] Pool {pool_name} exhausted ({pool.used}/{pool.total_quota})")
        return False
    
    def get_available(self, pool_name: str) -> int:
        """Get available quota in a pool."""
        self._check_daily_reset()
        pool = self.pools.get(pool_name)
        return pool.available if pool else 0
    
    def get_best_model_for_pool(self, pool_name: str) -> Optional[str]:
        """Get the best available model from a pool."""
        pool = self.pools.get(pool_name)
        if not pool or not pool.models:
            return None
        
        # Sort by quality (highest first)
        available_models = []
        for key in pool.models:
            if key == "groq:shared":
                # Find best Groq model
                for mk, m in self.models.items():
                    if m.is_shared and m.available > 0:
                        available_models.append((mk, m.quality_score))
            elif key in self.models:
                m = self.models[key]
                if m.available > 0:
                    available_models.append((key, m.quality_score))
        
        if available_models:
            available_models.sort(key=lambda x: x[1], reverse=True)
            return available_models[0][0]
        
        return None
    
    def get_status(self) -> Dict:
        """Get full quota pool status."""
        self._check_daily_reset()
        
        return {
            "last_reset": self.last_reset,
            "pools": {
                name: {
                    "total": pool.total_quota,
                    "used": pool.used,
                    "available": pool.available,
                    "models": pool.models,
                }
                for name, pool in self.pools.items()
            },
            "models": {
                key: {
                    "daily_limit": m.daily_limit,
                    "safe_limit": m.safe_limit,
                    "used": m.used_today,
                    "reserved": m.reserved,
                    "available": m.available,
                    "quality": m.quality_score,
                    "throughput": m.throughput,
                    "shared": m.is_shared,
                }
                for key, m in self.models.items()
            },
            "summary": {
                "total_daily_quota": sum(m.safe_limit for m in self.models.values() if not m.is_shared),
                "total_used": sum(m.used_today for m in self.models.values()),
                "total_available": sum(pool.available for pool in self.pools.values()),
                "production_regular_available": self.pools["PRODUCTION_REGULAR"].available,
                "production_critical_available": self.pools["PRODUCTION_CRITICAL"].available,
                "bonus_available": self.pools["ANALYTICS_BONUS"].available,
            }
        }
    
    def print_status(self):
        """Print quota pool status."""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("  QUOTA POOL STATUS")
        print("=" * 60)
        
        print(f"\n  Last Reset: {status['last_reset']}")
        
        print("\n  POOLS:")
        for name, info in status["pools"].items():
            pct = (info["available"] / info["total"] * 100) if info["total"] > 0 else 0
            print(f"    {name}:")
            print(f"      Available: {info['available']}/{info['total']} ({pct:.0f}%)")
            print(f"      Models: {', '.join(info['models'][:3])}...")
        
        print("\n  SUMMARY:")
        s = status["summary"]
        print(f"    Total Daily Quota: {s['total_daily_quota']}")
        print(f"    Total Used: {s['total_used']}")
        print(f"    Bonus Available: {s['bonus_available']}")


# Global instance
_pool_manager: Optional[QuotaPoolManager] = None


def get_pool_manager() -> QuotaPoolManager:
    """Get the global quota pool manager."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = QuotaPoolManager()
    return _pool_manager


def initialize_pools_from_discovery():
    """Initialize quota pools from model discovery."""
    try:
        from src.ai.model_helper import (
            _discover_gemini_models,
            _discover_groq_models,
            get_model_quality_score,
            get_model_rate_limit,
            _is_model_usable,
        )
        
        manager = get_pool_manager()
        
        # Register Gemini models
        gemini_models = _discover_gemini_models()
        for model in gemini_models:
            is_usable, quota = _is_model_usable(model, "gemini")
            if is_usable:
                score = get_model_quality_score(model)
                rate_info = get_model_rate_limit(model, "gemini")
                manager.register_model(
                    provider="gemini",
                    model=model,
                    daily_limit=quota,
                    quality=score,
                    throughput=rate_info.get("throughput", "medium"),
                )
        
        # Register Groq models
        groq_models = _discover_groq_models()
        for model in groq_models:
            score = get_model_quality_score(model)
            rate_info = get_model_rate_limit(model, "groq")
            manager.register_model(
                provider="groq",
                model=model,
                daily_limit=500,  # Shared pool
                quality=score,
                throughput=rate_info.get("throughput", "high"),
            )
        
        print("[QUOTA_POOL] Initialized from model discovery")
        manager.print_status()
        
    except Exception as e:
        print(f"[QUOTA_POOL] Discovery initialization failed: {e}")


# CLI
if __name__ == "__main__":
    import sys
    
    manager = get_pool_manager()
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        initialize_pools_from_discovery()
    else:
        manager.print_status()
