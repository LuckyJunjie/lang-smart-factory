"""
Smart Factory MCP Server
Model Context Protocol server for external agents
"""

import json
import sqlite3
import os
import sys
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database.services import (
    generate_code,
    log_audit,
    add_dependency,
    get_dependencies,
    generate_project_document,
)

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'


class SmartFactoryMCPServer:
    """MCP Server for Smart Factory operations"""
    
    def __init__(self):
        self.tools = {
            'create_project': self.tool_create_project,
            'get_projects': self.tool_get_projects,
            'create_requirement': self.tool_create_requirement,
            'get_requirements': self.tool_get_requirements,
            'add_dependency': self.tool_add_dependency,
            'get_dependencies': self.tool_get_dependencies,
            'get_project_document': self.tool_get_project_document,
            'search': self.tool_search,
        }
    
    def handle(self, tool_name: str, arguments: dict) -> dict:
        """Handle MCP tool call"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = self.tools[tool_name](**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    # ========== Project Tools ==========
    
    def tool_create_project(self, name: str, desc_alias: str = None, repo_url: str = None, agent: str = 'MCP') -> dict:
        """Create a new project"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        code = generate_code('project')
        
        cursor.execute('''
            INSERT INTO projects (code, name, desc_alias, status, repo_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (code, name, desc_alias or '', 'active', repo_url or ''))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        log_audit(
            agent_name=agent,
            operation='CREATE_PROJECT',
            target_type='project',
            target_id=str(project_id),
            details={'Name': name, 'code': code}
        )
        
        return {
            "id": project_id,
            "code": code,
            "name": name,
            "status": "active"
        }
    
    def tool_get_projects(self, status: str = None) -> dict:
        """Get all projects"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM projects WHERE status = ?', (status,))
        else:
            cursor.execute('SELECT * FROM projects')
        
        projects = [dict(r) for r in cursor.fetchall()]
        conn.close()
        
        return {"projects": projects, "count": len(projects)}
    
    # ========== Requirement Tools ==========
    
    def tool_create_requirement(
        self,
        project_id: int,
        title: str,
        description: str = None,
        priority: int = 1,
        agent: str = 'MCP'
    ) -> dict:
        """Create a new requirement"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        code = generate_code('requirement')
        
        cursor.execute('''
            INSERT INTO requirements 
            (project_id, code, title, description, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (project_id, code, title, description or '', priority, 'active'))
        
        req_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        log_audit(
            agent_name=agent,
            operation='CREATE_REQUIREMENT',
            target_type='requirement',
            target_id=str(req_id),
            details={'Title': title, 'code': code, 'project_id': project_id}
        )
        
        return {
            "id": req_id,
            "code": code,
            "title": title,
            "priority": priority,
            "status": "active"
        }
    
    def tool_get_requirements(self, project_id: int = None, status: str = None) -> dict:
        """Get requirements"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM requirements WHERE 1=1'
        params = []
        
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        requirements = [dict(r) for r in cursor.fetchall()]
        conn.close()
        
        return {"requirements": requirements, "count": len(requirements)}
    
    # ========== Dependency Tools ==========
    
    def tool_add_dependency(
        self,
        source_type: str,
        source_id: int,
        target_type: str,
        target_id: int,
        dep_type: str = 'relates_to',
        agent: str = 'MCP'
    ) -> dict:
        """Add a dependency"""
        result = add_dependency(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            dep_type=dep_type,
            agent=agent
        )
        
        if 'error' in result:
            return {"error": result['error']}
        
        return {"dependency": result, "status": "created"}
    
    def tool_get_dependencies(self, item_type: str = None, item_id: int = None) -> dict:
        """Get dependencies"""
        deps = get_dependencies(item_type, item_id)
        return {"dependencies": deps, "count": len(deps)}
    
    # ========== Document Tools ==========
    
    def tool_get_project_document(self, project_id: int, format: str = 'markdown') -> dict:
        """Get project as document"""
        doc = generate_project_document(project_id=project_id, format=format)
        
        if doc.startswith('{'):
            return json.loads(doc)
        
        return {"document": doc, "format": format}
    
    # ========== Search Tools ==========
    
    def tool_search(self, query: str, type: str = None) -> dict:
        """Search across all entities"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = []
        
        # Search projects
        if not type or type == 'project':
            cursor.execute(
                "SELECT *, 'project' as entity_type FROM projects WHERE name LIKE ? OR code LIKE ?",
                (f'%{query}%', f'%{query}%')
            )
            for r in cursor.fetchall():
                results.append({**dict(r), 'entity_type': 'project'})
        
        # Search requirements
        if not type or type == 'requirement':
            cursor.execute(
                "SELECT *, 'requirement' as entity_type FROM requirements WHERE title LIKE ? OR code LIKE ?",
                (f'%{query}%', f'%{query}%')
            )
            for r in cursor.fetchall():
                results.append({**dict(r), 'entity_type': 'requirement'})
        
        conn.close()
        
        return {"results": results, "count": len(results), "query": query}


# Flask MCP API routes
def create_mcp_routes():
    """Create Flask routes for MCP endpoints"""
    from flask import Blueprint, request, jsonify
    
    mcp_bp = Blueprint('mcp', __name__)
    server = SmartFactoryMCPServer()
    
    @mcp_bp.route('/api/mcp/tools', methods=['GET'])
    def list_tools():
        """List available MCP tools"""
        return jsonify({
            "tools": list(server.tools.keys()),
            "server": "Smart Factory MCP"
        })
    
    @mcp_bp.route('/api/mcp/call', methods=['POST'])
    def call_tool():
        """Call an MCP tool"""
        data = request.json or {}
        tool = data.get('tool')
        arguments = data.get('arguments', {})
        
        result = server.handle(tool, arguments)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    @mcp_bp.route('/api/mcp/project/create', methods=['POST'])
    def mcp_create_project():
        """MCP: Create project"""
        data = request.json or {}
        result = server.tool_create_project(
            name=data.get('name'),
            desc_alias=data.get('desc_alias'),
            repo_url=data.get('repo_url'),
            agent=data.get('agent', 'MCP')
        )
        return jsonify(result)
    
    @mcp_bp.route('/api/mcp/requirement/create', methods=['POST'])
    def mcp_create_requirement():
        """MCP: Create requirement"""
        data = request.json or {}
        result = server.tool_create_requirement(
            project_id=data.get('project_id'),
            title=data.get('title'),
            description=data.get('description'),
            priority=data.get('priority', 1),
            agent=data.get('agent', 'MCP')
        )
        return jsonify(result)
    
    @mcp_bp.route('/api/mcp/dependency/add', methods=['POST'])
    def mcp_add_dependency():
        """MCP: Add dependency"""
        data = request.json or {}
        result = server.tool_add_dependency(
            source_type=data.get('source_type'),
            source_id=data.get('source_id'),
            target_type=data.get('target_type'),
            target_id=data.get('target_id'),
            dep_type=data.get('dep_type'),
            agent=data.get('agent', 'MCP')
        )
        return jsonify(result)
    
    return mcp_bp
