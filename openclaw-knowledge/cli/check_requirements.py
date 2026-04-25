#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/.openclaw/workspace/smart-factory/openclaw-knowledge')
from cli.comm_cmd import get_api_base

import requests
base = get_api_base()
print(f"API base: {base}")

try:
    resp = requests.get(f"{base}/api/requirements?assigned_team=newton", timeout=5)
    print(f"Status: {resp.status_code}")
    print(resp.text[:2000])
except Exception as e:
    print(f"Error: {e}")
