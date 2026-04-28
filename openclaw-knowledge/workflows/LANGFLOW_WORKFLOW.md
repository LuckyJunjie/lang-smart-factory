# LangFlow Factory — OpenClaw Workflow Interaction

**Mode B: OpenClaw as Independent Executor**

## Overview

LangFlow Factory (Newton) orchestrates the software development pipeline. OpenClaw agents are the **code execution layer** — they monitor file queues and implement code.

```
Newton (LangFlow Factory)          OpenClaw Agents (einstein, curie, etc.)
         │                                  │
    DemandAnalyst (LLM)                    │
         │                                  │
    Architect (LLM)                         │
         │                                  │
    DetailDesigner (LLM)                    │
         │                                  │
    dispatch ─── write ──→ work/input/     │ ← Read task
         │                                  │ ← Spawn coding-agent
         │                                  │ ← Execute
         │ ◄── poll ── work/output/        │ ← Write result
         │                                  │
    (ReAct Loop)                           │
         │                                  │
         └─── feedback ──→ work/feedback/  │ ← Read feedback
                                           │ ← Re-execute (max 3)
```

## Workflow Steps

### 1. Newton Dispatches Task

Newton writes task JSON to:
```
/home/pi/.openclaw/workspace/{project_id}/work/input/{task_id}.json
```

### 2. OpenClaw Monitors

Cron job runs every 5 minutes:
```
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m src.skills.langflow_executor --watch
```

### 3. OpenClaw Executes

For each task in `work/input/`:
1. Read task JSON
2. Check `work/feedback/` for retry instructions
3. Spawn coding-agent (Claude Code/Codex) with task requirements
4. Self-verify output against acceptance_criteria
5. Write result to `work/output/{task_id}.json`

### 4. Newton Verifies

Newton polls `work/output/` and verifies against acceptance_criteria:
- **Pass** → Continue to next task
- **Fail** → Write feedback to `work/feedback/{task_id}_feedback_N.json` → OpenClaw retries

### 5. ReAct Loop (max 3 retries)

```
Task Created → Execute → Output Written
                            ↓
                    Newton Verifies
                            ↓
               ┌────────────┴────────────┐
            Pass                        Fail (Attempt N/3)
               ↓                         ↓
          Complete              Write feedback/
                                       ↓
                                OpenClaw Re-execute
                                       ↓
                                  Output Written
```

## File Paths

| Purpose | Path |
|---------|------|
| Input tasks | `/home/pi/.openclaw/workspace/{project_id}/work/input/` |
| Output results | `/home/pi/.openclaw/workspace/{project_id}/work/output/` |
| Retry feedback | `/home/pi/.openclaw/workspace/{project_id}/work/feedback/` |

## Notification

When all tasks for a project are complete, Newton sends a Feishu notification to the 福渊研发部 group.

## OpenClaw Agent Commands

```bash
# Start executor in watch mode
python3 -m src.skills.langflow_executor --watch

# Process specific project only
python3 -m src.skills.langflow_executor --project godot-trk-001

# Dry run (show pending tasks without executing)
python3 -m src.skills.langflow_executor --dry-run
```

## Cron Setup

Add to crontab:
```bash
crontab -e
# LangFlow Factory task executor
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m src.skills.langflow_executor >> /tmp/langflow_executor.log 2>&1
```
