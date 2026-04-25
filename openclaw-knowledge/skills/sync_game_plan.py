#!/usr/bin/env python3
"""
Skill: sync_game_plan
Executor: Vanguard / ops (on server where Smart Factory DB lives)
Syncs pinball-experience BASELINE_STEPS and FEATURE_STEPS to Smart Factory DB.
Run: python -m skills.sync_game_plan [--dry-run]
Or use project_mcp tool: sync_pinball_plan()
"""

import os
import sys
import argparse

# Ensure repo root on path
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from .log_util import get_logger
from mcp.remote.project_mcp import sync_plan

LOG = get_logger("sync_game_plan")


def main():
    parser = argparse.ArgumentParser(description="Sync pinball-experience plan to Smart Factory DB")
    parser.add_argument("--dry-run", action="store_true", help="Only check DB path, do not write")
    args = parser.parse_args()
    LOG.info("start dry_run=%s", args.dry_run)

    if args.dry_run:
        db_path = sync_plan.get_db_path()
        exists = os.path.exists(db_path)
        LOG.info("dry_run db_path=%s exists=%s", db_path, exists)
        print(f"DB path: {db_path}")
        print(f"Exists: {exists}")
        return 0 if exists else 1

    result = sync_plan.run_sync()
    if not result["success"]:
        LOG.warning("sync failed: %s", result.get("error", "Sync failed"))
        print(result.get("error", "Sync failed"), file=sys.stderr)
        return 1
    LOG.info("synced project_id=%s created=%s updated=%s total=%s", result["project_id"], result["created"], result["updated"], result["total"])
    print(f"Synced pinball-experience (project_id={result['project_id']})")
    print(f"  Created: {result['created']}, Updated: {result['updated']}, Total: {result['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
