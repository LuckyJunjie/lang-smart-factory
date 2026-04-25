"""
LangFlow Factory - Demand Analyst Agent
"""
from typing import Dict
import json

DEMAND_ANALYST_PROMPT = '''你是资深需求分析师。根据以下需求文本，进行结构化分析。

需求文本：
{requirement_text}

请输出 JSON 格式：
{{
  "requirements": [
    {{
      "id": "REQ-001",
      "title": "{req_title}",
      "description": "详细描述",
      "type": "feature",
      "priority": "medium",
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
  "estimated_complexity": "medium",
  "dependencies": []
}}'''

class DemandAnalyst:
    """需求分析师 Agent"""
    
    def __init__(self):
        self.name = "DemandAnalyst"
        self.role = "需求分析与拆解"
    
    def process(self, state: Dict) -> Dict:
        """分析需求"""
        requirement_text = state.get("raw_requirement", "")
        
        if not requirement_text:
            state["error"] = "No requirement text provided"
            return state
        
        # 构建提示词
        req_title = requirement_text[:50]
        prompt = DEMAND_ANALYST_PROMPT.format(requirement_text=requirement_text, req_title=req_title)
        
        # 模拟 LLM 调用 - 直接生成合理 JSON
        response = self._generate_response(requirement_text)
        
        try:
            result = json.loads(response)
            state["structured_requirements"] = result.get("requirements", [])
            state["acceptance_criteria"] = result.get("acceptance_criteria", [])
            state["estimated_complexity"] = result.get("estimated_complexity", "medium")
            state["current_step"] = "architecture"
        except json.JSONDecodeError:
            # 回退到默认结构
            state["structured_requirements"] = [{
                "id": "REQ-001",
                "title": requirement_text[:50],
                "description": requirement_text,
                "type": "feature",
                "priority": "medium"
            }]
            state["acceptance_criteria"] = []
            state["current_step"] = "architecture"
        
        return state
    
    def _generate_response(self, requirement_text: str) -> str:
        """生成模拟 LLM 响应"""
        return json.dumps({
            "requirements": [{
                "id": "REQ-001",
                "title": requirement_text[:50] if len(requirement_text) > 50 else requirement_text,
                "description": requirement_text,
                "type": "feature",
                "priority": "medium",
                "acceptance_criteria": ["功能正常运行", "测试通过"]
            }],
            "acceptance_criteria": [{
                "id": "AC-001",
                "given": "用户输入需求",
                "when": "提交分析请求",
                "then": "返回结构化分析结果"
            }],
            "estimated_complexity": "medium",
            "dependencies": []
        })
