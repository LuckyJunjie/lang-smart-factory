"""
LangFlow Factory - MiniMax LLM Client
"""
import os
import json
import requests
from typing import Optional

MINIMAX_API_URL = "https://api.minimaxi.com/v1/chat/completions"
MINIMAX_TOKEN = "sk-cp-fpe8voBPHxnCK_wO0osZmdJ9-Hb3qwq416OF6aDy_eZrAX7Lf4eZE163sUbwS9Ue4yV5lfhL1bGop9y42YJCVahhGXl35BY06G9l6d2Bc2vql3bqFhNMVew"
MODEL = "MiniMax-M2.7"
SYSTEM_PROMPT = "You are a helpful assistant. Output ONLY the answer, no explanation."

class LLMClient:
    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or MINIMAX_TOKEN
        self.model = MODEL
        self.base_url = MINIMAX_API_URL
    
    def generate(self, prompt: str, system: str = "", max_tokens: int = 4096) -> str:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                # MiniMax M2.7 outputs thinking block followed by \n\n and actual answer
                # Extract actual answer: everything after the last \n\n
                idx = content.rfind("\n\n")
                if idx >= 0:
                    return content[idx+4:].strip()
                return content.strip()
            else:
                return f"LLM Error: {response.status_code}"
        except Exception as e:
            return f"LLM Exception: {str(e)}"

llm_client = LLMClient()
