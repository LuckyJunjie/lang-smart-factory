#!/usr/bin/env python3
"""
Sync pinball-experience plan (BASELINE_STEPS, FEATURE_STEPS) to Smart Factory DB.
Used by project_mcp tool and by CLI wrapper in subsystems/tools.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Baseline steps 0.1-0.10
BASELINE_STEPS = [
    ("0.1", "Step 0.1 – Primitive playable (launcher + flippers)", "done", 100),
    ("0.2", "Step 0.2 – Drain", "done", 100),
    ("0.3", "Step 0.3 – Walls and boundaries", "done", 100),
    ("0.4", "Step 0.4 – Obstacles / bumpers (basic scoring)", "done", 100),
    ("0.5", "Step 0.5 – Rounds and game over", "done", 100),
    ("0.6", "Step 0.6 – Skill shot", "new", 0),
    ("0.7", "Step 0.7 – Multiplier", "new", 0),
    ("0.8", "Step 0.8 – Multiball", "new", 0),
    ("0.9", "Step 0.9 – Combo (optional)", "new", 0),
    ("0.10", "Step 0.10 – Polish (physics, animation, audio)", "new", 0),
]

# Feature steps 2.1-2.44
FEATURE_STEPS = [
    ("2.1", "Step 2.1 – Start flow: initial → play", "new", 0),
    ("2.2", "Step 2.2 – Game state and scoring (requirements shape)", "new", 0),
    ("2.3", "Step 2.3 – Point values and skill shot (I/O values)", "new", 0),
    ("2.4", "Step 2.4 – Character selection", "new", 0),
    ("2.5", "Step 2.5 – How to Play screen", "new", 0),
    ("2.6", "Step 2.6 – HUD (score, multiplier, rounds)", "new", 0),
    ("2.7", "Step 2.7 – Camera (waiting / playing / game over)", "new", 0),
    ("2.8", "Step 2.8 – Google rollovers (5k each)", "new", 0),
    ("2.9", "Step 2.9 – Google Word letters and spell Google", "new", 0),
    ("2.10", "Step 2.10 – Bonus ball (5s) from Google Word / Dash Nest", "new", 0),
    ("2.11", "Step 2.11 – Multiball indicators (4)", "new", 0),
    ("2.12", "Step 2.12 – SpaceshipRamp (5k shot, ramp bonus, multiplier)", "new", 0),
    ("2.13", "Step 2.13 – Android Acres rail", "new", 0),
    ("2.14", "Step 2.14 – Android bumpers A / B / COW (20k each)", "new", 0),
    ("2.15", "Step 2.15 – AndroidSpaceship target (200k + bonus)", "new", 0),
    ("2.16", "Step 2.16 – ChromeDino mouth (200k + dinoChomp)", "new", 0),
    ("2.17", "Step 2.17 – DinoWalls (bonus ball spawn position)", "new", 0),
    ("2.18", "Step 2.18 – Dino slingshots (optional)", "new", 0),
    ("2.19", "Step 2.19 – Signpost (5k)", "new", 0),
    ("2.20", "Step 2.20 – Dash bumpers (main 200k, A/B 20k) and animatronic", "new", 0),
    ("2.21", "Step 2.21 – Dash Nest bonus + bonus ball", "new", 0),
    ("2.22", "Step 2.22 – Sparky bumpers A/B/C (20k) and animatronic", "new", 0),
    ("2.23", "Step 2.23 – Sparky computer (200k + sparkyTurboCharge)", "new", 0),
    ("2.24", "Step 2.24 – Multiplier targets x2–x6 (visual)", "new", 0),
    ("2.25", "Step 2.25 – Bonus history display", "new", 0),
    ("2.26", "Step 2.26 – Backbox: leaderboard and initials", "new", 0),
    ("2.27", "Step 2.27 – Backbox: share and mobile overlay", "new", 0),
    ("2.28", "Step 2.28 – Bottom group: kickers (5k each)", "new", 0),
    ("2.29", "Step 2.29 – Launcher and input (I/O spec)", "new", 0),
    ("2.30", "Step 2.30 – Polish and NFRs", "new", 0),
    ("2.31", "Step 2.31 – Player assets and persistence", "new", 0),
    ("2.32", "Step 2.32 – Main menu: Play, Levels, Store", "new", 0),
    ("2.33", "Step 2.33 – Coin earning (Classic)", "new", 0),
    ("2.34", "Step 2.34 – Store scene and access", "new", 0),
    ("2.35", "Step 2.35 – Store: upgradable items and purchase", "new", 0),
    ("2.36", "Step 2.36 – Store: character-themed upgrades", "new", 0),
    ("2.37", "Step 2.37 – Post-game coin grant and Score Range Board hook", "new", 0),
    ("2.38", "Step 2.38 – Score Range Board", "new", 0),
    ("2.39", "Step 2.39 – Level Mode: entry and Level Select screen", "new", 0),
    ("2.40", "Step 2.40 – Level data and progression", "new", 0),
    ("2.41", "Step 2.41 – Level playfield (custom layout)", "new", 0),
    ("2.42", "Step 2.42 – Level objectives", "new", 0),
    ("2.43", "Step 2.43 – Level completion rewards", "new", 0),
    ("2.44", "Step 2.44 – Level progress and high scores persistence", "new", 0),
]


def get_db_path() -> str:
    """Smart Factory DB path. Env SMART_FACTORY_DB or repo db/factory.db."""
    repo_root = Path(__file__).resolve().parents[3]
    default = repo_root / "db" / "factory.db"
    if default.exists():
        return str(default)
    return os.environ.get("SMART_FACTORY_DB", str(Path.home() / ".openclaw" / "workspace" / "smart-factory" / "db" / "factory.db"))


def get_or_create_project(conn: sqlite3.Connection) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE name='pinball-experience'")
    row = c.fetchone()
    if row:
        return row[0]
    c.execute("""INSERT INTO projects (name, description, type, status, repo_url)
                 VALUES ('pinball-experience', '弹珠机游戏 - 基于BASELINE-STEPS和FEATURE-STEPS', 'game', 'active',
                         'https://github.com/LuckyJunjie/pinball-experience')""")
    return c.lastrowid


def ensure_columns(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute("PRAGMA table_info(requirements)")
    cols = {r[1] for r in c.fetchall()}
    for col, typ in [
        ("assigned_team", "TEXT"), ("assigned_agent", "TEXT"), ("taken_at", "DATETIME"),
        ("plan_step_id", "TEXT"), ("plan_phase", "TEXT"), ("step", "TEXT"), ("progress_percent", "INTEGER"),
    ]:
        if col not in cols:
            try:
                c.execute(f"ALTER TABLE requirements ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError:
                pass
    conn.commit()


def sync_requirements(conn: sqlite3.Connection, project_id: int) -> tuple:
    c = conn.cursor()
    created = updated = 0
    for step_id, title, status, progress in BASELINE_STEPS + FEATURE_STEPS:
        phase = "baseline" if step_id.startswith("0.") else "feature"
        priority = "P0" if step_id in ("0.1", "0.2", "0.3", "0.4", "0.5", "0.6") else "P1" if phase == "baseline" else "P2"
        c.execute("SELECT id, status, progress_percent FROM requirements WHERE project_id=? AND plan_step_id=?", (project_id, step_id))
        row = c.fetchone()
        if row:
            rid, old_status, old_progress = row
            if old_status != status or (isinstance(old_progress, int) and old_progress != progress):
                c.execute("UPDATE requirements SET title=?, status=?, progress_percent=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                          (title, status, progress, rid))
                updated += 1
        else:
            c.execute("""INSERT INTO requirements (project_id, title, plan_step_id, plan_phase, priority, status, progress_percent, type)
                         VALUES (?,?,?,?,?,?,?,'feature')""",
                      (project_id, title, step_id, phase, priority, status, progress))
            created += 1
    conn.commit()
    return created, updated


def run_sync(db_path: str = None) -> dict:
    """Run sync. Returns { success, project_id, created, updated, total, error? }."""
    db_path = db_path or get_db_path()
    if not Path(db_path).exists():
        return {"success": False, "error": f"DB not found: {db_path}", "project_id": None, "created": 0, "updated": 0, "total": 0}
    try:
        conn = sqlite3.connect(db_path)
        ensure_columns(conn)
        project_id = get_or_create_project(conn)
        created, updated = sync_requirements(conn, project_id)
        conn.close()
        total = len(BASELINE_STEPS) + len(FEATURE_STEPS)
        return {"success": True, "project_id": project_id, "created": created, "updated": updated, "total": total}
    except Exception as e:
        return {"success": False, "error": str(e), "project_id": None, "created": 0, "updated": 0, "total": 0}


def run_sync_cli() -> None:
    """CLI entrypoint."""
    result = run_sync()
    if not result["success"]:
        print(result.get("error", "Unknown error"))
        sys.exit(1)
    print(f"Synced pinball-experience (project_id={result['project_id']})")
    print(f"  Created: {result['created']}, Updated: {result['updated']}")
    print(f"  Total: {result['total']} requirements")


if __name__ == "__main__":
    run_sync_cli()
