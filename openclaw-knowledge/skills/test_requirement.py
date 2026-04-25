#!/usr/bin/env python3
"""
Skill: test_requirement
Executor: Tesla
Flow: get_requirement -> run_scene/run_tests (Godot or test-mcp) -> on failure create_requirement(type=bug) ->
      report_status -> on success update_requirement(tested).
"""

import os
import sys
import argparse

from .log_util import get_logger

try:
    import requests
except ImportError:
    # Pytest 会在收集阶段导入本文件（文件名以 test_ 开头），避免在导入时 sys.exit(1) 直接中断收集。
    # 真正运行该 skill 时再报错并提示安装依赖。
    requests = None

LOG = get_logger("test_requirement")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Tesla: test a requirement, create bug if needed, report and mark tested")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("requirement_id", type=int, nargs="?", help="Requirement ID to test")
    parser.add_argument("--team", default="tesla", help="Team name")
    parser.add_argument("--create-bug", action="store_true", help="Create a bug requirement (call with title/desc)")
    parser.add_argument("--title", help="Bug title (for --create-bug)")
    parser.add_argument("--description", default="", help="Bug description")
    parser.add_argument("--mark-tested", action="store_true", help="Set requirement as tested (step=verified)")
    args = parser.parse_args()
    base = args.api_base
    if requests is None:
        raise SystemExit("Missing dependency: requests. Please install it before running this skill.")
    LOG.info("start requirement_id=%s team=%s api_base=%s create_bug=%s mark_tested=%s", args.requirement_id, args.team, base, args.create_bug, args.mark_tested)

    if args.create_bug:
        if not args.title:
            LOG.warning("--create-bug requires --title")
            print("--create-bug requires --title", file=sys.stderr)
            return 1
        r = requests.post(
            f"{base}/requirements",
            json={
                "title": args.title,
                "description": args.description,
                "type": "bug",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        LOG.info("created bug requirement id=%s", data.get("id"))
        print("Created bug requirement:", data.get("id"))
        return 0

    if not args.requirement_id:
        r = requests.get(f"{base}/teams/{args.team}/assigned-requirements", timeout=TIMEOUT)
        r.raise_for_status()
        reqs = r.json()
        LOG.info("assigned to Tesla: %s", [x.get("id") for x in reqs])
        print("Assigned to Tesla:", [x.get("id") for x in reqs])
        return 0

    req = requests.get(f"{base}/requirements/{args.requirement_id}", timeout=TIMEOUT).json()
    LOG.info("testing requirement id=%s title=%s", args.requirement_id, req.get("title"))
    print("Testing requirement:", req.get("title"))

    if args.mark_tested:
        requests.patch(
            f"{base}/requirements/{args.requirement_id}",
            json={"status": "in_progress", "step": "verify"},
            timeout=TIMEOUT,
        )
        requests.post(
            f"{base}/teams/{args.team}/status-report",
            json={"team": args.team, "requirement_id": args.requirement_id, "step": "verify", "progress_percent": 100},
            timeout=TIMEOUT,
        )
        LOG.info("marked as tested")
        print("Marked as tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
