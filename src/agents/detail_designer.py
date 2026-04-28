"""
LangFlow Factory - Detail Designer Agent
"""
from typing import Dict
import json
import os

DETAIL_DESIGNER_PROMPT = '''你是游戏开发详细设计师。将以下需求拆解为具体的开发任务列表。

项目：temple-run-three-kingdoms 三国跑酷游戏
平台：Godot 4.x

需求列表：
{requirements}

请拆解为可执行的任务列表，输出 JSON：
{{
  "detailed_tasks": [
    {{
      "id": "TASK-001",
      "title": "角色系统实现",
      "description": "实现三名武将角色的选择和基础能力",
      "requirements": "角色选择界面，三名角色赵云/关羽/张飞，不同初始属性",
      "estimated_hours": 8,
      "dependencies": []
    }},
    {{
      "id": "TASK-002",
      "title": "跑酷核心机制",
      "description": "实现角色自动向前跑，键盘/触摸控制",
      "requirements": "自动奔跑，跳跃(空格)，滑铲(下键)，左右移动",
      "estimated_hours": 12,
      "dependencies": ["TASK-001"]
    }},
    {{
      "id": "TASK-003",
      "title": "场景生成系统",
      "description": "程序化生成古典中国建筑场景",
      "requirements": "TileMap实现，宫殿/城墙/寺庙三种场景，随机生成",
      "estimated_hours": 16,
      "dependencies": []
    }},
    {{
      "id": "TASK-004",
      "title": "障碍物系统",
      "description": "实现跳跃和滑铲躲避的障碍物",
      "requirements": "低障碍(需跳跃)，高障碍(需滑铲)，随机分布",
      "estimated_hours": 8,
      "dependencies": ["TASK-002", "TASK-003"]
    }},
    {{
      "id": "TASK-005",
      "title": "金币收集系统",
      "description": "收集金币用于升级角色能力",
      "requirements": "金币生成，碰撞检测，累计显示，升级系统",
      "estimated_hours": 6,
      "dependencies": ["TASK-002"]
    }},
    {{
      "id": "TASK-006",
      "title": "分数和游戏结束",
      "description": "每100米记录分数，游戏结束处理",
      "requirements": "实时分数显示，最高分记录，游戏结束界面",
      "estimated_hours": 4,
      "dependencies": ["TASK-002"]
    }}
  ]
}}'''

class DetailDesigner:
    """详细设计师 Agent"""
    
    def __init__(self):
        self.name = "DetailDesigner"
        self.role = "任务拆分与测试用例"
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def process(self, state: Dict) -> Dict:
        """生成详细任务"""
        requirements = state.get("structured_requirements", [])
        
        if not requirements:
            requirements = [
                {"id": "REQ-001", "title": "角色系统", "description": "三名武将角色"},
                {"id": "REQ-002", "title": "场景生成", "description": "古典中国建筑"},
                {"id": "REQ-003", "title": "障碍物系统", "description": "跳跃/滑铲"},
                {"id": "REQ-004", "title": "金币收集", "description": "收集升级"},
                {"id": "REQ-005", "title": "分数系统", "description": "计分系统"},
                {"id": "REQ-006", "title": "操作控制", "description": "键盘触摸"},
            ]
        
        # 生成任务列表
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                req_text = "\n".join([f"- {r.get('id')}: {r.get('title')} - {r.get('description', '')}" 
                                     for r in requirements])
                prompt = DETAIL_DESIGNER_PROMPT.format(requirements=req_text)
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                result_text = response.choices[0].message.content
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                result = json.loads(result_text)
                state["detailed_tasks"] = result.get("detailed_tasks", [])
            except Exception as e:
                print(f"[DetailDesigner] LLM error: {e}, using default")
                state["detailed_tasks"] = self._default_tasks(requirements)
        else:
            state["detailed_tasks"] = self._default_tasks(requirements)
        
        state["current_step"] = "dispatch"
        return state
    
    def _default_tasks(self, requirements) -> list:
        """默认任务列表"""
        tasks = []
        task_id = 1
        
        # 映射需求到任务
        req_to_task = {
            "REQ-001": {"title": "角色系统实现", "hours": 8},
            "REQ-002": {"title": "场景生成系统", "hours": 16},
            "REQ-003": {"title": "障碍物系统", "hours": 8},
            "REQ-004": {"title": "金币收集系统", "hours": 6},
            "REQ-005": {"title": "分数系统", "hours": 4},
            "REQ-006": {"title": "操作控制系统", "hours": 6},
        }
        
        for req in requirements:
            req_id = req.get("id", "")
            task_info = req_to_task.get(req_id, {"title": req.get("title", f"Task {task_id}"), "hours": 4})
            tasks.append({
                "id": f"TASK-{task_id:03d}",
                "title": task_info["title"],
                "description": req.get("description", ""),
                "requirements": req.get("description", ""),
                "estimated_hours": task_info["hours"],
                "dependencies": []
            })
            task_id += 1
        
        # 添加一些核心任务
        if len(tasks) < 4:
            tasks.extend([
                {"id": "TASK-MAIN", "title": "主场景和游戏循环", "hours": 12, "description": "主场景和游戏主循环", "dependencies": []},
                {"id": "TASK-UI", "title": "UI界面系统", "hours": 6, "description": "开始界面、分数显示、游戏结束界面", "dependencies": []},
            ])
        
        return tasks
