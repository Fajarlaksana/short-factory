#!/usr/bin/env python3
"""
ViralShorts Factory - Quota Monitor v15.0
==========================================

This module monitors API quotas across all providers and provides:
1. Real-time quota status
2. Quota reset timing
3. Smart scheduling recommendations
4. Automatic throttling when near limits

Provider Limits:
- Groq: 100,000 TPD (resets at midnight UTC)
- Gemini: 60 RPM + 1M TPD 
- OpenRouter: Variable (free tier)

Goal: Never hit 429 errors!
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# State directory
STATE_DIR = Path("data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

QUOTA_FILE = STATE_DIR / "quota_monitor.json"


@dataclass
class ProviderQuotaStatus:
    """Quota status for a provider."""
    name: str
    daily_limit: int
    hourly_limit: int
    minute_limit: int
    used_today: int
    used_this_hour: int
    used_this_minute: int
    last_reset_day: str
    last_reset_hour: str
    last_reset_minute: str
    last_429_time: Optional[str] = None
    is_exhausted: bool = False
    estimated_recovery_time: Optional[str] = None


class QuotaMonitor:
    """
    Monitors API quotas and provides intelligent recommendations.
    """
    
    # Provider limits
    LIMITS = {
        "groq": {
            "daily": 300,      # v18.5: Token-based (300 calls)
            "hourly": 50,      # Spread over 6 hours  # Rough estimate
            "minute": 30,      # 30 RPM    # Rough estimate
        },
        "gemini": {
            "daily": 100,      # v18.5: 5 models x 20 RPD
            "hourly": 10,      # Spread over 10 hours
            "minute": 15,      # 15 RPM   # 60 RPM * ~27 avg tokens
        },
        "openrouter": {
            "daily": 10000,    # Free tier is generous
            "hourly": 1000,
            "minute": 60,
        }
    }
    
    def __init__(self):
        self.status = self._load()
        self._check_resets()
    
    def _load(self) -> Dict[str, ProviderQuotaStatus]:
        """Load quota status from disk."""
        try:
            if QUOTA_FILE.exists():
                with open(QUOTA_FILE, 'r') as f:
                    data = json.load(f)
                    return {
                        name: ProviderQuotaStatus(**status)
                        for name, status in data.items()
                    }
        except Exception as e:
            print(f"[QuotaMonitor] Load error: {e}")
        
        now = datetime.now(timezone.utc)
        return {
            name: ProviderQuotaStatus(
                name=name,
                daily_limit=limits["daily"],
                hourly_limit=limits["hourly"],
                minute_limit=limits["minute"],
                used_today=0,
                used_this_hour=0,
                used_this_minute=0,
                last_reset_day=now.strftime("%Y-%m-%d"),
                last_reset_hour=now.strftime("%Y-%m-%d %H"),
                last_reset_minute=now.strftime("%Y-%m-%d %H:%M"),
            )
            for name, limits in self.LIMITS.items()
        }
    
    def _save(self):
        """Save quota status to disk."""
        try:
            data = {name: asdict(status) for name, status in self.status.items()}
            with open(QUOTA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[QuotaMonitor] Save error: {e}")
    
    def _check_resets(self):
        """Check and apply quota resets."""
        now = datetime.now(timezone.utc)
        now_day = now.strftime("%Y-%m-%d")
        now_hour = now.strftime("%Y-%m-%d %H")
        now_minute = now.strftime("%Y-%m-%d %H:%M")
        
        for name, status in self.status.items():
            # Daily reset at midnight UTC
            if status.last_reset_day != now_day:
                status.used_today = 0
                status.last_reset_day = now_day
                status.is_exhausted = False
                status.estimated_recovery_time = None
                print(f"[QuotaMonitor] {name} daily quota reset")
            
            # Hourly reset
            if status.last_reset_hour != now_hour:
                status.used_this_hour = 0
                status.last_reset_hour = now_hour
            
            # Minute reset
            if status.last_reset_minute != now_minute:
                status.used_this_minute = 0
                status.last_reset_minute = now_minute
        
        self._save()
    
    def record_usage(self, provider: str, tokens: int):
        """Record token usage for a provider."""
        if provider not in self.status:
            return
        
        status = self.status[provider]
        status.used_today += tokens
        status.used_this_hour += tokens
        status.used_this_minute += tokens
        
        # Check if exhausted
        if status.used_today >= status.daily_limit:
            status.is_exhausted = True
            # Calculate recovery time (midnight UTC)
            now = datetime.now(timezone.utc)
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            status.estimated_recovery_time = midnight.isoformat()
        
        self._save()
    
    def record_429(self, provider: str, retry_seconds: int = 60):
        """Record a 429 error."""
        if provider not in self.status:
            return
        
        now = datetime.now(timezone.utc)
        status = self.status[provider]
        status.last_429_time = now.isoformat()
        status.is_exhausted = True
        status.estimated_recovery_time = (now + timedelta(seconds=retry_seconds)).isoformat()
        
        self._save()
        print(f"[QuotaMonitor] {provider} hit 429 - recovery in {retry_seconds}s")
    
    def can_use_provider(self, provider: str, tokens_needed: int = 1000) -> Tuple[bool, str]:
        """
        Check if a provider can be used.
        
        Returns:
            (can_use, reason)
        """
        self._check_resets()
        
        if provider not in self.status:
            return False, f"Provider {provider} not tracked"
        
        status = self.status[provider]
        
        # Check exhaustion
        if status.is_exhausted:
            if status.estimated_recovery_time:
                try:
                    recovery = datetime.fromisoformat(status.estimated_recovery_time)
                    if datetime.now(timezone.utc) < recovery:
                        wait = (recovery - datetime.now(timezone.utc)).total_seconds()
                        return False, f"Exhausted, recovery in {int(wait)}s"
                    else:
                        # Recovery time passed
                        status.is_exhausted = False
                        status.estimated_recovery_time = None
                except:
                    pass
        
        # Check daily limit
        if status.used_today + tokens_needed > status.daily_limit:
            return False, f"Daily limit ({status.used_today}/{status.daily_limit})"
        
        # Check hourly limit
        if status.used_this_hour + tokens_needed > status.hourly_limit:
            return False, f"Hourly limit ({status.used_this_hour}/{status.hourly_limit})"
        
        # Check minute limit
        if status.used_this_minute + tokens_needed > status.minute_limit:
            return False, f"Minute limit ({status.used_this_minute}/{status.minute_limit})"
        
        return True, "OK"
    
    def get_best_provider(self, tokens_needed: int = 1000) -> Optional[str]:
        """
        Get the best available provider based on quota status.
        
        Priority:
        1. Groq (fastest) if available
        2. Gemini (most capacity) if available
        3. OpenRouter (backup)
        """
        providers_priority = ["groq", "gemini", "openrouter"]
        
        for provider in providers_priority:
            can_use, reason = self.can_use_provider(provider, tokens_needed)
            if can_use:
                return provider
        
        return None
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        self._check_resets()
        
        lines = ["=" * 60, "QUOTA MONITOR STATUS", "=" * 60]
        
        for name, status in self.status.items():
            pct = (status.used_today / status.daily_limit) * 100 if status.daily_limit else 0
            exhausted = " [EXHAUSTED]" if status.is_exhausted else ""
            recovery = ""
            if status.estimated_recovery_time:
                try:
                    rec = datetime.fromisoformat(status.estimated_recovery_time)
                    wait = (rec - datetime.now(timezone.utc)).total_seconds()
                    if wait > 0:
                        recovery = f" (recovery in {int(wait)}s)"
                except:
                    pass
            
            lines.append(
                f"  {name.upper():12} | "
                f"{status.used_today:,}/{status.daily_limit:,} ({pct:.1f}%){exhausted}{recovery}"
            )
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def get_scheduling_recommendation(self) -> Dict:
        """
        Get recommendation for when to run next batch.
        
        Returns:
            {
                "can_run_now": bool,
                "reason": str,
                "recommended_wait": int (seconds),
                "best_provider": str or None,
                "videos_possible": int
            }
        """
        self._check_resets()
        
        # Check if any provider is available
        # Use smaller token check - actual usage will be spread over time
        # We check daily availability, not minute limits
        best = self.get_best_provider(500)  # Check with per-call tokens (not per-video)
        
        if best:
            # Estimate how many videos we can make
            status = self.status[best]
            remaining = status.daily_limit - status.used_today
            videos = remaining // 13500  # ~13.5k tokens per video
            
            return {
                "can_run_now": True,
                "reason": f"{best} available",
                "recommended_wait": 0,
                "best_provider": best,
                "videos_possible": videos
            }
        
        # All providers exhausted - find earliest recovery
        earliest_recovery = None
        earliest_provider = None
        
        for name, status in self.status.items():
            if status.estimated_recovery_time:
                try:
                    rec = datetime.fromisoformat(status.estimated_recovery_time)
                    if earliest_recovery is None or rec < earliest_recovery:
                        earliest_recovery = rec
                        earliest_provider = name
                except:
                    pass
        
        if earliest_recovery:
            wait = max(0, (earliest_recovery - datetime.now(timezone.utc)).total_seconds())
            return {
                "can_run_now": False,
                "reason": f"All providers exhausted",
                "recommended_wait": int(wait),
                "best_provider": earliest_provider,
                "videos_possible": 0
            }
        
        # Default: wait until midnight UTC
        now = datetime.now(timezone.utc)
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait = (midnight - now).total_seconds()
        
        return {
            "can_run_now": False,
            "reason": "Daily limits reached, wait for midnight UTC reset",
            "recommended_wait": int(wait),
            "best_provider": None,
            "videos_possible": 0
        }


# Singleton
_quota_monitor = None

def get_quota_monitor() -> QuotaMonitor:
    """Get the singleton quota monitor."""
    global _quota_monitor
    if _quota_monitor is None:
        _quota_monitor = QuotaMonitor()
    return _quota_monitor


if __name__ == "__main__":
    # Test the quota monitor
    monitor = get_quota_monitor()
    
    print(monitor.get_status_summary())
    
    # Test recommendations
    rec = monitor.get_scheduling_recommendation()
    print(f"\nScheduling Recommendation:")
    print(f"  Can run now: {rec['can_run_now']}")
    print(f"  Reason: {rec['reason']}")
    print(f"  Best provider: {rec['best_provider']}")
    print(f"  Videos possible: {rec['videos_possible']}")
    
    if not rec['can_run_now']:
        print(f"  Wait: {rec['recommended_wait']}s ({rec['recommended_wait']//60}min)")

