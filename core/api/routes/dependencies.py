"""
Dependency Routes - 依赖关系管理 API
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database.services import (
    add_dependency,
    get_dependencies,
    delete_dependency,
    detect_priority_inversion
)

dependencies_bp = Blueprint('dependencies', __name__)

DATABASE = os.environ.get('SMART_FACTORY_DB') or '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    return dict(row) if row else None


@dependencies_bp.route('/api/dependencies', methods=['GET'])
def list_dependencies():
    """List all dependencies, optionally filtered by item"""
    item_type = request.args.get('item_type')
    item_id = request.args.get('item_id', type=int)
    
    deps = get_dependencies(item_type, item_id)
    return jsonify(deps)


@dependencies_bp.route('/api/dependencies', methods=['POST'])
def create_dependency():
    """Create a new dependency"""
    data = request.json or {}
    
    result = add_dependency(
        source_type=data.get('source_type'),
        source_id=data.get('source_id'),
        target_type=data.get('target_type'),
        target_id=data.get('target_id'),
        dep_type=data.get('dep_type'),
        agent=data.get('agent', 'api')
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 201


@dependencies_bp.route('/api/dependencies/<int:dep_id>', methods=['DELETE'])
def remove_dependency(dep_id):
    """Delete a dependency"""
    success = delete_dependency(dep_id, agent='api')
    if success:
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Dependency not found"}), 404


@dependencies_bp.route('/api/dependencies/priority-inversion', methods=['GET'])
def check_priority_inversion():
    """Check for priority inversion issues"""
    project_id = request.args.get('project_id', type=int)
    inversions = detect_priority_inversion(project_id)
    return jsonify({
        'inversions': inversions,
        'count': len(inversions)
    })


@dependencies_bp.route('/api/dependencies/cycle-check', methods=['POST'])
def check_cycle():
    """Check if adding a dependency would create a cycle"""
    data = request.json or {}
    
    from core.database.services import would_create_cycle
    
    would_cycle = would_create_cycle(
        data.get('source_type'),
        data.get('source_id'),
        data.get('target_type'),
        data.get('target_id')
    )
    
    return jsonify({
        'would_create_cycle': would_cycle
    })
