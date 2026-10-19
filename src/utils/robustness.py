"""
Robustness Utilities
Smart retry logic, validation, and self-healing capabilities.
"""
import time
import random
import functools
from typing import Callable, Any, Optional
import hashlib
import json
from pathlib import Path


def retry_with_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential: Use exponential backoff (2^n)
        jitter: Add random jitter to prevent thundering herd
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        print(f"❌ {func.__name__} failed after {max_retries} attempts")
                        raise
                    
                    # Calculate delay
                    if exponential:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay
                    
                    # Add jitter (0-50% of delay)
                    if jitter:
                        delay += random.uniform(0, delay * 0.5)
                    
                    print(f"⚠️ {func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                          f"retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator


def rate_limited(calls_per_minute: int = 30):
    """
    Decorator to rate limit function calls.
    Prevents hitting API rate limits.
    """
    min_interval = 60.0 / calls_per_minute
    last_call_time = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_call_time[0]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
            
            last_call_time[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ContentValidator:
    """Validates generated content before publishing."""
    
    # List of forbidden words/patterns
    FORBIDDEN_PATTERNS = [
        # Add any patterns to filter out
    ]
    
    @staticmethod
    def validate_wyr_question(question: dict) -> bool:
        """Validate a Would You Rather question."""
        required_keys = ["option_a", "option_b", "percentage_a"]
        
        # Check required keys
        if not all(key in question for key in required_keys):
            print("❌ Missing required keys in question")
            return False
        
        # Check option lengths
        if len(question["option_a"]) < 10 or len(question["option_b"]) < 10:
            print("❌ Options too short")
            return False
        
        if len(question["option_a"]) > 200 or len(question["option_b"]) > 200:
            print("❌ Options too long")
            return False
        
        # Check percentage
        percentage = question.get("percentage_a", 0)
        if not (1 <= percentage <= 99):
            print("❌ Invalid percentage")
            return False
        
        # Check for forbidden content
        text = f"{question['option_a']} {question['option_b']}".lower()
        for pattern in ContentValidator.FORBIDDEN_PATTERNS:
            if pattern.lower() in text:
                print(f"❌ Forbidden content detected")
                return False
        
        return True
    
    @staticmethod
    def validate_video_file(path: str) -> bool:
        """Validate a video file exists and has content."""
        p = Path(path)
        if not p.exists():
            print(f"❌ Video file not found: {path}")
            return False
        
        # Check minimum file size (100KB)
        if p.stat().st_size < 100_000:
            print(f"❌ Video file too small: {p.stat().st_size} bytes")
            return False
        
        return True


class ContentDeduplicator:
    """Prevents duplicate content from being published."""
    
    def __init__(self, cache_file: str = ".content_hashes.json"):
        self.cache_file = Path(cache_file)
        self.hashes = self._load_cache()
    
    def _load_cache(self) -> set:
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text())
                return set(data.get("hashes", []))
            except:
                pass
        return set()
    
    def _save_cache(self):
        # Keep only last 10000 hashes
        hashes_list = list(self.hashes)[-10000:]
        self.hashes = set(hashes_list)
        self.cache_file.write_text(json.dumps({"hashes": hashes_list}))
    
    def is_duplicate(self, content: str) -> bool:
        """Check if content has been seen before."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return content_hash in self.hashes
    
    def mark_as_seen(self, content: str):
        """Mark content as seen."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        self.hashes.add(content_hash)
        self._save_cache()


class HealthChecker:
    """Self-healing health checks for the system."""
    
    @staticmethod
    def check_dependencies() -> dict:
        """Check if all required dependencies are available."""
        results = {}
        
        dependencies = [
            ("moviepy", "moviepy.editor"),
            ("edge_tts", "edge_tts"),
            ("groq", "groq"),
            ("google-auth", "google.oauth2.credentials"),
        ]
        
        for name, import_path in dependencies:
            try:
                __import__(import_path)
                results[name] = "✅"
            except ImportError:
                results[name] = "❌"
        
        return results
    
    @staticmethod
    def check_api_connectivity() -> dict:
        """Check API connectivity."""
        import requests
        
        results = {}
        apis = [
            ("YouTube API", "https://www.googleapis.com/youtube/v3/videos"),
            ("Groq API", "https://api.groq.com/openai/v1/models"),
            ("HuggingFace", "https://huggingface.co/api/models"),
        ]
        
        for name, url in apis:
            try:
                response = requests.head(url, timeout=5)
                results[name] = "✅" if response.status_code < 500 else "⚠️"
            except:
                results[name] = "❌"
        
        return results


# Global instances
deduplicator = ContentDeduplicator()
validator = ContentValidator()


if __name__ == "__main__":
    # Self-test
    print("🔍 Running health checks...")
    
    print("\n📦 Dependencies:")
    for dep, status in HealthChecker.check_dependencies().items():
        print(f"  {status} {dep}")
    
    print("\n🌐 API Connectivity:")
    for api, status in HealthChecker.check_api_connectivity().items():
        print(f"  {status} {api}")
    
    print("\n✅ Robustness module loaded successfully")











