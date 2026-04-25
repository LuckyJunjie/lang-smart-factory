#!/usr/bin/env python3
"""
Skill: parse_requirement_doc
Executor: Any agent
Flow: extract_requirements(document_path) -> create_requirement for each.
Uses analysis-mcp style extraction + Smart Factory API to create requirements.
"""

import os
import re
import sys
import argparse
from pathlib import Path

from .log_util import get_logger

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

LOG = get_logger("parse_requirement_doc")

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15


def extract_requirements(document_path: str) -> list:
    p = Path(document_path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    requirements = []
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if re.match(r"^#+\s*(需求|requirement|feature|task)", line, re.I):
            requirements.append(line.lstrip("#").strip())
        elif re.match(r"^[-*]\s+\[.\]\s+", line):
            requirements.append(re.sub(r"^[-*]\s+\[.\]\s+", "", line))
        elif re.match(r"^\d+[.)]\s+", line):
            requirements.append(re.sub(r"^\d+[.)]\s+", "", line))
    return requirements[:50]


def main():
    parser = argparse.ArgumentParser(description="Extract requirements from PRD doc and create via API")
    parser.add_argument("document_path", help="Path to PRD or markdown document")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--project-id", type=int, help="Project ID for new requirements")
    parser.add_argument("--dry-run", action="store_true", help="Only extract, do not create")
    args = parser.parse_args()
    LOG.info("start document_path=%s api_base=%s project_id=%s dry_run=%s", args.document_path, args.api_base, args.project_id, args.dry_run)

    reqs = extract_requirements(args.document_path)
    LOG.info("extracted %d requirement(s)", len(reqs))
    print(f"Extracted {len(reqs)} requirement(s)")
    for i, r in enumerate(reqs):
        print(f"  {i+1}. {r[:80]}...")

    if args.dry_run or not reqs:
        return 0

    created = 0
    for title in reqs:
        body = {"title": title[:200], "description": title, "type": "feature"}
        if args.project_id is not None:
            body["project_id"] = args.project_id
        try:
            resp = requests.post(f"{args.api_base}/requirements", json=body, timeout=TIMEOUT)
            if resp.status_code in (200, 201):
                created += 1
                LOG.info("created requirement id=%s title=%s", resp.json().get("id"), title[:50])
                print("Created:", resp.json().get("id"), title[:50])
        except Exception as e:
            LOG.warning("create failed title=%s error=%s", title[:50], e)
            print("Failed:", title[:50], e)
    LOG.info("done created=%d", created)
    print(f"Created {created} requirements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
