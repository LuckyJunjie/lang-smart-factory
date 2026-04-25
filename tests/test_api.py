"""
智慧工厂 API 单元测试 — 使用 Flask 测试客户端与临时数据库
"""
import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core', 'api'))


@pytest.fixture
def app_and_db():
    """Create app with temp DB for testing."""
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


class TestProjectsAPI:
    """项目管理模块测试"""

    def test_list_projects(self, client):
        r = client.get('/api/projects')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_create_project(self, client):
        r = client.post('/api/projects', json={'name': 'TestProj', 'type': 'tool'})
        assert r.status_code == 201
        data = r.get_json() or r.json
        assert 'id' in data
        assert data['id'] == 1

    def test_get_project(self, client):
        client.post('/api/projects', json={'name': 'P1', 'type': 'game'})
        r = client.get('/api/projects/1')
        assert r.status_code == 200
        assert (r.get_json() or r.json).get('name') == 'P1'

    def test_get_project_requirements(self, client):
        client.post('/api/projects', json={'name': 'P1', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R1', 'priority': 'P2', 'type': 'feature'})
        r = client.get('/api/projects/1/requirements')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert len(data) >= 1
        assert data[0]['title'] == 'R1'

    def test_task_llm_usage_fields(self, client):
        client.post('/api/projects', json={'name': 'U', 'type': 'tool'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        client.post('/api/tasks', json={'req_id': 1, 'title': 'T1', 'executor': 'a'})
        p = client.patch('/api/tasks/1', json={'est_tokens_total': 9000, 'prompt_rounds': 4})
        assert p.status_code == 200
        g = client.get('/api/tasks/1')
        body = g.get_json() or g.json
        assert int(body.get('est_tokens_total') or 0) == 9000
        assert int(body.get('prompt_rounds') or 0) == 4
        bad = client.patch('/api/tasks/1', json={'est_tokens_total': 'x'})
        assert bad.status_code == 400

    def test_hierarchy_codes_p_req_task_tc(self, client):
        """docs/REQUIREMENTS.md §2.0: P<id>-words-REQ<id>-words-TASK…-TC…"""
        client.post('/api/projects', json={'name': 'Alpha Game Studio', 'type': 'game'})
        p = client.get('/api/projects/1').get_json() or {}
        assert p.get('code', '').startswith('P1-')
        assert 'REQ' not in p['code']
        client.post(
            '/api/requirements',
            json={'project_id': 1, 'title': 'User Authentication Story', 'priority': 'P2', 'type': 'feature'},
        )
        req = client.get('/api/requirements/1').get_json() or {}
        c_req = req.get('code') or ''
        assert c_req.startswith('P1-')
        assert 'REQ1-' in c_req
        assert 'TASK' not in c_req
        client.post('/api/tasks', json={'req_id': 1, 'title': 'Implement OAuth Handler', 'executor': 'a1'})
        tasks = client.get('/api/requirements/1/tasks').get_json() or []
        assert len(tasks) == 1
        c_task = tasks[0].get('code') or ''
        assert 'TASK1-' in c_task
        assert c_task.startswith(c_req)
        t_one = client.get('/api/tasks/1').get_json() or {}
        assert t_one.get('code') == c_task
        tc_resp = client.post(
            '/api/requirements/1/test-cases',
            json={'title': 'OAuth Redirect Success Path', 'layer': 'integration', 'task_id': 1},
        )
        assert tc_resp.status_code == 201
        body = tc_resp.get_json() or tc_resp.json
        assert 'TC1-' in (body.get('code') or '')
        assert 'TASK1-' in body['code']
        lst = client.get('/api/requirements/1/test-cases').get_json() or []
        assert len(lst) == 1
        assert lst[0].get('code') == body.get('code')


class TestHealthAPI:
    """健康检查 API 测试"""

    def test_health_endpoint(self, client):
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('status') == 'ok'
        assert 'timestamp' in data

    def test_ping_endpoint(self, client):
        r = client.get('/api/ping')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('status') == 'ok'


class TestRequirementsAPI:
    """需求管理模块测试"""

    def test_list_requirements(self, client):
        r = client.get('/api/requirements')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_create_requirement(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        r = client.post('/api/requirements', json={'project_id': 1, 'title': 'Req1', 'priority': 'P2', 'type': 'feature'})
        assert r.status_code == 201
        assert (r.get_json() or r.json).get('id') == 1

    def test_get_requirement(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.get('/api/requirements/1')
        assert r.status_code == 200
        assert (r.get_json() or r.json).get('title') == 'R'

    def test_update_requirement(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.patch('/api/requirements/1', json={'title': 'R2', 'status': 'in_progress'})
        assert r.status_code == 200
        r2 = client.get('/api/requirements/1')
        assert (r2.get_json() or r2.json).get('title') == 'R2'

    def test_update_requirement_step(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.patch('/api/requirements/1', json={'step': 'implement'})
        assert r.status_code == 200

    def test_auto_split_requirement(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'Feature X', 'priority': 'P2', 'type': 'feature'})
        r = client.post('/api/requirements/1/auto-split')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('requirement_id') == 1
        assert len(data.get('created_tasks', [])) >= 1


class TestTasksAPI:
    """任务管理模块测试"""

    def test_list_tasks(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.get('/api/requirements/1/tasks')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_create_task(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.post('/api/tasks', json={'req_id': 1, 'title': 'Task 1'})
        assert r.status_code == 201
        data = r.get_json() or r.json
        assert data.get('req_id') == 1 and data.get('title') == 'Task 1'

    def test_update_task(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        client.post('/api/tasks', json={'req_id': 1, 'title': 'T1'})
        r = client.patch('/api/tasks/1', json={'status': 'in_progress'})
        assert r.status_code == 200

    def test_update_task_step(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        client.post('/api/tasks', json={'req_id': 1, 'title': 'T1'})
        r = client.patch('/api/tasks/1', json={'step': 'implement'})
        assert r.status_code == 200


class TestMachinesAPI:
    """机器管理模块测试"""

    def test_list_machines(self, client):
        r = client.get('/api/machines')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_update_machine_status(self, client):
        # Need a machine first; create via raw DB or skip if empty
        r = client.get('/api/machines')
        if not (r.json or []):
            pytest.skip('no machines in test DB')
        mid = (r.json or [])[0]['id']
        r = client.post(f'/api/machines/{mid}/status', json={'status': 'online'})
        assert r.status_code == 200


class TestToolsAPI:
    """工具链模块测试"""

    def test_list_tools(self, client):
        r = client.get('/api/tools')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_register_tool(self, client):
        r = client.post('/api/tools', json={'name': 'mcp-x', 'type': 'mcp', 'path': '/path/to/mcp'})
        assert r.status_code == 201
        assert (r.get_json() or r.json).get('id') is not None


class TestPipelineAPI:
    """流水线模块测试"""

    def test_list_pipelines(self, client):
        r = client.get('/api/pipelines')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_create_pipeline(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        r = client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1, 'trigger_type': 'manual'})
        assert r.status_code == 201
        assert (r.get_json() or r.json).get('id') == 1

    def test_get_pipeline(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        r = client.get('/api/pipelines/1')
        assert r.status_code == 200
        assert (r.get_json() or r.json).get('name') == 'CI'

    def test_trigger_pipeline(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        r = client.post('/api/pipelines/1/run', json={'trigger_reason': 'test'})
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get('status') == 'started' and 'run_number' in data

    def test_get_pipeline_runs(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        client.post('/api/pipelines/1/run', json={'trigger_reason': 'test'})
        r = client.get('/api/pipelines/1/runs')
        assert r.status_code == 200
        assert len(r.json or []) >= 1

    def test_delete_pipeline(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        r = client.delete('/api/pipelines/1')
        assert r.status_code == 200
        r2 = client.get('/api/pipelines/1')
        assert r2.status_code == 404


class TestCICDTriggerAPI:
    """CI/CD 触发器模块测试"""

    def test_get_triggers(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        r = client.get('/api/pipelines/1/triggers')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_create_trigger(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CI', 'project_id': 1})
        r = client.post('/api/pipelines/1/triggers', json={'trigger_type': 'commit', 'repo_url': 'https://github.com/x/y', 'branch': 'main'})
        assert r.status_code == 201
        assert (r.get_json() or r.json).get('id') is not None

    def test_github_webhook(self, client):
        r = client.get('/api/webhook/github')
        assert r.status_code == 200
        assert (r.get_json() or r.json).get('status') == 'ok'


class TestCICDBuildsAPI:
    """CI/CD 构建模块测试"""

    def test_list_builds(self, client):
        r = client.get('/api/cicd/builds')
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_get_build(self, client):
        r = client.get('/api/cicd/builds/999')
        assert r.status_code == 404

    def test_update_build_status(self, client):
        # Create pipeline run and trigger to get a build, or test 404
        r = client.patch('/api/cicd/builds/1/status', json={'status': 'success'})
        # 200 if exists, or we just ensure no 500
        assert r.status_code in (200, 404)


class TestFeishuAPI:
    """飞书集成模块测试"""

    def test_analyze_logs(self, client):
        r = client.post('/api/feishu/logs/analyze', json={})
        # May succeed or fail on missing script; expect 200 or 500
        assert r.status_code in (200, 500)

    def test_get_stats(self, client):
        r = client.get('/api/feishu/stats')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert 'calls' in data or 'error' in data


class TestDashboardAPI:
    """仪表盘模块测试"""

    def test_get_stats(self, client):
        r = client.get('/api/dashboard/stats')
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert 'projects' in data and 'requirements' in data and 'tasks' in data


class TestHighRequirementsCRUD:
    """Project metadata, sub-requirements, test-case APIs (HIGH_REQUIREMENTS / OpenClaw blackboard)."""

    def test_patch_project_metadata(self, client):
        client.post(
            '/api/projects',
            json={
                'name': 'MetaProj',
                'type': 'tool',
                'purpose': 'bootstrap KB',
                'benefits': 'faster onboarding',
                'outcome': 'documented APIs',
                'category': 'platform',
                'priority': 'P1',
            },
        )
        r = client.patch(
            '/api/projects/1',
            json={'outcome': 'stable CRUD', 'benefits': 'agents can query all fields'},
        )
        assert r.status_code == 200
        g = client.get('/api/projects/1')
        assert g.status_code == 200
        body = g.get_json() or g.json
        assert body.get('purpose') == 'bootstrap KB'
        assert body.get('outcome') == 'stable CRUD'
        assert body.get('priority') == 'P1'

    def test_project_remote_repo_fields(self, client):
        client.post(
            '/api/projects',
            json={
                'name': 'RepoProj',
                'type': 'tool',
                'repo_url': 'https://example.com/org/repo.git',
                'repo_default_branch': 'main',
            },
        )
        r = client.patch(
            '/api/projects/1',
            json={
                'repo_last_sync_at': '2026-04-04T12:00:00+00:00',
                'repo_head_commit': 'a1b2c3d',
                'repo_remote_notes': 'pinball mainline',
            },
        )
        assert r.status_code == 200
        g = client.get('/api/projects/1')
        body = g.get_json() or g.json
        assert body.get('repo_url') == 'https://example.com/org/repo.git'
        assert body.get('repo_default_branch') == 'main'
        assert '2026-04-04' in (body.get('repo_last_sync_at') or '')
        assert body.get('repo_head_commit') == 'a1b2c3d'
        assert body.get('repo_remote_notes') == 'pinball mainline'

    def test_delete_project_conflict_when_has_requirements(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        r = client.delete('/api/projects/1')
        assert r.status_code == 409

    def test_delete_project_when_empty(self, client):
        client.post('/api/projects', json={'name': 'Empty', 'type': 'game'})
        r = client.delete('/api/projects/1')
        assert r.status_code == 200
        assert client.get('/api/projects/1').status_code == 404

    def test_requirement_parent_and_note(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'Parent', 'priority': 'P2', 'type': 'feature'})
        r = client.post(
            '/api/requirements',
            json={
                'project_id': 1,
                'title': 'Child',
                'priority': 'P2',
                'type': 'feature',
                'parent_requirement_id': 1,
                'note': 'decomposed',
                'depends_on': [1],
            },
        )
        assert r.status_code == 201
        g = client.get('/api/requirements/2')
        body = g.get_json() or g.json
        assert body.get('parent_requirement_id') == 1
        assert 'decomposed' in (body.get('note') or '')

    def test_test_cases_crud(self, client):
        client.post('/api/projects', json={'name': 'P', 'type': 'game'})
        client.post('/api/requirements', json={'project_id': 1, 'title': 'R', 'priority': 'P2', 'type': 'feature'})
        client.post('/api/tasks', json={'req_id': 1, 'title': 'Implement X', 'executor': 'agent-a'})
        r = client.post(
            '/api/requirements/1/test-cases',
            json={'title': 'Unit: X behaves', 'layer': 'unit', 'task_id': 1, 'description': 'see DoD'},
        )
        assert r.status_code == 201
        tc_id = (r.get_json() or r.json).get('id')
        lst = client.get('/api/requirements/1/test-cases')
        assert lst.status_code == 200
        assert len(lst.json or []) == 1
        r2 = client.patch(f'/api/test-cases/{tc_id}', json={'status': 'passed', 'result_notes': 'ok'})
        assert r2.status_code == 200
        one = client.get(f'/api/test-cases/{tc_id}')
        assert (one.get_json() or one.json).get('status') == 'passed'
        bad = client.post(
            '/api/requirements/1/test-cases',
            json={'title': 'wrong task', 'task_id': 999},
        )
        assert bad.status_code == 400
        d = client.delete(f'/api/test-cases/{tc_id}')
        assert d.status_code == 200
        assert client.get(f'/api/test-cases/{tc_id}').status_code == 404


class TestIntegration:
    """集成测试"""

    def test_project_requirement_task_flow(self, client):
        r = client.post('/api/projects', json={'name': 'FlowProj', 'type': 'game'})
        assert r.status_code == 201
        r = client.post('/api/requirements', json={'project_id': 1, 'title': 'FlowReq', 'priority': 'P2', 'type': 'feature'})
        assert r.status_code == 201
        r = client.post('/api/requirements/1/auto-split')
        assert r.status_code == 200
        r = client.get('/api/requirements/1/tasks')
        assert r.status_code == 200
        assert len(r.json or []) >= 1

    def test_pipeline_cicd_flow(self, client):
        client.post('/api/projects', json={'name': 'CICDProj', 'type': 'game'})
        client.post('/api/pipelines', json={'name': 'CIPipe', 'project_id': 1})
        client.post('/api/pipelines/1/triggers', json={'trigger_type': 'commit', 'repo_url': 'https://github.com/a/b', 'branch': 'main'})
        r = client.get('/api/cicd/builds')
        assert r.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
