#!/usr/bin/env python3
"""
Feishu API log analysis – shared logic for comm_mcp tools and CLI.
Parse Gateway logs, stats, DB, and issue detection.
"""

import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Repo root: comm_mcp -> remote -> mcp -> src -> smart-factory
_REPO_ROOT = Path(__file__).resolve().parents[4]


def get_db_path() -> str:
    """Feishu API log DB path. Env FEISHU_LOG_DB or core/db/feishu_api_log.db."""
    return os.environ.get(
        "FEISHU_LOG_DB",
        str(_REPO_ROOT / "db" / "feishu_api_log.db"),
    )


def init_db(db_path: Optional[str] = None) -> None:
    db_path = db_path or get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feishu_api_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT,
            chat_type TEXT,
            chat_id TEXT,
            user_id TEXT,
            api_endpoint TEXT,
            purpose TEXT,
            project_name TEXT,
            details TEXT,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS api_call_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT,
            chat_type TEXT,
            purpose TEXT,
            api_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            UNIQUE(date, source, chat_type, purpose)
        )
    """)
    conn.commit()
    conn.close()


def parse_gateway_log(log_file_path: str) -> list:
    """Parse gateway JSON-lines log for Feishu API calls."""
    calls = []
    feishu_patterns = [r'/open-apis/', r'feishu', r'bot', r'message', r'chat', r'user']
    openclaw_patterns = [r'\[tools\]', r'feishu_', r'subagent', r'cron']

    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                msg = entry.get('0', '')
                if not any(re.search(p, msg, re.I) for p in feishu_patterns):
                    continue
                call = {
                    'timestamp': entry.get('_meta', {}).get('date', ''),
                    'message': msg,
                    'source': 'openclaw' if any(re.search(p, msg, re.I) for p in openclaw_patterns) else 'feishu',
                    'chat_type': 'group' if ('group' in msg.lower() or 'chat' in msg.lower()) else ('private' if ('private' in msg.lower() or 'user' in msg.lower()) else 'unknown'),
                    'purpose': 'cron_task' if ('cron' in msg.lower() or 'schedule' in msg.lower()) else ('project_development' if any(kw in msg.lower() for kw in ['project', 'dev', 'pinball', '智慧工厂']) else 'other'),
                }
                match = re.search(r'(/open-apis/[\w/]+)', msg)
                call['api_endpoint'] = match.group(1) if match else ''
                calls.append(call)
            except json.JSONDecodeError:
                continue
    return calls


def analyze_calls(calls: list) -> dict:
    stats = {
        'total': len(calls),
        'by_source': defaultdict(int),
        'by_chat_type': defaultdict(int),
        'by_purpose': defaultdict(int),
        'by_source_and_purpose': defaultdict(lambda: defaultdict(int)),
        'by_hour': defaultdict(int),
    }
    for call in calls:
        stats['by_source'][call['source']] += 1
        stats['by_chat_type'][call['chat_type']] += 1
        stats['by_purpose'][call['purpose']] += 1
        stats['by_source_and_purpose'][call['source']][call['purpose']] += 1
        if call.get('timestamp'):
            try:
                dt = datetime.fromisoformat(call['timestamp'].replace('Z', '+00:00'))
                stats['by_hour'][dt.hour] += 1
            except Exception:
                pass
    # Return JSON-serializable dict (nested defaultdicts -> dict)
    out = {}
    for k, v in stats.items():
        if k == "by_source_and_purpose":
            out[k] = {s: dict(purposes) for s, purposes in v.items()}
        elif isinstance(v, defaultdict):
            out[k] = dict(v)
        else:
            out[k] = v
    return out


def save_to_db(calls: list, db_path: Optional[str] = None) -> None:
    db_path = db_path or get_db_path()
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for call in calls:
        c.execute("""
            INSERT INTO feishu_api_calls
            (timestamp, source, chat_type, purpose, api_endpoint, details, status)
            VALUES (?,?,?,?,?,?,?)
        """, (
            call.get('timestamp', ''),
            call.get('source', 'unknown'),
            call.get('chat_type', 'unknown'),
            call.get('purpose', 'other'),
            call.get('api_endpoint', ''),
            call.get('message', ''),
            'failed' if 'error' in call.get('message', '').lower() else 'success',
        ))
    conn.commit()
    today = datetime.now().strftime('%Y-%m-%d')
    for source in ['openclaw', 'feishu']:
        for purpose in ['project_development', 'cron_task', 'other']:
            count = sum(1 for c in calls if c['source'] == source and c['purpose'] == purpose)
            success = sum(1 for c in calls if c['source'] == source and c['purpose'] == purpose and 'error' not in c.get('message', '').lower())
            c.execute("""
                INSERT INTO api_call_stats (date, source, chat_type, purpose, api_count, success_count, failed_count)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(date, source, chat_type, purpose) DO UPDATE SET
                    api_count = api_count + excluded.api_count,
                    success_count = success_count + excluded.success_count,
                    failed_count = failed_count + excluded.failed_count
            """, (today, source, 'all', purpose, count, success, count - success))
    conn.commit()
    conn.close()


def get_stats_from_db(limit: int = 20, db_path: Optional[str] = None) -> list:
    """Return list of daily stats rows (dicts)."""
    db_path = db_path or get_db_path()
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT date, source, purpose, api_count, success_count, failed_count
        FROM api_call_stats
        ORDER BY date DESC, source
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def generate_report_text(stats: dict, _calls: Optional[list] = None) -> str:
    purpose_names = {'project_development': '项目开发', 'cron_task': '定时任务', 'other': '其他'}
    lines = [
        "=" * 60,
        "飞书API调用分析报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        f"📊 总调用数: {stats.get('total', 0)}",
        "",
        "📌 按来源:",
    ]
    for source, count in (stats.get('by_source') or {}).items():
        lines.append(f"   - {source}: {count}")
    lines.append("")
    lines.append("💬 按聊天类型:")
    for chat_type, count in (stats.get('by_chat_type') or {}).items():
        lines.append(f"   - {chat_type}: {count}")
    lines.append("")
    lines.append("🎯 按调用目的:")
    for purpose, count in (stats.get('by_purpose') or {}).items():
        lines.append(f"   - {purpose_names.get(purpose, purpose)}: {count}")
    lines.append("")
    lines.append("📈 来源×目的 交叉分析:")
    for source, purposes in (stats.get('by_source_and_purpose') or {}).items():
        lines.append(f"   {source}:")
        for purpose, count in purposes.items():
            lines.append(f"      - {purpose_names.get(purpose, purpose)}: {count}")
    by_hour = stats.get('by_hour') or {}
    if by_hour:
        total = stats.get('total') or 1
        lines.append("")
        lines.append("⏰ 按小时分布:")
        for hour in sorted(by_hour.keys()):
            bar = "█" * (by_hour[hour] // max(1, total // 20))
            lines.append(f"   {hour:02d}:00 - {by_hour[hour]:3d} {bar}")
    return "\n".join(lines)


# ----- Analyzer-style (raw log lines, issues) -----

def parse_logs_raw(log_file_path: str) -> tuple:
    """Parse raw gateway log lines for API calls and errors."""
    api_calls = []
    errors = []
    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            time_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
            timestamp = time_match.group(1) if time_match else None
            if 'open.feishu.cn' in line:
                api_match = re.search(r'open-apis/([a-z]+)/v(\d+)/([a-z_]+)', line)
                if api_match:
                    api_type = f"open-apis/{api_match.group(1)}/v{api_match.group(2)}/{api_match.group(3)}"
                    api_calls.append({'timestamp': timestamp, 'api': api_type, 'line': line})
                error_match = re.search(r'code=(\d+)', line)
                if error_match:
                    errors.append({'timestamp': timestamp, 'code': error_match.group(1), 'line': line[:200]})
    return api_calls, errors


def analyze_api_calls_raw(api_calls: list) -> dict:
    by_api = defaultdict(int)
    by_hour = defaultdict(int)
    for c in api_calls:
        by_api[c['api']] += 1
        if c.get('timestamp'):
            by_hour[c['timestamp'][11:13]] += 1
    return {'total_calls': len(api_calls), 'by_api': dict(by_api), 'by_hour': dict(by_hour)}


def analyze_errors_raw(errors: list) -> dict:
    by_code = defaultdict(int)
    for e in errors:
        by_code[e['code']] += 1
    return {'total_errors': len(errors), 'by_code': dict(by_code)}


def identify_issues(api_calls: list, errors: list) -> list:
    issues = []
    bot_info_count = sum(1 for c in api_calls if c['api'] == 'open-apis/bot/v3/info')
    if bot_info_count > 100:
        issues.append({
            'severity': 'HIGH', 'type': 'EXCESSIVE_POLLING',
            'description': f'bot/v3/info 被调用 {bot_info_count} 次',
            'cause': '可能是健康检查或探针过于频繁调用',
            'recommendation': '检查 probeFeishu 调用频率，添加缓存或减少调用次数',
        })
    error_count = len(errors)
    if error_count > 100:
        n_99991403 = sum(1 for e in errors if e['code'] == '99991403')
        issues.append({
            'severity': 'HIGH', 'type': 'HIGH_ERROR_RATE',
            'description': f'共 {error_count} 个错误，其中 99991403 错误 {n_99991403} 次',
            'cause': '可能是网络问题、证书问题或 API 调用频率限制',
            'recommendation': '检查网络连接、证书配置，添加重试间隔',
        })
    if error_count > 1000:
        issues.append({
            'severity': 'CRITICAL', 'type': 'INFINITE_RETRY',
            'description': f'错误次数 {error_count} 过高，可能存在无限重试',
            'cause': '错误处理逻辑可能导致重复请求',
            'recommendation': '实现指数退避重试，添加最大重试次数限制',
        })
    return issues


def run_analyze(log_file: Optional[str] = None, db_path: Optional[str] = None) -> dict:
    """
    Run full logger flow: parse (JSON format), save to DB, return stats and report.
    log_file: default from FEISHU_LOG_FILE or ~/.openclaw/logs/gateway.log or Windows temp.
    """
    log_file = log_file or os.environ.get("FEISHU_LOG_FILE") or str(Path.home() / ".openclaw" / "logs" / "gateway.log")
    if not os.path.exists(log_file):
        return {"success": False, "error": f"Log file not found: {log_file}", "calls_count": 0, "report": "", "stats": {}}
    db_path = db_path or get_db_path()
    init_db(db_path)
    calls = parse_gateway_log(log_file)
    save_to_db(calls, db_path)
    stats = analyze_calls(calls)
    report = generate_report_text(stats, calls)
    return {
        "success": True,
        "calls_count": len(calls),
        "report": report,
        "stats": stats,
        "db_path": db_path,
    }


def run_analyzer_style(log_file: Optional[str] = None) -> dict:
    """Run analyzer flow: raw log parse, API/error stats, issue detection."""
    log_file = log_file or os.environ.get("FEISHU_LOG_FILE") or str(Path.home() / ".openclaw" / "logs" / "gateway.log")
    if not os.path.exists(log_file):
        return {"success": False, "error": f"Log file not found: {log_file}", "api_analysis": {}, "error_analysis": {}, "issues": []}
    api_calls, errors = parse_logs_raw(log_file)
    api_analysis = analyze_api_calls_raw(api_calls)
    error_analysis = analyze_errors_raw(errors)
    issues = identify_issues(api_calls, errors)
    return {
        "success": True,
        "api_analysis": api_analysis,
        "error_analysis": error_analysis,
        "issues": issues,
        "generated_at": datetime.now().isoformat(),
    }


def run_logger_cli() -> None:
    """CLI entrypoint for cron/API: --log-file, --analyze, --report, --stats."""
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    import argparse
    parser = argparse.ArgumentParser(description='Feishu API Logger')
    parser.add_argument('--log-file', '-l', default=None)
    parser.add_argument('--analyze', '-a', action='store_true')
    parser.add_argument('--report', '-r', action='store_true')
    parser.add_argument('--stats', '-s', action='store_true')
    parser.add_argument('--db', action='store_true')
    args = parser.parse_args()

    init_db(None)
    if args.analyze or args.report:
        log_file = args.log_file or os.path.expanduser("~/AppData/Local/Temp/openclaw/openclaw-2026-02-28.log")
        if not os.path.exists(log_file):
            log_file = os.environ.get("FEISHU_LOG_FILE") or str(Path.home() / ".openclaw" / "logs" / "gateway.log")
        if not os.path.exists(log_file):
            print(f"日志文件不存在: {log_file}")
            sys.exit(1)
        result = run_analyze(log_file)
        if not result["success"]:
            print(result.get("error", "Unknown error"))
            sys.exit(1)
        print(f"正在解析日志: {log_file}")
        print(f"找到 {result['calls_count']} 条飞书API调用")
        print("已保存到数据库")
        if args.report:
            print("\n" + result["report"])
    if args.stats or args.db:
        rows = get_stats_from_db(20)
        print("\n📊 每日API调用统计:")
        print("-" * 60)
        print(f"{'日期':<12} {'来源':<12} {'目的':<20} {'成功':>6} {'失败':>6}")
        print("-" * 60)
        for row in rows:
            print(f"{row['date']:<12} {row['source']:<12} {row['purpose']:<20} {row['success_count']:>6} {row['failed_count']:>6}")


def run_analyzer_cli() -> None:
    """CLI entrypoint for analyzer: print report and write feishu_api_report.json."""
    log_file = os.environ.get("FEISHU_LOG_FILE") or str(Path.home() / ".openclaw" / "logs" / "gateway.log")
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        sys.exit(1)
    result = run_analyzer_style(log_file)
    if not result["success"]:
        print(result.get("error"))
        sys.exit(1)
    print("=" * 60)
    print("飞书 API 调用分析报告")
    print("=" * 60)
    print(f"\n总 API 调用次数: {result['api_analysis']['total_calls']}")
    print(f"总错误次数: {result['error_analysis']['total_errors']}")
    print("\nAPI 调用类型分布:")
    for api, count in sorted(result['api_analysis'].get('by_api', {}).items(), key=lambda x: -x[1]):
        print(f"  {api}: {count}")
    print("\n问题分析:")
    for i, issue in enumerate(result['issues'], 1):
        print(f"\n问题 {i}: [{issue['severity']}] {issue['type']}")
        print(f"  描述: {issue['description']}")
        print(f"  建议: {issue['recommendation']}")
    report_path = _REPO_ROOT / "data" / "feishu_api_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({k: v for k, v in result.items() if k != 'success'}, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存到: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyzer":
        sys.argv.pop(1)
        run_analyzer_cli()
    else:
        run_logger_cli()
