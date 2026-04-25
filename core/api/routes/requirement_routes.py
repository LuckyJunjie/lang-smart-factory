"""
Requirement Routes - Origin 功能合并到 Smart Factory
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import datetime

requirement_bp = Blueprint('requirements', __name__)

DATABASE = os.environ.get('SMART_FACTORY_DB') or '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    return dict(row) if row else None


@requirement_bp.route('/api/requirements', methods=['GET'])
def list_requirements():
    """List all requirements, optionally filtered by project_id"""
    project_id = request.args.get('project_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if project_id:
        cursor.execute(
            "SELECT * FROM requirements WHERE project_id = ? ORDER BY id", 
            (project_id,)
        )
    else:
        cursor.execute("SELECT * FROM requirements ORDER BY id")
    
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict_from_row(r) for r in rows])


@requirement_bp.route('/api/requirements', methods=['POST'])
def create_requirement():
    """Create a new requirement"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate code
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM requirements")
    next_id = cursor.fetchone()['next_id']
    code = f"REQ-{next_id:04d}"
    
    try:
        cursor.execute(
            """INSERT INTO requirements 
               (project_id, code, title, description, priority, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.get('project_id'), code, data.get('title'), data.get('description', ''),
             data.get('priority', 0), data.get('status', 'active'),
             datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat())
        )
        conn.commit()
        req_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": req_id, "code": code}), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400


@requirement_bp.route('/api/requirements/<int:rid>', methods=['GET'])
def get_requirement(rid):
    """Get requirement by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requirements WHERE id = ?", (rid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict_from_row(row))
    return jsonify({"error": "Requirement not found"}), 404


@requirement_bp.route('/api/requirements/<int:rid>', methods=['PATCH'])
def update_requirement(rid):
    """Update requirement"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key in ['title', 'description', 'priority', 'status', 'project_id']:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    
    if fields:
        fields.append("updated_at = ?")
        values.append(datetime.datetime.now().isoformat())
        values.append(rid)
        cursor.execute(f"UPDATE requirements SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    
    conn.close()
    return jsonify({"status": "updated"})


@requirement_bp.route('/api/requirements/<int:rid>', methods=['DELETE'])
def delete_requirement(rid):
    """Delete requirement"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requirements WHERE id = ?", (rid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})
