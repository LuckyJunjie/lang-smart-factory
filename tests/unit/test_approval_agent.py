"""
Approval Agent 单元测试
"""
import pytest
import sys
import os

# Fix path
_test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if _test_dir not in sys.path:
    sys.path.insert(0, _test_dir)

from src.agents.approval_agent import HumanApprovalAgent

class TestApprovalAgent:
    """审批 Agent 测试"""
    
    def test_agent_init(self):
        agent = HumanApprovalAgent()
        assert agent.name == "HumanApproval"
    
    def test_request_approval(self):
        agent = HumanApprovalAgent()
        state = {"project_id": "test-001", "current_step": "testing"}
        result = agent.request_approval(state)
        assert result["approval_status"] == "pending"
    
    def test_approve(self):
        agent = HumanApprovalAgent()
        state = {"project_id": "test-001"}
        result = agent.process_approval(state, approved=True, comment="LGTM")
        assert result["approval_status"] == "approved"
    
    def test_reject(self):
        agent = HumanApprovalAgent()
        state = {"project_id": "test-001"}
        result = agent.process_approval(state, approved=False, comment="需要修改")
        assert result["approval_status"] == "rejected"
