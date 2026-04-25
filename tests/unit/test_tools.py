"""
Tools 单元测试
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class TestRedisTools:
    """Redis 工具测试"""
    
    @patch('src.tools.redis_tools.redis')
    def test_init(self, mock_redis):
        """测试初始化"""
        from src.tools.redis_tools import RedisTools
        
        tools = RedisTools()
        assert tools.TASKS_STREAM == "smartfactory:stream:tasks"
        assert tools.RESULTS_STREAM == "smartfactory:stream:results"
        assert tools.STATE_PREFIX == "smartfactory:state:"
    
    @patch('src.tools.redis_tools.redis')
    def test_generate_id(self, mock_redis):
        """测试 ID 生成"""
        from src.tools.redis_tools import RedisTools
        
        tools = RedisTools()
        id1 = tools._generate_id()
        id2 = tools._generate_id()
        
        assert len(id1) > 0  # ID generated
        assert len(id1) > 0

class TestGitTools:
    """Git 工具测试"""
    
    def test_init(self):
        """测试初始化"""
        from src.tools.git_tools import GitTools
        
        tools = GitTools("/tmp/test-repo")
        assert tools.repo_path == "/tmp/test-repo"
    
    @patch('subprocess.run')
    def test_get_current_commit(self, mock_run):
        """测试获取当前 commit"""
        from src.tools.git_tools import GitTools
        
        mock_result = MagicMock()
        mock_result.stdout = b"abc123def456"
        mock_run.return_value = mock_result
        
        tools = GitTools("/tmp/test-repo")
        commit = tools.get_current_commit()
        
        assert commit == "abc123def456"
    
    @patch('subprocess.run')
    def test_get_branch(self, mock_run):
        """测试获取分支"""
        from src.tools.git_tools import GitTools
        
        mock_result = MagicMock()
        mock_result.stdout = b"main"
        mock_run.return_value = mock_result
        
        tools = GitTools("/tmp/test-repo")
        branch = tools.get_branch()
        
        assert branch == "main"

class TestSmartFactoryAPI:
    """API 工具测试"""
    
    @patch('src.tools.api_tools.requests.get')
    def test_get_project(self, mock_get):
        """测试获取项目"""
        from src.tools.api_tools import SmartFactoryAPI
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_get.return_value = mock_response
        
        api = SmartFactoryAPI()
        result = api.get_project(1)
        
        assert result == {"id": 1, "name": "Test"}
    
    @patch('src.tools.api_tools.requests.get')
    def test_get_project_not_found(self, mock_get):
        """测试项目不存在"""
        from src.tools.api_tools import SmartFactoryAPI
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        api = SmartFactoryAPI()
        result = api.get_project(999)
        
        assert result is None

class TestFeishuNotifier:
    """飞书通知测试"""
    
    def test_init_without_webhook(self):
        """测试无 webhook 初始化"""
        from src.tools.feishu_tools import FeishuNotifier
        
        notifier = FeishuNotifier(webhook=None)
        assert notifier.webhook is None
    
    def test_send_text_without_webhook(self):
        """测试无 webhook 发送"""
        from src.tools.feishu_tools import FeishuNotifier
        
        notifier = FeishuNotifier(webhook=None)
        result = notifier.send_text("Test message")
        
        assert result is False
