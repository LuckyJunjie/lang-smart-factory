#!/usr/bin/env python3
"""
Seed 24h workflow test requirements and tasks from 24H_WORKFLOW_TEST_DESIGN.md.
Aligns with OPENCLAW_COMMUNICATION_SYSTEM: assign → take → analyse → implement;
encoding per REQUIREMENTS.md 2.0: {req_id:04d}-{project_slug}-{req_slug}-{progress}[-{task_id:04d}].

Usage:
  python seed_24h_workflow_requirements.py [--db PATH]
  Default DB: db/factory.db
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

# Project slug for encoding
PROJECT_NAME = "smart-factory"
PLAN_STEP_ID = "24h"

REQUIREMENTS = [
    {
        "title": "REQ-A: API 与需求模块健康检查清单",
        "assigned_team": "jarvis",
        "description": "对 /api/、/api/requirements、/api/tasks 等做可用性检查，列出健康项与改进建议。产出：API 与需求模块健康检查与改进建议清单。",
        "tasks": [
            ("分析需求并输出任务拆解方案", "athena"),
            ("分配任务给成员并平衡负载", "chiron"),
            ("检查 API 发现与根端点", "hermes"),
            ("检查 requirements/tasks 相关端点", "cerberus"),
            ("整理清单格式与可读性", "apollo"),
            ("【决策】不一致处理与上报", "cerberus"),
        ],
    },
    {
        "title": "REQ-B: 测试与质量健康检查清单",
        "assigned_team": "codeforge",
        "description": "测试环境、用例覆盖、质量门禁等检查项与改进建议。产出：测试与质量健康检查与改进建议清单。",
        "tasks": [
            ("分析需求并输出任务拆解方案", "pangu"),
            ("分配任务给成员并平衡负载", "shennong"),
            ("检查测试环境与用例覆盖", "nuwa"),
            ("检查质量门禁与自动化", "yu"),
            ("整理清单格式与可读性", "luban"),
            ("【决策】测试环境缺失或方案可选时上报", "nuwa"),
        ],
    },
    {
        "title": "REQ-C: 部署与机器状态健康检查清单",
        "assigned_team": "newton",
        "description": "部署流程、机器/团队状态上报、在线判定等检查与改进建议。产出：部署与机器状态健康检查与改进建议清单。",
        "tasks": [
            ("分析需求并输出任务拆解方案", "einstein"),
            ("分配任务给成员并平衡负载", "darwin"),
            ("检查部署流程与机器状态 API", "curie"),
            ("检查团队状态上报与在线判定", "galileo"),
            ("整理清单格式与可读性", "hawking"),
            ("【决策】上报频率与 active 定义冲突时上报", "darwin"),
        ],
    },
    {
        "title": "REQ-D: 文档与通信流程健康检查清单",
        "assigned_team": "tesla",
        "description": "文档完整性、飞书/状态上报/风险报告等流程检查与改进建议。产出：文档与通信流程健康检查与改进建议清单。",
        "tasks": [
            ("分析需求并输出任务拆解方案", "model_s"),
            ("分配任务给成员并平衡负载", "model_3"),
            ("检查文档完整性与一致性", "model_x"),
            ("检查飞书/status-report/risk-report 流程", "model_y"),
            ("整理清单格式与可读性", "cybertruck"),
            ("【决策】文档过时或两方案可选时上报", "model_y"),
        ],
    },
]


def get_db_path(db_path: str) -> str:
    # openclaw-knowledge/scripts → repo root → core/db/factory.db
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    core_db = os.path.join(repo_root, "core", "db")
    if os.path.isabs(db_path):
        return db_path
    if db_path == "factory.db" or not db_path:
        return os.path.join(core_db, "factory.db")
    return os.path.normpath(os.path.join(repo_root, db_path))


def ensure_project(conn: sqlite3.Connection) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE name = ?", (PROJECT_NAME,))
    row = c.fetchone()
    if row:
        return row[0]
    c.execute(
        """INSERT INTO projects (name, description, type, status)
           VALUES (?, ?, ?, ?)""",
        (PROJECT_NAME, "24h 流程演练与 OpenClaw 通信系统测试", "tool", "active"),
    )
    conn.commit()
    return c.lastrowid


def close_old_24h_test_requirements(conn: sqlite3.Connection) -> None:
    """Close any old 24h machine-status style test requirements so only new 4 remain active."""
    c = conn.cursor()
    c.execute(
        "UPDATE requirements SET status = 'closed', updated_at = ? WHERE title LIKE ? OR title LIKE ?",
        (datetime.utcnow().isoformat(), "%机器状态%24%", "%24h%报告%"),
    )
    if c.rowcount:
        conn.commit()


def insert_requirement(conn: sqlite3.Connection, project_id: int, r: dict) -> int:
    c = conn.cursor()
    c.execute(
        """INSERT INTO requirements (
             project_id, title, description, priority, type, status,
             assigned_team, plan_step_id, step, progress_percent
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            project_id,
            r["title"],
            r["description"],
            "P2",
            "feature",
            "new",
            r["assigned_team"],
            PLAN_STEP_ID,
            "not start",
            0,
        ),
    )
    conn.commit()
    return c.lastrowid


def insert_tasks(conn: sqlite3.Connection, req_id: int, tasks: list) -> None:
    c = conn.cursor()
    for title, executor in tasks:
        c.execute(
            """INSERT INTO tasks (req_id, title, description, status, executor)
               VALUES (?, ?, ?, ?, ?)""",
            (req_id, title, "", "todo", executor),
        )
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed 24h workflow requirements and tasks")
    parser.add_argument("--db", default=None, help="Path to factory.db (default: db/factory.db)")
    args = parser.parse_args()
    db_path = get_db_path(args.db or "factory.db")
    if not os.path.isfile(db_path):
        print(f"DB not found: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    try:
        close_old_24h_test_requirements(conn)
        project_id = ensure_project(conn)
        created = []
        for r in REQUIREMENTS:
            rid = insert_requirement(conn, project_id, r)
            insert_tasks(conn, rid, r["tasks"])
            created.append((rid, r["title"], r["assigned_team"]))
        for rid, title, team in created:
            code = f"{rid:04d}-{PROJECT_NAME}-{title[:20].replace(' ', '-').replace(':', '')}-{PLAN_STEP_ID}"
            print(f"Requirement {rid}: {title} -> {team} (code style: {code})")
        print("Done. Teams can: GET /api/teams/<team>/assigned-requirements then POST /api/requirements/<id>/take")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
