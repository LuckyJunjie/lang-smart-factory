# 24 小时流程演练测试需求设计

> 版本: 1.1 | 更新日期: 2026-03-12  
> 目的：替代「24 小时机器状态报告」，用于验证任务分发、任务分析、团队内分配、结果汇总及**决策处理**流程。生产环境 **多机协作以 Redis 为主**（见 [docs/REDIS_COLLABORATION.md](../../docs/REDIS_COLLABORATION.md)）；本演练可用 **Skills / MCP / API** 模拟，但验收时应包含 **Redis 派发/消费** 或明确记为仅 API 降级演练。

---

## 1. 测试目标

| 维度 | 验证点 | MCP / Skill |
|------|--------|-------------|
| **任务分发** | Vanguard 分配需求 → 各团队获知并领取 | **Skill** `assign_tasks_to_teams`（须 **API assign + Redis 派发**）；团队**优先**消费 `stream:tasks`，降级：`get_team_assigned`、`take_requirement` / HTTP |
| **任务分析** | 架构师分析需求 → 拆解子任务 → 需求 step 进入 implement | analysis-mcp `extract_requirements` 等；API：`POST /api/requirements/<id>/auto-split` 或 `POST /api/tasks` |
| **团队内分发** | Scrum Master 查看任务列表 → 将任务分配给不同 executor | project-mcp `get_requirement`；API：`GET /api/requirements/<id>/tasks`、`PATCH /api/tasks/<id>` |
| **结果汇总** | 各团队完成各自需求 → **优先** `stream:results` → 可选 status-report 落库 → Vanguard 汇总 → 飞书 | **Skill** `generate_daily_report`；或 project-mcp `report_status`、comm-mcp `send_feishu_message` |
| **决策处理** | 「需决策」→ **优先** Redis blocker → Hera 决策 → `stream:results` / API | **Skill** `handle_blockage`；降级：project-mcp `report_blockage` 等 |

- **时长**：24 小时内完成一轮（可跨自然日）。
- **难度**：有真实产出，但不要求写复杂代码；以「检查 + 清单 + 决策记录」为主。
- **参与**：3 个开发团队（Jarvis, CodeForge, Newton）+ Tesla 团队（测试 + 玩家体验），各领 1 个需求；开发团队做开发与清单产出，Tesla 负责文档与通信流程检查，并以玩家视角补充体验改进建议（可转为 `type=enhancement`），充分发挥架构师、Scrum Master、多成员角色。

---

## 2. 总体设计：四团队并行「健康与改进清单」

**总目标**：在 24 小时内，每个团队产出一份**本团队负责领域的智慧工厂健康检查与改进建议清单**，并至少经历一次**需决策**流程；Vanguard 汇总 4 份产出后发飞书。

**4 个需求（一团队一需求）**：

| 需求标题 | 建议分配团队 | 产出物概要 |
|----------|--------------|------------|
| REQ-A: API 与需求模块健康检查清单 | Jarvis | 对 `/api/`、`/api/requirements`、`/api/tasks` 等做可用性检查，列出健康项与改进建议 |
| REQ-B: 测试与质量健康检查清单 | CodeForge | 测试环境、用例覆盖、质量门禁等检查项与改进建议 |
| REQ-C: 部署与机器状态健康检查清单 | Newton | 部署流程、机器/团队状态上报、在线判定等检查与改进建议 |
| REQ-D: 文档与通信流程健康检查清单 | Tesla | 文档完整性、飞书/状态上报/风险报告等流程检查与改进建议；测试/体验发现问题时创建 type=bug 或 type=enhancement 需求参与下一轮修复与实现（见 OPENCLAW 3.3） |

每个需求在 DB 中为独立 `requirement`，由 Vanguard 分别 `assign` 到对应团队，团队 `take` 后按标准流程：分析 → 拆任务 → Scrum Master 分配 → 执行 → 完成。

---

## 3. 任务结构示例（以 Jarvis / REQ-A 为例）

保证**多角色参与**且包含**至少一个决策点**。

| 序号 | 任务标题 | 建议角色 | 说明 |
|------|----------|----------|------|
| 1 | 分析需求并输出任务拆解方案 | athena（架构师） | 阅读需求，拆解为可执行任务，可调用 auto-split 或手动建 task |
| 2 | 分配任务给成员并平衡负载 | chiron（Scrum Master） | 查看 `GET /api/requirements/<id>/tasks`，为每任务设置 executor |
| 3 | 检查 API 发现与根端点 | hermes（DevOps） | 调用 `GET /api/`，记录可用端点列表与状态 |
| 4 | 检查 requirements/tasks 相关端点 | cerberus（测试） | 调用 GET/POST/PATCH 等，记录行为是否符合预期 |
| 5 | 整理清单格式与可读性 | apollo（美术/文档） | 将检查结果整理为「健康项 / 待改进项」清单 |
| 6 | 【决策】不一致处理与上报 | 任一执行人 | 若发现「实现与文档不一致」或「多方案可选」，记录选项、建议，并将任务标为 need_input 或通过 status-report 上报，团队/Vanguard 决策后更新任务并继续 |

其他三个需求（REQ-B/C/D）按同样模式设计：**架构师分析 + Scrum Master 分配 + 3～4 个执行任务 + 1 个「需决策」任务**。

---

## 4. 决策点设计（必测）

每个团队的需求中**至少包含 1 个会触发决策的任务**，用于验证：

1. **识别**：执行人发现「需要决策」的情况（例如：文档与 API 行为不一致、两种实现方案可选、依赖缺失等）。
2. **记录**：在任务描述或 status-report 中记录「问题简述、可选方案 A/B、建议」。
3. **状态**：将任务设为 `need_input`（或按现有 API 支持方式），或通过 `POST /api/teams/<team>/status-report` 在 payload 中说明阻塞原因。
4. **决策**：团队内部决策或 **`PUBLISH` blocker / `XADD stream:blockers`**（优先），降级 `POST /api/discussion/blockage`；Hera **消费阻塞流**或 `GET /api/discussion/blockages` 并 `PATCH` 决议。**依赖阻塞**时 Hera 可重新 assign（**+ Redis 再派发**）。决策结果记入任务/需求。
5. **继续**：任务从 `need_input` 恢复为 in_progress → done。

**可选决策场景示例**（各团队可自选或替换）：

- **Jarvis**：某 API 返回字段与 REQUIREMENTS.md 描述不一致 → 选项 A 改实现、选项 B 改文档，选一并记录。
- **CodeForge**：某测试环境缺失 → 选项 A 跳过该项并记入清单、选项 B 申请资源，选一并记录。
- **Newton**：机器状态上报频率与「40 分钟 active」定义冲突 → 建议统一口径并记录。
- **Tesla**：某文档过时 → 选项 A 仅记录在清单、选项 B 顺手更新文档，选一并记录。

---

## 5. 24 小时时间线（建议）

| 时段 | 动作 |
|------|------|
| T+0 | 在 DB 中创建 4 个需求（REQ-A/B/C/D），状态 `new`；Vanguard 对 4 个团队分别 `assign` |
| T+0～1h | 各团队：**优先** Redis `stream:tasks` 触发后 `take`；演练降级：project-mcp `get_team_assigned`、`take_requirement`；架构师拆解；Scrum Master 分配 executor |
| T+1h～22h | 执行；进度 **优先** `XADD stream:results`，辅以 `report_status` / status-report（落库）；决策点：**Redis blocker** 或 `report_blockage` / `handle_blockage` |
| T+22h～24h | 各团队完成所有任务，需求 `status=done`；Vanguard 运行 **Skill** `generate_daily_report`（或 `GET /api/teams/status-report/summary` + `POST /api/feishu/post`）发 24h 演练总结 |

「运行 24 小时」体现为：**从 assign 到汇总的整段时间在 24 小时内**；不要求 24 小时内每小时都有动作，但需在 24h 内完成一轮并汇总。

---

## 6. 验收标准（DoD）

- **任务分发**：4 个需求均被 assign 且被对应团队 take，assigned_agent 已填。
- **任务分析**：每个需求下至少有 4 个以上任务，且需求 step 曾进入 implement。
- **团队内分发**：每个任务均有 executor，且各团队成员负载相对均衡（无一人包揽全部）。
- **决策处理**：至少 2 个团队有任务曾处于 need_input 或通过 status-report 上报过「待决策」并留下决策记录。
- **结果汇总**：4 个需求均 status=done；Vanguard 已发飞书汇总（含 4 份清单摘要或链接）。

---

## 7. 与「24 小时机器状态报告」的对比

| 项目 | 原 24h 机器状态报告 | 本 24h 流程演练 |
|------|---------------------|-----------------|
| 团队协作 | 仅「每小时上报一次机器状态」，无任务拆解与角色分工 | 完整流程：领取 → 分析 → 拆任务 → 分配 → 执行 → 汇总 |
| 角色发挥 | 单一动作，无法区分架构师/Scrum Master/执行人 | 架构师分析、Scrum Master 分配、多成员执行 |
| 决策 | 无 | 明确「需决策」任务与 need_input/上报流程 |
| 产出 | 机器状态汇总 | 4 份健康与改进清单 + 决策记录 + 飞书总结 |
| 可观测性 | 仅 machine-status | status-report、tasks、requirements 全链路可查 |

---

## 8. 实施清单（创建需求时参考）

1. **写入数据库（推荐）**  
   - 运行脚本一次性创建项目、4 个需求及所有子任务（含建议 executor），并预置 assigned_team，符合 OPENCLAW 流程与 [REQUIREMENTS.md 2.0](../../docs/REQUIREMENTS.md) 编码约定：
   - `cd smart-factory && python3 openclaw-knowledge/scripts/seed_24h_workflow_requirements.py`
   - 需求/任务编码由 API 按 `{req_id:04d}-{project_slug}-{req_slug}-{progress}` / `-{task_id:04d}` 计算；DB 中需有 `plan_step_id`（本演练为 `24h`）。若已用脚本，可跳过步骤 2。

2. **或手动创建 4 个需求**（同一 project_id，如 smart-factory）  
   - 标题/描述按 REQ-A/B/C/D 填写，priority=P2，type=feature，status=new；随后需 Vanguard 分配。也可用 **Skill** `parse_requirement_doc` 从 PRD 提取并创建。

3. **Vanguard 分配**（若未在种子数据中预置 assigned_team）  
   - 运行 **Skill**：`python -m skills.assign_tasks_to_teams`（内部调用 project-mcp `assign_requirement`）；或直接 `POST /api/requirements/<id>/assign`，body `{"assigned_team": "jarvis"}`（依次 jarvis, codeforge, newton, tesla）。

4. **各团队**  
   - **优先** Redis 任务事件后领取；降级：`get_team_assigned` / HTTP。进度：**stream:results** 为主，按需 status-report。决策：Redis blocker 或 `report_blockage` / `handle_blockage`（§4）。

5. **Vanguard 汇总**  
   - 在 T+22h～24h 运行 **Skill**：`python -m skills.generate_daily_report`（内部拉取 status-report/summary 并 `send_feishu_message`）；或手动调用 status-report/summary 与 `POST /api/feishu/post`。

6. **Hera**  
   - **优先** 消费 **Redis 阻塞流**；运行 **Skill**：`python -m skills.handle_blockage`；降级：`GET /api/discussion/blockages`、`PATCH` 决议。

---

*24h 流程演练测试需求设计 - Smart Factory*
