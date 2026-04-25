#!/usr/bin/env python3
"""
Spawn subagents to analyze meetings.
Each subagent gets the meeting context and generates their own analysis.
"""
import os
import sys
import json
import requests
import subprocess
import time

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")
TIMEOUT = 15

# Agent role prompts
AGENT_PROMPTS = {
    "einstein": "从物理学角度分析：",
    "curie": "从科学角度分析：",
    "galileo": "从经典物理学视角分析：",
    "hawking": "从理论物理角度分析：",
    "darwin": "从进化论角度分析：",
    "newton": "从经典力学角度分析：",
    "model_s": "从Tesla供应链角度分析：",
    "model_3": "从Tesla市场角度分析：",
    "model_x": "从Tesla技术角度分析：",
    "model_y": "从新能源市场角度分析：",
    "cybertruck": "从风险管理角度分析：",
    "hera": "从会议协调角度总结：",
}


def get_meetings_for_agent(agent, status="running"):
    r = requests.get(f"{API_BASE}/meetings/for-agent", params={"agent": agent, "status": status}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() or []


def submit_meeting_input(meeting_id, agent_id, round_number, analysis, comments):
    r = requests.post(
        f"{API_BASE}/meetings/{meeting_id}/inputs",
        json={"agent_id": agent_id, "round_number": round_number, "analysis": analysis, "comments": comments},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def spawn_subagent(agent_id, meeting_id, topic, problem, contribute_focus):
    """Spawn a subagent to analyze the meeting."""
    prompt = AGENT_PROMPTS.get(agent_id, "分析：")
    
    task = f"""你是一个投资分析会议参与者。请分析以下会议议题：

议题：{topic}
问题：{problem}
你的角色：{contribute_focus}

请生成：
1. Analysis（分析）：从你的专业角度分析这个问题对全球股市的影响
2. Comments（建议）：具体的投资建议

注意：生成的文本应该是专业的投资分析意见，不是模板套话。"""

    cmd = [
        "openclaw", "sessions", "spawn",
        "--agent-id", agent_id,
        "--task", task,
        "--mode", "run",
        "--timeout-seconds", "120"
    ]
    
    print(f"Spawning subagent {agent_id} for meeting {meeting_id}...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/pi/.openclaw/workspace/implementation/smart-factory")
    return result.stdout, result.stderr


def main():
    # Check each agent
    agents = ["einstein", "curie", "galileo", "hawking", "darwin", "newton", 
              "model_s", "model_3", "model_x", "model_y", "cybertruck", "hera"]
    
    for agent in agents:
        try:
            meetings = get_meetings_for_agent(agent)
            if not meetings:
                continue
                
            for item in meetings:
                if not item.get("needs_your_input"):
                    continue
                    
                mid = item.get("id")
                topic = item.get("topic", "")
                problem = item.get("problem_to_solve", "")
                contribute_focus = item.get("my_participant", {}).get("contribute_focus", "")
                current_round = item.get("current_round", 1)
                
                print(f"\n=== Agent {agent} needs to submit for meeting {mid} ===")
                print(f"Topic: {topic}")
                print(f"Focus: {contribute_focus}")
                
                # Spawn subagent to analyze
                stdout, stderr = spawn_subagent(agent, mid, topic, problem, contribute_focus)
                print(f"Subagent output: {stdout[:500]}")
                if stderr:
                    print(f"Errors: {stderr[:500]}")
                    
        except Exception as e:
            print(f"Error processing {agent}: {e}")
            continue


if __name__ == "__main__":
    main()
