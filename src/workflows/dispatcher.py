"""
LangFlow Factory - Dispatcher
"""
from typing import Dict, List
from ..tools.redis_tools import RedisTools

class Dispatcher:
    """任务派发器"""
    
    def __init__(self):
        self.redis_tools = RedisTools()
    
    def dispatch_tasks(self, tasks: List[Dict], project_id: str) -> List[str]:
        """派发任务到 Redis Stream"""
        task_ids = []
        for task in tasks:
            task_payload = {
                "project_id": project_id,
                "task": task,
                "type": "implementation"
            }
            try:
                task_id = self.redis_tools.publish_task(task_payload)
                task_ids.append(task_id)
            except Exception as e:
                print(f"Failed to dispatch task {task.get('id')}: {e}")
        return task_ids
    
    def wait_for_results(self, task_ids: List[str], timeout: int = 300) -> List[Dict]:
        """等待任务结果"""
        results = []
        for task_id in task_ids:
            try:
                result = self.redis_tools.get_task_result(task_id, timeout=timeout//len(task_ids) if task_ids else 30)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Failed to get result for {task_id}: {e}")
        return results
    
    def dispatch_and_wait(self, tasks: List[Dict], project_id: str) -> List[Dict]:
        """派发并等待结果"""
        task_ids = self.dispatch_tasks(tasks, project_id)
        return self.wait_for_results(task_ids)
    
    def dispatch_single(self, task: Dict, project_id: str) -> str:
        """派发单个任务"""
        task_payload = {
            "project_id": project_id,
            "task": task,
            "type": task.get("type", "implementation")
        }
        return self.redis_tools.publish_task(task_payload)
