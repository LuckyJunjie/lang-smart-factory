"""
LangFlow Factory - Worker Base
"""
import json
import time
from typing import Dict, Callable
from .tools.redis_tools import RedisTools
from .tools.feishu_tools import FeishuNotifier

class Worker:
    """Worker 基类 - 监听 Redis Stream 并执行任务"""
    
    def __init__(self, worker_name: str, task_handler: Callable = None):
        self.worker_name = worker_name
        self.task_handler = task_handler
        self.redis_tools = RedisTools()
        self.feishu = FeishuNotifier()
        self.running = False
    
    def start(self):
        """启动 Worker"""
        self.running = True
        print(f"[{self.worker_name}] Worker started, listening for tasks...")
        
        last_id = "0"
        while self.running:
            try:
                messages = self.redis_tools.client.xread(
                    {self.redis_tools.TASKS_STREAM: last_id},
                    count=1,
                    block=1000
                )
                
                for stream, entries in messages:
                    for msg_id, data in entries:
                        last_id = msg_id
                        task_data = json.loads(data["data"])
                        
                        if self._should_handle(task_data):
                            self._process_task(task_data)
                            
            except Exception as e:
                print(f"[{self.worker_name}] Error: {e}")
                time.sleep(1)
    
    def stop(self):
        """停止 Worker"""
        self.running = False
        print(f"[{self.worker_name}] Worker stopped")
    
    def _should_handle(self, task: Dict) -> bool:
        """判断是否应该处理此任务"""
        return True
    
    def _process_task(self, task_data: Dict):
        """处理任务"""
        print(f"[{self.worker_name}] Processing task: {task_data.get('task_id')}")
        
        try:
            if self.task_handler:
                result = self.task_handler(task_data)
            else:
                result = {"status": "placeholder", "message": "No handler configured"}
            
            result_data = {
                "worker": self.worker_name,
                "task_id": task_data.get("task_id"),
                "status": "success",
                "result": result
            }
            self.redis_tools.publish_result(result_data)
            print(f"[{self.worker_name}] Task completed: {task_data.get('task_id')}")
            
        except Exception as e:
            error_result = {
                "worker": self.worker_name,
                "task_id": task_data.get("task_id"),
                "status": "failed",
                "error": str(e)
            }
            self.redis_tools.publish_result(error_result)
            print(f"[{self.worker_name}] Task failed: {task_data.get('task_id')} - {e}")
