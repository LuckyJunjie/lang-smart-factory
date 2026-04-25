"""
LangFlow Factory - Architect Agent
"""
from typing import Dict
from .base_agent import BaseAgent
import json

ARCHITECT_PROMPT = """你是资深系统架构师。根据以下需求，设计系统架构。

需求列表：
{requirements}

请输出 JSON 格式的架构文档：
{{
  "modules": [
    {{
      "name": "模块名称",
      "description": "模块描述",
      "dependencies": ["依赖模块"]
    }}
  ],
  "tech_stack": {{
    "language": "Python",
    "framework": "Flask/LangChain",
    "database": "SQLite"
  }},
  "integration_points": ["API接口1", "API接口2"],
  "task_breakdown_plan": ["任务1", "任务2"]
}}

只输出 JSON，不要有其他内容。"""

class Architect(BaseAgent):
    """架构师 Agent"""
    
    def __init__(self):
        super().__init__("Architect", "系统架构设计")
    
    def process(self, state: Dict) -> Dict:
        """设计架构"""
        requirements = state.get("structured_requirements", [])
        
        if not requirements:
            state["error"] = "No requirements provided"
            return state
        
        req_text = "\n".join([f"- {r.get('title', 'N/A')}" for r in requirements])
        prompt = ARCHITECT_PROMPT.format(requirements=req_text)
        response = self.invoke_llm(prompt)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
            else:
                json_str = response
            
            result = json.loads(json_str)
            state["architecture_doc"] = result
            state["current_step"] = "detail_design"
        except json.JSONDecodeError:
            # 使用默认架构
            state["architecture_doc"] = {
                "modules": [{"name": "main", "description": "主模块", "dependencies": []}],
                "tech_stack": {"language": "Python", "framework": "Flask", "database": "SQLite"},
                "integration_points": [],
                "task_breakdown_plan": []
            }
            state["current_step"] = "detail_design"
        
        return state
