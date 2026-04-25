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
