"""Communication CLI: Feishu, email, Feishu log analysis. Replaces comm-mcp."""
import argparse

from cli._base import out, err


def add_parser(sp):
    p = sp.add_parser("comm", help="Feishu, email, Feishu API log analysis")
    sub = p.add_subparsers(dest="comm_cmd", required=True)

    # send-feishu
    s = sub.add_parser("send-feishu", help="Send message to Feishu")
    s.add_argument("--content", required=True)
    s.add_argument("--webhook-url", default=None)
    s.add_argument("--msg-type", default=None)
    s.add_argument("--title", default=None)
    s.set_defaults(_run=_run_send_feishu)

    # send-email
    e = sub.add_parser("send-email", help="Send email (no-op if not configured)")
    e.add_argument("--to", required=True)
    e.add_argument("--subject", required=True)
    e.add_argument("--body", required=True)
    e.set_defaults(_run=_run_send_email)

    # analyze-feishu-logs
    a = sub.add_parser("analyze-feishu-logs", help="Parse Gateway log, save to DB, return stats")
    a.add_argument("--log-file", default=None)
    a.set_defaults(_run=_run_analyze_feishu_logs)

    # get-feishu-stats
    g = sub.add_parser("get-feishu-stats", help="Get Feishu API call stats from DB")
    g.add_argument("--limit", type=int, default=20)
    g.set_defaults(_run=_run_get_feishu_stats)

    # analyze-feishu-issues
    i = sub.add_parser("analyze-feishu-issues", help="Analyze log for issues (polling, errors)")
    i.add_argument("--log-file", default=None)
    i.set_defaults(_run=_run_analyze_feishu_issues)


def _run_send_feishu(args):
    from mcp.remote.comm_mcp.server import send_feishu_message
    return send_feishu_message(
        content=args.content,
        webhook_url=args.webhook_url,
        msg_type=args.msg_type,
        title=args.title,
    )


def _run_send_email(args):
    from mcp.remote.comm_mcp.server import send_email
    return send_email(to=args.to, subject=args.subject, body=args.body)


def _run_analyze_feishu_logs(args):
    from mcp.remote.comm_mcp.server import analyze_feishu_logs
    return analyze_feishu_logs(log_file=args.log_file)


def _run_get_feishu_stats(args):
    from mcp.remote.comm_mcp.server import get_feishu_api_stats
    return get_feishu_api_stats(limit=args.limit)


def _run_analyze_feishu_issues(args):
    from mcp.remote.comm_mcp.server import analyze_feishu_issues
    return analyze_feishu_issues(log_file=args.log_file)


def run(args):
    if not hasattr(args, "_run"):
        err("comm: missing subcommand")
    return args._run(args)
