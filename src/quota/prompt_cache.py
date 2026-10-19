#!/usr/bin/env python3
"""
ViralShorts Factory - Prompt Cache v17.8
=========================================

Caches AI responses to reduce quota usage.

Many prompts are similar or identical:
- Same topic asked multiple times
- Template-based prompts
- Repeated pattern generations

This module:
1. Creates hash of prompts
2. Checks cache before making API calls
3. Stores responses with TTL
4. Saves significant quota

Estimated savings: 30-50% reduction in API calls!
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/cache")
STATE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = STATE_DIR / "prompt_cache.json"
STATS_FILE = STATE_DIR / "cache_stats.json"

# Default cache settings
DEFAULT_TTL_HOURS = 24
MAX_CACHE_SIZE = 1000


class PromptCache:
    """
    Caches AI prompt responses to reduce API quota usage.
    """
    
    def __init__(self, ttl_hours: int = DEFAULT_TTL_HOURS):
        self.ttl_hours = ttl_hours
        self.cache = self._load_cache()
        self.stats = self._load_stats()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk."""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f)
    
    def _load_stats(self) -> Dict:
        """Load cache stats."""
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "hits": 0,
            "misses": 0,
            "saved_calls": 0,
            "saved_tokens_estimate": 0,
            "created": datetime.now().isoformat()
        }
    
    def _save_stats(self):
        """Save stats to disk."""
        self.stats["last_updated"] = datetime.now().isoformat()
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _hash_prompt(self, prompt: str, context: str = "") -> str:
        """Create a hash of the prompt for cache key."""
        # Normalize prompt
        normalized = prompt.lower().strip()
        full_key = f"{normalized}:{context}"
        return hashlib.sha256(full_key.encode()).hexdigest()[:32]
    
    def _is_expired(self, cached_item: Dict) -> bool:
        """Check if cached item has expired."""
        if "timestamp" not in cached_item:
            return True
        
        try:
            cached_time = datetime.fromisoformat(cached_item["timestamp"])
            expiry = cached_time + timedelta(hours=self.ttl_hours)
            return datetime.now() > expiry
        except:
            return True
    
    def get(self, prompt: str, context: str = "") -> Optional[str]:
        """
        Get cached response for a prompt.
        
        Args:
            prompt: The prompt text
            context: Optional context (e.g., category, task type)
        
        Returns:
            Cached response or None if not found/expired
        """
        key = self._hash_prompt(prompt, context)
        
        if key in self.cache:
            cached = self.cache[key]
            
            if not self._is_expired(cached):
                self.stats["hits"] += 1
                self.stats["saved_calls"] += 1
                self.stats["saved_tokens_estimate"] += len(cached.get("response", ""))
                self._save_stats()
                return cached.get("response")
            else:
                # Expired - remove from cache
                del self.cache[key]
                self._save_cache()
        
        self.stats["misses"] += 1
        self._save_stats()
        return None
    
    def set(self, prompt: str, response: str, context: str = ""):
        """
        Cache a prompt response.
        
        Args:
            prompt: The prompt text
            response: The AI response
            context: Optional context
        """
        key = self._hash_prompt(prompt, context)
        
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:100]  # For debugging
        }
        
        # Enforce max cache size
        if len(self.cache) > MAX_CACHE_SIZE:
            self._evict_old_entries()
        
        self._save_cache()
    
    def _evict_old_entries(self):
        """Remove oldest entries to stay under max size."""
        # Sort by timestamp
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        # Keep newest entries
        self.cache = dict(sorted_items[:MAX_CACHE_SIZE - 100])
    
    def clear_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        expired_keys = [
            k for k, v in self.cache.items()
            if self._is_expired(v)
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "hit_rate": f"{hit_rate:.1%}",
            "total_requests": total
        }
    
    def clear(self):
        """Clear the entire cache."""
        self.cache = {}
        self._save_cache()


# Singleton
_prompt_cache = None


def get_prompt_cache() -> PromptCache:
    """Get the singleton prompt cache."""
    global _prompt_cache
    if _prompt_cache is None:
        _prompt_cache = PromptCache()
    return _prompt_cache


def cached_ai_call(prompt: str, context: str = "") -> Optional[str]:
    """Check cache for a prompt. Returns None if not found."""
    return get_prompt_cache().get(prompt, context)


def cache_ai_response(prompt: str, response: str, context: str = ""):
    """Cache an AI response."""
    get_prompt_cache().set(prompt, response, context)


if __name__ == "__main__":
    # Test
    safe_print("Testing Prompt Cache...")
    
    cache = get_prompt_cache()
    
    # Test set and get
    test_prompt = "Generate a viral hook for productivity content"
    test_response = "STOP - This 2-minute habit will change your life"
    
    cache.set(test_prompt, test_response, context="hook")
    
    # Test retrieval
    result = cache.get(test_prompt, context="hook")
    assert result == test_response, "Cache get failed!"
    safe_print(f"[PASS] Cache set/get works")
    
    # Test cache miss
    result = cache.get("nonexistent prompt")
    assert result is None, "Cache should return None for miss"
    safe_print(f"[PASS] Cache miss works")
    
    # Get stats
    stats = cache.get_stats()
    safe_print(f"\nCache Stats:")
    safe_print(f"  Hits: {stats['hits']}")
    safe_print(f"  Misses: {stats['misses']}")
    safe_print(f"  Hit Rate: {stats['hit_rate']}")
    safe_print(f"  Cache Size: {stats['cache_size']}")
    
    safe_print("\nTest complete!")

