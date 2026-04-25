"""
LangFlow Factory - Base Agent
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    @abstractmethod
    def process(self, state: Dict) -> Dict:
        """处理状态，返回更新后的状态"""
        pass
    
    def invoke_llm(self, prompt: str, llm=None) -> str:
        """调用 LLM"""
        # Placeholder - 实际需要集成 LangChain LLM
        return f"[LLM Response for: {prompt[:50]}...]"
