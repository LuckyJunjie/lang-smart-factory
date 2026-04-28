"""
LangFlow Factory - Task Coordinator
File-based queue instead of Redis/LLM.
Coordinates tasks by writing input files and polling output files.
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = "/home/pi/.openclaw/workspace"

def get_task_list(project_id: str) -> list:
    """
    Read tasks from GraphState's task list.
    Look for tasks in: /home/pi/.openclaw/workspace/{project_id}/graph_state.json
    or /home/pi/.openclaw/workspace/{project_id}/tasks.json
    """
    possible_paths = [
        f"{WORKSPACE_ROOT}/{project_id}/graph_state.json",
        f"{WORKSPACE_ROOT}/{project_id}/tasks.json",
        f"{WORKSPACE_ROOT}/{project_id}/tasks.json",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                # Try to extract tasks from different possible structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    if "tasks" in data:
                        return data["tasks"]
                    elif "graph_state" in data and isinstance(data["graph_state"], dict):
                        if "tasks" in data["graph_state"]:
                            return data["graph_state"]["tasks"]
    
    logger.warning(f"No task list found for project {project_id}")
    return []


def ensure_directories(project_id: str) -> tuple[str, str]:
    """Create input/output directories for the project."""
    work_dir = f"{WORKSPACE_ROOT}/{project_id}/work"
    input_dir = os.path.join(work_dir, "input")
    output_dir = os.path.join(work_dir, "output")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Work dir: {work_dir}")
    return input_dir, output_dir


def write_task(input_dir: str, task: dict) -> str:
    """Write task to input file. Returns the input file path."""
    task_id = task.get("id")
    input_file = os.path.join(input_dir, f"{task_id}.json")
    
    with open(input_file, "w") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Wrote task input: {input_file}")
    return input_file


def poll_output(output_dir: str, task_id: str, timeout: int = 300) -> Optional[dict]:
    """
    Poll for output file until it appears or timeout.
    Returns the result dict or None on timeout.
    """
    output_file = os.path.join(output_dir, f"{task_id}.json")
    poll_interval = 2  # seconds
    elapsed = 0
    
    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval
        
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as f:
                    result = json.load(f)
                logger.info(f"Task {task_id} completed in {elapsed}s")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in output {output_file}: {e}")
                continue
        else:
            # Show progress for long-running tasks
            if elapsed % 30 == 0 and elapsed > 0:
                logger.info(f"Still waiting for {task_id}... ({elapsed}s)")
    
    logger.warning(f"Task {task_id} timed out after {timeout}s")
    return {
        "task_id": task_id,
        "status": "timeout",
        "error": f"Task timed out after {timeout} seconds",
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def run_single_task(project_id: str, task: dict, input_dir: str, output_dir: str, timeout: int = 300) -> dict:
    """Run a single task: write input, poll output, return result."""
    task_id = task.get("id")
    logger.info(f"Processing task: {task_id}")
    
    # Write task input
    write_task(input_dir, task)
    
    # Poll for output
    result = poll_output(output_dir, task_id, timeout)
    return result


def run_coordinator(project_id: str, timeout_per_task: int = 300) -> list:
    """
    Main coordinator function.
    Reads tasks, coordinates them, collects results.
    """
    logger.info(f"Starting TaskCoordinator for project: {project_id}")
    
    # Get task list
    tasks = get_task_list(project_id)
    if not tasks:
        logger.warning("No tasks found")
        return []
    
    logger.info(f"Found {len(tasks)} tasks")
    
    # Ensure directories exist
    input_dir, output_dir = ensure_directories(project_id)
    
    # Process each task
    results = []
    for i, task in enumerate(tasks, 1):
        task_id = task.get("id", f"task_{i:03d}")
        logger.info(f"[{i}/{len(tasks)}] Processing {task_id}")
        
        result = run_single_task(project_id, task, input_dir, output_dir, timeout_per_task)
        results.append(result)
        
        logger.info(f"Result: {result.get('status')}")
    
    logger.info(f"Completed {len(results)} tasks")
    return results


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Coordinator")
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per task in seconds")
    parser.add_argument("--task-id", help="Process single task by ID")
    
    args = parser.parse_args()
    
    if args.task_id:
        # Single task mode
        tasks = get_task_list(args.project_id)
        task = None
        for t in tasks:
            if t.get("id") == args.task_id:
                task = t
                break
        
        if not task:
            logger.error(f"Task {args.task_id} not found")
            sys.exit(1)
        
        input_dir, output_dir = ensure_directories(args.project_id)
        result = run_single_task(args.project_id, task, input_dir, output_dir, args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Process all tasks
        results = run_coordinator(args.project_id, args.timeout)
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()