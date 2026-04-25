#!/usr/bin/env python3
"""
Smart Factory API - 智慧工厂 REST API
需求管理、项目管理、资源监控
"""

from flask import Flask, request, jsonify, g, send_from_directory
from werkzeug.exceptions import HTTPException
import sqlite3
import os
import datetime
import time
import io
import tempfile
from functools import wraps

# Human-readable dashboard: serve static from api/static (absolute path so it works from any cwd)
_STATIC = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
app = Flask(__name__, static_folder=_STATIC, static_url_path='/static')


@app.route('/')
def dashboard_index():
    """Serve human-readable dashboard (same data as API, table/GUI view)."""
    return app.send_static_file('index.html')


@app.errorhandler(Exception)
def handle_exception(e):
    """Ensure all errors return JSON (not empty/HTML)"""
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description or str(e)}), e.code
    return jsonify({"error": str(e), "type": type(e).__name__}), 500


# This server and the DB are intended to run only on Vanguard001 (192.168.3.75). Other nodes do not run the API; they call http://192.168.3.75:5000/api.
# Database path: env SMART_FACTORY_DB overrides; else core/db/factory.db (same as seed script).
_api_dir = os.path.dirname(os.path.abspath(__file__))
_CORE_ROOT = os.path.dirname(_api_dir)
_REPO_ROOT = os.path.dirname(_CORE_ROOT)
_default_db = os.path.join(_CORE_ROOT, 'db', 'factory.db')
DATABASE = os.environ.get('SMART_FACTORY_DB') or _default_db

# Feishu API log database
FEISHU_LOG_DB = os.path.join(_CORE_ROOT, 'db', 'feishu_api_log.db')

# Team status report: report period 30 min; team considered active only if last report within this many minutes
STATUS_REPORT_ACTIVE_MINUTES = 40
REPORT_PERIOD_MINUTES = 30

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = dict_factory
    return g.db

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _slug(name):
    """Normalize to lowercase slug (alphanumeric and hyphens)."""
    if not name:
        return "unknown"
    s = (name or "").lower().replace(" ", "-")
    return "".join(c if c.isalnum() or c == "-" else "" for c in s).strip("-") or "unknown"


def _slug_words(title, max_words=10, max_len=72):
    """First `max_words` words from title → lowercase alphanumeric tokens joined by '-'; cap length."""
    if not title:
        return "n-a"
    words = str(title).strip().split()
    if not words:
        return "n-a"
    parts = []
    for w in words[:max_words]:
        token = "".join(c for c in w if c.isalnum())
        if not token:
            continue
        parts.append(token.lower())
    if not parts:
        return "n-a"
    s = "-".join(parts)
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "n-a"


def project_code_segment(project_id, project_name):
    """P<id>-<≤6 words from project name>. See docs/REQUIREMENTS.md §2.0."""
    return f"P{int(project_id)}-{_slug_words(project_name, 6)}"


def requirement_code_segment(requirement_id, requirement_title):
    """REQ<id>-<≤10 words from requirement title>."""
    return f"REQ{int(requirement_id)}-{_slug_words(requirement_title, 10)}"


def task_code_segment(task_id, task_title):
    """TASK<id>-<≤10 words from task title>."""
    return f"TASK{int(task_id)}-{_slug_words(task_title, 10)}"


def test_case_code_segment(test_case_id, test_case_title):
    """TC<id>-<≤10 words from test case title>."""
    return f"TC{int(test_case_id)}-{_slug_words(test_case_title, 10)}"


def requirement_code(project_id, project_name, requirement_id, requirement_title):
    """Full hierarchical code for a requirement: P…-REQ… (no task/test case segment)."""
    return f"{project_code_segment(project_id, project_name)}-{requirement_code_segment(requirement_id, requirement_title)}"


def task_code(project_id, project_name, requirement_id, requirement_title, task_id, task_title):
    """Full hierarchical code for a task: P…-REQ…-TASK…"""
    return f"{requirement_code(project_id, project_name, requirement_id, requirement_title)}-{task_code_segment(task_id, task_title)}"


def test_case_code(project_id, project_name, requirement_id, requirement_title, task_id, task_title, tc_id, tc_title):
    """Full chain P…-REQ…-TASK…-TC… (TASK omitted if test case has no linked task)."""
    base = requirement_code(project_id, project_name, requirement_id, requirement_title)
    if task_id:
        base = f"{base}-{task_code_segment(task_id, task_title)}"
    return f"{base}-{test_case_code_segment(tc_id, tc_title)}"


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ============ API Discovery (for OpenClaw / clients) ============

@app.route('/api/', methods=['GET'])
@app.route('/api', methods=['GET'])
def api_index():
    """List all available API endpoints. OpenClaw can use this to discover routes."""
    routes = [
        {"method": "GET", "path": "/api/", "desc": "API index (this)"},
        {"method": "GET", "path": "/api/projects", "desc": "List projects"},
        {"method": "POST", "path": "/api/projects", "desc": "Create project"},
        {"method": "GET", "path": "/api/projects/<pid>", "desc": "Get project"},
        {"method": "GET", "path": "/api/projects/<pid>/requirements", "desc": "List project requirements"},
        {"method": "GET", "path": "/api/requirements", "desc": "List requirements (?status=, ?assigned_team=)"},
        {"method": "POST", "path": "/api/requirements", "desc": "Create requirement"},
        {"method": "GET", "path": "/api/requirements/<rid>", "desc": "Get requirement"},
        {"method": "PATCH", "path": "/api/requirements/<rid>", "desc": "Update requirement"},
        {"method": "POST", "path": "/api/requirements/<rid>/take", "desc": "Take requirement (assigned_team, assigned_agent)"},
        {"method": "POST", "path": "/api/requirements/<rid>/assign", "desc": "Assign requirement to team (assigned_team)"},
        {"method": "POST", "path": "/api/requirements/<rid>/auto-split", "desc": "Auto-split requirement into tasks"},
        {"method": "GET", "path": "/api/requirements/<rid>/tasks", "desc": "List tasks of requirement"},
        {"method": "POST", "path": "/api/tasks", "desc": "Create task (req_id, title, executor)"},
        {"method": "GET", "path": "/api/tasks/<tid>", "desc": "Get single task (includes next_step_task_id, risk, blocker)"},
        {"method": "PATCH", "path": "/api/tasks/<tid>", "desc": "Update task (status, executor, next_step_task_id, risk, blocker, est_tokens_total, prompt_rounds)"},
        {"method": "GET", "path": "/api/machines", "desc": "List machines"},
        {"method": "POST", "path": "/api/machines/<mid>/status", "desc": "Update machine status"},
        {"method": "GET", "path": "/api/teams/online", "desc": "List online teams"},
        {"method": "GET", "path": "/api/teams/assigned-requirements", "desc": "List requirements assigned to team. Requires ?team=jarvis"},
        {"method": "GET", "path": "/api/teams/<team>/assigned-requirements", "desc": "Same, team in path. Example: /api/teams/jarvis/assigned-requirements"},
        {"method": "POST", "path": "/api/teams/<team>/machine-status", "desc": "Report machine status"},
        {"method": "GET", "path": "/api/teams/<team>/machine-status", "desc": "Get team machine status"},
        {"method": "GET", "path": "/api/teams/machine-status/summary", "desc": "Summary of all teams machine status"},
        {"method": "POST", "path": "/api/teams/<team>/status-report", "desc": "Report team status (payload)"},
        {"method": "GET", "path": "/api/teams/<team>/status-report", "desc": "Get team status report"},
        {"method": "GET", "path": "/api/teams/status-report/summary", "desc": "Summary of all teams status"},
        {"method": "POST", "path": "/api/teams/<team>/task-detail", "desc": "Report task dev detail (analysis/assignment/development)"},
        {"method": "GET", "path": "/api/teams/<team>/task-details", "desc": "List task details for team (?requirement_id=)"},
        {"method": "POST", "path": "/api/teams/<team>/report", "desc": "Submit development or test task report (report_type, requirement_id, content)"},
        {"method": "GET", "path": "/api/teams/<team>/reports", "desc": "List team reports (?requirement_id=, ?report_type=)"},
        {"method": "GET", "path": "/api/teams/development-details/summary", "desc": "Summary of all teams dev details (for final report)"},
        {"method": "POST", "path": "/api/work-log", "desc": "Append work log (role_or_team, task_name, task_output, next_step)"},
        {"method": "GET", "path": "/api/work-logs", "desc": "List work logs (?role_or_team=, ?since=)"},
        {"method": "GET", "path": "/api/dashboard/stats", "desc": "Dashboard stats"},
        {"method": "GET", "path": "/api/dashboard/risk-report", "desc": "Risk report"},
        {"method": "POST", "path": "/api/discussion/blockage", "desc": "Report blockage (team, requirement_id, reason)"},
        {"method": "GET", "path": "/api/discussion/blockages", "desc": "List blockages (?status=pending)"},
        {"method": "PATCH", "path": "/api/discussion/blockage/<id>", "desc": "Hera resolve blockage (status, decision)"},
        {"method": "POST", "path": "/api/meetings", "desc": "Create meeting (topic/problem + participants)"},
        {"method": "GET", "path": "/api/meetings/for-agent", "desc": "List running meetings for an agent (?agent=<id>)"},
        {"method": "GET", "path": "/api/meetings/<id>", "desc": "Get meeting theme/details"},
        {"method": "POST", "path": "/api/meetings/<id>/inputs", "desc": "Submit meeting analysis/comments"},
        {"method": "GET", "path": "/api/meetings/<id>/inputs", "desc": "Read meeting inputs (other agents)"},
        {"method": "POST", "path": "/api/meetings/<id>/finalize", "desc": "Host finalizes meeting; creates/assigns requirements"},
        {"method": "POST", "path": "/api/feishu/post", "desc": "Post to Feishu"},
        {"method": "POST", "path": "/api/voice", "desc": "语音转文字 (Voice to Text) - 接收音频文件，返回转录文字"},
        {"method": "PATCH", "path": "/api/projects/<pid>", "desc": "Update project (metadata fields)"},
        {"method": "DELETE", "path": "/api/projects/<pid>", "desc": "Delete project (only if no requirements)"},
        {"method": "GET", "path": "/api/requirements/<rid>/test-cases", "desc": "List test cases for requirement"},
        {"method": "POST", "path": "/api/requirements/<rid>/test-cases", "desc": "Create test case"},
        {"method": "GET", "path": "/api/test-cases/<tcid>", "desc": "Get test case"},
        {"method": "PATCH", "path": "/api/test-cases/<tcid>", "desc": "Update test case"},
        {"method": "DELETE", "path": "/api/test-cases/<tcid>", "desc": "Delete test case"},
    ]
    # Clients (all nodes) use Vanguard001; base in response points there.
    return jsonify({"endpoints": routes, "base": "http://192.168.3.75:5000"})


START_TIME = time.time()


# ============ Health Check API ============

@app.route('/api/health', methods=['GET'])
@app.route('/api/ping', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime_seconds": time.time() - START_TIME
    })

# ============ Projects API ============

@app.route('/api/projects', methods=['GET'])
def list_projects():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY updated_at DESC")
    result = c.fetchall()
    conn.close()
    for row in result:
        row['code'] = project_code_segment(row['id'], row.get('name'))
    return jsonify(result)

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        """INSERT INTO projects (name, description, type, status, gdd_path, repo_url,
             repo_default_branch, repo_last_sync_at, repo_head_commit, repo_remote_notes,
             category, purpose, benefits, outcome, priority)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            data.get('name'),
            data.get('description'),
            data.get('type', 'game'),
            data.get('status', 'active'),
            data.get('gdd_path'),
            data.get('repo_url'),
            data.get('repo_default_branch'),
            data.get('repo_last_sync_at'),
            data.get('repo_head_commit'),
            data.get('repo_remote_notes'),
            data.get('category'),
            data.get('purpose'),
            data.get('benefits'),
            data.get('outcome'),
            data.get('priority', 'P2'),
            data.get('owner'),
            data.get('expected_revenue', 0),
            data.get('progress_percent', 0),
        ),
    )
    conn.commit()
    project_id = c.lastrowid
    conn.close()
    return jsonify({"id": project_id}), 201

@app.route('/api/projects/<int:pid>', methods=['GET'])
def get_project(pid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id=?", (pid,))
    result = c.fetchone()
    conn.close()
    if result:
        result['code'] = project_code_segment(result['id'], result.get('name'))
        return jsonify(result)
    return jsonify({"error": "Project not found"}), 404


@app.route('/api/projects/<int:pid>', methods=['PATCH'])
def update_project(pid):
    """Update project (HIGH_REQUIREMENTS project metadata + core fields)."""
    data = request.json or {}
    allowed = [
        'name',
        'description',
        'type',
        'status',
        'gdd_path',
        'repo_url',
        'repo_default_branch',
        'repo_last_sync_at',
        'repo_head_commit',
        'repo_remote_notes',
        'category',
        'purpose',
        'benefits',
        'outcome',
        'priority',
        'owner',
        'expected_revenue',
        'progress_percent',
    ]
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE id=?", (pid,))
    if not c.fetchone():
        conn.close()
        return jsonify({"error": "Project not found"}), 404
    fields, values = [], []
    for key in allowed:
        if key not in data:
            continue
        fields.append(f"{key}=?")
        values.append(data[key])
    if fields:
        fields.append("updated_at=?")
        values.append(datetime.datetime.now().isoformat())
        values.append(pid)
        c.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    conn.close()
    return jsonify({"success": True, "id": pid})


@app.route('/api/projects/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    """Remove project only when it has no requirements (avoid orphan cascades)."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE id=?", (pid,))
    if not c.fetchone():
        conn.close()
        return jsonify({"error": "Project not found"}), 404
    c.execute("SELECT COUNT(*) AS n FROM requirements WHERE project_id=?", (pid,))
    row = c.fetchone()
    n = row[0] if not isinstance(row, dict) else row.get('n', 0)
    if n and int(n) > 0:
        conn.close()
        return jsonify({"error": "Project has requirements; delete or reassign them first", "requirement_count": int(n)}), 409
    c.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "deleted_id": pid}), 200


# ============ Requirements API ============

@app.route('/api/projects/<int:pid>/requirements', methods=['GET'])
def list_requirements(pid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(
        "SELECT r.*, p.name as project_name FROM requirements r JOIN projects p ON r.project_id = p.id "
        "WHERE r.project_id=? ORDER BY r.priority, r.created_at DESC",
        (pid,),
    )
    result = c.fetchall()
    conn.close()
    for row in result:
        row['code'] = requirement_code(
            row.get('project_id'),
            row.get('project_name'),
            row['id'],
            row.get('title'),
        )
    return jsonify(result)

def _requirement_deps_satisfied(cursor, depends_on_json):
    """Return True if depends_on is null/empty or all referenced requirement IDs are done/closed."""
    if not depends_on_json or not depends_on_json.strip():
        return True
    try:
        import json as _json
        ids = _json.loads(depends_on_json)
        if not ids:
            return True
        placeholders = ",".join("?" * len(ids))
        cursor.execute(
            f"SELECT COUNT(*) as cnt FROM requirements WHERE id IN ({placeholders}) AND status NOT IN ('done','closed')",
            ids,
        )
        row = cursor.fetchone()
        return (row.get('cnt') or 0) == 0 if isinstance(row, dict) else (row[0] or 0) == 0
    except (ValueError, TypeError):
        return True


@app.route('/api/requirements', methods=['GET'])
def list_all_requirements():
    status = request.args.get('status')
    priority = request.args.get('priority')
    assigned_team = request.args.get('assigned_team')
    project_id = request.args.get('project_id', type=int)
    assignable = request.args.get('assignable', type=lambda x: x in ('1', 'true', 'yes'))
    sort = request.args.get('sort', 'priority_asc')

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    query = "SELECT r.*, p.name as project_name FROM requirements r JOIN projects p ON r.project_id = p.id WHERE 1=1"
    params = []

    if status:
        query += " AND r.status=?"
        params.append(status)
    if priority:
        query += " AND r.priority=?"
        params.append(priority)
    if assigned_team:
        query += " AND r.assigned_team=?"
        params.append(assigned_team)
    if project_id:
        query += " AND r.project_id=?"
        params.append(project_id)

    if assignable:
        query += " AND r.status='new'"

    if sort == 'created_asc':
        query += " ORDER BY r.created_at ASC, r.id ASC"
    else:
        query += " ORDER BY CASE WHEN r.type='bug' THEN 0 ELSE 1 END, r.priority ASC, r.created_at ASC, r.id ASC"

    c.execute(query, params)
    result = c.fetchall()

    if assignable:
        result = [r for r in result if _requirement_deps_satisfied(c, r.get('depends_on') or '')]

    for row in result:
        row['code'] = requirement_code(
            row.get('project_id'),
            row.get('project_name'),
            row['id'],
            row.get('title'),
        )
    conn.close()
    return jsonify(result)

@app.route('/api/requirements', methods=['POST'])
def create_requirement():
    data = request.json or {}
    import json as _json

    dep = data.get('depends_on')
    if isinstance(dep, (list, tuple)):
        dep = _json.dumps(dep, ensure_ascii=False)
    elif dep is not None and not isinstance(dep, str):
        dep = str(dep)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        """INSERT INTO requirements (project_id, title, description, priority, type, assigned_to,
             plan_step_id, plan_phase, parent_requirement_id, depends_on, note)
             VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            data.get('project_id'),
            data.get('title'),
            data.get('description'),
            data.get('priority', 'P2'),
            data.get('type', 'feature'),
            data.get('assigned_to'),
            data.get('plan_step_id'),
            data.get('plan_phase'),
            data.get('parent_requirement_id'),
            dep,
            data.get('note'),
        ),
    )
    conn.commit()
    req_id = c.lastrowid
    conn.close()
    return jsonify({"id": req_id}), 201

@app.route('/api/requirements/<int:rid>', methods=['GET'])
def get_requirement(rid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT r.*, p.name as project_name FROM requirements r LEFT JOIN projects p ON r.project_id = p.id WHERE r.id=?", (rid,))
    result = c.fetchone()
    conn.close()
    if result:
        result['code'] = requirement_code(
            result.get('project_id'),
            result.get('project_name'),
            result['id'],
            result.get('title'),
        )
        return jsonify(result)
    return jsonify({"error": "Requirement not found"}), 404

@app.route('/api/requirements/<int:rid>/take', methods=['POST'])
def take_requirement(rid):
    """Team takes a requirement: set assigned_team, assigned_agent, status=in_progress"""
    data = request.json or {}
    team = data.get('assigned_team')
    agent = data.get('assigned_agent')
    if not team or not agent:
        return jsonify({"error": "assigned_team and assigned_agent required"}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""UPDATE requirements SET assigned_team=?, assigned_agent=?, taken_at=?, status='in_progress', step='analyse', updated_at=?
                 WHERE id=?""", 
               (team, agent, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), rid))
    if c.rowcount == 0:
        conn.close()
        return jsonify({"error": "Requirement not found or already taken"}), 404
    conn.commit()
    conn.close()
    return jsonify({"success": True, "requirement_id": rid, "assigned_team": team, "assigned_agent": agent})


@app.route('/api/requirements/<int:rid>/assign', methods=['POST'])
def assign_requirement(rid):
    """Vanguard assigns a requirement to a team (status stays new until team takes). Fails if depends_on not satisfied."""
    data = request.json or {}
    team = data.get('assigned_team')
    if not team:
        return jsonify({"error": "assigned_team required"}), 400
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT id, status, step, depends_on FROM requirements WHERE id=?", (rid,))
    req = c.fetchone()
    if not req:
        conn.close()
        return jsonify({"error": "Requirement not found"}), 404
    st = req.get('status')
    if st == 'new':
        if not _requirement_deps_satisfied(c, req.get('depends_on') or ''):
            conn.close()
            return jsonify({"error": "Cannot assign: dependency requirements not yet done/closed", "requirement_id": rid}), 400
    elif st == 'in_progress' and str(team).lower() == 'tesla':
        pass
    else:
        conn.close()
        return jsonify({"error": "Can only assign requirements with status=new, or in_progress to tesla (handoff to test)"}), 400
    c.execute("""UPDATE requirements SET assigned_team=?, updated_at=? WHERE id=?""",
               (team, datetime.datetime.now().isoformat(), rid))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "requirement_id": rid, "assigned_team": team})

@app.route('/api/requirements/<int:rid>', methods=['PATCH'])
def update_requirement(rid):
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    fields = []
    values = []
    allowed = ['title', 'description', 'priority', 'status', 'type', 'assigned_to', 'design_doc_path', 'acceptance_criteria',
               'assigned_team', 'assigned_agent', 'taken_at', 'plan_step_id', 'plan_phase', 'step', 'progress_percent', 'depends_on',
               'note', 'parent_requirement_id']
    for key in allowed:
        if key not in data:
            continue
        val = data[key]
        if key == 'depends_on' and isinstance(val, (list, tuple)):
            import json as _json
            val = _json.dumps(val, ensure_ascii=False)
        fields.append(f"{key}=?")
        values.append(val)
    
    if fields:
        fields.append("updated_at=?")
        values.append(datetime.datetime.now().isoformat())
        values.append(rid)
        
        query = f"UPDATE requirements SET {', '.join(fields)} WHERE id=?"
        c.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({"success": True})

# ============ Tasks API ============

@app.route('/api/requirements/<int:rid>/tasks', methods=['GET'])
def list_tasks(rid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(
        "SELECT r.id as req_id, r.title as req_title, r.project_id, p.name as project_name "
        "FROM requirements r LEFT JOIN projects p ON r.project_id = p.id WHERE r.id=?",
        (rid,),
    )
    req_row = c.fetchone()
    c.execute("SELECT * FROM tasks WHERE req_id=? ORDER BY status, created_at", (rid,))
    result = c.fetchall()
    conn.close()
    if req_row:
        pid = req_row.get('project_id')
        proj = req_row.get('project_name')
        rtitle = req_row.get('req_title')
        for row in result:
            row['code'] = task_code(pid, proj, rid, rtitle, row['id'], row.get('title'))
    return jsonify(result)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json or {}
    req_id = data.get('req_id')
    title = data.get('title') or data.get('name', '')
    if not req_id:
        return jsonify({"error": "req_id required"}), 400
    if not title:
        return jsonify({"error": "title required"}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO tasks (req_id, title, description, executor) 
                     VALUES (?,?,?,?)""", 
                   (req_id, title, data.get('description') or '', data.get('executor') or ''))
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": "Invalid req_id or constraint violation", "detail": str(e)}), 400
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return jsonify({"id": task_id, "req_id": req_id, "title": title}), 201


@app.route('/api/tasks/<int:tid>', methods=['GET'])
def get_task(tid):
    """Get a single task (includes next_step_task_id, risk, blocker for Hera/reassignment)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id=?", (tid,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    rid = row.get('req_id')
    c.execute(
        "SELECT r.title as req_title, r.project_id, p.name as project_name FROM requirements r "
        "LEFT JOIN projects p ON r.project_id = p.id WHERE r.id=?",
        (rid,),
    )
    req_row = c.fetchone()
    conn.close()
    if req_row:
        row['code'] = task_code(
            req_row.get('project_id'),
            req_row.get('project_name'),
            rid,
            req_row.get('req_title'),
            tid,
            row.get('title'),
        )
    return jsonify(row)


@app.route('/api/tasks/<int:tid>', methods=['PATCH'])
def update_task(tid):
    """Update task. Supports: title, status, executor, output_path, step, next_step_task_id, risk, blocker,
    est_tokens_total, prompt_rounds (approximate LLM usage per task)."""
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    fields = []
    values = []
    for key in ['title', 'status', 'executor', 'output_path', 'step', 'risk', 'blocker', 'note']:
        if key in data:
            fields.append(f"{key}=?")
            values.append(data[key])
    for key in ('est_tokens_total', 'prompt_rounds'):
        if key in data:
            try:
                v = int(data[key])
                if v < 0:
                    v = 0
            except (TypeError, ValueError):
                conn.close()
                return jsonify({"error": f"{key} must be a non-negative integer"}), 400
            fields.append(f"{key}=?")
            values.append(v)
    if 'next_step_task_id' in data:
        fields.append("next_step_task_id=?")
        values.append(data['next_step_task_id'] if data['next_step_task_id'] is not None else None)
    
    if data.get('status') == 'done' and 'completed_at' not in data:
        fields.append("completed_at=?")
        values.append(datetime.datetime.now().isoformat())
    
    if fields:
        values.append(tid)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id=?"
        c.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({"success": True})


# ============ Test cases API (V-model / test plan) ============


@app.route('/api/requirements/<int:rid>/test-cases', methods=['GET'])
def list_requirement_test_cases(rid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute(
            """SELECT tc.*, r.title AS requirement_title, r.project_id, p.name AS project_name,
                      lt.id AS linked_task_id, lt.title AS linked_task_title
               FROM test_cases tc
               JOIN requirements r ON tc.requirement_id = r.id
               JOIN projects p ON r.project_id = p.id
               LEFT JOIN tasks lt ON tc.task_id = lt.id
               WHERE tc.requirement_id=? ORDER BY tc.layer, tc.id""",
            (rid,),
        )
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": "test_cases table missing; run DB migrations (010)", "detail": str(e)}), 500
    rows = c.fetchall()
    conn.close()
    for row in rows:
        row['code'] = test_case_code(
            row.get('project_id'),
            row.get('project_name'),
            rid,
            row.get('requirement_title'),
            row.get('linked_task_id'),
            row.get('linked_task_title'),
            row['id'],
            row.get('title'),
        )
        for k in ('requirement_title', 'project_name', 'linked_task_id', 'linked_task_title', 'project_id'):
            row.pop(k, None)
    return jsonify(rows)


@app.route('/api/requirements/<int:rid>/test-cases', methods=['POST'])
def create_test_case(rid):
    data = request.json or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute("SELECT 1 FROM requirements WHERE id=?", (rid,))
        if not c.fetchone():
            conn.close()
            return jsonify({"error": "Requirement not found"}), 404
        task_id = data.get('task_id')
        if task_id is not None:
            c.execute("SELECT 1 FROM tasks WHERE id=? AND req_id=?", (task_id, rid))
            if not c.fetchone():
                conn.close()
                return jsonify({"error": "task_id not found on this requirement"}), 400
        layer = data.get('layer') or 'unit'
        c.execute(
            """INSERT INTO test_cases (requirement_id, task_id, layer, title, description, status, result_notes)
               VALUES (?,?,?,?,?,?,?)""",
            (
                rid,
                task_id,
                layer,
                title,
                data.get('description'),
                data.get('status') or 'planned',
                data.get('result_notes'),
            ),
        )
        conn.commit()
        tc_id = c.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": "test_cases table missing; run DB migrations (010)", "detail": str(e)}), 500
    if task_id is not None:
        c.execute(
            """SELECT r.title AS requirement_title, r.project_id, p.name AS project_name,
                      lt.id AS linked_task_id, lt.title AS linked_task_title
               FROM requirements r JOIN projects p ON r.project_id = p.id
               LEFT JOIN tasks lt ON lt.id = ? AND lt.req_id = r.id
               WHERE r.id = ?""",
            (task_id, rid),
        )
    else:
        c.execute(
            """SELECT r.title AS requirement_title, r.project_id, p.name AS project_name,
                      NULL AS linked_task_id, NULL AS linked_task_title
               FROM requirements r JOIN projects p ON r.project_id = p.id
               WHERE r.id = ?""",
            (rid,),
        )
    ctx = c.fetchone()
    conn.close()
    code = None
    if ctx:
        code = test_case_code(
            ctx.get('project_id'),
            ctx.get('project_name'),
            rid,
            ctx.get('requirement_title'),
            ctx.get('linked_task_id'),
            ctx.get('linked_task_title'),
            tc_id,
            title,
        )
    body = {"id": tc_id, "requirement_id": rid}
    if code:
        body["code"] = code
    return jsonify(body), 201


@app.route('/api/test-cases/<int:tcid>', methods=['GET'])
def get_test_case(tcid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute(
            """SELECT tc.*, r.id AS requirement_id, r.title AS requirement_title, r.project_id, p.name AS project_name,
                      lt.id AS linked_task_id, lt.title AS linked_task_title
               FROM test_cases tc
               JOIN requirements r ON tc.requirement_id = r.id
               JOIN projects p ON r.project_id = p.id
               LEFT JOIN tasks lt ON tc.task_id = lt.id
               WHERE tc.id = ?""",
            (tcid,),
        )
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": "test_cases table missing", "detail": str(e)}), 500
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Test case not found"}), 404
    rid = row.get('requirement_id')
    row['code'] = test_case_code(
        row.get('project_id'),
        row.get('project_name'),
        rid,
        row.get('requirement_title'),
        row.get('linked_task_id'),
        row.get('linked_task_title'),
        tcid,
        row.get('title'),
    )
    for k in ('requirement_title', 'project_name', 'linked_task_id', 'linked_task_title', 'project_id'):
        row.pop(k, None)
    return jsonify(row)


@app.route('/api/test-cases/<int:tcid>', methods=['PATCH'])
def update_test_case(tcid):
    data = request.json or {}
    allowed = ['task_id', 'layer', 'title', 'description', 'status', 'result_notes']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("SELECT requirement_id FROM test_cases WHERE id=?", (tcid,))
        row = c.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Test case not found"}), 404
        req_id = row[0] if not isinstance(row, dict) else row.get('requirement_id')
        fields, values = [], []
        for key in allowed:
            if key not in data:
                continue
            if key == 'task_id' and data['task_id'] is not None:
                c.execute("SELECT 1 FROM tasks WHERE id=? AND req_id=?", (data['task_id'], req_id))
                if not c.fetchone():
                    conn.close()
                    return jsonify({"error": "task_id must belong to same requirement"}), 400
            fields.append(f"{key}=?")
            values.append(data[key])
        if fields:
            fields.append("updated_at=?")
            values.append(datetime.datetime.now().isoformat())
            values.append(tcid)
            c.execute(f"UPDATE test_cases SET {', '.join(fields)} WHERE id=?", values)
            conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": "test_cases table missing", "detail": str(e)}), 500
    conn.close()
    return jsonify({"success": True, "id": tcid})


@app.route('/api/test-cases/<int:tcid>', methods=['DELETE'])
def delete_test_case(tcid):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM test_cases WHERE id=?", (tcid,))
        if c.rowcount == 0:
            conn.close()
            return jsonify({"error": "Test case not found"}), 404
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": "test_cases table missing", "detail": str(e)}), 500
    conn.close()
    return jsonify({"success": True, "deleted_id": tcid})


# ============ Machines API ============

@app.route('/api/machines', methods=['GET'])
def list_machines():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM machines ORDER BY name")
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/machines/<int:mid>/status', methods=['POST'])
def update_machine_status(mid):
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE machines SET status=?, last_seen=? WHERE id=?", 
               (data.get('status'), datetime.datetime.now().isoformat(), mid))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ============ Teams API (OpenClaw Communication) ============

@app.route('/api/teams/assigned-requirements', methods=['GET'])
def list_assigned_requirements_query():
    """List requirements assigned to team. Requires ?team=jarvis. Use when path param is awkward."""
    team = request.args.get('team')
    if not team:
        return jsonify({"error": "team required. Example: GET /api/teams/assigned-requirements?team=jarvis"}), 400
    return list_team_assigned_requirements(team)


@app.route('/api/teams/<team>/assigned-requirements', methods=['GET'])
def list_team_assigned_requirements(team):
    """List requirements assigned to a team (for team cron to fetch)"""
    status = request.args.get('status')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    query = "SELECT r.*, p.name as project_name FROM requirements r JOIN projects p ON r.project_id = p.id WHERE r.assigned_team=?"
    params = [team]
    if status:
        query += " AND r.status=?"
        params.append(status)
    # Sort by project priority (pinned ranks first), then by requirement priority/bug-first.
    # Note: we avoid adding a DB column; instead we compute a stable sort key from project name.
    query += """
        ORDER BY
          CASE
            WHEN LOWER(REPLACE(REPLACE(p.name, '_', ' '), '-', ' ')) = 'stock analyze' THEN 1
            WHEN LOWER(REPLACE(REPLACE(p.name, '_', ' '), '-', ' ')) IN ('pinball experience', 'pinball-experience') THEN 2
            WHEN LOWER(REPLACE(REPLACE(p.name, '_', ' '), '-', ' ')) = 'smart factory' THEN 3
            ELSE 1000 + p.id
          END,
          CASE WHEN r.type='bug' THEN 0 ELSE 1 END,
          r.priority ASC,
          r.created_at DESC
    """
    c.execute(query, params)
    result = c.fetchall()
    for row in result:
        row['code'] = requirement_code(
            row.get('project_id'),
            row.get('project_name'),
            row['id'],
            row.get('title'),
        )
    conn.close()
    return jsonify(result)


@app.route('/api/teams/online', methods=['GET'])
def list_online_teams():
    """List teams considered online: machines status=online, or machine_status within 2h, or status_report within STATUS_REPORT_ACTIVE_MINUTES (40 min)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # Teams from machines with team column and status=online
    c.execute("SELECT DISTINCT team FROM machines WHERE team IS NOT NULL AND team != '' AND status='online'")
    machine_teams = [r['team'] for r in c.fetchall() if r.get('team')]
    # Teams with recent machine_status (within last 2 hours); DB stores UTC
    cutoff_2h = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).isoformat()
    try:
        c.execute("SELECT DISTINCT team FROM team_machine_status WHERE reported_at >= ?", (cutoff_2h,))
        status_teams = [r['team'] for r in c.fetchall() if r.get('team')]
    except sqlite3.OperationalError:
        status_teams = []
    # Teams with status_report within active window (40 min); DB stores UTC
    cutoff_status = (datetime.datetime.utcnow() - datetime.timedelta(minutes=STATUS_REPORT_ACTIVE_MINUTES)).isoformat()
    try:
        c.execute(
            "SELECT DISTINCT team FROM team_status_report WHERE reported_at >= ?",
            (cutoff_status,)
        )
        report_teams = [r['team'] for r in c.fetchall() if r.get('team')]
    except sqlite3.OperationalError:
        report_teams = []
    conn.close()
    all_teams = list(set(machine_teams + status_teams + report_teams))
    return jsonify({"teams": sorted(all_teams)})


@app.route('/api/teams/<team>/machine-status', methods=['POST'])
def report_team_machine_status(team):
    """Team reports machine status (custom format in payload)"""
    data = request.json or {}
    payload = data.get('payload', data)
    if isinstance(payload, dict):
        import json
        payload = json.dumps(payload, ensure_ascii=False)
    reporter = data.get('reporter_agent', data.get('reporter', ''))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""INSERT INTO team_machine_status (team, payload, reporter_agent) VALUES (?,?,?)""",
               (team, payload, reporter))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": sid, "team": team})


@app.route('/api/teams/<team>/machine-status', methods=['GET'])
def get_team_machine_status(team):
    """Get latest machine status reports for a team"""
    limit = int(request.args.get('limit', 24))
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM team_machine_status WHERE team=? ORDER BY reported_at DESC LIMIT ?""",
                   (team, limit))
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


def _sync_tasks_from_payload(c, tasks_list):
    """Update existing tasks in DB from status-report payload tasks[]. Each item: id, status?, executor?, risk?, blocker?, next_step_task_id?, est_tokens_total?, prompt_rounds?."""
    if not isinstance(tasks_list, list):
        return
    for t in tasks_list:
        tid = t.get('id') if isinstance(t, dict) else None
        if not tid:
            continue
        fields, values = [], []
        for key in ['status', 'executor', 'risk', 'blocker']:
            if isinstance(t, dict) and key in t:
                fields.append(f"{key}=?")
                values.append(t[key])
        if isinstance(t, dict) and 'next_step_task_id' in t:
            fields.append("next_step_task_id=?")
            values.append(t['next_step_task_id'] if t.get('next_step_task_id') is not None else None)
        for key in ('est_tokens_total', 'prompt_rounds'):
            if isinstance(t, dict) and key in t:
                try:
                    v = int(t[key])
                    if v < 0:
                        v = 0
                except (TypeError, ValueError):
                    v = 0
                fields.append(f"{key}=?")
                values.append(v)
        if not fields:
            continue
        values.append(tid)
        try:
            c.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", values)
        except sqlite3.OperationalError:
            pass


@app.route('/api/teams/<team>/status-report', methods=['POST'])
def report_team_status(team):
    """Team reports status with task details to Hera (management). Payload: requirement_id, progress, tasks[], analysis_breakdown?, etc.
    tasks[] may include id, status, executor, risk, blocker, next_step_task_id, est_tokens_total, prompt_rounds; these are synced to the tasks table."""
    data = request.json or {}
    payload = data.get('payload', data)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Sync task status/executor/risk/blocker/next_step_task_id from payload to DB (update existing tasks only)
    if isinstance(payload, dict):
        _sync_tasks_from_payload(c, payload.get('tasks'))
    else:
        try:
            import json as json_mod
            pl = json_mod.loads(payload) if isinstance(payload, str) else None
            if isinstance(pl, dict):
                _sync_tasks_from_payload(c, pl.get('tasks'))
        except Exception:
            pass
    conn.commit()
    if isinstance(payload, dict):
        import json as json_mod
        payload = json_mod.dumps(payload, ensure_ascii=False)
    reporter = data.get('reporter_agent', data.get('reporter', ''))
    try:
        reported_at = datetime.datetime.utcnow().isoformat()
        c.execute("""INSERT INTO team_status_report (team, payload, reporter_agent, reported_at) VALUES (?,?,?,?)""",
                   (team, payload, reporter, reported_at))
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "team_status_report table not found, run migrations"}), 500
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": sid, "team": team})


@app.route('/api/teams/<team>/status-report', methods=['GET'])
def get_team_status_report(team):
    """Get latest status reports for a team (Hera reads). Optional ?since=<ISO timestamp> for incremental."""
    limit = int(request.args.get('limit', 24))
    since = request.args.get('since')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        if since:
            c.execute("""SELECT * FROM team_status_report WHERE team=? AND reported_at >= ? ORDER BY reported_at DESC LIMIT ?""",
                       (team, since, limit))
        else:
            c.execute("""SELECT * FROM team_status_report WHERE team=? ORDER BY reported_at DESC LIMIT ?""",
                       (team, limit))
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


@app.route('/api/teams/status-report/summary', methods=['GET'])
def get_all_teams_status_summary():
    """Hera: latest status report from each team. Each item has 'active' and 'workload' (in_progress count for load balancing)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute("""
            SELECT tsr.* FROM team_status_report tsr
            INNER JOIN (
                SELECT team, MAX(reported_at) as max_at FROM team_status_report GROUP BY team
            ) latest ON tsr.team = latest.team AND tsr.reported_at = latest.max_at
            ORDER BY tsr.reported_at DESC
        """)
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=STATUS_REPORT_ACTIVE_MINUTES)
    for row in result:
        reported = row.get('reported_at')
        if reported:
            try:
                if isinstance(reported, str):
                    reported_dt = datetime.datetime.fromisoformat(reported.replace('Z', '+00:00')[:19])
                else:
                    reported_dt = reported
                if getattr(reported_dt, 'tzinfo', None):
                    reported_dt = reported_dt.replace(tzinfo=None)
                row['active'] = reported_dt >= cutoff
            except (ValueError, TypeError):
                row['active'] = False
        else:
            row['active'] = False
        team_name = row.get('team')
        if team_name:
            try:
                c.execute("SELECT COUNT(*) as cnt FROM requirements WHERE assigned_team=? AND status='in_progress'", (team_name,))
                w = c.fetchone()
                row['workload'] = {"in_progress_count": (w.get('cnt') or 0) if isinstance(w, dict) else (w[0] or 0)}
            except sqlite3.OperationalError:
                row['workload'] = {"in_progress_count": 0}
    conn.close()
    return jsonify(result)


@app.route('/api/teams/<team>/task-detail', methods=['POST'])
def post_team_task_detail(team):
    """Team reports development detail for a specific task (analysis, assignment, or development). 
    Hera/Vanguard use for final report.
    
    requirement_id and task_id are optional for quick member status updates.
    """
    data = request.json or {}
    requirement_id = data.get('requirement_id')
    task_id = data.get('task_id')
    detail_type = (data.get('detail_type') or '').lower()
    content = data.get('content') or data.get('text', '')
    
    # Make task_id optional for requirement_id and quick member status updates
    if requirement_id is None:
        requirement_id = 0  # Use 0 as placeholder for "no specific requirement"
    if task_id is None:
        task_id = 0  # Use 0 as placeholder for "no specific task"
    
    if detail_type not in ('analysis', 'assignment', 'development'):
        return jsonify({"error": "detail_type must be one of: analysis, assignment, development"}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO team_task_detail (team, requirement_id, task_id, detail_type, content)
                     VALUES (?,?,?,?,?)""",
                  (team, requirement_id, task_id, detail_type, content))
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "team_task_detail table not found, run migrations (005_team_task_detail.sql)"}), 500
    conn.commit()
    did = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": did, "team": team, "requirement_id": requirement_id, "task_id": task_id, "detail_type": detail_type}), 201


@app.route('/api/teams/<team>/task-details', methods=['GET'])
def get_team_task_details(team):
    """List task development details for a team (Hera / report builder). Optional ?requirement_id=."""
    requirement_id = request.args.get('requirement_id', type=int)
    limit = min(int(request.args.get('limit', 100)), 200)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        if requirement_id is not None:
            c.execute("""SELECT * FROM team_task_detail WHERE team=? AND requirement_id=?
                        ORDER BY reported_at DESC LIMIT ?""", (team, requirement_id, limit))
        else:
            c.execute("""SELECT * FROM team_task_detail WHERE team=? ORDER BY reported_at DESC LIMIT ?""", (team, limit))
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


@app.route('/api/teams/<team>/report', methods=['POST'])
def post_team_report(team):
    """Submit full development or test task report (see standards/report/DEVELOPMENT_TASK_REPORT_TEMPLATE.md, TEST_TASK_REPORT_TEMPLATE.md)."""
    data = request.json or {}
    requirement_id = data.get('requirement_id')
    report_type = (data.get('report_type') or '').lower()
    content = data.get('content') or data.get('text', '')
    if requirement_id is None:
        return jsonify({"error": "requirement_id required"}), 400
    if report_type not in ('development', 'test'):
        return jsonify({"error": "report_type must be 'development' or 'test'"}), 400
    if isinstance(content, (dict, list)):
        import json as _json
        content = _json.dumps(content, ensure_ascii=False)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO team_report (team, requirement_id, report_type, content) VALUES (?,?,?,?)""",
                  (team, requirement_id, report_type, content))
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "team_report table not found, run migrations (006_openclaw_workflow.sql)"}), 500
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": rid, "team": team, "requirement_id": requirement_id, "report_type": report_type}), 201


@app.route('/api/teams/<team>/reports', methods=['GET'])
def get_team_reports(team):
    """List development/test reports for a team. Optional ?requirement_id=, ?report_type=development|test."""
    requirement_id = request.args.get('requirement_id', type=int)
    report_type = request.args.get('report_type', '').lower()
    limit = min(int(request.args.get('limit', 50)), 100)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        q = "SELECT * FROM team_report WHERE team=?"
        params = [team]
        if requirement_id is not None:
            q += " AND requirement_id=?"
            params.append(requirement_id)
        if report_type in ('development', 'test'):
            q += " AND report_type=?"
            params.append(report_type)
        q += " ORDER BY reported_at DESC LIMIT ?"
        params.append(limit)
        c.execute(q, params)
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


@app.route('/api/teams/development-details/summary', methods=['GET'])
def get_development_details_summary():
    """Summary of task development details and dev/test reports per team for final report."""
    per_team = max(1, min(int(request.args.get('per_team', 30)), 100))
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    out = []
    try:
        teams_set = set()
        c.execute("SELECT DISTINCT team FROM team_task_detail")
        for r in c.fetchall():
            teams_set.add(r['team'])
        c.execute("SELECT DISTINCT team FROM team_report")
        for r in c.fetchall():
            teams_set.add(r['team'])
        for team in sorted(teams_set):
            c.execute("""SELECT * FROM team_task_detail WHERE team=? ORDER BY reported_at DESC LIMIT ?""",
                      (team, per_team))
            details = c.fetchall()
            c.execute("""SELECT * FROM team_report WHERE team=? ORDER BY reported_at DESC LIMIT ?""", (team, 20))
            reports = c.fetchall()
            out.append({"team": team, "details": details, "reports": reports})
    except sqlite3.OperationalError:
        pass
    conn.close()
    return jsonify(out)


@app.route('/api/teams/machine-status/summary', methods=['GET'])
def get_all_teams_machine_status_summary():
    """Get latest machine status from all teams (for Vanguard summary)"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute("""
            SELECT tms.* FROM team_machine_status tms
            INNER JOIN (
                SELECT team, MAX(reported_at) as max_at FROM team_machine_status GROUP BY team
            ) latest ON tms.team = latest.team AND tms.reported_at = latest.max_at
            ORDER BY tms.reported_at DESC
        """)
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)

# ============ Tools API ============

@app.route('/api/tools', methods=['GET'])
def list_tools():
    tool_type = request.args.get('type')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    if tool_type:
        c.execute("SELECT * FROM tools WHERE type=? ORDER BY name", (tool_type,))
    else:
        c.execute("SELECT * FROM tools ORDER BY type, name")
    
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/tools', methods=['POST'])
def register_tool():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""INSERT INTO tools (name, type, source, path, status, config) 
                 VALUES (?,?,?,?,?,?)""", 
               (data.get('name'), data.get('type'), data.get('source'), 
                data.get('path'), data.get('status', 'active'), data.get('config')))
    conn.commit()
    tool_id = c.lastrowid
    conn.close()
    return jsonify({"id": tool_id}), 201

# ============ Dashboard API ============

@app.route('/api/dashboard/stats')
def dashboard_stats():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Project counts
    c.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
    projects = c.fetchall()
    
    # Requirement counts
    c.execute("SELECT status, COUNT(*) as count FROM requirements GROUP BY status")
    requirements = c.fetchall()
    
    # Task counts
    c.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    tasks = c.fetchall()
    
    # Machine status
    c.execute("SELECT status, COUNT(*) as count FROM machines GROUP BY status")
    machines = c.fetchall()
    
    conn.close()
    
    return jsonify({
        "projects": projects,
        "requirements": requirements,
        "tasks": tasks,
        "machines": machines
    })


@app.route('/api/dashboard/risk-report')
def dashboard_risk_report():
    """Hera: risk report for in-progress requirements and blocked tasks"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    risks = []
    # In-progress requirements with low progress or stuck
    c.execute("""SELECT r.id, r.title, r.assigned_team, r.step, r.progress_percent, r.taken_at
                 FROM requirements r WHERE r.status='in_progress'""")
    for req in c.fetchall():
        r = dict(req)
        if r.get('progress_percent', 0) == 0 and r.get('step') == 'analyse':
            risks.append({"type": "stuck_analyse", "req_id": r['id'], "team": r['assigned_team'], "title": r['title']})
        elif r.get('progress_percent', 0) < 50 and r.get('step') == 'implement':
            risks.append({"type": "slow_progress", "req_id": r['id'], "team": r['assigned_team'], "progress": r.get('progress_percent', 0)})
    # Blocked tasks
    c.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status='blocked'")
    row = c.fetchone()
    blocked = (row.get('cnt', 0) or 0) if row else 0
    if blocked > 0:
        risks.append({"type": "blocked_tasks", "count": blocked})
    conn.close()
    return jsonify({"risks": risks, "count": len(risks)})


# ============ Discussion / Blockage API (Team → Hera) ============

@app.route('/api/discussion/blockage', methods=['POST'])
def post_discussion_blockage():
    """Team reports a blockage; Hera coordinates resolution."""
    data = request.json or {}
    team = data.get('team')
    requirement_id = data.get('requirement_id')
    reason = data.get('reason') or data.get('reason_text', '')
    if not team or requirement_id is None:
        return jsonify({"error": "team and requirement_id required"}), 400
    options = data.get('options')
    if isinstance(options, (list, dict)):
        import json as _json
        options = _json.dumps(options, ensure_ascii=False)
    task_id = data.get('task_id')
    level = data.get('level')  # optional: 'L1' | 'L2' | 'L3'
    knowledge_ref = data.get('knowledge_ref')  # optional: pointer to knowledge base entry/doc
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        # level/knowledge_ref are optional; old DBs without these columns will raise OperationalError and be guided to re-run migrations.
        c.execute(
            """INSERT INTO discussion_blockage (team, requirement_id, task_id, reason, options, level, status, knowledge_ref)
               VALUES (?,?,?,?,?,?, 'pending', ?)""",
            (team, requirement_id, task_id, reason, options, level, knowledge_ref),
        )
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "discussion_blockage table not found or outdated, run migrations (004_discussion_blockage.sql)"}), 500
    conn.commit()
    bid = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": bid, "team": team, "requirement_id": requirement_id}), 201


@app.route('/api/discussion/blockages', methods=['GET'])
def list_discussion_blockages():
    """Hera: list blockages, optionally filtered by status=pending."""
    status = request.args.get('status', 'pending')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        if status:
            c.execute("SELECT * FROM discussion_blockage WHERE status=? ORDER BY reported_at DESC", (status,))
        else:
            c.execute("SELECT * FROM discussion_blockage ORDER BY reported_at DESC")
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


@app.route('/api/discussion/blockage/<int:bid>', methods=['PATCH'])
def patch_discussion_blockage(bid):
    """Hera: set decision and resolve blockage."""
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        updates = []
        values = []
        if 'status' in data:
            updates.append("status=?")
            values.append(data['status'])
            if data.get('status') == 'resolved':
                updates.append("resolved_at=?")
                values.append(datetime.datetime.now().isoformat())
        if 'decision' in data:
            updates.append("decision=?")
            values.append(data['decision'])
        if 'level' in data:
            # allow Hera to adjust blocker level after会诊
            updates.append("level=?")
            values.append(data['level'])
        if 'knowledge_ref' in data:
            # link to knowledge base entry or doc path
            updates.append("knowledge_ref=?")
            values.append(data['knowledge_ref'])
        if 'meeting_id' in data:
            # link to meetings (Hera triggers meeting for L2/L3 blockers, then resolves later)
            updates.append("meeting_id=?")
            values.append(data['meeting_id'])
        if not updates:
            conn.close()
            return jsonify({"error": "status or decision required"}), 400
        values.append(bid)
        c.execute("UPDATE discussion_blockage SET " + ", ".join(updates) + " WHERE id=?", values)
        conn.commit()
        if c.rowcount == 0:
            conn.close()
            return jsonify({"error": "Blockage not found"}), 404
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "discussion_blockage table not found, run migrations"}), 500
    conn.close()
    return jsonify({"success": True, "id": bid})


# ============ Meetings API ============

def _normalize_ts(ts: str) -> str:
    """Best-effort normalization for SQLite comparisons."""
    if not ts:
        return ts
    # We store timestamps using datetime.utcnow().isoformat() (with 'T') and without 'Z'.
    # Keep 'T' to preserve lexicographical ordering for ISO-like strings.
    return ts.replace("Z", "")


@app.route('/api/meetings', methods=['GET'])
def list_meetings():
    """Dashboard helper: list meetings by status (default: running)."""
    status = request.args.get('status') or 'running'
    limit = min(int(request.args.get('limit', 20)), 100)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT
              m.*,
              (SELECT COUNT(*) FROM meeting_participants mp WHERE mp.meeting_id = m.id) AS participants_total
            FROM meetings m
            WHERE m.status=?
            ORDER BY m.updated_at DESC, m.id DESC
            LIMIT ?
            """,
            (status, limit),
        )
        result = c.fetchall() or []
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


@app.route('/api/meetings', methods=['POST'])
def create_meeting():
    """Create a meeting and invite participants."""
    data = request.json or {}
    topic = data.get('topic')
    if not topic:
        return jsonify({"error": "topic required"}), 400

    host_agent = data.get('host_agent') or data.get('host')
    if not host_agent:
        return jsonify({"error": "host_agent required"}), 400

    problem_to_solve = data.get('problem_to_solve') or data.get('problem')
    status = data.get('status') or 'running'
    current_round = int(data.get('current_round') or 1)
    initiated_by_agent = data.get('initiated_by_agent') or host_agent
    participants = data.get('participants') or []

    if not isinstance(participants, list) or not participants:
        return jsonify({"error": "participants must be a non-empty list"}), 400

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO meetings (topic, problem_to_solve, status, host_agent, initiated_by_agent, current_round)
               VALUES (?,?,?,?,?,?)""",
            (topic, problem_to_solve, status, host_agent, initiated_by_agent, current_round),
        )
        mid = c.lastrowid

        for p in participants:
            if not isinstance(p, dict):
                continue
            agent_id = p.get('agent_id') or p.get('id')
            if not agent_id:
                continue
            role_label = p.get('role_label') or p.get('role')
            contribute_focus = p.get('contribute_focus') or p.get('contribute') or p.get('contribute_details')
            c.execute(
                """INSERT OR IGNORE INTO meeting_participants (meeting_id, agent_id, role_label, contribute_focus, status)
                   VALUES (?,?,?,?, 'invited')""",
                (mid, agent_id, role_label, contribute_focus),
            )

        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": f"meetings tables missing/outdated: {e}"}), 500
    conn.close()
    return jsonify({"success": True, "meeting_id": mid, "status": status, "current_round": current_round}), 201


@app.route('/api/meetings/for-agent', methods=['GET'])
def list_meetings_for_agent():
    """List running meetings where the given agent is invited."""
    agent = request.args.get('agent')
    if not agent:
        return jsonify({"error": "agent query param required"}), 400

    status_filter = request.args.get('status') or 'running'
    limit = min(int(request.args.get('limit', 20)), 50)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute(
        """
        SELECT m.*, mp.status as participant_status, mp.role_label, mp.contribute_focus
        FROM meetings m
        JOIN meeting_participants mp ON mp.meeting_id = m.id
        WHERE mp.agent_id=? AND m.status=?
        ORDER BY m.updated_at DESC, m.id DESC
        LIMIT ?
        """,
        (agent, status_filter, limit),
    )
    meetings = c.fetchall()

    out = []
    for m in meetings:
        mid = m.get('id')
        current_round = int(m.get('current_round') or 1)

        # Check if this agent submitted input for current round
        c.execute(
            """
            SELECT 1 as ok
            FROM meeting_participant_inputs
            WHERE meeting_id=? AND agent_id=? AND round_number=?
            LIMIT 1
            """,
            (mid, agent, current_round),
        )
        my_submitted = c.fetchone() is not None

        # Participants summary (no analysis leakage)
        c.execute(
            """
            SELECT agent_id, role_label, contribute_focus, status
            FROM meeting_participants
            WHERE meeting_id=?
            ORDER BY id
            """,
            (mid,),
        )
        participants = c.fetchall() or []
        participants_total = len(participants)

        # Others inputs count
        c.execute(
            """
            SELECT COUNT(*) as cnt
            FROM meeting_participant_inputs
            WHERE meeting_id=? AND round_number=?
            """,
            (mid, current_round),
        )
        cnt_row = c.fetchone() or {}
        submitted_cnt = int(cnt_row.get('cnt') or 0)

        out.append(
            {
                "id": mid,
                "topic": m.get('topic'),
                "problem_to_solve": m.get('problem_to_solve'),
                "host_agent": m.get('host_agent'),
                "status": m.get('status'),
                "current_round": current_round,
                "my_participant": {
                    "agent_id": agent,
                    "status": m.get('participant_status'),
                    "role_label": m.get('role_label'),
                    "contribute_focus": m.get('contribute_focus'),
                },
                "participants": participants,
                "my_input_submitted": my_submitted,
                "others_submitted_count": max(0, submitted_cnt - (1 if my_submitted else 0)),
                "participants_total": participants_total,
                "needs_your_input": not my_submitted,
            }
        )

    conn.close()
    return jsonify(out)


@app.route('/api/meetings/<int:mid>', methods=['GET'])
def get_meeting(mid: int):
    """Get meeting theme/details. Optional ?agent=<id> to include my participant status."""
    agent = request.args.get('agent')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute("SELECT * FROM meetings WHERE id=?", (mid,))
    m = c.fetchone()
    if not m:
        conn.close()
        return jsonify({"error": "Meeting not found"}), 404

    my_participant = None
    if agent:
        c.execute(
            """
            SELECT agent_id, role_label, contribute_focus, status, acknowledged_at, submitted_at
            FROM meeting_participants
            WHERE meeting_id=? AND agent_id=?
            """,
            (mid, agent),
        )
        my_participant = c.fetchone()

    c.execute(
        """
        SELECT agent_id, role_label, contribute_focus, status
        FROM meeting_participants
        WHERE meeting_id=?
        ORDER BY id
        """,
        (mid,),
    )
    participants = c.fetchall() or []

    conn.close()
    return jsonify({"meeting": m, "my_participant": my_participant, "participants": participants})


@app.route('/api/meetings/<int:mid>/inputs', methods=['POST'])
def post_meeting_inputs(mid: int):
    """Submit meeting analysis/comments for the given agent."""
    data = request.json or {}
    agent_id = data.get('agent_id')
    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute(
        "SELECT status FROM meeting_participants WHERE meeting_id=? AND agent_id=?",
        (mid, agent_id),
    )
    p = c.fetchone()
    if not p:
        conn.close()
        return jsonify({"error": "agent_id is not a participant"}), 403

    c.execute("SELECT current_round FROM meetings WHERE id=?", (mid,))
    m = c.fetchone()
    if not m:
        conn.close()
        return jsonify({"error": "Meeting not found"}), 404

    current_round = int(m.get('current_round') or 1)
    round_number = int(data.get('round_number') or current_round)
    analysis = data.get('analysis') or data.get('analysis_text')
    comments = data.get('comments') or data.get('comment') or data.get('comments_text')

    try:
        # Upsert input (single round by UNIQUE constraint)
        c.execute(
            """
            SELECT id FROM meeting_participant_inputs
            WHERE meeting_id=? AND agent_id=? AND round_number=?
            """,
            (mid, agent_id, round_number),
        )
        row = c.fetchone()
        now = datetime.datetime.utcnow().isoformat()
        if row:
            c.execute(
                """
                UPDATE meeting_participant_inputs
                SET analysis=?, comments=?, submitted_at=?
                WHERE id=?
                """,
                (analysis, comments, now, row.get('id')),
            )
        else:
            c.execute(
                """
                INSERT INTO meeting_participant_inputs (meeting_id, agent_id, round_number, analysis, comments, submitted_at)
                VALUES (?,?,?,?,?,?)
                """,
                (mid, agent_id, round_number, analysis, comments, now),
            )

        c.execute(
            """
            UPDATE meeting_participants
            SET status='submitted', submitted_at=?
            WHERE meeting_id=? AND agent_id=?
            """,
            (now, mid, agent_id),
        )

        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": f"meetings tables missing/outdated: {e}"}), 500

    conn.close()
    return jsonify({"success": True, "meeting_id": mid, "agent_id": agent_id, "round_number": round_number}), 201


@app.route('/api/meetings/<int:mid>/inputs', methods=['GET'])
def get_meeting_inputs(mid: int):
    """Read meeting inputs. Default excludes ?agent=<id> (self)."""
    agent = request.args.get('agent')
    exclude_self = request.args.get('exclude_self', '1')
    since = request.args.get('since')
    round_number = request.args.get('round_number')

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute("SELECT current_round FROM meetings WHERE id=?", (mid,))
    m = c.fetchone()
    if not m:
        conn.close()
        return jsonify({"error": "Meeting not found"}), 404
    current_round = int(m.get('current_round') or 1)
    rn = int(round_number) if round_number is not None else current_round

    params = [mid, rn]
    q = """
        SELECT agent_id, round_number, analysis, comments, submitted_at
        FROM meeting_participant_inputs
        WHERE meeting_id=? AND round_number=?
    """

    if since:
        q += " AND submitted_at >= ?"
        params.append(_normalize_ts(since))

    if agent and str(exclude_self).lower() not in ('0', 'false', 'no'):
        q += " AND agent_id <> ?"
        params.append(agent)

    q += " ORDER BY submitted_at ASC"

    c.execute(q, params)
    inputs = c.fetchall() or []
    conn.close()
    return jsonify({"meeting_id": mid, "round_number": rn, "inputs": inputs})


@app.route('/api/meetings/<int:mid>/finalize', methods=['POST'])
def finalize_meeting(mid: int):
    """Host finalizes a meeting; optionally creates requirements and assigns them."""
    data = request.json or {}
    host_agent = data.get('host_agent')
    if not host_agent:
        return jsonify({"error": "host_agent required"}), 400

    conclusion_summary = data.get('conclusion_summary') or data.get('conclusion') or data.get('final_summary')
    if not conclusion_summary:
        return jsonify({"error": "conclusion_summary required"}), 400

    conclusion_decision = data.get('conclusion_decision')
    requirements = data.get('requirements') or []
    if requirements and not isinstance(requirements, list):
        return jsonify({"error": "requirements must be a list"}), 400

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute("SELECT * FROM meetings WHERE id=?", (mid,))
    m = c.fetchone()
    if not m:
        conn.close()
        return jsonify({"error": "Meeting not found"}), 404

    if m.get('host_agent') != host_agent:
        conn.close()
        return jsonify({"error": "Only meeting host can finalize"}), 403

    if m.get('status') != 'running':
        conn.close()
        return jsonify({"error": "Meeting not in running status"}), 400

    import json as _json
    created_req_ids = []
    now = datetime.datetime.utcnow().isoformat()

    try:
        for r in requirements:
            if not isinstance(r, dict):
                continue
            title = r.get('title')
            project_id = r.get('project_id')
            if not title or project_id is None:
                conn.close()
                return jsonify({"error": "Each requirement needs title and project_id"}), 400

            req_type = r.get('type') or 'feature'
            priority = r.get('priority') or 'P2'
            description = r.get('description') or ''
            assigned_team = r.get('assigned_team') or r.get('team')
            assigned_agent = r.get('assigned_agent') or r.get('agent')
            if not assigned_team or not assigned_agent:
                conn.close()
                return jsonify({"error": "Each requirement needs assigned_team and assigned_agent"}), 400

            # Insert requirement with explicit assignment; keep status=new for next cycles.
            c.execute(
                """
                INSERT INTO requirements
                    (project_id, title, description, priority, status, type, assigned_to, assigned_team, assigned_agent, step, progress_percent)
                VALUES
                    (?,?,?,?, 'new', ?, ?, ?, ?, 'not start', 0)
                """,
                (
                    project_id,
                    title,
                    description,
                    priority,
                    req_type,
                    assigned_agent,  # assigned_to (legacy field)
                    assigned_team,
                    assigned_agent,
                ),
            )
            created_req_ids.append(c.lastrowid)

        created_req_ids_json = _json.dumps(created_req_ids)
        c.execute(
            """
            UPDATE meetings
            SET status='concluded',
                conclusion_summary=?,
                conclusion_decision=?,
                finalized_at=?,
                created_requirement_ids=?,
                updated_at=?
            WHERE id=?
            """,
            (conclusion_summary, conclusion_decision, now, created_req_ids_json, now, mid),
        )
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": f"finalize failed (tables missing/outdated): {e}"}), 500

    conn.close()
    return jsonify({"success": True, "meeting_id": mid, "status": "concluded", "created_requirement_ids": created_req_ids}), 201


# ============ Meeting Delete API ============

@app.route('/api/meetings/<int:mid>', methods=['DELETE'])
def delete_meeting(mid):
    """Delete a meeting (only if no participants with submissions)."""
    conn = get_db()
    c = conn.cursor()
    try:
        # Check if meeting exists
        c.execute("SELECT id, status FROM meetings WHERE id=?", (mid,))
        row = c.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": f"Meeting {mid} not found"}), 404
        
        # Check if there are any participants with submissions
        try:
            c.execute("SELECT COUNT(*) FROM meeting_participant_inputs WHERE meeting_id=?", (mid,))
            input_count = c.fetchone()[0]
        except:
            input_count = 0
        
        if input_count > 0:
            conn.close()
            return jsonify({"error": f"Cannot delete meeting with {input_count} participant inputs"}), 400
        
        # Delete meeting (cascade will handle participants)
        try:
            c.execute("DELETE FROM meeting_participant_inputs WHERE meeting_id=?", (mid,))
            c.execute("DELETE FROM meeting_participants WHERE meeting_id=?", (mid,))
            c.execute("DELETE FROM meetings WHERE id=?", (mid,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"error": f"Delete query failed: {str(e)}"}), 500
        
        conn.close()
        return jsonify({"success": True, "meeting_id": mid, "deleted": True}), 200
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Delete failed: {str(e)}"}), 500


# ============ Work Log API (all roles: 时间、任务名称、任务输出、任务下一步) ============

@app.route('/api/work-log', methods=['POST'])
def post_work_log():
    """Append a work log entry (role_or_team, task_name, task_output, next_step)."""
    data = request.json or {}
    role_or_team = data.get('role_or_team') or data.get('team') or data.get('role', '')
    task_name = data.get('task_name', '')
    task_output = data.get('task_output', '')
    next_step = data.get('next_step', '')
    if not role_or_team or not task_name:
        return jsonify({"error": "role_or_team and task_name required"}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO work_log (role_or_team, task_name, task_output, next_step) VALUES (?,?,?,?)""",
                  (role_or_team, task_name, task_output, next_step))
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({"error": "work_log table not found, run migrations (006_openclaw_workflow.sql)"}), 500
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": lid, "role_or_team": role_or_team, "task_name": task_name}), 201


@app.route('/api/work-logs', methods=['GET'])
def list_work_logs():
    """List work logs. Optional ?role_or_team=, ?since=<ISO timestamp>."""
    role_or_team = request.args.get('role_or_team')
    since = request.args.get('since')
    limit = min(int(request.args.get('limit', 100)), 500)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    try:
        q = "SELECT * FROM work_log WHERE 1=1"
        params = []
        if role_or_team:
            q += " AND role_or_team=?"
            params.append(role_or_team)
        if since:
            q += " AND created_at >= ?"
            params.append(since)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        c.execute(q, params)
        result = c.fetchall()
    except sqlite3.OperationalError:
        result = []
    conn.close()
    return jsonify(result)


# ============ Pipeline API ============

@app.route('/api/pipelines', methods=['GET'])
def list_pipelines():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("""SELECT p.*, pr.name as project_name 
                 FROM pipelines p 
                 LEFT JOIN projects pr ON p.project_id = pr.id 
                 ORDER BY p.updated_at DESC""")
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/pipelines', methods=['POST'])
def create_pipeline():
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""INSERT INTO pipelines (name, description, project_id, trigger_type, stages, status) 
                 VALUES (?,?,?,?,?,?)""", 
               (data.get('name'), data.get('description'), data.get('project_id'),
                data.get('trigger_type', 'manual'), data.get('stages'), 'inactive'))
    conn.commit()
    pipeline_id = c.lastrowid
    conn.close()
    return jsonify({"id": pipeline_id}), 201

@app.route('/api/pipelines/<int:pid>', methods=['GET'])
def get_pipeline(pid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM pipelines WHERE id=?", (pid,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify(result)
    return jsonify({"error": "Pipeline not found"}), 404

@app.route('/api/pipelines/<int:pid>/run', methods=['POST'])
def run_pipeline(pid):
    """Trigger a pipeline run"""
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Get current run number (fetchone returns tuple when no row_factory)
    c.execute("SELECT COALESCE(MAX(run_number), 0) + 1 as next FROM pipeline_runs WHERE pipeline_id=?", (pid,))
    row = c.fetchone()
    next_run = row[0] if row else 1
    
    # Create run record
    c.execute("""INSERT INTO pipeline_runs (pipeline_id, run_number, status, trigger_reason) 
                 VALUES (?,?,?,?)""", 
               (pid, next_run, 'running', data.get('trigger_reason', 'manual')))
    run_id = c.lastrowid
    
    # Update pipeline last_run_at
    c.execute("UPDATE pipelines SET last_run_at=?, updated_at=? WHERE id=?", 
               (datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), pid))
    
    conn.commit()
    conn.close()
    
    return jsonify({"run_id": run_id, "run_number": next_run, "status": "started"})

@app.route('/api/pipelines/<int:pid>/runs', methods=['GET'])
def list_pipeline_runs(pid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("""SELECT * FROM pipeline_runs WHERE pipeline_id=? ORDER BY run_number DESC LIMIT 20""", (pid,))
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/pipelines/<int:pid>', methods=['DELETE'])
def delete_pipeline(pid):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM pipelines WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ============ Auto Task Splitting ============

@app.route('/api/requirements/<int:rid>/auto-split', methods=['POST'])
def auto_split_requirement(rid):
    """Auto-generate tasks based on requirement type"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Get requirement
    c.execute("SELECT * FROM requirements WHERE id=?", (rid,))
    req = c.fetchone()
    
    if not req:
        conn.close()
        return jsonify({"error": "Requirement not found"}), 404
    
    req_type = req.get('type') or 'feature'
    req_title = req.get('title') or 'Untitled'
    
    # Generate tasks based on type
    task_templates = {
        "feature": [
            {"title": f"[{req_title}] 设计阶段", "description": "完成功能设计文档"},
            {"title": f"[{req_title}] 开发阶段", "description": "实现功能代码"},
            {"title": f"[{req_title}] 测试阶段", "description": "编写测试用例并验证"},
            {"title": f"[{req_title}] 集成阶段", "description": "集成到主分支"}
        ],
        "bug": [
            {"title": f"[{req_title}] 问题定位", "description": "定位并复现问题"},
            {"title": f"[{req_title}] 修复开发", "description": "编写修复代码"},
            {"title": f"[{req_title}] 验证测试", "description": "验证修复有效"}
        ],
        "enhancement": [
            {"title": f"[{req_title}] 需求分析", "description": "分析改进点"},
            {"title": f"[{req_title}] 实施方案", "description": "制定实施方案"},
            {"title": f"[{req_title}] 开发实现", "description": "开发改进代码"}
        ],
        "asset": [
            {"title": f"[{req_title}] 资源收集", "description": "收集相关资源"},
            {"title": f"[{req_title}] 资源处理", "description": "处理和优化资源"},
            {"title": f"[{req_title}] 集成测试", "description": "测试资源集成"}
        ],
        "research": [
            {"title": f"[{req_title}] 调研阶段", "description": "技术调研和方案对比"},
            {"title": f"[{req_title}] 结论总结", "description": "输出调研报告"}
        ]
    }
    
    templates = task_templates.get(req_type, task_templates["feature"])
    created_tasks = []
    
    for task in templates:
        c.execute("""INSERT INTO tasks (req_id, title, description, status) 
                     VALUES (?,?,?,?)""", 
                   (rid, task['title'], task['description'], 'todo'))
        created_tasks.append({"id": c.lastrowid, "title": task['title']})
    
    conn.commit()
    conn.close()
    
    return jsonify({"requirement_id": rid, "created_tasks": created_tasks})

# ============ CI/CD Triggers API ============

@app.route('/api/pipelines/<int:pid>/triggers', methods=['GET'])
def list_triggers(pid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM cicd_triggers WHERE pipeline_id=?", (pid,))
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/pipelines/<int:pid>/triggers', methods=['POST'])
def create_trigger(pid):
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""INSERT INTO cicd_triggers (pipeline_id, trigger_type, repo_url, branch, webhook_secret, schedule_cron) 
                 VALUES (?,?,?,?,?,?)""", 
               (pid, data.get('trigger_type', 'commit'), data.get('repo_url'),
                data.get('branch', 'main'), data.get('webhook_secret'), data.get('schedule_cron')))
    conn.commit()
    trigger_id = c.lastrowid
    conn.close()
    return jsonify({"id": trigger_id}), 201

@app.route('/api/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    import hmac
    import hashlib
    
    # Get payload
    payload = request.get_json()
    event = request.headers.get('X-GitHub-Event', 'push')
    
    # Find matching trigger
    repo_url = payload.get('repository', {}).get('html_url', '')
    branch = payload.get('ref', '').replace('refs/heads/', '')
    commit_sha = payload.get('after', '')
    commit_message = payload.get('commits', [{}])[0].get('message', '') if payload.get('commits') else ''
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Find enabled commit triggers for this repo
    c.execute("""SELECT t.*, p.name as pipeline_name FROM cicd_triggers t 
                 JOIN pipelines p ON t.pipeline_id = p.id 
                 WHERE t.trigger_type='commit' AND t.enabled=1 
                 AND t.repo_url LIKE ? AND t.branch=?""", 
               (f"%{repo_url.split('/')[-1]}%", branch))
    triggers = c.fetchall()
    
    triggered_builds = []
    for trigger in triggers:
        # Create build record
        c.execute("""INSERT INTO cicd_builds (trigger_id, pipeline_id, commit_sha, commit_message, branch, status) 
                     VALUES (?,?,?,?,?,?)""", 
                   (trigger['id'], trigger['pipeline_id'], commit_sha, commit_message, branch, 'running'))
        build_id = c.lastrowid
        
        # Update trigger last_triggered_at
        c.execute("UPDATE cicd_triggers SET last_triggered_at=? WHERE id=?", 
                   (datetime.datetime.now().isoformat(), trigger['id']))
        
        conn.commit()
        triggered_builds.append({"trigger_id": trigger['id'], "build_id": build_id, "pipeline": trigger['pipeline_name']})
    
    conn.close()
    
    return jsonify({
        "event": event,
        "repo": repo_url,
        "branch": branch,
        "builds_triggered": triggered_builds
    })

@app.route('/api/webhook/github', methods=['GET'])
def github_webhook_verify():
    """Verify webhook endpoint is active"""
    return jsonify({"status": "ok", "event": "github_webhook"})

@app.route('/api/cicd/builds', methods=['GET'])
def list_cicd_builds():
    pipeline_id = request.args.get('pipeline_id')
    status = request.args.get('status')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    query = "SELECT b.*, p.name as pipeline_name FROM cicd_builds b JOIN pipelines p ON b.pipeline_id = p.id WHERE 1=1"
    params = []
    
    if pipeline_id:
        query += " AND b.pipeline_id=?"
        params.append(pipeline_id)
    if status:
        query += " AND b.status=?"
        params.append(status)
    
    query += " ORDER BY b.started_at DESC LIMIT 50"
    
    c.execute(query, params)
    result = c.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/cicd/builds/<int:bid>', methods=['GET'])
def get_build(bid):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM cicd_builds WHERE id=?", (bid,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify(result)
    return jsonify({"error": "Build not found"}), 404

@app.route('/api/cicd/builds/<int:bid>/status', methods=['PATCH'])
def update_build_status(bid):
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    fields = ["status=?"]
    values = [data.get('status')]
    
    if data.get('status') in ['success', 'failed', 'cancelled']:
        fields.append("finished_at=?")
        values.append(datetime.datetime.now().isoformat())
    
    if data.get('build_log'):
        fields.append("build_log=?")
        values.append(data['build_log'])
    
    if data.get('artifacts'):
        fields.append("artifacts=?")
        values.append(data['artifacts'])
    
    values.append(bid)
    c.execute(f"UPDATE cicd_builds SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

# ============ Feishu API Logger ============

@app.route('/api/feishu/logs/analyze', methods=['POST'])
def analyze_feishu_logs():
    """分析飞书API日志"""
    import subprocess
    import sys
    
    log_file = request.json.get('log_file') if request.json else None
    
    try:
        env = os.environ.copy()
        env["FEISHU_LOG_DB"] = FEISHU_LOG_DB
        result = subprocess.run(
            [sys.executable, 'openclaw-knowledge/subsystems/tools/feishu_api_logger.py', '--analyze', '--report'],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
            env=env,
        )
        return jsonify({
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/feishu/post', methods=['POST'])
def post_to_feishu():
    """Post message to Feishu group via webhook. Set FEISHU_WEBHOOK_URL env for default."""
    import urllib.request
    import json as json_mod
    data = request.json or {}
    text = data.get('text', data.get('content', data.get('message', '')))
    title = data.get('title', 'Smart Factory')
    if not text:
        return jsonify({"error": "text, content, or message required"}), 400
    webhook_url = data.get('webhook_url') or os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        return jsonify({"error": "FEISHU_WEBHOOK_URL not configured, or pass webhook_url in body"}), 400
    payload = {"msg_type": "text", "content": {"text": f"[{title}]\n{text}"}}
    if data.get('msg_type') == 'interactive':
        payload = data.get('payload', payload)
    req = urllib.request.Request(webhook_url, data=json_mod.dumps(payload).encode(),
                                  headers={"Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            result = json_mod.loads(body) if body else {}
            # Feishu returns code=0 or StatusCode=0 on success
            if result.get('code', 0) == 0 or result.get('StatusCode', 0) == 0:
                return jsonify({"success": True, "feishu_response": result})
            return jsonify({"success": False, "feishu_response": result}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/feishu/stats', methods=['GET'])
def get_feishu_stats():
    """获取飞书API调用统计"""
    import sqlite3
    
    if not os.path.exists(FEISHU_LOG_DB):
        return jsonify({"error": "No data yet", "calls": []})
    
    conn = sqlite3.connect(FEISHU_LOG_DB)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Get daily stats
    c.execute('''
        SELECT date, source, purpose, api_count, success_count, failed_count
        FROM api_call_stats
        ORDER BY date DESC
        LIMIT 30
    ''')
    daily_stats = c.fetchall()
    
    # Get recent calls
    c.execute('''
        SELECT timestamp, source, chat_type, purpose, api_endpoint, status
        FROM feishu_api_calls
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    recent_calls = c.fetchall()
    
    conn.close()
    
    return jsonify({
        "calls": len(recent_calls or []),
        "daily_stats": daily_stats,
        "recent_calls": recent_calls
    })

# ============ Voice-to-Text API ============

@app.route('/api/voice', methods=['POST'])
def voice_to_text():
    """
    语音转文字 API
    接收音频文件或音频数据，调用 OpenAI Whisper API 进行语音识别
    
    支持的输入:
    - multipart/form-data 上传音频文件 (file 参数)
    - application/octet-stream 直接上传音频数据
    
    支持的音频格式: mp3, mp4, m4a, wav, webm, ogg, flac
    
    返回: { "success": true, "text": "转录文字" }
    """
    try:
        # 检查 OpenAI API Key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            # 尝试从配置文件读取
            import json
            config_path = os.path.expanduser('~/.openclaw/openclaw.json')
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                    api_key = config.get('skills', {}).get('openai-whisper-api', {}).get('apiKey')
                except:
                    pass
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "OPENAI_API_KEY 未配置",
                "message": "请设置 OPENAI_API_KEY 环境变量或在 ~/.openclaw/openclaw.json 中配置 skills.openai-whisper-api.apiKey"
            }), 401
        
        # 获取音频数据
        audio_data = None
        filename = "audio.mp3"
        
        # 方式1: 文件上传
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "未提供音频文件"}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "error": "文件名为空"}), 400
            filename = file.filename
            audio_data = file.read()
        # 方式2: 直接二进制数据
        elif request.data:
            audio_data = request.data
            filename = request.headers.get('X-Filename', 'audio.mp3')
        else:
            return jsonify({"success": False, "error": "未提供音频数据"}), 400
        
        if not audio_data:
            return jsonify({"success": False, "error": "音频数据为空"}), 400
        
        # 调用 OpenAI Whisper API
        try:
            from openai import OpenAI
        except ImportError:
            return jsonify({
                "success": False,
                "error": "openai 库未安装",
                "message": "请运行: pip install openai"
            }), 500
        
        client = OpenAI(api_key=api_key)
        
        # 获取语言参数 (可选)
        language = request.form.get('language') or request.json.get('language') if request.is_json else None
        
        # 获取额外提示 (可选)
        prompt = request.form.get('prompt') or request.json.get('prompt') if request.is_json else None
        
        # 创建临时文件用于 Whisper API
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # 调用 Whisper API
            with open(tmp_path, 'rb') as audio_file:
                kwargs = {
                    'model': 'whisper-1',
                    'file': audio_file,
                }
                if language:
                    kwargs['language'] = language
                if prompt:
                    kwargs['prompt'] = prompt
                
                response = client.audio.transcriptions.create(**kwargs)
                text = response.text
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        return jsonify({
            "success": True,
            "text": text,
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500

def init_db():
    """Initialize DB schema and run migrations."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    _api_dir = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(_api_dir)
    schema_path = os.path.join(_root, 'db', 'schema.sql')
    migrations_dir = os.path.join(_root, 'db', 'migrations')
    with sqlite3.connect(DATABASE) as conn:
        with open(schema_path) as f:
            conn.executescript(f.read())
        # Run migrations (safe to re-run); use executescript so multi-statement files apply correctly
        if os.path.isdir(migrations_dir):
            for f in sorted(os.listdir(migrations_dir)):
                if f.endswith('.sql'):
                    path = os.path.join(migrations_dir, f)
                    with open(path) as fp:
                        script = fp.read()
                    try:
                        conn.executescript(script)
                    except sqlite3.OperationalError as e:
                        err = str(e).lower()
                        if 'duplicate column' not in err and 'already exists' not in err:
                            raise
        conn.commit()


# ============ Knowledge Collection API ============

@app.route('/api/knowledge/collect', methods=['POST'])
def collect_knowledge():
    """Trigger on-demand knowledge collection for jay-knowledge-db"""
    import subprocess
    import sys
    
    try:
        result = subprocess.run(
            [sys.executable, "/home/pi/.openclaw/workspace/working/code/nlp/docs/auto_knowledge_collector.py", "on-demand"],
            capture_output=True, text=True, timeout=120
        )
        return jsonify({
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "errors": result.stderr
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500



# ============ Knowledge Base API ============

@app.route('/api/knowledge/items', methods=['GET'])
def get_knowledge_items():
    """List knowledge items with filtering"""
    category = request.args.get('category')
    tag = request.args.get('tag')
    project_id = request.args.get('project_id')
    search = request.args.get('search')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    query = "SELECT * FROM knowledge_items WHERE 1=1"
    params = []
    
    if category:
        query += " AND category=?"
        params.append(category)
    if project_id:
        query += " AND project_id=?"
        params.append(int(project_id))
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY created_at DESC"
    
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return jsonify(items)


@app.route('/api/knowledge/items/<int:item_id>', methods=['GET'])
def get_knowledge_item(item_id):
    """Get single knowledge item"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM knowledge_items WHERE id=?", (item_id,))
    item = c.fetchone()
    conn.close()
    if item:
        return jsonify(item)
    return jsonify({"error": "Not found"}), 404


@app.route('/api/knowledge/items', methods=['POST'])
def create_knowledge_item():
    """Create new knowledge item"""
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        """INSERT INTO knowledge_items (title, content, category, tags, source, project_id, requirement_id, created_by, status)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            data.get('title'),
            data.get('content'),
            data.get('category'),
            data.get('tags'),
            data.get('source', 'manual'),
            data.get('project_id'),
            data.get('requirement_id'),
            data.get('created_by', 'user'),
            data.get('status', 'active'),
        )
    )
    item_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": item_id}), 201


@app.route('/api/knowledge/items/<int:item_id>', methods=['PATCH'])
def update_knowledge_item(item_id):
    """Update knowledge item"""
    data = request.json or {}
    allowed = ['title', 'content', 'category', 'tags', 'source', 'status']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    fields, values = [], []
    for key in allowed:
        if key in data:
            fields.append(f"{key}=?")
            values.append(data[key])
    if fields:
        fields.append("updated_at=CURRENT_TIMESTAMP")
        values.append(item_id)
        c.execute(f"UPDATE knowledge_items SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    conn.close()
    return jsonify({"success": True, "id": item_id})


@app.route('/api/knowledge/items/<int:item_id>', methods=['DELETE'])
def delete_knowledge_item(item_id):
    """Delete knowledge item"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM knowledge_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route('/api/knowledge/categories', methods=['GET'])
def get_knowledge_categories():
    """List all categories"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM knowledge_categories ORDER BY sort_order, name")
    categories = c.fetchall()
    conn.close()
    return jsonify(categories)


@app.route('/api/knowledge/categories', methods=['POST'])
def create_knowledge_category():
    """Create category"""
    data = request.json or {}
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO knowledge_categories (name, description, icon, color) VALUES (?,?,?,?)",
        (data.get('name'), data.get('description'), data.get('icon', '📄'), data.get('color', '#6B7280'))
    )
    cat_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": cat_id}), 201


@app.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    """Full-text search for OpenClaw agents"""
    q = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(
        "SELECT * FROM knowledge_items WHERE title LIKE ? OR content LIKE ? LIMIT ?",
        (f"%{q}%", f"%{q}%", limit)
    )
    results = c.fetchall()
    conn.close()
    return jsonify(results)




@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """Get knowledge base statistics"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Total count
    c.execute("SELECT COUNT(*) as total FROM knowledge_items")
    total = c.fetchone()['total']
    
    # By category
    c.execute("""
        SELECT category, COUNT(*) as count 
        FROM knowledge_items 
        WHERE category IS NOT NULL 
        GROUP BY category
    """)
    by_category = {r['category']: r['count'] for r in c.fetchall()}
    
    # By source
    c.execute("""
        SELECT source, COUNT(*) as count 
        FROM knowledge_items 
        GROUP BY source
    """)
    by_source = {r['source']: r['count'] for r in c.fetchall()}
    
    # Recent (last 7 days)
    c.execute("""
        SELECT COUNT(*) as count FROM knowledge_items 
        WHERE created_at >= datetime('now', '-7 days')
    """)
    recent = c.fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'total': total,
        'by_category': by_category,
        'by_source': by_source,
        'recent_7days': recent
    })


@app.route('/api/knowledge/suggest', methods=['GET'])
def suggest_knowledge():
    """Suggest related knowledge items based on context query"""
    context = request.args.get('context', '')
    limit = int(request.args.get('limit', 5))
    
    if not context:
        return jsonify([])
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    
    # Simple keyword matching
    keywords = context.lower().split()
    conditions = ' OR '.join(['(title LIKE ? OR content LIKE ?)' for _ in keywords])
    params = [f"%{kw}%" for kw in keywords for _ in range(2)]
    
    query = f"""
        SELECT * FROM knowledge_items 
        WHERE {conditions}
        ORDER BY 
            CASE WHEN status = 'pinned' THEN 0 ELSE 1 END,
            created_at DESC
        LIMIT ?
    """
    params.append(limit)
    
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    
    return jsonify(results)


@app.route('/api/knowledge/items/<int:item_id>', methods=['PATCH'])
def update_knowledge_item_v2(item_id):
    """Update knowledge item including project_id/requirement_id"""
    data = request.json or {}
    allowed = ['title', 'content', 'category', 'tags', 'source', 'status', 'project_id', 'requirement_id']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Verify exists
    c.execute("SELECT id FROM knowledge_items WHERE id=?", (item_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({"error": "Not found"}), 404
    
    fields, values = [], []
    for key in allowed:
        if key in data:
            fields.append(f"{key}=?")
            values.append(data[key])
    
    if fields:
        fields.append("updated_at=CURRENT_TIMESTAMP")
        values.append(item_id)
        c.execute(f"UPDATE knowledge_items SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    
    conn.close()
    return jsonify({"success": True, "id": item_id})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route("/gui")
def react_gui():
    """Serve React GUI"""
    return app.send_static_file("react-gui/index.html")

@app.route("/gui/<path:filename>")
def react_gui_files(filename):
    """Serve React GUI static files"""
    return send_from_directory(os.path.join(_STATIC, "react-gui"), filename)

