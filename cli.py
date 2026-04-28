#!/usr/bin/env python3
"""
LangFlow Factory - CLI Entry Point
Unified command: python cli.py run "<requirement>" --project-id <project_id>
"""
import argparse
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    parser = argparse.ArgumentParser(description="LangFlow Factory CLI")
    parser.add_argument("command", nargs="?", default="run", help="Command (default: run)")
    parser.add_argument("requirement", nargs="?", help="Requirement text")
    parser.add_argument("--project-id", "-p", default="default", help="Project ID")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--use-langgraph", action="store_true", default=True, help="Use LangGraph (default: true)")
    
    args = parser.parse_args()
    
    if args.command != "run":
        print(f"Unknown command: {args.command}")
        print("Usage: python cli.py run '<requirement>' --project-id <project_id>")
        sys.exit(1)
    
    if not args.requirement:
        print("Error: requirement is required")
        print("Usage: python cli.py run '<requirement>' --project-id <project_id>")
        sys.exit(1)
    
    # Import and run workflow
    from workflows.development_workflow import run_workflow
    
    print(f"Running workflow for project: {args.project_id}")
    print(f"Requirement: {args.requirement}")
    print("-" * 50)
    
    result = run_workflow(args.requirement, args.project_id, use_langgraph=args.use_langgraph)
    
    print(f"\n--- Results ---")
    print(f"Current step: {result.get('current_step')}")
    print(f"Structured requirements: {len(result.get('structured_requirements', []))}")
    print(f"Architecture doc: {bool(result.get('architecture_doc'))}")
    print(f"Detailed tasks: {len(result.get('detailed_tasks', []))}")
    print(f"Test results: {result.get('test_results', {})}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"Result saved to: {args.output}")


if __name__ == "__main__":
    main()