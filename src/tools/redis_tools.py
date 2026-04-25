"""
LangFlow Factory - Redis 工具
"""
import redis
import json
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

class RedisTools:
    """Redis 工具集"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        
        # Stream 键名
        self.TASKS_STREAM = "smartfactory:stream:tasks"
        self.RESULTS_STREAM = "smartfactory:stream:results"
        self.STATE_PREFIX = "smartfactory:state:"
    
    def publish_task(self, task: Dict) -> str:
        """发布任务到 Stream"""
        task_id = task.get("task_id", f"task_{self._generate_id()}")
        task["task_id"] = task_id
        task["status"] = "pending"
        task["created_at"] = self._now()
        
        self.client.xadd(self.TASKS_STREAM, {
            "data": json.dumps(task),
            "priority": str(task.get("priority", 0))
        })
        return task_id
    
    def publish_result(self, result: Dict) -> str:
        """发布结果到 Results Stream"""
        result_id = result.get("task_id", f"result_{self._generate_id()}")
        result["completed_at"] = self._now()
        
        self.client.xadd(self.RESULTS_STREAM, {
            "data": json.dumps(result)
        })
        return result_id
    
    def get_task_result(self, task_id: str, timeout: int = 30) -> Optional[Dict]:
        """等待并获取任务结果"""
        stream_id = "0"
        start_time = timeout
        while timeout > 0:
            messages = self.client.xread({self.RESULTS_STREAM: stream_id}, count=1, block=1000)
            for stream, entries in messages:
                for msg_id, data in entries:
                    stream_id = msg_id
                    result_data = json.loads(data["data"])
                    if result_data.get("task_id") == task_id:
                        return result_data
            timeout -= 1
        return None
    
    def save_state(self, project_id: str, state: Dict) -> None:
        """保存项目状态"""
        key = f"{self.STATE_PREFIX}{project_id}"
        state["saved_at"] = self._now()
        self.client.set(key, json.dumps(state, default=str))
    
    def load_state(self, project_id: str) -> Optional[Dict]:
        """加载项目状态"""
        key = f"{self.STATE_PREFIX}{project_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def list_active_projects(self) -> List[str]:
        """列出活跃项目"""
        pattern = f"{self.STATE_PREFIX}*"
        keys = self.client.keys(pattern)
        return [k.replace(self.STATE_PREFIX, "") for k in keys]
    
    def delete_state(self, project_id: str) -> bool:
        """删除项目状态"""
        key = f"{self.STATE_PREFIX}{project_id}"
        return self.client.delete(key) > 0
    
    def _generate_id(self) -> str:
        return f"{int(datetime.now().timestamp() * 1000)}"
    
    def _now(self) -> str:
        return datetime.now().isoformat()
