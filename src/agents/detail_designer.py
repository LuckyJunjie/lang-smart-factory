"""
LangFlow Factory - Detail Designer Agent
"""
from typing import Dict
from .base_agent import BaseAgent
import json

DESIGNER_PROMPT = """你是资深技术负责人。根据以下架构文档，设计详细任务。

架构文档：
{architecture}

需求列表：
{requirements}

请输出 JSON 格式的详细任务列表：
{{
  "tasks": [
    {{
      "id": "TASK-001",
      "title": "任务标题",
      "description": "任务描述",
      "acceptance_criteria": ["验收标准1", "验收标准2"],
      "estimated_hours": 8,
      "assigned_role": "developer",
      "related_files": ["文件路径"]
    }}
  ],
  "task_graph": {{
    "TASK-001": [],
    "TASK-002": ["TASK-001"]
  }}
}}

只输出 JSON，不要有其他内容。"""

class DetailDesigner(BaseAgent):
    """详细设计师 Agent"""
    
    def __init__(self):
        super().__init__("DetailDesigner", "详细设计与任务拆分")
    
    def process(self, state: Dict) -> Dict:
        """设计详细任务"""
        arch_doc = state.get("architecture_doc", {})
        requirements = state.get("structured_requirements", [])
        
        if not arch_doc:
            state["error"] = "No architecture doc provided"
            return state
        
        arch_text = json.dumps(arch_doc, ensure_ascii=False)
        req_text = "\n".join([f"- {r.get('title', 'N/A')}" for r in requirements])
        
        prompt = DESIGNER_PROMPT.format(architecture=arch_text, requirements=req_text)
        response = self.invoke_llm(prompt)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
            else:
                json_str = response
            
            result = json.loads(json_str)
            state["detailed_tasks"] = result.get("tasks", [])
            state["task_graph"] = result.get("task_graph", {})
            state["current_step"] = "dispatch"
        except json.JSONDecodeError:
            # 使用默认任务
            state["detailed_tasks"] = [
                {
                    "id": "TASK-001",
                    "title": "初始化项目结构",
                    "description": "创建项目基础文件",
                    "acceptance_criteria": ["文件创建成功"],
                    "estimated_hours": 2,
                    "assigned_role": "developer"
                }
            ]
            state["task_graph"] = {"TASK-001": []}
            state["current_step"] = "dispatch"
        
        return state
