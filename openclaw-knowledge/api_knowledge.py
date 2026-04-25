#!/usr/bin/env python3
"""
API endpoint: POST /api/knowledge/collect
Trigger on-demand knowledge collection for jay-knowledge-db
"""

import sys
import subprocess
from pathlib import Path

def handler(request):
    """Handle on-demand collection"""
    # Run collector
    result = subprocess.run(
        [sys.executable, "/home/pi/.openclaw/workspace/working/code/nlp/docs/auto_knowledge_collector.py", "on-demand"],
        capture_output=True, text=True
    )
    
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr
    }

if __name__ == "__main__":
    result = handler(None)
    print(result)
