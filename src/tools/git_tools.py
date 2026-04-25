"""
LangFlow Factory - Git 工具
"""
import subprocess
import os
from typing import Dict, Optional, List

class GitTools:
    """Git 操作工具"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def clone(self, url: str, branch: str = "main") -> bool:
        """克隆仓库"""
        try:
            subprocess.run(
                ["git", "clone", "-b", branch, url, self.repo_path],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def checkout(self, branch: str) -> bool:
        """切换分支"""
        try:
            subprocess.run(["git", "checkout", branch], check=True, cwd=self.repo_path)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def pull(self) -> bool:
        """拉取最新代码"""
        try:
            subprocess.run(["git", "pull"], check=True, cwd=self.repo_path)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def commit(self, message: str, files: List[str] = None) -> Optional[str]:
        """提交更改"""
        try:
            if files:
                subprocess.run(["git", "add"] + files, check=True, cwd=self.repo_path)
            else:
                subprocess.run(["git", "add", "-A"], check=True, cwd=self.repo_path)
            subprocess.run(["git", "commit", "-m", message], check=True, cwd=self.repo_path)
            
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                check=True, capture_output=True, cwd=self.repo_path
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return None
    
    def push(self, branch: str = "main") -> bool:
        """推送代码"""
        try:
            subprocess.run(["git", "push", "origin", branch], check=True, cwd=self.repo_path)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_commit(self) -> Optional[str]:
        """获取当前 commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                check=True, capture_output=True, cwd=self.repo_path
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_branch(self) -> Optional[str]:
        """获取当前分支"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                check=True, capture_output=True, cwd=self.repo_path
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return None
    
    def status(self) -> str:
        """获取 git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                check=True, capture_output=True, cwd=self.repo_path
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return ""
