#!/usr/bin/env python3
"""
Skill: team_sync
Executor: Each team (Jarvis, CodeForge, Newton, Tesla)
Flow: get_team_assigned(in_progress) -> if none, get_team_assigned(new) -> take_requirement(first).
Run hourly via cron or by team agent via project-mcp. Replaces scripts/team_sync.py.
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

LOG = get_logger("team_sync")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Team: sync assigned requirements, take one if free")
    parser.add_argument("--team", required=True, help="Team name (jarvis, codeforge, newton, tesla)")
    parser.add_argument("--assigned-agent", default=None, help="Agent to assign when taking (default: team name)")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Do not take, only print")
    args = parser.parse_args()
    base = args.api_base
    team = args.team
    LOG.info("start team=%s api_base=%s dry_run=%s", team, base, args.dry_run)

    # 1. Already have in_progress? (one team one requirement at a time)
    r = requests.get(
        f"{base}/teams/{team}/assigned-requirements",
        params={"status": "in_progress"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    if r.json():
        LOG.info("already have in-progress requirement, skip")
        print("Already have in-progress requirement, skip taking")
        return 0

    # 2. Get assigned (new) requirements
    r = requests.get(
        f"{base}/teams/{team}/assigned-requirements",
        params={"status": "new"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    reqs = r.json()
    if not reqs:
        LOG.info("no assigned requirements to take")
        print("No assigned requirements to take")
        return 0

    rid = reqs[0]["id"]
    # Meeting/finalize 可能会预先写入 requirements.assigned_agent；优先使用该值。
    agent_to_take = args.assigned_agent or reqs[0].get("assigned_agent") or team
    if args.dry_run:
        LOG.info("dry-run would take req %s as %s", rid, agent_to_take)
        print(f"[dry-run] Would take req {rid} as {agent_to_take}")
        return 0

    r = requests.post(
        f"{base}/requirements/{rid}/take",
        json={"assigned_team": team, "assigned_agent": agent_to_take},
        timeout=TIMEOUT,
    )
    if r.status_code == 200:
        LOG.info("took req %s", rid)
        print(f"Took req {rid}")
    else:
        LOG.warning("take req %s failed: %s %s", rid, r.status_code, r.text[:200])
        print(f"Failed to take req {rid}: {r.text}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
