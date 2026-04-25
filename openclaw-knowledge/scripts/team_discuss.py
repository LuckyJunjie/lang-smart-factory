#!/usr/bin/env python3
"""
Team Discussion Reporter - 团队讨论记录
Usage: 
  python team_discuss.py --team newton --message "讨论内容"
  python team_discuss.py --team newton --list

队员可使用此脚本记录团队讨论
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


def list_discussions(base, team):
    """列出团队讨论"""
    try:
        r = requests.get(f"{base}/api/discussion/blockages?team={team}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error: {e}")
    return []


def post_discussion(base, team, message, requirement_id=0):
    """发布讨论消息"""
    try:
        # 使用 blockage API 作为讨论记录（复用已有表结构）
        r = requests.post(f"{base}/api/discussion/blockage", json={
            "team": team,
            "requirement_id": requirement_id,
            "reason": f"[讨论] {message}",
            "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "discussing",
        }, timeout=10)
        
        if r.status_code in (200, 201):
            return True, r.json()
        else:
            return False, r.text
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="团队讨论")
    parser.add_argument("--team", required=True, help="团队名称")
    parser.add_argument("--message", help="讨论消息")
    parser.add_argument("--requirement-id", type=int, default=0, help="需求ID (可选)")
    parser.add_argument("--list", action="store_true", help="列出讨论")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    args = parser.parse_args()
    
    base = args.api_base.rstrip("/")
    
    if args.list:
        # 列出讨论
        discussions = list_discussions(base, args.team)
        if discussions:
            print(f"=== {args.team} 团队讨论 ===")
            for d in discussions:
                print(f"- {d.get('reported_at')}: {d.get('reason', '')}")
        else:
            print("无讨论记录")
    elif args.message:
        # 发布讨论
        success, result = post_discussion(base, args.team, args.message, args.requirement_id)
        if success:
            print(f"✅ 讨论已发布: {args.message}")
        else:
            print(f"❌ 发布失败: {result}")
            return 1
    else:
        print("请指定 --message 或 --list")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
