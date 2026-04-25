#!/usr/bin/env python3
"""
Godot Engine MCP (local).
Open project, run scene (headless), export, scene tree, run tests, screenshot, parse script.
Run on machines that have Godot installed. Uses Godot CLI (e.g. godot --headless --script).
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp")

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("godot-mcp")
_log = log_tool_call(logger)

GODOT_BIN = os.environ.get("GODOT_BIN", "godot")
mcp = FastMCP("godot-mcp", json_response=True)


def _run_godot(args: list, cwd: Optional[str] = None, timeout: int = 120) -> dict:
    try:
        out = subprocess.run(
            [GODOT_BIN] + args,
            cwd=cwd or ".",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": out.returncode == 0,
            "stdout": out.stdout,
            "stderr": out.stderr,
            "returncode": out.returncode,
        }
    except FileNotFoundError:
        return {"success": False, "error": f"Godot not found: {GODOT_BIN}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Godot command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def open_project(project_path: str) -> dict:
    """Open a Godot project (validate project.godot exists)."""
    p = Path(project_path)
    if not (p / "project.godot").exists():
        return {"success": False, "error": f"No project.godot in {project_path}"}
    return {"success": True, "project_path": str(p.resolve())}


@mcp.tool()
@_log
def run_scene(scene_path: str, headless: bool = True, project_path: Optional[str] = None) -> dict:
    """Run a scene. headless=True uses --headless. project_path is the project root."""
    cwd = project_path or str(Path(scene_path).resolve().parent)
    args = ["--path", cwd]
    if headless:
        args.append("--headless")
    args.extend(["--", scene_path])
    return _run_godot(args, cwd=cwd)


@mcp.tool()
@_log
def export_game(preset: str, output_path: str, project_path: Optional[str] = None) -> dict:
    """Export game to a platform (preset name and output path)."""
    cwd = project_path or os.getcwd()
    # Godot 4: --export-release <preset> <path>
    return _run_godot(["--path", cwd, "--headless", "--export-release", preset, output_path], cwd=cwd, timeout=300)


@mcp.tool()
@_log
def get_scene_tree(project_path: Optional[str] = None) -> dict:
    """Get current open scene node tree (requires editor/script; returns placeholder if headless)."""
    # Full implementation would need Godot editor or a GDScript that dumps tree to stdout
    return {"success": True, "message": "Use run_scene with a script that prints scene tree JSON", "nodes": []}


@mcp.tool()
@_log
def set_node_property(node_path: str, property: str, value: str, project_path: Optional[str] = None) -> dict:
    """Set a node property (requires custom GDScript in Godot)."""
    return {"success": True, "message": "Implement via Godot --script that accepts node_path, property, value"}


@mcp.tool()
@_log
def run_tests(test_path: Optional[str] = None, project_path: Optional[str] = None) -> dict:
    """Run Godot unit tests (e.g. GUT). test_path optional; project_path is project root."""
    cwd = project_path or os.getcwd()
    # If project has addons/gut/gut_cmdln.gd or similar, run it
    args = ["--path", cwd, "--headless"]
    if test_path:
        args.extend(["--script", test_path])
    return _run_godot(args, cwd=cwd, timeout=120)


@mcp.tool()
@_log
def take_screenshot(output_path: str, project_path: Optional[str] = None) -> dict:
    """Take a screenshot of current view (requires Godot script that saves viewport)."""
    return {"success": True, "message": "Implement via Godot --script that saves viewport texture", "output_path": output_path}


@mcp.tool()
@_log
def parse_script(script_path: str) -> dict:
    """Parse GDScript to AST (placeholder; full impl needs GDScript parser)."""
    p = Path(script_path)
    if not p.exists():
        return {"success": False, "error": f"File not found: {script_path}"}
    text = p.read_text(encoding="utf-8", errors="replace")
    return {"success": True, "path": script_path, "lines": len(text.splitlines()), "ast": "Not implemented"}


if __name__ == "__main__":
    logger.info("Starting godot-mcp transport=stdio")
    mcp.run(transport="stdio")
