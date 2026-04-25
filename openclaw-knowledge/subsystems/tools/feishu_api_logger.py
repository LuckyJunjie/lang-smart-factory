#!/usr/bin/env python3
"""
Feishu API log analysis – backward-compat CLI wrapper.
Logic lives in mcp.remote.comm_mcp.feishu_log_analysis. Use:
  python subsystems/tools/feishu_api_logger.py [--log-file PATH] [--analyze] [--report] [--stats]
  or: python -m mcp.remote.comm_mcp.feishu_log_analysis
"""
import os
import sys

# Ensure smart-factory root is on path when run as script from repo
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from mcp.remote.comm_mcp.feishu_log_analysis import run_logger_cli

if __name__ == "__main__":
    run_logger_cli()
