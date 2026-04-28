# LangFlow Factory — OpenClaw Agent Guide

**For OpenClaw agents (einstein, curie, galileo, darwin, hawking, etc.)**

LangFlow Factory is a LangChain/LangGraph-based software factory. OpenClaw agents are the **code execution layer** — they read tasks from files, execute with Claude Code/Codex, and write results.

---

## System Overview

```
LangFlow Factory (Newton)                    OpenClaw Agents
┌──────────────────────┐                    ┌──────────────────────┐
│ DemandAnalyst (LLM) │                    │                       │
│         ↓           │                    │  Monitor work/input/  │
│ Architect (LLM)     │                    │         ↓             │
│         ↓           │                    │  Execute with coding │
│ DetailDesigner (LLM)│                    │         ↓             │
│         ↓           │                    │  Write to work/output│
│ dispatch_node       │ ── write ──→       │                       │
│         ↓           │                    │                       │
│ implementation_node │ ◄── poll ──│      │                       │
│ (ReAct Loop)        │                    │                       │
└──────────────────────┘                    └──────────────────────┘
```

## OpenClaw Agent Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Monitor** | Check `work/input/` every 5 minutes for new tasks |
| **Execute** | Run coding-agent (Claude Code/Codex) for each task |
| **Verify** | Self-check output against acceptance_criteria |
| **Write** | Write result JSON to `work/output/{task_id}.json` |
| **Retry** | Check `work/feedback/` for retry instructions |

## Workflow Interaction

### Step 1: Receive Task

Newton writes task to:
```
/home/pi/.openclaw/workspace/{project_id}/work/input/{task_id}.json
```

### Step 2: Execute

OpenClaw agent reads the task file, then spawns coding agent:

```python
# Example: using coding-agent skill
spawn_coding_agent(
    prompt=task["requirements"],
    project=task["project_id"],
    acceptance_criteria=task["acceptance_criteria"]
)
```

### Step 3: Write Output

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/path/to/main_menu.ts",
  "errors": [],
  "completed_at": "2026-04-28T10:05:00Z"
}
```

Write to: `/home/pi/.openclaw/workspace/{project_id}/work/output/{task_id}.json`

### Step 4: Handle Retry

If Newton found issues, it writes feedback to:
```
/home/pi/.openclaw/workspace/{project_id}/work/feedback/{task_id}_feedback_1.json
```

OpenClaw reads feedback, fixes issues, re-executes.

---

## Cron Setup

Add to crontab (`crontab -e`):

```bash
# LangFlow Factory task monitor - runs every 5 minutes
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m skills.langflow_executor >> /tmp/langflow_executor.log 2>&1
```

Or use OpenClaw's built-in cron:
```
openclaw cron add --name langflow-executor --interval 5m -- "cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m skills.langflow_executor"
```

---

## ReAct Loop (Retry Flow)

```
Task Created → Execute → Output Written
                            ↓
                    Newton Verifies
                            ↓
               ┌────────────┴────────────┐
            Pass                        Fail
               ↓                         ↓
          Complete               Write feedback/
                                       ↓
                                Re-execute (max 3)
                                       ↓
                                  Output Written
```

---

## File Paths Reference

| Purpose | Path |
|---------|------|
| Input tasks | `/home/pi/.openclaw/workspace/{project_id}/work/input/` |
| Output results | `/home/pi/.openclaw/workspace/{project_id}/work/output/` |
| Retry feedback | `/home/pi/.openclaw/workspace/{project_id}/work/feedback/` |
| Project code | `/home/pi/.openclaw/workspace/{project_id}/` |

---

## Key Rules

1. **Never delete** input files — Newton needs them for reference
2. **Always verify** output against acceptance_criteria before writing
3. **Include feedback** in retry execution — don't repeat the same mistakes
4. **Report completion** via sessions_send to Newton if configured
5. **Log errors** in output JSON for Newton to analyze

---

## Quick Start

1. Read `docs/LANGFLOW_FACTORY_REQUIREMENTS.md` for full requirements
2. Read `openclaw-knowledge/skills/langflow-executor/SKILL.md` for execution details
3. Set up cron job to monitor `work/input/`
4. When task appears, execute with coding-agent
5. Write result to `work/output/{task_id}.json`

---

## Contact

For questions about task requirements, contact Newton (the Team Manager).
For urgent issues, message in the 福渊研发部 Feishu group.
