"""
GodotTools 单元测试
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class TestGodotTools:
    """Godot 工具测试"""
    
    def test_init(self):
        """测试初始化"""
        from src.tools.godot_tools import GodotTools
        tools = GodotTools("godot", "/path/to/project")
        assert tools.godot_path == "godot"
        assert tools.project_path == "/path/to/project"
    
    @patch('subprocess.Popen')
    def test_launch_game(self, mock_popen):
        """测试启动游戏"""
        from src.tools.godot_tools import GodotTools
        mock_popen.return_value = MagicMock()
        tools = GodotTools()
        result = tools.launch_game()
        assert result is True
    
    def test_analyze_framerate(self):
        """测试帧率分析"""
        from src.tools.godot_tools import GodotTools
        tools = GodotTools()
        result = tools.analyze_framerate(duration=5)
        assert "avg_fps" in result
        assert "stable" in result
    
    @patch('subprocess.run')
    def test_take_screenshot(self, mock_run):
        """测试截图"""
        from src.tools.godot_tools import GodotTools
        mock_run.return_value = MagicMock()
        tools = GodotTools()
        result = tools.take_screenshot("/tmp/screenshot.png")
        assert mock_run.called
