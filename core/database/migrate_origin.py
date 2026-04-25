#!/usr/bin/env python3
"""
Database Migration - 添加 Origin 模型到 Smart Factory
运行: python migrate_origin.py
"""

import sqlite3
import os

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def migrate():
    conn = get_db()
    cursor = conn.cursor()
    
    print("=== Smart Factory 数据库迁移 ===")
    print(f"数据库: {DATABASE}")
    
    # 创建 projects 表
    print("\n1. 创建 projects 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            desc_alias TEXT,
            status TEXT DEFAULT 'active',
            repo_url TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    print("   ✅ projects 表完成")
    
    # 创建 requirements 表
    print("\n2. 创建 requirements 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    print("   ✅ requirements 表完成")
    
    # 创建 features 表
    print("\n3. 创建 features 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            tech_notes TEXT,
            art_asset_required TEXT,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (requirement_id) REFERENCES requirements(id)
        )
    """)
    print("   ✅ features 表完成")
    
    # 创建 test_cases 表
    print("\n4. 创建 test_cases 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            precondition TEXT,
            steps TEXT,
            expected_result TEXT,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (feature_id) REFERENCES features(id)
        )
    """)
    print("   ✅ test_cases 表完成")
    
    # 创建 dependencies 表
    print("\n5. 创建 dependencies 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            target_type TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            dep_type TEXT,
            created_at TEXT
        )
    """)
    print("   ✅ dependencies 表完成")
    
    # 创建 audit_logs 表
    print("\n6. 创建 audit_logs 表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            details TEXT,
            status TEXT DEFAULT 'success',
            created_at TEXT
        )
    """)
    print("   ✅ audit_logs 表完成")
    
    # 创建索引
    print("\n7. 创建索引...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_req_project ON requirements(project_id)",
        "CREATE INDEX IF NOT EXISTS idx_feat_requirement ON features(requirement_id)",
        "CREATE INDEX IF NOT EXISTS idx_tc_feature ON test_cases(feature_id)",
        "CREATE INDEX IF NOT EXISTS idx_dep_source ON dependencies(source_type, source_id)",
        "CREATE INDEX IF NOT EXISTS idx_dep_target ON dependencies(target_type, target_id)",
    ]
    for idx in indexes:
        cursor.execute(idx)
    print("   ✅ 索引完成")
    
    conn.commit()
    conn.close()
    
    print("\n=== 迁移完成 ===")
    print("新增表: projects, requirements, features, test_cases, dependencies, audit_logs")
    print("Origin 功能已合并到 Smart Factory!")

if __name__ == '__main__':
    migrate()
