"""
LangFlow Factory - Detail Designer Agent
使用 LLM 生成详细任务列表
"""
from typing import Dict
import json
from ..llm.minimax_client import llm_client

DESIGN_PROMPT_TEMPLATE = """根据以下需求和架构，设计详细任务列表。

需求：
{requirements}

架构模块：
{architecture}

输出JSON数组，每个任务包含：
{{
  "id": "TASK-001",
  "title": "任务标题",
  "description": "详细描述",
  "estimated_hours": 数字,
  "dependencies": ["TASK-XXX"],
  "requirements": "对应的需求ID",
  "module": "所属模块"
}}

只输出JSON数组。"""

class DetailDesigner:
    def __init__(self):
        self.name = "DetailDesigner"
        self.role = "详细设计"
    
    def process(self, state: Dict) -> Dict:
        requirements = state.get("structured_requirements", [])
        architecture = state.get("architecture_doc", {})
        
        if not requirements:
            state["error"] = "No requirements"
            state["current_step"] = "dispatch"
            return state
        
        req_text = "\n".join([f"- {r.get('id')}: {r.get('title')} - {r.get('description', '')}" 
                             for r in requirements])
        arch_text = json.dumps(architecture.get("modules", []), ensure_ascii=False)
        
        prompt = DESIGN_PROMPT_TEMPLATE.format(requirements=req_text, architecture=arch_text)
        print(f"[DetailDesigner] Designing {len(requirements)} tasks...")
        
        response = llm_client.generate(prompt, max_tokens=4096)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "[" in response:
                start = response.find("[")
                end = response.rfind("]") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            tasks = json.loads(json_str)
            state["detailed_tasks"] = tasks
            state["current_step"] = "dispatch"
            print(f"[DetailDesigner] Generated {len(tasks)} tasks")
        except json.JSONDecodeError as e:
            print(f"[DetailDesigner] JSON parse error: {e}")
            state["detailed_tasks"] = [{"id": f"TASK-{i+1:03d}", "title": r.get("title", "Task"), "description": r.get("description", ""), "estimated_hours": 8, "dependencies": [], "requirements": r.get("id", ""), "module": "main"} for i, r in enumerate(requirements)]
            state["current_step"] = "dispatch"
        
        return state
