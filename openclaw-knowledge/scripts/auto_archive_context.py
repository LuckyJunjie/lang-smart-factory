#!/usr/bin/env python3
"""
自动上下文管理 - 当群聊token接近上限时自动压缩

原版本把 sessions 目录写死在 /home/pi/...，当你把 OpenClaw 的 workspace / 数据目录迁移到别的机器或路径时会失效。
这里改为支持环境变量/命令行参数，默认行为仍等价于旧版本（vanguard001，~/.openclaw/agents/<id>/sessions）。
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path

TOKEN_LIMIT = 150000
ARCHIVE_THRESHOLD = 180000

DEFAULT_AGENT_ID = os.environ.get("OPENCLAW_AGENT_ID", "vanguard001")
DEFAULT_AGENTS_DIR = os.environ.get("OPENCLAW_AGENTS_DIR", str(Path.home() / ".openclaw" / "agents"))

def resolve_sessions_dir(agent_id: str) -> str:
    """
    Determine sessions directory.
    Priority:
    1) OPENCLAW_SESSIONS_DIR env
    2) OPENCLAW_AGENTS_DIR env + <agent_id>/sessions
    """
    explicit = os.environ.get("OPENCLAW_SESSIONS_DIR")
    if explicit:
        return os.path.expanduser(explicit)
    agents_dir = os.path.expanduser(DEFAULT_AGENTS_DIR)
    return os.path.join(agents_dir, agent_id, "sessions")

def get_session_token_count(session_file):
    try:
        size = os.path.getsize(session_file)
        return size / 4
    except:
        return 0

def archive_session(session_file):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = session_file.replace('.jsonl', f'_ARCHIVED_{timestamp}.jsonl')
    
    with open(session_file, 'r') as f:
        content = f.read()
    with open(archive_name, 'w') as f:
        f.write(content)
    
    session_id = os.path.basename(session_file).replace('.jsonl', '')
    with open(session_file, 'w') as f:
        f.write(json.dumps({
            "type": "session",
            "version": 3,
            "id": session_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "note": f"Archived {timestamp}. History: {os.path.basename(archive_name)}"
        }, ensure_ascii=False) + '\n')
    
    return archive_name

def check_and_archive(sessions_dir: str):
    results = []
    archived_count = 0
    
    if not os.path.isdir(sessions_dir):
        print(f"[auto_archive_context] sessions dir not found: {sessions_dir}")
        return results, archived_count

    for f in os.listdir(sessions_dir):
        if not f.endswith('.jsonl') or '_ARCHIVED' in f:
            continue
        if 'df9dc283' in f or 'group' in f.lower():
            filepath = os.path.join(sessions_dir, f)
            tokens = get_session_token_count(filepath)
            
            if tokens > ARCHIVE_THRESHOLD:
                archive_name = archive_session(filepath)
                archived_count += 1
                results.append(f"✅ {f}: {int(tokens)} tokens -> 已归档")
            elif tokens > TOKEN_LIMIT:
                results.append(f"⚠️  {f}: {int(tokens)} tokens -> 即将满")
            else:
                results.append(f"✓  {f}: {int(tokens)} tokens -> 正常")
    
    return results, archived_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-archive OpenClaw session files by token size.")
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID, help="Agent id (default: env OPENCLAW_AGENT_ID or vanguard001)")
    args = parser.parse_args()
    sessions_dir = resolve_sessions_dir(args.agent_id)

    print(f"=== 上下文自动管理 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    results, archived = check_and_archive(sessions_dir=sessions_dir)
    for r in results:
        print(r)
    print(f"\n已归档 {archived} 个会话")
