"""
LangFlow Factory - GraphState 定义
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime

@dataclass
class GraphState:
    """LangGraph 状态机状态"""
    project_id: str = ""
    requirement_id: str = ""
    current_step: Literal[
        "trigger", "analysis", "architecture", 
        "detail_design", "dispatch", "implementation",
        "testing", "gameplay_eval", "acceptance", "release"
    ] = "trigger"
    
    # 输入/输出数据
    raw_requirement: str = ""
    structured_requirements: List[Dict] = field(default_factory=list)
    acceptance_criteria: List[Dict] = field(default_factory=list)
    
    architecture_doc: Dict = field(default_factory=dict)
    detailed_tasks: List[Dict] = field(default_factory=list)
    
    # 执行追踪
    artifacts: Dict[str, Any] = field(default_factory=dict)
    execution_trace: List[Dict] = field(default_factory=list)
    
    # 审批状态
    approval_status: str = "pending"  # pending, approved, rejected
    approval_comment: str = ""
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_trace(self, step: str, action: str, data: Any = None):
        """添加执行追踪"""
        self.execution_trace.append({
            "step": step,
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "requirement_id": self.requirement_id,
            "current_step": self.current_step,
            "raw_requirement": self.raw_requirement,
            "structured_requirements": self.structured_requirements,
            "acceptance_criteria": self.acceptance_criteria,
            "architecture_doc": self.architecture_doc,
            "detailed_tasks": self.detailed_tasks,
            "artifacts": self.artifacts,
            "execution_trace": self.execution_trace,
            "approval_status": self.approval_status,
            "approval_comment": self.approval_comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
