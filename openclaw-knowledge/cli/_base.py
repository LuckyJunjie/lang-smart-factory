"""Shared CLI helpers: JSON output and CWD."""
import json
import os
import sys


def out(obj, stream=None):
    """Print JSON to stdout (or stream) for agent parsing."""
    stream = stream or sys.stdout
    print(json.dumps(obj, ensure_ascii=False, indent=2), file=stream)


def err(msg: str):
    """Print error message to stderr and exit 1."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def get_cwd():
    """Current working directory for path resolution (CLI runs from agent workspace)."""
    return os.getcwd()
