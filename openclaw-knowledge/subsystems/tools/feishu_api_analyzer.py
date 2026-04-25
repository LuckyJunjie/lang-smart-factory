#!/usr/bin/env python3
"""
Feishu API issue analysis – backward-compat CLI wrapper.
Logic lives in mcp.remote.comm_mcp.feishu_log_analysis. Use:
  python subsystems/tools/feishu_api_analyzer.py
  or: python -m mcp.remote.comm_mcp.feishu_log_analysis analyzer
"""
import os
import sys

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from mcp.remote.comm_mcp.feishu_log_analysis import run_analyzer_cli

if __name__ == "__main__":
    run_analyzer_cli()
