## 📊 团队状态汇报模版（Team Status Report）

> **用途**：各执行团队（见下）每 **30 分钟–1 小时** 向 Hera 上报团队状态，供 Vanguard 最终汇总。  
> **适用对象**：团队 Scrum Master / 团队负责人；由 OpenClaw 代理通过 **CLI** 与 **Skills** 上报；底层对接 Smart Factory API（与 `docs/REQUIREMENTS.md`、`workflows/OPENCLAW_COMMUNICATION_SYSTEM.md` 一致）。  
> **CLI 形式**：`python3 -m cli project …`（`openclaw-knowledge` 需在 `PYTHONPATH`），见 `openclaw-knowledge/cli/README.md`。  
> **上报方式**：
> - **cli project**：`report-status`、`report-blockage`、`report-task-detail`；拉取用 `get-team-assigned`、`take-requirement`、`list-tasks`（子命令均为 kebab-case）。
> - **Skill**（与 `OPENCLAW_DEVELOPMENT_FLOW.yaml` 中 `required_skills` 对齐）：**`report_team_status`**（周期状态上报，推荐）；**`develop_requirement`**（开发主责团队）；**`test_requirement`**（测试主责团队，如 Tesla、Newton）；上述 Skill 内部会调用与 `report-status` 等价的 API/CLI 封装。

### 0. 工作产物路径、API、Redis（与本周期状态一并满足）

与 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md)、[REDIS_COLLABORATION.md](../../../docs/REDIS_COLLABORATION.md) 一致，本模版**周期上报**的同时须落实：

| 项 | 要求 |
|----|------|
| **产物落盘** | 目标项目 **`repo_url` 检出根** 下 **`work/<current_agent>/<timestamp>-<worktype>/`**，本会话产生的日志/截图索引/脚本等集中存放，`**report-status`** 或 **`report-task-detail`** 中可引用路径。 |
| **API** | **tasks[]** 带任务 **id** 时同步 DB；需求/任务阶跃用 **`PATCH`** 或由 **`update-requirement`** / **`list-tasks`** + **`update-task`** 与现场一致。 |
| **Redis** | 在 **`report-status`** 之外，仍须在执行流中 **`XADD smartfactory:stream:results`**（进度/摘要）并 **`PUBLISH smartfactory:agent:heartbeat`**（建议 **≤15 分钟**），与本文 30min–1h 节奏**叠加**，不是二选一。 |

---

### 🧾 抬头信息

- **团队**：`<jarvis | codeforge | newton | tesla | dinosaur>`（与 `assigned_team` / `docs/ORGANIZATION.md` 一致；协调侧日常汇总不以本模版替代 Vanguard/Hera 终报）
- **汇报人 / 代理**：`<姓名 or Agent ID>`
- **汇报时间**：`YYYY-MM-DD HH:MM`
- **汇报周期**：`<本次覆盖的时间段，如 14:00–14:30>`
- **数据来源**：`<Vanguard 节点 API | 本地 API | 混合>`（通过 cli project 调用）
- **对应 CLI / Skill**：
  - 状态与机器：**cli project report-status**（可带 machine_info、**tasks[]** 含 id/status/executor/risk/blocker/next_step_task_id，同步到 DB）
  - 阻塞：**cli project report-blockage**
  - 任务细节：**cli project report-task-detail**（detail_type: analysis | assignment | development），或 **Skill** `report_team_status` / `develop_requirement` / `test_requirement` 过程上报

---

### 📁 项目与需求概览（Overview）

> **目的**：快速让 Hera / Vanguard 理解当前团队在做什么。

| 项目 | 类型 | 描述 | 当前需求数 | 进行中 | 已完成 | 阻塞 |
|------|------|------|-----------|--------|--------|------|
| `<project_name>` | `<应用/游戏/...>` | `<一句话描述>` | `<N>` | `<N>` | `<N>` | `<N>` |

---

### 📋 需求与任务状态（Requirements & Tasks）

> 将团队当前负责的需求按状态拆分，必要时只列出有变更的条目；其他由 **cli project get-team-assigned \<team\>** 或历史记录补全。

#### 1. 进行中需求（In Progress）

| ID | 需求名称 | 项目 | 步骤 (step) | 进度 % | 负责人 | 关键任务 / 备注 |
|----|----------|------|-------------|--------|--------|-----------------|
| `REQ-xxx` | `<title>` | `<project>` | `<analyse/dev/test/...>` | `xx%` | `<member/agent>` | `<今日关键推进点>` |

#### 1.1 任务明细（与 DB 同步，供 Hera/Vanguard 汇总）

> 通过 **report-status** 的 `tasks[]` 上报；每项带 **id** 时会将 status、executor、risk、blocker、next_step_task_id、**est_tokens_total**、**prompt_rounds**（可选，粗略 LLM 用量）写入 DB。Hera 可用 **list-tasks**、**update-task**、**record-task-usage** 查看与更新。

| 任务 ID | 需求 ID | 标题 | 状态 | 执行人 | 风险 (risk) | 阻塞 (blocker) | 下一步任务 (next_step_task_id) | est_tokens（约） | prompt 次数（约） |
|---------|---------|------|------|--------|-------------|----------------|----------------------------------|------------------|-------------------|
| `T-xxx` | `REQ-xxx` | `<title>` | `todo/in_progress/blocked/done` | `<executor>` | `<简要>` | `<简要>` | `<先做该任务再继续，如 Bug 修复任务 id>` | `<可选，与 DB 一致>` | `<可选>` |

#### 2. 本周期完成（Completed in this period）

| ID | 需求名称 | 项目 | 步骤 | 完成时间 | 输出物（报告/代码/测试） |
|----|----------|------|------|----------|--------------------------|
| `REQ-xxx` | `<title>` | `<project>` | `<step>` | `YYYY-MM-DD HH:MM` | `<DEV/TEST 报告链接，主要输出>` |

#### 3. 新接收 / 待开始（Newly Assigned / Pending）

| ID | 需求名称 | 项目 | 分配时间 | 预估开始时间 | 预计完成时间 |
|----|----------|------|----------|--------------|--------------|
| `REQ-xxx` | `<title>` | `<project>` | `YYYY-MM-DD HH:MM` | `YYYY-MM-DD HH:MM` | `YYYY-MM-DD HH:MM` |

---

### 🚧 阻塞与风险（Blockages & Risks）

> 与 **cli project report-blockage**（上报）、**cli project list-blockages**（Hera 查询）对齐；风险由 Hera 通过 dashboard 汇总。若无则写「无」。

#### 1. 新增阻塞（本周期发现）

| Blockage ID | 需求 ID | 任务 ID (可选) | 团队 | 原因摘要 | 影响 | 已上报给 Hera？ |
|-------------|---------|----------------|------|----------|------|------------------|
| `B-xxx` | `REQ-xxx` | `<task-id?>` | `<team>` | `<原因，如依赖前置需求未完成>` | `<影响，如进度延迟>` | `是/否（若否，说明原因）` |

#### 2. 已处理 / 解除阻塞

| Blockage ID | 需求 ID | Hera 决策摘要 | 当前状态 | 后续行动 |
|-------------|---------|----------------|----------|----------|
| `B-xxx` | `REQ-xxx` | `<重新分配/延后/关闭>` | `<resolved/closed/...>` | `<团队接下来要做什么>` |

#### 3. 其他风险提示（非正式阻塞）

- `<例如：测试资源紧张 / 代码评审排队 / 机器性能瓶颈等>`

---

### 🖥️ 机器与在线状态（Machines & Online Status）

> 通过 **cli project report-status** 的 machine_info 字段上报，或由部署在该机器上的脚本/代理上报；与 Vanguard 汇总的机器状态一致。

| 机器 | IP | 角色 | 状态 | 最后在线时间 | 备注 |
|------|----|------|------|--------------|------|
| `<hostname>` | `<ip>` | `<dev/test/main>` | `🟢 online / 🔴 offline` | `YYYY-MM-DD HH:MM` | `<如在跑什么任务>` |

**机器统计**：`<在线数>/<总数>` 在线

---

### 🧪 开发 / 测试详情摘要（Development & Test Details）

> 提炼关键的分析 / 分配 / 开发 / 测试过程，便于 Hera 与最终报告引用。  
> 通过 **cli project report-task-detail** 上报（detail_type: **analysis** | **assignment** | **development**），或 **Skill** `develop_requirement` / `test_requirement` 过程上报；Hera/Vanguard 从 **development-details/summary** 拉取汇总。

- **分析要点**（analysis）：
  - `<需求 REQ-xxx 的主要分析结论、拆解结果、设计选型、依赖关系>`
- **任务分配要点**（assignment）：
  - `<本周期调度 / 分配的逻辑，谁负责哪项任务、依据与优先级>`
- **开发 / 测试要点**（development）：
  - `<本周期实际完成的关键实现或测试结论>`

---

### 💬 团队讨论与决策（Discussions & Decisions）

> 重点记录「做出了什么决定」而不是「聊了什么」。

- **会议 / 讨论**：
  - 时间：`YYYY-MM-DD HH:MM`
  - 主题：`<主题，如 Step 0.6 Skill Shot 方案评审>`
  - 结论：`<关键结论与行动项列表>`
- **重要异步讨论**（如飞书、issue）：
  - 链接：`<消息或 issue 链接>`
  - 摘要：`<1–3 行说明>`

---

### 🔜 下一步计划（Next Steps）

> 对应工作日志的 `task_output` / `next_step`；可由 CLI/脚本写入工作日志（底层对接 Smart Factory API）。

- **下一报告周期内的重点目标**：
  - `<目标 1>`
  - `<目标 2>`
- **预期需要 Hera / Vanguard 支持的点**：
  - `<如需要决策、资源、跨团队协调的事项>`

---

### ✅ 同步确认（Sync Checklist）

- [ ] 本周期产出已写入 **`<project_repo_root>/work/<current_agent>/<timestamp>-<worktype>/`**（或等价可追溯路径已在报告中说明）
- [ ] 任务/需求状态已通过 **API**（含 **report-status** 的 **tasks[]**）与当前现场一致
- [ ] 已按规范追加 **Redis**：**`stream:results`**（进度/摘要）与 **agent heartbeat**（建议 ≤15 分钟内有效）
- [ ] 已通过 **cli project report-status** 上报本次状态（含 progress、step、**tasks[]**：带 **id, status, executor, risk, blocker, next_step_task_id** 的条目会同步到 DB，可选 machine_info）
- [ ] 机器状态已通过 **report-status** 上报（payload 字段 **`machine_info`**）或本地脚本上报
- [ ] 对新增阻塞已通过 **cli project report-blockage** 上报
- [ ] 需求分析/拆解、任务分配、开发细节已通过 **cli project report-task-detail**（analysis/assignment/development）或 **Skill**（`report_team_status` / `develop_requirement` / `test_requirement`）上报
- [ ] 若有开发/测试完成，已按规范提交 **开发任务报告 / 测试任务报告** 并在上文引用

