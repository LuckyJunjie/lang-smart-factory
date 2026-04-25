# 开发流程 - 需求驱动团队闭环

> 智慧工厂**两种等价标准流程**（按任务入口选用其一）：  
> - **A. Vanguard 协调（多设备）**：需求 → Redis 派发 → 团队消费任务 → 执行 → **Redis 上报结果与心跳** → **API 同步 DB** → 工作产物入 `work/<agent>/` → **推送远端** → 闭环。详见 [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)、[docs/REDIS_COLLABORATION.md](../../docs/REDIS_COLLABORATION.md)。  
> - **B. 团队独立（单团队闭环）**：**Master Jay / Winnie Chen** 直接 brief **Team Manager** → 读项目 `docs` 与代码做差距分析 → **spawn 预定义子代理** → 开发/测试/评审 → 产物入 `work/<agent>/`（建议 `input/`、`output/`）→ **推送远端** → 飞书汇报 **Master Jay**。**不依赖**跨设备 Redis/API 作为协调主路径。详见 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md)、`OPENCLAW_DEVELOPMENT_FLOW.yaml` 的 `team_standalone_cycle`。  
> **共用**：DoD [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md)、报告模板 `standards/report/`、CLI/Skills。  
> 技术细节（模式 A）：[cli/README.md](../cli/README.md)。

---

## 核心原则

### 模式 A（Vanguard 协调）

1. **任务发现**：团队从 **`smartfactory:stream:tasks`**（消费组 `dev-teams` / `test-teams`）获知派发信息；**禁止**以仅轮询 `GET /api/requirements` 作为协作主路径。`get-team-assigned` / API 仅用于与 DB 核对或 **Redis 不可用时的降级**。**Tesla / Newton** 测试主责，但可接收开发类分配；届时与 jarvis/codeforge/dinosaur 一样走 **develop_requirement** / **dev_team_cycle**（见 `OPENCLAW_DEVELOPMENT_FLOW.yaml`）。

### 模式 B（团队独立）

1. **任务发现**：以领导 brief 与项目文档为准；**不**将 `smartfactory:stream:tasks` 作为必选入口。可选仅用 Smart Factory DB 记账（`SMART_FACTORY_API`），不强制 Redis 消费组。

### 共用

2. **进度与存活（仅模式 A 强制跨机）**：模式 A 执行过程中 **`XADD smartfactory:stream:results`** 上报进度与结果摘要；按角色 **`PUBLISH smartfactory:agent:heartbeat`**（建议 ≤15 分钟）。模式 B 以团队内约定与最终报告为主；若未部署 Redis 则跳过流式上报。
3. **DB 为需求/任务字段的事实来源（模式 A）**：`requirements`、`tasks`、项目状态等以 **HTTP API**（`cli project` / project-mcp）为准；Redis 为 **实时事件层**。模式 B 可选同步 DB。
4. **一团队一需求（主责）**：团队主智能体（Team Main）同时只推进一条主需求，子任务由 Scrum/executor 分工；避免无序并行。
5. **工作产物路径**：凡本需求产生的设计笔记、脚本、测试日志、截图索引等，写入 **当前开发项目仓库根目录**（与该项目在 Smart Factory 中登记的 **`repo_url` 检出根** 一致）下的：

   ```text
   <project_repo_root>/work/<current_agent>/
   ```

   模式 B 建议在 `work/<agent>/input/`、`work/<agent>/output/` 区分输入材料与交付物（见 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) §5）。

6. **完成任务**：开发/测试在 **Git** 中提交**代码变更**；将 **测试结果报告**（含指向 `work/<agent>/` 中证据的路径或副本）纳入提交或 PR 说明；**push 到登记在项目上的远端**（`repo_url` 所指远程）后，**模式 A** 通过 **API** 将需求/任务置为应有状态并在 **`stream:results`** 中标记完成；**模式 B** 以领导验收与飞书汇报闭环（可选 API 更新）。

---

## 流程步骤（模式 A：Vanguard 协调）

模式 B 的分步叙述见 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) 第 3 节。

### 1. 接收任务（Redis）

- Team Main（或监听器）使用 **`XREADGROUP`** 消费 **`smartfactory:stream:tasks`** 中 **assignee** 为本团队的事件。
- 用 **cli project get-team-assigned \<team\>** 或 **GET** `assigned-requirements` **核对** DB 与 payload 是否一致（可选，降级时必用）。

### 2. 领取需求（API）

- **cli project take-requirement \<id\> --team \<team\> --agent \<agent\>**（Team Main 的 resident id，如 `jarvis` / `tesla`），或等价 **POST** `/api/requirements/<id>/take`。  
- 将 `status`、`step`、`assigned_*` 写入 DB，与 Redis 派发语义一致。

### 3. 分析、拆任务、分配 executor

- Team Main 分析需求，拆解子任务（**POST** `/api/tasks` 或 **PATCH** `/api/requirements/<id>` 更新 `step` 等）。
- Scrum Master（若存在）**PATCH** `/api/tasks/<id>` 设 **executor**；spawn 的专业智能体仅在 **`sessions_spawn`** 就绪后承接执行。
- 分析/分配细节可进 **`stream:results`** 载荷，并 **API** `report-task-detail` / `status-report` 落库（按 Hera/Vanguard 需要）。

### 4. 执行与持续上报

- 执行 **git / 构建 / 测试**；产物与日志放入 **`<project_repo_root>/work/<current_agent>/`**（可按日期或需求 id 分子目录，团队内约定即可）。
- **Redis**：定期或在里程碑点 **`XADD smartfactory:stream:results`**（`taskId`、`requirementId`、`team`、`status`、`progress`、`result.summary` 等）；**`PUBLISH smartfactory:agent:heartbeat`** 保持在线信号。
- **API**：用 **`PATCH /api/tasks/<id>`**、**`PATCH /api/requirements/<id>`**、`report-status` 等把**权威状态**写入 Smart Factory，供其他团队、仪表盘与 Hera 使用。

### 5. 阻塞

- **优先** **`PUBLISH smartfactory:task:blocker`** + **`XADD smartfactory:stream:blockers`**；降级 **POST** `/api/discussion/blockage`。  
- Hera 消费阻塞事件或 API，决策后 **assign/update** 并触发 **新一轮 Redis 派发**（由 Vanguard 流程完成）。

### 6. 完成需求：推送远端与关单

- 确认 **DoD**（测试、报告、文档要求见 [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md)）。
- **git commit**；**git push** 到 **`repo_url`** 对应远端（或团队约定的上游分支/PR 流程）。若遇 **GitHub 网络问题**，见 **`openclaw-knowledge/docs/GITHUB_NETWORK_AND_PUSH_RETRY.md`**（含 **每 5 分钟 cron 重试至成功后卸下** 的脚本说明）。  
- 提交说明或 PR 中引用：**测试结果**、相关 **`work/<agent>/`** 路径或附件清单。  
- **API**：将需求/任务更新为完成态（如开发团队 **developed**、测试 **tested** / 关闭路径按 [PROJECTS.md](./PROJECTS.md)）；**Redis**：最终 **`XADD smartfactory:stream:results`**（`status: completed`、摘要、commit/ref）。  
- 等待 **Vanguard** 下一轮 **`stream:tasks`** 事件进入下一需求（Tesla/Newton 测未测需求等规则不变）。

### 7. Bug / Enhancement（测试团队）

- Tesla/Newton：**POST** `/api/requirements` 创建 **type=bug** 或 **type=enhancement**；在 **`stream:results`** 中带上新需求 id。  
- 下一轮由 Vanguard **assign + Redis** 派回开发团队。

---

## 数据库字段说明

### requirements

| 字段 | 说明 |
|------|------|
| assigned_team | jarvis, codeforge, dinosaur, tesla, newton 等 |
| assigned_agent | 领取人（Team Main id 或登记负责人） |
| taken_at | 领取时间 |
| plan_step_id / plan_phase | 计划锚点 |
| step | not start \| analyse \| implement \| test \| verify \| done |
| progress_percent | 完成百分比 |

### tasks

| 字段 | 说明 |
|------|------|
| executor | 实际执行代理或成员标识 |
| status | 与后端约定一致 |

---

## 通道与工具速查

| 目的 | 首选 | DB / 降级 |
|------|------|-----------|
| 派发通知 | `PUBLISH smartfactory:task:dispatch` + `XADD smartfactory:stream:tasks` | `POST /api/requirements/<id>/assign`（须配合再发 Redis） |
| 领取 | （事件触发后）**take** API | — |
| 进度与结果 | **`XADD smartfactory:stream:results`** | `report_status` / `POST .../status-report` |
| 心跳 | **`PUBLISH smartfactory:agent:heartbeat`** | `POST .../machine-status` 等 |
| 阻塞 | blocker Pub/Sub + `stream:blockers` | `POST /api/discussion/blockage` |
| 状态字段 | — | **`PATCH` requirements/tasks**，**cli project** |

完整 HTTP 列表见 [docs/REQUIREMENTS.md](../../docs/REQUIREMENTS.md)、通信文档 §7。

---

## 数据初始化与计划同步

- **首次或清库**：`openclaw-knowledge/scripts/seed_factory_data.py` 或仓库内既有 seed（见 `scripts/README.md`）。  
- **24h 演练需求**：`python3 openclaw-knowledge/scripts/seed_24h_workflow_requirements.py`（见 [24H_WORKFLOW_TEST_DESIGN.md](../workflows/24H_WORKFLOW_TEST_DESIGN.md)）。  
- **pinball 计划同步**：`python -m skills.sync_game_plan` 或 `cli project sync-pinball-plan`（工程路径以环境为准）。

---

*智慧工厂 - OpenClaw 知识库与管理系统*
