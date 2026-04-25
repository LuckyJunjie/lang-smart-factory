"""
LangFlow Factory - Development Workflow
"""
from typing import Dict
from ..agents.demand_analyst import DemandAnalyst

def analysis_node(state: Dict) -> Dict:
    """需求分析节点"""
    analyst = DemandAnalyst()
    return analyst.process(state)

def architecture_node(state: Dict) -> Dict:
    """架构设计节点"""
    # TODO: 实现 Architect Agent
    state["current_step"] = "detail_design"
    state["architecture_doc"] = {
        "modules": [],
        "tech_stack": "Python + LangChain",
        "status": "placeholder"
    }
    return state

def detail_design_node(state: Dict) -> Dict:
    """详细设计节点"""
    # TODO: 实现 DetailDesigner Agent
    state["current_step"] = "dispatch"
    state["detailed_tasks"] = [
        {"id": "TASK-001", "title": "初始化项目", "status": "pending"}
    ]
    return state

def create_workflow_nodes():
    """创建工作流节点映射"""
    return {
        "analysis": analysis_node,
        "architecture": architecture_node,
        "detail_design": detail_design_node,
    }

def run_workflow(requirement_text: str, project_id: str = "default") -> Dict:
    """运行工作流"""
    from ..graph_state import GraphState
    
    # 初始化状态
    state = GraphState(
        project_id=project_id,
        raw_requirement=requirement_text,
        current_step="analysis"
    )
    state_dict = state.to_dict()
    
    # 执行节点链
    nodes = create_workflow_nodes()
    current = "analysis"
    
    while current in nodes and current != "dispatch":
        state_dict = nodes[current](state_dict)
        # 根据当前步骤确定下一步
        if state_dict.get("current_step"):
            current = state_dict["current_step"]
        else:
            break
    
    return state_dict
