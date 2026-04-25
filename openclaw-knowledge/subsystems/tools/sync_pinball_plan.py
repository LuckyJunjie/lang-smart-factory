#!/usr/bin/env python3
"""
Sync pinball-experience plan to Smart Factory DB – backward-compat CLI wrapper.
Logic lives in mcp.remote.project_mcp.sync_plan. Use:
  python subsystems/tools/sync_pinball_plan.py
  or: python -m mcp.remote.project_mcp.sync_plan
  Or call project_mcp tool: sync_pinball_plan()
"""
import os
import sys

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from mcp.remote.project_mcp.sync_plan import run_sync_cli

if __name__ == "__main__":
    run_sync_cli()
