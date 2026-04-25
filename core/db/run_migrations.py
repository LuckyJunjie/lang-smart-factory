#!/usr/bin/env python3
"""Run DB migrations. Call from  directory."""
import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "factory.db"
if not DB_PATH.exists():
    DB_PATH = Path.home() / ".openclaw" / "workspace" / "smart-factory" / "db" / "factory.db"

MIGRATIONS_DIR = DB_DIR / "migrations"

def run_migrations():
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        with open(f) as fp:
            script = fp.read()
        try:
            conn.executescript(script)
        except sqlite3.OperationalError as e:
            err = str(e).lower()
            if "duplicate column" in err or "already exists" in err:
                print(f"  Skip {f.name}: {e}")
            else:
                conn.close()
                raise
    conn.commit()
    conn.close()
    print("Migrations done.")

if __name__ == "__main__":
    run_migrations()
