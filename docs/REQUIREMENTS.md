# 智慧工厂需求文档

> 版本: 1.5 | 更新日期: 2026-04-08

本文档以 **HTTP API** 形式描述 Smart Factory **持久化层**（项目、需求、任务、机器状态、讨论等）。**Vanguard 多设备协作**下，**实时派发、任务协调与状态流**以 **Redis 事件总线**（Pub/Sub + Streams）为首选，**应优先使用 Redis** 连接各团队；API **不负责**作为**跨团队**任务发现的轮询通道，但在 Redis 不可用或需审计/报表时作为 **fallback** 与数据源。**单团队独立闭环**见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)，**不强制** Redis。完整拓扑、频道、消费组与心跳规范见 **[REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md)**（多设备模式下必读，置于 API 细则之前）。

### Smart Factory API 服务部署（vanguard001）

- **API 进程**：运行在 **vanguard001** 设备（树莓派，默认 **192.168.3.75**），与 [ORGANIZATION.md](./ORGANIZATION.md) 中主控节点一致；与 **Redis Server** 同机部署便于运维与内网访问。
- **其他团队设备**（Jarvis、CodeForge、Tesla、Newton、Hera 等）：**不作为** Smart Factory API 的宿主；通过 **`SMART_FACTORY_API`** 指向该主机，例如 `http://192.168.3.75:5000/api`（端口以实际 `core/api/server.py` 配置为准），进行项目/需求/任务的 **远程读写** 与状态上报。
- **project-mcp（remote）**：通常也只部署在可稳定访问上述 API 的节点（多为 vanguard001 或同网段网关侧），各 OpenClaw 代理经 MCP 或 **cli project** 间接访问同一 API。

---

## 协作层：Redis 事件总线（Vanguard 多设备优先）

| 维度 | Redis（首选） | HTTP API（本文件 §1 起） |
|------|----------------|---------------------------|
| 任务派发、通知团队开工 | `PUBLISH smartfactory:task:dispatch` + `XADD smartfactory:stream:tasks` | 降级：`POST /api/requirements/<id>/assign` 等 + 人工协调 |
| 执行过程进度与结果流 | `XADD smartfactory:stream:results`，消费组 `dev-teams` / `test-teams` | 降级：`POST /api/teams/<team>/status-report` |
| 阻塞与决策 | `smartfactory:task:blocker`、`smartfactory:stream:blockers`，Hera 消费 `hera-group` | 降级：`POST /api/discussion/blockage` |
| 机器/代理在线（实时） | `PUBLISH smartfactory:agent:heartbeat`（须 **按时**，建议 ≤15 分钟） | 补充持久化：`POST /api/teams/<team>/machine-status`、`status-report` |
| 项目/需求/任务 CRUD 与查询 | 事件中可携带 id；**真相源写入**仍走 API | `GET`/`POST`/`PATCH` 各资源 |

- **Redis Server**：部署在 **vanguard001** 设备（默认与 [ORGANIZATION.md](./ORGANIZATION.md) 同机，如 `192.168.3.75`）；其他机器均为 **客户端**（订阅任务列表、派发频道、上报结果）。  
- **流程与角色**：[OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)、[OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)。**单团队独立闭环**（领导直派、无跨设备 Redis 协调必选）见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)；该模式下 API/Redis 仅可选（如台账），不改变本节 HTTP 规格本身。  
- **禁止**（**多设备 Vanguard 模式**下）：以 **仅** 轮询 `GET /api/requirements` 或 **仅** Cron 拉 API 作为团队间任务协作主路径（Redis 正常时）。

以下各节为 **REST API** 规格，供持久化、仪表盘、MCP/CLI 及 **Redis 降级** 使用。

**Agent / MCP 对接**：HTTP 接口可由 **project-mcp**（remote）暴露，工具见 [OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) 与 [openclaw-knowledge/mcp/README.md](../openclaw-knowledge/mcp/README.md)。**模式 A** 下跨团队 **派发与状态流** 请按 [REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md) 配置 Redis，不得以「只调 API」替代事件总线（除非显式降级）。**模式 B** 见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)。

---

## 1. 项目管理模块 (Projects)

项目表除名称、描述、类型外，承载**当前关联代码仓与远端信息**（便于各设备对齐同一仓库视图；具体 `git pull` 仍在本机执行，DB 中记录为**登记/同步元数据**）：

| 字段 | 说明 |
|------|------|
| `repo_url` | 远程仓库克隆 URL（HTTPS/SSH，如 `git@github.com:org/smart-factory.git`） |
| `repo_default_branch` | 默认分支（如 `main` / `master`） |
| `repo_last_sync_at` | **上次登记**的与远端对齐时间（ISO 8601 字符串，由代理或运维 `PATCH` 更新，非自动 git hook） |
| `repo_head_commit` | 当时记录的 **HEAD 提交**（完整或缩短 SHA，可选带标签说明） |
| `repo_remote_notes` | 可选备注（例如「生产只读镜像」「子模块在 xxx」） |
| `updated_at` | 项目行任意字段更新时由服务端刷新 |

创建时可省略上述可选字段；建议在里程碑或每日站会后将各团队机器上确认的 **`repo_head_commit` + `repo_last_sync_at`** 写回项目，便于 Vanguard/Hera 汇总与审计。

**可读编码 `code`（项目）**：`GET /api/projects`、`GET /api/projects/<id>` 的每条项目带 **`code`**，格式见下文 **§2.0** 中 **项目段**（`P<id>-…`），由 **`name`** 派生，**不入库**（服务端即时计算）。

### 1.1 列出项目
- **API**: `GET /api/projects`
- **功能**: 列出所有项目
- **返回**: 项目列表（每项含 **`code`**，§2.0）

### 1.2 创建项目
- **API**: `POST /api/projects`
- **功能**: 创建新项目
- **参数**: name, description, type, status?, gdd_path?, **repo_url**, **repo_default_branch?**, **repo_last_sync_at?**, **repo_head_commit?**, **repo_remote_notes?**, category?, purpose?, benefits?, outcome?, priority?

### 1.3 获取项目详情
- **API**: `GET /api/projects/<id>`
- **功能**: 获取单个项目详情（含 **`code`**，§2.0）

### 1.4 获取项目需求
- **API**: `GET /api/projects/<id>/requirements`
- **功能**: 获取项目下的所有需求（每项含需求级 **`code`** = `P…-REQ…`，§2.0）

### 1.5 更新项目
- **API**: `PATCH /api/projects/<id>`
- **功能**: 更新项目字段（含 HIGH_REQUIREMENTS 元数据与远程仓库登记）
- **支持字段**: name, description, type, status, gdd_path, repo_url, **repo_default_branch**, **repo_last_sync_at**, **repo_head_commit**, **repo_remote_notes**, **category**, **purpose**, **benefits**, **outcome**, **priority** (P0–P3)

### 1.6 删除项目
- **API**: `DELETE /api/projects/<id>`
- **功能**: 删除项目；若仍存在需求则返回 **409**（需先迁移或删除需求）

---

## 2. 需求管理模块 (Requirements)

### 2.0 分层可读编码 (Code) — 项目 / 需求 / 任务 / 测试用例

除数字 **`id`** 外，API 为资源生成**分层可追溯 `code`**（服务端根据 **id + 标题/名称** 计算，**不入库**），便于 Redis 载荷、飞书与 `work/` 目录命名对齐。格式为 **段串联**，段内为 **`类型前缀` + `数字 id` + `-` + 英文 slug**：

| 段 | 前缀 | 标题来源 | 纳入词数（上限） | 示例段 |
|----|------|----------|------------------|--------|
| 项目 | `P` | `projects.name` | **6** | `P2-pinball-experience-game-studio` |
| 需求 | `REQ` | `requirements.title` | **10** | `REQ74-baseline-zero-dot-six-skill-shot` |
| 任务 | `TASK` | `tasks.title` | **10** | `TASK12-implement-collision-for-flippers` |
| 测试用例 | `TC` | `test_cases.title` | **10** | `TC4-screenshot-main-menu-layout` |

**Slug 规则**：取标题中**前 N 个单词**（按空格分词）；每个词只保留**字母与数字**并转小写；词之间用 **`-`** 连接；总长封顶（服务端约 **72** 字符）时右截断。无标题时用占位 `n-a`。

**完整 `code` 串**：

- **项目**（仅项目段）：`P<project_id>-<slug-from-name>`
- **需求**：`<项目段>-<需求段>`，例：`P2-pinball-experience-REQ1-user-auth-story`
- **任务**：`<需求完整 code>-<任务段>`，例：`…-TASK3-build-login-api`
- **测试用例**：`<需求完整 code>` 后，若 **`task_id` 非空**则插入 **`<任务段>`**，再接 **`<TC 段>`**；若无关联任务则 **`TASK` 段省略**，例：`P2-…-REQ1-…-TC5-login-form-validation`

**兼容与索引**：历史文档若出现旧格式 `0001-project-slug-0.1-0003`，以本 **`§2.0`** 与 API 当前返回为准；**DB 仍以整数 `id` 为主键**。

**出现位置**：`GET /api/projects`、`GET /api/projects/<id>`、`GET /api/projects/<id>/requirements`、`GET/POST /api/requirements` 列表与详情、`GET /api/teams/.../assigned-requirements`、`GET /api/requirements/<id>/tasks`、`GET /api/tasks/<id>`、`GET/POST /api/requirements/<rid>/test-cases`、`GET /api/test-cases/<id>` 等响应中的 **`code`** 字段（创建测试用例 **201** 体可选带 **`code`**）。

### 2.1 列出需求
- **API**: `GET /api/requirements`
- **功能**: 列出所有需求，支持过滤
- **参数**: status, priority, assigned_team

### 2.2 创建需求
- **API**: `POST /api/requirements`
- **功能**: 创建新需求。**Tesla（测试/玩家体验）发现问题或改进点**时创建需求：若属于缺陷则创建 Bug 需求（`type: "bug"`，填写 project_id、title、description（可注明关联原需求/步骤））；若属于非 Bug 的体验/玩法/平衡/可用性改进则创建 enhancement 需求（`type: "enhancement"`）。下一轮由 Vanguard 将 `status=new` 的需求分配给开发团队实现。
- **参数**: project_id, title, description, priority, type（含 feature, bug, enhancement, asset, research）；可选 **parent_requirement_id**（子需求）、**depends_on**（JSON 数组，需求 id 列表）、**note**

### 2.3 获取需求详情
- **API**: `GET /api/requirements/<id>`
- **功能**: 获取需求详情

### 2.4 更新需求
- **API**: `PATCH /api/requirements/<id>`
- **功能**: 更新需求字段
- **支持字段**: title, description, priority, status, step, note, type, assigned_to, assigned_team, assigned_agent, taken_at, plan_step_id, plan_phase, progress_percent, depends_on, **parent_requirement_id**, design_doc_path, acceptance_criteria

### 2.5 领取需求
- **API**: `POST /api/requirements/<id>/take`
- **功能**: 团队领取需求，设置 assigned_team、assigned_agent，status 自动设为 in_progress
- **参数**: assigned_team (团队名), assigned_agent (领取人)

### 2.6 自动拆分任务
- **API**: `POST /api/requirements/<id>/auto-split`
- **功能**: 根据需求类型自动生成开发任务

### 2.7 分配需求 (Vanguard / Hera)
- **API**: `POST /api/requirements/<id>/assign`
- **功能**: Vanguard 将需求分配给指定团队（assigned_team）。status=new 时可分配给任意团队（含 type=bug 的 Bug 需求）；status=in_progress 时仅可分配给 tesla（转交测试）。**Hera** 在开发团队依赖阻塞时可使用此接口给该团队**重新分配**另一条 new 需求。
- **参数**: assigned_team (团队名)
- **示例**: `POST /api/requirements/74/assign` Body: `{"assigned_team": "jarvis"}` 或 `{"assigned_team": "tesla"}`（in_progress 转测试）

### 开发流程
详见 [openclaw-knowledge/standards/DEVELOPMENT_FLOW.md](../openclaw-knowledge/standards/DEVELOPMENT_FLOW.md)：**两种等价模式** — **A.** Vanguard 协调（多设备）：Redis 派发与结果/心跳、API 写 DB、产物 `work/<agent>/`、推送远端关单；**B.** 团队独立闭环：领导直派 Team Manager，无跨设备 Redis 必选，DoD/报告与 A 共用，见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)。

---

## 3. 任务管理模块 (Tasks)

### 3.1 获取需求任务
- **API**: `GET /api/requirements/<id>/tasks`
- **功能**: 获取需求下的所有任务（含 **分层 `code`** §2.0、next_step_task_id、risk、blocker）

### 3.2 获取单个任务
- **API**: `GET /api/tasks/<id>`
- **功能**: 获取单条任务（含 **`code`** §2.0、next_step_task_id、risk、blocker，供 Hera 重分配用）

### 3.3 创建任务
- **API**: `POST /api/tasks`
- **功能**: 创建新任务
- **参数**: req_id, title, description, executor

### 3.4 更新任务
- **API**: `PATCH /api/tasks/<id>`
- **功能**: 更新任务；服务端/Hera 可重分配、设下一步任务
- **支持字段**: title, status, executor, output_path, step, **next_step_task_id**（可选，先做该任务再继续，如先修 Bug）, **risk**, **blocker**, **note**, **est_tokens_total**, **prompt_rounds**
- **LLM 用量（任务级，粗略）**：**`est_tokens_total`** 为非负整数，表示该任务累计**估算 token**（代理/工具自行汇总，非计费精度）；**`prompt_rounds`** 为非负整数，表示**模型调用 / prompt 轮次**约数。可通过 **`cli project record-task-usage`** 或 Skill **`record_task_usage`** 增量上报，亦可本接口直接 PATCH。**`report-status`** 的 **tasks[]** 带 **`id`** 时也可同步这两项（见 §4.5.6）。
- **流程**: 阻塞任务可设 status=blocked、next_step_task_id=修 Bug 任务 id；Bug 完成后清除 next_step_task_id 并恢复原任务

### 3.5 测试用例（V 模型 / 测试计划，HIGH_REQUIREMENTS §3.3）

测试用例表按 **requirement_id** 归属；可选 **task_id** 关联到该需求下的实现任务。

| 方法 | API | 说明 |
|------|-----|------|
| GET | `/api/requirements/<rid>/test-cases` | 列出某需求下全部测试用例（每项 **full `code`** §2.0） |
| POST | `/api/requirements/<rid>/test-cases` | 创建：`title` 必填；可选 `layer`（unit \| component \| integration \| screenshot \| console \| system）、`task_id`、`description`、`status`、`result_notes`；**201** 响应体可含 **`code`** |
| GET | `/api/test-cases/<id>` | 获取单条（含 **`code`** §2.0） |
| PATCH | `/api/test-cases/<id>` | 更新：`task_id`, `layer`, `title`, `description`, `status`, `result_notes`（`task_id` 须属于同一需求） |
| DELETE | `/api/test-cases/<id>` | 删除 |

---

## 4. 机器管理模块 (Machines)

### 4.1 列出机器
- **API**: `GET /api/machines`
- **功能**: 列出所有机器

### 4.2 更新机器状态
- **API**: `POST /api/machines/<id>/status`
- **功能**: 更新机器在线状态

---

## 4.5 团队通信 API (OpenClaw Communication)

> **多设备 Vanguard 协调下，协作主路径为 Redis**（见正文开头「协作层」与 [REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md)）。**单团队独立闭环**（[OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)）**不强制**本节所描述的 Redis 消费组/心跳；可选仅用 API 记账或完全本地闭环。  
> 本节 API 用于：**持久化**团队状态、**仪表盘/飞书汇总**、**Redis 不可用时的降级**，以及需写入 DB 的 **machine-status / status-report**。在 **模式 A** 下，OpenClaw **应**配置 Redis 消费组与心跳，避免长期仅依赖本节轮询。

### 4.5.1 团队分配需求
- **API**: `GET /api/teams/<team>/assigned-requirements` 或 `GET /api/teams/assigned-requirements?team=<team>`
- **功能**: 查询分配给某团队的需求（支持 status 过滤）
- **示例**: `GET /api/teams/jarvis/assigned-requirements?status=new`

### 4.5.2 在线团队
- **API**: `GET /api/teams/online`
- **功能**: 列出在线团队（机器心跳、machine_status 2h 内、或 status_report 40 分钟内；超过 40 分钟未上报视为 offline）

### 4.5.3 团队机器状态
- **API**: `POST /api/teams/<team>/machine-status`
- **功能**: 团队上报机器状态（自定义 JSON 格式）
- **参数**: payload (JSON), reporter_agent

### 4.5.4 获取团队状态
- **API**: `GET /api/teams/<team>/machine-status`
- **功能**: 获取某团队最近状态报告

### 4.5.5 状态汇总
- **API**: `GET /api/teams/machine-status/summary`
- **功能**: 获取各团队最新状态（Vanguard 汇总用）

### 4.5.6 团队状态上报（含任务明细）→ Hera → Vanguard
- **API**: `POST /api/teams/<team>/status-report`
- **功能**: 团队上报状态（requirement, progress, tasks[]）给 Hera；建议每 20 分钟上报，超过 40 分钟未上报则视为 offline。tasks 中每项可带可选字段 **analysis_notes**、**assignment_notes**、**development_notes**（分析/分配/开发细节），以及 **id**、**status**、**executor**、**risk**、**blocker**、**next_step_task_id**、**est_tokens_total**、**prompt_rounds**（粗略 LLM 用量，见 §3.4）；带 id 的条目会**同步到 DB**，供服务端重分配与下一步流程使用。
- **参数**: payload (JSON), reporter_agent

- **API**: `GET /api/teams/<team>/status-report`
- **功能**: 获取某团队最近状态报告

- **API**: `GET /api/teams/status-report/summary`
- **功能**: Hera 汇总各团队最新报告；每条带 `active`（最近上报在 40 分钟内为 true，否则为 false/offline）

- **API**: `GET /api/dashboard/risk-report`
- **功能**: Hera 风险报告（stuck, blocked, slow）

### 4.5.7 任务开发过程细节（进入最终报告）
- **API**: `POST /api/teams/<team>/task-detail`
- **功能**: 团队汇报特定任务的开发过程细节；Body: requirement_id, task_id, detail_type（analysis | assignment | development）, content。用于分析细节、任务分配细节、开发细节，与 status-report 一并由 Vanguard 汇总进最终飞书报告。
- **API**: `GET /api/teams/<team>/task-details`
- **功能**: 查询某团队已上报的任务细节；可选 ?requirement_id=, ?limit=
- **API**: `GET /api/teams/development-details/summary`
- **功能**: 各团队开发过程细节汇总（Hera/Vanguard 最终报告用）；可选 ?per_team=

### 4.5.8 讨论与风险处理（Team 上报阻塞 → Hera 协调）
- **API**: `POST /api/discussion/blockage`
- **功能**: 团队上报阻塞/需决策项；Body: team, requirement_id, task_id?, reason, options?。**依赖阻塞**时 reason 注明「依赖前置任务未完成」，便于 Hera 重新分配与延后。
- **API**: `GET /api/discussion/blockages`
- **功能**: Hera 查询待处理阻塞列表；可选 ?status=pending
- **API**: `PATCH /api/discussion/blockage/<id>`
- **功能**: Hera 更新决策（status=resolved, decision）。**依赖阻塞**时 Hera 还可：给该团队 `POST /api/requirements/<other_id>/assign` 重新分配另一任务；对原需求 `PATCH /api/requirements/<id>` 设 status=blocked 或清空 assigned_team 延后处理。

---

## 5. 工具链模块 (Tools)

### 5.1 列出工具
- **API**: `GET /api/tools`
- **功能**: 列出所有工具

### 5.2 注册工具
- **API**: `POST /api/tools`
- **功能**: 注册新工具
- **参数**: name, type, source, path, config

---

## 6. Pipeline 模块

### 6.1 列出流水线
- **API**: `GET /api/pipelines`
- **功能**: 列出所有流水线

### 6.2 创建流水线
- **API**: `POST /api/pipelines`
- **功能**: 创建新流水线

### 6.3 获取流水线详情
- **API**: `GET /api/pipelines/<id>`
- **功能**: 获取流水线配置

### 6.4 触发构建
- **API**: `POST /api/pipelines/<id>/run`
- **功能**: 触发流水线执行

### 6.5 获取构建历史
- **API**: `GET /api/pipelines/<id>/runs`
- **功能**: 获取流水线构建历史

### 6.6 删除流水线
- **API**: `DELETE /api/pipelines/<id>`
- **功能**: 删除流水线

---

## 7. CI/CD 触发器模块

### 7.1 获取触发器
- **API**: `GET /api/pipelines/<id>/triggers`
- **功能**: 获取流水线的触发器

### 7.2 创建触发器
- **API**: `POST /api/pipelines/<id>/triggers`
- **功能**: 创建新的触发器

### 7.3 GitHub Webhook
- **API**: `POST /api/webhook/github`
- **功能**: 处理 GitHub Webhook 事件

### 7.4 构建列表
- **API**: `GET /api/cicd/builds`
- **功能**: 列出所有构建记录

### 7.5 构建详情
- **API**: `GET /api/cicd/builds/<id>`
- **功能**: 获取构建详情

### 7.6 更新构建状态
- **API**: `PATCH /api/cicd/builds/<id>/status`
- **功能**: 更新构建状态

---

## 8. 飞书集成模块

### 8.1 分析日志
- **API**: `POST /api/feishu/logs/analyze`
- **功能**: 分析飞书 API 调用日志（内部调用 `openclaw-knowledge/mcp/remote/comm_mcp/feishu_log_analysis`；代理可用 comm-mcp 工具 `analyze_feishu_logs`、`get_feishu_api_stats`、`analyze_feishu_issues`）

### 8.2 统计信息
- **API**: `GET /api/feishu/stats`
- **功能**: 获取飞书 API 调用统计

### 8.3 发送消息
- **API**: `POST /api/feishu/post`
- **功能**: 向飞书群发送消息（需配置 FEISHU_WEBHOOK_URL 或传入 webhook_url）
- **参数**: text/content/message, title, webhook_url (可选)

---

## 9. DevOps 模块

### 9.1 列出 Runner
- **API**: `GET /api/devops/runners`
- **功能**: 列出所有 DevOps Runner

### 9.2 Runner 状态
- **API**: `GET /api/devops/runners/windows/status`
- **功能**: 获取 Windows Runner 状态

### 9.3 部署 Runner
- **API**: `POST /api/devops/runners/windows/setup`
- **功能**: 部署 Windows Runner

### 9.4 启动/停止 Runner
- **API**: `POST /api/devops/runners/windows/start`
- **API**: `POST /api/devops/runners/windows/stop`

---

## 10. 仪表盘模块

### 10.1 统计面板
- **API**: `GET /api/dashboard/stats`
- **功能**: 获取项目、需求、任务统计信息
