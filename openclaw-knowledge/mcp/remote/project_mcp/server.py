#!/usr/bin/env python3
"""
Project Management MCP (remote).
Tools map to Smart Factory API: requirements, teams, blockages.
Deploy on Vanguard001 / API server. Requires SMART_FACTORY_API.
"""

import os
from typing import Any, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("Install MCP SDK: pip install mcp requests")

import requests

from mcp.log_util import get_logger, log_tool_call

logger = get_logger("project-mcp")
_log = log_tool_call(logger)

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 30

mcp = FastMCP("project-mcp", json_response=True)


def _get(path: str, params: Optional[dict] = None) -> dict:
    r = requests.get(f"{API_BASE}{path}", params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, json_body: dict) -> dict:
    r = requests.post(f"{API_BASE}{path}", json=json_body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {"success": True}


def _patch(path: str, json_body: dict) -> dict:
    r = requests.patch(f"{API_BASE}{path}", json=json_body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {"success": True}


@mcp.tool()
@_log
def list_requirements(
    status: Optional[str] = None,
    assigned_team: Optional[str] = None,
    type_: Optional[str] = None,
    assignable: Optional[bool] = None,
) -> list:
    """Query requirements list. Filter by status, assigned_team, type. Use assignable=True for status=new and dependency-satisfied."""
    params = {}
    if status:
        params["status"] = status
    if assigned_team:
        params["assigned_team"] = assigned_team
    if type_:
        params["type"] = type_
    if assignable is not None:
        params["assignable"] = 1 if assignable else 0
    return _get("/requirements", params)


@mcp.tool()
@_log
def get_requirement(requirement_id: int) -> dict:
    """Get a single requirement by ID."""
    return _get(f"/requirements/{requirement_id}")


@mcp.tool()
@_log
def create_requirement(
    title: str,
    description: str = "",
    type: str = "feature",
    project_id: Optional[int] = None,
    priority: Optional[str] = None,
) -> dict:
    """Create a new requirement (including type=bug). Returns new requirement id."""
    body = {"title": title, "description": description, "type": type}
    if project_id is not None:
        body["project_id"] = project_id
    if priority:
        body["priority"] = priority
    return _post("/requirements", body)


@mcp.tool()
@_log
def update_requirement(requirement_id: int, fields: dict) -> dict:
    """Update requirement fields (e.g. status, assigned_team, depends_on)."""
    return _patch(f"/requirements/{requirement_id}", fields)


@mcp.tool()
@_log
def assign_requirement(requirement_id: int, assigned_team: str) -> dict:
    """Assign a requirement to a team (e.g. jarvis, codeforge, newton, tesla)."""
    return _post(f"/requirements/{requirement_id}/assign", {"assigned_team": assigned_team})


@mcp.tool()
@_log
def take_requirement(
    requirement_id: int,
    assigned_team: str,
    assigned_agent: str,
) -> dict:
    """Team takes the requirement and records the agent."""
    return _post(
        f"/requirements/{requirement_id}/take",
        {"assigned_team": assigned_team, "assigned_agent": assigned_agent},
    )


@mcp.tool()
@_log
def list_tasks(requirement_id: int) -> list:
    """List tasks for a requirement. Returns tasks with id, status, executor, next_step_task_id, risk, blocker, est_tokens_total, prompt_rounds."""
    return _get(f"/requirements/{requirement_id}/tasks")


@mcp.tool()
@_log
def get_task(task_id: int) -> dict:
    """Get a single task by ID (includes next_step_task_id, risk, blocker, est_tokens_total, prompt_rounds)."""
    return _get(f"/tasks/{task_id}")


@mcp.tool()
@_log
def update_task(task_id: int, fields: dict) -> dict:
    """Update a task. Fields: status, executor, title, step, output_path, next_step_task_id, risk, blocker,
    est_tokens_total, prompt_rounds (approximate LLM usage; non-negative integers)."""
    return _patch(f"/tasks/{task_id}", fields)


@mcp.tool()
@_log
def report_status(
    team: str,
    requirement_id: int,
    progress: Optional[int] = None,
    step: Optional[str] = None,
    tasks: Optional[list] = None,
    requirement_title: Optional[str] = None,
    machine_info: Optional[dict] = None,
) -> dict:
    """Submit team status report (progress, step, tasks). tasks[] items may include id, status, executor, risk, blocker, next_step_task_id, est_tokens_total, prompt_rounds; server syncs these to DB."""
    body = {"team": team, "requirement_id": requirement_id}
    if progress is not None:
        body["progress_percent"] = progress
    if step:
        body["step"] = step
    if tasks is not None:
        body["tasks"] = tasks
    if requirement_title:
        body["requirement_title"] = requirement_title
    if machine_info is not None:
        body["machine_info"] = machine_info
    return _post(f"/teams/{team}/status-report", body)


@mcp.tool()
@_log
def report_blockage(
    team: str,
    requirement_id: int,
    reason: str,
    task_id: Optional[int] = None,
    options: Optional[Any] = None,
) -> dict:
    """Report a blockage or decision item for Hera."""
    body = {"team": team, "requirement_id": requirement_id, "reason": reason}
    if task_id is not None:
        body["task_id"] = task_id
    if options is not None:
        body["options"] = options
    return _post("/discussion/blockage", body)


@mcp.tool()
@_log
def list_blockages(status: Optional[str] = "pending") -> list:
    """List blockages (Hera). status=pending or empty for all."""
    params = {"status": status} if status else {}
    return _get("/discussion/blockages", params)


@mcp.tool()
@_log
def resolve_blockage(
    blockage_id: int,
    decision: Optional[str] = None,
    status: str = "resolved",
) -> dict:
    """Hera: resolve a blockage with decision and status."""
    body = {"status": status}
    if decision:
        body["decision"] = decision
    return _patch(f"/discussion/blockage/{blockage_id}", body)


@mcp.tool()
@_log
def list_teams_online(within_minutes: Optional[int] = 40) -> list:
    """Get list of online teams (based on recent status report / machine heartbeat)."""
    data = _get("/teams/online")
    return data.get("teams", [])


@mcp.tool()
@_log
def get_team_assigned(team: str) -> list:
    """Get requirements currently assigned to a team."""
    return _get(f"/teams/{team}/assigned-requirements")


@mcp.tool()
@_log
def report_task_detail(
    team: str,
    requirement_id: int,
    detail_type: str,
    content: str,
    task_id: Optional[int] = None,
) -> dict:
    """Report requirement/task detail for final report. detail_type: analysis | assignment | development. Use for analyze/breakdown and sub-task assignment details."""
    body = {"requirement_id": requirement_id, "detail_type": detail_type, "content": content}
    if task_id is not None:
        body["task_id"] = task_id
    return _post(f"/teams/{team}/task-detail", body)


@mcp.tool()
@_log
def report_machine_status(
    team: str,
    payload: dict,
    reporter_agent: Optional[str] = None,
) -> dict:
    """Report machine status for a team (custom payload: hostname, platform, cpu, etc.)."""
    body = {"payload": payload}
    if reporter_agent:
        body["reporter_agent"] = reporter_agent
    return _post(f"/teams/{team}/machine-status", body)


# ----- Sync game plan to DB (moved from subsystems/tools) -----

@mcp.tool()
@_log
def sync_pinball_plan() -> dict:
    """Sync pinball-experience BASELINE_STEPS and FEATURE_STEPS to Smart Factory DB. Creates/updates requirements with plan_step_id. Run on server where DB lives (e.g. Vanguard001)."""
    from mcp.remote.project_mcp import sync_plan
    return sync_plan.run_sync()


if __name__ == "__main__":
    import sys
    transport = "streamable-http" if "--transport" in sys.argv and "streamable-http" in sys.argv else "stdio"
    port = 8001
    if "--port" in sys.argv:
        i = sys.argv.index("--port")
        if i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    logger.info("Starting project-mcp transport=%s port=%s", transport, port if transport == "streamable-http" else "N/A")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")
