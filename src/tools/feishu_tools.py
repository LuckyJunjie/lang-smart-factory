"""
LangFlow Factory - 飞书通知工具
"""
import requests
from typing import Dict, Optional
import os

class FeishuNotifier:
    """飞书通知"""
    
    def __init__(self, webhook: str = None):
        self.webhook = webhook or os.getenv("FEISHU_WEBHOOK")
    
    def send_text(self, text: str) -> bool:
        """发送文本消息"""
        if not self.webhook:
            print(f"[Feishu] Not configured, skipping: {text[:50]}...")
            return False
        
        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }
        
        try:
            r = requests.post(self.webhook, json=payload, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
    
    def send_card(self, title: str, content: str, status: str = "info") -> bool:
        """发送卡片消息"""
        if not self.webhook:
            print(f"[Feishu] Not configured, skipping card: {title}")
            return False
        
        color_map = {
            "info": "#3498db",
            "success": "#2ecc71", 
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": color_map.get(status, "#3498db")
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": content}}
                ]
            }
        }
        
        try:
            r = requests.post(self.webhook, json=payload, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
    
    def notify_workflow_complete(self, project_id: str, step: str, result: str) -> bool:
        """通知工作流完成"""
        return self.send_card(
            title=f"✅ LangFlow Workflow 完成",
            content=f"**项目:** {project_id}\n**步骤:** {step}\n**结果:** {result}",
            status="success"
        )
    
    def notify_error(self, project_id: str, error: str) -> bool:
        """通知错误"""
        return self.send_card(
            title=f"❌ LangFlow Workflow 错误",
            content=f"**项目:** {project_id}\n**错误:** {error}",
            status="error"
        )
