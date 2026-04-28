# LangFlow Executor Skill

**Purpose**: Process tasks from LangFlow Factory work/input/ directory, execute with coding agent, write results to work/output/.

**Trigger**: Cron job checks work/input/ every 5 minutes, OR manual invocation.

## How It Works

1. **Monitor** `work/input/` for new `{task_id}.json` files
2. **Read** task requirements and acceptance criteria
3. **Execute** using coding-agent (Claude Code/Codex) for the project
4. **Write** result to `work/output/{task_id}.json`
5. **If retry feedback exists** in `work/feedback/`, incorporate it before re-executing

## Task File Format (input)

```json
{
  "id": "task_001",
  "title": "实现主菜单",
  "requirements": "创建一个游戏主菜单，包含开始游戏、设置、退出按钮...",
  "project_id": "godot-trk-001",
  "acceptance_criteria": [
    "主菜单显示在屏幕中央",
    "点击开始游戏进入游戏场景",
    "设置按钮打开设置面板"
  ],
  "feedback": [
    {
      "attempt": 1,
      "errors": ["主菜单未居中显示"],
      "suggestion": "使用 CenterContainer 或设置 anchor"
    }
  ],
  "created_at": "2026-04-28T10:00:00Z"
}
```

## Output File Format

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/path/to/created/file.ts",
  "errors": [],
  "completed_at": "2026-04-28T10:05:00Z"
}
```

## Cron Setup

Add to crontab:
```
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m skills.langflow_executor
```

## Self-Verification

Before writing output, verify:
1. All acceptance_criteria are addressed
2. Code compiles/runs without errors
3. Output files exist at specified paths

## Feedback Handling

If `work/feedback/{task_id}_feedback_{n}.json` exists, read it and:
- Log previous errors
- Apply suggested corrections
- Re-execute with fixes
