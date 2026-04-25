# 项目与需求追踪标准

> 与 [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)、[OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) 及 [DEVELOPMENT_FLOW.md](./DEVELOPMENT_FLOW.md) 一致。**项目与需求行级数据以 Smart Factory API / 数据库为唯一事实来源**（若使用 DB）；**多设备 Vanguard 协调时，跨团队「谁在干什么、进度事件」以 Redis Streams 为实时主路径**（见 [REDIS_COLLABORATION.md](../../docs/REDIS_COLLABORATION.md)）。**团队独立闭环**可不写 Redis 流，以团队内约定与飞书汇报为准。

---

## 1. 数据来源

- **协作事件（优先）**：`smartfactory:stream:tasks` / `stream:results` / `stream:blockers`，Pub/Sub `task:dispatch`、`task:blocker`、`agent:heartbeat`
- **项目列表**：`GET /api/projects`
- **需求列表**：`GET /api/requirements`（支持 `?status=`、`?assigned_team=`、`?assignable=1` 等，见 [REQUIREMENTS.md](../docs/REQUIREMENTS.md)）— **供查询与 Vanguard 分配决策**，**不是**执行机轮询任务的主通道
- **团队已分配需求**：`GET /api/teams/<team>/assigned-requirements` — 与 DB 对齐、**降级/审计**用
- **状态汇总**：`GET /api/teams/status-report/summary`（Hera/Vanguard 报表）
- **OpenClaw 代理**：优先 **`cli project`**（或 **project-mcp**，二者等同 HTTP）。**多设备 Vanguard 协调时须另接 Redis**，不得仅轮询 API/MCP 替代**跨团队**派发。**团队独立闭环**见 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md)，不以 Redis 为必选。

**项目与远程仓库（登记字段）**：每个 `project` 可维护 **`repo_url`**、**`repo_default_branch`**、**`repo_last_sync_at`**（上次登记的同步/检视时间）、**`repo_head_commit`**、**`repo_remote_notes`**；由各团队在确认本地与远端一致后通过 **`PATCH /api/projects/<id>`** 更新，便于全厂对齐同一仓库视图。详见 [REQUIREMENTS.md](../../docs/REQUIREMENTS.md) §1。

不应以本地 Markdown 表格为权威数据；如需快照可导出 API 结果或使用日报/仪表盘。

**分层可读编码**：API 为项目/需求/任务/测试用例返回 **`code`**（`P…-REQ…-TASK…-TC…`），便于事件与报告引用；规范见 [REQUIREMENTS.md](../../docs/REQUIREMENTS.md) §2.0。

---

## 2. 追踪字段说明

| 字段 | 说明 | API/DB 对应 |
|------|------|-------------|
| **完成百分比** | 需求进度 0–100% | `progress_percent` |
| **开始/领取时间** | 需求开始或团队领取时间 | `taken_at`、创建时间 |
| **预估完成** | 基于当前速度的预计完成日期（可选，可由报表计算） | 衍生字段 |
| **主要问题/阻塞** | 当前阻碍或需决策项 | 通过 `POST /api/discussion/blockage` 上报，Hera 处理 |
| **需求状态** | 见下节 | `status` |
| **需求阶段** | 分析/实现/测试等 | `step`（analyse, implement, test, verify, done） |

---

## 3. 需求状态与流程（与通信系统一致）

需求生命周期与 [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) 第 6 节一致（**Vanguard 协调、需求入 DB 时**）。领导直派、单团队闭环且**未**走 DB 分配时，以 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) 为准，状态字段可选同步 API。

| 状态 | 说明 | 谁操作 |
|------|------|--------|
| **new** | 新需求，待分配 | Vanguard 通过 `assign_requirement` 分配给主责开发团队（jarvis/codeforge/dinosaur）或 **Tesla / Newton**（当其承担该类开发或测试任务时） |
| **in_progress** | 已分配且已被团队领取，开发/测试进行中 | 团队 `take_requirement` 后自动设置 |
| **developed** | 开发完成，待测试 | 开发团队完成时 `update_requirement` 设置；Vanguard 将此类需求分配给 **Tesla / Newton**（测试团队） |
| **tested** | 测试完成 | Tesla / Newton 完成测试时 `update_requirement` 设置 |
| **done** | 需求已关闭 | 流程结束 |
| **blocked** | 被阻塞（如依赖未满足） | Hera 在依赖阻塞时 `update_requirement` 设置；可清空 `assigned_team` 延后 |

**类型**：`type=bug` 多由 Tesla / Newton 在测试中创建，与普通需求同一套流程，由 Vanguard 分配给**任一**具备开发能力的团队（含 Tesla / Newton 自修或 jarvis/codeforge/dinosaur）。

---

## 4. 团队与角色

| 团队 | 角色 | 需求职责 |
|------|------|----------|
| **jarvis / codeforge / dinosaur** | 开发（主责） | 领取 `status=new` 或已分配的本团队需求，开发完成后置为 developed |
| **tesla / newton** | 测试与体验（主责）+ 开发 | 主责：领取已 **developed** 的需求，测试通过置为 **tested**；Bug → `type=bug`，体验改进 → `type=enhancement`。**同等**：可按分配领取 **new** / in-progress 类开发与修复需求，走完 **developed** 闭环（测试基建、脚本、缺陷修复、功能改动等） |
| **Vanguard001** | 主控 | **事件驱动**分配：可分配需求 → **Redis 派发** + API `assign`；汇总发飞书 |
| **Hera** | 项目管理/风险 | **订阅/消费阻塞流**；决策后更新 DB 并协调再派发（Redis + API） |

详见 [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) 第 2、6 节；团队独立模式见 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md)。

---

## 5. 进度计算（参考）

预估完成日期可按下式估算（仅作参考，非 API 字段）：

```
estimated_end = start_date + (100 - progress_percent) / daily_progress_rate
```

日报与汇总以 API 返回的 `progress_percent`、`step` 及 status-report 为准。

---

## 6. 工具链（MCP 与 Skills）

与 [mcp/README.md](../mcp/README.md)、[skills/README.md](../skills/README.md) 及通信系统 §4–5 一致。

### MCP 服务

| 类别 | 服务 | 用途 |
|------|------|------|
| **Remote** | project-mcp | 需求/任务/分配/阻塞，对接 Smart Factory API |
| **Remote** | comm-mcp | 飞书消息等 |
| **Local** | dev-mcp, godot-mcp, test-mcp, analysis-mcp | 文件、Git、Godot、测试、分析 |

### Skills

| Skill | 执行者 | 用途 |
|-------|--------|------|
| assign_tasks_to_teams | Vanguard | 分配需求、发飞书汇总 |
| handle_blockage | Hera | 处理阻塞与重新分配/延后 |
| develop_requirement | jarvis / codeforge / dinosaur / **Tesla / Newton** | 领取、开发、上报、标记 developed（测试主责团队在被分配开发任务时与本行同等） |
| test_requirement | Tesla / Newton | 测试、创建 Bug、标记 tested；并以玩家视角收集 non-bug 改进（可创建 `type=enhancement`） |
| generate_daily_report | Vanguard | 日报汇总发飞书 |

---

## 7. 相关链接

- [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) — 多设备流程、API、MCP、Skills
- [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) — 团队独立闭环
- [DEVELOPMENT_FLOW.md](./DEVELOPMENT_FLOW.md) — 双模式：A. Vanguard + Redis/API；B. 独立团队，`work/<agent>/`，推送远端
- [REQUIREMENTS.md](../docs/REQUIREMENTS.md) — API 需求模块
- GitHub: https://github.com/LuckyJunjie/smart-factory
- Prometheus / Grafana：按实际部署填写（如 192.168.3.75:9090）
