"""
LangFlow Factory - Human Approval Agent
人工审批 Agent
"""
from typing import Dict

class HumanApprovalAgent:
    """人工审批 Agent"""
    
    def __init__(self):
        self.name = "HumanApproval"
        self.feishu = None  # 初始化时设置
    
    def request_approval(self, state: Dict) -> Dict:
        """请求人工审批"""
        project_id = state.get("project_id", "unknown")
        
        # 发送飞书审批卡片
        self._send_approval_card(project_id, state.get("current_step"))
        
        state["approval_status"] = "pending"
        state["approval_requested_at"] = self._now()
        return state
    
    def process_approval(self, state: Dict, approved: bool, comment: str = "") -> Dict:
        """处理审批结果"""
        state["approval_status"] = "approved" if approved else "rejected"
        state["approval_comment"] = comment
        state["approval_processed_at"] = self._now()
        
        if approved:
            state["current_step"] = "release"
        else:
            state["current_step"] = "blocked"
        
        return state
    
    def _send_approval_card(self, project_id: str, step: str):
        """发送飞书审批卡片"""
        from ..tools.feishu_tools import FeishuNotifier
        notifier = FeishuNotifier()
        notifier.send_card(
            title="📋 需要人工审批",
            content=f"**项目:** {project_id}\n**步骤:** {step}\n\n请确认是否通过？",
            status="warning"
        )
    
    def _now(self):
        from datetime import datetime
        return datetime.now().isoformat()
