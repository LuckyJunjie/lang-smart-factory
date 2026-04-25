#!/usr/bin/env python3
"""
Verify Smart Factory DB schema: apply schema + migrations to a temp DB and run
API-representative queries. Exit 0 if OK, non-zero and print errors otherwise.

Usage:
  python3 db/verify_schema.py              # verify schema definition (in-memory)
  python3 db/verify_schema.py [path]       # verify existing DB file has all tables/columns
"""
import argparse
import os
import sqlite3
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = DB_DIR / "schema.sql"
MIGRATIONS_DIR = DB_DIR / "migrations"


def dict_factory(cursor, row):
    return {cursor.description[i][0]: row[i] for i in range(len(row))}


def run_schema_and_migrations(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        with open(f) as fp:
            script = fp.read()
        try:
            conn.executescript(script)
        except sqlite3.OperationalError as e:
            err = str(e).lower()
            if "duplicate column" not in err and "already exists" not in err:
                raise
    conn.commit()


def verify_connection(conn, errors):
    """Run all API-representative queries against an open connection."""
    c = conn.cursor()

    # Tables and one representative query each (as used by API)
    checks = [
        ("projects", "SELECT * FROM projects ORDER BY updated_at DESC LIMIT 1"),
        ("requirements", "SELECT r.*, p.name as project_name FROM requirements r JOIN projects p ON r.project_id = p.id LIMIT 1"),
        ("tasks", "SELECT * FROM tasks LIMIT 1"),
        ("machines", "SELECT * FROM machines ORDER BY name LIMIT 1"),
        ("tools", "SELECT * FROM tools ORDER BY type, name LIMIT 1"),
        ("team_machine_status", "SELECT * FROM team_machine_status LIMIT 1"),
        ("team_status_report", "SELECT * FROM team_status_report LIMIT 1"),
        ("discussion_blockage", "SELECT * FROM discussion_blockage LIMIT 1"),
        ("meetings", "SELECT * FROM meetings LIMIT 1"),
        ("meeting_participants", "SELECT * FROM meeting_participants LIMIT 1"),
        ("meeting_participant_inputs", "SELECT * FROM meeting_participant_inputs LIMIT 1"),
        ("pipelines", "SELECT p.*, pr.name as project_name FROM pipelines p LEFT JOIN projects pr ON p.project_id = pr.id LIMIT 1"),
        ("pipeline_runs", "SELECT * FROM pipeline_runs LIMIT 1"),
        ("cicd_triggers", "SELECT * FROM cicd_triggers LIMIT 1"),
        ("cicd_builds", "SELECT * FROM cicd_builds LIMIT 1"),
        ("team_task_detail", "SELECT * FROM team_task_detail LIMIT 1"),
        ("work_log", "SELECT * FROM work_log LIMIT 1"),
        ("team_report", "SELECT * FROM team_report LIMIT 1"),
    ]

    for name, query in checks:
        try:
            c.execute(query)
            c.fetchall()
        except sqlite3.OperationalError as e:
            errors.append(f"{name}: {e}")

    # Columns API expects on requirements (e.g. assignable filter, PATCH)
    try:
        c.execute("SELECT id, status, step, depends_on, assigned_team, assigned_agent, taken_at, plan_step_id, plan_phase, progress_percent FROM requirements LIMIT 1")
        c.fetchall()
    except sqlite3.OperationalError as e:
        errors.append(f"requirements columns: {e}")

    # Columns API expects on tasks (PATCH next_step_task_id, risk, blocker)
    try:
        c.execute(
            "SELECT id, status, executor, output_path, step, next_step_task_id, risk, blocker, completed_at, est_tokens_total, prompt_rounds FROM tasks LIMIT 1"
        )
        c.fetchall()
    except sqlite3.OperationalError as e:
        errors.append(f"tasks columns: {e}")

    # machines.team (teams/online)
    try:
        c.execute("SELECT DISTINCT team FROM machines WHERE team IS NOT NULL AND team != '' AND status='online'")
        c.fetchall()
    except sqlite3.OperationalError as e:
        errors.append(f"machines.team: {e}")


def main():
    parser = argparse.ArgumentParser(description="Verify Smart Factory DB schema")
    parser.add_argument("db_path", nargs="?", default=None, help="Optional: path to existing factory.db to verify")
    args = parser.parse_args()

    if args.db_path:
        db_path = Path(args.db_path).resolve()
        if not db_path.exists():
            print("DB file not found:", db_path, file=sys.stderr)
            return 1
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = dict_factory
        errors = []
        verify_connection(conn, errors)
        conn.close()
        if errors:
            for e in errors:
                print("ERROR:", e, file=sys.stderr)
            return 1
        print("Existing DB OK: all required tables and columns present:", db_path)
        return 0

    conn = sqlite3.connect(":memory:")
    conn.row_factory = dict_factory
    try:
        run_schema_and_migrations(conn)
    except Exception as e:
        print("Schema/migrations failed:", e, file=sys.stderr)
        return 1
    errors = []
    verify_connection(conn, errors)
    conn.close()
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print("Schema verification OK: all tables and API-used columns present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
