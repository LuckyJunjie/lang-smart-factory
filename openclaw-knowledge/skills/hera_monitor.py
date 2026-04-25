#!/usr/bin/env python3
"""
Skill: hera_monitor
Executor: Hera
Flow: GET risk-report + GET blockages(pending) -> print or optionally post to Feishu.
Run every 15–30 min via cron for visibility. For resolution use handle_blockage.
Replaces scripts/hera_monitor.py.
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

LOG = get_logger("hera_monitor")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Hera: monitor risks and pending blockages (read-only)")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Do not post, only print (always true for this skill)")
    args = parser.parse_args()
    base = args.api_base
    LOG.info("start api_base=%s dry_run=%s", base, args.dry_run)

    r = requests.get(f"{base}/dashboard/risk-report", timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    risks = data.get("risks", [])

    try:
        rb = requests.get(f"{base}/discussion/blockages", params={"status": "pending"}, timeout=TIMEOUT)
        blockages = rb.json() if rb.status_code == 200 else []
    except Exception:
        blockages = []

    if not risks and not blockages:
        LOG.info("no risks or pending blockages")
        print("No risks or pending blockages")
        return 0

    LOG.info("risks=%d blockages=%d", len(risks), len(blockages))
    if risks:
        report = "\n".join([f"- {x.get('type', '?')}: {x}" for x in risks])
        print("Risks:\n" + report)
    if blockages:
        print("Pending blockages (Hera resolve via handle_blockage or PATCH /api/discussion/blockage/<id>):")
        for b in blockages:
            print(
                f"  id={b.get('id')} team={b.get('team')} req={b.get('requirement_id')} "
                f"reason={str(b.get('reason', ''))[:60]}"
            )
    LOG.info("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
