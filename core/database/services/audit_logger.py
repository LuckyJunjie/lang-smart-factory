"""
Audit Logger Service - 审计日志服务
记录所有项目操作
"""

import sqlite3
import json
from datetime import datetime

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def log_audit(
    agent_name: str,
    operation: str,
    target_type: str = None,
    target_id: str = None,
    details: dict = None,
    status: str = 'success'
) -> int:
    """
    记录审计日志
    
    Args:
        agent_name: 操作代理名称
        operation: 操作类型 (CREATE_PROJECT, UPDATE_REQUIREMENT, etc.)
        target_type: 目标类型 (project, requirement, feature, etc.)
        target_id: 目标ID
        details: 详细信息字典
        status: 操作状态 (success, failure)
    
    Returns:
        审计日志ID
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    details_json = json.dumps(details) if details else None
    
    cursor.execute('''
        INSERT INTO audit_logs 
        (agent_name, operation, target_type, target_id, details, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        agent_name,
        operation,
        target_type,
        target_id,
        details_json,
        status,
        datetime.now().isoformat()
    ))
    
    audit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return audit_id


def get_audit_logs(
    limit: int = 100,
    agent_name: str = None,
    operation: str = None,
    target_type: str = None
) -> list:
    """
    获取审计日志
    
    Args:
        limit: 返回数量限制
        agent_name: 过滤代理名称
        operation: 过滤操作类型
        target_type: 过滤目标类型
    
    Returns:
        审计日志列表
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM audit_logs WHERE 1=1'
    params = []
    
    if agent_name:
        query += ' AND agent_name = ?'
        params.append(agent_name)
    
    if operation:
        query += ' AND operation = ?'
        params.append(operation)
    
    if target_type:
        query += ' AND target_type = ?'
        params.append(target_type)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
