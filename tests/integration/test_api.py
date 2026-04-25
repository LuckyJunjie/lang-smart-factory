"""
API 集成测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class TestAPI:
    """API 测试"""
    
    def test_api_server_import(self):
        """测试 API Server 可导入"""
        from api_server import app
        assert app is not None
    
    def test_health_endpoint_structure(self):
        """测试健康检查端点结构"""
        from api_server import app
        with app.test_client() as client:
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert "service" in data
    
    def test_nodes_endpoint(self):
        """测试节点列表端点"""
        from api_server import app
        with app.test_client() as client:
            response = client.get("/api/v1/nodes")
            assert response.status_code == 200
            data = response.get_json()
            assert "nodes" in data
            assert len(data["nodes"]) >= 3
    
    def test_run_workflow_missing_requirement(self):
        """测试缺少需求文本的错误处理"""
        from api_server import app
        with app.test_client() as client:
            response = client.post("/api/v1/workflow/run", json={})
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
    
    def test_run_workflow_with_requirement(self):
        """测试带需求文本的工作流运行"""
        from api_server import app
        with app.test_client() as client:
            response = client.post("/api/v1/workflow/run", json={
                "requirement": "实现股票筛选功能",
                "project_id": "test-api-001"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "completed"
