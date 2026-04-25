# OpenClaw 团队独立工作流（单设备 / 单团队闭环）

> 版本: 1.0 | 更新日期: 2026-04-08  
> **并列文档**：与 [OPENCLAW_COMMUNICATION_SYSTEM.md](./OPENCLAW_COMMUNICATION_SYSTEM.md)（**多设备 Vanguard 协调 + Redis/API**）**同级**；二者**不矛盾**，按任务来源与组织方式**二选一**或**并存**（不同项目/不同阶段可用不同模式）。

---

## 1. 概述

**独立工作流**指：**Master Jay** 或 **Winnie Chen**（组织中亦见 [ORGANIZATION.md](../../docs/ORGANIZATION.md) 的 **Winnie (My Lord)**）将需求**直接**下达给某一团队的 **Team Manager**（resident 主智能体，如 `jarvis`、`codeforge`、`tesla`、`newton`、`dinosaur`）。该团队在本机（或本团队环境）内**自行**完成分析、开发、子智能体分工、测试、评审与推送，**不依赖**跨物理设备的 **Redis 任务派发**与**多机 API 协调**。

| 维度 | Vanguard 协调模式（通信系统文档） | 团队独立模式（本文档） |
|------|-----------------------------------|-------------------------|
| 需求入口 | Vanguard/Hera + DB 分配 + Redis 事件 | 领导直接 → Team Manager |
| 跨设备协作 | 必须：`REDIS_URI`、`SMART_FACTORY_API` 等 | **不要求** Redis/API 作为机间协调主路径 |
| 团队边界 | 多团队按流消费任务 | **同一团队内** spawn 子代理闭环 |
| DoD / 报告模板 | [DEFINITION_OF_DONE.md](../standards/DEFINITION_OF_DONE.md)、`standards/report/` | **相同** |
| CLI / Skills | `cli dev` / `cli godot` / `cli test` / `develop_requirement` 等 | **相同**（可不调用依赖 DB 分配的步骤） |

**可选**：若仍希望将需求记入 Smart Factory DB（仅作台账、非机间派发），可在本机配置 `SMART_FACTORY_API` 使用 `cli project create-requirement` / `update-requirement`；**独立模式不强制** Redis 消费组与跨团队 `stream:tasks` 协议。

---

## 2. 角色与职责

- **领导**：Master Jay、Winnie Chen — 下达目标、优先级、验收口径；接收最终汇报。
- **Team Manager**：各团队 resident 主智能体（见 [OPENCLAW_DEVELOPMENT_FLOW.yaml](./OPENCLAW_DEVELOPMENT_FLOW.yaml) `teams` 与 `role_skill_policy`）— 接收需求、阅读项目文档、做差距分析、拆解工作、**spawn 预定义子代理**（与协作模式相同的 `named_spawn_agents` / `optional_spawn_specialists`）、整合结果、组织测试与评审、**推送远端**并汇报。
- **子代理（Sub-agents）**：由 Team Manager 按任务类型启动；执行具体开发、修复、测试、UX 等；产物写入本项目仓库约定目录（见 §5）。

组织与设备表仍以 **[ORGANIZATION.md](../../docs/ORGANIZATION.md)** 为准。

---

## 3. 流程（Team Manager 执行顺序）

1. **接收直接需求**  
   从飞书/会话/书面 brief 明确：目标范围、项目仓库、`docs/` 或产品需求位置、截止时间、是否需同步写入 Smart Factory DB。

2. **读项目需求与现状**  
   在 **目标项目仓库** 内阅读 `docs/`（如 `HIGH_REQUIREMENTS.md`、`REQUIREMENTS` 相关）、设计文档、CHANGELOG；对照代码与已有功能做 **gap 列表**（未实现 / 部分实现 / 需修复）。

3. **规划与 spawn**  
   按 [OPENCLAW_DEVELOPMENT_FLOW.yaml](./OPENCLAW_DEVELOPMENT_FLOW.yaml) 中本团队的 `role_skill_policy`（含 Godot 的 `godogen` / `godot-task` 策略）选择 **预定义子代理类型**，通过 `sessions_spawn`（或等价机制）启动执行体；分配子任务（可维护团队内 checklist，**无需** Redis `stream:tasks`）。

4. **开发 — 测试 — 评审**  
   - 开发：与协作模式相同技能路径（如 `develop_requirement`、本地 `cli dev` / `cli godot`）。  
   - 测试：团队内执行 `cli test` / `cli godot run-tests` 等；主责测试的团队沿用 `test_requirement` 心智。  
   - **评审/验收**：Team Manager 确认满足 [DEFINITION_OF_DONE.md](../standards/DEFINITION_OF_DONE.md)（代码可运行、测试与 0.1–0.5 验证、Git 流程、文档更新等）。

5. **产物与记录**  
   凡设计笔记、输入材料、输出日志、测试报告、截图索引等，写入 **项目仓库**（见 §5）。

6. **Git 与远端**  
   `feature/*` 或 `fix/*` → 合并策略与团队约定一致 → **push** 到项目登记远端（与 DoD 一致）。

7. **向 Master Jay 汇报**  
   使用与协作模式相同的报告结构（见 `openclaw-knowledge/standards/report/`，如开发/测试任务报告模板）；通过飞书群「**福渊研发部**」提交**最终结果、变更摘要、`work/` 证据路径、commit/PR 引用**。

---

## 4. 与协作模式共用的规范

- **DoD**：[DEFINITION_OF_DONE.md](../standards/DEFINITION_OF_DONE.md)  
- **报告模板**：[standards/report/README.md](../standards/report/README.md)  
- **环境与工具**：[openclaw-knowledge/docs/TOOLCHAIN.md](../docs/TOOLCHAIN.md)、根目录 [docs/TOOLCHAIN.md](../../docs/TOOLCHAIN.md)  
- **结构化机读流程**：[OPENCLAW_DEVELOPMENT_FLOW.yaml](./OPENCLAW_DEVELOPMENT_FLOW.yaml) 中的 `team_standalone_cycle` 与 `execution_modes.team_standalone`

---

## 5. 工作产物目录（项目仓库内）

根路径与协作模式一致：`<project_repo_root>/work/<agent>/`（`<agent>` 为执行该步骤的代理 id，与 workspace 目录名一致）。

独立模式建议**显式**使用子目录区分输入/输出，便于审计与汇报：

```text
<project_repo_root>/work/<agent>/input/    # 领导 brief 摘要、引用的需求片段、分析中间稿
<project_repo_root>/work/<agent>/output/   # 执行日志、测试报告、截图索引、交付说明
```

团队可约定：仅 Team Manager 写 `input/` 级摘要，子代理主要写 `output/`；或直接沿用扁平的 `work/<agent>/`（与 [DEVELOPMENT_FLOW.md](../standards/DEVELOPMENT_FLOW.md) 一致）。

---

## 6. 何时选用何种模式

- **选 Vanguard 协调**：多设备并行、跨团队依赖、需 Hera 阻塞决策、统一从 DB/Redis 接单。  
- **选团队独立**：单团队即可闭环、领导直派、无跨机任务队列诉求、希望减少 Redis/API 运维依赖。

切换模式时，在 brief 或项目 README 中**写明当前模式**，避免代理误用 Redis 消费流程。

---

## 8. 独立团队开发模式 — Sub-Agent 人员预定义与持续饱和运作

### 8.1 核心理念

**OpenClaw 的 Sub-Agent 不是随机生成的临时工，而是预定义在配置中的团队成员。**

每个团队（Jarvis / CodeForge / Tesla / Newton / dinosaur）都有**固定的 sub-agent 花名册**，每个 sub-agent 拥有独立的 workspace（含 SOUL.md、IDENTITY.md、USER.md、TOOLS.md 等身份文件），类似于一个真实开发团队的正式成员。这些 sub-agent **必须由 Team Manager 显式 spawn 后执行任务**，而不是临时起意的随机智能体。

### 8.2 Sub-Agent 预定义特性

| 特性 | 说明 |
|------|------|
| **命名固定** | 每个 sub-agent 有固定代号（如 `athena`、`pangu`、`model_s`），不能随意创建 |
| **Workspace 专属** | 每个 sub-agent 有独立工作区路径 `workspace/<team>/<agent>/`，含身份文件 |
| **技能预定义** | 每个 sub-agent 按其代号有对应的技能定位（如 `mac-developer`、`game-tester`） |
| **血缘关系** | 由 Team Manager spawn 并管理，任务完成后可销毁或回收 |

### 8.3 团队 Sub-Agent 花名册（当前配置）

| 团队 | Sub-Agents（预定义） | 技能定位 |
|------|---------------------|----------|
| **Jarvis** | `athena`、`cerberus`、`apollo`、`hermes`、`chiron` | 开发、测试、渲染引擎、调试等 |
| **CodeForge** | `pangu`、`nuwa`、`luban`、`yu`、`shennong` | Windows 开发、工具、修复等 |
| **Tesla** | `model_s`、`model_3`、`model_x`、`model_y`、`cybertruck` | 测试与玩家体验（主责）、开发协作 |
| **Newton** | `einstein`、`curie`、`galileo`、`hawking`、`darwin` | 测试与体验（主责）、开发协作 |
| **dinosaur** | `trex`、`raptor`、`ptero`、`bronto`（预留） | 开发、渲染、NAS 服务 |

> **注意**：这些 sub-agent **不常驻**，必须由 Team Manager 显式 `sessions_spawn` 后才会激活执行任务。

### 8.4 持续饱和运作原则

当任务队列中有**足够数量的任务**时，应让所有预定义的 sub-agent **始终保持 1-2 个任务持续工作**，实现团队产能最大化。

#### 饱和运作规则

```
任务数量 ≥ 团队 Sub-Agent 数量 × 1.5 → 启动全员饱和模式
每人维持任务数: 1-2 个（不堆积 >2，不空闲 =0）
```

#### 操作步骤

1. **评估任务量**：Team Manager 接收需求后，先清点任务数量
2. **Spawn 预定义 Sub-Agents**：按花名册依次 spawn，每个分配 1 个初始任务
3. **动态补充**：当某个 sub-agent 完成任务后，立即分配下一个任务，保持 1-2 个在跑
4. **溢出处理**：任务数 > sub-agent 上限时，按优先级排队，等待空闲 slot
5. **空闲预警**：若某 sub-agent 长时间（>30 min）无任务，触发重新分配检查

#### 伪代码示例

```python
# Team Manager 饱和调度伪代码
sub_agents = ["athena", "cerberus", "apollo", "hermes", "chiron"]
active_tasks = {}  # agent -> current_task

def assign_task(agent, task):
    if len(active_tasks.get(agent, [])) >= 2:
        return False  # 该 agent 已饱和
    if agent not in active_tasks:
        active_tasks[agent] = []
    active_tasks[agent].append(task)
    spawn(agent, task)
    return True

def check_saturation():
    idle_agents = [a for a in sub_agents if len(active_tasks.get(a, [])) < 1]
    if len(task_queue) >= len(sub_agents) * 1.5 and idle_agents:
        for agent in idle_agents:
            if task_queue:
                assign_task(agent, task_queue.pop(0))
```

### 8.5 与传统 Scrum 的区别

| 维度 | 传统 Scrum | OpenClaw 独立团队模式 |
|------|-----------|----------------------|
| **人员** | 真实人类，固定 sprint 周期 | 预定义 sub-agent，持续动态调度 |
| **任务分配** | Sprint Planning 批量分配 | Team Manager 实时 spawn + 动态补充 |
| **WIP 限制** | Kanban 板限制 | 每个 agent 1-2 个任务上限 |
| **上下文切换** | 人类换任务成本高 | sub-agent 可快速切换（workspace 继承） |
| **并行度** | 受限于人类并行能力 | 可同时让 5+ 个 sub-agent 并行工作 |
| **启动成本** | Sprint 启动耗时 | spawn 一个 sub-agent 几乎即时 |

### 8.6 关键约束

- **禁止随机创建 sub-agent**：只使用预定义的团队花名册中的成员
- **禁止空转**：当有排队任务时，不允许 sub-agent 处于空闲状态
- **上限保护**：单个 sub-agent 不超过 2 个并发任务（避免上下文稀释）
- **Team Manager 负责制**：饱和调度策略由 Team Manager 统一执行

---

## 9. 参考链接

- [OPENCLAW_COMMUNICATION_SYSTEM.md](./OPENCLAW_COMMUNICATION_SYSTEM.md) — 多设备协作与 Redis/API 映射  
- [OPENCLAW_DEVELOPMENT_FLOW.yaml](./OPENCLAW_DEVELOPMENT_FLOW.yaml) — 角色、技能、YAML 工作流（含 `team_standalone_cycle`）  
- [DEVELOPMENT_FLOW.md](../standards/DEVELOPMENT_FLOW.md) — 标准流程总览（双模式）  
- [SMART_FACTORY_CONTEXT.md](../organization/SMART_FACTORY_CONTEXT.md) — 代理必读上下文  

---

*Smart Factory — OpenClaw 团队独立闭环工作流*
