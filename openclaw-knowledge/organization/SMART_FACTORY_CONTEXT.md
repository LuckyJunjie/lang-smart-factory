# Smart Factory - Agent Context

> 智慧工厂知识库：所有 OpenClaw 代理应了解的工作方式与规范。
> 路径: `./` (项目根)

---

## 📋 必读文档

| 文档 | 说明 |
|------|------|
| [docs/README.md](../docs/README.md) | 系统概述、架构、API |
| [archived/game/README.md](../../archived/game/README.md) | 归档游戏文档：历史参考；活跃流程见 DEVELOPMENT_FLOW |
| [docs/ORGANIZATION.md](../docs/ORGANIZATION.md) | 组织架构、团队、角色 |
| [standards/DEFINITION_OF_DONE.md](../standards/DEFINITION_OF_DONE.md) | 全类型开发与测试完成标准 (DoD)，对齐 HIGH_REQUIREMENTS |
| [archived/game/development-pipeline.md](../../archived/game/development-pipeline.md) | 归档 7 阶段流水线参考；当前遵循 DEVELOPMENT_FLOW |
| [docs/REQUIREMENTS.md](../docs/REQUIREMENTS.md) | HTTP API 规格（持久化；协作见 Redis；**§2.0** 分层 **`code`**：`P…-REQ…-TASK…-TC…`） |
| [docs/REDIS_COLLABORATION.md](../docs/REDIS_COLLABORATION.md) | Redis 协作架构与使用指南（**多设备 Vanguard 模式**） |
| [workflows/OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) | **团队独立闭环**：领导直派 Team Manager，无跨设备 Redis 协调 |
| [docs/TOOLCHAIN.md](../docs/TOOLCHAIN.md) | **OpenClaw 环境与版本安装基线**（Git、Godot 4.5.1、pytest…）；完整工具目录见根 [docs/TOOLCHAIN.md](../../docs/TOOLCHAIN.md) |
| [docs/GITHUB_NETWORK_AND_PUSH_RETRY.md](../docs/GITHUB_NETWORK_AND_PUSH_RETRY.md) | GitHub 网络与 push；**cron 5 分钟重试**（`scripts/git_push_retry_until_ok.sh`） |
| [docs/GODOT_SKILLS_AND_TESTING.md](../docs/GODOT_SKILLS_AND_TESTING.md) | **godogen** / **godot-task** 与游戏测试索引 |
| [cli/README.md](../cli/README.md) | Smart Factory CLI（代理用 CLI 替代 MCP） |
| [skills/README.md](../skills/README.md) | 高级技能（流程任务） |

*路径相对于 `./` 项目根。*

---

## ✅ Definition of Done (DoD) 要点

1. **代码实现**：功能完成、无编译/运行时错误
2. **测试验证**：单元测试、集成测试、0.1-0.5 验证通过
3. **Git 流程**：feature/fix 分支 → 合并 master → 推送远程
4. **文档更新**：相关文档、CHANGELOG 已更新

---

## 🔄 工作流

- **需求→发布**：飞书提交 → 需求创建 → 设计确认 → 任务拆分 → 开发/测试 → 集成验证 → 发布
- **每日**：晨间检查任务 → 开发执行 → 晚间日报

### 团队开发流程（两种等价模式）

- **A. Vanguard 协调模式**（多设备 + Redis）：详见 [workflows/OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)
  - **Vanguard** 基于事件发布任务：`PUBLISH smartfactory:task:dispatch` + `XADD smartfactory:stream:tasks`。
  - **开发主管（Jarvis / CodeForge / dinosaur）与测试主管（Tesla / Newton）** 从 `smartfactory:stream:tasks` 消费任务并执行；Tesla / Newton **主责测试**，**同时具备完整开发能力**（见 ORGANIZATION 能力模型与 `OPENCLAW_DEVELOPMENT_FLOW.yaml` 中 `role_skill_policy`）。
  - **执行结果**统一写入 `smartfactory:stream:results`。
  - **阻塞**统一写入 `smartfactory:task:blocker` / `smartfactory:stream:blockers`，由 Hera 实时处理。

- **B. 团队独立模式**（领导直派、单团队闭环）：详见 [workflows/OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md) 与 `OPENCLAW_DEVELOPMENT_FLOW.yaml` 的 `team_standalone_cycle`
  - **Master Jay / Winnie Chen** → **Team Manager**；读项目 `docs` 与代码做 gap；spawn 预定义子代理；**不依赖**跨设备 Redis/API 协调；DoD 与报告模板与模式 A **相同**；产物建议 `work/<agent>/input/`、`work/<agent>/output/`。

详见 [standards/DEVELOPMENT_FLOW.md](../standards/DEVELOPMENT_FLOW.md)

---

## 📊 汇报规范

- **汇报对象**：Master Jay, Winnie
- **渠道**：飞书群「福渊研发部」
- **格式**：任务名、状态、进度%、问题、下一步

---

## 🔧 Redis 与 Skills

- **Redis**：**模式 A** 统一使用 `smartfactory:*` 通道与队列（见通信系统文档）。**模式 B** 不以 Redis 为机间协调必选；本地 CLI/Skills 即可。
- **团队任务（模式 A）**：通过 `smartfactory:stream:tasks` 消费，不使用 API 轮询作为**跨团队**领取主路径
- **状态/结果（模式 A）**：通过 `smartfactory:stream:results` 上报
- **阻塞（模式 A）**：通过 `smartfactory:task:blocker` / `smartfactory:stream:blockers` 上报
- **CLI**：`cli project`、`cli comm`、`cli dev`、`cli godot`、`cli test`、`cli analysis`，见 [cli/README.md](../cli/README.md)。代理直接使用 CLI，无需 MCP 进程。
- **Skills**：`assign_tasks_to_teams`、`handle_blockage`、`generate_daily_report`、`develop_requirement`、`test_requirement`、`sync_game_plan`、`feishu_api_health_report` 等，见 [skills/README.md](../skills/README.md)。需求/任务操作建议用 **cli project** 或 API，不再使用 `factory-skill` CLI。
- **通信系统**：详见 [workflows/OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)

---

## 🖥️ 硬件集群

| 团队 | IP | 角色 |
|------|-----|------|
| Vanguard001 | 192.168.3.75 | 主控、汇总汇报飞书；**Smart Factory API + Redis 默认宿主**（他机 `SMART_FACTORY_API` / `REDIS_URI` 指向此 IP） |
| Hera | 192.168.3.75 | 项目管理经理（与 Vanguard001 同设备） |
| Jarvis | 192.168.3.79 | 开发 |
| CodeForge | 192.168.3.4 | 开发 |
| Newton | 192.168.3.82 | 测试与体验（主责）+ 开发（工具/自动化/fix/feature） |
| Tesla | 192.168.3.83 | 测试与玩家体验（主责）+ 开发（同上） |
| dinosaur | 待确认 | 开发/渲染/NAS 服务（未来） |

---

## 👥 Agent 花名册（协作与通信）

> Agent 间协作时查阅，用于知道「找谁做什么」。完整架构见 [ORGANIZATION.md](../docs/ORGANIZATION.md)

| 团队 | 主智能体（物理设备常驻） | 子智能体（按需 Spawn） | 宿主设备 | 工作区路径 |
|------|------------------------|---------------------|---------|------------|
| Vanguard001 | `vanguard001` | 历史子智能体：`penny`、`fuxi`、`hera(from-vanguard001)` | `192.168.3.75` | `workspace/vanguard001/` |
| Hera | `hera` | - | `192.168.3.75`（与 `vanguard001` 同设备） | `workspace/hera/` |
| Jarvis | `jarvis` | `athena`、`cerberus`、`apollo`、`hermes`、`chiron` | `192.168.3.79` | `workspace/jarvis/` |
| CodeForge | `codeforge` | `pangu`、`nuwa`、`luban`、`yu`、`shennong` | `192.168.3.4` | `workspace/codeforge/` |
| Newton | `newton` | （历史提交）`einstein`、`curie`、`galileo`、`hawking`、`darwin` | `192.168.3.82` | `workspace/newton/` |
| Tesla | `tesla` | （历史提交）`model_s`、`model_3`、`model_x`、`model_y`、`cybertruck` | `192.168.3.83` | `workspace/tesla/` |
| dinosaur | `dinosaur` | 预留（未来）：`trex`、`raptor`、`ptero`、`bronto` | 待确认 | `workspace/dinosaur/` |

---

### 专业智能体（按需 Spawn）

专业智能体（例如 `mac-developer`、`game-tester`、`risk-manager` 等）以 `sessions_spawn` 动态生成。  
它们可以拥有**预定义命名 workspace 与身份文件**（SOUL/IDENTITY/USER/CONTEXT/TOOLS）。当前团队子智能体清单见上方「Agent 花名册」。

注意：这些 sub-agent 默认不常驻，必须由对应 Team Main 明确 spawn 后执行任务。

---

*每个代理应根据自身角色深入学习相关文档。*
