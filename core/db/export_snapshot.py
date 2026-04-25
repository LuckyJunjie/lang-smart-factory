#!/usr/bin/env python3
"""
Export Smart Factory SQLite data to markdown snapshots under:

    core/db/snapshot/<timestamp>/

Default DB: core/db/factory.db (overridable with --db or SMART_FACTORY_DB).
"""
from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db_dir() -> Path:
    return Path(__file__).resolve().parent


def _default_db_path() -> Path:
    env = os.environ.get("SMART_FACTORY_DB")
    if env:
        return Path(env)
    return _db_dir() / "factory.db"


def _md_cell(value) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _write_table(path: Path, title: str, columns: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not columns:
        path.write_text(f"# {title}\n\n*(no columns)*\n", encoding="utf-8")
        return
    lines = [f"# {title}\n", "", "| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(row[i] if i < len(row) else "") for i in range(len(columns))) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def _select_columns(available: list[str], wanted: list[str]) -> list[str]:
    avail = set(available)
    return [c for c in wanted if c in avail]


def export_snapshot(db_path: Path, out_dir: Path) -> None:
    if not db_path.is_file():
        raise SystemExit(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()

        proj_cols = _select_columns(
            _table_columns(conn, "projects"),
            ["id", "name", "description", "type", "status", "created_at", "updated_at", "gdd_path", "repo_url"],
        )
        cur.execute(f"SELECT {', '.join(proj_cols)} FROM projects ORDER BY id")
        proj_rows = cur.fetchall()
        _write_table(
            out_dir / "projects.md",
            "Projects",
            list(proj_rows[0].keys()) if proj_rows else proj_cols,
            [tuple(r[c] for c in r.keys()) for r in proj_rows],
        )

        req_avail = set(_table_columns(conn, "requirements"))
        req_sel = [
            "r." + c
            for c in _select_columns(
                list(req_avail),
                [
                    "id",
                    "project_id",
                    "title",
                    "description",
                    "priority",
                    "status",
                    "type",
                    "assigned_to",
                    "assigned_team",
                    "assigned_agent",
                    "taken_at",
                    "plan_step_id",
                    "plan_phase",
                    "step",
                    "progress_percent",
                    "created_at",
                    "updated_at",
                    "note",
                    "design_doc_path",
                    "acceptance_criteria",
                    "depends_on",
                ],
            )
        ]
        req_sql = f"SELECT {', '.join(req_sel)}, p.name AS project_name FROM requirements r JOIN projects p ON p.id = r.project_id ORDER BY r.project_id, r.id"
        cur.execute(req_sql)
        req_rows = cur.fetchall()
        if req_rows:
            req_headers = list(req_rows[0].keys())
        else:
            req_headers = [c.replace("r.", "", 1) for c in req_sel] + ["project_name"]
        _write_table(
            out_dir / "requirements.md",
            "Requirements",
            req_headers,
            [tuple(r[c] for c in r.keys()) for r in req_rows],
        )

        tcols = _table_columns(conn, "tasks")
        t_sel = _select_columns(
            tcols,
            [
                "id",
                "req_id",
                "title",
                "description",
                "status",
                "step",
                "note",
                "executor",
                "output_path",
                "next_step_task_id",
                "risk",
                "blocker",
                "created_at",
                "started_at",
                "completed_at",
            ],
        )
        if not t_sel:
            task_rows = []
        else:
            t_col_list = ", ".join(f"t.{c}" for c in t_sel)
            task_sql = f"""SELECT {t_col_list}, r.title AS requirement_title, r.project_id, p.name AS project_name
               FROM tasks t
               JOIN requirements r ON r.id = t.req_id
               JOIN projects p ON p.id = r.project_id
               ORDER BY r.project_id, t.req_id, t.id"""
            cur.execute(task_sql)
            task_rows = cur.fetchall()
        if task_rows:
            task_headers = list(task_rows[0].keys())
            _write_table(
                out_dir / "tasks.md",
                "Tasks",
                task_headers,
                [tuple(r[c] for c in r.keys()) for r in task_rows],
            )
        elif t_sel:
            task_headers = [f"t_{c}" for c in t_sel] + ["requirement_title", "project_id", "project_name"]
            _write_table(out_dir / "tasks.md", "Tasks", task_headers, [])
        else:
            (out_dir / "tasks.md").write_text("# Tasks\n\n*(tasks table has no columns to export)*\n", encoding="utf-8")

        # Nested narrative view
        by_project: dict[int, dict] = {}
        for r in proj_rows:
            pid = r["id"]
            by_project[pid] = {"project": dict(r), "requirements": []}

        for r in req_rows:
            pid = r["project_id"]
            if pid in by_project:
                entry = dict(r)
                entry["tasks"] = [dict(t) for t in task_rows if t["req_id"] == r["id"]]
                by_project[pid]["requirements"].append(entry)

        narrative = out_dir / "snapshot_by_project.md"
        lines = ["# Snapshot by project", ""]
        for pid in sorted(by_project.keys()):
            block = by_project[pid]
            p = block["project"]
            lines.append(f"## Project {pid}: {_md_cell(p.get('name'))}")
            lines.append("")
            lines.append(f"- **Status:** {_md_cell(p.get('status'))}")
            lines.append(f"- **Type:** {_md_cell(p.get('type'))}")
            if p.get("description"):
                lines.append(f"- **Description:** {_md_cell(p.get('description'))}")
            lines.append("")
            for req in block["requirements"]:
                lines.append(f"### Requirement #{req['id']}: {_md_cell(req.get('title'))}")
                lines.append("")
                lines.append(f"| Field | Value |")
                lines.append("| --- | --- |")
                for key in (
                    "status",
                    "priority",
                    "type",
                    "step",
                    "progress_percent",
                    "assigned_team",
                    "assigned_agent",
                    "plan_step_id",
                    "plan_phase",
                ):
                    lines.append(f"| {key} | {_md_cell(req.get(key))} |")
                if req.get("description"):
                    lines.append("")
                    lines.append(f"**Description:** {_md_cell(req.get('description'))}")
                lines.append("")
                if req["tasks"]:
                    lines.append("| task_id | title | status | step | executor |")
                    lines.append("| --- | --- | --- | --- | --- |")
                    for t in req["tasks"]:
                        lines.append(
                            f"| {t.get('id')} | {_md_cell(t.get('title'))} | {_md_cell(t.get('status'))} | "
                            f"{_md_cell(t.get('step'))} | {_md_cell(t.get('executor'))} |"
                        )
                else:
                    lines.append("*No tasks.*")
                lines.append("")
        narrative.write_text("\n".join(lines), encoding="utf-8")

        # Machines & tools if tables exist and have rows
        try:
            cur.execute("SELECT * FROM machines ORDER BY id")
            mrows = cur.fetchall()
            if mrows:
                cols = list(mrows[0].keys())
                _write_table(
                    out_dir / "machines.md",
                    "Machines",
                    cols,
                    [tuple(r[c] for c in cols) for r in mrows],
                )
        except sqlite3.OperationalError:
            pass

        try:
            cur.execute("SELECT * FROM tools ORDER BY id")
            trows = cur.fetchall()
            if trows:
                cols = list(trows[0].keys())
                _write_table(
                    out_dir / "tools.md",
                    "Tools",
                    cols,
                    [tuple(r[c] for c in cols) for r in trows],
                )
        except sqlite3.OperationalError:
            pass

    finally:
        conn.close()

    readme = out_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Database snapshot",
                "",
                f"- **Exported at (UTC):** {datetime.now(timezone.utc).isoformat()}",
                f"- **Source DB:** `{db_path.resolve()}`",
                "",
                "## Files",
                "",
                "| File | Contents |",
                "| --- | --- |",
                "| `README.md` | This index |",
                "| `projects.md` | All projects |",
                "| `requirements.md` | All requirements with project name |",
                "| `tasks.md` | All tasks with requirement and project |",
                "| `snapshot_by_project.md` | Human-readable hierarchy |",
                "| `machines.md` | Machines (if any) |",
                "| `tools.md` | Tools registry (if any) |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Export Smart Factory DB to markdown under core/db/snapshot/<timestamp>/")
    ap.add_argument("--db", default=None, help="Path to SQLite DB (default: core/db/factory.db or SMART_FACTORY_DB)")
    ap.add_argument(
        "--out",
        default=None,
        help="Output directory (default: core/db/snapshot/<UTC timestamp>)",
    )
    args = ap.parse_args()

    db_path = Path(args.db).resolve() if args.db else _default_db_path().resolve()
    if args.out:
        out_dir = Path(args.out).resolve()
    else:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        out_dir = _db_dir() / "snapshot" / ts

    export_snapshot(db_path, out_dir)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
