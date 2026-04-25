#!/usr/bin/env python3
"""
Team Member Task Reporter - 团队成员汇报任务进度
Usage: python team_member_report.py --team newton --member einstein --task "API端点检查" --progress 50 --remaining 30

队员使用此脚本汇报当前任务进度和预计剩余时间。
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
    parser = argparse.ArgumentParser(description="团队成员任务汇报")
    parser.add_argument("--team", required=True, help="团队名称")
    parser.add_argument("--member", required=True, help="成员名称")
    parser.add_argument("--task", required=True, help="当前任务名称")
    parser.add_argument("--requirement-id", type=int, default=0, help="需求ID (可选)")
    parser.add_argument("--progress", type=int, default=0, help="完成百分比 (0-100)")
    parser.add_argument("--remaining", type=int, default=0, help="预计剩余分钟数")
    parser.add_argument("--status", default="in_progress", help="任务状态 (waiting/in_progress/completed)")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    args = parser.parse_args()
    
    base = args.api_base.rstrip("/")
    
    # 任务详情
    task_detail = {
        "task_title": args.task,
        "executor": args.member,
        "requirement_id": args.requirement_id,
        "status": args.status,
        "progress_percent": args.progress,
        "estimated_remaining_minutes": args.remaining,
        "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    # 通过 task-detail API 上报
    try:
        r = requests.post(f"{base}/teams/{args.team}/task-detail", json={
            "requirement_id": args.requirement_id if args.requirement_id else 0,
            "task_id": 0,
            "detail_type": "development",
            "content": json.dumps(task_detail, ensure_ascii=False),
        }, timeout=10)
        
        if r.status_code in (200, 201):
            print(f"✅ {args.member} 任务汇报成功: {args.task} - {args.progress}%")
            print(f"   预计剩余: {args.remaining} 分钟")
        else:
            print(f"❌ 汇报失败: {r.text}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"❌ 汇报失败: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
