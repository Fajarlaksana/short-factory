#!/usr/bin/env python3
"""
ViralShorts Factory - Revenue Tracking & CPM Optimization v17.9.50
===================================================================

Tracks revenue metrics and optimizes content for higher CPM.

Features:
- Track estimated CPM by category
- Identify high-revenue content niches
- Revenue projection based on views
- Monetization readiness checklist
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    """Print with Unicode fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
REVENUE_FILE = STATE_DIR / "revenue_tracking.json"


# Industry CPM estimates by category (USD per 1000 views)
# These are averages for YouTube Shorts - actual varies widely
CATEGORY_CPM_ESTIMATES = {
    # High CPM categories (advertisers pay more)
    "finance": {"cpm_low": 4.0, "cpm_high": 12.0, "avg": 8.0},
    "money": {"cpm_low": 4.0, "cpm_high": 12.0, "avg": 8.0},
    "technology": {"cpm_low": 3.0, "cpm_high": 10.0, "avg": 6.5},
    "business": {"cpm_low": 3.5, "cpm_high": 10.0, "avg": 6.75},
    "health": {"cpm_low": 2.5, "cpm_high": 8.0, "avg": 5.25},
    
    # Medium CPM categories
    "education": {"cpm_low": 2.0, "cpm_high": 6.0, "avg": 4.0},
    "productivity": {"cpm_low": 2.0, "cpm_high": 6.0, "avg": 4.0},
    "psychology": {"cpm_low": 1.5, "cpm_high": 5.0, "avg": 3.25},
    "science": {"cpm_low": 1.5, "cpm_high": 5.0, "avg": 3.25},
    "marketing": {"cpm_low": 2.5, "cpm_high": 8.0, "avg": 5.25},
    
    # Lower CPM categories (but often higher volume)
    "entertainment": {"cpm_low": 0.5, "cpm_high": 3.0, "avg": 1.75},
    "lifestyle": {"cpm_low": 0.5, "cpm_high": 3.0, "avg": 1.75},
    "motivation": {"cpm_low": 0.8, "cpm_high": 3.5, "avg": 2.15},
    "relationships": {"cpm_low": 0.8, "cpm_high": 3.5, "avg": 2.15},
    
    # Default for uncategorized
    "general": {"cpm_low": 0.5, "cpm_high": 2.5, "avg": 1.5},
}

# Monetization requirements
MONETIZATION_REQUIREMENTS = {
    "youtube_partner": {
        "subscribers": 1000,
        "watch_hours": 4000,  # or 10M Shorts views in 90 days
        "shorts_views_90days": 10_000_000,
    },
    "shorts_fund": {
        "subscribers": 0,  # No minimum
        "shorts_views": 1000,  # Views on qualifying Shorts
    }
}


class RevenueTracker:
    """
    Tracks revenue metrics and provides monetization insights.
    """
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load revenue tracking data."""
        try:
            if REVENUE_FILE.exists():
                with open(REVENUE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            safe_print(f"[REVENUE] Load error: {e}")
        
        return {
            "videos": [],
            "category_performance": {},
            "total_views": 0,
            "estimated_revenue": 0,
            "monetization_status": "not_eligible",
            "last_updated": None
        }
    
    def _save(self):
        """Save revenue tracking data."""
        self.data["last_updated"] = datetime.now().isoformat()
        try:
            with open(REVENUE_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            safe_print(f"[REVENUE] Save error: {e}")
    
    def record_video(self, video_id: str, title: str, category: str, 
                     views: int = 0, engagement_rate: float = 0):
        """
        Record a video's performance for revenue tracking.
        """
        cpm_data = CATEGORY_CPM_ESTIMATES.get(
            category.lower(), 
            CATEGORY_CPM_ESTIMATES["general"]
        )
        
        estimated_revenue = (views / 1000) * cpm_data["avg"]
        
        video_record = {
            "id": video_id,
            "title": title,
            "category": category,
            "views": views,
            "engagement_rate": engagement_rate,
            "estimated_cpm": cpm_data["avg"],
            "estimated_revenue": round(estimated_revenue, 2),
            "recorded_at": datetime.now().isoformat()
        }
        
        self.data["videos"].append(video_record)
        self.data["total_views"] += views
        self.data["estimated_revenue"] += estimated_revenue
        
        # Update category performance
        cat_perf = self.data.get("category_performance", {})
        if category not in cat_perf:
            cat_perf[category] = {
                "videos": 0,
                "views": 0,
                "revenue": 0,
                "avg_views": 0
            }
        
        cat_perf[category]["videos"] += 1
        cat_perf[category]["views"] += views
        cat_perf[category]["revenue"] += estimated_revenue
        cat_perf[category]["avg_views"] = (
            cat_perf[category]["views"] / cat_perf[category]["videos"]
        )
        
        self.data["category_performance"] = cat_perf
        self._save()
        
        safe_print(f"[REVENUE] Recorded: {title[:30]}... | "
                  f"Est. ${estimated_revenue:.2f}")
    
    def get_high_cpm_categories(self, min_cpm: float = 3.0) -> List[Dict]:
        """
        Get categories with high CPM potential.
        
        Useful for content strategy optimization.
        """
        high_cpm = []
        
        for category, cpm_data in CATEGORY_CPM_ESTIMATES.items():
            if cpm_data["avg"] >= min_cpm:
                high_cpm.append({
                    "category": category,
                    "avg_cpm": cpm_data["avg"],
                    "cpm_range": f"${cpm_data['cpm_low']}-${cpm_data['cpm_high']}",
                    "priority": "high" if cpm_data["avg"] >= 5.0 else "medium"
                })
        
        # Sort by average CPM
        high_cpm.sort(key=lambda x: x["avg_cpm"], reverse=True)
        
        return high_cpm
    
    def get_revenue_projection(self, monthly_views: int = None) -> Dict:
        """
        Project potential revenue based on current performance.
        """
        if monthly_views is None:
            # Estimate from recent data
            total_videos = len(self.data.get("videos", []))
            if total_videos > 0:
                avg_views = self.data["total_views"] / total_videos
                # Assume 6 videos/day = 180/month
                monthly_views = int(avg_views * 180)
            else:
                monthly_views = 10000  # Conservative default
        
        # Calculate projections based on category mix
        cat_perf = self.data.get("category_performance", {})
        weighted_cpm = 0
        total_videos = 0
        
        for category, stats in cat_perf.items():
            cpm_data = CATEGORY_CPM_ESTIMATES.get(
                category.lower(), 
                CATEGORY_CPM_ESTIMATES["general"]
            )
            weighted_cpm += cpm_data["avg"] * stats["videos"]
            total_videos += stats["videos"]
        
        if total_videos > 0:
            avg_cpm = weighted_cpm / total_videos
        else:
            avg_cpm = 2.0  # Default assumption
        
        monthly_revenue = (monthly_views / 1000) * avg_cpm
        yearly_revenue = monthly_revenue * 12
        
        return {
            "projected_monthly_views": monthly_views,
            "avg_cpm": round(avg_cpm, 2),
            "projected_monthly_revenue": round(monthly_revenue, 2),
            "projected_yearly_revenue": round(yearly_revenue, 2),
            "recommendation": self._get_revenue_recommendation(monthly_revenue)
        }
    
    def _get_revenue_recommendation(self, monthly_revenue: float) -> str:
        """Get recommendation based on revenue level."""
        if monthly_revenue < 10:
            return "Focus on growing views first. Target 10K+ views per video."
        elif monthly_revenue < 100:
            return "Good start! Consider high-CPM categories (finance, tech)."
        elif monthly_revenue < 500:
            return "Growing well! Add affiliate links for extra income."
        elif monthly_revenue < 1000:
            return "Nice! Consider sponsorships and product placements."
        else:
            return "Excellent! Diversify with courses, merch, and partnerships."
    
    def check_monetization_eligibility(self, 
                                        subscribers: int = 0,
                                        watch_hours: int = 0,
                                        shorts_views_90days: int = 0) -> Dict:
        """
        Check if channel meets monetization requirements.
        """
        reqs = MONETIZATION_REQUIREMENTS["youtube_partner"]
        
        # Check traditional path (watch hours)
        traditional_eligible = (
            subscribers >= reqs["subscribers"] and
            watch_hours >= reqs["watch_hours"]
        )
        
        # Check Shorts path (10M views in 90 days)
        shorts_eligible = (
            subscribers >= reqs["subscribers"] and
            shorts_views_90days >= reqs["shorts_views_90days"]
        )
        
        # Progress tracking
        subscriber_progress = min(100, (subscribers / reqs["subscribers"]) * 100)
        
        if traditional_eligible or shorts_eligible:
            watch_progress = 100
        else:
            watch_progress = min(100, (watch_hours / reqs["watch_hours"]) * 100)
        
        shorts_progress = min(100, (shorts_views_90days / reqs["shorts_views_90days"]) * 100)
        
        return {
            "eligible": traditional_eligible or shorts_eligible,
            "traditional_path": {
                "eligible": traditional_eligible,
                "subscribers": f"{subscribers}/{reqs['subscribers']}",
                "watch_hours": f"{watch_hours}/{reqs['watch_hours']}"
            },
            "shorts_path": {
                "eligible": shorts_eligible,
                "subscribers": f"{subscribers}/{reqs['subscribers']}",
                "shorts_views": f"{shorts_views_90days:,}/{reqs['shorts_views_90days']:,}"
            },
            "progress": {
                "subscribers": round(subscriber_progress, 1),
                "watch_hours": round(watch_progress, 1),
                "shorts_views": round(shorts_progress, 1)
            },
            "next_steps": self._get_next_steps(subscribers, watch_hours, shorts_views_90days)
        }
    
    def _get_next_steps(self, subs: int, hours: int, views: int) -> List[str]:
        """Get personalized next steps for monetization."""
        steps = []
        
        reqs = MONETIZATION_REQUIREMENTS["youtube_partner"]
        
        if subs < reqs["subscribers"]:
            remaining = reqs["subscribers"] - subs
            steps.append(f"Gain {remaining} more subscribers (currently {subs})")
        
        if hours < reqs["watch_hours"] and views < reqs["shorts_views_90days"]:
            # Recommend Shorts path (usually faster)
            remaining = reqs["shorts_views_90days"] - views
            steps.append(f"Get {remaining:,} more Shorts views in 90 days")
            steps.append("Shorts path is usually faster than watch hours!")
        
        if not steps:
            steps.append("You're eligible! Apply for the YouTube Partner Program.")
        
        return steps
    
    def get_summary(self) -> Dict:
        """Get revenue tracking summary."""
        cat_perf = self.data.get("category_performance", {})
        
        # Find best performing category
        best_category = None
        best_views = 0
        for cat, stats in cat_perf.items():
            if stats.get("avg_views", 0) > best_views:
                best_views = stats["avg_views"]
                best_category = cat
        
        return {
            "total_videos_tracked": len(self.data.get("videos", [])),
            "total_views": self.data.get("total_views", 0),
            "estimated_total_revenue": round(self.data.get("estimated_revenue", 0), 2),
            "best_category": best_category,
            "best_category_avg_views": best_views,
            "category_breakdown": cat_perf,
            "high_cpm_categories": self.get_high_cpm_categories(),
            "last_updated": self.data.get("last_updated")
        }


# Global instance
_tracker = None


def get_revenue_tracker() -> RevenueTracker:
    """Get global revenue tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RevenueTracker()
    return _tracker


# Test
if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("REVENUE TRACKER - TEST")
    safe_print("=" * 60)
    
    tracker = RevenueTracker()
    
    # Show high CPM categories
    safe_print("\nHigh CPM Categories:")
    for cat in tracker.get_high_cpm_categories()[:5]:
        safe_print(f"  {cat['category']}: ${cat['avg_cpm']} CPM ({cat['cpm_range']})")
    
    # Revenue projection
    safe_print("\nRevenue Projection (100K views/month):")
    projection = tracker.get_revenue_projection(100000)
    safe_print(f"  Monthly: ${projection['projected_monthly_revenue']}")
    safe_print(f"  Yearly: ${projection['projected_yearly_revenue']}")
    safe_print(f"  Recommendation: {projection['recommendation']}")
    
    # Monetization check
    safe_print("\nMonetization Eligibility (500 subs, 1000 hours):")
    eligibility = tracker.check_monetization_eligibility(500, 1000, 500000)
    safe_print(f"  Eligible: {eligibility['eligible']}")
    safe_print(f"  Next steps: {eligibility['next_steps']}")
