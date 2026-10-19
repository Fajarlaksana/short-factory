#!/usr/bin/env python3
"""
ViralShorts Factory - Performance Dashboard v15.0
===================================================

This module provides a unified view of all performance metrics:
1. Token usage across providers
2. Video quality scores
3. Regeneration rates
4. Learning progress
5. Quota status

Use this to monitor the health of the video generation system.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Data directories
STATE_DIR = Path("data/persistent")
DASHBOARD_FILE = STATE_DIR / "dashboard_data.json"


def safe_print(text):
    """Print safely regardless of encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))


class PerformanceDashboard:
    """
    Unified performance dashboard for ViralShorts Factory.
    """
    
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load dashboard data from disk."""
        try:
            if DASHBOARD_FILE.exists():
                with open(DASHBOARD_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_videos_generated": 0,
                "total_tokens_used": 0,
                "avg_quality_score": 0.0,
                "regeneration_rate": 0.0,
            },
            "history": [],
            "provider_stats": {
                "groq": {"calls": 0, "tokens": 0, "errors": 0},
                "gemini": {"calls": 0, "tokens": 0, "errors": 0},
                "openrouter": {"calls": 0, "tokens": 0, "errors": 0}
            },
            "quality_trend": [],
            "learning_progress": []
        }
    
    def _save(self):
        """Save dashboard data to disk."""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            self.data["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(DASHBOARD_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            safe_print(f"[Dashboard] Save error: {e}")
    
    def collect_metrics(self) -> Dict:
        """
        Collect metrics from all v15.0 systems.
        
        Returns a comprehensive metrics dictionary.
        """
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token_budget": None,
            "self_learning": None,
            "quota_monitor": None,
            "first_attempt": None
        }
        
        # Collect from Token Budget Manager
        try:
            from token_budget_manager import get_budget_manager
            budget = get_budget_manager()
            metrics["token_budget"] = {
                "videos_remaining": budget.estimate_videos_remaining(),
                "status": budget.get_status()
            }
        except Exception as e:
            metrics["token_budget"] = {"error": str(e)}
        
        # Collect from Self-Learning Engine
        try:
            from self_learning_engine import get_learning_engine
            engine = get_learning_engine()
            stats = engine.data.get("stats", {})
            metrics["self_learning"] = {
                "total_videos": stats.get("total_videos", 0),
                "avg_first_attempt_score": stats.get("avg_first_attempt_score", 0),
                "regeneration_rate": stats.get("regeneration_rate", 0),
                "top_categories": stats.get("top_categories", []),
                "worst_categories": stats.get("worst_categories", [])
            }
        except Exception as e:
            metrics["self_learning"] = {"error": str(e)}
        
        # Collect from Quota Monitor
        try:
            from quota_monitor import get_quota_monitor
            monitor = get_quota_monitor()
            rec = monitor.get_scheduling_recommendation()
            metrics["quota_monitor"] = {
                "can_run_now": rec["can_run_now"],
                "best_provider": rec["best_provider"],
                "videos_possible": rec["videos_possible"],
                "reason": rec["reason"]
            }
        except Exception as e:
            metrics["quota_monitor"] = {"error": str(e)}
        
        # Collect from First-Attempt Maximizer
        try:
            from token_budget_manager import get_first_attempt_maximizer
            first = get_first_attempt_maximizer()
            metrics["first_attempt"] = {
                "avg_first_attempt_score": first.history.get("avg_first_attempt_score", 0),
                "regeneration_rate": first.history.get("regeneration_rate", 0),
                "total_videos": first.history.get("total_videos", 0)
            }
        except Exception as e:
            metrics["first_attempt"] = {"error": str(e)}
        
        return metrics
    
    def update_dashboard(self):
        """Update dashboard with current metrics."""
        metrics = self.collect_metrics()
        
        # Add to history (keep last 100 entries)
        self.data["history"].append(metrics)
        self.data["history"] = self.data["history"][-100:]
        
        # Update summary
        if metrics.get("self_learning") and not metrics["self_learning"].get("error"):
            self.data["summary"]["total_videos_generated"] = metrics["self_learning"]["total_videos"]
            self.data["summary"]["avg_quality_score"] = metrics["self_learning"]["avg_first_attempt_score"]
            self.data["summary"]["regeneration_rate"] = metrics["self_learning"]["regeneration_rate"]
        
        if metrics.get("token_budget") and not metrics["token_budget"].get("error"):
            status = metrics["token_budget"].get("status", {})
            total_tokens = sum(s.get("used", 0) for s in status.values())
            self.data["summary"]["total_tokens_used"] = total_tokens
        
        self._save()
        return metrics
    
    def get_summary_string(self) -> str:
        """Get a human-readable summary string."""
        metrics = self.update_dashboard()
        
        lines = [
            "=" * 70,
            "   VIRALSHORTS FACTORY - PERFORMANCE DASHBOARD",
            "=" * 70,
            "",
            "SUMMARY:",
            f"  Total Videos Generated: {self.data['summary']['total_videos_generated']}",
            f"  Average Quality Score: {self.data['summary']['avg_quality_score']:.1f}/10",
            f"  Regeneration Rate: {self.data['summary']['regeneration_rate']*100:.1f}%",
            f"  Goal: <10% regeneration, 8+/10 quality",
            ""
        ]
        
        # Token Budget Status
        if metrics.get("token_budget") and not metrics["token_budget"].get("error"):
            lines.append("TOKEN BUDGET:")
            for provider, status in metrics["token_budget"]["status"].items():
                pct = (status["used"] / status["limit"]) * 100 if status["limit"] > 0 else 0
                cooldown = " [COOLDOWN]" if status.get("in_cooldown") else ""
                lines.append(f"  {provider.upper():12} | {status['used']:,}/{status['limit']:,} ({pct:.1f}%){cooldown}")
            lines.append(f"  Videos Remaining Today: {metrics['token_budget']['videos_remaining']}")
            lines.append("")
        
        # Quota Status
        if metrics.get("quota_monitor") and not metrics["quota_monitor"].get("error"):
            qm = metrics["quota_monitor"]
            lines.append("QUOTA STATUS:")
            lines.append(f"  Can Run Now: {qm['can_run_now']}")
            lines.append(f"  Best Provider: {qm['best_provider']}")
            lines.append(f"  Reason: {qm['reason']}")
            lines.append("")
        
        # Learning Progress
        if metrics.get("self_learning") and not metrics["self_learning"].get("error"):
            sl = metrics["self_learning"]
            lines.append("SELF-LEARNING:")
            lines.append(f"  Videos Analyzed: {sl['total_videos']}")
            lines.append(f"  Top Categories: {', '.join(sl.get('top_categories', [])[:3]) or 'None yet'}")
            lines.append(f"  Categories to Avoid: {', '.join(sl.get('worst_categories', [])[:3]) or 'None yet'}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append(f"Last Updated: {self.data['last_updated']}")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def export_html(self) -> str:
        """Export dashboard as HTML for viewing."""
        metrics = self.collect_metrics()
        summary = self.data['summary']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ViralShorts Factory - Performance Dashboard</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            margin-bottom: 30px;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }}
        .card h2 {{ 
            color: #00d4ff; 
            margin-top: 0;
            font-size: 1.2em;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .metric-value {{ 
            font-weight: bold; 
            color: #00ff88;
        }}
        .warning {{ color: #ff6b6b; }}
        .success {{ color: #00ff88; }}
        .footer {{ 
            text-align: center; 
            margin-top: 30px; 
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ViralShorts Factory - Performance Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>Summary</h2>
                <div class="metric">
                    <span>Total Videos</span>
                    <span class="metric-value">{summary['total_videos_generated']}</span>
                </div>
                <div class="metric">
                    <span>Avg Quality Score</span>
                    <span class="metric-value {'success' if summary['avg_quality_score'] >= 8 else 'warning'}">{summary['avg_quality_score']:.1f}/10</span>
                </div>
                <div class="metric">
                    <span>Regeneration Rate</span>
                    <span class="metric-value {'success' if summary['regeneration_rate'] < 0.1 else 'warning'}">{summary['regeneration_rate']*100:.1f}%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Token Budget</h2>
                {''.join(f'<div class="metric"><span>{p.upper()}</span><span class="metric-value">{s.get("used", 0):,}/{s.get("limit", 0):,}</span></div>' for p, s in (metrics.get("token_budget", {}).get("status", {})).items())}
                <div class="metric">
                    <span>Videos Remaining</span>
                    <span class="metric-value">{metrics.get('token_budget', {}).get('videos_remaining', 'N/A')}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Quota Status</h2>
                <div class="metric">
                    <span>Can Run Now</span>
                    <span class="metric-value {'success' if metrics.get('quota_monitor', {}).get('can_run_now') else 'warning'}">{metrics.get('quota_monitor', {}).get('can_run_now', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Best Provider</span>
                    <span class="metric-value">{metrics.get('quota_monitor', {}).get('best_provider', 'N/A')}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Self-Learning</h2>
                <div class="metric">
                    <span>Videos Analyzed</span>
                    <span class="metric-value">{metrics.get('self_learning', {}).get('total_videos', 0)}</span>
                </div>
                <div class="metric">
                    <span>Top Categories</span>
                    <span class="metric-value">{', '.join(metrics.get('self_learning', {}).get('top_categories', [])[:3]) or 'None'}</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Last Updated: {datetime.now(timezone.utc).isoformat()}<br>
            ViralShorts Factory v15.0
        </div>
    </div>
</body>
</html>
"""
        return html


# Singleton
_dashboard = None

def get_dashboard() -> PerformanceDashboard:
    """Get the singleton dashboard."""
    global _dashboard
    if _dashboard is None:
        _dashboard = PerformanceDashboard()
    return _dashboard


if __name__ == "__main__":
    dashboard = get_dashboard()
    print(dashboard.get_summary_string())
    
    # Export HTML
    html = dashboard.export_html()
    html_path = Path("dashboard.html")
    html_path.write_text(html)
    print(f"\nDashboard exported to: {html_path.absolute()}")

