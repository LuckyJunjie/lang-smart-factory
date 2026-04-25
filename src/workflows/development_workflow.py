"""
LangFlow Factory - Development Workflow
"""
from typing import Dict
from ..agents.demand_analyst import DemandAnalyst
from ..agents.architect import Architect
from ..agents.detail_designer import DetailDesigner

def analysis_node(state: Dict) -> Dict:
    """需求分析节点"""
    analyst = DemandAnalyst()
    return analyst.process(state)

def architecture_node(state: Dict) -> Dict:
    """架构设计节点"""
    architect = Architect()
    return architect.process(state)

def detail_design_node(state: Dict) -> Dict:
    """详细设计节点"""
    designer = DetailDesigner()
    return designer.process(state)

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
    max_iterations = 10
    iterations = 0
    
    while current in nodes and current not in ["dispatch", "implementation", "testing", "acceptance", "release"] and iterations < max_iterations:
        state_dict = nodes[current](state_dict)
        iterations += 1
        # 根据当前步骤确定下一步
        if state_dict.get("current_step"):
            current = state_dict["current_step"]
        else:
            break
    
    return state_dict

def get_next_node(current_step: str) -> str:
    """获取下一步节点"""
    flow = {
        "analysis": "architecture",
        "architecture": "detail_design",
        "detail_design": "dispatch",
        "dispatch": "implementation",
        "implementation": "testing",
        "testing": "acceptance",
        "acceptance": "release",
        "release": None
    }
    return flow.get(current_step)
