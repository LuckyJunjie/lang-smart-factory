## 📊 最终日报模版（Hera & Vanguard 汇总）

> **⚠️ 模版性质**：本文件只定义**栏目结构、字段含义与书写规范**，**不是**可直接粘贴到飞书的定稿正文。文内示例 IP、示例表格行、`<N>` / `REQ-xxx` / `YYYY-MM-DD` 等均为**版式占位**，**禁止**原样当作真实状态对外汇报。  
> **实时数据**：发送最终日报**当时**，须通过 **Skill `generate_daily_report`**、**cli project**（及 **`GET /api/...` 汇总端点**，见 `docs/REQUIREMENTS.md`）**现查现填**在线状态、需求/任务/阻塞/风险等；若人工排版，亦须在**生成时刻**用拉取结果替换全部占位，不得使用历史快照或过期的复制粘贴。  
> **CLI 调用形式**：`python3 -m cli <domain> <subcommand>`（如 `python3 -m cli project list-teams-online`），依赖 `PYTHONPATH` 含 **`openclaw-knowledge`** 或等价工作区，详见 `openclaw-knowledge/cli/README.md`。

> **用途**：Hera 汇总阻塞与风险，Vanguard001 生成并发送「福渊研发部」飞书最终日报。**Hera 与 Vanguard 须汇报从子团队与系统获得的全部信息**，不得遗漏。  
> **执行方式**：通过 **CLI** 与 **Skills** 完成，不直接调用 API。  
> **数据来源（须全部拉取并纳入报告）**：
> - **Skill** `generate_daily_report`（Vanguard）：内部通过 **cli project** 拉取团队与机器状态、风险、**各团队任务明细与开发细节**，通过 **cli comm send-feishu** 发送飞书。
> - **cli project**（子命令均为 kebab-case）：`list-teams-online`、`get-team-assigned`、`list-tasks`（某需求下任务，含 risk、blocker、next_step_task_id）、`get-requirement`、`list-requirements`、`list-blockages`、`resolve-blockage` 等；**单条任务详情**当前无独立子命令，请用 **`GET /api/tasks/<id>`** 或 `list-tasks` 结果。  
> - **日报汇总块**（风险、团队状态摘要、开发细节、机器汇总）：由 Skill **`generate_daily_report`** 内 **`GET /api/dashboard/risk-report`**、`/api/teams/status-report/summary`、`/api/teams/development-details/summary`、`/api/teams/machine-status/summary` 拉取（与 `skills/generate_daily_report.py` 一致）；**并非**每个端点都有独立 `cli project` 封装。
> - **cli comm**：`send-feishu` 发送最终报告到飞书群。
> - 工作日志：由各角色通过 CLI/脚本写入（底层对接 API）。
> **执行侧前提（汇总前 Hera/Vanguard 可抽检）**：各团队应已将本周期产物落在 **目标项目** **`work/<current_agent>/<timestamp>-<worktype>/`**；任务与需求状态经 **API** 更新；**Redis** 侧已持续 **`XADD smartfactory:stream:results`** 与 **heartbeat**；并按 **30 分钟–1 小时** 节奏完成 **report-status（机器 + tasks[]）**。详见 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md)。

---

### 🧾 抬头信息

- **报告标题**：`📊 Smart Factory 项目状态汇报`
- **日期 / 时间范围**：`YYYY-MM-DD（如 2026-03-12）`，`覆盖时间段：HH:MM–HH:MM`
- **报告生成者**：`Vanguard001（自动）` / `<人工/Agent 名称>`
- **主要角色**：`Hera（风险与阻塞决策）`，`Vanguard001（最终汇总与飞书发送）`

---

### 🌐 API 与系统健康（API & System Health）

> 对齐 OpenClaw 通信设计的「系统健康度」部分。**cli project** 与 **Skill** `generate_daily_report` 依赖 Smart Factory API；若 Vanguard 节点 API 不可用，可回退到本地 API（需配置 `SMART_FACTORY_API` 或本地运行 API）。

- **Vanguard 节点（API）**：`<host:port>` — `✅ 正常 / ⚠️ 未响应（使用本地 API）`
- **本地 API**：`localhost:5000` — `✅ 运行中 / ⚠️ 异常`（供本地 cli project / Skill 使用）
- **数据库迁移 & 状态**（可选）：`<如已应用至 007_task_next_step_risk_blocker.sql，任务表含 next_step_task_id、risk、blocker>`

如使用回退策略，可简要写明：

- 当前使用：`<Vanguard 节点 API / 本地 API / 混合>`（通过 cli project 调用）
- 影响范围：`<如 list_teams_online、机器心跳依赖哪侧 API>`

---

### 🖥️ 机器与团队在线状态（Machines & Teams Online）

> 聚合各团队机器状态 + 在线判定（40 分钟内有状态上报视为 online）。**下表示意为栏目结构**；机器名/IP/团队与实时在线请以**汇报时** `list-teams-online`、machine-status 等为准（与 `docs/ORGANIZATION.md` 可能演进）。

#### 1. 机器状态总览

| 机器 | 团队 | IP | 角色 | 状态 | 最后在线 |
|------|------|----|------|------|----------|
| `vanguard` | `Vanguard/Hera` | `192.168.3.75` | 主控 | `🟢 online / 🔴 offline` | `YYYY-MM-DD HH:MM` |
| `tesla` | `Tesla` | `192.168.3.83` | 测试 + 玩家体验 | `🟢/🔴` | `...` |
| `newton` | `Newton` | `192.168.3.82` | 开发 | `🟢/🔴` | `...` |
| `jarvis` | `Jarvis` | `192.168.3.79` | 开发 | `🟢/🔴` | `...` |
| `codeforge` | `CodeForge` | `192.168.3.4` | 开发 | `🟢/🔴` | `...` |

**机器统计**：`<在线数>/<总数>` 在线

#### 2. 团队活跃度

| 团队 | 在线状态 | 最近状态上报时间 | 进行中需求数 | 阻塞数（pending） |
|------|----------|------------------|--------------|-------------------|
| `Tesla` | `🟢 active / 🔴 offline` | `YYYY-MM-DD HH:MM` | `<N>` | `<N>` |
| `Newton` | `🟢/🔴` | `...` | `<N>` | `<N>` |
| `Jarvis` | `🟢/🔴` | `...` | `<N>` | `<N>` |
| `CodeForge` | `🟢/🔴` | `...` | `<N>` | `<N>` |

---

### 📁 项目与需求总体进度（Projects & Requirements Summary）

> 对齐各团队通过 **cli project report-status** / **Skill** 上报的状态，按项目维度汇总整体进度。

| 项目 | 类型 | 描述 | 总需求数 | 完成 | 进行中 | 测试中 | 阻塞 | 关键说明 |
|------|------|------|----------|------|--------|--------|------|----------|
| `smart-factory` | 应用 | 智慧工厂 | `<N>` | `<N>` | `<N>` | `<N>` | `<N>` | `<今天的关键里程碑/变更>` |
| `pinball-experience` | 游戏 | 弹珠机体验 | `<N>` | `<N>` | `<N>` | `<N>` | `<N>` | `<如 0.1–0.5 完成情况>` |

#### 已完成关键需求（里程碑）

| ID | 需求名称 | 项目 | 所属团队 | 步骤 | 完成时间 | 报告链接 / 备注 |
|----|----------|------|----------|------|----------|------------------|
| `REQ-xxx` | `<title>` | `<project>` | `<team>` | `<step>` | `YYYY-MM-DD HH:MM` | `<DEV/TEST 报告、PR、构建链接>` |

#### 任务级状态与下一步（来自 list-tasks / status-report，须全部纳入）

> 从 **cli project list-tasks \<requirement_id\>** 及 **status-report/summary** 拉取；每条任务含 **risk**、**blocker**、**next_step_task_id**（先做该任务再继续）。Hera 可用 **update-task** 重分配或设下一步任务。

| 需求 ID | 任务 ID | 任务标题 | 状态 | 执行人 | 风险 | 阻塞 | 下一步任务 (next_step_task_id) |
|---------|---------|----------|------|--------|------|------|----------------------------------|
| `REQ-xxx` | `T-xxx` | `<title>` | `todo/in_progress/blocked/done` | `<executor>` | `<risk>` | `<blocker>` | `<先做的任务 id 或 —>` |

---

### 👥 各团队状态摘要（Per-Team Summary）

> 对接团队级别的 `TEAM_STATUS_REPORT_TEMPLATE`，每个团队 3–6 行摘要即可；详细表格在团队报告中。

#### Tesla 团队

- **需求数量**：`<总数>`（进行中 `<N>` / 完成 `<N>` / 阻塞 `<N>`）
- **当前重点**：`<例如：pinball 0.1–0.5 测试覆盖、Bug 回归>`
- **本日报告亮点**：
  - `<亮点 1：完成哪些测试场景/覆盖率提升>`
  - `<亮点 2：关键缺陷发现与处理>`
- **风险 / 注意事项**：`<例如：所有任务停留在 analyse 阶段，无实际测试输出>`

#### Newton 团队

- **需求数量**：`...`
- **当前重点**：`...`
- **亮点**：`...`
- **风险 / 注意事项**：`...`

#### Jarvis 团队

`<同上，简要列出>`

#### CodeForge 团队

`<同上，简要列出>`

---

### 🚧 阻塞与风险总览（Global Blockages & Risks）

> Hera 的视角：哪些问题正在拖慢整体进度、已经做了哪些决策。

#### 1. 关键阻塞（待处理或刚处理）

| Blockage ID | 需求 ID | 团队 | 原因摘要 | 创建时间 | 当前状态 | Hera 决策 / 建议 |
|-------------|---------|------|----------|----------|----------|-------------------|
| `B-xxx` | `REQ-xxx` | `<team>` | `<简短描述>` | `YYYY-MM-DD HH:MM` | `<pending/resolved>` | `<Hera 的决策，如重新分配/延后>` |

#### 2. 风险报告摘要（Risk Report）

- **来自 Hera 汇总（cli project 或 Skill 拉取 risk-report）的主要风险点**：
  - `<风险 1：如进度严重滞后、未上报团队>`  
  - `<风险 2>`  
  - `<风险 3>`  

---

### 🧪 开发与测试详情（Development & Test Details）

> **须全部纳入**：来源于 **GET /api/teams/development-details/summary**（各团队 **report-task-detail** 的 analysis / assignment / development）及 DEV/TEST 报告。Vanguard 通过 **cli project** 拉取 **development-details/summary** 后写入本段。

#### 1. 需求分析与拆解摘要（各团队 analysis）

- `REQ-xxx <title>` — `<team>`  
  - 分析/拆解要点：`<设计选型、依赖关系、子任务划分>`
  - 来源：task-detail detail_type=analysis

#### 2. 任务分配明细（各团队 assignment）

- `REQ-xxx` — `<team>`  
  - 分配要点：`<谁负责哪项、优先级、依据>`
  - 来源：task-detail detail_type=assignment

#### 3. 关键开发活动（各团队 development）

- `REQ-xxx <title>` — `<team>`  
  - 主要实现：`<1–3 行描述关键实现/重构/接口变更>`
  - 影响范围：`<受影响模块/系统>`
  - 相关报告 / PR：`<链接>`

#### 4. 关键测试活动

- `REQ-yyy <title>` — `Tesla`  
  - 执行用例：`<覆盖范围，如 Smoke / Regression / Full 0.1–0.5>`
  - 结果：`<通过率、发现 Bug 数>`  
  - 新建 Bug：`<Bug 需求 ID 列表，如 REQ-BUG-1, REQ-BUG-2>`

---

### 💬 讨论与决策纪要（Discussions & Decisions Digest）

> 汇总各团队 + Hera 在当天做出的「重要决策」，便于管理层快速过目。

- **架构 / 方案决策**：
  - `<例如：pinball 物理系统采用何种实现、Smart Factory API 版本升级策略>`
- **流程 / 资源调整**：
  - `<例如：Tesla 专注测试，Newton 接手某范围开发；某机器临时改作测试环境>`
- **跨团队协作事项**：
  - `<例如：Jarvis 与 Tesla 针对 0.1–0.5 需求的联调计划>`

如有关键讨论链接（飞书、issue、文档），可在此列出：

- `<链接 1>` — `<一句话说明>`
- `<链接 2>` — `<一句话说明>`

---

### 🔜 明日 / 下一周期计划（Next Period Plan）

- **总体目标**：
  - `<目标 1：例如完成 pinball 0.1–0.5 全量测试>`
  - `<目标 2：Smart Factory API 部署验证与健康检查>`
- **团队级目标简表**：

| 团队 | 明日重点 | 关键依赖 / 风险 |
|------|----------|-----------------|
| Tesla | `<例如：完成 REQ-1 测试并提交测试报告>` | `<例如：需要 dev 团队尽快修复某关键 Bug>` |
| Newton | `<例如：实现 REQ-A/REQ-C API>` | `<例如：依赖某环境/第三方服务上线>` |
| Jarvis | `...` | `...` |
| CodeForge | `...` | `...` |

---

### ✅ 汇报与存档（Reporting & Archiving Checklist）

- [ ] 已确认各团队执行侧满足 **work/**、**API**、**Redis** 与 **周期 report-status** 约定（见 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md) 与上文「执行侧前提」）
- [ ] 已确认正文数据来自**本次发送前**的实时拉取，而非本文档的静态示例或旧版缓存
- [ ] 已通过 **Skill** `generate_daily_report` 或 **cli comm send-feishu** 向「福渊研发部」发送本报告内容或链接
- [ ] 已通过 **cli project** 拉取并纳入报告**全部**数据：**status-report/summary**、**development-details/summary**（分析/分配/开发细节）、**list-tasks**（各需求任务含 risk、blocker、next_step_task_id）、机器状态汇总、risk-report、阻塞列表
- [ ] 任务级状态与下一步（含 risk、blocker、next_step_task_id）已在上文「任务级状态与下一步」中体现
- [ ] 各团队需求分析与拆解、任务分配明细、开发/测试详情已从 development-details/summary 纳入「开发与测试详情」
- [ ] 关键 DEV/TEST 报告已在上文引用并已存档（通过 CLI/Skill 对应流程）
- [ ] Hera / Vanguard 的关键工作日志已通过 CLI/脚本写入（底层对接工作日志 API）

