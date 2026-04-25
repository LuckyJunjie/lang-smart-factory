"""
CI/CD Orchestrator 单元测试
"""
import pytest
import sys
import os

_test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if _test_dir not in sys.path:
    sys.path.insert(0, _test_dir)

class TestCICDOrchestrator:
    """CI/CD 编排测试"""
    
    def test_trigger_build(self):
        from src.agents.cicd_orchestrator import CICDOrchestrator
        orch = CICDOrchestrator()
        result = orch.trigger_build("test-project")
        assert "build_id" in result
        assert result["status"] == "triggered"
    
    def test_check_build_status(self):
        from src.agents.cicd_orchestrator import CICDOrchestrator
        orch = CICDOrchestrator()
        result = orch.check_build_status("build_001")
        assert "status" in result
        assert result["passed"] is True
    
    def test_create_release(self):
        from src.agents.cicd_orchestrator import CICDOrchestrator
        orch = CICDOrchestrator()
        result = orch.create_release("test-project", "v1.0.0")
        assert result["version"] == "v1.0.0"
        assert result["status"] == "published"
