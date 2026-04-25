#!/usr/bin/env python3
"""
Smart Factory OpenClaw Skill (DEPRECATED – use project_mcp tools instead)
需求管理、项目管理、资源监控

Prefer: project_mcp tools (list_requirements, get_requirement, create_requirement, etc.)
and SMART_FACTORY_API. This CLI remains for ad-hoc scripts; agents should use MCP.
"""

import json
import sys
import os
import requests
from datetime import datetime

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")

def list_projects():
    resp = requests.get(f"{API_BASE}/projects")
    return resp.json()

def get_project(pid):
    resp = requests.get(f"{API_BASE}/projects/{pid}")
    return resp.json()

def list_requirements(status=None, priority=None):
    params = {}
    if status: params['status'] = status
    if priority: params['priority'] = priority
    resp = requests.get(f"{API_BASE}/requirements", params=params)
    return resp.json()

def create_requirement(project_id, title, description="", priority="P2", req_type="feature"):
    resp = requests.post(f"{API_BASE}/requirements", json={
        "project_id": project_id,
        "title": title,
        "description": description,
        "priority": priority,
        "type": req_type
    })
    return resp.json()

def update_requirement(rid, **kwargs):
    resp = requests.patch(f"{API_BASE}/requirements/{rid}", json=kwargs)
    return resp.json()

def take_requirement(rid, assigned_team, assigned_agent):
    """Team takes a requirement: POST /api/requirements/<id>/take"""
    resp = requests.post(f"{API_BASE}/requirements/{rid}/take", json={
        "assigned_team": assigned_team,
        "assigned_agent": assigned_agent
    })
    return resp.json()

def list_tasks(req_id=None):
    if req_id:
        resp = requests.get(f"{API_BASE}/requirements/{req_id}/tasks")
    else:
        resp = requests.get(f"{API_BASE}/tasks")
    return resp.json()

def create_task(req_id, title, description="", executor=""):
    resp = requests.post(f"{API_BASE}/tasks", json={
        "req_id": req_id,
        "title": title,
        "description": description,
        "executor": executor
    })
    return resp.json()

def update_task(tid, **kwargs):
    resp = requests.patch(f"{API_BASE}/tasks/{tid}", json=kwargs)
    return resp.json()

def list_machines():
    resp = requests.get(f"{API_BASE}/machines")
    return resp.json()

def check_machine_status(ip, port=18789):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def refresh_machine_status():
    machines = list_machines()
    results = []
    for m in machines:
        online = check_machine_status(m['ip'], m.get('port', 18789))
        status = "online" if online else "offline"
        results.append({"name": m['name'], "ip": m['ip'], "status": status})
    return results

def list_tools(tool_type=None):
    params = {}
    if tool_type: params['type'] = tool_type
    resp = requests.get(f"{API_BASE}/tools", params=params)
    return resp.json()

def dashboard_stats():
    resp = requests.get(f"{API_BASE}/dashboard/stats")
    return resp.json()

# CLI interface
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "projects":
        print(json.dumps(list_projects(), indent=2, ensure_ascii=False))
    
    elif cmd == "requirements":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(list_requirements(status=status), indent=2, ensure_ascii=False))
    
    elif cmd == "machines":
        print(json.dumps(refresh_machine_status(), indent=2, ensure_ascii=False))
    
    elif cmd == "stats":
        print(json.dumps(dashboard_stats(), indent=2, ensure_ascii=False))
    
    elif cmd == "create-req":
        # usage: create-req <project_id> <title> [priority]
        pid = sys.argv[2]
        title = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else "P2"
        print(json.dumps(create_requirement(pid, title, priority=priority), indent=2))
    
    else:
        print("""
Smart Factory CLI
Usage:
  projects                    - List all projects
  requirements [status]       - List requirements (optional: status filter)
  machines                    - Check machine status
  stats                       - Dashboard statistics
  create-req <pid> <title>   - Create requirement
        """)
