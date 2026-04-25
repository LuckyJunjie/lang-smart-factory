#!/usr/bin/env python3
"""
Seed Smart Factory DB: projects, machines, pinball-experience requirements (from plan),
24h workflow requirements (from 24H_WORKFLOW_TEST_DESIGN.md). Other projects added as archive.

Rules:
- pinball-experience: requirements from /Users/junjiepan/Game/pinball-experience/plan (baseline + feature steps)
- 24h experiment: requirements from docs/24H_WORKFLOW_TEST_DESIGN.md (REQ-A/B/C/D)
- smart-factory: active project, no new requirements
- Other projects: add as archive

Usage:
  cd smart-factory && python3 scripts/seed_factory_data.py [--db PATH] [--init]
  On Pi (if DB is in workspace): python3 scripts/seed_factory_data.py --db /home/pi/.openclaw/workspace/db/factory.db [--init]
  --init: create DB and run schema+migrations if DB missing (otherwise assumes DB exists).
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

# Paths: openclaw-knowledge/scripts/this.py → repo root → core/db
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
_CORE_DB = os.path.join(_REPO_ROOT, "core", "db")

# ---------- Pinball-experience: baseline steps (0.1–0.10) from BASELINE-STEPS.md ----------
PINBALL_BASELINE = [
    ("Step 0.1 – Primitive playable (launcher + flippers)", "0.1"),
    ("Step 0.2 – Drain", "0.2"),
    ("Step 0.3 – Walls and boundaries", "0.3"),
    ("Step 0.4 – Obstacles / bumpers (basic scoring)", "0.4"),
    ("Step 0.5 – Rounds and game over", "0.5"),
    ("Step 0.6 – Skill shot", "0.6"),
    ("Step 0.7 – Multiplier", "0.7"),
    ("Step 0.8 – Multiball", "0.8"),
    ("Step 0.9 – Combo (optional; not in target)", "0.9"),
    ("Step 0.10 – Polish (physics, animation, audio)", "0.10"),
]

# ---------- Pinball-experience: feature steps (2.1–2.44) from FEATURE-STEPS.md ----------
PINBALL_FEATURE = [
    ("Step 2.1 – Start flow: initial → play", "2.1"),
    ("Step 2.2 – Game state and scoring (requirements shape)", "2.2"),
    ("Step 2.3 – Point values and skill shot (I/O values)", "2.3"),
    ("Step 2.4 – Character selection", "2.4"),
    ("Step 2.5 – How to Play screen", "2.5"),
    ("Step 2.6 – HUD (score, multiplier, rounds)", "2.6"),
    ("Step 2.7 – Camera (waiting / playing / game over)", "2.7"),
    ("Step 2.8 – Google rollovers (5k each)", "2.8"),
    ("Step 2.9 – Google Word letters and spell Google", "2.9"),
    ("Step 2.10 – Bonus ball (5s) from Google Word / Dash Nest", "2.10"),
    ("Step 2.11 – Multiball indicators (4)", "2.11"),
    ("Step 2.12 – SpaceshipRamp (5k shot, ramp bonus, multiplier)", "2.12"),
    ("Step 2.13 – Android Acres rail", "2.13"),
    ("Step 2.14 – Android bumpers A / B / COW (20k each)", "2.14"),
    ("Step 2.15 – AndroidSpaceship target (200k + bonus)", "2.15"),
    ("Step 2.16 – ChromeDino mouth (200k + dinoChomp)", "2.16"),
    ("Step 2.17 – DinoWalls (bonus ball spawn position)", "2.17"),
    ("Step 2.18 – Dino slingshots (optional)", "2.18"),
    ("Step 2.19 – Signpost (5k)", "2.19"),
    ("Step 2.20 – Dash bumpers (main 200k, A/B 20k) and animatronic", "2.20"),
    ("Step 2.21 – Dash Nest bonus + bonus ball", "2.21"),
    ("Step 2.22 – Sparky bumpers A/B/C (20k) and animatronic", "2.22"),
    ("Step 2.23 – Sparky computer (200k + sparkyTurboCharge)", "2.23"),
    ("Step 2.24 – Multiplier targets x2–x6 (visual)", "2.24"),
    ("Step 2.25 – Bonus history display", "2.25"),
    ("Step 2.26 – Backbox: leaderboard and initials", "2.26"),
    ("Step 2.27 – Backbox: share and mobile overlay", "2.27"),
    ("Step 2.28 – Bottom group: kickers (5k each)", "2.28"),
    ("Step 2.29 – Launcher and input (I/O spec)", "2.29"),
    ("Step 2.30 – Polish and NFRs", "2.30"),
    ("Step 2.31 – Player assets and persistence", "2.31"),
    ("Step 2.32 – Main menu: Play, Levels, Store", "2.32"),
    ("Step 2.33 – Coin earning (Classic)", "2.33"),
    ("Step 2.34 – Store scene and access", "2.34"),
    ("Step 2.35 – Store: upgradable items and purchase", "2.35"),
    ("Step 2.36 – Store: character-themed upgrades", "2.36"),
    ("Step 2.37 – Post-game coin grant and Score Range Board hook", "2.37"),
    ("Step 2.38 – Score Range Board", "2.38"),
    ("Step 2.39 – Level Mode: entry and Level Select screen", "2.39"),
    ("Step 2.40 – Level data and progression", "2.40"),
    ("Step 2.41 – Level playfield (custom layout)", "2.41"),
    ("Step 2.42 – Level objectives", "2.42"),
    ("Step 2.43 – Level completion rewards", "2.43"),
    ("Step 2.44 – Level progress and high scores persistence", "2.44"),
]

# ---------- 24h workflow (from 24H_WORKFLOW_TEST_DESIGN.md) ----------
REQ_24H = [
    {
        "title": "REQ-A: API 与需求模块健康检查清单",
        "assigned_team": "jarvis",
        "description": "对 /api/、/api/requirements、/api/tasks 等做可用性检查，列出健康项与改进建议。",
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
        "description": "测试环境、用例覆盖、质量门禁等检查项与改进建议。",
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
        "description": "部署流程、机器/团队状态上报、在线判定等检查与改进建议。",
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
        "description": "文档完整性、飞书/状态上报/风险报告等流程检查与改进建议。",
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

# ---------- Machines (from docs/README.md) ----------
MACHINES = [
    ("vanguard", "192.168.3.75", "主控", "vanguard"),
    ("jarvis", "192.168.3.79", "开发", "jarvis"),
    ("codeforge", "192.168.3.4", "开发", "codeforge"),
    ("newton", "192.168.3.82", "研发/开发", "newton"),
    ("tesla", "192.168.3.83", "测试 + 玩家体验", "tesla"),
]


def get_db_path(db_path: str) -> str:
    if os.path.isabs(db_path):
        return db_path
    if not db_path or db_path == "factory.db":
        return os.path.join(_CORE_DB, "factory.db")
    return os.path.normpath(os.path.join(_REPO_ROOT, db_path))


def init_schema(conn: sqlite3.Connection) -> None:
    schema_path = os.path.join(_CORE_DB, "schema.sql")
    migrations_dir = os.path.join(_CORE_DB, "migrations")
    with open(schema_path) as f:
        conn.executescript(f.read())
    if os.path.isdir(migrations_dir):
        for f in sorted(os.listdir(migrations_dir)):
            if f.endswith(".sql"):
                path = os.path.join(migrations_dir, f)
                with open(path) as fp:
                    script = fp.read()
                try:
                    conn.executescript(script)
                except sqlite3.OperationalError as e:
                    err = str(e).lower()
                    if "duplicate column" not in err and "already exists" not in err:
                        raise
    conn.commit()


def ensure_project(conn: sqlite3.Connection, name: str, description: str, type_: str, status: str, repo_url: str = None) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE name = ?", (name,))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE projects SET description=?, type=?, status=?, updated_at=?, repo_url=? WHERE id=?",
            (description, type_, status, datetime.utcnow().isoformat(), repo_url or "", row[0]),
        )
        conn.commit()
        return row[0]
    c.execute(
        """INSERT INTO projects (name, description, type, status, repo_url)
           VALUES (?, ?, ?, ?, ?)""",
        (name, description, type_, status, repo_url or ""),
    )
    conn.commit()
    return c.lastrowid


def ensure_machines(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    for name, ip, role, team in MACHINES:
        c.execute("SELECT id FROM machines WHERE name = ?", (name,))
        if c.fetchone():
            c.execute(
                "UPDATE machines SET ip=?, role=?, status='offline' WHERE name=?",
                (ip, role, name),
            )
            try:
                c.execute("UPDATE machines SET team=? WHERE name=?", (team, name))
            except sqlite3.OperationalError:
                pass
        else:
            try:
                c.execute(
                    """INSERT INTO machines (name, ip, port, role, status, team)
                       VALUES (?, ?, 18789, ?, 'offline', ?)""",
                    (name, ip, role, team),
                )
            except sqlite3.OperationalError:
                c.execute(
                    """INSERT INTO machines (name, ip, port, role, status)
                       VALUES (?, ?, 18789, ?, 'offline')""",
                    (name, ip, role),
                )
    conn.commit()


def insert_pinball_requirements(conn: sqlite3.Connection, project_id: int) -> int:
    c = conn.cursor()
    count = 0
    for title, plan_step_id in PINBALL_BASELINE + PINBALL_FEATURE:
        c.execute(
            """INSERT INTO requirements (project_id, title, description, priority, type, status, plan_step_id, plan_phase, step)
               VALUES (?, ?, ?, 'P2', 'feature', 'new', ?, ?, 'not start')""",
            (project_id, title, "", plan_step_id, "baseline" if plan_step_id.startswith("0.") else "feature"),
        )
        count += 1
    conn.commit()
    return count


def close_old_24h_requirements(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(
        "UPDATE requirements SET status = 'closed', updated_at = ? WHERE title LIKE ? OR title LIKE ?",
        (datetime.utcnow().isoformat(), "%机器状态%24%", "%24h%报告%"),
    )
    if c.rowcount:
        conn.commit()


def insert_24h_requirement(conn: sqlite3.Connection, project_id: int, r: dict) -> int:
    c = conn.cursor()
    c.execute(
        """INSERT INTO requirements (
             project_id, title, description, priority, type, status,
             assigned_team, plan_step_id, step, progress_percent
           ) VALUES (?, ?, ?, ?, ?, ?, ?, '24h', 'not start', 0)""",
        (
            project_id,
            r["title"],
            r["description"],
            "P2",
            "feature",
            "new",
            r["assigned_team"],
        ),
    )
    conn.commit()
    return c.lastrowid


def insert_tasks(conn: sqlite3.Connection, req_id: int, tasks: list) -> None:
    c = conn.cursor()
    for title, executor in tasks:
        c.execute(
            """INSERT INTO tasks (req_id, title, description, status, executor)
               VALUES (?, ?, ?, 'todo', ?)""",
            (req_id, title, "", executor),
        )
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Smart Factory: projects, machines, pinball + 24h requirements")
    parser.add_argument("--db", default=None, help="Path to factory.db (default: db/factory.db)")
    parser.add_argument("--init", action="store_true", help="Create DB and run schema+migrations if DB missing")
    args = parser.parse_args()
    db_path = get_db_path(args.db or "factory.db")

    if not os.path.isfile(db_path):
        if args.init:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            init_schema(conn)
            conn.close()
            print("Created DB and ran schema at", db_path)
        else:
            print("DB not found:", db_path, file=sys.stderr)
            print("Run with --init to create and initialize it.", file=sys.stderr)
            return 1

    conn = sqlite3.connect(db_path)

    try:
        # 1. Projects: pinball-experience (active), smart-factory (active), others (archive)
        pid_pinball = ensure_project(
            conn,
            "pinball-experience",
            "Pinball Experience – baseline + feature steps from plan (BASELINE-STEPS, FEATURE-STEPS)",
            "game",
            "active",
            "https://github.com/LuckyJunjie/pinball-experience",
        )
        pid_smart = ensure_project(
            conn,
            "smart-factory",
            "24h 流程演练与 OpenClaw 通信系统测试",
            "tool",
            "active",
        )
        ensure_project(conn, "pi-pin-ball", "Legacy reference (archived)", "game", "archive")
        ensure_project(conn, "legacy-reference", "Archived reference project", "tool", "archive")
        print("Projects: pinball-experience (active), smart-factory (active), pi-pin-ball/legacy-reference (archive)")

        # 2. Machines
        ensure_machines(conn)
        print("Machines: vanguard, jarvis, codeforge, newton, tesla")

        # 3. Pinball-experience requirements (from plan; no assigned_team)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM requirements WHERE project_id = ?", (pid_pinball,))
        existing = c.fetchone()[0]
        if existing == 0:
            n = insert_pinball_requirements(conn, pid_pinball)
            print("Pinball-experience: inserted", n, "requirements (baseline 0.1–0.10 + feature 2.1–2.44)")
        else:
            print("Pinball-experience: already has", existing, "requirements, skip insert")

        # 4. 24h workflow requirements (REQ-A/B/C/D)
        close_old_24h_requirements(conn)
        created_24h = []
        for r in REQ_24H:
            rid = insert_24h_requirement(conn, pid_smart, r)
            insert_tasks(conn, rid, r["tasks"])
            created_24h.append((rid, r["title"], r["assigned_team"]))
        for rid, title, team in created_24h:
            print("24h requirement", rid, ":", title[:50], "->", team)
        print("24h: 4 requirements + tasks inserted. Teams: GET /api/teams/<team>/assigned-requirements then POST /take")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
