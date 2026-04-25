"""Test CLI: unit/integration tests, coverage, parse output. Replaces test-mcp."""
import argparse

from cli._base import err, get_cwd


def add_parser(sp):
    p = sp.add_parser("test", help="Unit/integration tests, coverage, parse test output")
    sub = p.add_subparsers(dest="test_cmd", required=True)

    # run-unit-tests
    u = sub.add_parser("run-unit-tests", help="Run unit tests (pytest, unittest)")
    u.add_argument("framework", help="pytest or unittest")
    u.add_argument("test_path", help="Directory or file")
    u.add_argument("--cov", default=None, help="Coverage path for pytest")
    u.add_argument("--cwd", default=None)
    u.set_defaults(_run=_run_run_unit_tests)

    # run-integration-tests
    i = sub.add_parser("run-integration-tests", help="Run integration test suite")
    i.add_argument("test_suite", help="Path to suite or script")
    i.add_argument("--cwd", default=None)
    i.set_defaults(_run=_run_run_integration_tests)

    # check-coverage
    c = sub.add_parser("check-coverage", help="Collect coverage report")
    c.add_argument("--format", default="text", help="text or json")
    c.add_argument("--cwd", default=None)
    c.set_defaults(_run=_run_check_coverage)

    # parse-test-output
    pto = sub.add_parser("parse-test-output", help="Parse test output file to structured result")
    pto.add_argument("file_path")
    pto.set_defaults(_run=_run_parse_test_output)


def _run_run_unit_tests(args):
    from mcp.local.test_mcp.server import run_unit_tests
    cwd = args.cwd or get_cwd()
    options = {"cov": args.cov} if args.cov else None
    return run_unit_tests(
        framework=args.framework,
        test_path=args.test_path,
        options=options,
        cwd=cwd,
    )


def _run_run_integration_tests(args):
    from mcp.local.test_mcp.server import run_integration_tests
    cwd = args.cwd or get_cwd()
    return run_integration_tests(test_suite=args.test_suite, cwd=cwd)


def _run_check_coverage(args):
    from mcp.local.test_mcp.server import check_coverage
    cwd = args.cwd or get_cwd()
    return check_coverage(report_format=args.format, cwd=cwd)


def _run_parse_test_output(args):
    from mcp.local.test_mcp.server import parse_test_output
    return parse_test_output(file_path=args.file_path)


def run(args):
    if not hasattr(args, "_run"):
        err("test: missing subcommand")
    return args._run(args)
