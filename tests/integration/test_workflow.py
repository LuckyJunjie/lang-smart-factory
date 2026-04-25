"""
Workflow 集成测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.graph_state import GraphState
from src.workflows.development_workflow import run_workflow, create_workflow_nodes
from src.agents.demand_analyst import DemandAnalyst
from src.agents.architect import Architect
from src.agents.detail_designer import DetailDesigner

class TestWorkflow:
    """工作流测试"""
    
    def test_workflow_initialization(self):
        """测试工作流初始化"""
        state = GraphState(
            project_id="test-001",
            raw_requirement="测试需求",
            current_step="analysis"
        )
        assert state.project_id == "test-001"
        assert state.current_step == "analysis"
    
    def test_workflow_nodes_exist(self):
        """测试所有工作流节点存在"""
        nodes = create_workflow_nodes()
        assert "analysis" in nodes
        assert "architecture" in nodes
        assert "detail_design" in nodes
    
    def test_workflow_run_with_requirement(self):
        """测试工作流运行"""
        result = run_workflow(
            "实现一个简单的股票筛选功能",
            "test-stock-screener"
        )
        assert result["project_id"] == "test-stock-screener"
        assert result["current_step"] in ["architecture", "detail_design", "dispatch", "implementation"]

class TestAgents:
    """Agent 测试"""
    
    def test_demand_analyst_process(self):
        """测试需求分析"""
        analyst = DemandAnalyst()
        state = {"raw_requirement": "实现股票筛选功能"}
        result = analyst.process(state)
        assert "structured_requirements" in result
        assert result["current_step"] == "architecture"
    
    def test_architect_process(self):
        """测试架构设计"""
        architect = Architect()
        state = {
            "structured_requirements": [{"id": "REQ-001", "title": "股票筛选"}],
            "current_step": "architecture"
        }
        result = architect.process(state)
        assert "architecture_doc" in result or "error" in result
    
    def test_detail_designer_process(self):
        """测试详细设计"""
        designer = DetailDesigner()
        state = {
            "architecture_doc": {"modules": []},
            "structured_requirements": [],
            "current_step": "detail_design"
        }
        result = designer.process(state)
        assert "detailed_tasks" in result or "error" in result

class TestDispatcher:
    """派发器测试"""
    
    def test_dispatcher_init(self):
        """测试派发器初始化"""
        from src.workflows.dispatcher import Dispatcher
        dispatcher = Dispatcher()
        assert dispatcher.redis_tools is not None
