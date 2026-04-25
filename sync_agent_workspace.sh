#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
WORKSPACE_ROOT="$REPO_ROOT/openclaw-knowledge/organization/workspace"

usage() {
  cat <<'EOF'
Usage:
  ./sync_agent_workspace.sh <team>/<agent> [options]

Description:
  Copy files from openclaw-knowledge/organization/workspace/<team>/<agent>/ into repo root.
  This includes nested folders (subagent-related files) under that agent folder.

Options:
  --apply         Execute the copy. Without this flag, script runs in dry-run mode.
  --overwrite     Allow overwriting files in repo root if same path exists.
  --verbose       Print rsync output in detail.
  -h, --help      Show this help.

Examples:
  ./sync_agent_workspace.sh codeforge/luban
  ./sync_agent_workspace.sh codeforge/luban --apply
  ./sync_agent_workspace.sh tesla/model_3 --apply --overwrite
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -eq 0 ]]; then
  usage
  exit 0
fi

TARGET="${1:-}"
shift || true

if [[ "$TARGET" != */* ]]; then
  echo "Error: target must be in <team>/<agent> format, got '$TARGET'."
  exit 1
fi

SOURCE_DIR="$WORKSPACE_ROOT/$TARGET"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: source agent workspace does not exist: $SOURCE_DIR"
  exit 1
fi

DO_APPLY=0
ALLOW_OVERWRITE=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      DO_APPLY=1
      shift
      ;;
    --overwrite)
      ALLOW_OVERWRITE=1
      shift
      ;;
    --verbose)
      VERBOSE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown option '$1'"
      usage
      exit 1
      ;;
  esac
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is required but not found."
  exit 1
fi

RSYNC_ARGS=(-a --human-readable --itemize-changes)

# Keep repository internals untouched.
RSYNC_ARGS+=(--exclude ".git/" --exclude ".cursor/")

if [[ $ALLOW_OVERWRITE -eq 0 ]]; then
  RSYNC_ARGS+=(--ignore-existing)
fi

if [[ $VERBOSE -eq 1 ]]; then
  RSYNC_ARGS+=(-v)
fi

if [[ $DO_APPLY -eq 0 ]]; then
  RSYNC_ARGS+=(--dry-run)
  echo "[DRY RUN] Previewing copy from:"
else
  echo "[APPLY] Copying from:"
fi

echo "  $SOURCE_DIR/"
echo "to"
echo "  $REPO_ROOT/"
echo

if [[ $ALLOW_OVERWRITE -eq 0 ]]; then
  echo "Overwrite mode: OFF (existing root files are kept)"
else
  echo "Overwrite mode: ON (existing root files may be replaced)"
fi
echo

rsync "${RSYNC_ARGS[@]}" "$SOURCE_DIR/" "$REPO_ROOT/"

if [[ $DO_APPLY -eq 0 ]]; then
  echo
  echo "Dry-run complete. Add --apply to perform the copy."
fi
