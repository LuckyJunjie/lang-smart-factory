#!/usr/bin/env python3
"""
All Teams Status Aggregator - 汇总所有团队状态
每半小时运行一次，汇总所有团队的状态供 Hera/Vanguard 使用

Usage: python team_all_status.py [--api-base URL]
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000")

# 所有团队列表
ALL_TEAMS = ["newton", "tesla", "jarvis", "codeforge"]


def get_team_status(base, team):
    """获取单个团队状态"""
    try:
        r = requests.get(f"{base}/teams/{team}/status-report", timeout=10)
        if r.status_code == 200:
            reports = r.json()
            return reports[0] if reports else None
    except:
        pass
    return None


def get_team_task_details(base, team):
    """获取团队任务详情"""
    try:
        r = requests.get(f"{base}/teams/{team}/task-details", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def get_blockages(base):
    """获取所有阻塞问题"""
    try:
        r = requests.get(f"{base}/api/discussion/blockages", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def generate_summary_report(teams_status, all_task_details, blockages):
    """生成汇总报告"""
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    md = f"""## 🚀 Smart Factory 全团队状态汇总 - {report_time}

---
"""
    
    # 各团队状态
    for team in ALL_TEAMS:
        status = teams_status.get(team)
        tasks = all_task_details.get(team, [])
        
        md += f"### 👥 {team.capitalize()} 团队\n"
        
        if status:
            try:
                payload = json.loads(status.get("payload", "{}")) if isinstance(status.get("payload"), str) else status.get("payload", {})
                member_status = payload.get("member_status", [])
                
                if member_status:
                    md += f"| 成员 | 角色 | 需求 | 当前任务 | 状态 | 进度 | 预计剩余 |\n"
                    md += f"|------|------|------|----------|------|------|----------|\n"
                    for m in member_status:
                        status_emoji = "✅" if m.get("status") == "completed" else "🔄" if m.get("status") == "in_progress" else "⏳"
                        md += f"| {m.get('member', '')} | {m.get('role', '')} | {m.get('requirement', '')[:15]} | {m.get('current_task', '')[:15]} | {status_emoji} | {m.get('progress', 0)}% | {m.get('remaining', 'N/A')} |\n"
                else:
                    md += "_无任务状态_\n"
            except:
                md += "_无状态_\n"
        else:
            md += "_离线_\n"
        
        md += "\n"
    
    # 阻塞问题
    md += "### 🚧 阻塞问题\n"
    if blockages:
        for b in blockages:
            md += f"- **{b.get('team', '?')}**: {b.get('reason', '未知原因')}\n"
    else:
        md += "- 无\n"
    
    md += f"""
---
*汇总时间: {report_time}*
"""
    
    return md


def main():
    parser = argparse.ArgumentParser(description="全团队状态汇总")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    args = parser.parse_args()
    
    base = args.api_base.rstrip("/")
    
    # 获取各团队状态
    teams_status = {}
    all_task_details = {}
    
    for team in ALL_TEAMS:
        status = get_team_status(base, team)
        if status:
            teams_status[team] = status
        tasks = get_team_task_details(base, team)
        if tasks:
            all_task_details[team] = tasks
    
    # 获取阻塞问题
    blockages = get_blockages(base)
    
    # 生成报告
    report = generate_summary_report(teams_status, all_task_details, blockages)
    
    print(report)
    
    # 保存报告
    with open("/tmp/all_teams_status.md", "w") as f:
        f.write(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
