# AGENTS.md - Smart Factory

> Entry point for LLM agents working on this codebase. Read this first.

## Agent Obligations (mandatory)

**All agents must:**

1. **Identify who you are helping** — Read `USER.md` in your workspace (`openclaw-knowledge/organization/workspace/<team>/<agent>/USER.md`) to know the human (Master Jay, Winnie, or designated lead) you report to and serve.
2. **Act by your defined role** — Follow **[OpenClaw Development Flow](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)** for your team and agent role (e.g. Vanguard001 coordination, Jarvis/CodeForge/dinosaur development, Tesla/Newton test-primary plus development, Hera blockage handling). Use the workflows, CLI commands, and skills specified there for your role.
3. **Follow defined reports and DoD** — Use the report templates referenced in the flow (e.g. `openclaw-knowledge/standards/report/DEVELOPMENT_TASK_REPORT_TEMPLATE.md`, `TEST_TASK_REPORT_TEMPLATE.md`, `TEAM_STATUS_REPORT_TEMPLATE.md`, `FINAL_DAILY_REPORT_TEMPLATE.md`) and meet **[Definition of Done](openclaw-knowledge/standards/DEFINITION_OF_DONE.md)** for all development work (code complete, tests pass, Git flow, docs updated).

## Quick Context

Smart Factory is OpenClaw's knowledge base and management system for AI-driven software development. It defines workflows, requirements, projects, and team structure.

## Essential Reading (in order)

1. **[OpenClaw Development Flow](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)** — Role-based workflows, CLI, skills, report templates (primary source for agent behavior).
2. **[Smart Factory Context](openclaw-knowledge/organization/SMART_FACTORY_CONTEXT.md)** — DoD, workflow, API, reporting norms
3. **[Definition of Done](openclaw-knowledge/standards/DEFINITION_OF_DONE.md)** — Game/app/tool/research dev + QA completion, artifacts, Git flow (aligned with `docs/HIGH_REQUIREMENTS.md`)
4. **[Development Pipeline](archived/game/development-pipeline.md)** — 7-phase game dev workflow (archived reference)

## Key Paths

| Purpose | Path |
|---------|------|
| **Deploy OpenClaw workspaces (bootstrap symlinks)** | **[OPENCLAW_DEPLOY.md](OPENCLAW_DEPLOY.md)** (repo root) |
| **Redis 协作（任务派发/结果流/心跳；优先于 API 轮询）** | `docs/REDIS_COLLABORATION.md` |
| **High-level product & harness I/O** | `docs/HIGH_REQUIREMENTS.md` |
| **Game development golden rules** (Godot / coordinator → `docs/` → headless gates) | `docs/GAME_DEVELOPMENT_GOLDEN_RULES.md` |
| System docs | `docs/README.md` |
| Organization | `docs/ORGANIZATION.md` |
| **API spec** (HTTP CRUD for OpenClaw; includes project PATCH/DELETE, requirements, tasks, **test-cases**, teams, meetings, work-log) | `docs/REQUIREMENTS.md` |
| **Development flow (roles & workflows)** | `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` |
| **Communication system**（多设备 Vanguard） | `openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md` |
| **Team standalone workflow**（领导直派、单团队闭环） | `openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md` |
| **CLI (agent tools)** | `openclaw-knowledge/cli/README.md` — use CLI instead of MCP |
| **Report templates** | `openclaw-knowledge/standards/report/README.md` |
| **Skills** | `openclaw-knowledge/skills/README.md` |
| **CLI / Skills / MCP / scripts index** | `openclaw-knowledge/TOOLS_INDEX.md` |
| **Toolchain（环境 / 版本安装基线）** | `openclaw-knowledge/docs/TOOLCHAIN.md` |
| Toolchain（工具/MCP/技能目录表） | `docs/TOOLCHAIN.md` |
| **Project & requirement tracking** | `openclaw-knowledge/standards/PROJECTS.md` |
| Pending tasks | `archived/game/docs/pending_tasks.md` (archived) |
| Dev status | `archived/game/docs/development_status.md` (archived) |
| **Smart Factory core** (API, DB, migrations) | `core/README.md` |
| **DB → markdown snapshot** (optional operator utility) | `python3 core/db/export_snapshot.py` → `core/db/snapshot/<timestamp>/` |
| **Agent workspaces** (identity files live **here only**, not at repo root) | `openclaw-knowledge/organization/workspace/` |

## Workflow Summary

- **Demand→Release**: 飞书 → 需求创建 → 设计确认 → 任务拆分 → 开发/测试 → 集成验证 → 发布
- **Daily**: 晨间检查 → 开发执行 → 晚间日报
- **Reporting**: 飞书群「福渊研发部」, report to Master Jay / Winnie

### Team Development Flow (DB-driven)

**Vanguard-coordinated** (multi-device): See [OPENCLAW_COMMUNICATION_SYSTEM.md](openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md). **Team standalone** (leadership → Team Manager, no cross-device Redis): See [OPENCLAW_STANDALONE_WORKFLOW.md](openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md). Both modes are defined in [OPENCLAW_DEVELOPMENT_FLOW.yaml](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) (`execution_modes`).
- Vanguard assigns via `POST /api/requirements/<id>/assign` (new / bug / feature to dev-primary teams **or** Tesla/Newton when they own the dev work; developed handoff to **Tesla / Newton** for test)
- Tesla / Newton: test finds issues → create bug requirement (`POST /api/requirements`, type=bug); Vanguard may assign fixes to **any** dev-capable team (**including** Tesla/Newton)
- Dev team blocked by dependency → report via `POST /api/discussion/blockage`; Hera may reassign another requirement and defer the blocked one (PATCH status=blocked or clear assigned_team)
- Teams fetch `GET /api/teams/<team>/assigned-requirements`, then `POST /api/requirements/<id>/take`
- Teams report status to Hera; Vanguard posts to Feishu

### Role Skill Usage (mandatory)

- Follow `role_skill_policy` in `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`.
- Godot work selection rule:
  - **Project-level Godot generation/refactor**: use `godogen`
  - **Concrete Godot task execution** (`.tscn`, `.gd`, headless validation, screenshot/VQA): use `godot-task`
- Non-Godot tasks should continue to use `develop_requirement` / `test_requirement` and standard CLI domains.

### Environment Self-Bootstrap (mandatory)

- Before starting work, verify/install required tools based on your role using `environment_bootstrap` in `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` and **`openclaw-knowledge/docs/TOOLCHAIN.md`**（环境与 **Godot 4.5.1** 等版本基线）；智慧工厂工具总表见根目录 **`docs/TOOLCHAIN.md`**。
- At minimum ensure: `python3`, `git`, `requests`. **Multi-device Vanguard mode** also needs **`SMART_FACTORY_API`**（生产指向 **vanguard001** 上 API 的 `/api` 基地址，见 `docs/REQUIREMENTS.md` 文首）and **`REDIS_URI`**（多机协作；Redis 与 API **默认同机** vanguard001，见 `docs/REDIS_COLLABORATION.md`）。**Team standalone mode**（[OPENCLAW_STANDALONE_WORKFLOW.md](openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)）does **not** require Redis or API for inter-machine coordination; optional `SMART_FACTORY_API` for ledger only.
- Godot roles must ensure: `godot` (headless), and recommended `xvfb-run`, `ffmpeg`, `gdlint`.

**Standard team cycle — mode A** (Vanguard-coordinated, all nodes): **`openclaw-knowledge/standards/DEVELOPMENT_FLOW.md`** — Redis `stream:tasks` / `stream:results` / heartbeat; API for DB; artifacts under `<project_repo_root>/work/<agent>/`; push to remote to finish.

**Standard team cycle — mode B** (team standalone): **`openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md`** and `team_standalone_cycle` in **`OPENCLAW_DEVELOPMENT_FLOW.yaml`** — leadership brief → Team Manager; project-docs gap analysis; spawn sub-agents; same DoD/report templates; `work/<agent>/input|output`; push to remote; Feishu report to Master Jay (no mandatory Redis/API for coordination).

## Definition of Done (abbreviated)

- Code complete, no compile/runtime errors
- Tests pass (unit, integration, 0.1–0.5 verification)
- Git: feature/fix branch → merge master → push remote
- Docs updated as needed

## For OpenClaw Team Agents

**Repository root** holds only shared docs (`AGENTS.md`, `README.md`, …) and code trees (`core/`, `openclaw-knowledge/`, `docs/`). It does **not** contain per-agent `USER.md`, `SOUL.md`, `CONTEXT.md`, `HEARTBEAT.md`, or `SESSION.md`; those exist under each agent directory below.

If you work from `openclaw-knowledge/organization/workspace/<team>/<agent>/` (or a generated `.openclaw-workspace/agents/<agent_id>/` that symlinks these files):

1. **Identify who you serve**: Read that folder’s `USER.md`.
2. **Your identity**: Read `AGENT.md` (or `SOUL.md`).
3. **Your role in the flow**: Follow `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` — workflows/skills for your team/role (e.g. `dev_team_cycle`, `tesla_cycle`, `hera_cycle`, `vanguard_hourly`).
4. **Context**: Read **that folder’s** `CONTEXT.md` (points at `organization/SMART_FACTORY_CONTEXT.md` via symlink) — not any path at repo root.
5. **Reports & DoD**: Use `openclaw-knowledge/standards/report/` and `openclaw-knowledge/standards/DEFINITION_OF_DONE.md`.
6. **Recent context**: Read `memory/YYYY-MM-DD.md` when present (runtime workspace).

---

*Smart Factory - OpenClaw 知识库与管理系统*
