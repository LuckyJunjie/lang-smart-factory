#!/usr/bin/env python3
"""
Development Environment MCP (local).
File read/write, list directory, Git, run command (whitelist), build.
Run on every agent server.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp")

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("dev-mcp")
_log = log_tool_call(logger)

# Whitelist for run_command (comma-separated env MCP_DEV_ALLOWED_COMMANDS)
ALLOWED_COMMANDS = set(
    os.environ.get("MCP_DEV_ALLOWED_COMMANDS", "make,gradle,npm,npx,python,python3,git").split(",")
)
ALLOWED_COMMANDS = {c.strip().lower() for c in ALLOWED_COMMANDS if c.strip()}

mcp = FastMCP("dev-mcp", json_response=True)


def _resolve_path(path: str, cwd: Optional[str] = None) -> Path:
    p = Path(path)
    if not p.is_absolute() and cwd:
        p = Path(cwd) / p
    return p.resolve()


@mcp.tool()
@_log
def read_file(path: str, cwd: Optional[str] = None) -> str:
    """Read file content. path can be relative to cwd."""
    p = _resolve_path(path, cwd)
    if not p.is_file():
        return f"Error: Not a file or not found: {p}"
    return p.read_text(encoding="utf-8", errors="replace")


@mcp.tool()
@_log
def write_file(path: str, content: str, cwd: Optional[str] = None) -> dict:
    """Write content to file. path can be relative to cwd."""
    p = _resolve_path(path, cwd)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"success": True, "path": str(p)}


@mcp.tool()
@_log
def list_directory(path: str, cwd: Optional[str] = None) -> list:
    """List directory entries (names only). path can be relative to cwd."""
    p = _resolve_path(path, cwd)
    if not p.is_dir():
        return []
    return sorted(os.listdir(p))


@mcp.tool()
@_log
def git_status(repo_path: str) -> dict:
    """Get Git status (changed files) for repo_path."""
    try:
        out = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = (out.stdout or "").strip().splitlines()
        return {"success": True, "changes": lines, "returncode": out.returncode}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def git_commit(repo_path: str, message: str) -> dict:
    """Commit all changes in repo_path with the given message."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True, capture_output=True, timeout=30)
        out = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if out.returncode != 0 and "nothing to commit" not in (out.stderr or "").lower():
            return {"success": False, "stderr": out.stderr, "stdout": out.stdout}
        rev = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return {"success": True, "commit": (rev.stdout or "").strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def git_push(repo_path: str, remote: Optional[str] = None) -> dict:
    """Push to remote. remote defaults to origin."""
    try:
        args = ["git", "push"]
        if remote:
            args.append(remote)
        out = subprocess.run(args, cwd=repo_path, capture_output=True, text=True, timeout=60)
        return {
            "success": out.returncode == 0,
            "stdout": out.stdout,
            "stderr": out.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def run_command(command: str, args: Optional[List[str]] = None, cwd: Optional[str] = None) -> dict:
    """Execute a shell command (whitelist only). command is the program name (e.g. make), args are the rest."""
    cmd_name = (command or "").strip().lower()
    if cmd_name not in ALLOWED_COMMANDS:
        return {"success": False, "error": f"Command not in whitelist: {command}. Allowed: {sorted(ALLOWED_COMMANDS)}"}
    full_args = [command] + (args or [])
    try:
        out = subprocess.run(
            full_args,
            cwd=cwd or ".",
            capture_output=True,
            text=True,
            timeout=300,
        )
        return {
            "success": out.returncode == 0,
            "stdout": out.stdout,
            "stderr": out.stderr,
            "returncode": out.returncode,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def build_project(project_path: str, target: Optional[str] = None) -> dict:
    """Run build (make or gradle or npm run build) in project_path. target e.g. default, release."""
    cwd = project_path or "."
    if (Path(cwd) / "Makefile").exists():
        cmd, cargs = "make", [target] if target else []
    elif (Path(cwd) / "build.gradle").exists() or (Path(cwd) / "build.gradle.kts").exists():
        cmd, cargs = "gradle", ["build"] if not target else [target]
    elif (Path(cwd) / "package.json").exists():
        cmd, cargs = "npm", ["run", "build"]
    else:
        return {"success": False, "error": "No Makefile, build.gradle, or package.json found"}
    result = run_command(cmd, cargs, cwd)
    result["build_log"] = (result.get("stdout") or "") + (result.get("stderr") or "")
    return result


if __name__ == "__main__":
    logger.info("Starting dev-mcp transport=stdio")
    mcp.run(transport="stdio")
