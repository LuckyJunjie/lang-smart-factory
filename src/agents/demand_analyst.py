"""
LangFlow Factory - Demand Analyst Agent
"""
from typing import Dict
import json
import os

DEMAND_ANALYST_PROMPT = '''你是资深游戏需求分析师。根据以下需求，拆解为详细的功能需求列表。

游戏名称：temple-run-three-kingdoms（三国跑酷）
类型：跑酷游戏，跑酷+收集
平台：Godot 4.x

需求文本：
{requirement_text}

请输出 JSON 格式的需求列表：
{{
  "requirements": [
    {{
      "id": "REQ-001",
      "title": "角色系统",
      "description": "可选择赵云、关羽、张飞三名角色，每个角色有不同的初始能力和特效",
      "type": "feature",
      "priority": "high",
      "acceptance_criteria": ["可以选择三名角色", "角色有不同属性", "角色有独特技能特效"]
    }},
    {{
      "id": "REQ-002", 
      "title": "场景生成",
      "description": "程序化生成古典中国建筑场景，包括宫殿、城墙、寺庙等",
      "type": "feature", 
      "priority": "high",
      "acceptance_criteria": ["场景自动生成", "古典中国风格", "无限跑酷"]
    }},
    {{
      "id": "REQ-003",
      "title": "障碍物系统",
      "description": "包括滑铲、跳跃躲避的障碍物",
      "type": "feature",
      "priority": "high",
      "acceptance_criteria": ["障碍物随机出现", "跳跃躲避低矮障碍", "滑铲躲避高障碍"]
    }},
    {{
      "id": "REQ-004",
      "title": "金币收集",
      "description": "收集金币用于升级角色能力",
      "type": "feature",
      "priority": "medium",
      "acceptance_criteria": ["金币随机分布", "收集有音效", "金币累计显示"]
    }},
    {{
      "id": "REQ-005",
      "title": "分数系统",
      "description": "每100米记录分数，记录最高分",
      "type": "feature",
      "priority": "high",
      "acceptance_criteria": ["实时显示分数", "保存最高分", "分数排行榜"]
    }},
    {{
      "id": "REQ-006",
      "title": "操作控制",
      "description": "键盘和触摸操作支持",
      "type": "feature",
      "priority": "high",
      "acceptance_criteria": ["空格跳跃", "下滑铲", "左右移动", "触摸支持"]
    }}
  ],
  "acceptance_criteria": [
    {{
      "id": "AC-001",
      "given": "玩家启动游戏",
      "when": "点击开始",
      "then": "角色开始跑酷"
    }},
    {{
      "id": "AC-002",
      "given": "玩家按空格",
      "when": "遇到低矮障碍",
      "then": "角色跳跃躲避"
    }},
    {{
      "id": "AC-003",
      "given": "玩家向下滑动/按下滑键",
      "when": "遇到高障碍",
      "then": "角色滑铲躲避"
    }},
    {{
      "id": "AC-004",
      "given": "收集金币",
      "when": "角色触碰金币",
      "then": "金币消失并增加计数"
    }},
    {{
      "id": "AC-005",
      "given": "撞到障碍物",
      "when": "未成功躲避",
      "then": "游戏结束并显示分数"
    }}
  ],
  "estimated_complexity": "high",
  "dependencies": ["Godot 4.x", "2D Engine"]
}}'''

class DemandAnalyst:
    """需求分析师 Agent"""
    
    def __init__(self):
        self.name = "DemandAnalyst"
        self.role = "需求分析与拆解"
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def process(self, state: Dict) -> Dict:
        """分析需求"""
        requirement_text = state.get("raw_requirement", "")
        
        if not requirement_text:
            state["error"] = "No requirement text provided"
            return state
        
        # 使用实际 LLM 或预定义模板
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                prompt = DEMAND_ANALYST_PROMPT.format(requirement_text=requirement_text)
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                result_text = response.choices[0].message.content
                # 提取 JSON
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                result = json.loads(result_text)
                state["structured_requirements"] = result.get("requirements", [])
                state["acceptance_criteria"] = result.get("acceptance_criteria", [])
                state["estimated_complexity"] = result.get("estimated_complexity", "medium")
            except Exception as e:
                print(f"[DemandAnalyst] LLM error: {e}, using default")
                result = self._default_analysis(requirement_text)
                state.update(result)
        else:
            # 使用默认分析
            result = self._default_analysis(requirement_text)
            state.update(result)
        
        state["current_step"] = "architecture"
        return state
    
    def _default_analysis(self, requirement_text: str) -> Dict:
        """默认需求分析"""
        return {
            "structured_requirements": [
                {"id": "REQ-001", "title": "角色系统", "description": "三名三国武将角色", "type": "feature", "priority": "high"},
                {"id": "REQ-002", "title": "场景生成", "description": "古典中国建筑跑酷场景", "type": "feature", "priority": "high"},
                {"id": "REQ-003", "title": "障碍物系统", "description": "跳跃和滑铲躲避障碍", "type": "feature", "priority": "high"},
                {"id": "REQ-004", "title": "金币收集", "description": "收集金币升级角色", "type": "feature", "priority": "medium"},
                {"id": "REQ-005", "title": "分数系统", "description": "每100米记录分数", "type": "feature", "priority": "high"},
                {"id": "REQ-006", "title": "操作控制", "description": "键盘和触摸操作", "type": "feature", "priority": "high"},
            ],
            "acceptance_criteria": [
                {"id": "AC-001", "given": "玩家开始游戏", "when": "点击开始", "then": "角色跑酷"},
                {"id": "AC-002", "given": "按空格", "when": "遇障碍", "then": "跳跃躲避"},
                {"id": "AC-003", "given": "滑动/下滑键", "when": "遇高障碍", "then": "滑铲躲避"},
                {"id": "AC-004", "given": "收集金币", "when": "触碰金币", "then": "金币增加"},
                {"id": "AC-005", "given": "撞障碍", "when": "未躲避", "then": "游戏结束"},
            ],
            "estimated_complexity": "high",
        }
