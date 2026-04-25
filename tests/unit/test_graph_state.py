"""
GraphState 单元测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.graph_state import GraphState

class TestGraphState:
    """GraphState 测试"""
    
    def test_init_default_state(self):
        """测试默认初始化"""
        state = GraphState()
        assert state.project_id == ""
        assert state.current_step == "trigger"
        assert state.approval_status == "pending"
        assert state.structured_requirements == []
        assert state.detailed_tasks == []
        assert state.execution_trace == []
    
    def test_init_with_values(self):
        """测试带值初始化"""
        state = GraphState(
            project_id="test-001",
            requirement_id="req-001",
            current_step="analysis",
            raw_requirement="测试需求"
        )
        assert state.project_id == "test-001"
        assert state.current_step == "analysis"
        assert state.raw_requirement == "测试需求"
    
    def test_add_trace(self):
        """测试添加追踪"""
        state = GraphState(project_id="test-001")
        initial_count = len(state.execution_trace)
        
        state.add_trace("analysis", "started", {"key": "value"})
        
        assert len(state.execution_trace) == initial_count + 1
        assert state.execution_trace[-1]["step"] == "analysis"
        assert state.execution_trace[-1]["action"] == "started"
        assert state.execution_trace[-1]["data"] == {"key": "value"}
    
    def test_state_update(self):
        """测试状态更新"""
        state = GraphState()
        
        state.structured_requirements = [{"id": "REQ-001", "title": "Test"}]
        state.current_step = "architecture"
        
        assert len(state.structured_requirements) == 1
        assert state.current_step == "architecture"
    
    def test_to_dict(self):
        """测试字典转换"""
        state = GraphState(project_id="test-001", raw_requirement="Test requirement")
        state_dict = state.to_dict()
        
        assert state_dict["project_id"] == "test-001"
        assert state_dict["raw_requirement"] == "Test requirement"
        assert "created_at" in state_dict
        assert "updated_at" in state_dict
