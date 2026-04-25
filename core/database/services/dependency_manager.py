"""
Dependency Manager Service - 依赖关系管理
包含循环检测和优先级反转检测
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def add_dependency(
    source_type: str,
    source_id: int,
    target_type: str,
    target_id: int,
    dep_type: Optional[str] = None,
    agent: str = 'system'
) -> dict:
    """
    添加依赖关系
    
    Args:
        source_type: 来源类型 (project, requirement, feature)
        source_id: 来源ID
        target_type: 目标类型
        target_id: 目标ID
        dep_type: 依赖类型 (blocks, requires, relates_to)
        agent: 操作代理
    
    Returns:
        新创建的依赖记录
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute('''
        SELECT id FROM dependencies
        WHERE source_type = ? AND source_id = ? AND target_type = ? AND target_id = ?
    ''', (source_type, source_id, target_type, target_id))
    
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return {'id': existing[0], 'message': 'Dependency already exists'}
    
    # 检查循环依赖
    if would_create_cycle(source_type, source_id, target_type, target_id):
        conn.close()
        return {'error': 'Would create circular dependency'}
    
    # 创建依赖
    cursor.execute('''
        INSERT INTO dependencies 
        (source_type, source_id, target_type, target_id, dep_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source_type, source_id, target_type, target_id, dep_type, datetime.now().isoformat()))
    
    dep_id = cursor.lastrowid
    
    # 记录审计日志
    cursor.execute('''
        INSERT INTO audit_logs 
        (agent_name, operation, target_type, target_id, details, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        agent,
        'ADD_DEPENDENCY',
        'dependency',
        str(dep_id),
        json.dumps({
            'source': f'{source_type}:{source_id}',
            'target': f'{target_type}:{target_id}',
            'dep_type': dep_type
        }),
        'success',
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return {'id': dep_id}


def would_create_cycle(source_type: str, source_id: int, target_type: str, target_id: int) -> bool:
    """检查是否会产生循环依赖"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 检查从 target 是否能到达 source（反向检查）
    visited = set()
    queue = [(target_type, target_id)]
    
    while queue:
        current_type, current_id = queue.pop(0)
        if (current_type, current_id) in visited:
            continue
        visited.add((current_type, current_id))
        
        # 如果能直接到达 source，说明有环
        if current_type == source_type and current_id == source_id:
            conn.close()
            return True
        
        # 查找当前节点指向的所有节点
        cursor.execute('''
            SELECT target_type, target_id FROM dependencies
            WHERE source_type = ? AND source_id = ?
        ''', (current_type, current_id))
        
        for row in cursor.fetchall():
            next_type, next_id = row
            if (next_type, next_id) not in visited:
                queue.append((next_type, next_id))
    
    conn.close()
    return False


def get_dependencies(
    item_type: str = None,
    item_id: int = None
) -> list:
    """
    获取依赖关系
    
    Args:
        item_type: 过滤类型
        item_id: 过滤ID
    
    Returns:
        依赖列表
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if item_type and item_id:
        cursor.execute('''
            SELECT * FROM dependencies
            WHERE (source_type = ? AND source_id = ?)
               OR (target_type = ? AND target_id = ?)
            ORDER BY created_at DESC
        ''', (item_type, item_id, item_type, item_id))
    else:
        cursor.execute('SELECT * FROM dependencies ORDER BY created_at DESC')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_dependency(dep_id: int, agent: str = 'system') -> bool:
    """
    删除依赖关系
    
    Returns:
        是否成功删除
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM dependencies WHERE id = ?', (dep_id,))
    dep = cursor.fetchone()
    
    if not dep:
        conn.close()
        return False
    
    cursor.execute('DELETE FROM dependencies WHERE id = ?', (dep_id,))
    
    # 记录审计日志
    cursor.execute('''
        INSERT INTO audit_logs 
        (agent_name, operation, target_type, target_id, details, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        agent,
        'DELETE_DEPENDENCY',
        'dependency',
        str(dep_id),
        json.dumps({'deleted_dep': dict(dep)}),
        'success',
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    return True


def detect_priority_inversion(project_id: int = None) -> list:
    """
    检测优先级反转
    高优先级项目依赖低优先级项目时被阻塞
    
    Args:
        project_id: 项目ID，不指定则检查所有
    
    Returns:
        优先级反转列表
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    inversions = []
    
    # 获取所有依赖关系
    cursor.execute('SELECT * FROM dependencies')
    deps = cursor.fetchall()
    
    for dep in deps:
        source_type = dep['source_type']
        source_id = dep['source_id']
        target_type = dep['target_type']
        target_id = dep['target_id']
        
        # 获取源和目标的优先级
        source_priority = get_priority(cursor, source_type, source_id)
        target_priority = get_priority(cursor, target_type, target_id)
        
        # 如果源优先级更高但依赖低优先级项，记录为反转
        if source_priority > 0 and target_priority > 0 and source_priority > target_priority:
            inversions.append({
                'source_type': source_type,
                'source_id': source_id,
                'source_priority': source_priority,
                'target_type': target_type,
                'target_id': target_id,
                'target_priority': target_priority,
                'inversion_level': source_priority - target_priority,
                'dep_type': dep['dep_type']
            })
    
    conn.close()
    return inversions


def get_priority(cursor, entity_type: str, entity_id: int) -> int:
    """获取实体的优先级"""
    table_map = {
        'requirement': 'requirements',
        'feature': 'origin_features',
        'test_case': 'origin_test_cases'
    }
    
    table = table_map.get(entity_type)
    if not table:
        return 0
    
    try:
        cursor.execute(f'SELECT priority FROM {table} WHERE id = ?', (entity_id,))
        result = cursor.fetchone()
        return result['priority'] if result else 0
    except:
        return 0
