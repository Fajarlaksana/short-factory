#!/usr/bin/env python3
"""
Workflow Health Monitor v1.0
============================

Monitors the health of all workflows:
1. Checks recent run success rates
2. Identifies failing workflows
3. Analyzes error patterns
4. Provides recommendations

GOAL: Proactive monitoring to prevent failures.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

STATE_DIR = Path("./data/persistent")
STATE_DIR.mkdir(parents=True, exist_ok=True)

HEALTH_STATE_FILE = STATE_DIR / "workflow_health.json"


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        print(re.sub(r'[^\x00-\x7F]+', '', msg))


class WorkflowHealthMonitor:
    """
    Monitors workflow health and provides insights.
    """
    
    WORKFLOWS = {
        "generate.yml": {"name": "Video Generator", "critical": True},
        "aggressive-mode.yml": {"name": "Aggressive Learning", "critical": False},
        "analytics-feedback.yml": {"name": "Analytics", "critical": False},
        "model-discovery.yml": {"name": "Model Discovery", "critical": False},
        "pre-work.yml": {"name": "Pre-Work Fetcher", "critical": False},
        "prompt-testing.yml": {"name": "Prompt Testing", "critical": False},
    }
    
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo = os.environ.get("GITHUB_REPOSITORY", "")
        self.health_data = self._load_health()
    
    def _load_health(self) -> Dict:
        try:
            if HEALTH_STATE_FILE.exists():
                with open(HEALTH_STATE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "workflows": {},
            "last_check": None,
            "alerts": []
        }
    
    def _save_health(self):
        self.health_data["last_check"] = datetime.now().isoformat()
        with open(HEALTH_STATE_FILE, 'w') as f:
            json.dump(self.health_data, f, indent=2)
    
    def check_workflow_runs(self, workflow_name: str, limit: int = 10) -> Dict:
        """Check recent runs for a workflow."""
        if not self.github_token or not requests:
            return {"error": "No GitHub token or requests library"}
        
        try:
            response = requests.get(
                f"https://api.github.com/repos/{self.repo}/actions/workflows/{workflow_name}/runs",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                params={"per_page": limit},
                timeout=10
            )
            
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            
            data = response.json()
            runs = data.get("workflow_runs", [])
            
            if not runs:
                return {"status": "no_runs", "success_rate": 0}
            
            # Analyze runs
            successful = sum(1 for r in runs if r.get("conclusion") == "success")
            failed = sum(1 for r in runs if r.get("conclusion") == "failure")
            in_progress = sum(1 for r in runs if r.get("status") == "in_progress")
            
            success_rate = successful / len(runs) if runs else 0
            
            # Get last run info
            last_run = runs[0] if runs else {}
            
            return {
                "status": "ok" if success_rate > 0.7 else ("warning" if success_rate > 0.5 else "critical"),
                "success_rate": round(success_rate * 100, 1),
                "total_runs": len(runs),
                "successful": successful,
                "failed": failed,
                "in_progress": in_progress,
                "last_run": {
                    "status": last_run.get("conclusion", "unknown"),
                    "created_at": last_run.get("created_at", ""),
                    "run_id": last_run.get("id"),
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_all_workflows(self) -> Dict:
        """Check health of all workflows."""
        results = {}
        alerts = []
        
        for workflow_file, info in self.WORKFLOWS.items():
            safe_print(f"   Checking {info['name']}...")
            result = self.check_workflow_runs(workflow_file)
            results[workflow_file] = result
            
            # Generate alerts
            if result.get("status") == "critical":
                alerts.append({
                    "workflow": info["name"],
                    "type": "critical",
                    "message": f"Success rate: {result.get('success_rate', 0)}%",
                    "is_critical": info["critical"]
                })
            elif result.get("error"):
                alerts.append({
                    "workflow": info["name"],
                    "type": "error",
                    "message": result["error"]
                })
        
        # Update health data
        self.health_data["workflows"] = results
        self.health_data["alerts"] = alerts
        self._save_health()
        
        return {
            "workflows": results,
            "alerts": alerts,
            "overall_status": "critical" if any(a.get("is_critical") for a in alerts) else 
                             ("warning" if alerts else "healthy")
        }
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on health data."""
        recommendations = []
        
        for workflow_file, result in self.health_data.get("workflows", {}).items():
            info = self.WORKFLOWS.get(workflow_file, {})
            
            if result.get("status") == "critical":
                recommendations.append(
                    f"[CRITICAL] {info.get('name', workflow_file)}: "
                    f"Only {result.get('success_rate', 0)}% success rate. "
                    f"Check error logs for run #{result.get('last_run', {}).get('run_id', 'unknown')}"
                )
            
            if result.get("failed", 0) >= 3:
                recommendations.append(
                    f"[WARNING] {info.get('name', workflow_file)}: "
                    f"{result.get('failed')} failures in last {result.get('total_runs')} runs"
                )
        
        if not recommendations:
            recommendations.append("[OK] All workflows are healthy!")
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate text health report."""
        health = self.check_all_workflows()
        
        report = [
            "=" * 50,
            "WORKFLOW HEALTH REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
            ""
        ]
        
        for workflow_file, result in health["workflows"].items():
            info = self.WORKFLOWS.get(workflow_file, {})
            status_icon = "OK" if result.get("status") == "ok" else (
                "WARN" if result.get("status") == "warning" else "FAIL"
            )
            
            report.append(f"[{status_icon}] {info.get('name', workflow_file)}")
            report.append(f"    Success Rate: {result.get('success_rate', 'N/A')}%")
            report.append(f"    Last 10 runs: {result.get('successful', 0)} OK, {result.get('failed', 0)} FAIL")
            report.append("")
        
        report.append("-" * 50)
        report.append("RECOMMENDATIONS:")
        for rec in self.get_recommendations():
            report.append(f"  {rec}")
        
        return "\n".join(report)


def check_workflow_health() -> Dict:
    """Check all workflow health."""
    monitor = WorkflowHealthMonitor()
    return monitor.check_all_workflows()


def get_health_report() -> str:
    """Get text health report."""
    monitor = WorkflowHealthMonitor()
    return monitor.generate_report()


if __name__ == "__main__":
    safe_print("Checking Workflow Health...")
    
    monitor = WorkflowHealthMonitor()
    report = monitor.generate_report()
    safe_print(report)