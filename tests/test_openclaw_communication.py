"""
OpenClaw Communication System API 测试
"""
import pytest
import sys
import os
import tempfile
import sqlite3

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core', 'api'))


@pytest.fixture
def app_and_db():
    """Create app with temp DB for testing"""
    import server as srv
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    srv.DATABASE = path
    srv.init_db()
    yield srv.app, path
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def client(app_and_db):
    app, _ = app_and_db
    return app.test_client()


class TestAssignAPI:
    def test_assign_requirement_requires_team(self, client):
        r = client.post('/api/requirements/1/assign', json={})
        assert r.status_code == 400

    def test_assign_requirement_not_found(self, client):
        r = client.post('/api/requirements/999/assign', json={'assigned_team': 'jarvis'})
        assert r.status_code == 404

    def test_assign_requirement_success(self, client):
        # Create project and requirement first
        client.post('/api/projects', json={'name': 'Test', 'type': 'tool'})
        client.post('/api/requirements', json={
            'project_id': 1, 'title': 'Test', 'priority': 'P2', 'type': 'feature'
        })
        r = client.post('/api/requirements/1/assign', json={'assigned_team': 'jarvis'})
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('assigned_team') == 'jarvis'


class TestTeamsAPI:
    def test_team_assigned_requirements_empty(self, client):
        r = client.get('/api/teams/jarvis/assigned-requirements')
        assert r.status_code == 200
        assert r.json == []

    def test_teams_online_empty(self, client):
        r = client.get('/api/teams/online')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert 'teams' in data

    def test_report_machine_status(self, client):
        r = client.post('/api/teams/jarvis/machine-status', json={
            'payload': {'cpu': '45%', 'hostname': 'jarvis-mac'},
            'reporter_agent': 'jarvis'
        })
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('team') == 'jarvis'

    def test_get_team_machine_status(self, client):
        client.post('/api/teams/jarvis/machine-status', json={'payload': {'test': 1}})
        r = client.get('/api/teams/jarvis/machine-status')
        assert r.status_code == 200
        data = r.get_json() if hasattr(r, 'get_json') else r.json
        assert len(data) >= 1

    def test_machine_status_summary(self, client):
        r = client.get('/api/teams/machine-status/summary')
        assert r.status_code == 200

    def test_status_report_and_summary_with_active_flag(self, client):
        r = client.post('/api/teams/jarvis/status-report', json={
            'payload': {'requirement_id': 1, 'progress_percent': 50, 'tasks': []},
            'reporter_agent': 'jarvis'
        })
        assert r.status_code == 200
        r = client.get('/api/teams/status-report/summary')
        assert r.status_code == 200
        data = r.get_json() if hasattr(r, 'get_json') else r.json
        assert len(data) >= 1
        jarvis = next((x for x in data if x.get('team') == 'jarvis'), None)
        assert jarvis is not None
        assert 'active' in jarvis
        assert 'workload' in jarvis
        assert jarvis['workload'].get('in_progress_count') is not None
        # Just reported, so should be active
        assert jarvis['active'] is True

    def test_teams_online_includes_recent_status_report(self, client):
        client.post('/api/teams/codeforge/status-report', json={
            'payload': {'requirement_id': 1}, 'reporter_agent': 'codeforge'
        })
        r = client.get('/api/teams/online')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert 'teams' in data
        assert 'codeforge' in data['teams']


class TestRequirementsFilter:
    def test_requirements_filter_assigned_team(self, client):
        r = client.get('/api/requirements?assigned_team=jarvis')
        assert r.status_code == 200

    def test_requirements_assignable(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.get('/api/requirements?assignable=1')
        assert r.status_code == 200
        data = r.get_json() if hasattr(r, 'get_json') else r.json
        assert isinstance(data, list)
        # May include the new requirement if no depends_on or deps satisfied
        if data:
            assert data[0].get('status') == 'new'


class TestWorkLogAndReport:
    def test_work_log_post_and_list(self, client):
        r = client.post('/api/work-log', json={
            'role_or_team': 'vanguard',
            'task_name': '检查在线团队',
            'task_output': 'jarvis, codeforge',
            'next_step': '检查需求列表'
        })
        assert r.status_code == 201
        r = client.get('/api/work-logs?role_or_team=vanguard')
        assert r.status_code == 200
        data = r.get_json() if hasattr(r, 'get_json') else r.json
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0].get('task_name') == '检查在线团队'

    def test_team_report_development(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.post('/api/teams/jarvis/report', json={
            'requirement_id': 1,
            'report_type': 'development',
            'content': '{"completed_tasks": [{"id": "1", "executor": "dev1", "lines": 120}]}'
        })
        assert r.status_code == 201
        r = client.get('/api/teams/jarvis/reports?report_type=development')
        assert r.status_code == 200
        data = r.get_json() if hasattr(r, 'get_json') else r.json
        assert len(data) >= 1
        assert data[0].get('report_type') == 'development'

    def test_team_report_test(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.post('/api/teams/tesla/report', json={
            'requirement_id': 1,
            'report_type': 'test',
            'content': '{"test_cases": [], "result": "pass"}'
        })
        assert r.status_code == 201


class TestMeetingsAPI:
    def test_meeting_create_post_inputs_finalize(self, client):
        # prerequisite: project exists
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})

        # create meeting
        r = client.post('/api/meetings', json={
            'topic': '阻塞会诊',
            'problem_to_solve': '确认处理方案',
            'host_agent': 'hera',
            'initiated_by_agent': 'hera',
            'participants': [
                {'agent_id': 'hera', 'role_label': 'host', 'contribute_focus': '主持并汇总'},
                {'agent_id': 'athena', 'role_label': 'architect', 'contribute_focus': '技术方案分析'},
            ],
        })
        assert r.status_code == 201
        data = r.get_json() or r.json
        mid = data.get('meeting_id')

        # post input for athena
        r = client.post(f'/api/meetings/{mid}/inputs', json={
            'agent_id': 'athena',
            'analysis': 'analysis here',
            'comments': 'comment here',
        })
        assert r.status_code == 201

        # finalize meeting and create requirements
        r = client.post(f'/api/meetings/{mid}/finalize', json={
            'host_agent': 'hera',
            'conclusion_summary': 'Concluded',
            'requirements': [
                {
                    'project_id': 1,
                    'title': 'New requirement from meeting',
                    'description': 'desc',
                    'type': 'feature',
                    'priority': 'P2',
                    'assigned_team': 'jarvis',
                    'assigned_agent': 'athena',
                }
            ],
        })
        assert r.status_code == 201
        data = r.get_json() or r.json
        assert data.get('status') == 'concluded'

        # verify requirement exists
        r = client.get('/api/requirements?assigned_team=jarvis')
        assert r.status_code == 200
        reqs = r.get_json() or r.json
        assert any(x.get('title') == 'New requirement from meeting' for x in reqs)
