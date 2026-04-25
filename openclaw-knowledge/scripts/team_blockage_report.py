#!/usr/bin/env python3
"""
Team Blockage Reporter - 简化的阻塞上报
Usage: python team_blockage_report.py --team newton --reason "需要 API 文档"

队员可直接使用此脚本上报阻塞问题
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000")


def main():
    parser = argparse.ArgumentParser(description="团队阻塞上报")
    parser.add_argument("--team", required=True, help="团队名称")
    parser.add_argument("--requirement-id", type=int, required=True, help="需求ID")
    parser.add_argument("--reason", required=True, help="阻塞原因")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    args = parser.parse_args()
    
    base = args.api_base.rstrip("/")
    
    # 上报阻塞
    try:
        r = requests.post(f"{base}/api/discussion/blockage", json={
            "team": args.team,
            "requirement_id": args.requirement_id if args.requirement_id else None,
            "reason": args.reason,
            "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }, timeout=10)
        
        if r.status_code in (200, 201):
            print(f"✅ 阻塞已上报: {args.team} - {args.reason}")
        else:
            print(f"❌ 上报失败: {r.text}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"❌ 上报失败: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
