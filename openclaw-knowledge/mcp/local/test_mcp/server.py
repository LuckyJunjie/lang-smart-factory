#!/usr/bin/env python3
"""
Test Execution MCP (local).
Run unit/integration tests, check coverage, parse test output.
Run on every agent server (and Tesla).
"""

import os
import re
import subprocess
import json
from pathlib import Path
from typing import Optional, Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp")

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("test-mcp")
_log = log_tool_call(logger)

mcp = FastMCP("test-mcp", json_response=True)


def _run(cmd: list, cwd: Optional[str] = None, timeout: int = 300) -> dict:
    try:
        out = subprocess.run(
            cmd,
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
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_log
def run_unit_tests(
    framework: str,
    test_path: str,
    options: Optional[dict] = None,
    cwd: Optional[str] = None,
) -> dict:
    """Run unit tests. framework: pytest, unittest, gut, etc. test_path: directory or file."""
    cwd = cwd or os.getcwd()
    opts = options or {}
    if framework.lower() == "pytest":
        cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short"]
        if opts.get("cov"):
            cmd.extend(["--cov", opts.get("cov", ".")])
        result = _run(cmd, cwd=cwd)
    elif framework.lower() == "unittest":
        cmd = ["python", "-m", "unittest", "discover", "-s", test_path, "-v"]
        result = _run(cmd, cwd=cwd)
    else:
        result = {"success": False, "error": f"Unknown framework: {framework}. Use pytest or unittest."}
    result["report"] = (result.get("stdout") or "") + (result.get("stderr") or "")
    return result


@mcp.tool()
@_log
def run_integration_tests(test_suite: str, cwd: Optional[str] = None) -> dict:
    """Run integration test suite (e.g. path to suite or script name)."""
    cwd = cwd or os.getcwd()
    if test_suite.endswith(".py"):
        result = _run(["python", test_suite], cwd=cwd)
    else:
        result = _run(["python", "-m", "pytest", test_suite, "-v", "-m", "integration"], cwd=cwd)
    result["report"] = (result.get("stdout") or "") + (result.get("stderr") or "")
    return result


@mcp.tool()
@_log
def check_coverage(report_format: str = "text", cwd: Optional[str] = None) -> dict:
    """Collect code coverage. report_format: text, json."""
    cwd = cwd or os.getcwd()
    cmd = ["python", "-m", "coverage", "report"]
    if report_format == "json":
        cmd.append("--format=json")
    result = _run(cmd, cwd=cwd)
    if result.get("stdout") and report_format == "json":
        try:
            result["coverage"] = json.loads(result["stdout"])
        except json.JSONDecodeError:
            pass
    return result


@mcp.tool()
@_log
def parse_test_output(file_path: str) -> dict:
    """Parse a test output file (e.g. pytest, JUnit XML) into structured results."""
    p = Path(file_path)
    if not p.exists():
        return {"success": False, "error": f"File not found: {file_path}"}
    text = p.read_text(encoding="utf-8", errors="replace")
    # Simple heuristic: count passed/failed from common patterns
    passed = len(re.findall(r"(PASSED|passed|OK|\.\s+ok)", text, re.I))
    failed = len(re.findall(r"(FAILED|failed|ERROR|error)", text, re.I))
    if passed == 0 and failed == 0:
        passed = len(re.findall(r"test_.*?passed", text, re.I))
        failed = len(re.findall(r"test_.*?failed", text, re.I))
    return {
        "success": True,
        "path": file_path,
        "passed": passed,
        "failed": failed,
        "summary": text[-2000:] if len(text) > 2000 else text,
    }


if __name__ == "__main__":
    logger.info("Starting test-mcp transport=stdio")
    mcp.run(transport="stdio")
