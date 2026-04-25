---
name: smart-factory-db-snapshot
description: >-
  Exports the Smart Factory SQLite database to timestamped markdown under
  core/db/snapshot/<UTC-timestamp>/. Use when the user asks for a DB snapshot,
  export_snapshot, factory.db export, or markdown dump of projects/requirements/tasks.
  Chinese triggers: 数据库快照, 导出 factory.db, Smart Factory DB 导出.
---

# Smart Factory DB snapshot

## What it does

Runs `core/db/export_snapshot.py` to read the SQLite DB and write markdown tables plus a nested `snapshot_by_project.md` for human review and LLM context.

## How to run

From the **repository root** (`smart-factory/`):

```bash
python3 core/db/export_snapshot.py
```

- **Default DB:** `core/db/factory.db`, or path in env `SMART_FACTORY_DB` if set.
- **Default output:** `core/db/snapshot/<YYYY-MM-DDTHH-MM-SSZ>/` (UTC). The script prints the output directory path on success.

### Options

| Flag | Meaning |
| --- | --- |
| `--db PATH` | SQLite file to export (overrides default / `SMART_FACTORY_DB`) |
| `--out DIR` | Exact output directory (skips auto timestamp subfolder) |

## Preconditions

- `db_path` must exist as a file; otherwise the script exits with `Database not found: …`.
- Uses only the Python standard library (`sqlite3`).

## Output files (typical)

Inside the new snapshot folder:

| File | Contents |
| --- | --- |
| `README.md` | Export time (UTC), source DB path, file index |
| `projects.md` | Projects table (selected columns) |
| `requirements.md` | Requirements joined with project name |
| `tasks.md` | Tasks joined with requirement and project (if `tasks` table has exportable columns) |
| `snapshot_by_project.md` | Per-project narrative: requirements and nested task rows |
| `machines.md` | Present only if `machines` table exists and has rows |
| `tools.md` | Present only if `tools` table exists and has rows |

Column sets follow the script: missing columns in older schemas are skipped automatically.

## When not to use this

- **Live production on another host:** Point `SMART_FACTORY_DB` or `--db` at a copied `.db` file if the canonical DB is remote; do not assume the local `factory.db` is up to date.
- **API-only workflows:** Agents that only call HTTP should use `GET` endpoints per `docs/REQUIREMENTS.md`; this skill is for offline markdown exports from SQLite.

## Import from code

`export_snapshot(db_path: Path, out_dir: Path)` in `core/db/export_snapshot.py` can be called programmatically if a scripted pipeline needs the same export without CLI.
