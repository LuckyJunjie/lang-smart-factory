"""
LangFlow Factory - Architect Agent
使用 LLM 设计系统架构
"""
from typing import Dict
import json
from ..llm.minimax_client import llm_client

ARCHITECT_PROMPT_TEMPLATE = """根据以下需求列表，设计系统架构。

需求列表：
{requirements}

输出JSON格式架构文档：
{{
  "modules": [
    {{
      "name": "模块名(英文)",
      "description": "模块描述",
      "dependencies": ["依赖模块"],
      "responsibilities": ["职责1", "职责2"]
    }}
  ],
  "tech_stack": {{
    "language": "语言",
    "framework": "框架", 
    "database": "数据库",
    "other": "其他技术"
  }},
  "data_flow": "数据流描述",
  "integration_points": ["接口1", "接口2"]
}}

只输出JSON。"""

class Architect:
    def __init__(self):
        self.name = "Architect"
        self.role = "系统架构设计"
    
    def process(self, state: Dict) -> Dict:
        requirements = state.get("structured_requirements", [])
        if not requirements:
            state["error"] = "No requirements provided"
            state["current_step"] = "detail_design"
            return state
        
        req_text = "\n".join([f"- {r.get('id')}: {r.get('title')} - {r.get('description', '')}" 
                             for r in requirements])
        prompt = ARCHITECT_PROMPT_TEMPLATE.format(requirements=req_text)
        print(f"[Architect] Designing architecture for {len(requirements)} requirements...")
        
        response = llm_client.generate(prompt, max_tokens=4096)
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            state["architecture_doc"] = json.loads(json_str)
            state["current_step"] = "detail_design"
            print(f"[Architect] Architecture designed with {len(state['architecture_doc'].get('modules', []))} modules")
        except json.JSONDecodeError as e:
            print(f"[Architect] JSON parse error: {e}")
            state["architecture_doc"] = {"modules": [], "tech_stack": {}, "data_flow": "", "integration_points": []}
            state["current_step"] = "detail_design"
        
        return state
