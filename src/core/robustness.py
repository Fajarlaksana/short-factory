#!/usr/bin/env python3
"""
Robustness & Future-Proofing Module v1.0
========================================

Ensures system resilience to:
1. API changes (dynamic endpoint discovery)
2. Model deprecations (auto-fallback chains)
3. Rate limit changes (adaptive delays)
4. Service outages (multi-provider failover)
5. Schema changes (flexible parsing)

GOAL: System should NEVER fail completely due to external changes.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

try:
    import requests
except ImportError:
    requests = None

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

HEALTH_STATE_FILE = STATE_DIR / "service_health.json"
FALLBACK_CONFIG_FILE = STATE_DIR / "fallback_config.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class ServiceHealthMonitor:
    """
    Monitors service health and tracks failures.
    Enables auto-switching to healthy alternatives.
    """
    
    def __init__(self):
        self.health_data = self._load_health()
    
    def _load_health(self) -> Dict:
        try:
            if HEALTH_STATE_FILE.exists():
                with open(HEALTH_STATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "services": {},  # service_name -> {status, last_check, failures, last_success}
            "last_updated": None
        }
    
    def _save_health(self):
        self.health_data["last_updated"] = datetime.now().isoformat()
        with open(HEALTH_STATE_FILE, 'w') as f:
            json.dump(self.health_data, f, indent=2)
    
    def record_success(self, service: str):
        """Record successful service call."""
        if service not in self.health_data["services"]:
            self.health_data["services"][service] = {"failures": 0, "successes": 0}
        
        svc = self.health_data["services"][service]
        svc["status"] = "healthy"
        svc["last_success"] = datetime.now().isoformat()
        svc["failures"] = 0
        svc["successes"] = svc.get("successes", 0) + 1
        self._save_health()
    
    def record_failure(self, service: str, error: str = ""):
        """Record failed service call."""
        if service not in self.health_data["services"]:
            self.health_data["services"][service] = {"failures": 0, "successes": 0}
        
        svc = self.health_data["services"][service]
        svc["failures"] = svc.get("failures", 0) + 1
        svc["last_failure"] = datetime.now().isoformat()
        svc["last_error"] = error[:200]
        
        # Mark unhealthy after 3 consecutive failures
        if svc["failures"] >= 3:
            svc["status"] = "unhealthy"
        
        self._save_health()
    
    def is_healthy(self, service: str) -> bool:
        """Check if service is healthy."""
        if service not in self.health_data["services"]:
            return True  # Assume healthy if unknown
        
        svc = self.health_data["services"][service]
        
        # Auto-reset after 1 hour
        if svc.get("status") == "unhealthy":
            last_failure = svc.get("last_failure")
            if last_failure:
                try:
                    fail_time = datetime.fromisoformat(last_failure)
                    if datetime.now() - fail_time > timedelta(hours=1):
                        svc["status"] = "recovering"
                        svc["failures"] = 0
                        self._save_health()
                        return True
                except:
                    pass
        
        return svc.get("status", "healthy") != "unhealthy"
    
    def get_healthy_services(self, service_list: List[str]) -> List[str]:
        """Get list of healthy services from candidates."""
        return [s for s in service_list if self.is_healthy(s)]


class AdaptiveRateLimiter:
    """
    Adaptive rate limiting that learns from 429 errors.
    Adjusts delays dynamically to avoid rate limits.
    """
    
    def __init__(self):
        self.delays = {}  # provider -> current_delay
        self.default_delays = {
            "groq": 0.5,
            "gemini": 4.0,
            "openrouter": 1.0,
            "pexels": 0.2,
            "pixabay": 0.2,
        }
    
    def get_delay(self, provider: str) -> float:
        """Get current delay for provider."""
        return self.delays.get(provider, self.default_delays.get(provider, 1.0))
    
    def record_rate_limit(self, provider: str):
        """Increase delay after rate limit hit."""
        current = self.get_delay(provider)
        new_delay = min(current * 2, 60)  # Max 60 seconds
        self.delays[provider] = new_delay
        safe_print(f"   [RATE] Increased {provider} delay to {new_delay}s")
    
    def record_success(self, provider: str):
        """Slightly decrease delay after success."""
        current = self.get_delay(provider)
        default = self.default_delays.get(provider, 1.0)
        new_delay = max(current * 0.95, default)  # Min is default
        self.delays[provider] = new_delay
    
    def wait(self, provider: str):
        """Wait the appropriate delay for provider."""
        delay = self.get_delay(provider)
        if delay > 0:
            time.sleep(delay)


class FlexibleParser:
    """
    Flexible JSON/response parsing that handles schema changes.
    Uses multiple extraction strategies.
    """
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict]:
        """Extract JSON from text using multiple strategies."""
        import re
        
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Strategy 2: Extract from markdown code block
        if "```json" in text:
            try:
                json_str = text.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            except:
                pass
        
        if "```" in text:
            try:
                json_str = text.split("```")[1].split("```")[0]
                return json.loads(json_str)
            except:
                pass
        
        # Strategy 3: Find JSON object/array
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        try:
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        # Strategy 4: Line-by-line JSON extraction
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('{') or line.startswith('['):
                try:
                    return json.loads(line)
                except:
                    pass
        
        return None
    
    @staticmethod
    def safe_get(data: Dict, *keys, default=None):
        """Safely get nested dictionary value."""
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and isinstance(key, int):
                try:
                    current = current[key]
                except IndexError:
                    return default
            else:
                return default
            
            if current is None:
                return default
        return current


class ProviderFailover:
    """
    Manages failover between multiple providers.
    Automatically switches when primary fails.
    """
    
    def __init__(self):
        self.health_monitor = ServiceHealthMonitor()
        self.rate_limiter = AdaptiveRateLimiter()
    
    def execute_with_failover(self, providers: List[Dict], operation: Callable) -> Any:
        """
        Execute operation with automatic failover.
        
        providers: [{"name": "groq", "config": {...}}, {"name": "gemini", "config": {...}}]
        operation: function(provider_name, config) -> result
        """
        healthy = self.health_monitor.get_healthy_services([p["name"] for p in providers])
        
        # Try healthy providers first
        for provider in providers:
            if provider["name"] not in healthy:
                continue
            
            try:
                self.rate_limiter.wait(provider["name"])
                result = operation(provider["name"], provider["config"])
                
                if result is not None:
                    self.health_monitor.record_success(provider["name"])
                    self.rate_limiter.record_success(provider["name"])
                    return result
            except Exception as e:
                error_str = str(e)
                self.health_monitor.record_failure(provider["name"], error_str)
                
                if "429" in error_str or "rate" in error_str.lower():
                    self.rate_limiter.record_rate_limit(provider["name"])
                
                safe_print(f"   [!] {provider['name']} failed: {error_str[:100]}")
        
        # Try unhealthy providers as last resort
        for provider in providers:
            if provider["name"] in healthy:
                continue
            
            try:
                self.rate_limiter.wait(provider["name"])
                result = operation(provider["name"], provider["config"])
                
                if result is not None:
                    self.health_monitor.record_success(provider["name"])
                    return result
            except Exception as e:
                safe_print(f"   [!] Last resort {provider['name']} also failed")
        
        return None


# Global instances
_health_monitor = None
_rate_limiter = None
_failover = None

def get_health_monitor() -> ServiceHealthMonitor:
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ServiceHealthMonitor()
    return _health_monitor

def get_rate_limiter() -> AdaptiveRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = AdaptiveRateLimiter()
    return _rate_limiter

def get_failover() -> ProviderFailover:
    global _failover
    if _failover is None:
        _failover = ProviderFailover()
    return _failover


if __name__ == "__main__":
    safe_print("Testing Robustness Module...")
    
    # Test health monitor
    hm = get_health_monitor()
    hm.record_success("groq")
    hm.record_failure("gemini", "Test error")
    safe_print(f"Groq healthy: {hm.is_healthy('groq')}")
    safe_print(f"Gemini healthy: {hm.is_healthy('gemini')}")
    
    # Test flexible parser
    test_text = "Here is the result: ```json\n{\"key\": \"value\"}\n```"
    result = FlexibleParser.extract_json(test_text)
    safe_print(f"Parsed: {result}")
    
    safe_print("Robustness module test complete!")