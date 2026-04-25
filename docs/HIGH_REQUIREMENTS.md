# High-level requirements (Smart Factory + OpenClaw)

This document refines roadmap, data ownership, workflows, and **harness-style inputs/outputs** for OpenClaw: every automated step should declare what it consumes, what it emits, and how success is verified (machine-parseable where possible).

**Game development (Godot / multi-agent):** Field-proven practices from a full OpenClaw run (raw brief → design docs → iterative dev/test) are captured in **[GAME_DEVELOPMENT_GOLDEN_RULES.md](./GAME_DEVELOPMENT_GOLDEN_RULES.md)**. Use that doc as the **normative checklist** for new `projects.type=game` work; iterate it after each successful delivery.

## Harness principles (OpenClaw I/O standard)

Apply to all skills, CLI wrappers, heartbeat steps, and Feishu-triggered jobs. **Multi-host OpenClaw**：团队间协作事件以 **Redis** 为主（见 `docs/REDIS_COLLABORATION.md`）；Cron 仅用于本地技能/报告/心跳辅助，**不得**作为跨团队任务发现主机制。

| Field | Requirement |
|-------|-------------|
| **Preconditions** | Env vars (`SMART_FACTORY_API`, Redis URL/channel names if used), repo paths, role (from workspace `USER.md` / `AGENT.md`). |
| **Input** | Structured: CLI args, JSON body for API, file paths, or explicit Feishu message IDs. No implicit “latest file” without a named path or query. |
| **Output** | **CLI / skills**: JSON on stdout (single object or array); human explanations on stderr. **API**: JSON response bodies per `docs/REQUIREMENTS.md`. **Artifacts**: markdown reports under the owning agent’s `work/` tree or paths given in the step. |
| **Exit / status** | Process exit code 0 = success; non-zero = failure. API HTTP status matches REST semantics. |
| **Side effects** | List mutations: DB rows, Redis publish, Feishu posts, file writes. |
| **Idempotency** | Re-running with the same input should not duplicate requirements/tasks unless the operation is explicitly “create new version”. |
| **Verification** | How a manager agent confirms success: e.g. `GET` resource, row counts, presence of report file, test log without `ASSERT FAIL`. |

---

## 1. Roadmap and agent management

1. **Roadmap**: Game and applications development as the bootstrapping phase; Smart Factory + OpenClaw knowledge base for teams; later design/manufacture robots.
   - **[input]** Strategy docs / human direction (Feishu or repo markdown).
   - **[output]** Priorities reflected in project records via API (`POST/PATCH /api/projects`, requirements priorities); no separate “roadmap DB” required initially.

---

## 2. Organization management

All organization data queryable via API (teams, machines, responsibilities).

1. **Team responsibility** (existing model).
   - **[input]** Master data in DB or admin API; reference `openclaw-knowledge/organization/` for narrative.
   - **[output]** `GET /api/teams`, `GET /api/machines`, etc. per `docs/REQUIREMENTS.md`; JSON fields stable for agents.

2. **Device ↔ team mapping**; team manager agent is the external interface: receives tasks, spawns sub-agents, coordinates blockers, reports outcomes.
   - **[input]** **Mode A —** Assignments from Vanguard/Hera (`POST /api/requirements/<id>/assign`, Redis events per `openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md`). **Mode B —** Direct brief from Master Jay / Winnie to Team Manager per `openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md` (project docs + gap analysis; no mandatory cross-device Redis).
   - **[output]** **Mode A —** 进度/结果优先 **`XADD smartfactory:stream:results`**；需落库或降级时 `cli project report-status` / 等价 API；团队 markdown 按 flow YAML。**Mode B —** 团队内产物与最终飞书汇报；可选 `report-status` / API 台账；**不强制** `stream:results`。

---

## 3. Requirement management (database + API)

Design normalized tables for all entities below; expose CRUD/query via API as in `docs/REQUIREMENTS.md`. **分层可读编码 `code`**（`P…-REQ…-TASK…-TC…`）由 API 根据 id 与标题计算，见 **`docs/REQUIREMENTS.md` §2.0**（主键仍为整数 id）。

### 3.1 Projects (from original requirements)

Fields include: categories, purpose, description, benefits, outcome, priority.

- **[input]** Raw requirement from Feishu webhook/pipeline or file drop path (structured JSON or parsed markdown).
- **[output]** `POST /api/projects` (or import job) creates/updates project; Vanguard/Hera markdown under `openclaw-knowledge/organization/workspace/.../work/` documents validation, gaps, and ingestion result; assignment state reflected in `requirements` (assigned or queued when teams at cap ~3 active per team). Deferred assignments can be triggered later by Feishu instruction or assigner skill.

### 3.2 Requirements decomposition

OpenClaw breaks down project-level intent into detailed requirements and sub-requirements.

- **[input]** Canonical project/requirement text from (a) manager `work/` outputs, or (b) `GET /api/projects`, `GET /api/requirements`.
- **[output]** `POST /api/requirements` for new rows; analyst report in agent `work/` per DoD; optional verification requirement created with **highest priority**; parent requirement may stay `ready` until verification completes.

### 3.3 Design / GDD / technical design / test plan

Per-requirement design with priority, status, notes; API is the shared **blackboard** (any OpenClaw CURD → others see via query).

1. **Architecture / GDD**
   - **[input]** Requirement IDs and constraints from API; prior design docs linked in task detail or attachments path.
   - **[output]** Design sections stored as tasks or requirement `description`/`metadata` fields per schema; markdown artifact in `work/`; `PATCH` requirement status transitions per workflow.
   - **Game repos (`repo_url` checkout):** Promote stable design to **`docs/`** (e.g. GDD, architecture, milestone plan, tech choices) as the **long-lived product truth**, not only under `work/<agent>/`. See [GAME_DEVELOPMENT_GOLDEN_RULES.md](./GAME_DEVELOPMENT_GOLDEN_RULES.md) §2–3.

2. **Detailed technical design** (sequence/data flow/modules/classes; requirements split into executable technical tasks)
   - **[input]** Approved scope from parent requirement; dependencies from `depends_on` / task graph.
   - **[output]** Child tasks via `POST /api/tasks` or batch; diagrams as linked files or embedded in `report-task-detail`; JSON summary in API for search.

3. **Test plan** (V-model: layers — unit, component, screenshot, console; ≥1 test case per technical task; integration + screenshot per requirement)
   - **[input]** Technical task list from API; test strategy from `openclaw-knowledge/standards/DEFINITION_OF_DONE.md`.
   - **[output]** Test tasks/cases in DB or attached checklist paths; Tesla/other team owns execution per assignment rules; results **优先** `smartfactory:stream:results`，并 `report-status` / 测试报告模板落库。

---

## 4. Program management

### 4.1 Task assignment

Vanguard001 + Hera use skills + **Redis** per balance rules (~1.5–3× tasks per team vs consumption when DB allows).

- **[input]** 可分配列表：`GET /api/requirements` / CLI（**仅供 Vanguard 决策与写库**，不是团队 listen 主路径）；在线：`GET /api/teams/online` 或 Redis heartbeat。触发：**Redis 可用时**以事件/Feishu 指令驱动分配 skill；**可选**每 **30 min** 管理巡检（审计负载、补偿派发），**不是**替代 Redis 的团队通知。
- **[output]** **主路径**：`PUBLISH smartfactory:task:dispatch` + `XADD smartfactory:stream:tasks`；**持久化**：`POST /api/requirements/<id>/assign`；stdout 摘要；飞书可选。

### 4.2 Monitor and adjust

- **[input]** 实时监控：**聚合 `stream:results`、heartbeat**；**可选**每 **20 min** 用 `GET` 拉取 DB 状态做审计/仪表盘（Redis 正常时**不作为**任务派发主触发）。
- **[output]** 再平衡：**优先** Redis 通知 + `POST assign`；`PATCH` 更新；记录 work-log（若实现）。

### 4.3 Meetings

- **[input]** Existing meeting API payloads (unchanged).
- **[output]** Stored minutes / attendance per current API; agent participation records if applicable.

### 4.4 Task dependencies

If a task is blocked on another: managers set dependent task to pending (lower priority, reassign, or clear assignee) and prioritize prerequisite tasks.

- **[input]** Blockage report: `POST /api/discussion/blockage` or `cli project` equivalent; dependency graph fields.
- **[output]** Updated `requirements`/`tasks` rows; Hera/Vanguard actions visible via `GET`.

### 4.5 Evaluation and prediction

Task authors add rough time and token estimates; managers aggregate Gantt-style views from project priority and plan.

- **[input]** Estimates on task create/update (fields or JSON); actuals from agent reports (token monitor below).
- **[output]** Report skill JSON + optional Feishu summary; dashboard/API aggregates when implemented.

---

## 5. OpenClaw assistant (markdown + tools)

Markdown-first assets live under `openclaw-knowledge/` (skills, MCP, templates). Not duplicated in DB except pointers/URLs if needed.

### 5.1 Quick deployment

- **[input]** Local repo path; workspace id; optional `--force` for symlink refresh.
- **[output]** `openclaw-knowledge/scripts/setup_openclaw_workspaces.py` run log; symlinks `cli`, `skills`, `mcp`, `workflows`, `standards`, etc.; exit 0 on success.

### 5.2 Tools and skills

- **[input]** Task description + role from flow YAML.
- **[output]** SKILL.md + self-description; invocations documented with stdin/stdout contract above.

### 5.3 Token monitor

- **[input]** Task completion reports from agents (estimated tokens, prompt count) via `report-status` or dedicated fields.
- **[output]** Rolling aggregates in DB or reporting tables; JSON/CSV for dashboards.

### 5.4 Report templates / instructions

- **[input]** Process changes in `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`.
- **[output]** Updated templates under `openclaw-knowledge/standards/report/`; agents cite template paths in reports.

### 5.5 Verification steps

1. **Design verification** — parallel verification requirement assigned to another team.
   - **[input]** Design task ID; verifier team from Vanguard/Hera.
   - **[output]** Verdict in requirement status + markdown review; blocking issues become bugs (`type=bug` requirement) if needed.

2. **Coding verification** — all required tests exist and pass (unit, console, harness stdout rules for Godot per `godot-task` skill).
   - **[input]** Branch/commit or artifact paths; CI or local test logs.
   - **[output]** Test results attached to task; exit 0 from test runners; no `ASSERT FAIL` in harness logs.
   - **Games:** Prefer the game repo’s **documented headless commands** (project parse, import when assets change, gameplay/UI regression scripts) as acceptance; do not treat “reached main menu” as the only gate. See [GAME_DEVELOPMENT_GOLDEN_RULES.md](./GAME_DEVELOPMENT_GOLDEN_RULES.md) §4–6.

3. **Test verification** — cross-team component + screenshot tests.
   - **[input]** Build artifact from dev team; environment matrix from test plan.
   - **[output]** Pass/fail in Tesla (or assigned test team) reports; failures create bugs or blockages.

---

## 6. Central database and Redis

1. **Database** covers all structured data above; OpenClaw assistant prose stays in markdown under `openclaw-knowledge/`.
2. **Consistency**: single writer patterns or migrations from `core/db/`; backup/replica strategy out of scope here but assumed for prod.
3. **Redis** is the primary real-time bus; API remains source of truth for persistence; human-editable views via API + static dashboard under `core/api/static/`.

- **[input]** Events: assign, status change, blockage (schema in communication doc).
- **[output]** Subscribers update local state and call API to persist; CLI continues to return JSON for agents without Redis access.

---

## Workflow design

### W.1 Deployment: Smart Factory git on every OpenClaw node

1. Skill merges OpenClaw configuration into each workspace (identity, agent, user, soul, skills path) **without** wiping local history.
   - **[input]** Repo revision (branch/tag); workspace paths.
   - **[output]** Merged config files; diff logged to stderr; exit 0.

2. Copy/sync skills to workspace roots (default skills path).
   - **[input]** Source: `openclaw-knowledge/skills/`; target workspace.
   - **[output]** Updated skill trees; version stamp optional in `memory/`.

3. Heartbeat / 本地定时任务与 workflow YAML 对齐（**非** API 轮询协作）。
   - **[input]** YAML：`openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`；`docs/REDIS_COLLABORATION.md`（`smartfactory:agent:heartbeat`）。
   - **[output]** Crontab/systemd：心跳、会议 skill、报告 skill；运维文档记录最近运行时间；**团队任务触发仍以 Redis Stream 为主**。

### W.2 Management agents

- **[input]** Raw requirements stream (Feishu + DB).
- **[output]** Decomposed work in DB; only escalate to human on `blocked` or policy exception.

### W.3 Humans

- **[input]** Feishu questions; browser/API for read-only or admin views.
- **[output]** Same APIs as agents; audit via existing logs.

---

## Further optimization

1. Shared NAS for code and repositories across OpenClaw hosts.
2. Local CI/CD (GitLab + runners) — **[input]** pipeline defs; **[output]** build artifacts linked from tasks.

---

## Repository layout (this project)

| Part | Path |
|------|------|
| **Smart Factory core** (API, SQLite, migrations, devops) | `core/` |
| **OpenClaw knowledge base** (workflows, standards, org workspaces, CLI, skills, MCP, scripts) | `openclaw-knowledge/` |
| **Product / API docs** | `docs/` |
| **Game dev golden rules** (OpenClaw + Godot checklist; iterate after each successful game) | [GAME_DEVELOPMENT_GOLDEN_RULES.md](./GAME_DEVELOPMENT_GOLDEN_RULES.md) |
| **Archived** (legacy game docs, monitoring, meeting scripts, experiments) | `archived/` |
