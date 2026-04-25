#!/usr/bin/env python3
"""
Newton Team Status Reporter - 按 Tesla 风格汇报
包含：机器状态、团队成员状态、任务进度、预计剩余时间、阻塞问题

Usage: python team_newton_status.py --team newton [--api-base URL]
"""

import argparse
import json
import os
import platform
import socket
import sys
import psutil
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

# API runs only on Vanguard001 (192.168.3.75). Other nodes must call that host.
API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api")

# Newton 团队成员定义
TEAM_MEMBERS = {
    "einstein": {"role": "架构师/开发", "emoji": "🔬"},
    "athena": {"role": "文档/测试", "emoji": "📚"},
    "darwin": {"role": "Scrum Master", "emoji": "🧬"},
    "curie": {"role": "开发/DevOps", "emoji": "🧪"},
    "galileo": {"role": "开发", "emoji": "🔭"},
    "newton": {"role": "团队主管", "emoji": "🍎"},
}


def get_machine_status():
    """获取本机状态"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "cpu": f"{cpu_percent:.1f}%",
            "memory": f"{memory.percent:.1f}%",
            "load": load_avg,
        }
    except Exception as e:
        return {"hostname": socket.gethostname(), "error": str(e)}


def get_requirements(base, team):
    """获取团队的需求"""
    try:
        r = requests.get(f"{base}/requirements", params={"assigned_to": team}, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Warning: Could not fetch requirements: {e}")
    return []


def get_team_status_reports(base, team):
    """获取团队状态报告"""
    try:
        r = requests.get(f"{base}/teams/{team}/status-report", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Warning: Could not fetch status reports: {e}")
    return []


def get_task_details(base, team, requirement_id=None):
    """获取任务开发细节"""
    try:
        params = {}
        if requirement_id:
            params["requirement_id"] = requirement_id
        r = requests.get(f"{base}/teams/{team}/task-details", 
                        params=params,
                        timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Warning: Could not fetch task details: {e}")
    return []


def generate_markdown_report(team, machine_status, requirements, latest_report, task_details):
    """生成 Markdown 格式的汇报"""
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 过滤出当前团队的需求
    team_reqs = [req for req in requirements if req.get("assigned_to") == team]
    
    # 解析任务信息 - 优先从 task_details 获取，其次从 latest_report
    tasks_info = []
    
    # 先从 task_details 获取成员汇报
    member_reports = {}
    for td in task_details:
        try:
            content = json.loads(td.get("content", "{}"))
        except:
            content = {}
        member = content.get("executor", "").lower()
        if member:
            if member not in member_reports:
                member_reports[member] = []
            member_reports[member].append(content)
    
    # 构建需求ID到标题的映射
    requirement_map = {req.get("id"): req.get("title", "") for req in requirements}
    
    # 解析 latest_report 中的任务
    if latest_report and "payload" in latest_report:
        try:
            payload = json.loads(latest_report["payload"]) if isinstance(latest_report["payload"], str) else latest_report["payload"]
            tasks_info = payload.get("tasks", [])
        except:
            pass
    
    # 生成成员状态 - 优先使用成员汇报
    member_status = []
    for member_id, member_info in TEAM_MEMBERS.items():
        # 从成员汇报中获取最新状态
        reports = member_reports.get(member_id.lower(), [])
        latest_report_for_member = reports[0] if reports else None
        
        if latest_report_for_member:
            req_id = latest_report_for_member.get("requirement_id", 0)
            req_title = requirement_map.get(req_id, f"REQ-{req_id}") if req_id else "无"
            member_status.append({
                "member": f"{member_info['emoji']} {member_id}",
                "role": member_info["role"],
                "requirement": req_title[:25] if req_title else "无",
                "current_task": latest_report_for_member.get("task_title", "无"),
                "status": latest_report_for_member.get("status", "unknown"),
                "progress": latest_report_for_member.get("progress_percent", 0),
                "remaining": latest_report_for_member.get("estimated_remaining_minutes", "未知"),
            })
        else:
            member_status.append({
                "member": f"{member_info['emoji']} {member_id}",
                "role": member_info["role"],
                "requirement": "无",
                "current_task": "待分配",
                "status": "waiting",
                "progress": 0,
                "remaining": "N/A",
            })
    
    # 生成任务概览
    task_overview = []
    for req in team_reqs:
        status_emoji = "✅" if req.get("step") == "done" else "🔄"
        task_overview.append({
            "id": req.get("id"),
            "title": req.get("title", ""),
            "progress": req.get("progress_percent", 0),
            "step": req.get("step", ""),
            "emoji": status_emoji,
        })
    
    # 生成 Markdown 报告
    md = f"""## 🚀 {team.capitalize()} 团队状态汇报 - {report_time}

### 机器状态
- **主机名**: {machine_status.get('hostname', 'N/A')}
- **平台**: {machine_status.get('platform', 'N/A')}
- **CPU**: {machine_status.get('cpu', 'N/A')}
- **内存**: {machine_status.get('memory', 'N/A')}
- **负载**: {machine_status.get('load', 'N/A')}

### 团队成员状态
| 成员 | 角色 | 需求 | 当前任务 | 状态 | 进度 | 预计剩余 |
|------|------|------|----------|------|------|----------|
"""
    for m in member_status:
        status_display = m["status"]
        if status_display == "completed":
            status_display = "✅ 完成"
        elif status_display == "in_progress":
            status_display = "🔄 进行中"
        elif status_display == "waiting":
            status_display = "⏳ 待分配"
        else:
            status_display = "❓ 未知"
        
        md += f"| {m['member']} | {m['role']} | {m['requirement']} | {m['current_task'][:20]} | {status_display} | {m['progress']}% | {m['remaining']} |\n"
    
    md += f"""
### 今日任务概览
"""
    for t in task_overview:
        md += f"- **{t['id']}** {t['title']}: {t['progress']}% - {t['step']} {t['emoji']}\n"
    
    md += f"""
### 阻塞问题
- 无

### 下一步计划
- 等待 Vanguard 分配新需求

---
*报告时间: {report_time}*
"""
    
    return md, {
        "team": team,
        "report_time": report_time,
        "machine_status": machine_status,
        "member_status": member_status,
        "task_overview": task_overview,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", default="newton", help="Team name")
    parser.add_argument("--api-base", default=API_BASE, help="Smart Factory API base URL")
    parser.add_argument("--reporter", default="newton-cron", help="Reporter name")
    args = parser.parse_args()
    
    base = args.api_base.rstrip("/")
    team = args.team
    
    # 获取机器状态
    machine_status = get_machine_status()
    
    # 获取需求
    requirements = get_requirements(base, team)
    
    # 获取最新状态报告
    reports = get_team_status_reports(base, team)
    latest_report = reports[0] if reports else None
    
    # 获取成员任务汇报
    task_details = get_task_details(base, team)
    
    # 生成报告
    content, summary = generate_markdown_report(team, machine_status, requirements, latest_report, task_details)
    
    # 上报
    try:
        r = requests.post(f"{base}/teams/{team}/status-report", json={
            "content": content,
            "payload": json.dumps(summary),
            "reporter_agent": args.reporter,
        }, timeout=10)
        
        if r.status_code == 200:
            print(f"Reported status for {team}")
            print(content)
        else:
            print(f"Failed: {r.text}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Failed to report: {e}", file=sys.stderr)
        # 打印报告供调试
        print(content)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
