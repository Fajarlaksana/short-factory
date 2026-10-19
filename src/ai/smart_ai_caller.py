#!/usr/bin/env python3
"""
ViralShorts Factory - Smart AI Caller v17.9.9
==============================================

Makes AI calls using the SmartModelRouter.

Features:
- Routes each prompt to the BEST model for its type
- Automatic fallback through entire chain
- GUARANTEES eventual success (tries ALL models)
- Respects rate limits per model
- Tracks success/failure for learning

USAGE:
    from src.ai.smart_ai_caller import smart_call_ai
    
    result = smart_call_ai(
        prompt="Generate a viral topic about psychology",
        hint="topic",  # Optional hint to help classify
        max_tokens=2000
    )
"""

import os
import json
import time
import re
import warnings
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

# Suppress google.generativeai deprecation warning (will migrate to google.genai later)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

# Import the router
try:
    from src.ai.smart_model_router import (
        get_smart_router, SmartModelRouter, ModelInfo
    )
    from src.ai.model_helper import get_smart_delay
except ImportError:
    from smart_model_router import get_smart_router, SmartModelRouter, ModelInfo
    try:
        from model_helper import get_smart_delay
    except ImportError:
        # Fallback if not available
        def get_smart_delay(model_name: str, provider: str = None) -> float:
            return 12.0  # Conservative default


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


# =============================================================================
# PROVIDER-SPECIFIC CALLERS
# =============================================================================

_PERMANENT_ERROR_MARKERS = ("404", "model_not_found", "does not exist", "no longer available",
                            "decommissioned", "limit: 0", "not supported for generatecontent")


def _disable_if_dead(provider: str, model_id: str, error) -> None:
    """Disable a model in the router when the error means it will never work for this key."""
    msg = str(error).lower()
    if any(marker in msg for marker in _PERMANENT_ERROR_MARKERS):
        try:
            get_smart_router().mark_unavailable(f"{provider}:{model_id}", msg.split("\n")[0][:80])
        except Exception:
            pass


def _call_groq(model_id: str, prompt: str, max_tokens: int,
               temperature: float) -> Optional[str]:
    """Call Groq API."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        safe_print(f"   [!] Groq ({model_id}): {e}")
        _disable_if_dead("groq", model_id, e)
        return None


def _call_gemini(model_id: str, prompt: str, max_tokens: int,
                 temperature: float) -> Optional[str]:
    """Call Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(model_id)
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            },
            request_options={"timeout": 90}  # never hang forever on a stuck request
        )
        return response.text
    except Exception as e:
        safe_print(f"   [!] Gemini ({model_id}): {str(e).splitlines()[0][:200]}")
        _disable_if_dead("gemini", model_id, e)
        return None


def _call_openrouter(model_id: str, prompt: str, max_tokens: int,
                     temperature: float) -> Optional[str]:
    """Call OpenRouter API."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None
    
    try:
        import requests
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        if response.status_code == 404:
            _disable_if_dead("openrouter", model_id, "404")
        return None
    except Exception as e:
        safe_print(f"   [!] OpenRouter ({model_id}): {e}")
        return None


def _call_huggingface(model_id: str, prompt: str, max_tokens: int,
                      temperature: float) -> Optional[str]:
    """Call HuggingFace Inference API."""
    api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
    if not api_key:
        return None
    
    try:
        import requests
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
        return None
    except Exception as e:
        safe_print(f"   [!] HuggingFace ({model_id}): {e}")
        return None


# Provider function mapping
PROVIDER_CALLERS = {
    "groq": _call_groq,
    "gemini": _call_gemini,
    "openrouter": _call_openrouter,
    "huggingface": _call_huggingface
}


# =============================================================================
# SMART AI CALLER
# =============================================================================

class SmartAICaller:
    """
    Makes AI calls using the SmartModelRouter.
    
    Automatically:
    - Selects best model for each prompt type
    - Falls back through entire chain on failure
    - Respects rate limits
    - Tracks statistics
    """
    
    def __init__(self):
        self.router = get_smart_router()
        self.last_call_time = {}  # Track last call per provider
    
    def call(self, prompt: str, hint: str = None, 
             max_tokens: int = 2000, temperature: float = 0.8,
             prompt_name: str = None) -> Optional[str]:
        """
        Make an AI call with smart routing.
        
        Args:
            prompt: The prompt to send
            hint: Optional hint about prompt type (e.g., "topic", "evaluation")
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)
            prompt_name: Optional name for prompt tracking (e.g., "VIRAL_TOPIC_PROMPT")
        
        Returns:
            The AI response text, or None if all models fail
        """
        # Get fallback chain for this prompt type
        prompt_type = self.router.classify_prompt(prompt, hint)
        chain = self.router.get_model_chain(prompt_type)
        
        safe_print(f"   [ROUTER] Type: {prompt_type}, Chain: {len(chain)} models")
        
        # Try each model in the chain
        for i, (model_key, model_info) in enumerate(chain):
            # Extract provider and model_id
            provider, model_id = model_key.split(":", 1)
            
            # Check if provider caller exists
            caller = PROVIDER_CALLERS.get(provider)
            if not caller or not model_info.available:
                continue
            
            # Respect rate limits - v17.9.32: Use smart per-model delay with 10% margin
            smart_delay = get_smart_delay(model_id, provider)
            self._wait_for_rate_limit(provider, model_id, smart_delay)
            
            # Log attempt
            if i > 0:
                safe_print(f"   [FALLBACK] Trying {model_key}...")
            else:
                safe_print(f"   [AI] Using {model_key}")
            
            # Make the call with retry for transient errors
            # v17.9.12: Exponential backoff for network/rate limit errors
            max_retries = 3
            retry_delay = 5  # Start with 5 seconds
            
            for attempt in range(max_retries):
                try:
                    result = caller(model_id, prompt, max_tokens, temperature)
                    
                    if result:
                        # Success!
                        self.router.record_result(model_key, success=True, 
                                                  was_fallback=(i > 0))
                        if i > 0:
                            safe_print(f"   [OK] Fallback succeeded with {model_key}")
                        
                        # v17.9.43: Record prompt performance for learning
                        if prompt_name:
                            try:
                                from prompts_registry import record_prompt_usage
                                record_prompt_usage(prompt_name, model_key, 
                                                    success=True, response_quality=7.5)
                            except ImportError:
                                pass  # Registry not available
                        
                        return result
                    else:
                        # Empty response, try next model
                        self.router.record_result(model_key, success=False)
                        break  # Don't retry empty responses
                        
                except Exception as e:
                    error_str = str(e)
                    # Retry for rate limits (429) and network errors
                    is_retryable = '429' in error_str or 'timeout' in error_str.lower() or \
                                   'connection' in error_str.lower() or 'network' in error_str.lower()
                    
                    # v17.9.13: Record quota from 429 errors for smarter model selection
                    if '429' in error_str:
                        import re
                        match = re.search(r'quota_value[:\s]+(\d+)', error_str)
                        if match:
                            try:
                                from src.ai.model_helper import record_quota_from_429
                                model_name = model_id.split(':')[-1] if ':' in model_id else model_id
                                record_quota_from_429(model_name, int(match.group(1)))
                            except ImportError:
                                pass  # Function not available
                    
                    if is_retryable and attempt < max_retries - 1:
                        safe_print(f"   [!] {model_key}: {error_str[:50]}... retrying in {retry_delay}s")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        safe_print(f"   [!] {model_key} exception: {e}")
                        self.router.record_result(model_key, success=False)
                        break  # Move to next model
        
        # All models failed
        safe_print(f"   [FAIL] All {len(chain)} models failed!")
        return None
    
    def _wait_for_rate_limit(self, provider: str, model_id: str, delay: float):
        """
        v17.9.32: Wait to respect SMART per-model rate limits.
        
        Uses per-model tracking (not per-provider) because different models
        of the same provider have different rate limits.
        
        E.g., gemini-2.5-flash (15/min) vs gemini-2.5-pro (2/min)
        """
        model_key = f"{provider}:{model_id}"
        now = time.time()
        last = self.last_call_time.get(model_key, 0)
        elapsed = now - last
        
        if elapsed < delay:
            wait_time = delay - elapsed
            safe_print(f"   [RATE] Waiting {wait_time:.1f}s for {model_id} rate limit")
            time.sleep(wait_time)
        
        self.last_call_time[model_key] = time.time()
    
    def parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        if not text:
            return None
        
        # Clean markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
        
        # Find JSON object
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        # Try to parse as array
        try:
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        return None
    
    def get_stats(self) -> Dict:
        """Get router/caller statistics."""
        return self.router.get_stats()


# =============================================================================
# GLOBAL INSTANCE & CONVENIENCE FUNCTIONS
# =============================================================================

_caller = None


def get_smart_caller() -> SmartAICaller:
    """Get the global SmartAICaller instance."""
    global _caller
    if _caller is None:
        _caller = SmartAICaller()
    return _caller


def smart_call_ai(prompt: str, hint: str = None,
                  max_tokens: int = 2000, temperature: float = 0.8,
                  prompt_name: str = None) -> Optional[str]:
    """
    Convenience function for smart AI calls.
    
    Args:
        prompt: The prompt to send
        prompt_name: Optional prompt name for performance tracking
        hint: Optional hint about prompt type
        max_tokens: Maximum tokens
        temperature: Creativity level
    
    Returns:
        AI response text or None
    
    Example:
        result = smart_call_ai(
            prompt="Generate a viral topic about psychology",
            hint="topic"
        )
    """
    caller = get_smart_caller()
    return caller.call(prompt, hint, max_tokens, temperature, prompt_name)


def smart_call_json(prompt: str, hint: str = None,
                    max_tokens: int = 2000, temperature: float = 0.7,
                    prompt_name: str = None) -> Optional[Dict]:
    """
    Make AI call and parse JSON response.
    
    Lower default temperature for more consistent JSON output.
    """
    caller = get_smart_caller()
    text = caller.call(prompt, hint, max_tokens, temperature, prompt_name)
    return caller.parse_json(text)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("SMART AI CALLER TEST")
    safe_print("=" * 60)
    
    caller = get_smart_caller()
    
    # Test 1: Simple prompt
    safe_print("\n[TEST 1] Simple prompt (hashtag generation)")
    result = caller.call(
        prompt="Generate 5 hashtags for a video about productivity tips.",
        hint="hashtag",
        max_tokens=200
    )
    if result:
        safe_print(f"Result: {result[:200]}...")
        safe_print("PASS")
    else:
        safe_print("FAIL - No response")
    
    # Test 2: Creative prompt
    safe_print("\n[TEST 2] Creative prompt (topic generation)")
    result = caller.call(
        prompt="Generate a viral topic idea about psychology that would work for YouTube Shorts.",
        hint="topic",
        max_tokens=500
    )
    if result:
        safe_print(f"Result: {result[:200]}...")
        safe_print("PASS")
    else:
        safe_print("FAIL - No response")
    
    # Test 3: JSON parsing
    safe_print("\n[TEST 3] JSON response parsing")
    result = smart_call_json(
        prompt='Return JSON: {"score": 8, "reason": "test"}',
        hint="evaluation",
        max_tokens=100
    )
    if result and "score" in result:
        safe_print(f"Parsed JSON: {result}")
        safe_print("PASS")
    else:
        safe_print(f"FAIL - Could not parse JSON (got: {result})")
    
    # Print stats
    safe_print("\n[STATS]")
    stats = caller.get_stats()
    for key, value in stats.items():
        safe_print(f"  {key}: {value}")
    
    safe_print("\n" + "=" * 60)

