#!/usr/bin/env python3
"""
Error Logger for ViralShorts Factory v17.7.6
=============================================

Centralized error logging that:
- Logs errors to file for post-mortem analysis
- Tracks error patterns to learn from failures
- Provides error statistics for debugging
"""

import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Create logs directory
LOGS_DIR = Path("./data/logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

ERROR_LOG_FILE = LOGS_DIR / "error_log.json"

class ErrorLogger:
    """Centralized error logging with pattern tracking."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.errors = self._load_errors()
        self.session_errors = []
    
    def _load_errors(self) -> Dict:
        """Load existing error log."""
        try:
            if ERROR_LOG_FILE.exists():
                with open(ERROR_LOG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "errors": [],
            "error_counts": {},
            "last_session": None,
            "total_errors": 0
        }
    
    def _save_errors(self):
        """Save error log to file."""
        try:
            # Keep only last 500 errors
            self.errors["errors"] = self.errors["errors"][-500:]
            with open(ERROR_LOG_FILE, 'w') as f:
                json.dump(self.errors, f, indent=2)
        except:
            pass  # Don't fail on logging failure
    
    def log_error(
        self, 
        error: Exception, 
        context: str = "",
        component: str = "unknown",
        severity: str = "error",  # error, warning, critical
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """Log an error with context and metadata."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "severity": severity,
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc() if severity in ["error", "critical"] else None,
            "extra_data": extra_data
        }
        
        self.errors["errors"].append(error_entry)
        self.errors["total_errors"] += 1
        self.session_errors.append(error_entry)
        
        # Track error counts by type
        error_key = f"{component}:{type(error).__name__}"
        self.errors["error_counts"][error_key] = self.errors["error_counts"].get(error_key, 0) + 1
        
        # Save every 5 errors
        if len(self.session_errors) % 5 == 0:
            self._save_errors()
        
        return error_entry
    
    def log_api_failure(
        self, 
        provider: str, 
        status_code: int, 
        response_text: str = "",
        endpoint: str = ""
    ):
        """Log an API failure with details."""
        self.log_error(
            error=Exception(f"API {status_code}: {response_text[:200]}"),
            context=f"API call to {endpoint}",
            component=f"api_{provider}",
            severity="error",
            extra_data={
                "provider": provider,
                "status_code": status_code,
                "endpoint": endpoint
            }
        )
    
    def get_session_summary(self) -> Dict:
        """Get summary of errors in this session."""
        if not self.session_errors:
            return {"status": "clean", "error_count": 0}
        
        counts = {}
        for e in self.session_errors:
            key = e["component"]
            counts[key] = counts.get(key, 0) + 1
        
        return {
            "status": "has_errors",
            "error_count": len(self.session_errors),
            "by_component": counts,
            "critical_count": sum(1 for e in self.session_errors if e["severity"] == "critical")
        }
    
    def get_frequent_errors(self, top_n: int = 5) -> list:
        """Get the most frequent error types."""
        sorted_errors = sorted(
            self.errors["error_counts"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_errors[:top_n]
    
    def finalize_session(self):
        """Called at end of session to save all logs."""
        self.errors["last_session"] = datetime.now().isoformat()
        self._save_errors()


# Singleton getter
_error_logger = None

def get_error_logger() -> ErrorLogger:
    """Get the singleton error logger."""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


def log_error(error: Exception, context: str = "", component: str = "unknown"):
    """Convenience function to log an error."""
    get_error_logger().log_error(error, context, component)


if __name__ == "__main__":
    # Test the error logger
    logger = get_error_logger()
    
    try:
        raise ValueError("Test error message")
    except Exception as e:
        logger.log_error(e, "Testing error logger", "test_component")
    
    try:
        raise KeyError("Missing key 'test'")
    except Exception as e:
        logger.log_error(e, "Another test", "test_component")
    
    logger.log_api_failure("gemini", 429, "Rate limit exceeded", "/v1/generate")
    
    print("Session summary:", logger.get_session_summary())
    print("Frequent errors:", logger.get_frequent_errors())
    
    logger.finalize_session()
    print("Error log saved to:", ERROR_LOG_FILE)

