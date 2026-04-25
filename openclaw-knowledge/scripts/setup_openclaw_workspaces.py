#!/usr/bin/env python3
"""
OpenClaw workspace layout bootstrapper for this repository.

Goal:
- Keep existing source-of-truth identity/docs under `organization/workspace/...`.
- Generate per-agent runtime workspaces under:
    <repo-root>/.openclaw-workspace/agents/<agent_id>/
- In each per-agent workspace, create symlinks so that:
  - `python -m cli ...` / `python -m skills...` work from the workspace root
  - markdown paths like `docs/...` and `openclaw-knowledge/...` still resolve (via a `smart-factory` symlink)

This script is designed to be re-runnable.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def _safe_rel_symlink(target: Path, link_path: Path) -> None:
    """
    Create symlink using a relative path for nicer portability across machines.
    """
    link_path_parent = link_path.parent
    link_path_parent.mkdir(parents=True, exist_ok=True)

    # Relative target from link parent.
    rel_target = os.path.relpath(str(target), str(link_path_parent))
    link_path.symlink_to(rel_target)


def _replace_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def ensure_link(target: Path, link_path: Path, *, force: bool) -> None:
    """
    Ensure link_path is a symlink pointing to target.
    If force=True, replace mismatched paths.
    """
    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink():
            try:
                current = link_path.resolve()
                if current == target.resolve():
                    return
            except FileNotFoundError:
                # Broken symlink, replace
                pass
        if not force:
            raise RuntimeError(f"Path already exists (not desired): {link_path}")
        _replace_path(link_path)

    _safe_rel_symlink(target, link_path)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Setup OpenClaw per-agent workspaces (symlinks + identity files).")
    p.add_argument("--force", action="store_true", help="Replace existing mismatched paths.")
    p.add_argument(
        "--only-team",
        default=None,
        help="If set, only process organization/workspace/<name>/ (e.g. tesla). "
        "Skips other top-level team folders. Combines with --only-agent.",
    )
    p.add_argument("--only-agent", default=None, help="If set, only generate this agent_id.")
    p.add_argument(
        "--workspace-name",
        default=".openclaw-workspace",
        help="Name of the workspace folder under repo root.",
    )
    p.add_argument(
        "--identity-root",
        default=None,
        help="Override identity root (default: <inner>/organization/workspace).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    script_path = Path(__file__).resolve()

    # Resolve repository root: openclaw-knowledge/, core/, docs/ at top level.
    code_root = None
    for p in script_path.parents:
        if (p / "openclaw-knowledge").is_dir() and (p / "core").is_dir() and (p / "docs").is_dir():
            code_root = p
            break
    if code_root is None:
        raise RuntimeError(f"Could not locate repository root from script path: {script_path}")

    outer_root = code_root
    outer_game_root = outer_root / "archived" / "game"
    kb_root = code_root / "openclaw-knowledge"

    identity_root = (
        Path(args.identity_root).resolve()
        if args.identity_root
        else (kb_root / "organization" / "workspace").resolve()
    )

    workspace_root = (outer_root / args.workspace_name).resolve()
    agents_root = workspace_root / "agents"

    if not identity_root.is_dir():
        raise RuntimeError(f"Identity root not found: {identity_root}")

    # Candidate identity filenames in repo.
    identity_files = [
        "SOUL.md",
        "USER.md",
        "CONTEXT.md",
        "TOOLS.md",
        "IDENTITY.md",
        "AGENT.md",
        "HEARTBEAT.md",
        "SESSION.md",
    ]

    # For convenience: make sure agent workspaces have code available at workspace root.
    workspace_links = [
        ("cli", kb_root / "cli"),
        ("skills", kb_root / "skills"),
        ("mcp", kb_root / "mcp"),
        ("organization", kb_root / "organization"),
        ("workflows", kb_root / "workflows"),
        ("standards", kb_root / "standards"),
        ("openclaw-knowledge", kb_root),
        ("docs", code_root / "docs"),
        ("core", code_root / "core"),
        ("tests", code_root / "tests"),
        ("smart-factory", code_root),
    ]
    if outer_game_root.is_dir():
        workspace_links.append(("game", outer_game_root))

    def is_agent_workspace_dir(candidate: Path) -> bool:
        return any((candidate / fname).exists() for fname in identity_files)

    def setup_agent_workspace(agent_dir: Path) -> int:
        agent_id = agent_dir.name
        if args.only_agent and agent_id != args.only_agent:
            return 0

        dest_agent_root = agents_root / agent_id
        dest_agent_root.mkdir(parents=True, exist_ok=True)

        # Create code symlinks at workspace root so `python -m cli` works.
        for link_name, target_path in workspace_links:
            link_path = dest_agent_root / link_name
            if target_path.exists():
                ensure_link(target=target_path, link_path=link_path, force=args.force)

        # Link/copy identity files into workspace root.
        for fname in identity_files:
            src = agent_dir / fname
            if not src.exists() and not src.is_symlink():
                continue
            dst = dest_agent_root / fname
            if dst.exists() or dst.is_symlink():
                if not args.force:
                    continue
            ensure_link(target=src.resolve(), link_path=dst, force=args.force)

        # Prepare runtime directories (OpenClaw will write into them).
        (dest_agent_root / "memory").mkdir(parents=True, exist_ok=True)
        # sessions are created by OpenClaw; do not hard-create unless needed.
        return 1

    agents_created = 0

    for team_dir in sorted([d for d in identity_root.iterdir() if d.is_dir()]):
        if args.only_team and team_dir.name != args.only_team:
            continue
        # Support both layouts:
        # 1) organization/workspace/<agent>/[SOUL.md...]
        # 2) organization/workspace/<team>/<agent>/[SOUL.md...]
        if is_agent_workspace_dir(team_dir):
            agents_created += setup_agent_workspace(team_dir)

        for agent_dir in sorted([d for d in team_dir.iterdir() if d.is_dir()]):
            if is_agent_workspace_dir(agent_dir):
                agents_created += setup_agent_workspace(agent_dir)

    print(f"OpenClaw workspaces prepared: {agents_created} agent(s)")
    print(f"Workspace root: {workspace_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

