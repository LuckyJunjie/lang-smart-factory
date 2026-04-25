# Definition of Done (DoD) — Smart Factory & OpenClaw

**版本:** 2.1  
**更新日期:** 2026-04-08  
**适用范围:** 在 Smart Factory / OpenClaw 流程下交付的**全部项目类型**（`projects.type`：`game`、`app`、`finance`、`tool`、`research`），含**开发**与**测试**角色。  
**对齐:** [docs/HIGH_REQUIREMENTS.md](../../docs/HIGH_REQUIREMENTS.md)（Harness I/O、验证层级、DB/Redis）；[DEVELOPMENT_FLOW.md](./DEVELOPMENT_FLOW.md)（`work/<agent>/`、**模式 A** Redis/API **或** **模式 B** 团队独立、[OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md)、推送远端）；实体分层编码 [docs/REQUIREMENTS.md](../../docs/REQUIREMENTS.md) §2.0（`P…-REQ…-TASK…-TC…`，报告与 `work/` 命名建议包含 **id** 或 **`code`** 段以便追溯）。

---

## 1. Harness 对齐（所有自动化步骤）

凡 Skill、CLI、心跳、飞书任务，均应能以机器可读方式说明**输入/输出/验证**（与 HIGH_REQUIREMENTS 「Harness principles」一致）：

| 项 | 要求 |
|----|------|
| **Preconditions** | 仓库路径、代理身份（`USER.md` / `AGENT.md`）；**模式 A**：`SMART_FACTORY_API`、`REDIS_URI`（多机）；**模式 B**：二者可选（台账/本地） |
| **Input** | 显式路径、CLI 参数或 API JSON；禁止无命名的「最新文件」 |
| **Output** | **stdout**：JSON（skills/CLI）；**API**：见 [docs/REQUIREMENTS.md](../../docs/REQUIREMENTS.md)；**Artifacts**：见下文 §3–§4 |
| **Exit / status** | 进程退出码 0；API HTTP 语义正确 |
| **Side effects** | 可列举：DB、Redis、飞书、写盘 |
| **Verification** | `GET` 资源、测试日志无失败断言、报告文件存在等 |

---

## 2. 全类型通用完成标准（开发 + 测试共同底线）

完成一项需求/任务闭环前，须同时满足：

### 2.1 实现质量
- [ ] 功能或验证目标已达成，**无已知阻塞性缺陷**（若已知须已登记为 `type=bug` 或 blocker）
- [ ] **无编译/构建失败**；运行时无未处理崩溃（语言/平台以项目为准）
- [ ] 依赖与配置可复现（README、[docs/TOOLCHAIN.md](../docs/TOOLCHAIN.md) 环境基线、根目录 `docs/TOOLCHAIN.md` 或任务说明中有记录）

### 2.2 测试与验证（按项目裁剪，但须声明范围）
- [ ] **单元/组件测试**：对业务逻辑、核心模块适用则必须通过（无测试库的项目须在 `work/` 中留**手工验证清单**与结果）
- [ ] **集成或 E2E**：对 `app` / `api` 类至少覆盖主路径；对 `game` 含 Godot headless/场景或项目规定的 harness（参见 `godot-task` / 流水线）
- [ ] **回归**：改动波及公共契约时，相关用例已更新并通过  
- [ ] **0.1–0.5 级快速验收**：至少一次可演示的冒烟或通过项目约定的最小检查清单

### 2.3 Git 与远端
- [ ] 变更已 **commit**；分支命名符合团队规范（`feature/`、`fix/` 等）
- [ ] 已 **merge** 到团队约定主线（常为 `main` / `master`，以 `repo_default_branch` 为准）
- [ ] 已 **push** 到项目在 Smart Factory 登记的 **`repo_url`** 远端；PR/MR 与 `repo_head_commit` / `repo_last_sync_at` 可通过 [REQUIREMENTS](../../docs/REQUIREMENTS.md) **PATCH project** 更新登记

### 2.4 Smart Factory / Redis / 报告（不以本地随意 Markdown 为准）
- [ ] **需求/任务状态**、进度与阻塞已在 **API** 中体现（`PATCH` requirements/tasks 或 `cli project` 等价）
- [ ] **跨团队事件**：**优先** `smartfactory:stream:results`；**心跳**按 `HEARTBEAT.md` / [REDIS_COLLABORATION](../../docs/REDIS_COLLABORATION.md)
- [ ] **任务级 LLM 用量（可选但推荐）**：对主要使用模型的任务，通过 **`record-task-usage`** / **report-status** 写入 **`est_tokens_total`**、**prompt_rounds`**（粗略即可，见 [REQUIREMENTS.md](../../docs/REQUIREMENTS.md) §3.4）
- [ ] **开发**完成提交 [开发任务报告模板](./report/DEVELOPMENT_TASK_REPORT_TEMPLATE.md)；**测试**完成提交 [测试任务报告模板](./report/TEST_TASK_REPORT_TEMPLATE.md)（或合并进 status-report 且字段等价）
- [ ] **不向已弃用的独立游戏状态 Markdown 写权威状态**；以 DB 与上述报告为准

**以上 2.1–2.4 全部勾选，才视为满足本 DoD 的「通用条」。**

---

## 3. 开发侧产出物标准（Develop）

以下产物落在 **当前开发项目根**（与 `repo_url` 检出根一致）的 **`work/<current_agent>/`** 下（见 [DEVELOPMENT_FLOW.md](./DEVELOPMENT_FLOW.md)）；必要时同时在 API **task-detail** / **requirement** 中留指针。

| 产物 | 内容 | 何时必须 |
|------|------|----------|
| **实现说明** | 改了什么、如何验证、已知限制 | 每个有代码交付的需求 |
| **设计/决策摘录** | 与 HIGH_REQUIREMENTS §3.2–§3.3 对齐；可链到 `report-task-detail` | 架构或接口变更时 |
| **构建与测试结果摘要** | 命令、日志路径或 CI 链接；**无 `FAIL` / `ASSERT FAIL`** | 每次合并前 |
| **DB 测试用例引用** | 对绑定需求已创建/更新的 `test_cases`（层：unit / component / integration / screenshot / console / system） | V 模型要求时（HIGH_REQUIREMENTS §3.3） |

**按项目类型追加：**

| `projects.type` | 开发 DoD 追加 |
|-----------------|---------------|
| **game** | 场景/资源变更可 headless 导入与约定场景跑通；重大玩法须有可复现步骤说明 |
| **app** | API 契约或 UI 关键路径有自动化或签字的手工清单；安全敏感改动须注明审阅 |
| **finance** | 计算/合规逻辑有双检或审计轨迹说明 |
| **tool** | CLI/库有 `--help` 或文档片段示例；破坏性变更有迁移说明 |
| **research** | 假设、实验步骤、结论与复现包（数据/脚本路径） |

---

## 4. 测试侧产出物标准（Test / QA）

测试主责团队（Tesla / Newton）在领取 **待测（developed）** 需求时，除 §2 通用条外须交付下表。

> **开发分配**：若同一团队当前处理的是 **new / fix / 工具与自动化** 等开发类需求，则适用 **§3 开发侧产出物标准**（与 jarvis/codeforge/dinosaur 同等），不以仅「测试侧」表格为完成条件。

| 产物 | 内容 | 验证 |
|------|------|------|
| **测试任务报告** | 使用 [TEST_TASK_REPORT_TEMPLATE.md](./report/TEST_TASK_REPORT_TEMPLATE.md) | 与 requirement id 关联 |
| **用例与执行结果** | DB **`test_cases`** 或等价清单：**planned → passed/failed/blocked** 与 `result_notes` | `GET /api/requirements/<id>/test-cases` 可查 |
| **缺陷与改进** | **Bug** → `POST /api/requirements` `type=bug`；**体验改进** → `type=enhancement` | 新建需求已在报告与 `stream:results` 中引用 |
| **证据** | 截图路径、录屏、控制台日志、Godot 测试输出等，放 **`work/<agent>/`** 并写进报告 | Manager 可按路径复检 |

**按类型追加：**

| 类型 | 测试 DoD 追加 |
|------|----------------|
| **game** | 覆盖 HIGH_REQUIREMENTS §5.5：组件级 +**截图/视觉**（若项目适用）；关键关卡可玩性抽检 |
| **app** | 多端/多浏览器矩阵在任务范围内声明；API 契约测试或 Postman/脚本记录 |
| **finance / tool / research** | 以任务 acceptance_criteria 为准，**等同严格**：须逐条勾选并留证据路径 |

---

## 5. 验证层级（与 HIGH_REQUIREMENTS §5.5 一致）

1. **设计验证**：独立验证需求或同行评审结论写入 DB / `work/`；阻塞项转为 bug 或 blocker。  
2. **编码验证**：要求的自动化测试**全部通过**；Harness stdout 规则（如 Godot）无失败断言。  
3. **测试验证**：跨团队测试报告 + test_cases 状态；失败则 bug / 阻塞流，不得伪「完成」。

---

## 6. Bug 修复（通用 Git 流程）

```text
git checkout -b fix/<short-name>
# 修改、测试、更新 work/<agent>/ 与报告
git add . && git commit -m "fix: <scope> <summary>"
git push -u origin fix/<short-name>
# 合并至主线（PR 或直接 merge，以团队规范为准）
git checkout <mainline> && git merge fix/<short-name> && git push origin <mainline>
```

**模式 A**：在 Smart Factory 中关联原需求/Bug、更新任务状态并 **Redis/API** 上报。**模式 B**：可选 API 台账；闭环以 **push + 飞书汇报 Master Jay** 为主（与 [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) 一致）。

---

## 7. 验收检查清单（交付前自扫）

- [ ] 代码在约定主线且远端可见？  
- [ ] §3 / §4 要求的最小产物已在 `work/<agent>/` 或 API 可追踪？  
- [ ] 测试与验证范围已写明，且无未解释失败？  
- [ ] **DEVELOPMENT_FLOW**：已 **push**？**模式 A** 下已 **PATCH**/`report-status`（及 Redis 结果）关闭循环？**模式 B** 下领导验收与飞书汇报已完成（可选 PATCH）？  
- [ ] 仍开放的 Bug 均已登记，未「静默延期」？

---

## 8. 相关模板与文档

| 文档 | 用途 |
|------|------|
| [DEVELOPMENT_TASK_REPORT_TEMPLATE.md](./report/DEVELOPMENT_TASK_REPORT_TEMPLATE.md) | 开发交付报告 |
| [TEST_TASK_REPORT_TEMPLATE.md](./report/TEST_TASK_REPORT_TEMPLATE.md) | 测试交付报告 |
| [TEAM_STATUS_REPORT_TEMPLATE.md](./report/TEAM_STATUS_REPORT_TEMPLATE.md) | 团队周期状态 |
| [docs/HIGH_REQUIREMENTS.md](../../docs/HIGH_REQUIREMENTS.md) | 产品与 Harness 总纲 |
| [docs/REQUIREMENTS.md](../../docs/REQUIREMENTS.md) | HTTP API / test_cases |

---

*智慧工厂 — 全类型开发与测试 DoD*
