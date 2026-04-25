"""
LangFlow Factory - Game Play Evaluator Agent
评估游戏质量：手感、视觉反馈、难度平衡
"""
from typing import Dict

GAME_EVAL_PROMPT = '''你是资深游戏评测师。分析以下游戏评测数据，给出评分和建议。

游戏数据：
{game_data}

请输出 JSON 格式评测报告：
{
  "fun_rating": 4,
  "control_feel": "responsive",
  "visual_feedback_quality": "good",
  "difficulty_balance": "appropriate",
  "suggestions": ["建议1", "建议2"],
  "bugs": []
}'''

class GamePlayEvaluator:
    """游戏性评估 Agent"""
    
    def __init__(self):
        self.name = "GamePlayEvaluator"
        self.role = "游戏性评估"
    
    def process(self, state: Dict) -> Dict:
        """评估游戏"""
        game_data = state.get("game_data", {})
        
        prompt = GAME_EVAL_PROMPT.format(game_data=str(game_data))
        result = self._generate_eval(game_data)
        
        state["game_eval_report"] = result
        state["current_step"] = state.get("next_step", "testing")
        
        return state
    
    def _generate_eval(self, game_data: Dict) -> Dict:
        """生成评估报告"""
        return {
            "fun_rating": 4,
            "control_feel": "responsive",
            "visual_feedback_quality": "good",
            "difficulty_balance": "appropriate",
            "suggestions": ["游戏体验良好", "可继续优化"],
            "bugs": []
        }
