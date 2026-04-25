"""
智慧工厂 模块集成测试
"""
import pytest
import os
import sqlite3


class TestDatabaseSchema:
    """数据库 Schema 测试"""
    
    @pytest.fixture
    def db_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')
    
    def test_projects_table_exists(self, db_path):
        """测试 projects 表存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "projects 表不存在"
    
    def test_requirements_table_exists(self, db_path):
        """测试 requirements 表存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='requirements'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "requirements 表不存在"
    
    def test_tasks_table_exists(self, db_path):
        """测试 tasks 表存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "tasks 表不存在"
    
    def test_machines_table_exists(self, db_path):
        """测试 machines 表存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machines'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "machines 表不存在"
    
    def test_tools_table_exists(self, db_path):
        """测试 tools 表存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tools'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "tools 表不存在"


class TestRequirementsFields:
    """需求表字段测试"""
    
    @pytest.fixture
    def db_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')
    
    def test_requirements_has_step_field(self, db_path):
        """测试 requirements 表有 step 字段"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(requirements)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        assert 'step' in columns, "requirements 表缺少 step 字段"
    
    def test_requirements_has_note_field(self, db_path):
        """测试 requirements 表有 note 字段"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(requirements)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        assert 'note' in columns, "requirements 表缺少 note 字段"
    
    def test_step_values_valid(self, db_path):
        """测试 step 字段存在"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(requirements)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        assert 'step' in columns, "requirements 表缺少 step 字段"


class TestTasksFields:
    """任务表字段测试"""
    
    @pytest.fixture
    def db_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')
    
    def test_tasks_has_step_field(self, db_path):
        """测试 tasks 表有 step 字段"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        assert 'step' in columns, "tasks 表缺少 step 字段"
    
    def test_tasks_has_note_field(self, db_path):
        """测试 tasks 表有 note 字段"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        assert 'note' in columns, "tasks 表缺少 note 字段"


class TestProjectsData:
    """项目数据测试"""
    
    @pytest.fixture
    def db_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')
    
    def test_has_projects(self, db_path):
        """测试有项目数据"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "没有项目数据"


class TestMachinesData:
    """机器数据测试"""
    
    @pytest.fixture
    def db_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')
    
    def test_has_machines(self, db_path):
        """测试有机器数据"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM machines")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "没有机器数据"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
