# Contributing to Smart Factory

> 贡献指南 — 人类与 AI 代理协作规范

## For AI Agents

### 1. Start Here

Read **[AGENTS.md](AGENTS.md)** at repo root. It links to:

- Smart Factory Context (DoD, workflow, API)
- Definition of Done
- Development Pipeline (for game tasks)

### 2. Workflow

```
需求创建 → 设计确认 → 任务拆分 → 开发/测试 → 集成验证 → 发布
```

- **Daily**: 晨间检查任务 → 开发执行 → 晚间日报
- **Reporting**: 飞书群「福渊研发部」, report to Master Jay / Winnie

### 3. Definition of Done

Before marking a task complete:

- [ ] Code complete, no compile/runtime errors
- [ ] Tests pass (unit, integration, 0.1–0.5 verification)
- [ ] Git: feature/fix branch → merge master → push remote
- [ ] Docs updated (CHANGELOG, development_status, etc.)

### 4. Key Paths

| Purpose | Path |
|---------|------|
| Pending tasks | `archived/game/docs/pending_tasks.md` (reference) |
| Dev status | `archived/game/docs/development_status.md` (reference) |
| Agent workspaces | `openclaw-knowledge/organization/workspace/` |
| API spec | `docs/REQUIREMENTS.md` |
| Organization | `docs/ORGANIZATION.md` |

### 5. OpenClaw Team Agents

If you have a workspace under `openclaw-knowledge/organization/workspace/<team>/<agent>/`:

1. Read `AGENT.md` (or `SOUL.md`) — your identity
2. Read `USER.md` — who you help
3. Read `CONTEXT.md` — local pointers into Smart Factory context (repo root has no agent identity files)
4. Follow `memory/` for session continuity when your runtime uses it

---

## For Humans

- Report blockers and progress via 飞书群「福渊研发部」
- Review agent-generated code and docs before merge
- Prefer Smart Factory API / DB for task state; archived references: `archived/game/docs/pending_tasks.md`, `archived/game/docs/development_status.md`

---

*Smart Factory - OpenClaw 知识库与管理系统*
