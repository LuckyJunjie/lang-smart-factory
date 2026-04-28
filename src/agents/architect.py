"""
LangFlow Factory - Architect Agent
"""
from typing import Dict
import json
import os

ARCHITECT_PROMPT = """你是资深游戏架构师。根据以下需求，设计三国跑酷游戏的系统架构。

需求列表：
{requirements}

请输出 JSON 格式的架构文档，包含 modules, tech_stack, integration_points, data_flow。
只输出 JSON，不要解释。"""

class Architect:
    """架构师 Agent"""
    
    def __init__(self):
        self.name = "Architect"
        self.role = "系统架构设计"
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def process(self, state: Dict) -> Dict:
        """设计架构"""
        requirements = state.get("structured_requirements", [])
        
        if not requirements:
            state["error"] = "No requirements provided"
            state["current_step"] = "detail_design"
            return state
        
        # 生成架构
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                req_text = "\n".join([f"- {r.get('id')}: {r.get('title')} - {r.get('description', '')}" 
                                     for r in requirements])
                prompt = ARCHITECT_PROMPT.format(requirements=req_text)
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                result_text = response.choices[0].message.content
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                result = json.loads(result_text)
                state["architecture_doc"] = result
                state["current_step"] = "detail_design"
                return state
            except Exception as e:
                print(f"[Architect] LLM error: {e}, using default")
        
        # 默认架构（针对三国跑酷游戏优化）
        state["architecture_doc"] = {
            "modules": [
                {
                    "name": "character",
                    "description": "角色系统 - 管理赵云/关羽/张飞三名武将角色的选择、属性和动画",
                    "dependencies": []
                },
                {
                    "name": "scene_generator",
                    "description": "场景生成器 - 程序化生成古典中国建筑跑酷场景",
                    "dependencies": []
                },
                {
                    "name": "obstacle_manager",
                    "description": "障碍物管理器 - 管理跳跃和滑铲躲避的障碍物生成和碰撞",
                    "dependencies": ["scene_generator"]
                },
                {
                    "name": "coin_system",
                    "description": "金币系统 - 金币生成、收集、累计和升级逻辑",
                    "dependencies": ["character"]
                },
                {
                    "name": "score_manager",
                    "description": "分数管理器 - 每100米记录分数，保存最高分",
                    "dependencies": []
                },
                {
                    "name": "input_controller",
                    "description": "输入控制器 - 键盘和触摸操作支持",
                    "dependencies": ["character"]
                },
                {
                    "name": "game_loop",
                    "description": "游戏主循环 - 控制跑酷流程、游戏状态和游戏结束逻辑",
                    "dependencies": ["character", "obstacle_manager", "coin_system", "score_manager"]
                },
                {
                    "name": "ui_manager",
                    "description": "UI管理器 - 开始界面、分数显示、游戏结束界面",
                    "dependencies": ["score_manager"]
                }
            ],
            "tech_stack": {
                "engine": "Godot 4.x",
                "language": "GDScript",
                "rendering": "2D",
                "platforms": ["Android", "Windows"],
                "audio": "Godot AudioStream"
            },
            "integration_points": [
                "character_signal: jump_requested, slide_requested, move_requested",
                "scene_signal: obstacle_spawned, coin_spawned, distance_updated",
                "game_signal: game_over, score_updated, coin_collected"
            ],
            "data_flow": "Input -> InputController -> Character -> GameLoop -> Collision -> Score/Coin/Health"
        }
        state["current_step"] = "detail_design"
        return state
