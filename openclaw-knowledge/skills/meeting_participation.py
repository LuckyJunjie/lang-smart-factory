#!/usr/bin/env python3
"""
Skill: meeting_participation
Executor: All agents
Flow:
  1) GET /api/meetings/for-agent?agent=<agent>&status=running
  2) If my input not submitted for current_round:
       - print meeting topic/problem/contribute_focus
       - (optional) POST /api/meetings/<id>/inputs to submit analysis/comments
Run every 15 minutes via cron/heartbeat for meeting participation.
"""

import os
import sys
import argparse

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

from log_util import get_logger

LOG = get_logger("meeting_participation")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Meeting participation heartbeat")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL (default: env SMART_FACTORY_API)")
    parser.add_argument("--agent", required=True, help="This agent id (e.g. hera, vanguard001, athena)")
    parser.add_argument("--status", default="running", help="Meeting status filter (default: running)")
    parser.add_argument("--submit", action="store_true", help="If set, submit analysis/comments via API")
    parser.add_argument("--analysis", default=None, help="analysis text (required when --submit)")
    parser.add_argument("--comments", default=None, help="comments text (required when --submit)")
    parser.add_argument("--round_number", type=int, default=None, help="Override round_number (default: meeting.current_round)")
    parser.add_argument("--dry-run", action="store_true", help="Do not post inputs; only print")
    args = parser.parse_args()

    base = args.api_base
    agent = args.agent
    LOG.info("start agent=%s api_base=%s submit=%s dry_run=%s", agent, base, args.submit, args.dry_run)

    r = requests.get(
        f"{base}/meetings/for-agent",
        params={"agent": agent, "status": args.status},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    meetings = r.json() or []

    if not meetings:
        LOG.info("no running meetings for this agent")
        print("HEARTBEAT_OK")
        return 0

    for item in meetings:
        mid = item.get("id")
        cur_round = item.get("current_round")
        my_participant = item.get("my_participant") or {}
        contribute_focus = my_participant.get("contribute_focus") or ""
        topic = item.get("topic") or ""
        problem = item.get("problem_to_solve") or ""
        needs = item.get("needs_your_input")

        if not needs:
            continue

        print(f"=== Meeting for {agent} ===")
        print(f"meeting_id={mid} round={cur_round}")
        print(f"topic={topic}")
        print(f"problem_to_solve={problem}")
        print(f"contribute_focus={contribute_focus}")

        if args.submit:
            if not args.analysis or args.comments is None:
                raise SystemExit("--submit requires --analysis and --comments")
            if args.dry_run:
                print("[dry-run] would POST inputs")
                continue
            round_to_use = args.round_number or cur_round
            rp = requests.post(
                f"{base}/meetings/{mid}/inputs",
                json={
                    "agent_id": agent,
                    "round_number": round_to_use,
                    "analysis": args.analysis,
                    "comments": args.comments,
                },
                timeout=TIMEOUT,
            )
            rp.raise_for_status()
            LOG.info("submitted meeting inputs meeting_id=%s agent=%s round=%s", mid, agent, round_to_use)

    return 0


if __name__ == "__main__":
    sys.exit(main())

