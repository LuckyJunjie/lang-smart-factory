"""
Additional API tests against core/api/server.py (temp SQLite) to raise coverage on
query params, team summaries, CI webhook, meetings, and validation paths.
"""
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core", "api"))


@pytest.fixture
def app_and_db():
    import server as srv

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    srv.DATABASE = path
    srv.init_db()
    yield srv.app, path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client(app_and_db):
    app, _ = app_and_db
    return app.test_client()


class TestApiDiscovery:
    def test_api_index_lists_endpoints(self, client):
        r = client.get("/api")
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert "endpoints" in data
        paths = {e.get("path") for e in data["endpoints"]}
        assert "/api/requirements" in paths
        assert "/api/dashboard/risk-report" in paths


class TestRequirementsQueryParams:
    def test_list_requirements_filter_status_and_team(self, client):
        client.post("/api/projects", json={"name": "Q", "type": "tool"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "A", "priority": "P2", "type": "feature"},
        )
        client.post("/api/requirements/1/assign", json={"assigned_team": "jarvis"})
        r = client.get("/api/requirements?status=new&assigned_team=jarvis")
        assert r.status_code == 200
        rows = r.get_json() or r.json
        assert len(rows) == 1
        assert rows[0]["title"] == "A"

    def test_list_requirements_sort_created_asc(self, client):
        client.post("/api/projects", json={"name": "Q", "type": "tool"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "First", "priority": "P2", "type": "feature"},
        )
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "Second", "priority": "P2", "type": "feature"},
        )
        r = client.get("/api/requirements?sort=created_asc")
        assert r.status_code == 200
        titles = [x["title"] for x in (r.get_json() or r.json)]
        assert titles.index("First") < titles.index("Second")

    def test_assignable_excludes_unmet_dependencies(self, client):
        client.post("/api/projects", json={"name": "Q", "type": "tool"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "Dep", "priority": "P2", "type": "feature"},
        )
        client.post(
            "/api/requirements",
            json={
                "project_id": 1,
                "title": "Blocked",
                "priority": "P2",
                "type": "feature",
                "depends_on": [1],
            },
        )
        r = client.get("/api/requirements?assignable=1")
        assert r.status_code == 200
        titles = {x["title"] for x in (r.get_json() or r.json)}
        assert "Dep" in titles
        assert "Blocked" not in titles

        client.patch("/api/requirements/1", json={"status": "done"})
        r2 = client.get("/api/requirements?assignable=1")
        titles2 = {x["title"] for x in (r2.get_json() or r2.json)}
        assert "Blocked" in titles2


class TestAssignAndHandoff:
    def test_assign_after_dependency_done(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        dep = client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "Dep", "priority": "P2", "type": "feature"},
        ).get_json()["id"]
        main = client.post(
            "/api/requirements",
            json={
                "project_id": 1,
                "title": "Main",
                "priority": "P2",
                "type": "feature",
                "depends_on": [dep],
            },
        ).get_json()["id"]
        a = client.post(f"/api/requirements/{main}/assign", json={"assigned_team": "jarvis"})
        assert a.status_code == 400

        client.patch(f"/api/requirements/{dep}", json={"status": "done"})
        b = client.post(f"/api/requirements/{main}/assign", json={"assigned_team": "jarvis"})
        assert b.status_code == 200

    def test_assign_in_progress_to_tesla_handoff(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "R", "priority": "P2", "type": "feature"},
        )
        client.post(
            "/api/requirements/1/take",
            json={"assigned_team": "jarvis", "assigned_agent": "athena"},
        )
        r = client.post("/api/requirements/1/assign", json={"assigned_team": "tesla"})
        assert r.status_code == 200
        body = r.get_json() or r.json
        assert body.get("assigned_team") == "tesla"


class TestTeamAssignedRequirementsQuery:
    def test_assigned_requirements_query_param_requires_team(self, client):
        r = client.get("/api/teams/assigned-requirements")
        assert r.status_code == 400
        assert "team" in str(r.get_json() or r.json).lower()

    def test_assigned_requirements_query_param_matches_path_style(self, client):
        client.post("/api/projects", json={"name": "P", "type": "tool"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "X", "priority": "P2", "type": "feature"},
        )
        client.post("/api/requirements/1/assign", json={"assigned_team": "tesla"})
        r_path = client.get("/api/teams/tesla/assigned-requirements")
        r_q = client.get("/api/teams/assigned-requirements?team=tesla")
        assert r_path.status_code == r_q.status_code == 200
        assert (r_path.get_json() or r_path.json) == (r_q.get_json() or r_q.json)


class TestTeamSummariesAndReports:
    def test_status_report_get_and_summary(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "R", "priority": "P2", "type": "feature"},
        )
        client.post(
            "/api/teams/jarvis/status-report",
            json={
                "reporter_agent": "jarvis",
                "payload": {"requirement_id": 1, "progress_percent": 10, "tasks": []},
            },
        )
        r1 = client.get("/api/teams/jarvis/status-report?limit=5")
        assert r1.status_code == 200
        assert len(r1.get_json() or r1.json) >= 1
        r2 = client.get("/api/teams/status-report/summary")
        assert r2.status_code == 200
        teams = {row.get("team") for row in (r2.get_json() or r2.json)}
        assert "jarvis" in teams

    def test_machine_status_summary_endpoint(self, client):
        client.post(
            "/api/teams/jarvis/machine-status",
            json={"payload": {"cpu": "1%"}, "reporter_agent": "jarvis"},
        )
        r = client.get("/api/teams/machine-status/summary")
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert isinstance(data, list)
        assert any(row.get("team") == "jarvis" for row in data)

    def test_development_details_summary_endpoint(self, client):
        r = client.get("/api/teams/development-details/summary")
        assert r.status_code == 200
        assert isinstance(r.get_json() or r.json, list)

    def test_team_report_post_and_list(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "R", "priority": "P2", "type": "feature"},
        )
        p = client.post(
            "/api/teams/jarvis/report",
            json={
                "requirement_id": 1,
                "report_type": "development",
                "content": "Implemented feature X.",
            },
        )
        assert p.status_code == 201
        g = client.get("/api/teams/jarvis/reports?requirement_id=1&report_type=development")
        assert g.status_code == 200
        rows = g.get_json() or g.json
        assert len(rows) >= 1
        assert "Implemented" in (rows[0].get("content") or "")

    def test_task_detail_invalid_type_returns_400(self, client):
        r = client.post(
            "/api/teams/jarvis/task-detail",
            json={"detail_type": "wrong", "content": "x"},
        )
        assert r.status_code == 400


class TestWorkLog:
    def test_work_log_list_after_post(self, client):
        client.post(
            "/api/work-log",
            json={"role_or_team": "vanguard", "task_name": "dispatch", "task_output": "ok"},
        )
        r = client.get("/api/work-logs?role_or_team=vanguard&limit=10")
        assert r.status_code == 200
        rows = r.get_json() or r.json
        assert any(x.get("task_name") == "dispatch" for x in rows)


class TestToolsFilter:
    def test_list_tools_filter_by_type(self, client):
        client.post(
            "/api/tools",
            json={"name": "filter-tool-a", "type": "mcp", "path": "/x"},
        )
        client.post(
            "/api/tools",
            json={"name": "filter-tool-b", "type": "cli", "path": "/y"},
        )
        r = client.get("/api/tools?type=mcp")
        assert r.status_code == 200
        names = [t.get("name") for t in (r.get_json() or r.json)]
        assert "filter-tool-a" in names
        assert "filter-tool-b" not in names


class TestDashboardRisk:
    def test_risk_report_stuck_analyse(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "Stuck", "priority": "P2", "type": "feature"},
        )
        client.patch(
            "/api/requirements/1",
            json={
                "status": "in_progress",
                "step": "analyse",
                "progress_percent": 0,
                "assigned_team": "jarvis",
            },
        )
        r = client.get("/api/dashboard/risk-report")
        assert r.status_code == 200
        data = r.get_json() or r.json
        risks = data.get("risks") or []
        assert any(x.get("type") == "stuck_analyse" for x in risks)


class TestTestCasesValidation:
    def test_patch_test_case_rejects_foreign_task(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "R1", "priority": "P2", "type": "feature"},
        )
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "R2", "priority": "P2", "type": "feature"},
        )
        client.post("/api/tasks", json={"req_id": 1, "title": "T1", "executor": "a"})
        client.post("/api/tasks", json={"req_id": 2, "title": "T2", "executor": "b"})
        tc = client.post(
            "/api/requirements/1/test-cases",
            json={"title": "TC", "layer": "unit", "task_id": 1},
        )
        tc_id = (tc.get_json() or tc.json)["id"]
        bad = client.patch(f"/api/test-cases/{tc_id}", json={"task_id": 2})
        assert bad.status_code == 400


class TestAutoSplitVariants:
    def test_auto_split_bug_creates_three_tasks(self, client):
        client.post("/api/projects", json={"name": "P", "type": "game"})
        client.post(
            "/api/requirements",
            json={"project_id": 1, "title": "Crash", "priority": "P1", "type": "bug"},
        )
        r = client.post("/api/requirements/1/auto-split")
        assert r.status_code == 200
        created = (r.get_json() or r.json).get("created_tasks") or []
        assert len(created) == 3


class TestMeetingsExtras:
    def test_list_meetings_running(self, client):
        client.post(
            "/api/meetings",
            json={
                "topic": "T",
                "problem_to_solve": "P",
                "host_agent": "hera",
                "initiated_by_agent": "hera",
                "participants": [{"agent_id": "athena", "role_label": "dev"}],
            },
        )
        r = client.get("/api/meetings?status=running")
        assert r.status_code == 200
        assert len(r.get_json() or r.json) >= 1

    def test_meetings_for_agent_requires_query(self, client):
        r = client.get("/api/meetings/for-agent")
        assert r.status_code == 400

    def test_meetings_for_agent_lists_invited(self, client):
        client.post(
            "/api/meetings",
            json={
                "topic": "Sync",
                "problem_to_solve": "Q",
                "host_agent": "hera",
                "initiated_by_agent": "hera",
                "participants": [
                    {"agent_id": "hera", "role_label": "host"},
                    {"agent_id": "athena", "role_label": "arch"},
                ],
            },
        )
        r = client.get("/api/meetings/for-agent?agent=athena")
        assert r.status_code == 200
        payload = r.get_json() or r.json
        assert len(payload) >= 1
        assert any(m.get("topic") == "Sync" for m in payload)

    def test_delete_meeting_without_inputs(self, client):
        cresp = client.post(
            "/api/meetings",
            json={
                "topic": "Trash",
                "problem_to_solve": "x",
                "host_agent": "hera",
                "initiated_by_agent": "hera",
                "participants": [{"agent_id": "athena", "role_label": "x"}],
            },
        )
        mid = (cresp.get_json() or cresp.json)["meeting_id"]
        d = client.delete(f"/api/meetings/{mid}")
        assert d.status_code == 200
        assert client.get(f"/api/meetings/{mid}").status_code == 404


class TestGithubWebhookPost:
    def test_webhook_post_creates_build_when_trigger_matches(self, client):
        client.post("/api/projects", json={"name": "GHProj", "type": "tool"})
        client.post("/api/pipelines", json={"name": "Pipe", "project_id": 1})
        client.post(
            "/api/pipelines/1/triggers",
            json={
                "trigger_type": "commit",
                "repo_url": "https://github.com/acme/demo-repo",
                "branch": "main",
            },
        )
        body = {
            "ref": "refs/heads/main",
            "after": "abc123",
            "repository": {"html_url": "https://github.com/acme/demo-repo"},
            "commits": [{"message": "fix: thing"}],
        }
        r = client.post(
            "/api/webhook/github",
            data=json.dumps(body),
            content_type="application/json",
            headers={"X-GitHub-Event": "push"},
        )
        assert r.status_code == 200
        data = r.get_json() or r.json
        assert data.get("branch") == "main"
        triggered = data.get("builds_triggered") or []
        assert len(triggered) >= 1
        assert "build_id" in triggered[0]

        builds = client.get("/api/cicd/builds?pipeline_id=1")
        assert builds.status_code == 200
        blast = builds.get_json() or builds.json
        assert len(blast) >= 1


class TestFeishuVoiceValidation:
    def test_feishu_post_requires_text_or_webhook(self, client):
        r = client.post("/api/feishu/post", json={})
        assert r.status_code == 400
        body = r.get_json() or r.json
        assert "text" in str(body).lower() or "required" in str(body).lower()

    def test_voice_requires_audio_or_returns_error(self, client):
        r = client.post("/api/voice", data="")
        assert r.status_code in (400, 401)


class TestNotFoundCases:
    def test_patch_project_missing_returns_404(self, client):
        r = client.patch("/api/projects/99", json={"name": "nope"})
        assert r.status_code == 404

    def test_get_requirement_missing_returns_404(self, client):
        r = client.get("/api/requirements/999")
        assert r.status_code == 404
