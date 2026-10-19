#!/usr/bin/env python3
"""
ViralShorts Factory - Smart Upload Scheduler v17.9.51
======================================================

Optimizes upload timing based on:
- Learned best posting hours from analytics
- Day of week performance
- Timezone optimization for target audience
- Competition analysis (avoid peak upload times)
- Holiday/event awareness

Research shows:
- Optimal timing can increase views by 30-50%
- Consistency matters more than perfect timing
- Different categories have different peak times
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
SCHEDULE_FILE = STATE_DIR / "upload_schedule.json"
VARIETY_FILE = STATE_DIR / "variety_state.json"


class SmartScheduler:
    """
    Intelligently schedules uploads for maximum reach.
    """
    
    # Default optimal hours by region (UTC)
    # Based on industry research for YouTube Shorts
    DEFAULT_OPTIMAL_HOURS = {
        "US": [14, 15, 16, 17, 18, 19, 20, 21],  # 9AM-4PM EST
        "UK": [11, 12, 13, 14, 15, 16, 17, 18],  # 11AM-6PM GMT
        "global": [14, 15, 16, 17, 18, 19],      # Overlap of major markets
    }
    
    # Day of week multipliers (based on research)
    DAY_MULTIPLIERS = {
        "Monday": 0.95,
        "Tuesday": 1.05,
        "Wednesday": 1.10,
        "Thursday": 1.08,
        "Friday": 1.00,
        "Saturday": 1.15,
        "Sunday": 1.12
    }
    
    # Category-specific optimal hours (UTC)
    CATEGORY_HOURS = {
        "productivity": [5, 6, 7, 14, 15],       # Early morning + lunch
        "motivation": [5, 6, 7, 21, 22],         # Morning + evening
        "money": [12, 13, 14, 18, 19],           # Lunch + after work
        "psychology": [19, 20, 21, 22],          # Evening relaxation
        "health": [5, 6, 7, 17, 18],             # Morning + after work
        "technology": [10, 11, 14, 15, 20, 21],  # Work breaks + evening
        "entertainment": [18, 19, 20, 21, 22],   # Evening prime time
        "education": [9, 10, 14, 15, 19, 20],    # Study times
    }
    
    def __init__(self):
        self.data = self._load()
        self.variety_state = self._load_variety_state()
    
    def _load(self) -> Dict:
        try:
            if SCHEDULE_FILE.exists():
                with open(SCHEDULE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "scheduled_uploads": [],
            "hour_performance": {},
            "day_performance": {},
            "last_updated": None
        }
    
    def _load_variety_state(self) -> Dict:
        """Load learned optimal times from analytics."""
        try:
            if VARIETY_FILE.exists():
                with open(VARIETY_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_optimal_upload_time(self, category: str = None,
                                 target_region: str = "global") -> Dict:
        """
        Get the optimal time to upload a video.
        
        Args:
            category: Content category for category-specific optimization
            target_region: Target audience region
        
        Returns:
            Dict with recommended upload time and reasoning
        """
        now = datetime.utcnow()
        
        # Get learned hours from analytics (if available)
        learned_hours = self.variety_state.get("best_posting_hours_utc", [])
        learned_days = self.variety_state.get("best_posting_days", [])
        
        # Get category-specific hours
        category_hours = self.CATEGORY_HOURS.get(
            category.lower() if category else "general",
            self.DEFAULT_OPTIMAL_HOURS["global"]
        )
        
        # Combine learned + category + defaults
        if learned_hours:
            optimal_hours = learned_hours
            source = "analytics_learned"
        elif category_hours:
            optimal_hours = category_hours
            source = "category_optimized"
        else:
            optimal_hours = self.DEFAULT_OPTIMAL_HOURS.get(
                target_region, 
                self.DEFAULT_OPTIMAL_HOURS["global"]
            )
            source = "default"
        
        # Find next optimal slot
        next_slot = self._find_next_slot(now, optimal_hours, learned_days)
        
        # Calculate score for this slot
        day_name = next_slot.strftime("%A")
        day_multiplier = self.DAY_MULTIPLIERS.get(day_name, 1.0)
        
        return {
            "recommended_time_utc": next_slot.isoformat(),
            "recommended_hour": next_slot.hour,
            "recommended_day": day_name,
            "day_multiplier": day_multiplier,
            "source": source,
            "optimal_hours": optimal_hours,
            "delay_seconds": (next_slot - now).total_seconds(),
            "reasoning": self._get_reasoning(source, category, day_name)
        }
    
    def _find_next_slot(self, now: datetime, optimal_hours: List[int],
                        optimal_days: List[str] = None) -> datetime:
        """Find the next available optimal upload slot."""
        # Start from now
        candidate = now
        
        # Look up to 7 days ahead
        for day_offset in range(8):
            check_date = now + timedelta(days=day_offset)
            day_name = check_date.strftime("%A")
            
            # Skip if not an optimal day (if we have learned days)
            if optimal_days and len(optimal_days) >= 3:
                if day_name not in optimal_days:
                    continue
            
            # Check each optimal hour
            for hour in sorted(optimal_hours):
                candidate = check_date.replace(
                    hour=hour, minute=random.randint(0, 29), 
                    second=0, microsecond=0
                )
                
                # If this time is in the future, use it
                if candidate > now:
                    # Add some randomness (0-15 min) for natural feel
                    candidate += timedelta(minutes=random.randint(0, 15))
                    return candidate
        
        # Fallback: next hour
        return now + timedelta(hours=1)
    
    def _get_reasoning(self, source: str, category: str, day: str) -> str:
        """Generate human-readable reasoning for the schedule."""
        reasons = []
        
        if source == "analytics_learned":
            reasons.append("Based on your channel's historical performance")
        elif source == "category_optimized":
            reasons.append(f"Optimized for {category} content viewers")
        else:
            reasons.append("Using industry best practices")
        
        multiplier = self.DAY_MULTIPLIERS.get(day, 1.0)
        if multiplier >= 1.1:
            reasons.append(f"{day} typically has +{int((multiplier-1)*100)}% engagement")
        elif multiplier < 1.0:
            reasons.append(f"{day} has slightly lower engagement")
        
        return ". ".join(reasons) + "."
    
    def schedule_batch(self, video_count: int, category: str = None,
                       spacing_hours: int = 4) -> List[Dict]:
        """
        Schedule multiple videos with optimal spacing.
        
        Args:
            video_count: Number of videos to schedule
            category: Content category
            spacing_hours: Minimum hours between uploads
        
        Returns:
            List of scheduled upload times
        """
        schedules = []
        last_time = datetime.utcnow()
        
        for i in range(video_count):
            # Get optimal time after last scheduled
            optimal = self.get_optimal_upload_time(category)
            scheduled_time = datetime.fromisoformat(optimal["recommended_time_utc"])
            
            # Ensure minimum spacing
            min_time = last_time + timedelta(hours=spacing_hours)
            if scheduled_time < min_time:
                scheduled_time = min_time
            
            schedule = {
                "video_number": i + 1,
                "scheduled_time_utc": scheduled_time.isoformat(),
                "day": scheduled_time.strftime("%A"),
                "hour": scheduled_time.hour,
                "category": category
            }
            schedules.append(schedule)
            last_time = scheduled_time
        
        # Save schedules
        self.data["scheduled_uploads"].extend(schedules)
        self._save()
        
        return schedules
    
    def record_performance(self, hour: int, day: str, views: int):
        """Record upload performance for learning."""
        # Track hourly performance
        hour_key = str(hour)
        if hour_key not in self.data.get("hour_performance", {}):
            self.data["hour_performance"][hour_key] = {"count": 0, "views": 0, "avg": 0}
        
        self.data["hour_performance"][hour_key]["count"] += 1
        self.data["hour_performance"][hour_key]["views"] += views
        self.data["hour_performance"][hour_key]["avg"] = (
            self.data["hour_performance"][hour_key]["views"] / 
            self.data["hour_performance"][hour_key]["count"]
        )
        
        # Track daily performance
        if day not in self.data.get("day_performance", {}):
            self.data["day_performance"][day] = {"count": 0, "views": 0, "avg": 0}
        
        self.data["day_performance"][day]["count"] += 1
        self.data["day_performance"][day]["views"] += views
        self.data["day_performance"][day]["avg"] = (
            self.data["day_performance"][day]["views"] / 
            self.data["day_performance"][day]["count"]
        )
        
        self._save()
    
    def get_insights(self) -> Dict:
        """Get scheduling insights from collected data."""
        hour_perf = self.data.get("hour_performance", {})
        day_perf = self.data.get("day_performance", {})
        
        # Find best hours
        best_hours = sorted(
            [(int(h), d["avg"]) for h, d in hour_perf.items() if d["count"] >= 2],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Find best days
        best_days = sorted(
            [(d, s["avg"]) for d, s in day_perf.items() if s["count"] >= 2],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "best_hours": [h for h, _ in best_hours],
            "best_days": [d for d, _ in best_days],
            "hour_performance": hour_perf,
            "day_performance": day_perf,
            "data_points": sum(d["count"] for d in hour_perf.values()),
            "recommendation": self._generate_recommendation(best_hours, best_days)
        }
    
    def _generate_recommendation(self, best_hours: List, best_days: List) -> str:
        """Generate scheduling recommendation."""
        if not best_hours:
            return "Need more data. Upload at consistent times to build patterns."
        
        hours_str = ", ".join(f"{h}:00 UTC" for h, _ in best_hours[:3])
        if best_days:
            days_str = ", ".join(d for d, _ in best_days[:2])
            return f"Best times: {hours_str} on {days_str}"
        return f"Best hours: {hours_str}"


# Global instance
_scheduler = None

def get_scheduler() -> SmartScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SmartScheduler()
    return _scheduler

def get_next_upload_time(category: str = None) -> Dict:
    """Get next optimal upload time."""
    return get_scheduler().get_optimal_upload_time(category)


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("SMART SCHEDULER - TEST")
    safe_print("=" * 60)
    
    scheduler = SmartScheduler()
    
    # Test single schedule
    optimal = scheduler.get_optimal_upload_time("productivity")
    safe_print(f"\nOptimal Upload Time: {optimal['recommended_time_utc']}")
    safe_print(f"Day: {optimal['recommended_day']} (multiplier: {optimal['day_multiplier']})")
    safe_print(f"Source: {optimal['source']}")
    safe_print(f"Reasoning: {optimal['reasoning']}")
    
    # Test batch scheduling
    safe_print("\nBatch Schedule (3 videos):")
    batch = scheduler.schedule_batch(3, "productivity", spacing_hours=4)
    for s in batch:
        safe_print(f"  Video {s['video_number']}: {s['scheduled_time_utc']} ({s['day']} {s['hour']}:00)")
