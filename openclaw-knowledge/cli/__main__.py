#!/usr/bin/env python3
"""
Smart Factory CLI – agent entry point.
Run from smart-factory directory: python -m cli <domain> <subcommand> [args...]
Output: JSON to stdout for agent parsing.
"""
import argparse
import sys

from cli._base import out, err


def main():
    parser = argparse.ArgumentParser(
        description="Smart Factory CLI (replaces MCP). Agents use CLI instead of MCP tools.",
        prog="python -m cli",
    )
    parser.add_argument("--cwd", default=None, help="Working directory (default: current)")
    sp = parser.add_subparsers(dest="domain", required=True)

    from cli import project_cmd, comm_cmd, dev_cmd, godot_cmd, test_cmd, analysis_cmd
    project_cmd.add_parser(sp)
    comm_cmd.add_parser(sp)
    dev_cmd.add_parser(sp)
    godot_cmd.add_parser(sp)
    test_cmd.add_parser(sp)
    analysis_cmd.add_parser(sp)

    args = parser.parse_args()
    if args.cwd:
        import os
        os.chdir(args.cwd)

    runners = {
        "project": project_cmd.run,
        "comm": comm_cmd.run,
        "dev": dev_cmd.run,
        "godot": godot_cmd.run,
        "test": test_cmd.run,
        "analysis": analysis_cmd.run,
    }
    run = runners.get(args.domain)
    if not run:
        err(f"Unknown domain: {args.domain}")
    try:
        result = run(args)
        out(result)
    except Exception as e:
        err(f"CLI error: {e}")


if __name__ == "__main__":
    main()
