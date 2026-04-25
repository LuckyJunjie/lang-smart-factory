#!/usr/bin/env python3
"""
LangFlow Factory - CLI Entry Point
"""
import argparse
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

def run_workflow_command(args):
    """运行工作流"""
    from src.workflows.development_workflow import run_workflow
    
    print(f"Running workflow for project: {args.project_id}")
    print(f"Requirement: {args.requirement}")
    print("-" * 50)
    
    result = run_workflow(args.requirement, args.project_id)
    
    print(f"Current step: {result.get('current_step')}")
    print(f"Structured requirements: {len(result.get('structured_requirements', []))}")
    print(f"Architecture doc: {bool(result.get('architecture_doc'))}")
    print(f"Detailed tasks: {len(result.get('detailed_tasks', []))}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResult saved to: {args.output}")

def status_command(args):
    """查看状态"""
    print(f"Status for project: {args.project_id}")
    print("Status: pending - implementation required")

def main():
    parser = argparse.ArgumentParser(description="LangFlow Factory CLI")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="运行需求分析")
    run_parser.add_argument("--requirement", "-r", required=True, help="需求文本")
    run_parser.add_argument("--project-id", "-p", default="default", help="项目ID")
    run_parser.add_argument("--output", "-o", help="输出文件 (JSON)")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看状态")
    status_parser.add_argument("--project-id", "-p", required=True, help="项目ID")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有节点")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_workflow_command(args)
    elif args.command == "status":
        status_command(args)
    elif args.command == "list":
        print("Available workflow nodes:")
        print("  - analysis: Demand Analyst")
        print("  - architecture: Architect")
        print("  - detail_design: Detail Designer")
        print("  - dispatch: Task Dispatch")
        print("  - implementation: Code Implementation")
        print("  - testing: Testing & Verification")
        print("  - acceptance: Final Acceptance")
        print("  - release: CI/CD & Release")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
