#!/usr/bin/env python3
"""
ViralShorts Factory - Dashboard Generator v17.8
=================================================

Generates HTML dashboards for performance analytics.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)


class DashboardGenerator:
    """Generates HTML performance dashboards."""
    
    def __init__(self):
        self.data = self._collect_data()
    
    def _collect_data(self) -> Dict:
        """Collect data from all persistent files."""
        data = {}
        
        files_to_read = [
            ("quality_gate", "quality_gate_history.json"),
            ("virality", "virality_scores.json"),
            ("self_learning", "self_learning.json"),
            ("variety", "variety_state.json"),
            ("patterns", "viral_patterns.json"),
        ]
        
        for name, filename in files_to_read:
            try:
                file_path = STATE_DIR / filename
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data[name] = json.load(f)
            except:
                data[name] = {}
        
        return data
    
    def generate_html(self) -> str:
        """Generate full HTML dashboard."""
        quality = self.data.get("quality_gate", {})
        virality = self.data.get("virality", {})
        learning = self.data.get("self_learning", {})
        
        # Calculate stats
        checks = quality.get("checks", [])
        total_checks = len(checks)
        pass_rate = quality.get("pass_rate", 0) * 100
        avg_score = quality.get("avg_score", 0)
        
        virality_avg = virality.get("average", 0)
        virality_best = virality.get("best", 0)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ViralShorts Factory Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            text-align: center;
            font-size: 2.5rem;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }}
        .card h3 {{
            color: #48dbfb;
            margin-bottom: 16px;
            font-size: 1.1rem;
        }}
        .stat {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .stat.green {{ color: #2ecc71; }}
        .stat.yellow {{ color: #f39c12; }}
        .stat.red {{ color: #e74c3c; }}
        .stat.blue {{ color: #3498db; }}
        .label {{ color: #999; font-size: 0.9rem; }}
        .modules {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }}
        .module {{
            background: rgba(46, 204, 113, 0.2);
            color: #2ecc71;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.85rem;
        }}
        .bar {{
            background: rgba(255, 255, 255, 0.1);
            height: 8px;
            border-radius: 4px;
            margin-top: 12px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        .bar-fill.green {{ background: linear-gradient(90deg, #2ecc71, #27ae60); }}
        .bar-fill.blue {{ background: linear-gradient(90deg, #3498db, #2980b9); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ViralShorts Factory Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h3>Quality Gate</h3>
                <div class="stat {'green' if pass_rate >= 80 else 'yellow' if pass_rate >= 60 else 'red'}">{pass_rate:.1f}%</div>
                <div class="label">Pass Rate</div>
                <div class="bar">
                    <div class="bar-fill green" style="width: {min(100, pass_rate)}%"></div>
                </div>
            </div>
            
            <div class="card">
                <h3>Average Score</h3>
                <div class="stat blue">{avg_score:.1f}</div>
                <div class="label">Out of 100</div>
                <div class="bar">
                    <div class="bar-fill blue" style="width: {min(100, avg_score)}%"></div>
                </div>
            </div>
            
            <div class="card">
                <h3>Virality Average</h3>
                <div class="stat {'green' if virality_avg >= 70 else 'yellow'}">{virality_avg:.1f}</div>
                <div class="label">Score</div>
            </div>
            
            <div class="card">
                <h3>Best Virality</h3>
                <div class="stat green">{virality_best:.1f}</div>
                <div class="label">Peak Score</div>
            </div>
            
            <div class="card">
                <h3>Total Checks</h3>
                <div class="stat blue">{total_checks}</div>
                <div class="label">Quality checks run</div>
            </div>
            
            <div class="card">
                <h3>Active Modules</h3>
                <div class="stat green">26</div>
                <div class="label">AI modules</div>
                <div class="modules">
                    <span class="module">Hook Gen</span>
                    <span class="module">CTA Gen</span>
                    <span class="module">Title Opt</span>
                    <span class="module">Virality</span>
                    <span class="module">+22 more</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            ViralShorts Factory v17.8.26
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_dashboard(self, output_path: str = "dashboard.html") -> str:
        """Generate and save dashboard."""
        html = self.generate_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        safe_print(f"   [DASHBOARD] Generated: {output_path}")
        return output_path
    
    def get_summary(self) -> Dict:
        """Get summary data."""
        quality = self.data.get("quality_gate", {})
        virality = self.data.get("virality", {})
        
        return {
            "quality_checks": len(quality.get("checks", [])),
            "pass_rate": round(quality.get("pass_rate", 0) * 100, 1),
            "avg_score": round(quality.get("avg_score", 0), 1),
            "virality_avg": round(virality.get("average", 0), 1),
            "virality_best": round(virality.get("best", 0), 1),
            "generated_at": datetime.now().isoformat()
        }


# Singleton
_dashboard_generator = None


def get_dashboard_generator() -> DashboardGenerator:
    """Get singleton generator."""
    global _dashboard_generator
    if _dashboard_generator is None:
        _dashboard_generator = DashboardGenerator()
    return _dashboard_generator


def generate_dashboard(output_path: str = "dashboard.html") -> str:
    """Convenience function."""
    return get_dashboard_generator().save_dashboard(output_path)


if __name__ == "__main__":
    safe_print("Testing Dashboard Generator...")
    
    generator = get_dashboard_generator()
    
    # Generate dashboard
    path = generator.save_dashboard()
    
    # Get summary
    summary = generator.get_summary()
    
    safe_print(f"\nDashboard Summary:")
    safe_print("-" * 40)
    for key, value in summary.items():
        safe_print(f"  {key}: {value}")
    
    safe_print(f"\nDashboard saved to: {path}")
    safe_print("\nTest complete!")

