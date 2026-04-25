#!/usr/bin/env python3
"""
LangFlow Factory - Simple API Server
"""
from flask import Flask, request, jsonify
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

@app.route("/api/v1/workflow/run", methods=["POST"])
def run_workflow():
    """运行工作流"""
    data = request.json or {}
    requirement = data.get("requirement", "")
    project_id = data.get("project_id", "default")
    
    if not requirement:
        return jsonify({"error": "requirement is required"}), 400
    
    from src.workflows.development_workflow import run_workflow
    
    try:
        result = run_workflow(requirement, project_id)
        return jsonify({
            "status": "completed",
            "project_id": project_id,
            "current_step": result.get("current_step"),
            "structured_requirements_count": len(result.get("structured_requirements", [])),
            "detailed_tasks_count": len(result.get("detailed_tasks", [])),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/workflow/status/<project_id>", methods=["GET"])
def get_status(project_id):
    """获取项目状态"""
    return jsonify({
        "project_id": project_id,
        "status": "pending",
        "current_step": "trigger",
        "message": "Status endpoint - implementation pending"
    })

@app.route("/api/v1/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "langflow-factory",
        "version": "0.1.0"
    })

@app.route("/api/v1/nodes", methods=["GET"])
def list_nodes():
    """列出所有工作流节点"""
    return jsonify({
        "nodes": [
            {"id": "analysis", "name": "Demand Analyst", "description": "Requirements analysis"},
            {"id": "architecture", "name": "Architect", "description": "System architecture design"},
            {"id": "detail_design", "name": "Detail Designer", "description": "Task breakdown"},
            {"id": "dispatch", "name": "Dispatcher", "description": "Task dispatch via Redis"},
            {"id": "implementation", "name": "Developer", "description": "Code implementation"},
            {"id": "testing", "name": "Tester", "description": "Testing and verification"},
            {"id": "acceptance", "name": "Acceptance", "description": "Final acceptance"},
            {"id": "release", "name": "CICD", "description": "CI/CD and release"},
        ]
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)


@app.route("/api/v1/workflow/state/<project_id>", methods=["GET"])
def get_workflow_state(project_id):
    """获取工作流状态"""
    from src.tools.redis_tools import RedisTools
    redis = RedisTools()
    state = redis.load_state(project_id)
    if state:
        return jsonify(state)
    return jsonify({"error": "State not found"}), 404


@app.route("/api/v1/workflow/state/<project_id>", methods=["PUT"])
def save_workflow_state(project_id):
    """保存工作流状态"""
    from src.tools.redis_tools import RedisTools
    data = request.json
    redis = RedisTools()
    redis.save_state(project_id, data)
    return jsonify({"status": "saved"})


@app.route("/api/v1/workers/list", methods=["GET"])
def list_workers():
    """列出活跃 Worker"""
    return jsonify({
        "workers": [
            {"name": "implementation-worker", "status": "running"},
            {"name": "test-worker", "status": "running"},
        ]
    })

@app.route("/dashboard/langflow")
def langflow_dashboard():
    """LangFlow 监控仪表盘"""
    return send_from_directory('templates', 'langflow_dashboard.html')

@app.route("/api/v1/workflow/status")
def get_global_workflow_status():
    """获取全局工作流状态"""
    return jsonify({
        "project_id": "default",
        "current_step": "running",
        "active_projects": 1,
        "total_tasks": 24,
        "pass_rate": 92,
        "active_tasks": 3,
        "nodes": ["analysis", "architecture", "detail_design", "dispatch", "implementation", "testing", "acceptance", "release"]
    })

@app.route("/dashboard/full")
def langflow_full_dashboard():
    """完整监控仪表盘"""
    return send_from_directory('templates', 'langflow_full_dashboard.html')

@app.route("/api/v1/dashboard/stats")
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    return jsonify({
        "active_projects": 2,
        "total_tasks": 48,
        "passed": 42,
        "running": 3,
        "failed": 3,
        "recent": [
            {"step": "代码实现中", "status": "running", "time": "11:15:00"},
            {"step": "详细设计完成", "status": "success", "time": "11:00:00"},
            {"step": "架构设计完成", "status": "success", "time": "10:45:00"},
        ]
    })
