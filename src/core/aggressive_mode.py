#!/usr/bin/env python3
"""
ViralShorts Factory - Aggressive Mode v17.9.33
===============================================

AGGRESSIVE MODE: Use leftover/wasted quota for extra value!

When enabled, this mode uses surplus API quota (that would otherwise expire unused) for:
1. Extra virality analysis runs
2. More frequent self-learning cycles
3. Research video concept generation
4. Enhanced analytics and pattern detection

QUOTA MANAGEMENT:
- Production quota is ALWAYS reserved first (with 10% margin)
- Only SURPLUS quota is used for aggressive features
- Groq's shared 14,400/day quota provides large surplus
- OpenRouter free models provide additional capacity

SWITCH CONTROL:
- Enable: set_aggressive_mode(True) or via environment variable
- Disable: set_aggressive_mode(False)
- Check: is_aggressive_mode_enabled()

This is a SWITCH - when OFF, system operates normally.
When ON, it consumes extra quota for enhanced learning.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# State file for aggressive mode
STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
AGGRESSIVE_MODE_FILE = STATE_DIR / "aggressive_mode.json"


def _safe_print(msg: str):
    """Print with encoding fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())


# =============================================================================
# QUOTA POOL CONFIGURATION
# =============================================================================

# Estimated daily production needs (with 10% safety margin already applied)
PRODUCTION_QUOTA_NEEDS = {
    "video_generation": 350,    # ~50 calls/video * 6 videos + margin
    "analytics": 50,            # Performance analysis
    "pre_work": 50,             # Concept pre-generation
    "fallback_reserve": 100,    # Reserved for fallback scenarios
}

TOTAL_PRODUCTION_NEED = sum(PRODUCTION_QUOTA_NEEDS.values())  # ~550 calls/day

# Available quota pools (discovered dynamically, these are estimates)
ESTIMATED_QUOTA_POOLS = {
    "gemini_flash": 1500,       # Daily limit for flash models
    "gemini_pro": 50,           # Daily limit for pro models
    "groq_shared": 14400,       # Shared across all Groq models
    "openrouter_free": 2000,    # Conservative estimate for free models
}

TOTAL_AVAILABLE = sum(ESTIMATED_QUOTA_POOLS.values())  # ~17,950 calls/day


def get_surplus_quota() -> int:
    """
    Calculate surplus quota available for aggressive mode.
    
    Returns: Number of API calls available for aggressive features
    """
    # Reserve production needs + 20% extra safety
    reserved = int(TOTAL_PRODUCTION_NEED * 1.20)
    surplus = TOTAL_AVAILABLE - reserved
    return max(0, surplus)  # Never negative


# =============================================================================
# AGGRESSIVE MODE STATE
# =============================================================================

_aggressive_mode_enabled = None  # Cached state


def _load_state() -> Dict:
    """Load aggressive mode state from file."""
    try:
        if AGGRESSIVE_MODE_FILE.exists():
            with open(AGGRESSIVE_MODE_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {
        "enabled": False,
        "last_changed": None,
        "stats": {
            "extra_analytics_runs": 0,
            "research_concepts_generated": 0,
            "learning_cycles_completed": 0,
            "quota_used": 0,
        }
    }


def _save_state(state: Dict):
    """Save aggressive mode state to file."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(AGGRESSIVE_MODE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        _safe_print(f"[AGGRESSIVE] Failed to save state: {e}")


def is_aggressive_mode_enabled() -> bool:
    """
    Check if aggressive mode is enabled.
    
    Can be set via:
    1. Environment variable: AGGRESSIVE_MODE=1
    2. Persistent state file
    3. set_aggressive_mode() function
    """
    global _aggressive_mode_enabled
    
    # Check environment variable first (highest priority)
    env_value = os.environ.get("AGGRESSIVE_MODE", "").lower()
    if env_value in ("1", "true", "yes", "on"):
        return True
    if env_value in ("0", "false", "no", "off"):
        return False
    
    # Check cached value
    if _aggressive_mode_enabled is not None:
        return _aggressive_mode_enabled
    
    # Load from file
    state = _load_state()
    _aggressive_mode_enabled = state.get("enabled", False)
    return _aggressive_mode_enabled


def set_aggressive_mode(enabled: bool) -> Dict:
    """
    Enable or disable aggressive mode.
    
    Args:
        enabled: True to enable, False to disable
    
    Returns:
        Updated state dict
    """
    global _aggressive_mode_enabled
    
    state = _load_state()
    state["enabled"] = enabled
    state["last_changed"] = datetime.now().isoformat()
    
    _save_state(state)
    _aggressive_mode_enabled = enabled
    
    status = "ENABLED" if enabled else "DISABLED"
    _safe_print(f"[AGGRESSIVE] Mode {status}")
    if enabled:
        surplus = get_surplus_quota()
        _safe_print(f"[AGGRESSIVE] Surplus quota available: ~{surplus} calls/day")
    
    return state


def get_aggressive_mode_stats() -> Dict:
    """Get aggressive mode statistics."""
    state = _load_state()
    return {
        "enabled": state.get("enabled", False),
        "last_changed": state.get("last_changed"),
        "surplus_quota": get_surplus_quota(),
        "production_reserved": TOTAL_PRODUCTION_NEED,
        "stats": state.get("stats", {}),
    }


def record_aggressive_action(action_type: str, quota_used: int = 1):
    """
    Record an aggressive mode action for stats tracking.
    
    Args:
        action_type: Type of action ("analytics", "research", "learning")
        quota_used: Number of API calls consumed
    """
    state = _load_state()
    stats = state.get("stats", {})
    
    if action_type == "analytics":
        stats["extra_analytics_runs"] = stats.get("extra_analytics_runs", 0) + 1
    elif action_type == "research":
        stats["research_concepts_generated"] = stats.get("research_concepts_generated", 0) + 1
    elif action_type == "learning":
        stats["learning_cycles_completed"] = stats.get("learning_cycles_completed", 0) + 1
    
    stats["quota_used"] = stats.get("quota_used", 0) + quota_used
    state["stats"] = stats
    
    _save_state(state)


# =============================================================================
# AGGRESSIVE MODE ACTIONS
# =============================================================================

def should_run_extra_analytics() -> bool:
    """
    Check if we should run extra analytics in aggressive mode.
    
    Returns True if:
    - Aggressive mode is enabled
    - We have surplus quota
    - Haven't exceeded daily extra runs limit
    """
    if not is_aggressive_mode_enabled():
        return False
    
    state = _load_state()
    stats = state.get("stats", {})
    
    # Limit to 10 extra analytics runs per day
    MAX_EXTRA_ANALYTICS = 10
    today_runs = stats.get("extra_analytics_runs", 0)
    
    return today_runs < MAX_EXTRA_ANALYTICS


def should_generate_research_concepts() -> bool:
    """
    Check if we should generate research video concepts.
    
    Research concepts are generated to:
    - Test new topic ideas without uploading
    - Build a bank of pre-evaluated concepts
    - Learn what performs well
    """
    if not is_aggressive_mode_enabled():
        return False
    
    state = _load_state()
    stats = state.get("stats", {})
    
    # Limit to 20 research concepts per day
    MAX_RESEARCH_CONCEPTS = 20
    today_concepts = stats.get("research_concepts_generated", 0)
    
    return today_concepts < MAX_RESEARCH_CONCEPTS


def should_run_learning_cycle() -> bool:
    """
    Check if we should run an extra self-learning cycle.
    
    Learning cycles analyze past performance and update:
    - Viral patterns
    - Hook effectiveness
    - Topic preferences
    """
    if not is_aggressive_mode_enabled():
        return False
    
    state = _load_state()
    stats = state.get("stats", {})
    
    # Limit to 5 extra learning cycles per day
    MAX_LEARNING_CYCLES = 5
    today_cycles = stats.get("learning_cycles_completed", 0)
    
    return today_cycles < MAX_LEARNING_CYCLES


def get_aggressive_mode_summary() -> str:
    """Get a human-readable summary of aggressive mode status."""
    stats = get_aggressive_mode_stats()
    
    if not stats["enabled"]:
        return "Aggressive Mode: DISABLED"
    
    lines = [
        "=" * 50,
        "AGGRESSIVE MODE: ENABLED",
        "=" * 50,
        f"Surplus Quota: ~{stats['surplus_quota']} calls/day",
        f"Production Reserved: ~{stats['production_reserved']} calls/day",
        "",
        "Today's Aggressive Actions:",
        f"  - Extra Analytics Runs: {stats['stats'].get('extra_analytics_runs', 0)}/10",
        f"  - Research Concepts: {stats['stats'].get('research_concepts_generated', 0)}/20",
        f"  - Learning Cycles: {stats['stats'].get('learning_cycles_completed', 0)}/5",
        f"  - Total Quota Used: {stats['stats'].get('quota_used', 0)}",
        "=" * 50,
    ]
    
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("on", "enable", "1", "true"):
            set_aggressive_mode(True)
        elif cmd in ("off", "disable", "0", "false"):
            set_aggressive_mode(False)
        elif cmd == "status":
            print(get_aggressive_mode_summary())
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python aggressive_mode.py [on|off|status]")
    else:
        print(get_aggressive_mode_summary())
