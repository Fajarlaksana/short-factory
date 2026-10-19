#!/usr/bin/env python3
"""
Quota Monitoring Dashboard v1.0
===============================

Real-time visualization of quota usage across all providers.
Generates HTML dashboard for monitoring.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

STATE_DIR = Path("./data/persistent")
OUTPUT_DIR = Path("./data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class QuotaDashboard:
    """
    Generates quota monitoring dashboard.
    """
    
    def __init__(self):
        self.router_cache = self._load_router_cache()
        self.quota_state = self._load_quota_state()
    
    def _load_router_cache(self) -> Dict:
        try:
            cache_file = STATE_DIR / "smart_router_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _load_quota_state(self) -> Dict:
        try:
            quota_file = STATE_DIR / "enhanced_quota_state.json"
            if quota_file.exists():
                with open(quota_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def get_model_usage(self) -> Dict[str, Dict]:
        """Get usage stats per model."""
        models = self.router_cache.get("models", {})
        usage = {}
        
        for key, model in models.items():
            if isinstance(model, dict):
                usage[key] = {
                    "calls_today": model.get("calls_today", 0),
                    "daily_limit": model.get("daily_limit", 100),
                    "consecutive_failures": model.get("consecutive_failures", 0),
                    "available": model.get("available", True),
                    "cooldown_until": model.get("cooldown_until", ""),
                    "provider": model.get("provider", "unknown"),
                }
                # Calculate percentage
                limit = usage[key]["daily_limit"]
                calls = usage[key]["calls_today"]
                usage[key]["usage_percent"] = min(100, round(calls / max(1, limit) * 100, 1))
        
        return usage
    
    def generate_html(self) -> str:
        """Generate HTML dashboard."""
        usage = self.get_model_usage()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Group by provider
        providers = {}
        for key, data in usage.items():
            provider = data.get("provider", "unknown")
            if provider not in providers:
                providers[provider] = []
            providers[provider].append((key, data))
        
        # Build HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Quota Dashboard - ViralShorts Factory</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7b2fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .timestamp {{ text-align: center; color: #888; margin-bottom: 20px; }}
        .providers {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .provider {{ 
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .provider h2 {{ 
            margin-bottom: 15px; 
            color: #00d4ff;
            font-size: 1.3em;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }}
        .model {{ 
            background: rgba(0,0,0,0.2);
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        .model-name {{ font-size: 0.85em; color: #aaa; margin-bottom: 8px; }}
        .bar-container {{ 
            height: 20px; 
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .bar {{ 
            height: 100%;
            transition: width 0.3s;
            border-radius: 10px;
        }}
        .bar.green {{ background: linear-gradient(90deg, #00c853, #00e676); }}
        .bar.yellow {{ background: linear-gradient(90deg, #ff9800, #ffc107); }}
        .bar.red {{ background: linear-gradient(90deg, #f44336, #ff5252); }}
        .stats {{ display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.8em; color: #888; }}
        .status {{ 
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7em;
            margin-left: 10px;
        }}
        .status.ok {{ background: #00c853; }}
        .status.warn {{ background: #ff9800; }}
        .status.error {{ background: #f44336; }}
        .summary {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }}
        .summary-stat {{
            display: inline-block;
            margin: 0 30px;
        }}
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00d4ff;
        }}
        .summary-label {{ color: #888; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Quota Dashboard</h1>
    <p class="timestamp">Last updated: {now}</p>
    
    <div class="summary">
'''
        # Summary stats
        total_models = len(usage)
        active_models = sum(1 for u in usage.values() if u["available"])
        exhausted_models = sum(1 for u in usage.values() if u["usage_percent"] >= 90)
        
        html += f'''
        <div class="summary-stat">
            <div class="summary-value">{total_models}</div>
            <div class="summary-label">Total Models</div>
        </div>
        <div class="summary-stat">
            <div class="summary-value">{active_models}</div>
            <div class="summary-label">Active</div>
        </div>
        <div class="summary-stat">
            <div class="summary-value">{exhausted_models}</div>
            <div class="summary-label">Near Exhaustion</div>
        </div>
    </div>
    
    <div class="providers">
'''
        
        # Provider sections
        for provider, models in sorted(providers.items()):
            html += f'''
        <div class="provider">
            <h2>{provider.upper()}</h2>
'''
            for key, data in sorted(models, key=lambda x: x[1]["usage_percent"], reverse=True):
                pct = data["usage_percent"]
                bar_class = "green" if pct < 50 else ("yellow" if pct < 80 else "red")
                status_class = "ok" if data["available"] and pct < 80 else ("warn" if pct < 95 else "error")
                status_text = "OK" if status_class == "ok" else ("LOW" if status_class == "warn" else "EXHAUSTED")
                
                model_name = key.split(":")[-1] if ":" in key else key
                
                html += f'''
            <div class="model">
                <div class="model-name">{model_name}<span class="status {status_class}">{status_text}</span></div>
                <div class="bar-container">
                    <div class="bar {bar_class}" style="width: {pct}%"></div>
                </div>
                <div class="stats">
                    <span>{data["calls_today"]} / {data["daily_limit"]} calls</span>
                    <span>{pct}% used</span>
                </div>
            </div>
'''
            html += '        </div>\n'
        
        html += '''
    </div>
</body>
</html>'''
        
        return html
    
    def save_dashboard(self, filename: str = "quota_dashboard.html"):
        """Save dashboard to file."""
        html = self.generate_html()
        output_path = OUTPUT_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        safe_print(f"[DASHBOARD] Saved to {output_path}")
        return str(output_path)


def generate_quota_dashboard() -> str:
    """Generate and save quota dashboard."""
    dashboard = QuotaDashboard()
    return dashboard.save_dashboard()


if __name__ == "__main__":
    safe_print("Generating Quota Dashboard...")
    path = generate_quota_dashboard()
    safe_print(f"Dashboard saved: {path}")