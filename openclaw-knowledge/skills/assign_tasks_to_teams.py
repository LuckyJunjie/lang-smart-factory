#!/usr/bin/env python3
"""
Skill: assign_tasks_to_teams
Executor: Vanguard
Flow: list_requirements(new/assignable) -> list_teams_online -> assign_requirement to dev teams
      -> list_requirements(developed) -> assign to Tesla -> send_feishu_message.
Can be run as cron (hourly) or by OpenClaw via MCP tools.
"""

import os
import sys
import argparse

from log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("assign_tasks_to_teams")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
DEV_TEAMS = ("jarvis", "codeforge", "newton")
TEST_TEAM = "tesla"
STEP_READY_FOR_TEST = ("test", "verify")
TIMEOUT = 15

PINNED_PROJECT_PRIORITY = {
    # Higher priority = smaller rank number
    "stock analyze": 1,
    "pinball-experience": 2,
    "smart-factory": 3,
}


def _normalize_project_name(name: str) -> str:
    if not name:
        return ""
    s = str(name).strip().lower().replace("_", " ").replace("-", " ")
    # collapse whitespace
    return " ".join(s.split())


def _project_priority_ranks(projects: list[dict]) -> dict[int, int]:
    """
    Compute a unique per-project priority rank:
    - pinned projects get fixed ranks (1/2/3)
    - all others continue from 4 in ascending project id order
    """
    ranks_by_pid: dict[int, int] = {}
    remaining: list[dict] = []

    for p in projects or []:
        if not p:
            continue
        pid = p.get("id")
        if pid is None:
            continue
        pid_int = int(pid)
        pname = _normalize_project_name(p.get("name"))
        for pinned_name, rank in PINNED_PROJECT_PRIORITY.items():
            if _normalize_project_name(pinned_name) == pname:
                ranks_by_pid[pid_int] = rank
                break
        else:
            remaining.append(p)

    remaining.sort(key=lambda x: int(x.get("id", 0)))
    next_rank = max(PINNED_PROJECT_PRIORITY.values() or [0]) + 1
    for p in remaining:
        pid_int = int(p.get("id", 0))
        if pid_int not in ranks_by_pid:
            ranks_by_pid[pid_int] = next_rank
            next_rank += 1
    return ranks_by_pid


def _priority_rank(priority: str) -> int:
    if not priority:
        return 2
    s = str(priority).strip().upper()
    if s.startswith("P"):
        try:
            return int(s[1:])
        except Exception:
            return 2
    return 2


def main():
    parser = argparse.ArgumentParser(description="Vanguard: assign tasks to dev teams and Tesla")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Do not assign or post, only print")
    parser.add_argument("--project-ids", type=str, help="Comma-separated project IDs to filter (e.g., '4,5,6,7')")
    parser.add_argument("--limit", type=int, default=0, help="Max assignments per run (0=unlimited)")
    args = parser.parse_args()
    
    # Parse project IDs filter
    filter_project_ids = None
    if args.project_ids:
        filter_project_ids = set(int(x.strip()) for x in args.project_ids.split(",") if x.strip().isdigit())
        LOG.info("filtering to project_ids: %s", filter_project_ids)
    
    base = args.api_base
    LOG.info("start api_base=%s dry_run=%s project_ids=%s", base, args.dry_run, filter_project_ids)

    try:
        # 1. Online teams
        r = requests.get(f"{base}/teams/online", timeout=TIMEOUT)
        r.raise_for_status()
        all_teams = [t for t in r.json().get("teams", []) if t and str(t).lower() != "vanguard001"]
        if not all_teams:
            LOG.info("no online teams, exit")
            print("No online teams")
            return 0
        LOG.info("online teams: %s", all_teams)
        dev_teams = [t for t in all_teams if str(t).lower() in DEV_TEAMS]
        tesla_online = any(str(t).lower() == TEST_TEAM for t in all_teams)

        # 2. Projects (for per-project priority rank)
        r = requests.get(f"{base}/projects", timeout=TIMEOUT)
        r.raise_for_status()
        projects = r.json() or []
        ranks_by_pid = _project_priority_ranks(projects)

        # 3. Requirements: new and in_progress
        r = requests.get(f"{base}/requirements", timeout=TIMEOUT)
        r.raise_for_status()
        all_reqs = r.json()

        def sort_key(req: dict) -> tuple:
            project_id = req.get("project_id")
            project_rank = ranks_by_pid.get(int(project_id)) if project_id is not None else 999999
            req_type = (req.get("type") or "").lower()
            bug_first = 0 if req_type == "bug" else 1
            pr = _priority_rank(req.get("priority"))
            created_at = req.get("created_at") or ""
            rid = req.get("id", 0) or 0
            return (project_rank, bug_first, pr, created_at, rid)

        reqs = sorted(
            [x for x in all_reqs if x.get("status") in ("new", "in_progress")],
            key=sort_key,
        )

        # Apply project filter if specified
        if filter_project_ids:
            reqs = [x for x in reqs if x.get("project_id") in filter_project_ids]
            LOG.info("filtered to project_ids, remaining reqs: %d", len(reqs))

        # Meeting/finalize may already specify assigned_team for some requirements.
        # Avoid overriding those assignments.
        pending_dev = [x for x in reqs if x.get("status") == "new" and not (x.get("assigned_team"))]
        pending_test = [x for x in reqs if x.get("status") == "in_progress" and (x.get("step") or "").lower() in STEP_READY_FOR_TEST]
        LOG.info("pending_dev=%d pending_test=%d dev_teams=%s", len(pending_dev), len(pending_test), dev_teams)

        assigned = 0
        # 3. Assign new to dev teams (round-robin)
        for i, req in enumerate(pending_dev):
            if not dev_teams:
                break
            # Respect limit
            if args.limit > 0 and assigned >= args.limit:
                break
            team = dev_teams[i % len(dev_teams)]
            rid = req["id"]
            if args.dry_run:
                LOG.info("dry-run would assign req %s to %s", rid, team)
                print(f"[dry-run] Would assign req {rid} to {team}")
                assigned += 1
                continue
            resp = requests.post(f"{base}/requirements/{rid}/assign", json={"assigned_team": team}, timeout=TIMEOUT)
            if resp.status_code == 200:
                LOG.info("assigned req %s to %s", rid, team)
                print(f"Assigned req {rid} to {team}")
                assigned += 1
            else:
                LOG.warning("assign req %s to %s failed: %s %s", rid, team, resp.status_code, resp.text[:200])

        # 4. Assign developed (test/verify) to Tesla
        for req in pending_test:
            if not tesla_online:
                break
            # Respect limit
            if args.limit > 0 and assigned >= args.limit:
                break
            rid = req["id"]
            if args.dry_run:
                LOG.info("dry-run would assign req %s (test) to %s", rid, TEST_TEAM)
                print(f"[dry-run] Would assign req {rid} (test) to {TEST_TEAM}")
                assigned += 1
                continue
            resp = requests.post(f"{base}/requirements/{rid}/assign", json={"assigned_team": TEST_TEAM}, timeout=TIMEOUT)
            if resp.status_code == 200:
                LOG.info("assigned req %s to %s (test)", rid, TEST_TEAM)
                print(f"Assigned req {rid} to {TEST_TEAM} (test)")
                assigned += 1
            else:
                LOG.warning("assign req %s to Tesla failed: %s %s", rid, resp.status_code, resp.text[:200])

        # 5. Optional: post summary to Feishu
        if assigned and not args.dry_run:
            try:
                summary = f"Vanguard 分配: 本周期分配 {assigned} 条需求。开发团队: {', '.join(dev_teams)}。Tesla 在线: {tesla_online}"
                requests.post(f"{base}/feishu/post", json={"text": summary, "title": "Vanguard 分配"}, timeout=TIMEOUT)
                LOG.info("feishu summary posted")
            except Exception as e:
                LOG.warning("feishu post failed: %s", e)
        LOG.info("done assigned=%d", assigned)
        print(f"Done. Assigned: {assigned}")
        return 0
    except requests.RequestException as e:
        LOG.exception("request failed: %s", e)
        raise


if __name__ == "__main__":
    sys.exit(main())
