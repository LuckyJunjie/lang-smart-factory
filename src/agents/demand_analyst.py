"""
LangFlow Factory - Demand Analyst Agent
使用 LLM 分析需求，输出结构化需求列表
"""
from typing import Dict
import json
from ..llm.minimax_client import llm_client

ANALYSIS_PROMPT_TEMPLATE = """分析以下需求，输出结构化JSON需求列表。

需求：{requirement}

要求：
- 每个需求包含: id, title, type (feature/performance/ux/security), priority (high/medium/low)
- description: 详细描述
- acceptance_criteria: Given-When-Then格式的验收标准数组
- estimated_complexity: low/medium/high
- 识别跨需求依赖关系

只输出JSON数组，不要解释。"""

class DemandAnalyst:
    def __init__(self):
        self.name = "DemandAnalyst"
        self.role = "需求分析"
    
    def process(self, state: Dict) -> Dict:
        requirement = state.get("raw_requirement", "")
        if not requirement:
            state["error"] = "No requirement provided"
            return state
        
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(requirement=requirement)
        print(f"[DemandAnalyst] Analyzing: {requirement[:50]}...")
        
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
            
            requirements = json.loads(json_str)
            state["structured_requirements"] = requirements
            
            high = sum(1 for r in requirements if r.get("priority") == "high")
            state["estimated_complexity"] = "high" if high >= 5 else "medium" if high >= 3 else "low"
            state["current_step"] = "architecture"
            print(f"[DemandAnalyst] Generated {len(requirements)} requirements, complexity: {state['estimated_complexity']}")
        except json.JSONDecodeError as e:
            print(f"[DemandAnalyst] JSON parse error: {e}, response: {response[:200]}")
            state["structured_requirements"] = [{"id": "REQ-001", "title": "核心功能", "type": "feature", "priority": "high", "description": requirement, "acceptance_criteria": ["功能可运行"], "estimated_complexity": "medium"}]
            state["estimated_complexity"] = "medium"
            state["current_step"] = "architecture"
        
        return state
