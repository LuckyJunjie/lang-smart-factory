#!/usr/bin/env python3
"""
Skill: record_task_usage
Approximate LLM usage per task: est_tokens_total (rough token estimate) and prompt_rounds (how many model/prompt invocations).
Use after a work chunk or at task completion; values are indicative, not billing-precision.

Prefer: python3 -m cli project record-task-usage <task_id> --add-tokens N --add-prompts N
This module mirrors that via HTTP for agents without CLI subprocess.
"""

from __future__ import annotations

import argparse
import os
import sys

from .log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("record_task_usage")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def main() -> int:
    p = argparse.ArgumentParser(description="Record approximate LLM token/prompt usage on a task")
    p.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    p.add_argument("--task-id", type=int, required=True, dest="task_id")
    p.add_argument("--add-tokens", type=int, default=0)
    p.add_argument("--add-prompts", type=int, default=0)
    p.add_argument("--set-tokens", type=int, default=None)
    p.add_argument("--set-prompts", type=int, default=None)
    args = p.parse_args()
    base = args.api_base.rstrip("/")

    r = requests.get(f"{base}/tasks/{args.task_id}", timeout=TIMEOUT)
    if r.status_code == 404:
        print("Task not found", file=sys.stderr)
        return 1
    r.raise_for_status()
    t = r.json()
    cur_tok = int(t.get("est_tokens_total") or 0)
    cur_pr = int(t.get("prompt_rounds") or 0)

    new_tok = cur_tok
    new_pr = cur_pr
    if args.set_tokens is not None:
        new_tok = max(0, args.set_tokens)
    elif args.add_tokens:
        new_tok = cur_tok + args.add_tokens
    if args.set_prompts is not None:
        new_pr = max(0, args.set_prompts)
    elif args.add_prompts:
        new_pr = cur_pr + args.add_prompts

    body = {}
    if args.set_tokens is not None or args.add_tokens:
        body["est_tokens_total"] = new_tok
    if args.set_prompts is not None or args.add_prompts:
        body["prompt_rounds"] = new_pr
    if not body:
        print(
            '{"task_id": %d, "est_tokens_total": %d, "prompt_rounds": %d, "note": "no change; use --add-* or --set-*"}'
            % (args.task_id, cur_tok, cur_pr)
        )
        return 0

    u = requests.patch(f"{base}/tasks/{args.task_id}", json=body, timeout=TIMEOUT)
    u.raise_for_status()
    g = requests.get(f"{base}/tasks/{args.task_id}", timeout=TIMEOUT)
    g.raise_for_status()
    out = g.json()
    LOG.info("task_id=%s est_tokens_total=%s prompt_rounds=%s", args.task_id, out.get("est_tokens_total"), out.get("prompt_rounds"))
    import json

    print(json.dumps({"task_id": args.task_id, "est_tokens_total": out.get("est_tokens_total"), "prompt_rounds": out.get("prompt_rounds")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
