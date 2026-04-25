#!/usr/bin/env python3
"""
Skill: handle_blockage
Executor: Hera
Flow: list_blockages(pending) -> get_requirement for each -> decide -> assign_requirement or
      update_requirement(blocked) -> resolve_blockage -> optional send_feishu_message.
Run every 15 min (cron) or by Hera agent via MCP.
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

LOG = get_logger("handle_blockage")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main():
    parser = argparse.ArgumentParser(description="Hera: resolve blockages")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Only list, do not resolve")
    args = parser.parse_args()
    base = args.api_base
    LOG.info("start api_base=%s dry_run=%s", base, args.dry_run)

    r = requests.get(f"{base}/discussion/blockages", params={"status": "pending"}, timeout=TIMEOUT)
    r.raise_for_status()
    blockages = r.json()
    if not blockages:
        LOG.info("no pending blockages")
        print("No pending blockages")
        return 0

    LOG.info("pending blockages: %d", len(blockages))
    print(f"Pending blockages: {len(blockages)}")
    def default_meeting_participants(team: str):
        base = [
            {
                "agent_id": "vanguard001",
                "role_label": "meeting_coordinator",
                "contribute_focus": "协调整合结论，必要时给出需求任务创建与分配建议",
            },
            {
                "agent_id": "hera",
                "role_label": "host",
                "contribute_focus": "主持会诊并汇总各方输入，最终形成可落地的结论/决策并 finalize 会议",
            },
        ]
        mapping = {
            "jarvis": [
                {"agent_id": "athena", "role_label": "architect", "contribute_focus": "技术方案分析、依赖关系与风险评估"},
                {"agent_id": "chiron", "role_label": "scrum_master", "contribute_focus": "拆分可执行子任务/需求与优先级建议"},
                {"agent_id": "hermes", "role_label": "devops", "contribute_focus": "环境/工具可行性排查与运维风险评估"},
            ],
            "codeforge": [
                {"agent_id": "pangu", "role_label": "architect", "contribute_focus": "技术方案分析、依赖关系与风险评估"},
                {"agent_id": "shennong", "role_label": "scrum_master", "contribute_focus": "拆分可执行子任务/需求与优先级建议"},
                {"agent_id": "yu", "role_label": "devops", "contribute_focus": "环境/工具可行性排查与运维风险评估"},
            ],
            "newton": [
                {"agent_id": "einstein", "role_label": "architect", "contribute_focus": "技术方案分析、依赖关系与风险评估"},
                {"agent_id": "darwin", "role_label": "scrum_master", "contribute_focus": "拆分可执行子任务/需求与优先级建议"},
                {"agent_id": "hawking", "role_label": "dev", "contribute_focus": "实现路径可行性与测试/验收建议"},
            ],
            "tesla": [
                {"agent_id": "model_s", "role_label": "architect", "contribute_focus": "测试策略/复杂场景技术评估"},
                {"agent_id": "model_y", "role_label": "scrum_master", "contribute_focus": "拆分测试/验证子任务与优先级建议"},
                {"agent_id": "cybertruck", "role_label": "devops", "contribute_focus": "测试环境/自动化执行可行性评估"},
            ],
        }
        return base + mapping.get(str(team).lower(), [])

    for b in blockages:
        bid = b.get("id")
        team = b.get("team")
        rid = b.get("requirement_id")
        reason = b.get("reason", "")[:200]
        meeting_id = b.get("meeting_id")
        # Get requirement context
        try:
            req = requests.get(f"{base}/requirements/{rid}", timeout=TIMEOUT).json()
            title = req.get("title", "?")
        except Exception:
            title = "?"
        print(f"  Blockage {bid}: team={team} req={rid} ({title}) reason={reason}")

        if args.dry_run:
            continue

        # 1) If a meeting already exists, resolve only after meeting is concluded.
        if meeting_id:
            try:
                m = requests.get(f"{base}/meetings/{meeting_id}", timeout=TIMEOUT).json()
                meeting = m.get("meeting") or m
                if meeting and meeting.get("status") == "concluded":
                    decision = meeting.get("conclusion_summary") or meeting.get("conclusion_decision") or "Meeting concluded."
                    requests.patch(
                        f"{base}/discussion/blockage/{bid}",
                        json={"status": "resolved", "decision": decision},
                        timeout=TIMEOUT,
                    )
                    LOG.info("resolved blockage %s via meeting %s", bid, meeting_id)
                    print(f"  Resolved {bid} (meeting {meeting_id})")
                else:
                    LOG.info("blockage %s waiting meeting %s status=%s", bid, meeting_id, meeting.get("status") if meeting else "?")
            except Exception as e:
                LOG.warning("failed to check meeting for blockage %s: %s", bid, e)
            continue

        # 2) No meeting yet: create one for multi-agent diagnosis.
        participants = default_meeting_participants(team)
        topic = f"阻塞会诊: {title}"
        problem_to_solve = f"需求 {rid} 遇阻塞：{reason}"

        try:
            r = requests.post(
                f"{base}/meetings",
                json={
                    "topic": topic,
                    "problem_to_solve": problem_to_solve,
                    "host_agent": "hera",
                    "initiated_by_agent": "hera",
                    "current_round": 1,
                    "participants": participants,
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            meeting_created = r.json()
            new_mid = meeting_created.get("meeting_id")
            if new_mid:
                requests.patch(
                    f"{base}/discussion/blockage/{bid}",
                    json={"meeting_id": new_mid},
                    timeout=TIMEOUT,
                )
                LOG.info("created meeting %s for blockage %s", new_mid, bid)
                print(f"  Created meeting {new_mid} for blockage {bid}")
        except Exception as e:
            LOG.warning("failed to create meeting for blockage %s: %s", bid, e)
    LOG.info("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
