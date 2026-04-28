"""
LangFlow Factory - Development Workflow
完整的 LangGraph StateGraph 工作流，包含所有节点
"""
from typing import Dict, Literal, Optional
import json
import time
import redis

# LangGraph imports (optional, gracefully degrade if not available)
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from ..agents.demand_analyst import DemandAnalyst
from ..agents.architect import Architect
from ..agents.detail_designer import DetailDesigner
from ..graph_state import GraphState


# =============================================================================
# Node Functions
# =============================================================================

def analysis_node(state: Dict) -> Dict:
    """需求分析节点 - DemandAnalyst"""
    analyst = DemandAnalyst()
    result = analyst.process(state)
    result["current_step"] = "architecture"
    return result


def architecture_node(state: Dict) -> Dict:
    """架构设计节点 - Architect"""
    architect = Architect()
    result = architect.process(state)
    result["current_step"] = "detail_design"
    return result


def detail_design_node(state: Dict) -> Dict:
    """详细设计节点 - DetailDesigner"""
    designer = DetailDesigner()
    result = designer.process(state)
    result["current_step"] = "dispatch"
    return result


def dispatch_node(state: Dict) -> Dict:
    """
    Dispatch 节点 - 将详细任务发送到 Redis Stream
    
    遍历 detailed_tasks，为每个任务创建 task_id，
    然后 XADD 到 smartfactory:stream:tasks
    """
    r = redis.from_url("redis://localhost:6379", decode_responses=True)
    stream_key = "smartfactory:stream:tasks"
    
    detailed_tasks = state.get("detailed_tasks", [])
    if not detailed_tasks:
        detailed_tasks = [{"id": "task_1", "title": "Default Task", "requirements": state.get("raw_requirement", "")}]
    
    task_ids = []
    for i, task in enumerate(detailed_tasks):
        task_id = task.get("id", f"task_{i+1}")
        task_ids.append(task_id)
        
        # 创建任务消息
        task_data = {
            "task_id": task_id,
            "task": {
                "id": task_id,
                "title": task.get("title", f"Task {i+1}"),
                "requirements": task.get("requirements", task.get("description", "")),
                "project_id": state.get("project_id", "default"),
            }
        }
        
        # 发布到 Redis Stream
        msg_id = r.xadd(stream_key, {"data": json.dumps(task_data)})
        print(f"[Dispatch] Published task {task_id} -> {msg_id}")
    
    state["dispatched_tasks"] = task_ids
    state["dispatch_count"] = len(task_ids)
    state["current_step"] = "implementation"
    return state


def implementation_node(state: Dict) -> Dict:
    """
    Implementation 节点 - 等待 Worker 执行完成
    
    轮询 smartfactory:stream:results，直到所有任务完成
    """
    r = redis.from_url("redis://localhost:6379", decode_responses=True)
    results_key = "smartfactory:stream:results"
    tasks_key = "smartfactory:stream:tasks"
    
    dispatched = state.get("dispatched_tasks", [])
    if not dispatched:
        state["current_step"] = "testing"
        return state
    
    completed = []
    max_wait_seconds = 300  # 最多等待5分钟
    start_time = time.time()
    
    print(f"[Implementation] Waiting for {len(dispatched)} tasks to complete...")
    
    while len(completed) < len(dispatched):
        # 检查超时
        if time.time() - start_time > max_wait_seconds:
            print(f"[Implementation] Timeout after {max_wait_seconds}s")
            break
        
        # 读取 results
        results = r.xrange(results_key, "-", "+", count=10)
        for msg_id, data in results:
            try:
                result_data = json.loads(data["data"])
                task_id = result_data.get("task_id") or result_data.get("task", {}).get("id")
                if task_id and task_id in dispatched and task_id not in completed:
                    completed.append(task_id)
                    print(f"[Implementation] Task {task_id} completed: {result_data.get('status', 'unknown')}")
                    # ACK 原始任务
                    r.xack(tasks_key, "newton", msg_id)
            except (json.JSONDecodeError, KeyError):
                continue
        
        if len(completed) < len(dispatched):
            time.sleep(2)  # 每2秒轮询一次
    
    state["completed_tasks"] = completed
    state["implementation_results"] = {"completed": completed, "total": len(dispatched)}
    state["current_step"] = "testing"
    return state


def testing_node(state: Dict) -> Dict:
    """
    Testing 节点 - 汇总测试结果
    
    收集 Worker 返回的测试结果，生成测试报告
    """
    results = state.get("implementation_results", {})
    completed = results.get("completed", [])
    total = results.get("total", 0)
    
    # 简单的测试结果汇总
    test_results = {
        "total": total,
        "passed": len(completed),
        "failed": total - len(completed),
        "tasks": completed
    }
    
    state["test_results"] = test_results
    state["current_step"] = "acceptance"
    print(f"[Testing] {test_results['passed']}/{test_results['total']} tasks passed")
    return state


def acceptance_node(state: Dict) -> Dict:
    """
    Acceptance 节点 - 验收决策
    
    检查是否需要人工审批。如果测试全部通过，自动通过；
    否则标记需要人工决策。
    """
    test_results = state.get("test_results", {})
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    
    if failed > 0:
        # 有失败的任务，需要人工决策
        state["needs_human_approval"] = True
        state["approval_status"] = "pending"
        print(f"[Acceptance] {failed} tasks failed, needs human approval")
        # 在实际实现中，这里应该暂停等待人工输入
        # 目前先标记为 rejected
        state["approval_decision"] = "rejected"
    else:
        # 全部通过，自动接受
        state["needs_human_approval"] = False
        state["approval_status"] = "auto_approved"
        state["approval_decision"] = "approved"
        print(f"[Acceptance] All {passed} tasks passed, auto-approved")
    
    state["current_step"] = "release"
    return state


def release_node(state: Dict) -> Dict:
    """
    Release 节点 - 发布最终产物
    
    生成 release notes，更新项目状态，发送通知
    """
    project_id = state.get("project_id", "default")
    test_results = state.get("test_results", {})
    
    release_info = {
        "project_id": project_id,
        "status": "completed" if state.get("approval_decision") == "approved" else "rejected",
        "test_results": test_results,
        "completed_tasks": state.get("completed_tasks", []),
        "release_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    state["release_info"] = release_info
    state["current_step"] = "completed"
    print(f"[Release] Project {project_id} {release_info['status']}")
    return state


# =============================================================================
# Workflow Creation
# =============================================================================

def create_workflow_nodes() -> Dict[str, callable]:
    """创建工作流节点映射（用于简单模式）"""
    return {
        "analysis": analysis_node,
        "architecture": architecture_node,
        "detail_design": detail_design_node,
        "dispatch": dispatch_node,
        "implementation": implementation_node,
        "testing": testing_node,
        "acceptance": acceptance_node,
        "release": release_node,
    }


def get_next_node(current_step: str) -> Optional[str]:
    """获取下一步节点（用于简单模式）"""
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


def route_based_on_step(state: Dict) -> Literal["dispatch", "implementation", "testing", "acceptance", "release", "end"]:
    """LangGraph 条件路由函数"""
    step = state.get("current_step", "analysis")
    routes = {
        "analysis": "architecture",
        "architecture": "detail_design",
        "detail_design": "dispatch",
        "dispatch": "implementation",
        "implementation": "testing",
        "testing": "acceptance",
        "acceptance": "release",
        "release": "end",
    }
    return routes.get(step, "end")


def create_langgraph_workflow():
    """
    创建 LangGraph StateGraph 工作流
    
    使用 LangGraph 的条件路由连接所有节点
    """
    if not LANGGRAPH_AVAILABLE:
        print("[LangGraph] Not available, using simple workflow")
        return None
    
    # 定义节点
    nodes = [
        ("analysis", analysis_node),
        ("architecture", architecture_node),
        ("detail_design", detail_design_node),
        ("dispatch", dispatch_node),
        ("implementation", implementation_node),
        ("testing", testing_node),
        ("acceptance", acceptance_node),
        ("release", release_node),
    ]
    
    # 创建 StateGraph
    workflow = StateGraph(Dict)
    
    for name, func in nodes:
        workflow.add_node(name, func)
    
    # 设置入口点
    workflow.set_entry_point("analysis")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "analysis",
        route_based_on_step,
        {
            "architecture": "architecture",
            "detail_design": "detail_design",
            "dispatch": "dispatch",
            "implementation": "implementation",
            "testing": "testing",
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "architecture",
        route_based_on_step,
        {
            "detail_design": "detail_design",
            "dispatch": "dispatch",
            "implementation": "implementation",
            "testing": "testing",
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "detail_design",
        route_based_on_step,
        {
            "dispatch": "dispatch",
            "implementation": "implementation",
            "testing": "testing",
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "dispatch",
        route_based_on_step,
        {
            "implementation": "implementation",
            "testing": "testing",
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "implementation",
        route_based_on_step,
        {
            "testing": "testing",
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "testing",
        route_based_on_step,
        {
            "acceptance": "acceptance",
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_conditional_edges(
        "acceptance",
        route_based_on_step,
        {
            "release": "release",
            "end": END,
        }
    )
    
    workflow.add_edge("release", END)
    
    return workflow.compile()


# =============================================================================
# Main Entry Point
# =============================================================================

def run_workflow(requirement_text: str, project_id: str = "default", use_langgraph: bool = False) -> Dict:
    """
    运行工作流
    
    Args:
        requirement_text: 需求文本
        project_id: 项目 ID
        use_langgraph: 是否使用 LangGraph（如果可用）
    
    Returns:
        最终状态字典
    """
    # 初始化状态
    state = GraphState(
        project_id=project_id,
        raw_requirement=requirement_text,
        current_step="analysis"
    )
    state_dict = state.to_dict()
    
    # 尝试使用 LangGraph
    if use_langgraph and LANGGRAPH_AVAILABLE:
        graph = create_langgraph_workflow()
        if graph:
            print("[Workflow] Using LangGraph StateGraph")
            result = graph.invoke(state_dict)
            return result
    
    # 回退到简单模式
    print("[Workflow] Using simple sequential workflow")
    nodes = create_workflow_nodes()
    current = "analysis"
    max_iterations = 20
    iterations = 0
    
    while current in nodes and iterations < max_iterations:
        state_dict = nodes[current](state_dict)
        iterations += 1
        print(f"[Workflow] Executed {current}, next: {state_dict.get('current_step')}")
        
        if state_dict.get("current_step") == "completed":
            break
        
        next_node = get_next_node(state_dict.get("current_step", ""))
        if not next_node:
            break
        current = next_node
    
    return state_dict


# =============================================================================
# CLI Usage Example
# =============================================================================

if __name__ == "__main__":
    # 测试工作流
    print("Testing workflow...")
    result = run_workflow("开发一个简单的计算器应用")
    print(f"\nFinal state: {result.get('current_step')}")
    print(f"Released: {result.get('release_info')}")
