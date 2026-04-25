"""
GameEvaluator 单元测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.game_evaluator import GamePlayEvaluator

class TestGameEvaluator:
    """游戏评估器测试"""
    
    def test_evaluator_init(self):
        """测试评估器初始化"""
        evaluator = GamePlayEvaluator()
        assert evaluator.name == "GamePlayEvaluator"
        assert evaluator.role == "游戏性评估"
    
    def test_process_with_game_data(self):
        """测试处理游戏数据"""
        evaluator = GamePlayEvaluator()
        state = {
            "game_data": {"name": "test-game", "fps_stability": "stable"},
            "next_step": "testing"
        }
        result = evaluator.process(state)
        assert "game_eval_report" in result
        assert "fun_rating" in result["game_eval_report"]
    
    def test_generate_eval_returns_valid_report(self):
        """测试生成评估报告"""
        evaluator = GamePlayEvaluator()
        game_data = {"name": "test"}
        result = evaluator._generate_eval(game_data)
        assert "fun_rating" in result
        assert 1 <= result["fun_rating"] <= 5
        assert "control_feel" in result
        assert "difficulty_balance" in result
    
    def test_fun_rating_range(self):
        """测试评分范围"""
        evaluator = GamePlayEvaluator()
        for _ in range(5):
            result = evaluator._generate_eval({})
            assert 1 <= result["fun_rating"] <= 5
