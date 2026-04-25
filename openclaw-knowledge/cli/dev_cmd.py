"""Dev CLI: file, Git, run command, build. Replaces dev-mcp. Run on agent machine."""
import argparse

from cli._base import out, err, get_cwd


def add_parser(sp):
    p = sp.add_parser("dev", help="File read/write, Git, run command (whitelist), build")
    sub = p.add_subparsers(dest="dev_cmd", required=True)

    # read-file
    r = sub.add_parser("read-file", help="Read file content")
    r.add_argument("path", help="Path (relative to --cwd)")
    r.add_argument("--cwd", default=None)
    r.set_defaults(_run=_run_read_file)

    # write-file
    w = sub.add_parser("write-file", help="Write content to file")
    w.add_argument("path")
    w.add_argument("--content", required=True)
    w.add_argument("--cwd", default=None)
    w.set_defaults(_run=_run_write_file)

    # list-dir
    l = sub.add_parser("list-dir", help="List directory entries")
    l.add_argument("path", help="Directory path")
    l.add_argument("--cwd", default=None)
    l.set_defaults(_run=_run_list_directory)

    # git-status
    gs = sub.add_parser("git-status", help="Git status (changed files)")
    gs.add_argument("repo_path", help="Repository path")
    gs.set_defaults(_run=_run_git_status)

    # git-commit
    gc = sub.add_parser("git-commit", help="Commit all changes")
    gc.add_argument("repo_path")
    gc.add_argument("--message", "-m", required=True)
    gc.set_defaults(_run=_run_git_commit)

    # git-push
    gp = sub.add_parser("git-push", help="Push to remote")
    gp.add_argument("repo_path")
    gp.add_argument("--remote", default=None)
    gp.set_defaults(_run=_run_git_push)

    # run-command
    rc = sub.add_parser("run-command", help="Run whitelisted command (make, gradle, npm, python, git)")
    rc.add_argument("command", help="Program name")
    rc.add_argument("args", nargs="*", help="Arguments")
    rc.add_argument("--cwd", default=None)
    rc.set_defaults(_run=_run_run_command)

    # build
    b = sub.add_parser("build", help="Run build (Makefile, gradle, or npm run build)")
    b.add_argument("project_path", help="Project root")
    b.add_argument("--target", default=None)
    b.set_defaults(_run=_run_build)


def _run_read_file(args):
    from mcp.local.dev_mcp.server import read_file
    cwd = args.cwd or get_cwd()
    content = read_file(path=args.path, cwd=cwd)
    return {"content": content}


def _run_write_file(args):
    from mcp.local.dev_mcp.server import write_file
    cwd = args.cwd or get_cwd()
    return write_file(path=args.path, content=args.content, cwd=cwd)


def _run_list_directory(args):
    from mcp.local.dev_mcp.server import list_directory
    cwd = args.cwd or get_cwd()
    return list_directory(path=args.path, cwd=cwd)


def _run_git_status(args):
    from mcp.local.dev_mcp.server import git_status
    return git_status(repo_path=args.repo_path)


def _run_git_commit(args):
    from mcp.local.dev_mcp.server import git_commit
    return git_commit(repo_path=args.repo_path, message=args.message)


def _run_git_push(args):
    from mcp.local.dev_mcp.server import git_push
    return git_push(repo_path=args.repo_path, remote=args.remote)


def _run_run_command(args):
    from mcp.local.dev_mcp.server import run_command
    cwd = args.cwd or get_cwd()
    return run_command(command=args.command, args=args.args or None, cwd=cwd)


def _run_build(args):
    from mcp.local.dev_mcp.server import build_project
    return build_project(project_path=args.project_path, target=args.target)


def run(args):
    if not hasattr(args, "_run"):
        err("dev: missing subcommand")
    return args._run(args)
