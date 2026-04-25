"""
Project Routes - 使用服务层的项目 CRUD
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import sys

# 添加 services 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database.services import generate_code, log_audit, generate_project_document

project_bp = Blueprint('projects', __name__)

DATABASE = os.environ.get('SMART_FACTORY_DB') or '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    return dict(row) if row else None


@project_bp.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict_from_row(r) for r in rows])


@project_bp.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project with auto-generated code"""
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    
    # 使用 ID Generator 服务生成编码
    code = generate_code('project')
    
    try:
        cursor.execute(
            """INSERT INTO projects (code, name, desc_alias, status, repo_url, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
            (code, data.get('name'), data.get('desc_alias', ''), 
             data.get('status', 'active'), data.get('repo_url', '')))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 记录审计日志
        log_audit(
            agent_name='api',
            operation='CREATE_PROJECT',
            target_type='project',
            target_id=str(project_id),
            details={'name': data.get('name'), 'code': code}
        )
        
        return jsonify({"id": project_id, "code": code}), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400


@project_bp.route('/api/projects/<int:pid>', methods=['GET'])
def get_project(pid):
    """Get project by ID with full details"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (pid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict_from_row(row))
    return jsonify({"error": "Project not found"}), 404


@project_bp.route('/api/projects/<int:pid>', methods=['PATCH'])
def update_project(pid):
    """Update project"""
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key in ['name', 'desc_alias', 'status', 'repo_url']:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    
    if fields:
        fields.append("updated_at = datetime('now')")
        values.append(pid)
        cursor.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        
        # 记录审计日志
        log_audit(
            agent_name='api',
            operation='UPDATE_PROJECT',
            target_type='project',
            target_id=str(pid),
            details=data
        )
    
    conn.close()
    return jsonify({"status": "updated"})


@project_bp.route('/api/projects/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    """Delete project"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    
    log_audit(
        agent_name='api',
        operation='DELETE_PROJECT',
        target_type='project',
        target_id=str(pid)
    )
    return jsonify({"status": "deleted"})


@project_bp.route('/api/projects/<int:pid>/document', methods=['GET'])
def get_project_document(pid):
    """Get project as document (Markdown or JSON)"""
    fmt = request.args.get('format', 'markdown')
    doc = generate_project_document(project_id=pid, format=fmt)
    return doc, 200, {'Content-Type': 'text/plain; charset=utf-8'}
