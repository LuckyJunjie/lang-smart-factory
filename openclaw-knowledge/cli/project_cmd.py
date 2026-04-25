"""Project CLI: requirements, teams, blockages (Smart Factory API). Replaces project-mcp."""
import argparse
import json

from cli._base import out, err


def add_parser(sp):
    p = sp.add_parser("project", help="Requirements, teams, blockages (Smart Factory API)")
    sub = p.add_subparsers(dest="project_cmd", required=True)

    # list-requirements
    q = sub.add_parser("list-requirements", help="Query requirements; filter by status, team, type, assignable")
    q.add_argument("--status", help="Filter by status (e.g. new, developed)")
    q.add_argument("--assigned-team", help="Filter by assigned_team")
    q.add_argument("--type", dest="type_", help="Filter by type (e.g. feature, bug)")
    q.add_argument("--assignable", type=lambda x: x.lower() == "true" or x == "1", metavar="BOOL",
                   default=None, help="Only assignable (status=new, deps satisfied)")
    q.set_defaults(_run=_run_list_requirements)

    # get-requirement
    g = sub.add_parser("get-requirement", help="Get single requirement by ID")
    g.add_argument("id", type=int, help="Requirement ID")
    g.set_defaults(_run=_run_get_requirement)

    # create-requirement
    c = sub.add_parser("create-requirement", help="Create requirement (incl. type=bug)")
    c.add_argument("--title", required=True)
    c.add_argument("--description", default="")
    c.add_argument("--type", default="feature", help="feature or bug")
    c.add_argument("--project-id", type=int, default=None)
    c.add_argument("--priority", default=None)
    c.set_defaults(_run=_run_create_requirement)

    # update-requirement
    u = sub.add_parser("update-requirement", help="Update requirement fields")
    u.add_argument("id", type=int)
    u.add_argument("--fields", required=True, help="JSON object e.g. '{\"status\":\"developed\"}'")
    u.set_defaults(_run=_run_update_requirement)

    # assign-requirement
    a = sub.add_parser("assign-requirement", help="Assign requirement to team")
    a.add_argument("id", type=int)
    a.add_argument("--team", required=True, dest="assigned_team", help="jarvis, codeforge, newton, tesla")
    a.set_defaults(_run=_run_assign_requirement)

    # take-requirement
    t = sub.add_parser("take-requirement", help="Team takes requirement (record agent)")
    t.add_argument("id", type=int)
    t.add_argument("--team", required=True, dest="assigned_team")
    t.add_argument("--agent", required=True, dest="assigned_agent")
    t.set_defaults(_run=_run_take_requirement)

    # report-status
    r = sub.add_parser("report-status", help="Submit team status report")
    r.add_argument("--team", required=True)
    r.add_argument("--requirement-id", type=int, required=True)
    r.add_argument("--progress", type=int, default=None)
    r.add_argument("--step", default=None)
    r.add_argument("--tasks", default=None, help="JSON array: [{id, title?, status?, executor?, risk?, blocker?, next_step_task_id?}] (synced to DB)")
    r.add_argument("--requirement-title", default=None)
    r.add_argument("--machine-info", default=None, help="JSON object")
    r.set_defaults(_run=_run_report_status)

    # report-task-detail
    rtd = sub.add_parser("report-task-detail", help="Report requirement/task detail (analysis, assignment, or development) for final report")
    rtd.add_argument("--team", required=True)
    rtd.add_argument("--requirement-id", type=int, required=True)
    rtd.add_argument("--detail-type", required=True, choices=["analysis", "assignment", "development"])
    rtd.add_argument("--content", required=True)
    rtd.add_argument("--task-id", type=int, default=None)
    rtd.set_defaults(_run=_run_report_task_detail)

    # report-blockage
    b = sub.add_parser("report-blockage", help="Report blockage for Hera")
    b.add_argument("--team", required=True)
    b.add_argument("--requirement-id", type=int, required=True)
    b.add_argument("--reason", required=True)
    b.add_argument("--task-id", type=int, default=None)
    b.add_argument("--options", default=None, help="JSON object")
    b.set_defaults(_run=_run_report_blockage)

    # list-blockages
    lb = sub.add_parser("list-blockages", help="List blockages (Hera)")
    lb.add_argument("--status", default="pending")
    lb.set_defaults(_run=_run_list_blockages)

    # resolve-blockage
    rb = sub.add_parser("resolve-blockage", help="Resolve blockage (Hera)")
    rb.add_argument("id", type=int, help="Blockage ID")
    rb.add_argument("--decision", default=None)
    rb.add_argument("--status", default="resolved")
    rb.set_defaults(_run=_run_resolve_blockage)

    # list-teams-online
    lo = sub.add_parser("list-teams-online", help="Get online teams")
    lo.add_argument("--within-minutes", type=int, default=40)
    lo.set_defaults(_run=_run_list_teams_online)

    # list-tasks
    lt = sub.add_parser(
        "list-tasks",
        help="List tasks for a requirement (includes next_step_task_id, risk, blocker, est_tokens_total, prompt_rounds)",
    )
    lt.add_argument("requirement_id", type=int, help="Requirement ID")
    lt.set_defaults(_run=_run_list_tasks)

    # update-task
    ut = sub.add_parser("update-task", help="Update task (status, executor, next_step_task_id, risk, blocker)")
    ut.add_argument("id", type=int, help="Task ID")
    ut.add_argument("--fields", required=True, help="JSON object e.g. '{\"status\":\"blocked\",\"next_step_task_id\":42}'")
    ut.set_defaults(_run=_run_update_task)

    # get-team-assigned
    ga = sub.add_parser("get-team-assigned", help="Get requirements assigned to team")
    ga.add_argument("team", help="jarvis, codeforge, newton, tesla")
    ga.set_defaults(_run=_run_get_team_assigned)

    # report-machine-status
    rm = sub.add_parser("report-machine-status", help="Report machine status for team")
    rm.add_argument("--team", required=True)
    rm.add_argument("--payload", required=True, help="JSON object (hostname, platform, etc.)")
    rm.add_argument("--reporter-agent", default=None)
    rm.set_defaults(_run=_run_report_machine_status)

    # record-task-usage (approximate LLM tokens / prompt rounds on task)
    ru = sub.add_parser(
        "record-task-usage",
        help="Record approximate est_tokens_total and/or prompt_rounds on a task (increment or set)",
    )
    ru.add_argument("id", type=int, help="Task ID")
    ru.add_argument("--add-tokens", type=int, default=0, help="Add to est_tokens_total")
    ru.add_argument("--add-prompts", type=int, default=0, help="Add to prompt_rounds (LLM call count)")
    ru.add_argument("--set-tokens", type=int, default=None, help="Set est_tokens_total (overrides add)")
    ru.add_argument("--set-prompts", type=int, default=None, help="Set prompt_rounds (overrides add)")
    ru.set_defaults(_run=_run_record_task_usage)

    # sync-pinball-plan
    sync = sub.add_parser("sync-pinball-plan", help="Sync pinball-experience plan to DB (run on server)")
    sync.set_defaults(_run=_run_sync_pinball_plan)


def _run_list_requirements(args):
    from mcp.remote.project_mcp.server import list_requirements
    return list_requirements(
        status=args.status,
        assigned_team=args.assigned_team,
        type_=args.type_,
        assignable=args.assignable,
    )


def _run_get_requirement(args):
    from mcp.remote.project_mcp.server import get_requirement
    return get_requirement(args.id)


def _run_create_requirement(args):
    from mcp.remote.project_mcp.server import create_requirement
    return create_requirement(
        title=args.title,
        description=args.description,
        type=args.type,
        project_id=args.project_id,
        priority=args.priority,
    )


def _run_update_requirement(args):
    from mcp.remote.project_mcp.server import update_requirement
    fields = json.loads(args.fields)
    return update_requirement(args.id, fields)


def _run_assign_requirement(args):
    from mcp.remote.project_mcp.server import assign_requirement
    return assign_requirement(args.id, args.assigned_team)


def _run_take_requirement(args):
    from mcp.remote.project_mcp.server import take_requirement
    return take_requirement(args.id, args.assigned_team, args.assigned_agent)


def _run_report_status(args):
    from mcp.remote.project_mcp.server import report_status
    tasks = json.loads(args.tasks) if args.tasks else None
    machine_info = json.loads(args.machine_info) if args.machine_info else None
    return report_status(
        team=args.team,
        requirement_id=args.requirement_id,
        progress=args.progress,
        step=args.step,
        tasks=tasks,
        requirement_title=args.requirement_title,
        machine_info=machine_info,
    )


def _run_list_tasks(args):
    from mcp.remote.project_mcp.server import list_tasks
    return list_tasks(args.requirement_id)


def _run_report_task_detail(args):
    from mcp.remote.project_mcp.server import report_task_detail
    return report_task_detail(
        team=args.team,
        requirement_id=args.requirement_id,
        detail_type=args.detail_type,
        content=args.content,
        task_id=args.task_id,
    )


def _run_update_task(args):
    from mcp.remote.project_mcp.server import update_task
    fields = json.loads(args.fields)
    return update_task(args.id, fields)


def _run_record_task_usage(args):
    from mcp.remote.project_mcp.server import get_task, update_task
    t = get_task(args.id)
    cur_tok = int(t.get("est_tokens_total") or 0)
    cur_pr = int(t.get("prompt_rounds") or 0)
    new_tok = cur_tok
    new_pr = cur_pr
    if args.set_tokens is not None:
        new_tok = max(0, int(args.set_tokens))
    elif args.add_tokens:
        new_tok = cur_tok + int(args.add_tokens)
    if args.set_prompts is not None:
        new_pr = max(0, int(args.set_prompts))
    elif args.add_prompts:
        new_pr = cur_pr + int(args.add_prompts)
    fields = {}
    if args.set_tokens is not None or args.add_tokens:
        fields["est_tokens_total"] = new_tok
    if args.set_prompts is not None or args.add_prompts:
        fields["prompt_rounds"] = new_pr
    if not fields:
        return {"task_id": args.id, "est_tokens_total": cur_tok, "prompt_rounds": cur_pr, "note": "no changes; pass --add-tokens/--add-prompts or --set-*"}
    update_task(args.id, fields)
    out = get_task(args.id)
    return {
        "task_id": args.id,
        "est_tokens_total": out.get("est_tokens_total"),
        "prompt_rounds": out.get("prompt_rounds"),
    }


def _run_report_blockage(args):
    from mcp.remote.project_mcp.server import report_blockage
    options = json.loads(args.options) if args.options else None
    return report_blockage(
        team=args.team,
        requirement_id=args.requirement_id,
        reason=args.reason,
        task_id=args.task_id,
        options=options,
    )


def _run_list_blockages(args):
    from mcp.remote.project_mcp.server import list_blockages
    return list_blockages(status=args.status or None)


def _run_resolve_blockage(args):
    from mcp.remote.project_mcp.server import resolve_blockage
    return resolve_blockage(args.id, decision=args.decision, status=args.status)


def _run_list_teams_online(args):
    from mcp.remote.project_mcp.server import list_teams_online
    return list_teams_online(within_minutes=args.within_minutes)


def _run_get_team_assigned(args):
    from mcp.remote.project_mcp.server import get_team_assigned
    return get_team_assigned(args.team)


def _run_report_machine_status(args):
    from mcp.remote.project_mcp.server import report_machine_status
    payload = json.loads(args.payload)
    return report_machine_status(team=args.team, payload=payload, reporter_agent=args.reporter_agent)


def _run_sync_pinball_plan(args):
    from mcp.remote.project_mcp.server import sync_pinball_plan
    return sync_pinball_plan()


def run(args):
    if not hasattr(args, "_run"):
        err("project: missing subcommand")
    return args._run(args)
