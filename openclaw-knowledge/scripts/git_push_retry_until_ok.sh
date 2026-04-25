#!/usr/bin/env bash
# OpenClaw: retry git push every 5 minutes via cron until success, then remove this job from crontab.
# Usage:
#   chmod +x git_push_retry_until_ok.sh
#   crontab -e
# Add (adjust paths / branch):
#   */5 * * * * /path/to/smart-factory/openclaw-knowledge/scripts/git_push_retry_until_ok.sh /path/to/your/git/repo origin main
#
# On success, all crontab lines containing this script name are removed (keep a single retry job per device).

set -u
REPO="${1:-.}"
REMOTE="${2:-origin}"
BRANCH="${3:-}"

cd "$REPO" || { echo "cannot cd to $REPO" >&2; exit 1; }
REPO_ABS="$(pwd)"
if [[ -z "$BRANCH" ]]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || { echo "not a git repo: $REPO_ABS" >&2; exit 1; }
fi

LOG="${OPENCLAW_GIT_PUSH_RETRY_LOG:-${HOME}/.openclaw-git-push-retry.log}"
STAMP="$(date -Iseconds 2>/dev/null || date)"
echo "[$STAMP] try push $REPO_ABS $REMOTE $BRANCH" >> "$LOG"

if git push "$REMOTE" "$BRANCH" >>"$LOG" 2>&1; then
  echo "[$STAMP] SUCCESS $REPO_ABS $REMOTE $BRANCH — removing cron lines for this script" >> "$LOG"
  # shellcheck disable=SC2002
  if command -v crontab >/dev/null 2>&1; then
    TMP="$(mktemp)"
    (crontab -l 2>/dev/null || true) | grep -v "git_push_retry_until_ok.sh" >"$TMP" || true
    crontab "$TMP" 2>/dev/null || true
    rm -f "$TMP"
  fi
  exit 0
fi

echo "[$STAMP] FAILED (will retry on next cron)" >> "$LOG"
exit 0
