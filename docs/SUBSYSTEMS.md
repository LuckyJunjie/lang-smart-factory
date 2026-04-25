# 智慧工厂子系统设计

> 各子系统需求、设计与实现状态
> 最后更新: 2026-03-03

---

## 1. API 子系统 (`core/api/`)

**状态:** ✅ 已实现

**功能:**
- 需求、项目、任务、机器、工具链 CRUD
- Pipeline、CI/CD、飞书集成、DevOps、Dashboard API

**设计要点:**
- Flask + SQLite
- 跨平台数据库路径 (Windows/Linux)
- 详见 [REQUIREMENTS.md](./REQUIREMENTS.md)

**待完善:**
- [ ] 统一 schema 路径 (`core/db/` vs `core/database/`)
- [ ] 添加 API 认证

---

## 2. 工具子系统 (`openclaw-knowledge/subsystems/tools/`)

**状态:** ✅ 已实现（逻辑在 `openclaw-knowledge/mcp/`，对外通过 CLI/skills 调用）

**工具（包装器）:**
| 工具 | 功能 | 实现位置 |
|------|------|----------|
| feishu_api_logger.py | 解析 Gateway 日志，统计飞书 API 调用 | comm_mcp.feishu_log_analysis；CLI：`cli comm analyze-feishu-logs` / `get-feishu-stats` / `analyze-feishu-issues` |
| feishu_api_analyzer.py | 分析 API 调用模式、问题检测 | 同上 |
| sync_pinball_plan.py | 同步 pinball 计划到 DB | project_mcp.sync_plan；CLI：`cli project sync-pinball-plan`；Skill sync_game_plan |

**依赖:**
- Gateway 日志: `~/.openclaw/logs/gateway.log` 或 FEISHU_LOG_FILE
- 飞书日志 DB: FEISHU_LOG_DB 或 `core/db/feishu_api_log.db`

**待完善:**
- [ ] 与 feishu_api_issues 修复方案联动
- [ ] 添加 Prometheus metrics 导出

---

## 3. CLI 与 MCP 实现 (`openclaw-knowledge/cli/` + `openclaw-knowledge/mcp/`)

**状态:** ✅ 已实现。**代理使用 CLI**，见 [openclaw-knowledge/cli/README.md](../openclaw-knowledge/cli/README.md)。MCP 实现保留在 `openclaw-knowledge/mcp/`（逻辑供 CLI 调用；可选部署见 [openclaw-knowledge/mcp/README.md](../openclaw-knowledge/mcp/README.md)）。

| 能力 | CLI 域 | 功能 |
|------|--------|------|
| 需求/分配/阻塞 | cli project | 对接 Smart Factory API；sync-pinball-plan 同步游戏计划到 DB |
| 飞书/邮件/日志分析 | cli comm | send-feishu、analyze-feishu-logs、get-feishu-stats、analyze-feishu-issues |
| 文件/Git/构建 | cli dev | 文件、Git、白名单命令、build |
| Godot | cli godot | 场景/测试/导出 |
| 测试 | cli test | 单元/集成测试、覆盖率、parse-test-output |
| 分析 | cli analysis | 代码分析、需求提取、变更摘要 |

---

## 4. Skills 子系统 (`openclaw-knowledge/skills/` + `openclaw-knowledge/subsystems/skills/`)

**状态:** ✅ 已实现（`openclaw-knowledge/skills/`）；✅ 基础实现（`openclaw-knowledge/subsystems/skills/`）

**当前 Skills（`openclaw-knowledge/skills/`，流程驱动）:**
| Skill | 执行者 | 功能 |
|-------|--------|------|
| assign_tasks_to_teams | Vanguard | 分配需求、汇报飞书 |
| handle_blockage | Hera | 处理阻塞与决策 |
| generate_daily_report | Vanguard | 日报汇总发飞书 |
| develop_requirement | 开发团队 | 领取、上报、标记 developed |
| test_requirement | Tesla | 测试、创建 Bug、标记 tested |
| parse_requirement_doc | 任意 | PRD 提取并创建需求 |
| sync_game_plan | Vanguard/ops | 同步 pinball-experience 计划到 DB（`cli project sync-pinball-plan` 或 Skill） |
| feishu_api_health_report | Vanguard/ops | 飞书 API 日志分析，可选发飞书（`cli comm analyze-feishu-logs` / `analyze-feishu-issues` 或 Skill） |

**传统（`openclaw-knowledge/subsystems/skills/factory-skill`）:**
| Skill | 功能 | 状态 |
|-------|------|------|
| factory-skill | 调用 Smart Factory API (projects, requirements, tasks, machines, tools, stats) | ⚠️ 已弃用，建议使用 cli project 或 API |

**设计要点:**
- `openclaw-knowledge/skills/` 下 Skills 可经 **定时器或 OpenClaw** 调用（组合 CLI）。**Vanguard 多设备模式下**，**跨团队任务流**须配合 **Redis**（见 [REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md)），Cron **不得**充当**团队间**派发主机制。**团队独立闭环**见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)，**不强制** Redis。
- **模式 A**：依赖 `SMART_FACTORY_API`；多机另设 **`REDIS_URI`**。**模式 B**：二者可选。详见 [skills/README.md](../openclaw-knowledge/skills/README.md)、[OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)。

**待完善:**
- [ ] 添加 SKILL.md 元数据（factory-skill）
- [ ] 支持远程 API 地址配置（已通过环境变量支持）

---

## 5. DevOps 子系统 (`core/devops/`)

**状态:** ⚠️ 部分实现

**组件:**
| 组件 | 功能 | 状态 |
|------|------|------|
| windows_runner.md | Windows Runner 部署文档 | ✅ |
| setup_windows_runner.ps1 | 部署脚本 | ✅ |
| windows_runner_api.py | Runner 状态 API | ✅ |

**待完善:**
- [ ] 与 API server 集成 (当前 API 有 devops 路由但实现可能不完整)
- [ ] 添加 Mac/Linux Runner 支持
- [ ] 文档与 requirements 对齐

---

## 6. 监控子系统 (monitoring/)

**状态:** ⚠️ 设计完成，待部署

**组件:**
- Node Exporter (Linux)
- Prometheus
- Grafana
- macOS Exporter, Windows Exporter
- 详见 monitoring/*.md

**待完善:**
- [ ] 部署各 Exporter
- [ ] 配置 Prometheus 抓取
- [ ] 创建 Grafana Dashboard

---

## 7. 数据库

**状态:** ⚠️ 存在两套 schema

**文件:**
- `core/db/schema.sql` - API 实际使用 (projects, requirements, tasks, machines, tools)
- `core/database/schema.sql` - 增强版 (toolchain, pipelines, progress_history 等)

**建议:**
- [ ] 统一为单一 schema
- [ ] 迁移 `core/database/schema` 中的增强表到 `core/db/schema`
- [ ] 修复 `core/database/schema` 中 INSERT 语句错误 (poetryforge, scriptforge 行)

---

## 实施优先级

| 优先级 | 任务 |
|--------|------|
| P0 | 统一数据库 schema |
| P1 | 完善 DevOps API 集成 |
| P1 | 部署监控 Exporter |
| P2 | factory-skill 远程配置 |
| P2 | 飞书 API 修复方案实施 |
