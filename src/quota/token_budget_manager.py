#!/usr/bin/env python3
"""
ViralShorts Factory - Smart Token Budget Manager v15.0
======================================================

This module provides intelligent token distribution across AI providers:
- Groq: 100,000 TPD (tokens per day) - FAST but limited
- Gemini: 60 RPM (requests per minute), 1M TPD - UNLIMITED but slower
- OpenRouter: Free tier - BACKUP for when others fail

STRATEGY:
1. Track token usage per provider per day
2. Reserve Groq tokens for critical tasks (concept, evaluation)
3. Use Gemini for bulk tasks (regenerations, analysis)
4. Use OpenRouter when others are exhausted
5. Avoid regenerations by making first attempt count

TOKEN BUDGET ALLOCATION (per 3-video batch):
- Groq: 30,000 tokens (10k per video)
  - Concept generation: 3,000 tokens
  - Content evaluation: 5,000 tokens
  - Quality check: 2,000 tokens
- Gemini: Unlimited (use for everything else)
  - Regenerations, trend analysis, metadata

This is AI-DRIVEN and SELF-TUNING!
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_best_gemini_model
except ImportError:
    def get_best_gemini_model(api_key=None):
        return "gemini-2.5-flash"  # Fallback only if import fails

# State directory
STATE_DIR = Path("data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

BUDGET_FILE = STATE_DIR / "token_budget.json"


@dataclass
class ProviderBudget:
    """Token budget for a single provider."""
    name: str
    daily_limit: int
    used_today: int
    reserved: int  # Reserved for critical tasks
    last_reset: str
    calls_today: int
    avg_tokens_per_call: int
    last_429_time: Optional[str] = None
    cooldown_until: Optional[str] = None


class TokenBudgetManager:
    """
    Manages token budgets across all AI providers.
    Ensures we never hit rate limits by smart distribution.
    """
    
    # Provider limits (configurable via environment - no hardcoding)
    # These can be updated when providers change their quotas
    # v16.8: Made configurable - defaults are conservative buffers
    GROQ_DAILY_LIMIT = int(os.environ.get("GROQ_DAILY_LIMIT", 90000))  # 100k with 10k buffer
    GEMINI_RPM_LIMIT = int(os.environ.get("GEMINI_RPM_LIMIT", 50))  # 60 with 10 buffer
    GEMINI_DAILY_LIMIT = int(os.environ.get("GEMINI_DAILY_LIMIT", 900000))  # 1M with 100k buffer
    OPENROUTER_DAILY_LIMIT = int(os.environ.get("OPENROUTER_DAILY_LIMIT", 200000))  # Free tier
    
    # Task token costs (estimated)
    TASK_COSTS = {
        "concept": 3000,      # Stage 1: Video concept
        "content": 5000,      # Stage 2: Generate phrases
        "evaluate": 3000,     # Stage 3: Evaluate and enhance
        "broll": 1500,        # Stage 4: B-roll keywords
        "metadata": 1000,     # Final: Title/description
        "regenerate": 4000,   # Regeneration attempt
        "analysis": 2000,     # Analytics feedback
        "trend": 1500,        # Trend fetching
    }
    
    def __init__(self):
        self.budgets = self._load()
        self._check_daily_reset()
    
    def _load(self) -> Dict[str, ProviderBudget]:
        """Load budget state from disk."""
        try:
            if BUDGET_FILE.exists():
                with open(BUDGET_FILE, 'r') as f:
                    data = json.load(f)
                    return {
                        name: ProviderBudget(**budget)
                        for name, budget in data.items()
                    }
        except Exception as e:
            print(f"[TokenBudget] Load error: {e}")
        
        # Initialize fresh budgets
        now = datetime.now().isoformat()
        return {
            "groq": ProviderBudget(
                name="groq",
                daily_limit=self.GROQ_DAILY_LIMIT,
                used_today=0,
                reserved=30000,  # Reserve for critical tasks
                last_reset=now,
                calls_today=0,
                avg_tokens_per_call=2000
            ),
            "gemini": ProviderBudget(
                name="gemini",
                daily_limit=self.GEMINI_DAILY_LIMIT,
                used_today=0,
                reserved=0,  # Gemini is our workhorse
                last_reset=now,
                calls_today=0,
                avg_tokens_per_call=1500
            ),
            "openrouter": ProviderBudget(
                name="openrouter",
                daily_limit=self.OPENROUTER_DAILY_LIMIT,
                used_today=0,
                reserved=0,
                last_reset=now,
                calls_today=0,
                avg_tokens_per_call=1500
            )
        }
    
    def _save(self):
        """Save budget state to disk."""
        try:
            data = {name: asdict(budget) for name, budget in self.budgets.items()}
            with open(BUDGET_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[TokenBudget] Save error: {e}")
    
    def _check_daily_reset(self):
        """Reset budgets if it's a new day."""
        now = datetime.now()
        for name, budget in self.budgets.items():
            try:
                last_reset = datetime.fromisoformat(budget.last_reset)
                if now.date() > last_reset.date():
                    print(f"[TokenBudget] Resetting {name} budget (new day)")
                    budget.used_today = 0
                    budget.calls_today = 0
                    budget.last_reset = now.isoformat()
                    budget.cooldown_until = None
            except:
                pass
        self._save()
    
    def get_available_tokens(self, provider: str) -> int:
        """Get available tokens for a provider."""
        if provider not in self.budgets:
            return 0
        budget = self.budgets[provider]
        return budget.daily_limit - budget.used_today - budget.reserved
    
    def is_in_cooldown(self, provider: str) -> bool:
        """Check if provider is in cooldown from 429."""
        if provider not in self.budgets:
            return False
        budget = self.budgets[provider]
        if not budget.cooldown_until:
            return False
        try:
            cooldown = datetime.fromisoformat(budget.cooldown_until)
            return datetime.now() < cooldown
        except:
            return False
    
    def record_429(self, provider: str, retry_seconds: int = 60):
        """Record a 429 error and set cooldown."""
        if provider in self.budgets:
            now = datetime.now()
            self.budgets[provider].last_429_time = now.isoformat()
            self.budgets[provider].cooldown_until = (
                now + timedelta(seconds=retry_seconds)
            ).isoformat()
            self._save()
            print(f"[TokenBudget] {provider} in cooldown for {retry_seconds}s")
    
    def record_usage(self, provider: str, tokens: int):
        """Record token usage."""
        if provider in self.budgets:
            self.budgets[provider].used_today += tokens
            self.budgets[provider].calls_today += 1
            # Update running average
            calls = self.budgets[provider].calls_today
            avg = self.budgets[provider].avg_tokens_per_call
            self.budgets[provider].avg_tokens_per_call = int(
                (avg * (calls - 1) + tokens) / calls
            )
            self._save()
    
    def choose_provider(self, task: str, prefer_quality: bool = True) -> str:
        """
        Choose the best provider for a task based on budget and priority.
        
        Args:
            task: Type of task (concept, content, evaluate, etc.)
            prefer_quality: If True, prefer Groq for quality tasks
        
        Returns:
            Provider name: "groq", "gemini", or "openrouter"
        """
        task_cost = self.TASK_COSTS.get(task, 2000)
        
        # v17.9.7: GROQ FIRST - Gemini FREE tier has strict per-minute limits (20 req/min)
        # Groq has more generous limits and faster response times
        # Use Gemini as backup to preserve its limited quota across 6 daily runs
        
        # Check each provider
        groq_available = (
            self.get_available_tokens("groq") >= task_cost and
            not self.is_in_cooldown("groq")
        )
        gemini_available = (
            self.get_available_tokens("gemini") >= task_cost and
            not self.is_in_cooldown("gemini")
        )
        openrouter_available = (
            self.get_available_tokens("openrouter") >= task_cost and
            not self.is_in_cooldown("openrouter")
        )
        huggingface_available = not self.is_in_cooldown("huggingface")
        
        # v17.9.11: Decision logic - GEMINI FIRST (higher request quota!)
        # Gemini 1.5-flash: 1,500 requests/day
        # Groq: 100K tokens/day (but each call uses ~500-1000 tokens)
        if gemini_available:
            # Gemini is PRIMARY - 1,500+ requests/day!
            return "gemini"
        elif groq_available:
            # Groq is SECONDARY - good but token-limited (100K/day)
            return "groq"
        elif openrouter_available:
            # OpenRouter as tertiary
            return "openrouter"
        elif huggingface_available:
            # HuggingFace as last resort
            return "huggingface"
        else:
            # All providers exhausted - try Groq anyway (might recover faster)
            print("[TokenBudget] WARNING: All providers exhausted, trying Groq")
            return "groq"
    
    def get_status(self) -> Dict:
        """Get current budget status."""
        return {
            name: {
                "available": self.get_available_tokens(name),
                "used": budget.used_today,
                "limit": budget.daily_limit,
                "calls": budget.calls_today,
                "in_cooldown": self.is_in_cooldown(name)
            }
            for name, budget in self.budgets.items()
        }
    
    def print_status(self):
        """Print current budget status."""
        print("\n" + "="*60)
        print("TOKEN BUDGET STATUS")
        print("="*60)
        for name, status in self.get_status().items():
            pct = (status["used"] / status["limit"]) * 100 if status["limit"] > 0 else 0
            cooldown = " [COOLDOWN]" if status["in_cooldown"] else ""
            print(f"  {name.upper():12} | {status['used']:,}/{status['limit']:,} ({pct:.1f}%) | {status['calls']} calls{cooldown}")
        print("="*60 + "\n")
    
    def estimate_videos_remaining(self) -> int:
        """Estimate how many videos we can generate today."""
        tokens_per_video = sum([
            self.TASK_COSTS["concept"],
            self.TASK_COSTS["content"],
            self.TASK_COSTS["evaluate"],
            self.TASK_COSTS["broll"],
            self.TASK_COSTS["metadata"],
        ])  # ~13,500 tokens per video
        
        # Sum available tokens across all providers
        total_available = sum(
            self.get_available_tokens(p) for p in self.budgets.keys()
        )
        
        return total_available // tokens_per_video


# Singleton instance
_budget_manager = None

def get_budget_manager() -> TokenBudgetManager:
    """Get the singleton budget manager."""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = TokenBudgetManager()
    return _budget_manager


def print_quota_health_report():
    """Print a quick quota health report for workflow logs.
    v17.6: Added for better monitoring in workflow logs.
    """
    mgr = get_budget_manager()
    print("\n" + "="*50)
    print("QUOTA HEALTH REPORT - v17.6")
    print("="*50)
    
    for provider in ["gemini", "groq", "openrouter"]:
        available = mgr.get_available_tokens(provider)
        budget = mgr.budgets.get(provider)
        if budget:
            used_pct = (budget.used_today / budget.daily_limit * 100) if budget.daily_limit > 0 else 0
            status = "OK" if available > 10000 else "LOW" if available > 0 else "EXHAUSTED"
            print(f"  {provider.upper()}: {available:,} available ({used_pct:.1f}% used) [{status}]")
    
    videos_remaining = mgr.get_videos_remaining()
    print(f"\n  Videos Possible: {videos_remaining}")
    print("="*50 + "\n")


# =============================================================================
# SMART AI CALLER WITH BUDGET AWARENESS
# =============================================================================

class BudgetAwareAICaller:
    """
    AI caller that respects token budgets and optimizes provider selection.
    
    Usage:
        caller = BudgetAwareAICaller()
        response = caller.call("concept", prompt, max_tokens=2000)
    """
    
    def __init__(self):
        self.budget = get_budget_manager()
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        
        # Initialize clients
        self.groq_client = None
        self.gemini_model = None
        
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                print(f"[BudgetAI] Groq init error: {e}")
        
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                # DYNAMIC MODEL SELECTION - no hardcoded model names
                model_name = get_best_gemini_model(self.gemini_key)
                self.gemini_model = genai.GenerativeModel(f'models/{model_name}')
            except Exception as e:
                print(f"[BudgetAI] Gemini init error: {e}")
    
    def call(self, task: str, prompt: str, max_tokens: int = 2000, 
             temperature: float = 0.9, prefer_quality: bool = True) -> str:
        """
        Call AI with budget-aware provider selection.
        
        Args:
            task: Task type for budget tracking
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            temperature: Creativity level
            prefer_quality: Whether to prefer Groq for quality
        
        Returns:
            AI response string
        """
        import time
        import re
        
        # Choose provider based on budget
        provider = self.budget.choose_provider(task, prefer_quality)
        print(f"[BudgetAI] Task '{task}' -> Provider: {provider}")
        
        # Rate limit protection
        time.sleep(get_smart_delay("default", "groq") if "get_smart_delay" in dir() else 0.5)
        
        def extract_retry_delay(error_msg: str) -> int:
            match = re.search(r'retry in (\d+(?:\.\d+)?)', str(error_msg), re.IGNORECASE)
            if match:
                return int(float(match.group(1))) + 2
            return 60
        
        # Try the chosen provider
        # v16.8: DYNAMIC MODEL - No hardcoded model names
        if provider == "groq" and self.groq_client:
            # Get dynamic model list
            try:
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                groq_models = optimizer.get_groq_models()
            except:
                groq_models = ["llama-3.3-70b-versatile"]  # Last resort fallback
            
            for model_name in groq_models:
                try:
                    response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    result = response.choices[0].message.content
                    self.budget.record_usage("groq", max_tokens)
                    return result
                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str:
                        print(f"[BudgetAI] Groq {model_name} 429 - trying next...")
                        continue
                    elif '404' in error_str:
                        print(f"[BudgetAI] Groq {model_name} not found - trying next...")
                        continue
                    else:
                        print(f"[BudgetAI] Groq {model_name} error: {e}")
                        continue
            
            # All Groq models failed
            self.budget.record_429("groq", 60)
            print(f"[BudgetAI] All Groq models exhausted - falling back")
        
        if provider == "gemini" or provider == "groq":  # Fallback from Groq
            if self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    self.budget.record_usage("gemini", max_tokens)
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str:
                        delay = extract_retry_delay(error_str)
                        self.budget.record_429("gemini", delay)
                        print(f"[BudgetAI] Gemini 429 - falling back")
                    else:
                        print(f"[BudgetAI] Gemini error: {e}")
        
        # OpenRouter fallback
        if self.openrouter_key:
            try:
                import requests
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "HTTP-Referer": "https://github.com/viralshorts-factory",
                        "X-Title": "ViralShorts Factory"
                    },
                    json={
                        "model": "meta-llama/llama-3.2-3b-instruct:free",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        self.budget.record_usage("openrouter", max_tokens)
                        return content
            except Exception as e:
                print(f"[BudgetAI] OpenRouter error: {e}")
        
        return ""


# =============================================================================
# FIRST-ATTEMPT QUALITY MAXIMIZER
# =============================================================================

class FirstAttemptMaximizer:
    """
    Ensures first video generation attempt is high quality to avoid regenerations.
    Regenerations waste tokens - we want 8+/10 on FIRST try!
    
    Strategy:
    1. Use best prompts that have historically scored 8+
    2. Inject proven patterns into generation
    3. Pre-validate concept before full generation
    """
    
    # Own file: quality_history.json is used by ai_content_quality_checker with a different schema
    HISTORY_FILE = STATE_DIR / "first_attempt_history.json"

    def __init__(self):
        self.history = self._load()

    def _load(self) -> Dict:
        history = {
            "high_score_patterns": [],  # Patterns that scored 8+
            "low_score_patterns": [],   # Patterns that scored <6
            "avg_first_attempt_score": 5.0,
            "regeneration_rate": 0.5,
            "total_videos": 0
        }
        try:
            if self.HISTORY_FILE.exists():
                with open(self.HISTORY_FILE, 'r') as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    history.update({k: v for k, v in loaded.items() if v is not None})
        except:
            pass
        return history
    
    def _save(self):
        try:
            with open(self.HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass
    
    def get_success_boost(self) -> str:
        """Get prompt boost based on successful patterns."""
        if not self.history["high_score_patterns"]:
            return """
PROVEN SUCCESS PATTERNS (use these!):
- Start with a SHOCKING claim or question
- Use SPECIFIC numbers that sound believable ($500, 80%, 3 steps)
- Deliver REAL VALUE in the middle (not fluff)
- End with engagement bait (Comment, Like, Save)
- Keep total length under 60 words for 20-second video
- Use CONVERSATIONAL tone, not robotic
"""
        
        # Build from actual high-scoring patterns
        patterns = self.history["high_score_patterns"][-10:]  # Last 10 successes
        boost = "PROVEN SUCCESS PATTERNS FROM OUR BEST VIDEOS:\n"
        for p in patterns[:5]:
            boost += f"- {p['pattern']}\n"
        return boost
    
    def get_failure_warnings(self) -> str:
        """Get warnings based on failed patterns."""
        if not self.history["low_score_patterns"]:
            return """
AVOID THESE MISTAKES (historically failed):
- Awkward numbers like $3333, 47.3%, 1847 (use round numbers!)
- Vague promises without delivery
- Too many sentences (more than 5)
- Generic AI-sounding phrases
- Missing hook in first sentence
- No call-to-action at end
"""
        
        patterns = self.history["low_score_patterns"][-10:]
        warning = "AVOID THESE (caused low scores in our videos):\n"
        for p in patterns[:5]:
            warning += f"- {p['pattern']}\n"
        return warning
    
    def record_result(self, score: int, category: str, hook: str, was_regeneration: bool):
        """Record video result for learning."""
        pattern = {
            "category": category,
            "hook_style": hook[:50] if hook else "",
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        if score >= 8:
            pattern["pattern"] = f"{category}: {hook[:30]}..."
            self.history["high_score_patterns"].append(pattern)
            # Keep only last 50
            self.history["high_score_patterns"] = self.history["high_score_patterns"][-50:]
        elif score < 6:
            pattern["pattern"] = f"FAILED {category}: {hook[:30]}..."
            self.history["low_score_patterns"].append(pattern)
            self.history["low_score_patterns"] = self.history["low_score_patterns"][-50:]
        
        # Update stats
        self.history["total_videos"] += 1
        if not was_regeneration:
            total = self.history["total_videos"]
            old_avg = self.history["avg_first_attempt_score"]
            self.history["avg_first_attempt_score"] = (
                (old_avg * (total - 1) + score) / total
            )
        else:
            # Track regeneration rate
            regen_count = len([p for p in self.history["low_score_patterns"] if p.get("score", 0) < 6])
            self.history["regeneration_rate"] = regen_count / max(1, self.history["total_videos"])
        
        self._save()
    
    def get_quality_boost_prompt(self) -> str:
        """Get the full quality boost for prompts."""
        return f"""
=== FIRST-ATTEMPT QUALITY MAXIMIZER ===
Our average first-attempt score: {self.history['avg_first_attempt_score']:.1f}/10
Regeneration rate: {self.history['regeneration_rate']*100:.1f}% (GOAL: <10%)

{self.get_success_boost()}

{self.get_failure_warnings()}

YOUR GOAL: Score 8+/10 on FIRST attempt! No regenerations!
============================================
"""


# Singletons
_first_attempt_maximizer = None

def get_first_attempt_maximizer() -> FirstAttemptMaximizer:
    global _first_attempt_maximizer
    if _first_attempt_maximizer is None:
        _first_attempt_maximizer = FirstAttemptMaximizer()
    return _first_attempt_maximizer


if __name__ == "__main__":
    # Test the budget manager
    budget = get_budget_manager()
    budget.print_status()
    
    print(f"Estimated videos remaining today: {budget.estimate_videos_remaining()}")
    
    # Test provider selection
    for task in ["concept", "content", "regenerate", "analysis"]:
        provider = budget.choose_provider(task)
        print(f"Task '{task}' -> Provider: {provider}")

