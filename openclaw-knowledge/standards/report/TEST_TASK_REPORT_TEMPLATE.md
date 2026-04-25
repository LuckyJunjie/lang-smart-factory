# 测试任务报告模版

> **测试主责团队**（如 Tesla、Newton，见 `docs/ORGANIZATION.md`）在**测试完成时**按此模版填写并随 **report-status** 上报，供 Hera/Vanguard 汇总与飞书展示；如本周期包含玩家体验改进点，也可在「结论与建议」中补充。  
> **与 DB 对齐**：任务可含 **risk**、**blocker**、**next_step_task_id**（若测试阻塞需先修 Bug，可填 Bug 任务 id）；通过 **report-status** 的 tasks[] 同步到 DB，或 **report-task-detail** 提交测试细节。  
> **CLI**：`python3 -m cli project …`（`openclaw-knowledge` 在 `PYTHONPATH`），见 `openclaw-knowledge/cli/README.md`。**Skill**：`test_requirement`、`report_team_status`（`OPENCLAW_DEVELOPMENT_FLOW.yaml`）。

---

## 0. 工作产物路径、API 状态、Redis 与周期汇报（必读）

与 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md)、[DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md)、[REDIS_COLLABORATION.md](../../../docs/REDIS_COLLABORATION.md) 一致：

| 要求 | 说明 |
|------|------|
| **工作产物目录** | **`<project_repo_root>/work/<current_agent>/<timestamp>-<worktype>/`**（`repo_url` 检出根；**worktype** 可用 `test`、`regression`、`screenshot` 等）。截图、录屏索引、Godot/控制台日志、临时用例脚本等集中落此目录；本报告中用例与证据路径应对应到此树下。 |
| **任务/需求状态（API）** | 通过 **`PATCH /api/tasks/<id>`**、**`PATCH /api/requirements/<id>`** 与 **`cli project report-status`**（**tasks[]** 带 **id**）把测试进度、阻塞、**next_step_task_id**（如先修 Bug）写入 DB。 |
| **Redis（优先）** | **`XADD smartfactory:stream:results`** 上报测试进度/结论摘要；**`PUBLISH smartfactory:agent:heartbeat`**（建议 **≤15 分钟**）；发现的阻塞走 **`task:blocker`** / **`stream:blockers`**。 |
| **周期汇报** | **30 分钟–1 小时** **`report-status`**（**machine_info** + **tasks[]**）及/或 **`stream:results`**，保持机器与任务状态对 Hera/Vanguard 可见，勿仅提交本终次测试报告。 |

---

## 1. 基本信息

| 字段 | 填写说明 |
|------|----------|
| **团队** | `tesla` / `newton`（或与 DB `assigned_team` 一致的测试主责团队 id） |
| **需求 ID** | 被测试的需求 ID |
| **需求标题** | 被测试的需求标题 |
| **报告时间** | 年月日 时:分 (UTC+8) |
| **报告人** | 测试负责人或指定成员 |

---

## 2. 测试范围

| 项目 | 内容 |
|------|------|
| **测试对象** | 需求 ID + 标题，及版本/构建标识（若有） |
| **测试类型** | 功能测试 / 回归测试 / 冒烟测试 / 其他 |
| **测试环境** | 如设备、OS、依赖版本等（简要） |

---

## 3. 测试用例列表

列出本轮执行的测试用例（名称或 ID + 简要说明）。

| 序号 | 测试用例 ID / 名称 | 用例说明（一句话） |
|------|--------------------|--------------------|
| 1 | TC-001 | 关卡加载与初始化 |
| 2 | TC-002 | 小球与挡板碰撞 |
| 3 | TC-003 | 计分与生命值 |
| … | … | … |

---

## 4. 测试执行结果

| 序号 | 测试用例 | 执行结果 | 备注 |
|------|----------|----------|------|
| 1 | TC-001 | 通过 / 失败 | 若失败：简述原因或见 Bug ID |
| 2 | TC-002 | 通过 | — |
| 3 | TC-003 | 失败 | 已报 Bug #85 |
| … | … | … | … |

**汇总**：

| 项目 | 数值 |
|------|------|
| **执行总数** |  |
| **通过数** |  |
| **失败数** |  |
| **阻塞/跳过** | 若有，简要说明原因 |

---

## 5. 所报 Bug（若有）

测试过程中发现并已提交的 Bug 需求（任选其一）：**`python3 -m cli project create-requirement --title "…" --type bug`**（可选 `--description` / `--project-id`）；**Skill** `python3 -m skills.test_requirement --create-bug --title "…"`；或 **`POST /api/requirements`** 且 `type=bug`（见 `docs/REQUIREMENTS.md`）。

| Bug 需求 ID | 标题 / 简述 | 关联用例 | 严重程度（可选） |
|-------------|-------------|----------|------------------|
| 86 | 计分在第二次碰撞后归零 | TC-003 | 高 |
| … | … | … | … |

若无 Bug，填「无」。

---

## 6. 结论与建议

| 项目 | 内容 |
|------|------|
| **测试结论** | 通过 / 不通过 / 有条件通过（说明条件） |
| **建议** | 如：需修复 #86 后回归；可发布等 |

---

## 7. 上报方式

- **report-status**：payload 中 **tasks[]** 带 **id, status, executor, risk, blocker, next_step_task_id** 会同步到 DB；可带 analysis_notes、assignment_notes、development_notes。  
- **cli project report-status**（或 **Skill** `test_requirement` / **`report_team_status`**）：上报测试结果与报告摘要。  
- **cli project report-task-detail**：`detail_type: "development"`（测试结论），`content` 为本文报告正文或结构化 JSON。  
- 完整报告可同时写入团队工作空间或文档库，链接在 status-report 中提供。  
- 发现的 Bug 创建为需求（type=bug）后，可将该 Bug 任务 id 填为相关任务的 **next_step_task_id**，便于先修 Bug 再回归。

**关单前自检**：**`work/<current_agent>/<timestamp>-<worktype>/`** 下测试证据齐全；**API** 与 **Redis**（**stream:results** + **heartbeat**）与结论一致；周期 **report-status** 已覆盖测试中机器/任务状态。

---

*测试任务报告 - OpenClaw Communication System*
