#!/usr/bin/env python3
"""
Skill: generate_daily_report
Executor: Vanguard
Flow: risk-report -> status-report/summary (with task details) -> development-details/summary
      -> machine-status/summary -> send_feishu_message.
Replaces scripts/vanguard_post_feishu_summary.py; same content (task details, dev details).
"""

import json
import os
import sys
import argparse
from datetime import datetime

from .log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("generate_daily_report")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Vanguard: generate daily report and post to Feishu")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Print only, do not post to Feishu")
    parser.add_argument("--machine-only", action="store_true", help="Only machine status, no task details")
    args = parser.parse_args()
    base = args.api_base
    LOG.info("start api_base=%s dry_run=%s machine_only=%s", base, args.dry_run, args.machine_only)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📊 Smart Factory 状态汇总 {now}", ""]

    # 1. Risk report (Hera)
    try:
        r = requests.get(f"{base}/dashboard/risk-report", timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            risks = data.get("risks", [])
            if risks:
                lines.append("⚠️ 风险提示 (Hera):")
                for risk in risks[:5]:
                    lines.append(f"  - {risk.get('type', '?')}: {risk}")
                lines.append("")
    except Exception:
        pass

    # 2. Team status reports (with task details)
    if not args.machine_only:
        try:
            r = requests.get(f"{base}/teams/status-report/summary", timeout=TIMEOUT)
            if r.status_code == 200:
                reports = r.json()
                if reports:
                    lines.append("📋 团队状态 (含任务明细):")
                    for rep in reports:
                        team = rep.get("team", "?")
                        active = rep.get("active", True)
                        payload = rep.get("payload", "{}")
                        try:
                            p = json.loads(payload) if isinstance(payload, str) else payload
                        except Exception:
                            p = {}
                        reported_at = (rep.get("reported_at") or "")[:19]
                        status_label = " (offline)" if not active else ""
                        lines.append(f"【{team}】 {reported_at}{status_label}")
                        req_title = p.get("requirement_title") or p.get("requirement_id") or "-"
                        lines.append(f"  需求: {req_title} | 进度: {p.get('progress_percent', 0)}% | step: {p.get('step', '-')}")
                        for t in p.get("tasks", [])[:5]:
                            line = f"    - {t.get('title', '?')} [{t.get('status', '?')}] {t.get('executor', '')}"
                            if t.get("analysis_notes"):
                                line += f" | 分析: {str(t['analysis_notes'])[:80]}"
                            if t.get("assignment_notes"):
                                line += f" | 分配: {str(t['assignment_notes'])[:60]}"
                            if t.get("development_notes"):
                                line += f" | 开发: {str(t['development_notes'])[:80]}"
                            lines.append(line)
                        lines.append("")
        except Exception:
            pass

    # 2b. Development details (analysis / assignment / development per task)
    if not args.machine_only:
        try:
            r = requests.get(f"{base}/teams/development-details/summary", params={"per_team": 25}, timeout=TIMEOUT)
            if r.status_code == 200:
                dev_summary = r.json()
                for team_block in dev_summary:
                    details = team_block.get("details") or []
                    if not details:
                        continue
                    team = team_block.get("team", "?")
                    lines.append(f"📝 【{team}】开发过程细节:")
                    type_label = {"analysis": "分析", "assignment": "分配", "development": "开发"}
                    for d in details[:15]:
                        dt = d.get("detail_type", "?")
                        content = (d.get("content") or "")[:120]
                        req_id = d.get("requirement_id", "?")
                        task_id = d.get("task_id", "?")
                        reported = (d.get("reported_at") or "")[:16]
                        lines.append(f"  req{req_id} task{task_id} [{type_label.get(dt, dt)}] {reported}: {content}")
                    lines.append("")
        except Exception:
            pass

    # 3. Machine status
    try:
        r = requests.get(f"{base}/teams/machine-status/summary", timeout=TIMEOUT)
        r.raise_for_status()
        reports = r.json()
        if reports:
            lines.append("🖥️ 机器状态:")
            for rep in reports:
                team = rep.get("team", "?")
                payload = rep.get("payload", "{}")
                try:
                    p = json.loads(payload) if isinstance(payload, str) else payload
                except Exception:
                    p = {"raw": str(payload)[:100]}
                reported_at = (rep.get("reported_at") or "")[:19]
                lines.append(f"【{team}】 {reported_at}")
                for k, v in p.items():
                    if k not in ("requirement_id", "requirement_title", "tasks"):
                        lines.append(f"  {k}: {v}")
            lines.append("")
    except Exception:
        if len(lines) <= 2:
            lines.append("暂无团队上报")

    report = "\n".join(lines)
    print(report)
    LOG.info("report built lines=%d", len(lines))

    if args.dry_run:
        LOG.info("dry_run exit")
        return 0

    try:
        r = requests.post(
            f"{base}/feishu/post",
            json={"text": report, "title": "Smart Factory 状态汇总"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200 and r.json().get("success"):
            LOG.info("posted to Feishu")
            print("Posted to Feishu.")
        else:
            LOG.warning("feishu post failed: %s %s", r.status_code, r.text[:200])
            print(f"Feishu post failed: {r.text}", file=sys.stderr)
            return 1
    except Exception as e:
        LOG.exception("feishu post failed: %s", e)
        print(f"Feishu post failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
