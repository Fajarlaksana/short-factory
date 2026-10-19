#!/usr/bin/env python3
"""
ViralShorts Factory - Performance Dashboard Generator v17.9.51
===============================================================

Generates comprehensive HTML dashboards for performance visualization.

Features:
- Real-time metrics overview
- Category performance charts
- Series tracking
- Revenue projections
- Trend analysis
- AI recommendations

Output: Beautiful HTML dashboard with charts
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)
VARIETY_FILE = STATE_DIR / "variety_state.json"
REVENUE_FILE = STATE_DIR / "revenue_tracking.json"
SERIES_FILE = STATE_DIR / "series_tracking.json"


class DashboardGenerator:
    """
    Generates HTML performance dashboards.
    """
    
    def __init__(self):
        self.variety_state = self._load_json(VARIETY_FILE)
        self.revenue_data = self._load_json(REVENUE_FILE)
        self.series_data = self._load_json(SERIES_FILE)
    
    def _load_json(self, path: Path) -> Dict:
        try:
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def generate_dashboard(self, output_path: str = "performance_dashboard.html") -> str:
        """
        Generate a comprehensive HTML dashboard.
        
        Returns:
            Path to generated HTML file
        """
        # Gather all metrics
        metrics = self._gather_metrics()
        
        # Generate HTML
        html = self._generate_html(metrics)
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        safe_print(f"[DASHBOARD] Generated: {output_path}")
        return output_path
    
    def _gather_metrics(self) -> Dict:
        """Gather all metrics for dashboard."""
        return {
            "overview": self._get_overview_metrics(),
            "categories": self._get_category_metrics(),
            "series": self._get_series_metrics(),
            "revenue": self._get_revenue_metrics(),
            "trends": self._get_trend_metrics(),
            "recommendations": self._get_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_overview_metrics(self) -> Dict:
        """Get high-level overview metrics."""
        videos = self.revenue_data.get("videos", [])
        
        total_views = sum(v.get("views", 0) for v in videos)
        total_videos = len(videos)
        avg_views = total_views / max(1, total_videos)
        
        return {
            "total_videos": total_videos,
            "total_views": total_views,
            "avg_views_per_video": int(avg_views),
            "estimated_revenue": round(self.revenue_data.get("estimated_revenue", 0), 2),
            "last_updated": self.variety_state.get("last_updated")
        }
    
    def _get_category_metrics(self) -> List[Dict]:
        """Get performance by category."""
        cat_perf = self.revenue_data.get("category_performance", {})
        
        categories = []
        for cat, stats in cat_perf.items():
            categories.append({
                "name": cat,
                "videos": stats.get("videos", 0),
                "views": stats.get("views", 0),
                "revenue": round(stats.get("revenue", 0), 2),
                "avg_views": int(stats.get("avg_views", 0))
            })
        
        return sorted(categories, key=lambda x: x["views"], reverse=True)
    
    def _get_series_metrics(self) -> List[Dict]:
        """Get series performance metrics."""
        series_list = []
        
        for series_id, series in self.series_data.get("series", {}).items():
            total_views = sum(v.get("views", 0) for v in series.get("videos", []))
            series_list.append({
                "name": series.get("name", "Unknown"),
                "category": series.get("category", "general"),
                "episodes": len(series.get("videos", [])),
                "total_views": total_views,
                "status": series.get("status", "unknown")
            })
        
        return sorted(series_list, key=lambda x: x["total_views"], reverse=True)[:10]
    
    def _get_revenue_metrics(self) -> Dict:
        """Get revenue metrics."""
        cat_perf = self.revenue_data.get("category_performance", {})
        
        # Calculate weighted CPM
        total_revenue = self.revenue_data.get("estimated_revenue", 0)
        total_views = sum(c.get("views", 0) for c in cat_perf.values())
        
        if total_views > 0:
            effective_cpm = (total_revenue / total_views) * 1000
        else:
            effective_cpm = 2.0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "effective_cpm": round(effective_cpm, 2),
            "monthly_projection": round(total_revenue * 4, 2),  # Rough projection
            "yearly_projection": round(total_revenue * 52, 2)
        }
    
    def _get_trend_metrics(self) -> Dict:
        """Get trend and learning metrics."""
        analytics = self.variety_state.get("analytics_insights", {})
        learned = self.variety_state.get("learned_from_performance", {})
        
        return {
            "best_categories": learned.get("best_performing_categories", [])[:5],
            "best_hours": learned.get("best_posting_hours_utc", [])[:5],
            "best_days": learned.get("best_posting_days", [])[:3],
            "optimal_duration": analytics.get("optimal_duration"),
            "optimal_title_length": analytics.get("optimal_title_word_count")
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get AI recommendations."""
        recs = []
        
        # From variety state
        ai_recs = self.variety_state.get("ai_recommendations", {})
        
        if ai_recs.get("trending_topics"):
            recs.append(f"Trending topics: {', '.join(ai_recs['trending_topics'][:3])}")
        
        if ai_recs.get("recommended_hooks"):
            recs.append(f"Best hooks: {', '.join(ai_recs['recommended_hooks'][:2])}")
        
        # Revenue-based recommendations
        revenue = self._get_revenue_metrics()
        if revenue["effective_cpm"] < 3.0:
            recs.append("Focus on high-CPM categories: finance, technology, business")
        
        # Default recommendations
        if not recs:
            recs = [
                "Keep posting consistently",
                "Analyze top-performing videos for patterns",
                "Test different hook styles"
            ]
        
        return recs[:5]
    
    def _generate_html(self, metrics: Dict) -> str:
        """Generate the HTML dashboard."""
        overview = metrics["overview"]
        categories = metrics["categories"]
        series = metrics["series"]
        revenue = metrics["revenue"]
        trends = metrics["trends"]
        recommendations = metrics["recommendations"]
        
        # Generate category rows
        category_rows = ""
        for cat in categories[:10]:
            category_rows += f"""
                <tr>
                    <td>{cat['name'].title()}</td>
                    <td>{cat['videos']}</td>
                    <td>{cat['views']:,}</td>
                    <td>${cat['revenue']:.2f}</td>
                    <td>{cat['avg_views']:,}</td>
                </tr>
            """
        
        # Generate series rows
        series_rows = ""
        for s in series[:5]:
            series_rows += f"""
                <tr>
                    <td>{s['name']}</td>
                    <td>{s['episodes']}</td>
                    <td>{s['total_views']:,}</td>
                    <td><span class="status-{s['status']}">{s['status']}</span></td>
                </tr>
            """
        
        # Generate recommendations list
        recs_list = "".join(f"<li>{r}</li>" for r in recommendations)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ViralShorts Factory - Performance Dashboard</title>
    <style>
        :root {{
            --primary: #6366f1;
            --success: #22c55e;
            --warning: #eab308;
            --danger: #ef4444;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--primary), #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .header .subtitle {{
            color: var(--text-muted);
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 1rem;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .metric-card {{
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .metric-label {{
            color: var(--text-muted);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .section-title {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        th {{
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.875rem;
        }}
        
        .status-active {{
            color: var(--success);
        }}
        
        .status-unknown {{
            color: var(--text-muted);
        }}
        
        .recommendations {{
            background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
        }}
        
        .recommendations ul {{
            list-style: none;
        }}
        
        .recommendations li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        
        .recommendations li::before {{
            content: "💡 ";
        }}
        
        .trends-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        
        .trend-item {{
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }}
        
        .trend-value {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--success);
        }}
        
        .trend-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ViralShorts Factory</h1>
        <p class="subtitle">Performance Dashboard | Generated: {metrics['generated_at'][:19]}</p>
    </div>
    
    <!-- Overview Metrics -->
    <div class="grid">
        <div class="card metric-card">
            <div class="metric-value">{overview['total_videos']}</div>
            <div class="metric-label">Total Videos</div>
        </div>
        <div class="card metric-card">
            <div class="metric-value">{overview['total_views']:,}</div>
            <div class="metric-label">Total Views</div>
        </div>
        <div class="card metric-card">
            <div class="metric-value">{overview['avg_views_per_video']:,}</div>
            <div class="metric-label">Avg Views/Video</div>
        </div>
        <div class="card metric-card">
            <div class="metric-value">${overview['estimated_revenue']:.2f}</div>
            <div class="metric-label">Est. Revenue</div>
        </div>
    </div>
    
    <!-- Revenue Projections -->
    <div class="grid">
        <div class="card metric-card">
            <div class="metric-value">${revenue['effective_cpm']:.2f}</div>
            <div class="metric-label">Effective CPM</div>
        </div>
        <div class="card metric-card">
            <div class="metric-value">${revenue['monthly_projection']:.0f}</div>
            <div class="metric-label">Monthly Projection</div>
        </div>
        <div class="card metric-card">
            <div class="metric-value">${revenue['yearly_projection']:.0f}</div>
            <div class="metric-label">Yearly Projection</div>
        </div>
    </div>
    
    <!-- Main Content Grid -->
    <div class="grid" style="grid-template-columns: 2fr 1fr;">
        <!-- Category Performance -->
        <div class="card">
            <h2 class="section-title">📊 Category Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Videos</th>
                        <th>Views</th>
                        <th>Revenue</th>
                        <th>Avg Views</th>
                    </tr>
                </thead>
                <tbody>
                    {category_rows if category_rows else '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No data yet</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <!-- Recommendations -->
        <div class="card recommendations">
            <h2 class="section-title">💡 AI Recommendations</h2>
            <ul>
                {recs_list}
            </ul>
        </div>
    </div>
    
    <!-- Series and Trends -->
    <div class="grid" style="grid-template-columns: 1fr 1fr;">
        <!-- Active Series -->
        <div class="card">
            <h2 class="section-title">📺 Active Series</h2>
            <table>
                <thead>
                    <tr>
                        <th>Series</th>
                        <th>Episodes</th>
                        <th>Views</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {series_rows if series_rows else '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No series yet</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <!-- Learned Insights -->
        <div class="card">
            <h2 class="section-title">🧠 Learned Insights</h2>
            <div class="trends-grid">
                <div class="trend-item">
                    <div class="trend-value">{', '.join(str(h) + ':00' for h in trends['best_hours'][:3]) or 'N/A'}</div>
                    <div class="trend-label">Best Hours (UTC)</div>
                </div>
                <div class="trend-item">
                    <div class="trend-value">{', '.join(trends['best_days'][:2]) or 'N/A'}</div>
                    <div class="trend-label">Best Days</div>
                </div>
                <div class="trend-item">
                    <div class="trend-value">{trends['optimal_duration'] or 45}s</div>
                    <div class="trend-label">Optimal Duration</div>
                </div>
                <div class="trend-item">
                    <div class="trend-value">{trends['optimal_title_length'] or 8} words</div>
                    <div class="trend-label">Title Length</div>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <strong>Top Categories:</strong>
                <p style="color: var(--text-muted);">{', '.join(c.title() for c in trends['best_categories']) or 'Learning...'}</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>ViralShorts Factory v17.9.51 | Powered by AI-driven optimization</p>
        <p>Dashboard auto-updates with each analytics run</p>
    </div>
</body>
</html>"""
        
        return html


# Global instance
_generator = None

def get_dashboard_generator() -> DashboardGenerator:
    global _generator
    if _generator is None:
        _generator = DashboardGenerator()
    return _generator

def generate_performance_dashboard(output_path: str = None) -> str:
    """Generate performance dashboard HTML."""
    generator = get_dashboard_generator()
    return generator.generate_dashboard(output_path or "performance_dashboard.html")


if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("DASHBOARD GENERATOR - TEST")
    safe_print("=" * 60)
    
    generator = DashboardGenerator()
    output = generator.generate_dashboard("test_dashboard.html")
    safe_print(f"\nDashboard generated: {output}")
    safe_print("Open in browser to view!")
