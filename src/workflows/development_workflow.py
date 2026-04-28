"""
LangFlow Factory - Development Workflow
File-based queue workflow. No Redis required.
"""
from typing import Dict
import json
import time
import os

from ..agents.demand_analyst import DemandAnalyst
from ..agents.architect import Architect
from ..agents.detail_designer import DetailDesigner


WORKSPACE_ROOT = "/home/pi/.openclaw/workspace"


def analysis_node(state: Dict) -> Dict:
    """Demand Analysis node - analyze requirements using LLM."""
    analyst = DemandAnalyst()
    result = analyst.process(state)
    result["current_step"] = "architect"
    return result


def architect_node(state: Dict) -> Dict:
    """Architecture Design node - design system architecture using LLM."""
    architect = Architect()
    result = architect.process(state)
    result["current_step"] = "detail_design"
    return result


def detail_design_node(state: Dict) -> Dict:
    """Detail Design node - break down into tasks using LLM."""
    designer = DetailDesigner()
    result = designer.process(state)
    result["current_step"] = "dispatch"
    return result


def dispatch_node(state: Dict) -> Dict:
    """
    Dispatch node - write tasks to file queue.
    Creates work/input/ and work/output/ directories,
    writes each task as a JSON file.
    """
    project_id = state.get("project_id", "default")
    tasks = state.get("detailed_tasks", [])
    
    if not tasks:
        tasks = [{
            "id": "task_001",
            "title": "Default Task",
            "requirements": state.get("raw_requirement", ""),
            "project_id": project_id,
            "acceptance_criteria": ["完成基本功能"],
        }]
    
    work_dir = f"{WORKSPACE_ROOT}/{project_id}/work"
    input_dir = os.path.join(work_dir, "input")
    output_dir = os.path.join(work_dir, "output")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    task_ids = []
    for task in tasks:
        task_id = task.get("id", f"task_{len(task_ids)+1:03d}")
        task_ids.append(task_id)
        
        task_file = {
            "id": task_id,
            "title": task.get("title", "Task"),
            "requirements": task.get("requirements", task.get("description", "")),
            "project_id": project_id,
            "acceptance_criteria": task.get("acceptance_criteria", []),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        
        input_file = os.path.join(input_dir, f"{task_id}.json")
        with open(input_file, "w") as f:
            json.dump(task_file, f, indent=2, ensure_ascii=False)
        
        print(f"[Dispatch] Wrote task {task_id} -> {input_file}")
    
    state["dispatched_tasks"] = task_ids
    state["dispatch_count"] = len(task_ids)
    state["current_step"] = "implementation"
    return state


def implementation_node(state: Dict) -> Dict:
    """
    Implementation node - poll for results from OpenClaw output files.
    Waits for OpenClaw to write results to work/output/ directory.
    """
    project_id = state.get("project_id", "default")
    dispatched = state.get("dispatched_tasks", [])
    
    if not dispatched:
        state["current_step"] = "testing"
        return state
    
    output_dir = f"{WORKSPACE_ROOT}/{project_id}/work/output"
    completed = []
    max_wait = 300  # 5 minutes timeout
    
    print(f"[Implementation] Waiting for {len(dispatched)} tasks...")
    start_time = time.time()
    
    while len(completed) < len(dispatched) and (time.time() - start_time) < max_wait:
        for task_id in dispatched:
            if task_id in completed:
                continue
            
            output_file = os.path.join(output_dir, f"{task_id}.json")
            if os.path.exists(output_file):
                try:
                    with open(output_file, "r") as f:
                        result = json.load(f)
                    print(f"[Implementation] Task {task_id} completed: {result.get('status')}")
                    completed.append(task_id)
                except json.JSONDecodeError as e:
                    print(f"[Implementation] Error reading {output_file}: {e}")
        
        if len(completed) < len(dispatched):
            time.sleep(2)
    
    state["completed_tasks"] = completed
    state["implementation_results"] = {"completed": completed, "total": len(dispatched)}
    state["current_step"] = "testing"
    return state


def verify_node(state: Dict) -> Dict:
    """
    ReAct Verification node - verify OpenClaw outputs against acceptance_criteria.
    If verification fails, write feedback to work/feedback/ and mark for retry.
    """
    project_id = state.get("project_id", "default")
    dispatched = state.get("dispatched_tasks", [])
    max_retries = 3
    
    if not dispatched:
        state["current_step"] = "testing"
        return state
    
    input_dir = f"{WORKSPACE_ROOT}/{project_id}/work/input"
    output_dir = f"{WORKSPACE_ROOT}/{project_id}/work/output"
    feedback_dir = f"{WORKSPACE_ROOT}/{project_id}/work/feedback"
    
    os.makedirs(feedback_dir, exist_ok=True)
    
    verified = []
    failed = []
    
    print(f"[Verify] Starting ReAct verification for {len(dispatched)} tasks...")
    
    for task_id in dispatched:
        input_file = os.path.join(input_dir, f"{task_id}.json")
        output_file = os.path.join(output_dir, f"{task_id}.json")
        
        # Load task spec
        task = {"acceptance_criteria": [], "requirements": ""}
        if os.path.exists(input_file):
            with open(input_file, "r") as f:
                task = json.load(f)
        
        # Check if output exists
        if not os.path.exists(output_file):
            failed.append({"task_id": task_id, "reason": "output not found"})
            continue
        
        with open(output_file, "r") as f:
            result = json.load(f)
        
        # ReAct verification
        errors = []
        
        # Check status
        if result.get("status") != "completed":
            errors.append(f"Status is {result.get('status')}, expected completed")
        
        # Check output file exists
        output_path = result.get("output_file")
        if output_path and not os.path.exists(output_path):
            errors.append(f"Output file does not exist: {output_path}")
        
        # Check error logs
        if result.get("errors"):
            errors.extend(result["errors"])
        
        if errors:
            # Get retry count
            retry_count = len([f for f in os.listdir(feedback_dir) 
                             if f.startswith(f"{task_id}_feedback_")])
            
            if retry_count < max_retries:
                # Write feedback and delete output to trigger retry
                feedback = {
                    "task_id": task_id,
                    "attempt": retry_count + 1,
                    "errors": errors,
                    "acceptance_criteria": task.get("acceptance_criteria", []),
                    "suggestion": f"Fix errors: {', '.join(errors)}",
                }
                feedback_file = os.path.join(feedback_dir, f"{task_id}_feedback_{retry_count+1}.json")
                with open(feedback_file, "w") as f:
                    json.dump(feedback, f, indent=2)
                
                # Delete output to trigger retry
                os.remove(output_file)
                print(f"[ReAct] Task {task_id} failed verification (attempt {retry_count+1}), feedback written")
                failed.append({"task_id": task_id, "reason": "verification failed", "errors": errors})
            else:
                print(f"[ReAct] Task {task_id} exceeded max retries ({max_retries})")
                failed.append({"task_id": task_id, "reason": "max retries exceeded"})
        else:
            print(f"[ReAct] Task {task_id} verified OK")
            verified.append(task_id)
    
    state["verified_tasks"] = verified
    state["failed_tasks"] = [f["task_id"] for f in failed]
    state["verification_errors"] = {f["task_id"]: f["errors"] for f in failed if "errors" in f}
    state["current_step"] = "testing"
    print(f"[Verify] {len(verified)}/{len(dispatched)} tasks verified")
    return state


def testing_node(state: Dict) -> Dict:
    """Testing node - summarize results."""
    results = state.get("implementation_results", {})
    completed = results.get("completed", [])
    total = results.get("total", 0)
    
    test_results = {
        "total": total,
        "passed": len(completed),
        "failed": total - len(completed),
        "tasks": completed,
    }
    
    state["test_results"] = test_results
    state["current_step"] = "release"
    print(f"[Testing] {len(completed)}/{total} tasks completed")
    return state


def release_node(state: Dict) -> Dict:
    """Release node - finalize and report."""
    project_id = state.get("project_id", "default")
    test_results = state.get("test_results", {})
    
    state["release_info"] = {
        "project_id": project_id,
        "status": "completed" if test_results.get("failed", 0) == 0 else "partial",
        "test_results": test_results,
        "release_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    state["current_step"] = "completed"
    print(f"[Release] Project {project_id} {state['release_info']['status']}")
    return state


def run_workflow(requirement_text: str, project_id: str = "default") -> Dict:
    """
    Run the complete workflow.
    
    Args:
        requirement_text: Natural language requirement
        project_id: Project identifier
    
    Returns:
        Final state dict
    """
    state = {
        "project_id": project_id,
        "raw_requirement": requirement_text,
        "current_step": "analysis",
        "structured_requirements": [],
        "architecture_doc": {},
        "detailed_tasks": [],
        "dispatched_tasks": [],
        "completed_tasks": [],
        "test_results": {},
        "release_info": {},
    }
    
    nodes = [
        ("analysis", analysis_node),
        ("architecture", architect_node),
        ("detail_design", detail_design_node),
        ("dispatch", dispatch_node),
        ("implementation", implementation_node),
        ("verify", verify_node),
        ("testing", testing_node),
        ("release", release_node),
    ]
    
    for name, func in nodes:
        print(f"[Workflow] Executing: {name}")
        state = func(state)
        if state.get("current_step") == "completed":
            break
    
    return state
