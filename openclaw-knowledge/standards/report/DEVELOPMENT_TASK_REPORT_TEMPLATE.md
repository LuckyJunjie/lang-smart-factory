# 开发任务报告模版

> **各常驻团队**在承担**开发类**工作且**需求/任务完成时**按此模版填写并随 status-report 或 task-detail 上报，供 Hera/Vanguard 汇总与飞书展示（与 [ORGANIZATION.md](../../../docs/ORGANIZATION.md)「各团队默认同时具备开发与测试能力」一致：测试主责团队完成脚本、修复、环境等开发产出时同样使用本模版）。  
> **与 DB 对齐**：任务表含 **next_step_task_id**、**risk**、**blocker**；上报时通过 **report-status** 的 tasks[]（id、status、executor、risk、blocker、next_step_task_id）同步到 DB，或通过 **report-task-detail** 提交分析/分配/开发细节。  
> 与最新 DB 对齐：任务含 **status, executor, risk, blocker, next_step_task_id**；status-report 的 tasks[] 带 id 时会同步到 DB。

---

## 0. 工作产物路径、API 状态、Redis 与周期汇报（必读）

与 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md)、[DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md)、[REDIS_COLLABORATION.md](../../../docs/REDIS_COLLABORATION.md) 一致：

| 要求 | 说明 |
|------|------|
| **工作产物目录** | 在**目标项目**仓库根（该项目在 Smart Factory 中登记的 **`repo_url` 检出根**）下落地：**`<project_repo_root>/work/<current_agent>/<timestamp>-<worktype>/`**。`<current_agent>` 为执行本步骤的代理 id（小写，与 workspace 目录名一致）；**`<timestamp>-<worktype>`** 为本轮交付或会话目录名（例：`20260404T1530-dev`、`20260404-req74-analysis`）。设计笔记、脚本、测试日志、截图索引、报告草稿等均放此处；本报告 **输出说明** 须写清相对或可追溯路径。 |
| **任务/需求状态（API）** | **DB 权威**：通过 **`PATCH /api/tasks/<id>`**、**`PATCH /api/requirements/<id>`**、`cli project update-requirement`、`report-status`（**tasks[]** 带任务 **id** 时同步 **status / executor / risk / blocker / next_step_task_id**）更新，与协作事件语义一致。 |
| **Redis（优先）** | 执行过程中及里程碑：**`XADD smartfactory:stream:results`**（进度、摘要、**work 路径** commit/PR 线索等）；**`PUBLISH smartfactory:agent:heartbeat`**（建议 **≤15 分钟**）；阻塞优先 **`smartfactory:task:blocker`** + **`XADD smartfactory:stream:blockers`**。Redis 正常时**不能用「只写本地」代替**跨团队可见的进度线。 |
| **周期汇报** | **30 分钟–1 小时**（或团队明文约定）上报 **机器 + 任务**：**`cli project report-status`**（含 **machine_info**、**tasks[]**）和/或 增量写入 **`smartfactory:stream:results`**；勿仅靠任务完成时单次填报。 |

---

## 1. 基本信息

| 字段 | 填写说明 |
|------|----------|
| **团队** | 填报方所属常驻团队 id：`vanguard001` / `hera` / `jarvis` / `codeforge` / `tesla` / `newton` / `dinosaur`（与 DB `assigned_team`、消费组身份一致） |
| **需求 ID** | 如 74 |
| **需求标题** | 如「弹球体验 0.1 关卡逻辑」 |
| **报告时间** | 年月日 时:分 (UTC+8) |
| **报告人** | 团队负责人或指定成员 |

---

## 2. 完成情况摘要

| 项目 | 内容 |
|------|------|
| **完成的需求** | 需求 ID + 标题（若本报告仅覆盖部分任务，可写「需求 ID + 本报告对应任务范围」） |
| **完成的任务列表** | 任务 1、任务 2、任务 3 …（任务 ID 或可读编码 + 标题） |

---

## 3. 任务明细（按任务填写）

对**每个已完成任务**填写下表（可复制多份）。与 DB 字段一致：**status**、**executor**、**risk**、**blocker**、**next_step_task_id**；以及 **est_tokens_total**、**prompt_rounds**（粗略 LLM 用量，见 `docs/REQUIREMENTS.md` §3.4，可通过 **`cli project record-task-usage`** / **`skills.record_task_usage`** 或 **report-status** 的 **tasks[]** 同步）。

| 字段 | 填写说明 |
|------|----------|
| **任务 ID / `code`** | 数字 id 与 API **`code`**（`P…-REQ…-TASK…`，见 `docs/REQUIREMENTS.md` §2.0） |
| **任务标题** | 简短标题 |
| **状态 (status)** | todo / in_progress / blocked / done |
| **具体完成队员 (executor)** | 负责该任务的成员（agent/角色名） |
| **输出说明** | 代码路径、**`work/<current_agent>/<timestamp>-<worktype>/`** 下证据与日志、配置变更等；若有测试用例一并列出路径或名称 |
| **代码行数** | 本任务新增/修改代码行数（可选：按语言或文件统计） |
| **测试用例** | 本任务关联的测试用例路径或名称（若有） |
| **风险 (risk)** | 本任务相关风险简述（会写入 DB） |
| **阻塞 (blocker)** | 阻塞原因简述（会写入 DB；若需先做其他任务，见下一项） |
| **下一步任务 (next_step_task_id)** | 若当前任务 blocked，先完成的任务 ID（如 Bug 修复任务），完成后可恢复本任务 |
| **估算 token 累计 (est_tokens_total)** | 本任务关联 LLM 调用的**粗略** token 估计（整数；非计费精度；与 DB 一致） |
| **prompt 次数 (prompt_rounds)** | 本任务上模型调用 / 回合**约数**（整数） |
| **备注** | 其他依赖、遗留项等 |

**示例（单任务）**：

| 字段 | 内容 |
|------|------|
| 任务 ID / code | `TASK3-…` 或完整 `P1-…-REQ1-…-TASK3-…` |
| 任务标题 | 实现关卡碰撞检测 |
| 状态 | done |
| 具体完成队员 | dev_member_1 |
| 输出说明 | `game/src/collision.py`，单元测试 `tests/test_collision.py` |
| 代码行数 | +120 行 Python |
| 测试用例 | test_collision.py（3 条用例） |
| 风险 | 无 |
| 阻塞 | 无 |
| 下一步任务 | — |
| 估算 token 累计 | 例：≈12000（说明统计口径：如「主代理+一次子 agent」） |
| prompt 次数 | 例：8 |
| 备注 | 无 |

---

## 4. 汇总（可选）

| 项目 | 数值/说明 |
|------|-----------|
| **总代码行数** | 本需求本次完成合计 |
| **总测试用例数** | 本需求本次新增/修改用例数 |
| **LLM 用量（任务合计，可选）** | 各任务 **est_tokens_total** / **prompt_rounds** 汇总或区间说明 |
| **遗留项 / 风险** | 若有 |

---

## 5. 上报方式

- **report-status**：payload 中 **tasks[]** 每项带 **id, status, executor, risk, blocker, next_step_task_id** 会**同步到 DB**；可同时带 analysis_notes、assignment_notes、development_notes 进入报告。  
- **CLI**：`python3 -m cli project report-status` / `report-task-detail` / `list-tasks` / `update-task`（`openclaw-knowledge/cli/README.md`）。  
- **Skill**（`OPENCLAW_DEVELOPMENT_FLOW.yaml`）：**`develop_requirement`**（开发执行闭环）；**`report_team_status`**（周期状态，常与 report-status 对齐）。  
- **cli project record-task-usage** / **`python3 -m skills.record_task_usage`**：将本任务的 **est_tokens_total**、**prompt_rounds** 写入 DB（增量 `--add-*` 或绝对 `--set-*`）。  
- **cli project report-task-detail**：`detail_type: "development"`，`content` 为本文报告正文或结构化 JSON；需求分析/拆解用 `detail_type: "analysis"`，任务分配用 `detail_type: "assignment"`。  
- 完整报告可同时写入团队工作空间或文档库，链接在 status-report 中提供。  
- Hera 可通过 **cli project list-tasks**、**update-task** 查看与更新任务（含 next_step_task_id、risk、blocker）。

**关单前自检**：**work/** 产物目录已建且路径已写入报告或 **stream:results**；**API** 任务/需求状态已更新；本阶段 **Redis** 进度与 **heartbeat** 已发。

---

*开发任务报告（全团队可用）- OpenClaw Communication System*
