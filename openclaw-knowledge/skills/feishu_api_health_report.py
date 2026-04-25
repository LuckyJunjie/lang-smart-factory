#!/usr/bin/env python3
"""
Skill: feishu_api_health_report
Executor: Vanguard / ops
Analyzes Feishu API log (Gateway), optionally posts summary to Feishu.
Run: python -m skills.feishu_api_health_report [--log-file PATH] [--post] [--dry-run]
Or use comm_mcp tools: analyze_feishu_logs(), get_feishu_api_stats(), analyze_feishu_issues().
"""

import os
import sys
import argparse

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from .log_util import get_logger
from mcp.remote.comm_mcp import feishu_log_analysis

LOG = get_logger("feishu_api_health_report")

try:
    import requests
except ImportError:
    requests = None


def main():
    parser = argparse.ArgumentParser(description="Feishu API health: analyze log, optional post to Feishu")
    parser.add_argument("--log-file", "-l", default=None, help="Gateway log path")
    parser.add_argument("--post", action="store_true", help="Post summary to Feishu via API")
    parser.add_argument("--dry-run", action="store_true", help="Print only, no post")
    args = parser.parse_args()
    LOG.info("start log_file=%s post=%s dry_run=%s", args.log_file, args.post, args.dry_run)

    # Run full logger flow (parse, save to DB, report)
    result = feishu_log_analysis.run_analyze(log_file=args.log_file)
    if not result.get("success"):
        LOG.warning("analysis failed: %s", result.get("error", "Analysis failed"))
        print(result.get("error", "Analysis failed"), file=sys.stderr)
        return 1

    report = result.get("report", "")
    LOG.info("analysis success report_len=%d", len(report))
    print(report)

    if args.post and not args.dry_run and requests:
        api_base = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
        try:
            r = requests.post(
                f"{api_base}/feishu/post",
                json={"text": report[:4000], "title": "飞书API调用分析"},
                timeout=15,
            )
            r.raise_for_status()
            LOG.info("posted to Feishu")
            print("Posted to Feishu.")
        except Exception as e:
            LOG.exception("post to Feishu failed: %s", e)
            print(f"Post to Feishu failed: {e}", file=sys.stderr)
            return 1
    elif args.post and args.dry_run:
        LOG.info("dry-run would post to Feishu")
        print("[dry-run] Would post to Feishu.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
