"""
LangFlow Factory - Base Agent
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import json

class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    @abstractmethod
    def process(self, state: Dict) -> Dict:
        """处理状态，返回更新后的状态"""
        pass
    
    def invoke_llm(self, prompt: str, llm=None) -> str:
        """调用 LLM - 优先使用 OpenAI，其次本地模型"""
        
        # 如果有 OpenAI API key，使用它
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLM] OpenAI error: {e}")
        
        # 回退：返回带结构的响应，让子类处理
        return json.dumps({
            "status": "llm_unavailable",
            "prompt_preview": prompt[:100],
            "fallback": True
        })
