import json
import os
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Optional


# Make `server.py` importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core", "api"))
import server as srv  # noqa: E402


class SmartFactoryAPITestCase(unittest.TestCase):
    def setUp(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db_path = path
        srv.DATABASE = path
        srv.init_db()
        self.client = srv.app.test_client()

    def tearDown(self) -> None:
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def _post_json(self, url: str, payload: Dict[str, Any], expected_status: Optional[int] = None):
        resp = self.client.post(url, json=payload)
        if expected_status is not None:
            self.assertEqual(resp.status_code, expected_status, msg=resp.get_data(as_text=True))
        return resp

    def _get_json(self, url: str, expected_status: Optional[int] = None):
        resp = self.client.get(url)
        if expected_status is not None:
            self.assertEqual(resp.status_code, expected_status, msg=resp.get_data(as_text=True))
        return resp

    def _patch_json(self, url: str, payload: Dict[str, Any], expected_status: Optional[int] = None):
        resp = self.client.patch(url, json=payload)
        if expected_status is not None:
            self.assertEqual(resp.status_code, expected_status, msg=resp.get_data(as_text=True))
        return resp

    def create_project(self, name="P", type="game", description="") -> int:
        resp = self._post_json(
            "/api/projects",
            {"name": name, "type": type, "description": description},
            expected_status=201,
        )
        data = resp.get_json() or resp.json
        return int(data["id"])

    def create_requirement(
        self,
        project_id: int,
        title="R",
        priority="P2",
        type="feature",
        extra: Optional[Dict[str, Any]] = None,
        expected_status: int = 201,
    ) -> int:
        payload = {"project_id": project_id, "title": title, "priority": priority, "type": type, "description": ""}
        if extra:
            payload.update(extra)
        resp = self._post_json("/api/requirements", payload, expected_status=expected_status)
        data = resp.get_json() or resp.json
        return int(data["id"])

    def get_requirement(self, rid: int) -> dict:
        resp = self._get_json(f"/api/requirements/{rid}", expected_status=200)
        data = resp.get_json() or resp.json
        return data

    def create_task(self, req_id: int, title="T", executor: str = "") -> int:
        resp = self._post_json(
            "/api/tasks",
            {"req_id": req_id, "title": title, "executor": executor, "description": ""},
            expected_status=201,
        )
        data = resp.get_json() or resp.json
        return int(data["id"])

    def list_requirement_tasks(self, req_id: int) -> List[Dict[str, Any]]:
        resp = self._get_json(f"/api/requirements/{req_id}/tasks", expected_status=200)
        data = resp.get_json() or resp.json
        return data or []


class TestRequirementsFlow(unittest.TestCase):
    def setUp(self) -> None:
        self.case = SmartFactoryAPITestCase()
        self.case.setUp()
        self.client = self.case.client

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_assign_requires_dependencies(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        dep_id = case.create_requirement(pid, title="Dep", type="feature")
        rid = case.create_requirement(pid, title="Main", type="feature")

        # Set B.depends_on = [A.id] but keep A.status=new, so assign should fail.
        case._patch_json(f"/api/requirements/{rid}", {"depends_on": [dep_id]}, expected_status=200)
        resp = case._post_json(f"/api/requirements/{rid}/assign", {"assigned_team": "jarvis"})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json() or resp.json
        self.assertIn("Cannot assign", str(data.get("error") or data))

    def test_take_requires_agent_and_sets_progress_step(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")

        # Missing assigned_agent -> 400
        resp = case._post_json(f"/api/requirements/{rid}/take", {"assigned_team": "jarvis"}, expected_status=400)
        data = resp.get_json() or resp.json
        self.assertIn("assigned_team", str(data.get("error") or data))

        # Provide both -> in_progress + step=analyse
        case._post_json(
            f"/api/requirements/{rid}/take",
            {"assigned_team": "jarvis", "assigned_agent": "athena"},
            expected_status=200,
        )
        got = case.get_requirement(rid)
        self.assertEqual(got["status"], "in_progress")
        self.assertEqual(got["step"], "analyse")


class TestTasksAndStatusReport(unittest.TestCase):
    def setUp(self) -> None:
        self.case = SmartFactoryAPITestCase()
        self.case.setUp()

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_patch_task_sets_completed_at(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")
        tid = case.create_task(rid, title="T1", executor="dev1")

        resp = case._patch_json(f"/api/tasks/{tid}", {"status": "done"}, expected_status=200)
        self.assertEqual(resp.get_json() or resp.json, {"success": True})

        got = case.client.get(f"/api/tasks/{tid}")
        self.assertEqual(got.status_code, 200)
        data = got.get_json() or got.json
        self.assertIn("completed_at", data)
        self.assertIsNotNone(data["completed_at"])

    def test_status_report_syncs_task_fields(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")
        tid = case.create_task(rid, title="T1", executor="dev1")

        # Submit team status report with task sync payload
        case._post_json(
            f"/api/teams/jarvis/status-report",
            {
                "reporter_agent": "jarvis",
                "payload": {
                    "requirement_id": rid,
                    "progress_percent": 50,
                    "tasks": [
                        {
                            "id": tid,
                            "status": "in_progress",
                            "executor": "dev2",
                            "risk": "medium",
                            "blocker": "none",
                            "next_step_task_id": None,
                        }
                    ],
                },
            },
            expected_status=200,
        )

        tasks = case.list_requirement_tasks(rid)
        self.assertEqual(len(tasks), 1)
        t = tasks[0]
        self.assertEqual(t["id"], tid)
        self.assertEqual(t["status"], "in_progress")
        self.assertEqual(t["executor"], "dev2")
        self.assertEqual(t["risk"], "medium")
        self.assertEqual(t["blocker"], "none")


class TestDiscussionAndMeetings(unittest.TestCase):
    def setUp(self) -> None:
        self.case = SmartFactoryAPITestCase()
        self.case.setUp()

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_discussion_blockage_lifecycle(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")
        tid = case.create_task(rid, title="T1", executor="dev1")

        r = case._post_json(
            "/api/discussion/blockage",
            {
                "team": "jarvis",
                "requirement_id": rid,
                "task_id": tid,
                "reason": "waiting for dependency",
                "options": {"attempts": 1},
                "level": "L1",
            },
            expected_status=201,
        )
        data = r.get_json() or r.json
        bid = int(data["id"])

        r = case._get_json("/api/discussion/blockages?status=pending", expected_status=200)
        blockages = r.get_json() or r.json
        self.assertTrue(any(x.get("id") == bid and x.get("status") == "pending" for x in blockages))

        case._patch_json(
            f"/api/discussion/blockage/{bid}",
            {"status": "resolved", "decision": "reassign later"},
            expected_status=200,
        )

        r = case._get_json("/api/discussion/blockages?status=resolved", expected_status=200)
        blockages = r.get_json() or r.json
        self.assertTrue(any(x.get("id") == bid and x.get("status") == "resolved" for x in blockages))

    def test_meeting_inputs_and_finalize_host_guard(self):
        case = self.case
        # Meeting: create -> submit inputs -> GET exclude_self -> finalize guard -> finalize success
        case.create_project(name="P1", type="game")
        participants = [
            {"agent_id": "hera", "role_label": "host", "contribute_focus": "主持并汇总"},
            {"agent_id": "athena", "role_label": "architect", "contribute_focus": "技术方案分析"},
        ]
        r = case._post_json(
            "/api/meetings",
            {
                "topic": "阻塞会诊",
                "problem_to_solve": "确认处理方案",
                "host_agent": "hera",
                "initiated_by_agent": "hera",
                "participants": participants,
            },
            expected_status=201,
        )
        mid = int((r.get_json() or r.json)["meeting_id"])

        # Submit hera input
        case._post_json(
            f"/api/meetings/{mid}/inputs",
            {"agent_id": "hera", "analysis": "hera analysis", "comments": "hera comments"},
            expected_status=201,
        )
        # Submit athena input
        case._post_json(
            f"/api/meetings/{mid}/inputs",
            {"agent_id": "athena", "analysis": "athena analysis", "comments": "athena comments"},
            expected_status=201,
        )

        # Exclude self: asking as athena should return only hera inputs.
        r = case._get_json(
            f"/api/meetings/{mid}/inputs?agent=athena&exclude_self=1",
            expected_status=200,
        )
        data = r.get_json() or r.json
        inputs = data.get("inputs") or []
        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0]["agent_id"], "hera")

        # Host guard: wrong host_agent should fail
        r = case._post_json(
            f"/api/meetings/{mid}/finalize",
            {
                "host_agent": "not-host",
                "conclusion_summary": "Concluded",
                "requirements": [],
            },
            expected_status=403,
        )
        self.assertIn("Only meeting host can finalize", str(r.get_json() or r.json))

        # Finalize success: host finalizes and creates requirements
        r = case._post_json(
            f"/api/meetings/{mid}/finalize",
            {
                "host_agent": "hera",
                "conclusion_summary": "Concluded",
                "conclusion_decision": json.dumps({"decision": "ok"}),
                "requirements": [
                    {
                        "project_id": 1,
                        "title": "New requirement from meeting",
                        "description": "desc",
                        "type": "feature",
                        "priority": "P2",
                        "assigned_team": "jarvis",
                        "assigned_agent": "athena",
                    }
                ],
            },
            expected_status=201,
        )
        data = r.get_json() or r.json
        self.assertEqual(data.get("status"), "concluded")

        # Requirement should be visible to assigned_team filter
        r = case._get_json("/api/requirements?assigned_team=jarvis", expected_status=200)
        reqs = r.get_json() or r.json
        self.assertTrue(any(x.get("title") == "New requirement from meeting" for x in reqs))


class TestValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.case = SmartFactoryAPITestCase()
        self.case.setUp()

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_work_log_validation(self):
        case = self.case
        r = case._post_json("/api/work-log", {"role_or_team": "vanguard", "task_name": ""}, expected_status=400)
        self.assertIn("role_or_team", str(r.get_json() or r.json))


class TestMoreAPIs(unittest.TestCase):
    def setUp(self) -> None:
        self.case = SmartFactoryAPITestCase()
        self.case.setUp()

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_auto_split_creates_expected_task_count_for_feature(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="Feature X", type="feature")

        r = case._post_json(f"/api/requirements/{rid}/auto-split", {}, expected_status=200)
        data = r.get_json() or r.json
        created = data.get("created_tasks") or []
        # feature templates in server: 4 stages
        self.assertEqual(len(created), 4)

        tasks = case.list_requirement_tasks(rid)
        self.assertEqual(len(tasks), 4)
        self.assertTrue(all(t.get("status") == "todo" for t in tasks))

    def test_assign_in_progress_only_allows_tesla(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")

        # Take the requirement -> status becomes in_progress
        case._post_json(
            f"/api/requirements/{rid}/take",
            {"assigned_team": "jarvis", "assigned_agent": "athena"},
            expected_status=200,
        )

        # Re-assign to jarvis again should fail (only handoff to tesla allowed)
        r = case._post_json(f"/api/requirements/{rid}/assign", {"assigned_team": "jarvis"}, expected_status=None)
        self.assertEqual(r.status_code, 400)

    def test_task_detail_report_round_trip(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")
        tid = case.create_task(rid, title="T1", executor="dev1")

        case._post_json(
            "/api/teams/jarvis/task-detail",
            {
                "requirement_id": rid,
                "task_id": tid,
                "detail_type": "analysis",
                "content": "analysis text",
            },
            expected_status=201,
        )

        r = case._get_json(f"/api/teams/jarvis/task-details?requirement_id={rid}", expected_status=200)
        details = r.get_json() or r.json
        self.assertTrue(any(d.get("task_id") == tid and d.get("detail_type") == "analysis" for d in details))

    def test_blockage_patch_requires_status_or_decision(self):
        case = self.case
        pid = case.create_project(name="P1", type="game")
        rid = case.create_requirement(pid, title="R1", type="feature")

        r = case._post_json(
            "/api/discussion/blockage",
            {"team": "jarvis", "requirement_id": rid, "reason": "x"},
            expected_status=201,
        )
        bid = int((r.get_json() or r.json)["id"])
        r2 = case._patch_json(f"/api/discussion/blockage/{bid}", {}, expected_status=None)
        self.assertEqual(r2.status_code, 400)

    def test_teams_online_and_machine_status_round_trip(self):
        case = self.case
        # machine mapping uses machines.team and machines.status=online; but table can be empty.
        # We'll just ensure report -> get endpoints work.
        r = case._post_json(
            "/api/teams/jarvis/machine-status",
            {"payload": {"cpu": "10%"}, "reporter_agent": "jarvis"},
            expected_status=200,
        )
        self.assertEqual((r.get_json() or r.json).get("team"), "jarvis")

        r = case._get_json("/api/teams/jarvis/machine-status?limit=5", expected_status=200)
        rows = r.get_json() or r.json
        self.assertTrue(len(rows) >= 1)

        # status-report also marks "active" teams; validate summary endpoint returns jarvis key
        case._post_json(
            "/api/teams/jarvis/status-report",
            {"payload": {"requirement_id": 1, "progress_percent": 0, "tasks": []}, "reporter_agent": "jarvis"},
            expected_status=200,
        )
        r = case._get_json("/api/teams/online", expected_status=200)
        data = r.get_json() or r.json
        self.assertIn("jarvis", data.get("teams") or [])


if __name__ == "__main__":
    unittest.main()

