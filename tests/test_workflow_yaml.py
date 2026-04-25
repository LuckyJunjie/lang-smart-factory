"""Validate the canonical OpenClaw development workflow YAML (single document)."""

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / "openclaw-knowledge" / "workflows" / "OPENCLAW_DEVELOPMENT_FLOW.yaml"


class WorkflowYamlTests(unittest.TestCase):
    def test_workflow_yaml_loads_as_single_mapping(self) -> None:
        try:
            import yaml  # type: ignore
        except ImportError:
            self.skipTest("PyYAML not installed (pip install pyyaml)")

        raw = WORKFLOW.read_text(encoding="utf-8")
        docs = list(yaml.safe_load_all(raw))
        self.assertEqual(
            len(docs),
            1,
            "Expected exactly one YAML document in OPENCLAW_DEVELOPMENT_FLOW.yaml",
        )
        data = docs[0]
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("version"), "3.0")
        self.assertIn("entity_codes", data)
        self.assertIn("role_skill_policy", data)
        self.assertIn("environment_bootstrap", data)
        self.assertIn("redis", data)
        self.assertIn("schedule", data)
        self.assertIn("api", data)
        rsp = data.get("role_skill_policy") or {}
        for team in ("tesla", "newton"):
            skills = (rsp.get(team) or {}).get("required_skills") or []
            self.assertIn(
                "develop_requirement",
                skills,
                msg=f"{team} must list develop_requirement alongside test work",
            )

    def test_workflow_file_exists(self) -> None:
        self.assertTrue(WORKFLOW.is_file(), msg=str(WORKFLOW))


if __name__ == "__main__":
    unittest.main()
