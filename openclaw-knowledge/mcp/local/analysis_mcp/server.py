#!/usr/bin/env python3
"""
Analysis MCP (local).
Code analysis (e.g. gdlint), extract requirements from docs, estimate complexity, summarize changes.
Run on every agent server.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp")

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("analysis-mcp")
_log = log_tool_call(logger)

mcp = FastMCP("analysis-mcp", json_response=True)


def _run(cmd: list, cwd: Optional[str] = None, timeout: int = 60) -> dict:
    try:
        out = subprocess.run(
            cmd,
            cwd=cwd or ".",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {"success": out.returncode == 0, "stdout": out.stdout, "stderr": out.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def analyze_code(path: str, rules: Optional[List[str]] = None, cwd: Optional[str] = None) -> dict:
    """Run code analysis (e.g. gdlint for GDScript, or pylint for Python). Returns list of issues."""
    cwd = cwd or os.getcwd()
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": f"Path not found: {path}", "issues": []}
    # GDScript: try gdlint if path has .gd
    if str(p).endswith(".gd"):
        r = _run(["gdlint", str(p)], cwd=cwd)
        issues = []
        for line in (r.get("stdout") or "").splitlines():
            if line.strip():
                issues.append({"message": line, "path": path})
        return {"success": True, "issues": issues, "raw": r.get("stdout", "")}
    # Python: try pylint or flake8
    if str(p).endswith(".py"):
        r = _run(["python", "-m", "py_compile", str(p)], cwd=cwd)
        if not r["success"]:
            return {"success": False, "issues": [{"message": r.get("stderr", "syntax error"), "path": path}], "raw": r.get("stderr")}
        return {"success": True, "issues": [], "raw": "py_compile OK"}
    return {"success": True, "issues": [], "raw": "No analyzer for this file type"}


@mcp.tool()
@_log
def extract_requirements(document_path: str) -> dict:
    """Extract requirement-like items from a document (markdown/PRD). Returns list of requirement texts."""
    p = Path(document_path)
    if not p.exists():
        return {"success": False, "requirements": [], "error": f"File not found: {document_path}"}
    text = p.read_text(encoding="utf-8", errors="replace")
    requirements = []
    # Simple extraction: lines that look like "## Requirement" or "- [ ]" or numbered items
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^#+\s*(需求|requirement|feature|task)", line, re.I):
            requirements.append(line)
        elif re.match(r"^[-*]\s+\[.\]\s+", line) or re.match(r"^\d+[.)]\s+", line):
            requirements.append(line)
        elif line.startswith("- ") and len(line) > 10:
            requirements.append(line)
    return {"success": True, "requirements": requirements[:100], "path": document_path}


@mcp.tool()
@_log
def estimate_complexity(input_text: str) -> dict:
    """Estimate task/code complexity from description or code snippet. Returns a simple score."""
    # Heuristic: length and keywords
    text = (input_text or "").lower()
    score = 1
    if len(text) > 500:
        score += 1
    if any(k in text for k in ["integration", "api", "database", "async", "multi"]):
        score += 1
    if any(k in text for k in ["simple", "fix", "typo"]):
        score = max(1, score - 1)
    return {"success": True, "complexity_score": min(5, score), "description": "1=low, 5=high"}


@mcp.tool()
@_log
def summarize_changes(git_diff: str) -> str:
    """Generate a short summary of a git diff (files changed, approximate scope)."""
    if not git_diff or not git_diff.strip():
        return "No changes."
    lines = git_diff.strip().splitlines()
    files = set()
    additions = 0
    deletions = 0
    for line in lines:
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 3:
                files.add(parts[2].replace("a/", ""))
        elif line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    summary = f"Files changed: {len(files)}. +{additions} -{deletions} lines."
    if files:
        summary += " Files: " + ", ".join(sorted(files)[:10])
        if len(files) > 10:
            summary += f" (+{len(files)-10} more)"
    return summary


if __name__ == "__main__":
    logger.info("Starting analysis-mcp transport=stdio")
    mcp.run(transport="stdio")
