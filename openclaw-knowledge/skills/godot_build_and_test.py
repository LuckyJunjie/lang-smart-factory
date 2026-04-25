#!/usr/bin/env python3
"""
Skill: godot_build_and_test
Executor: Dev or Test team
Flow: export_game -> run_tests -> parse_test_output -> on failure send_feishu_message -> report_status.
Invoke Godot MCP or CLI; this script is a placeholder that documents the flow.
"""

import sys

from .log_util import get_logger

LOG = get_logger("godot_build_and_test")


def main():
    LOG.info("start (placeholder: use Godot MCP or CLI)")
    print("godot_build_and_test: Run via Godot MCP (export_game, run_tests) and test-mcp (parse_test_output).")
    print("Or run Godot/CLI manually and then report_status via API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
