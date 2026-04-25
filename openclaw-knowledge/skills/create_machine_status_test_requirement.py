#!/usr/bin/env python3
"""
Skill: create_machine_status_test_requirement
Executor: One-time / ops
Creates the 24h machine status report test requirement via API.
Replaces scripts/create_machine_status_test_requirement.py.
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

LOG = get_logger("create_machine_status_test_requirement")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15

REQ_TITLE = "机器状态 24h 报告测试"
REQ_DESC = """各团队每小时上报机器状态（格式自定），Vanguard 汇总后发飞书。
流程：
1. 各团队 cron 每30分钟: python -m skills.report_machine_status --team <team>
2. Vanguard cron 每小时: python -m skills.generate_daily_report
3. 持续 24 小时
"""


def main():
    parser = argparse.ArgumentParser(description="Create 24h machine status test requirement")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--project-id", type=int, default=1, help="Project ID")
    args = parser.parse_args()
    base = args.api_base
    LOG.info("start api_base=%s project_id=%s", base, args.project_id)

    r = requests.get(f"{base}/projects", timeout=TIMEOUT)
    r.raise_for_status()
    projects = r.json()
    pid = args.project_id
    if not any(p.get("id") == pid for p in projects):
        r = requests.post(
            f"{base}/projects",
            json={
                "name": "OpenClaw Communication Test",
                "type": "tool",
                "description": "Test project for OpenClaw communication system",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        pid = r.json().get("id", 1)

    r = requests.post(
        f"{base}/requirements",
        json={
            "project_id": pid,
            "title": REQ_TITLE,
            "description": REQ_DESC,
            "priority": "P2",
            "type": "research",
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    rid = r.json().get("id")
    LOG.info("created requirement id=%s title=%s", rid, REQ_TITLE)
    print(f"Created requirement id={rid}: {REQ_TITLE}")
    print("Next: Vanguard assigns via python -m skills.assign_tasks_to_teams or POST /api/requirements/<id>/assign")
    return 0


if __name__ == "__main__":
    sys.exit(main())
