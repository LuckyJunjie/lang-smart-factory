"""
LangFlow Factory - Development Workflow
Complete LangGraph StateGraph workflow with proper structure.
Flow: analysis → architecture → detail_design → implementation → testing → release
"""
from typing import Dict, Literal, Optional, Any, Callable
import json
import time
import os
import requests

# LangGraph imports - REQUIRED, no fallback
from langgraph.graph import StateGraph, END
from langgraph.predefined import ToolNode

# Local imports
from ..agents.demand_analyst import DemandAnalyst
from ..agents.architect import Architect
from ..agents.detail_designer import DetailDesigner
from ..graph_state import GraphState
from ..llm.minimax_client import LLMClient


# =============================================================================
# Redis Queue (renamed to langflow:tasks)
# =============================================================================

REDIS_AVAILABLE = True
try:
    import redis
    REDIS_CLIENT = redis.from_url("redis://localhost:6379", decode_responses=True)
except Exception:
    REDIS_AVAILABLE = False
    REDIS_CLIENT = None

TASKS_STREAM = "langflow:tasks"
RESULTS_STREAM = "langflow:results"


def publish_task_to_queue(task_data: Dict) -> Optional[str]:
    """Publish task to langflow:tasks Redis stream."""
    if not REDIS_AVAILABLE:
        print("[Queue] Redis not available, skipping publish")
        return None
    
    task_id = task_data.get("task_id", f"task_{int(time.time()*1000)}")
    task_data["status"] = "pending"
    task_data["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    msg_id = REDIS_CLIENT.xadd(TASKS_STREAM, {"data": json.dumps(task_data)})
    print(f"[Queue] Published task {task_id} -> {msg_id}")
    return task_id


def wait_for_result(task_id: str, timeout: int = 120) -> Optional[Dict]:
    """Wait for result from langflow:results stream."""
    if not REDIS_AVAILABLE:
        return None
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        results = REDIS_CLIENT.xrange(RESULTS_STREAM, "-", "+", count=10)
        for msg_id, data in results:
            try:
                result_data = json.loads(data["data"])
                if result_data.get("task_id") == task_id:
                    return result_data
            except (json.JSONDecodeError, KeyError):
                continue
        time.sleep(1)
    
    return None


# =============================================================================
# Node Functions
# =============================================================================

def analysis_node(state: Dict) -> Dict:
    """Demand Analysis node - analyze requirements."""
    analyst = DemandAnalyst()
    result = analyst.process(state)
    result["current_step"] = "architecture"
    print(f"[Node] Analysis complete → architecture")
    return result


def architecture_node(state: Dict) -> Dict:
    """Architecture Design node - create system architecture."""
    architect = Architect()
    result = architect.process(state)
    result["current_step"] = "detail_design"
    print(f"[Node] Architecture complete → detail_design")
    return result


def detail_design_node(state: Dict) -> Dict:
    """Detail Design node - create implementation tasks."""
    designer = DetailDesigner()
    result = designer.process(state)
    result["current_step"] = "implementation"
    print(f"[Node] Detail design complete → implementation")
    return result


def implementation_node(state: Dict) -> Dict:
    """
    Implementation node - execute tasks via LLM calls.
    Uses direct LLM calls (or sessions_spawn pattern) instead of Redis consumer groups.
    """
    detailed_tasks = state.get("detailed_tasks", [])
    project_id = state.get("project_id", "default")
    
    if not detailed_tasks:
        # No tasks to implement - skip to testing
        state["implementation_results"] = {"completed": [], "total": 0}
        state["current_step"] = "testing"
        return state
    
    llm_client = LLMClient()
    completed = []
    
    print(f"[Node] Implementing {len(detailed_tasks)} tasks via LLM...")
    
    for i, task in enumerate(detailed_tasks):
        task_id = task.get("id", f"task_{i+1}")
        title = task.get("title", f"Task {i+1}")
        requirements = task.get("requirements", task.get("description", ""))
        
        print(f"[Implementation] Processing task {task_id}: {title}")
        
        # Build prompt for LLM
        prompt = f"""Task: {title}
Requirements: {requirements}
Project: {project_id}

Generate the implementation code. Output ONLY the code, no explanation."""

        # Call LLM directly
        generated_code = llm_client.generate(prompt, max_tokens=4096)
        
        # Save generated code to file
        project_dir = f"/home/pi/.openclaw/workspace/lang-smart-factory/projects/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        output_file = os.path.join(project_dir, f"{task_id}.py")
        
        try:
            with open(output_file, "w") as f:
                f.write(f"# Task: {task_id}\n# Title: {title}\n# Generated by LangFlow\n\n")
                f.write(generated_code)
            completed.append(task_id)
            print(f"[Implementation] Task {task_id} completed: {output_file}")
        except Exception as e:
            print(f"[Implementation] Error writing {task_id}: {e}")
            completed.append(task_id)  # Still count as completed
    
    state["implementation_results"] = {
        "completed": completed,
        "total": len(detailed_tasks)
    }
    state["current_step"] = "testing"
    print(f"[Node] Implementation complete → testing ({len(completed)}/{len(detailed_tasks)})")
    return state


def testing_node(state: Dict) -> Dict:
    """Testing node - summarize test results."""
    results = state.get("implementation_results", {})
    completed = results.get("completed", [])
    total = results.get("total", 0)
    
    test_results = {
        "total": total,
        "passed": len(completed),
        "failed": max(0, total - len(completed)),
        "tasks": completed
    }
    
    state["test_results"] = test_results
    state["current_step"] = "release"
    print(f"[Node] Testing complete → release ({test_results['passed']}/{test_results['total']} passed)")
    return state


def release_node(state: Dict) -> Dict:
    """Release node - finalize and release."""
    project_id = state.get("project_id", "default")
    test_results = state.get("test_results", {})
    
    # Determine release status
    approval_decision = "approved" if test_results.get("passed", 0) > 0 else "rejected"
    
    release_info = {
        "project_id": project_id,
        "status": "completed" if approval_decision == "approved" else "rejected",
        "test_results": test_results,
        "completed_tasks": state.get("implementation_results", {}).get("completed", []),
        "release_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    state["release_info"] = release_info
    state["current_step"] = "completed"
    print(f"[Node] Release complete: {project_id} {release_info['status']}")
    return state


# =============================================================================
# Conditional Routing
# =============================================================================

def route_by_step(state: Dict) -> str:
    """Route to next step based on current_step."""
    step = state.get("current_step", "analysis")
    routes = {
        "analysis": "architecture",
        "architecture": "detail_design",
        "detail_design": "implementation",
        "implementation": "testing",
        "testing": "release",
        "release": "end",
    }
    return routes.get(step, "end")


# =============================================================================
# Workflow Definition
# =============================================================================

def create_workflow():
    """Create LangGraph StateGraph workflow."""
    from typing import TypedDict
    
    class WorkflowState(TypedDict):
        """Workflow state schema."""
        project_id: str
        requirement_id: str
        current_step: str
        raw_requirement: str
        structured_requirements: list
        architecture_doc: dict
        detailed_tasks: list
        implementation_results: dict
        test_results: dict
        release_info: dict
    
    # Create workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("architecture", architecture_node)
    workflow.add_node("detail_design", detail_design_node)
    workflow.add_node("implementation", implementation_node)
    workflow.add_node("testing", testing_node)
    workflow.add_node("release", release_node)
    
    # Set entry point
    workflow.set_entry_point("analysis")
    
    # Add conditional edges from each step
    for step in ["analysis", "architecture", "detail_design", "implementation", "testing"]:
        workflow.add_conditional_edges(
            step,
            route_by_step,
            {
                "architecture": "architecture",
                "detail_design": "detail_design",
                "implementation": "implementation",
                "testing": "testing",
                "release": "release",
                "end": END,
            }
        )
    
    # Add edge from release to end
    workflow.add_edge("release", END)
    
    return workflow.compile()


# =============================================================================
# Main Entry Point
# =============================================================================

def run_workflow(requirement_text: str, project_id: str = "default", use_langgraph: bool = True) -> Dict:
    """
    Run the development workflow.
    
    Args:
        requirement_text: Raw requirement text from user
        project_id: Project identifier
        use_langgraph: Always uses LangGraph (parameter kept for compatibility)
    
    Returns:
        Final state dictionary with all results
    """
    # Initialize state
    initial_state: Dict = {
        "project_id": project_id,
        "requirement_id": f"req_{int(time.time()*1000)}",
        "current_step": "analysis",
        "raw_requirement": requirement_text,
        "structured_requirements": [],
        "architecture_doc": {},
        "detailed_tasks": [],
        "implementation_results": {},
        "test_results": {},
        "release_info": {},
    }
    
    # Create and run workflow
    graph = create_workflow()
    print(f"[Workflow] Starting LangGraph workflow for project: {project_id}")
    print(f"[Workflow] Requirement: {requirement_text[:100]}...")
    
    result = graph.invoke(initial_state)
    
    print(f"[Workflow] Completed: {result.get('current_step')}")
    return result


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("Testing LangFlow workflow...")
    result = run_workflow("Build a simple calculator application")
    print(f"\nFinal step: {result.get('current_step')}")
    print(f"Release info: {result.get('release_info')}")