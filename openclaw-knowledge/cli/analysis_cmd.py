"""Analysis CLI: code analysis, extract requirements, complexity, summarize changes. Replaces analysis-mcp."""
import argparse

from cli._base import err, get_cwd


def add_parser(sp):
    p = sp.add_parser("analysis", help="Code analysis, doc extraction, complexity, diff summary")
    sub = p.add_subparsers(dest="analysis_cmd", required=True)

    # analyze-code
    a = sub.add_parser("analyze-code", help="Run gdlint/pylint etc. on path")
    a.add_argument("path")
    a.add_argument("--rules", default=None, help="Comma-separated rules")
    a.add_argument("--cwd", default=None)
    a.set_defaults(_run=_run_analyze_code)

    # extract-requirements
    e = sub.add_parser("extract-requirements", help="Extract requirement-like items from document")
    e.add_argument("document_path")
    e.set_defaults(_run=_run_extract_requirements)

    # estimate-complexity
    c = sub.add_parser("estimate-complexity", help="Estimate task/code complexity from text")
    c.add_argument("input_text", help="Description or code snippet")
    c.set_defaults(_run=_run_estimate_complexity)

    # summarize-changes
    s = sub.add_parser("summarize-changes", help="Summarize git diff (files, +/‑ lines)")
    s.add_argument("git_diff", help="Git diff text (or - for stdin)")
    s.set_defaults(_run=_run_summarize_changes)


def _run_analyze_code(args):
    from mcp.local.analysis_mcp.server import analyze_code
    cwd = args.cwd or get_cwd()
    rules = args.rules.split(",") if args.rules else None
    return analyze_code(path=args.path, rules=rules, cwd=cwd)


def _run_extract_requirements(args):
    from mcp.local.analysis_mcp.server import extract_requirements
    return extract_requirements(document_path=args.document_path)


def _run_estimate_complexity(args):
    from mcp.local.analysis_mcp.server import estimate_complexity
    return estimate_complexity(input_text=args.input_text)


def _run_summarize_changes(args):
    from mcp.local.analysis_mcp.server import summarize_changes
    if args.git_diff == "-":
        import sys
        git_diff = sys.stdin.read()
    else:
        git_diff = args.git_diff
    result = summarize_changes(git_diff=git_diff)
    return {"summary": result}


def run(args):
    if not hasattr(args, "_run"):
        err("analysis: missing subcommand")
    return args._run(args)
