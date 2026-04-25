#!/usr/bin/env python3
"""
Skill: develop_requirement
Executor: Dev team (Jarvis/CodeForge/Newton)
Flow: get_requirement -> read files / analyze -> (agent implements via dev-mcp) -> run_tests -> report_status -> update_requirement(developed).
This module provides the API glue; actual code edits and tests are done by the agent or local MCPs.
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

LOG = get_logger("develop_requirement")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def get_requirement(requirement_id: int, base: str = None) -> dict:
    base = base or API_BASE
    r = requests.get(f"{base}/requirements/{requirement_id}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def report_status(team: str, requirement_id: int, progress: int = None, step: str = None, tasks: list = None, base: str = None) -> dict:
    base = base or API_BASE
    body = {"team": team, "requirement_id": requirement_id}
    if progress is not None:
        body["progress_percent"] = progress
    if step:
        body["step"] = step
    if tasks is not None:
        body["tasks"] = tasks
    r = requests.post(f"{base}/teams/{team}/status-report", json=body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def update_requirement(requirement_id: int, fields: dict, base: str = None) -> dict:
    base = base or API_BASE
    r = requests.patch(f"{base}/requirements/{requirement_id}", json=fields, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def main():
    parser = argparse.ArgumentParser(description="Dev team: fetch requirement and report progress (rest is agent/MCP)")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("requirement_id", type=int, nargs="?", help="Requirement ID")
    parser.add_argument("--team", default="jarvis", help="Team name")
    parser.add_argument("--progress", type=int, help="Progress percent to report")
    parser.add_argument("--step", help="Step (e.g. implement, test)")
    parser.add_argument("--mark-developed", action="store_true", help="Set status=in_progress step=test when done")
    args = parser.parse_args()
    base = args.api_base
    LOG.info("start requirement_id=%s team=%s api_base=%s", args.requirement_id, args.team, base)

    if not args.requirement_id:
        # List assigned for team
        r = requests.get(f"{base}/teams/{args.team}/assigned-requirements", timeout=TIMEOUT)
        r.raise_for_status()
        reqs = r.json()
        LOG.info("assigned requirements: %s", [x.get("id") for x in reqs])
        print("Assigned requirements:", [x.get("id") for x in reqs])
        return 0

    req = get_requirement(args.requirement_id, base)
    LOG.info("requirement: id=%s title=%s status=%s step=%s", args.requirement_id, req.get("title"), req.get("status"), req.get("step"))
    print("Requirement:", req.get("title"), "| status:", req.get("status"), "| step:", req.get("step"))

    if args.progress is not None or args.step:
        report_status(args.team, args.requirement_id, progress=args.progress, step=args.step, base=base)
        LOG.info("status reported progress=%s step=%s", args.progress, args.step)
        print("Status reported.")

    if args.mark_developed:
        update_requirement(args.requirement_id, {"status": "in_progress", "step": "test"}, base=base)
        LOG.info("marked as developed (step=test)")
        print("Marked as developed (step=test).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
