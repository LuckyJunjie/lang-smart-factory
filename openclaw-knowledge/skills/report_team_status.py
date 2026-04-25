#!/usr/bin/env python3
"""
Skill: report_team_status
Executor: Each team (Jarvis, CodeForge, Newton, Tesla)
Flow: get_team_assigned(in_progress) -> get requirement tasks -> POST status-report with payload.
Run every 30 min via cron or by team agent. Replaces scripts/team_report_status.py.
"""

import os
import sys
import argparse

from .log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("report_team_status")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Team: report status with task details to Hera")
    parser.add_argument("--team", required=True, help="Team name (jarvis, codeforge, newton, tesla)")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--reporter", default="cron", help="Reporter agent name")
    args = parser.parse_args()
    base = args.api_base
    team = args.team
    LOG.info("start team=%s api_base=%s reporter=%s", team, base, args.reporter)

    r = requests.get(
        f"{base}/teams/{team}/assigned-requirements",
        params={"status": "in_progress"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    reqs = r.json()
    req = reqs[0] if reqs else None

    payload = {"team": team}
    if req:
        rid = req["id"]
        payload["requirement_id"] = rid
        payload["requirement_title"] = req.get("title", "")
        payload["progress_percent"] = req.get("progress_percent", 0)
        payload["step"] = req.get("step", "")
        rt = requests.get(f"{base}/requirements/{rid}/tasks", timeout=TIMEOUT)
        if rt.status_code == 200:
            payload["tasks"] = [
                {
                    "id": t["id"],
                    "title": t.get("title", ""),
                    "status": t.get("status", ""),
                    "executor": t.get("executor", ""),
                }
                for t in rt.json()
            ]
        else:
            payload["tasks"] = []
    else:
        payload["requirement_id"] = None
        payload["tasks"] = []

    r = requests.post(
        f"{base}/teams/{team}/status-report",
        json={"payload": payload, "reporter_agent": args.reporter},
        timeout=TIMEOUT,
    )
    if r.status_code == 200:
        LOG.info("reported status for %s", team)
        print(f"Reported status for {team}")
    else:
        LOG.warning("report status failed: %s %s", r.status_code, r.text[:200])
        print(f"Failed: {r.text}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
