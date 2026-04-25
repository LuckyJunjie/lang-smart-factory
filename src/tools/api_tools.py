"""
LangFlow Factory - Smart Factory API 工具
"""
import requests
from typing import Dict, List, Optional, Any
import os

class SmartFactoryAPI:
    """Smart Factory API 客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("SMART_FACTORY_API", "http://192.168.3.75:5000")
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """获取项目"""
        try:
            r = requests.get(f"{self.base_url}/api/projects/{project_id}", timeout=10)
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
    
    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        try:
            r = requests.get(f"{self.base_url}/api/projects", timeout=10)
            return r.json().get("projects", []) if r.status_code == 200 else []
        except Exception:
            return []
    
    def create_requirement(self, project_id: int, requirement: Dict) -> Optional[Dict]:
        """创建需求"""
        try:
            r = requests.post(
                f"{self.base_url}/api/projects/{project_id}/requirements",
                json=requirement,
                timeout=10
            )
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
    
    def create_task(self, project_id: int, task: Dict) -> Optional[Dict]:
        """创建任务"""
        try:
            r = requests.post(
                f"{self.base_url}/api/projects/{project_id}/tasks",
                json=task,
                timeout=10
            )
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
    
    def update_project_progress(self, project_id: int, progress: int) -> bool:
        """更新项目进度"""
        try:
            r = requests.patch(
                f"{self.base_url}/api/projects/{project_id}",
                json={"progress_percent": progress},
                timeout=10
            )
            return r.status_code == 200
        except Exception:
            return False
