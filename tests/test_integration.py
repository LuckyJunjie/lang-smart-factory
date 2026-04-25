"""
智慧工厂 API 集成测试
"""
import pytest
import sqlite3
import os
import sys

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'core', 'db', 'factory.db')


class TestDatabaseConnection:
    """数据库连接测试"""
    
    def test_database_exists(self):
        """测试数据库文件存在"""
        assert os.path.exists(DB_PATH), f"数据库不存在: {DB_PATH}"
    
    def test_database_readable(self):
        """测试数据库可读"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        assert result[0] == 1


class TestProjectsTable:
    """项目表测试"""
    
    def test_list_projects(self):
        """测试列出项目"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) > 0, "项目表为空"
    
    def test_project_fields(self):
        """测试项目表字段"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(projects)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        required = {'id', 'name', 'description', 'type', 'status', 'created_at', 'updated_at'}
        assert required.issubset(columns), f"缺少字段: {required - columns}"


class TestRequirementsTable:
    """需求表测试"""
    
    def test_requirements_table_exists(self):
        """测试需求表存在"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='requirements'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None
    
    def test_requirements_fields(self):
        """测试需求表字段"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(requirements)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        required = {'id', 'project_id', 'title', 'description', 'priority', 'status', 'step', 'note'}
        assert required.issubset(columns), f"缺少字段: {required - columns}"
    
    def test_step_values_constraint(self):
        """测试 step 字段约束"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(requirements)")
        for row in cursor.fetchall():
            if row[1] == 'step':
                # 检查字段有默认值 (可能是 'not start' 或 "'not start")
                default = str(row[4]).strip("'")
                assert default == 'not start', f"step 默认值错误: {row[4]}"
        conn.close()
    
    def test_requirements_data(self):
        """测试需求数据"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requirements WHERE project_id = 2")
        rows = cursor.fetchall()
        conn.close()
        # pinball-experience 应该有需求数据
        assert len(rows) >= 1, "pinball-experience 缺少需求数据"
    
    def test_pinball_requirement_step(self):
        """测试 pinball 需求 step 字段"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT step, note FROM requirements WHERE project_id = 2 ORDER BY id")
        row = cursor.fetchone()
        conn.close()
        if row:
            assert row['step'] in ['not start', 'analyse', 'implement', 'test', 'verify', 'done'], \
                f"step 值无效: {row['step']}"


class TestTasksTable:
    """任务表测试"""
    
    def test_tasks_table_exists(self):
        """测试任务表存在"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None
    
    def test_tasks_fields(self):
        """测试任务表字段"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        required = {'id', 'req_id', 'title', 'description', 'status', 'step', 'note'}
        assert required.issubset(columns), f"缺少字段: {required - columns}"


class TestMachinesTable:
    """机器表测试"""
    
    def test_machines_table_exists(self):
        """测试机器表存在"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='machines'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None
    
    def test_machines_data(self):
        """测试机器数据"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines")
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) >= 1, "机器表为空"


class TestToolsTable:
    """工具表测试"""
    
    def test_tools_table_exists(self):
        """测试工具表存在"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tools'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None


class TestDatabaseIntegrity:
    """数据库完整性测试"""
    
    def test_foreign_keys(self):
        """测试外键约束"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 检查 requirements.project_id 引用 projects.id
        cursor.execute("SELECT COUNT(*) FROM requirements WHERE project_id NOT IN (SELECT id FROM projects)")
        orphan = cursor.fetchone()[0]
        conn.close()
        assert orphan == 0, f"存在无效的 project_id 引用: {orphan} 条"
    
    def test_no_null_titles(self):
        """测试需求标题不为空"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM requirements WHERE title IS NULL OR title = ''")
        null_count = cursor.fetchone()[0]
        conn.close()
        assert null_count == 0, f"存在空标题: {null_count} 条"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
