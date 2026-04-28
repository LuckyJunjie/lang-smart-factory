# OpenClaw Agent Workspace — LangFlow Factory Integration

**For OpenClaw agents in the 福渊研发部 team**

This directory contains the knowledge base and skills for OpenClaw agents to participate in the LangFlow Factory software development pipeline.

---

## Quick Start for New Agents

1. **Read this file** — understand the system
2. **Read `AGENTS.md`** — your responsibilities as an OpenClaw executor
3. **Read `skills/langflow-executor/SKILL.md`** — how to execute tasks
4. **Set up cron job** — monitor work/input/ every 5 minutes
5. **Start processing tasks** — check work/input/ for pending work

---

## System Overview

LangFlow Factory (Newton) is the **orchestrator** — it analyzes requirements, designs architecture, and breaks down tasks. OpenClaw agents are the **executors** — they implement the code.

```
Newton (LangFlow Factory)          OpenClaw Agents (You)
         │                                  │
    DemandAnalyst                          │
         │                                  │
    Architect                              │
         │                                  │
    DetailDesigner                         │
         │                                  │
    dispatch ─── write ──→ work/input/     │
         │                                  │ ← Read task
         │                                  │ ← Execute with coding-agent
         │                                  │
         │ ◄── poll ── work/output/        │
         │                                  │
    (ReAct verification loop)              │
         │                                  │
         │ ◄── feedback ── work/feedback/   │
         │                                  │
```

---

## Directory Structure

```
openclaw-knowledge/
├── README.md                    # This file
├── AGENTS.md                     # OpenClaw agent responsibilities
├── skills/
│   └── langflow-executor/        # Task execution skill
│       └── SKILL.md              # Execution protocol
└── workflows/
    └── LANGFLOW_WORKFLOW.md      # Workflow interaction details
```

---

## Your Tasks

| Task | Description |
|------|-------------|
| Monitor | Check `work/input/` every 5 minutes |
| Execute | Run coding-agent for each task |
| Verify | Self-check against acceptance_criteria |
| Output | Write results to `work/output/` |
| Retry | Handle feedback in `work/feedback/` |

---

## Getting Help

- **Task questions** → Ask Newton in Feishu
- **Urgent issues** → Message in 福渊研发部 group
- **Skill updates** → Check this knowledge base

---

## Key Principles

1. **File-based communication** — no Redis, no direct API calls to Newton
2. **Acceptance criteria first** — always verify against the criteria before reporting completion
3. **Self-verification** — check your output before writing to work/output/
4. **Retry with feedback** — incorporate previous errors when re-executing
5. **Log everything** — help Newton debug by including errors in output JSON
