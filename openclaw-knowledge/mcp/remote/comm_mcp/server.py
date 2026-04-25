#!/usr/bin/env python3
"""
Communication MCP (remote).
Feishu and optional email. Deploy on Vanguard001 with project-mcp.
Uses Smart Factory API for Feishu when webhook not provided, or FEISHU_WEBHOOK_URL.
"""

import os
import json
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp requests")

import requests

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("comm-mcp")
_log = log_tool_call(logger)

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK_URL", "")
TIMEOUT = 15

mcp = FastMCP("comm-mcp", json_response=True)


def _post_feishu_via_api(content: str, title: Optional[str] = None) -> dict:
    """Post to Feishu via Smart Factory API (uses server's FEISHU_WEBHOOK_URL)."""
    r = requests.post(
        f"{API_BASE}/feishu/post",
        json={"text": content, "title": title or "Smart Factory"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json() if r.content else {"success": True}


def _post_feishu_direct(webhook_url: str, content: str, msg_type: str = "text") -> dict:
    """Post to Feishu using webhook URL directly."""
    body = {"msg_type": msg_type, "content": {"text": content}}
    r = requests.post(webhook_url, json=body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


@mcp.tool()
@_log
def send_feishu_message(
    content: str,
    webhook_url: Optional[str] = None,
    msg_type: Optional[str] = None,
    title: Optional[str] = None,
) -> dict:
    """Send a message to Feishu. Uses webhook_url if given, else FEISHU_WEBHOOK_URL, else Smart Factory API /feishu/post."""
    url = (webhook_url or FEISHU_WEBHOOK or "").strip()
    if url:
        return _post_feishu_direct(url, content, msg_type or "text")
    return _post_feishu_via_api(content, title)


@mcp.tool()
@_log
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email (optional; no-op if no mail backend configured)."""
    # Placeholder: Smart Factory API may not have email; return success for now
    return {"success": True, "message": "Email not configured; message logged", "to": to, "subject": subject}


# ----- Feishu API log analysis (moved from subsystems/tools) -----

def _feishu_analysis():
    from mcp.remote.comm_mcp import feishu_log_analysis
    return feishu_log_analysis


@mcp.tool()
@_log
def analyze_feishu_logs(log_file: Optional[str] = None) -> dict:
    """Parse Gateway log for Feishu API calls, save to DB, return stats and report text. Optional log_file path; else uses FEISHU_LOG_FILE or default path."""
    mod = _feishu_analysis()
    return mod.run_analyze(log_file=log_file)


@mcp.tool()
@_log
def get_feishu_api_stats(limit: int = 20) -> list:
    """Get daily Feishu API call stats from DB (date, source, purpose, success_count, failed_count)."""
    mod = _feishu_analysis()
    return mod.get_stats_from_db(limit=limit)


@mcp.tool()
@_log
def analyze_feishu_issues(log_file: Optional[str] = None) -> dict:
    """Analyze Gateway log for Feishu API issues (excessive polling, high error rate). Returns api_analysis, error_analysis, issues list."""
    mod = _feishu_analysis()
    return mod.run_analyzer_style(log_file=log_file)


if __name__ == "__main__":
    import sys
    transport = "streamable-http" if "--transport" in sys.argv and "streamable-http" in sys.argv else "stdio"
    port = 8002
    if "--port" in sys.argv:
        i = sys.argv.index("--port")
        if i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    logger.info("Starting comm-mcp transport=%s port=%s", transport, port if transport == "streamable-http" else "N/A")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")
