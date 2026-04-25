"""
ID Generator Service - 适配 Smart Factory 表结构
"""

import sqlite3
import os
from datetime import datetime

DATABASE = '/home/pi/.openclaw/workspace/smart-factory/core/db/factory.db'
LOCK_DIR = '/tmp/smart_factory_id_locks'

os.makedirs(LOCK_DIR, exist_ok=True)

# Smart Factory 表配置
TABLE_CONFIG = {
    'project': {'table': 'projects', 'name_col': 'name'},
    'requirement': {'table': 'requirements', 'name_col': 'title'},
    'task': {'table': 'tasks', 'name_col': 'title'},
}


def generate_code(entity_type: str) -> str:
    """生成规范化编码: P001, REQ001, TASK001"""
    prefix_map = {'project': 'P', 'requirement': 'REQ', 'task': 'TASK'}
    prefix = prefix_map.get(entity_type, entity_type.upper()[:3])
    
    config = TABLE_CONFIG.get(entity_type, {'table': entity_type, 'name_col': 'name'})
    table = config['table']
    
    lock_file = os.path.join(LOCK_DIR, f'{entity_type}.lock')
    
    # 简单文件锁
    for _ in range(50):
        try:
            with open(lock_file, 'x') as f:
                f.write(str(os.getpid()))
            break
        except FileExistsError:
            import time
            time.sleep(0.02)
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT MAX(id) FROM {table}')
        max_id = cursor.fetchone()[0] or 0
        
        next_num = max_id + 1
        code = f'{prefix}{next_num:03d}'
        
        conn.close()
        return code
    finally:
        try:
            os.remove(lock_file)
        except:
            pass


def get_entity_by_code(code: str) -> dict:
    """通过编码查找实体"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 尝试各表
    for table in ['projects', 'requirements', 'tasks']:
        cursor.execute(f'SELECT *, "{table}" as entity_type FROM {table} WHERE id = ?', 
                      (int(code.split('_')[-1]) if '_' in code else int(code[3:]),))
        row = cursor.fetchone()
        if row:
            conn.close()
            return dict(row)
    
    conn.close()
    return None
