#!/usr/bin/env python3
"""
Skill: report_machine_status
Executor: Each team (Jarvis, CodeForge, Newton, Tesla)
Flow: Build payload (default: hostname, platform, team) -> POST /api/teams/<team>/machine-status.
Run every 30 min via cron. Replaces scripts/team_report_machine_status.py.
"""

import argparse
import json
import os
import platform
import socket
import sys

from .log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("report_machine_status")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def default_payload(team: str) -> dict:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "team": team,
        "reported_by": "cron",
    }


def main():
    parser = argparse.ArgumentParser(description="Team: report machine status")
    parser.add_argument("--team", required=True, help="Team name (jarvis, codeforge, newton, tesla)")
    parser.add_argument("--payload", default=None, help="JSON payload (or use default)")
    parser.add_argument("--reporter", default="cron", help="Reporter agent name")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    args = parser.parse_args()
    base = args.api_base
    team = args.team
    LOG.info("start team=%s api_base=%s reporter=%s", team, base, args.reporter)

    payload = default_payload(team)
    if args.payload:
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as e:
            LOG.warning("invalid JSON payload: %s", e)
            print(f"Invalid JSON payload: {e}", file=sys.stderr)
            return 1

    r = requests.post(
        f"{base}/teams/{team}/machine-status",
        json={"payload": payload, "reporter_agent": args.reporter},
        timeout=TIMEOUT,
    )
    if r.status_code == 200:
        LOG.info("reported machine status for %s", team)
        print(f"Reported machine status for {team}")
    else:
        LOG.warning("report machine status failed: %s %s", r.status_code, r.text[:200])
        print(f"Failed: {r.text}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
