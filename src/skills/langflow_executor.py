"""
LangFlow Executor - OpenClaw Agent Task Processor

Monitors work/input/ for new tasks, executes with coding agent,
writes results to work/output/. Supports ReAct retry loop.

Usage:
    python -m src.skills.langflow_executor
    python -m src.skills.langflow_executor --project <project_id>
    python -m src.skills.langflow_executor --watch  # continuous mode
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

WORKSPACE_ROOT = "/home/pi/.openclaw/workspace"


def get_pending_tasks(project_id: Optional[str] = None) -> List[Dict]:
    """Find all task JSON files in work/input/ directories."""
    tasks = []
    
    if project_id:
        projects = [project_id]
    else:
        # Find all project directories
        projects = []
        try:
            for entry in os.listdir(WORKSPACE_ROOT):
                project_path = os.path.join(WORKSPACE_ROOT, entry)
                if os.path.isdir(project_path):
                    input_dir = os.path.join(project_path, "work", "input")
                    if os.path.exists(input_dir):
                        projects.append(entry)
        except PermissionError:
            pass
    
    for proj in projects:
        input_dir = os.path.join(WORKSPACE_ROOT, proj, "work", "input")
        output_dir = os.path.join(WORKSPACE_ROOT, proj, "work", "output")
        
        if not os.path.exists(input_dir):
            continue
        
        for filename in os.listdir(input_dir):
            if not filename.endswith(".json"):
                continue
            
            task_id = filename[:-5]  # remove .json
            output_file = os.path.join(output_dir, filename)
            
            # Skip if already processed
            if os.path.exists(output_file):
                try:
                    with open(output_file, "r") as f:
                        result = json.load(f)
                    if result.get("status") in ("completed", "failed"):
                        continue
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            task_file = os.path.join(input_dir, filename)
            try:
                with open(task_file, "r") as f:
                    task_data = json.load(f)
                task_data["_input_path"] = task_file
                task_data["_output_path"] = output_file
                task_data["_project_id"] = proj
                tasks.append(task_data)
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    return tasks


def check_feedback(task_id: str, project_id: str) -> Optional[Dict]:
    """Check for retry feedback in work/feedback/ directory."""
    feedback_dir = os.path.join(WORKSPACE_ROOT, project_id, "work", "feedback")
    
    if not os.path.exists(feedback_dir):
        return None
    
    # Find most recent feedback file for this task
    pattern = f"{task_id}_feedback_"
    feedback_files = []
    
    for filename in os.listdir(feedback_dir):
        if filename.startswith(pattern) and filename.endswith(".json"):
            feedback_files.append(os.path.join(feedback_dir, filename))
    
    if not feedback_files:
        return None
    
    # Return most recent
    feedback_files.sort(key=lambda f: os.path.getmtime(f))
    latest = feedback_files[-1]
    
    with open(latest, "r") as f:
        return json.load(f)


def execute_task(task: Dict) -> Dict:
    """
    Execute a task using coding agent (Claude Code/Codex).
    
    In a real implementation, this would spawn a coding agent.
    For now, this is a placeholder that logs the task.
    """
    task_id = task.get("id", "unknown")
    project_id = task.get("_project_id", "default")
    requirements = task.get("requirements", "")
    acceptance_criteria = task.get("acceptance_criteria", [])
    feedback = task.get("feedback", [])
    
    print(f"[Executor] Processing task {task_id} for project {project_id}")
    
    # Check for retry feedback
    fb = check_feedback(task_id, project_id)
    if fb:
        print(f"[Executor] Found feedback for {task_id}: {fb.get('errors', [])}")
        # In real implementation, incorporate feedback into prompt
    
    # Placeholder: simulate execution
    # In real implementation, use sessions_spawn with coding-agent
    print(f"[Executor] Would execute: {requirements[:100]}...")
    print(f"[Executor] Acceptance criteria: {acceptance_criteria}")
    
    # For demo, simulate success
    result = {
        "task_id": task_id,
        "status": "completed",
        "output_file": f"/home/pi/.openclaw/workspace/{project_id}/src/{task_id}.py",
        "errors": [],
        "completed_at": datetime.now().isoformat(),
    }
    
    return result


def verify_output(result: Dict, task: Dict) -> tuple[bool, List[str]]:
    """
    Self-verify output against acceptance criteria.
    Returns (is_valid, errors).
    """
    errors = []
    
    # Check status
    if result.get("status") != "completed":
        errors.append(f"Task status is {result.get('status')}, expected completed")
    
    # Check output file exists
    output_file = result.get("output_file")
    if output_file and not os.path.exists(output_file):
        errors.append(f"Output file does not exist: {output_file}")
    
    # Check for error logs
    if result.get("errors"):
        errors.extend(result["errors"])
    
    return len(errors) == 0, errors


def write_result(task: Dict, result: Dict) -> None:
    """Write result to output file."""
    output_path = task.get("_output_path")
    if not output_path:
        return
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[Executor] Wrote result to {output_path}")


def process_tasks(project_id: Optional[str] = None, dry_run: bool = False) -> Dict:
    """Process all pending tasks."""
    tasks = get_pending_tasks(project_id)
    
    results = {
        "processed": 0,
        "completed": 0,
        "failed": 0,
        "tasks": [],
    }
    
    for task in tasks:
        task_id = task.get("id", "unknown")
        print(f"[Executor] Processing {task_id}...")
        
        try:
            result = execute_task(task)
            
            # Self-verify
            is_valid, errors = verify_output(result, task)
            
            if not is_valid:
                print(f"[Executor] Self-verification failed: {errors}")
                result["status"] = "failed"
                result["errors"] = errors
            
            write_result(task, result)
            
            results["processed"] += 1
            if result.get("status") == "completed":
                results["completed"] += 1
            else:
                results["failed"] += 1
            
            results["tasks"].append({
                "task_id": task_id,
                "status": result.get("status"),
            })
            
        except Exception as e:
            print(f"[Executor] Error processing {task_id}: {e}")
            results["failed"] += 1
            results["tasks"].append({
                "task_id": task_id,
                "status": "error",
                "error": str(e),
            })
    
    return results


def main():
    parser = argparse.ArgumentParser(description="LangFlow Executor")
    parser.add_argument("--project", "-p", help="Process specific project only")
    parser.add_argument("--watch", "-w", action="store_true", help="Run continuously")
    parser.add_argument("--interval", "-i", type=int, default=300, help="Watch interval in seconds")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Don't actually execute")
    
    args = parser.parse_args()
    
    if args.watch:
        print(f"[Executor] Running in watch mode (interval: {args.interval}s)")
        while True:
            results = process_tasks(project_id=args.project, dry_run=args.dry_run)
            print(f"[Executor] Cycle complete: {results['processed']} processed, "
                  f"{results['completed']} completed, {results['failed']} failed")
            time.sleep(args.interval)
    else:
        results = process_tasks(project_id=args.project, dry_run=args.dry_run)
        print(f"[Executor] Done: {results['processed']} processed, "
              f"{results['completed']} completed, {results['failed']} failed")
        return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
