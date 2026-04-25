"""
Document Generator Service - 文档生成服务
从项目数据生成 Markdown/JSON 文档
"""

import sqlite3
import json
from datetime import datetime

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


def generate_project_document(
    project_id: int = None,
    project_code: str = None,
    format: str = 'markdown'
) -> str:
    """
    生成项目文档
    
    Args:
        project_id: 项目ID
        project_code: 项目编码
        format: 输出格式 (markdown, json)
    
    Returns:
        项目文档字符串
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取项目
    if project_id:
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    elif project_code:
        cursor.execute('SELECT * FROM projects WHERE code = ?', (project_code,))
    else:
        conn.close()
        return '{"error": "project_id or project_code required"}'
    
    project = cursor.fetchone()
    if not project:
        conn.close()
        return json.dumps({'error': 'Project not found'})
    
    project = dict(project)
    
    # 获取需求
    cursor.execute('''
        SELECT * FROM requirements WHERE project_id = ?
        ORDER BY priority DESC, id
    ''', (project['id'],))
    requirements = [dict(r) for r in cursor.fetchall()]
    
    # 获取特性
    for req in requirements:
        cursor.execute('''
            SELECT * FROM origin_features WHERE requirement_id = ?
            ORDER BY priority DESC, id
        ''', (req['id'],))
        req['features'] = [dict(f) for f in cursor.fetchall()]
        
        # 获取测试用例
        for feat in req['features']:
            cursor.execute('''
                SELECT * FROM origin_test_cases WHERE feature_id = ?
                ORDER BY priority DESC, id
            ''', (feat['id'],))
            feat['test_cases'] = [dict(tc) for tc in cursor.fetchall()]
    
    conn.close()
    
    if format == 'json':
        return json.dumps({
            'project': project,
            'requirements': requirements,
            'generated_at': datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)
    
    # Markdown 格式
    return generate_markdown_doc(project, requirements)


def generate_markdown_doc(project: dict, requirements: list) -> str:
    """生成 Markdown 文档"""
    lines = [
        f"# {project['name']}",
        '',
        f"**编码:** {project['code']}",
        f"**状态:** {project['status']}",
        f"**描述:** {project.get('desc_alias', '-')}",
        '',
    ]
    
    if requirements:
        lines.append('## 需求')
        lines.append('')
        
        for i, req in enumerate(requirements, 1):
            lines.append(f"### {i}. {req['title']}")
            lines.append('')
            lines.append(f"**编码:** {req['code']}")
            lines.append(f"**优先级:** P{req['priority']}")
            lines.append(f"**状态:** {req['status']}")
            lines.append('')
            
            if req.get('description'):
                lines.append(f"{req['description']}")
                lines.append('')
            
            # 特性
            features = req.get('features', [])
            if features:
                lines.append('**特性:**')
                for j, feat in enumerate(features, 1):
                    lines.append(f"- {j}. **{feat['name']}** (代码: {feat['code']})")
                    if feat.get('tech_notes'):
                        lines.append(f"  - 技术备注: {feat['tech_notes']}")
                    
                    # 测试用例
                    test_cases = feat.get('test_cases', [])
                    if test_cases:
                        lines.append('  - **测试用例:**')
                        for tc in test_cases:
                            lines.append(f'    - TC: {tc["code"]}')
                            if tc.get('precondition'):
                                lines.append(f'      - 前置: {tc["precondition"]}')
                            if tc.get('steps'):
                                lines.append(f'      - 步骤: {tc["steps"]}')
                            if tc.get('expected_result'):
                                lines.append(f'      - 期望: {tc["expected_result"]}')
                lines.append('')
    
    lines.append('---')
    lines.append(f'\n*文档生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*\n')
    
    return '\n'.join(lines)


def generate_dependency_graph(project_id: int = None) -> dict:
    """
    生成依赖关系图数据
    
    Returns:
        节点和边的列表，用于可视化
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    nodes = []
    edges = []
    
    # 获取项目节点
    if project_id:
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    else:
        cursor.execute('SELECT * FROM projects')
    
    for row in cursor.fetchall():
        project = dict(row)
        nodes.append({
            'id': f"project_{project['id']}",
            'label': project['name'],
            'type': 'project',
            'data': project
        })
    
    # 获取需求节点和边
    req_query = 'SELECT * FROM requirements'
    if project_id:
        req_query += ' WHERE project_id = ?'
    
    cursor.execute(req_query, (project_id,) if project_id else ())
    for row in cursor.fetchall():
        req = dict(row)
        nodes.append({
            'id': f"req_{req['id']}",
            'label': req['title'],
            'type': 'requirement',
            'data': req
        })
        # 需求到项目的边
        edges.append({
            'source': f"req_{req['id']}",
            'target': f"project_{req['project_id']}",
            'type': 'belongs_to'
        })
    
    # 获取依赖边
    cursor.execute('SELECT * FROM dependencies')
    for row in cursor.fetchall():
        dep = dict(row)
        source_id = f"{dep['source_type']}_{dep['source_id']}".replace('-', '_')
        target_id = f"{dep['target_type']}_{dep['target_id']}".replace('-', '_')
        edges.append({
            'source': source_id,
            'target': target_id,
            'type': dep.get('dep_type', 'relates_to'),
            'data': dep
        })
    
    conn.close()
    
    return {
        'nodes': nodes,
        'edges': edges,
        'generated_at': datetime.now().isoformat()
    }
