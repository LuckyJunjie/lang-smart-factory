"""
LangFlow Factory - Demand Analyst Agent
"""
from typing import Dict, List
from .base_agent import BaseAgent
import json

DEMAND_ANALYST_PROMPT = """你是资深需求分析师。根据以下需求文本，进行结构化分析。

需求文本：
{requirement_text}

请输出 JSON 格式的子需求列表和验收标准：
{{
  "requirements": [
    {{
      "id": "REQ-001",
      "title": "子需求标题",
      "description": "详细描述",
      "type": "feature|bug|enhancement",
      "priority": "high|medium|low",
      "acceptance_criteria": ["标准1", "标准2"]
    }}
  ],
  "acceptance_criteria": [
    {{
      "id": "AC-001",
      "given": "前提条件",
      "when": "触发动作",
      "then": "预期结果"
    }}
  ],
  "estimated_complexity": "low|medium|high",
  "dependencies": []
}}

只输出 JSON，不要有其他内容。"""

class DemandAnalyst(BaseAgent):
    """需求分析师 Agent"""
    
    def __init__(self):
        super().__init__("DemandAnalyst", "需求分析与拆解")
    
    def process(self, state: Dict) -> Dict:
        """分析需求"""
        requirement_text = state.get("raw_requirement", "")
        
        if not requirement_text:
            state["error"] = "No requirement text provided"
            return state
        
        # 调用 LLM 分析
        prompt = DEMAND_ANALYST_PROMPT.format(requirement_text=requirement_text)
        response = self.invoke_llm(prompt)
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
            else:
                json_str = response
            
            result = json.loads(json_str)
            state["structured_requirements"] = result.get("requirements", [])
            state["acceptance_criteria"] = result.get("acceptance_criteria", [])
            state["estimated_complexity"] = result.get("estimated_complexity", "medium")
            state["current_step"] = "architecture"
            state["_trace"] = {"step": "analysis", "action": "completed", "data": result}
        except json.JSONDecodeError:
            state["error"] = f"Failed to parse requirements"
            # 使用默认结构
            state["structured_requirements"] = []
            state["acceptance_criteria"] = []
        
        return state
