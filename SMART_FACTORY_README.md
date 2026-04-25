# 智慧工厂 (Smart Factory)

> 福渊研发部 AI 驱动的软件开发管理系统

## 概述

智慧工厂是一个 AI 辅助的软件开发管理平台，提供需求管理、项目管理、CI/CD、飞书集成等功能。

**规范来源（以文档为准）**：

- **HTTP API 与协作层分层**：`docs/REQUIREMENTS.md`（持久化 / fallback）、`docs/REDIS_COLLABORATION.md`（多机派发与状态流主路径）
- **团队与网络**：`docs/ORGANIZATION.md`
- **OpenClaw 角色与工作流**：`openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`、[OPENCLAW_COMMUNICATION_SYSTEM.md](openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      控制层 (OpenClaw)                        │
│  - 飞书群聊交互                                             │
│  - 任务分发与调度（多机：Redis Pub/Sub + Streams 优先）      │
│  - 定时报告 / 心跳（非 API 轮询协作主路径）                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│ Redis（vanguard001 宿主）  │         │ HTTP API（Flask）            │
│ smartfactory:* 派发/结果流 │         │ 项目/需求/任务持久化与查询   │
│ 其余设备：客户端           │         │ API 为 Redis 降级与报表支撑 │
└───────────────────────────┘         └─────────────┬─────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      智慧工厂 API (Flask)                    │
│  - 需求管理 /api/requirements                               │
│  - 项目管理 /api/projects                                   │
│  - 任务管理 /api/tasks                                      │
│  - 机器资源 /api/machines                                   │
│  - 工具链 /api/tools                                        │
│  - Pipeline /api/pipelines                                  │
│  - CI/CD /api/cicd                                          │
│  - 飞书日志分析 /api/feishu                                 │
│  - 团队通信 /api/teams/* (见 OPENCLAW_COMMUNICATION_SYSTEM)  │
│  - DevOps /api/devops                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (SQLite)                          │
│  - projects - 项目                                          │
│  - requirements - 需求                                       │
│  - tasks - 任务                                             │
│  - machines - 机器资源                                       │
│  - tools - 工具链                                           │
│  - pipelines - CI/CD 流水线                                 │
│  - cicd_* - CI/CD 构建记录                                  │
│  - feishu_api_calls - 飞书 API 调用日志                     │
└─────────────────────────────────────────────────────────────┘
```

多机 OpenClaw 协作以 **Redis**（`smartfactory:*`）为主路径，HTTP API 用于持久化、仪表盘与 Redis 降级；说明见 **`docs/REDIS_COLLABORATION.md`** 与 **`docs/REQUIREMENTS.md`** 文首「协作层」。

## 子系统

### 1. 需求管理 (Requirements)

管理软件开发需求，支持多种需求类型。

**API（节选；完整见 `docs/REQUIREMENTS.md` §2）：**
- `GET /api/requirements` - 列出所有需求（可过滤 status、priority、assigned_team）
- `POST /api/requirements` - 创建需求
- `GET /api/requirements/<id>` - 获取需求详情
- `PATCH /api/requirements/<id>` - 更新需求
- `POST /api/requirements/<id>/take` - 团队领取需求（OpenClaw 工作流）
- `POST /api/requirements/<id>/assign` - Vanguard 分配团队
- `POST /api/requirements/<id>/auto-split` - 自动拆分任务

**需求类型:** feature, bug, enhancement, asset, research

### 2. 项目管理 (Projects)

管理软件开发项目。

**API:**
- `GET /api/projects` - 列出所有项目
- `POST /api/projects` - 创建项目
- `GET /api/projects/<id>` - 获取项目详情
- `PATCH /api/projects/<id>` - 更新项目

### 3. 任务管理 (Tasks)

管理开发任务，与需求关联。需求下**测试用例**的 REST 见 `docs/REQUIREMENTS.md`（`/api/requirements/<rid>/test-cases` 等）。

**API:**
- `GET /api/requirements/<id>/tasks` - 获取需求下的任务
- `GET /api/tasks/<id>` - 单条任务详情
- `POST /api/tasks` - 创建任务
- `PATCH /api/tasks/<id>` - 更新任务

### 4. 机器资源管理 (Machines)

管理研发设备资源（与 `docs/REQUIREMENTS.md` §4 一致；当前实现以列表与状态更新为主）。

**API:**
- `GET /api/machines` - 列出所有机器
- `POST /api/machines/<id>/status` - 更新机器在线状态

### 5. 工具链管理 (Tools)

管理开发工具、MCP服务、Skills等。

**API:**
- `GET /api/tools` - 列出所有工具
- `POST /api/tools` - 注册工具

### 6. Pipeline 工作流

CI/CD 流水线管理。

**API:**
- `GET /api/pipelines` - 列出流水线
- `POST /api/pipelines` - 创建流水线
- `POST /api/pipelines/<id>/run` - 触发构建
- `GET /api/pipelines/<id>/runs` - 构建历史

### 7. CI/CD 触发器

支持 GitHub Webhook 触发构建。

**API:**
- `POST /api/webhook/github` - GitHub Webhook
- `GET /api/cicd/builds` - 构建列表
- `GET /api/cicd/builds/<id>` - 构建详情
- `PATCH /api/cicd/builds/<id>/status` - 更新构建状态

### 8. 飞书 API 分析

分析飞书 API 调用情况。

**API:**
- `POST /api/feishu/logs/analyze` - 分析日志
- `GET /api/feishu/stats` - 调用统计
- `POST /api/feishu/post` - 发送消息到飞书群

**工具:** 逻辑在 MCP（comm_mcp）；CLI 包装保留于 `openclaw-knowledge/subsystems/tools/`。
- **MCP（comm-mcp）**: `analyze_feishu_logs`、`get_feishu_api_stats`、`analyze_feishu_issues`
- **CLI（向后兼容）**: `openclaw-knowledge/subsystems/tools/feishu_api_logger.py`、`feishu_api_analyzer.py`

### 8.5 OpenClaw 通信系统

多设备协调、团队上报、Vanguard/Hera 管理。**模式 A（Vanguard 协调）下，执行机发现跨团队任务的主路径为 Redis**（`smartfactory:stream:tasks` 等）；**模式 B（团队独立）** 见 [OPENCLAW_STANDALONE_WORKFLOW.md](openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)。本节 API 用于持久化、汇总与降级；流程与 Skills 映射见 [OPENCLAW_COMMUNICATION_SYSTEM.md](openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)、[OPENCLAW_DEVELOPMENT_FLOW.yaml](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)。

**API（节选；完整见 `docs/REQUIREMENTS.md` §4.5）：**
- `GET /api/teams/<team>/assigned-requirements`（或 `GET /api/teams/assigned-requirements?team=`）- 团队分配需求
- `POST /api/teams/<team>/machine-status` / `GET /api/teams/<team>/machine-status` / `GET /api/teams/machine-status/summary`
- `POST /api/teams/<team>/status-report` / `GET /api/teams/<team>/status-report` / `GET /api/teams/status-report/summary`
- `POST /api/teams/<team>/task-detail` / `GET /api/teams/<team>/task-details` / `GET /api/teams/development-details/summary`
- `POST /api/discussion/blockage` / `GET /api/discussion/blockages` / `PATCH /api/discussion/blockage/<id>`
- `GET /api/teams/online` - 在线团队
- `GET /api/dashboard/risk-report` - Hera 风险报告
- `GET /api/dashboard/stats` - 仪表盘统计

### 9. DevOps 子系统

CI/CD Runner 管理。

**Windows Runner:**
- 部署脚本: `core/devops/setup_windows_runner.ps1`
- 配置文档: `core/devops/windows_runner.md`
- API: `core/devops/windows_runner_api.py`

**API:**
- `GET /api/devops/runners` - 列出所有 Runner
- `GET /api/devops/runners/windows/status` - Windows Runner 状态
- `POST /api/devops/runners/windows/setup` - 部署 Windows Runner
- `POST /api/devops/runners/windows/start` - 启动
- `POST /api/devops/runners/windows/stop` - 停止

## 快速开始

### 启动 API 服务

```bash
cd core/api
python3 server.py
```

默认监听 `http://0.0.0.0:5000`。**生产约定**：API 与 Redis 跑在 **vanguard001**（`docs/REQUIREMENTS.md` / `docs/ORGANIZATION.md`）；其他设备设置环境变量 **`SMART_FACTORY_API`**（例如 `http://192.168.3.75:5000/api`）远程访问，而非在每台机器本地起完整 API。

### 运行飞书日志分析

```bash
# 方式1：CLI 包装（向后兼容）
python3 openclaw-knowledge/subsystems/tools/feishu_api_logger.py --analyze --report
# 方式2：Skill（可 --post 发飞书）；在 openclaw-knowledge 下执行
cd openclaw-knowledge && python3 -m skills.feishu_api_health_report
```
（逻辑在 `openclaw-knowledge/mcp/remote/comm_mcp/feishu_log_analysis.py`；代理可调用 comm-mcp 工具 `analyze_feishu_logs`。）

### 部署 Windows Runner

```powershell
# 管理员模式运行
cd core\devops
.\setup_windows_runner.ps1 -DroneServer "192.168.3.75:3001" -Secret "your-secret"
```

## 部署信息

### 集群与 API 宿主（与 `docs/ORGANIZATION.md` 一致）

| 团队 / 常驻代理 | 主机 | IP | 说明 |
|-----------------|------|-----|------|
| vanguard001 + hera | 树莓派 | 192.168.3.75 | **Smart Factory API + Redis 默认宿主**；`SMART_FACTORY_API` / `REDIS_URI` 指向本机 |
| Jarvis | Mac mini | 192.168.3.79 | 客户端：远程访问 vanguard001 上 API/Redis |
| CodeForge | Windows | 192.168.3.4 | 客户端 |
| Newton | 树莓派 | 192.168.3.82 | 客户端 |
| Tesla | 树莓派 | 192.168.3.83 | 客户端 |
| Dinosaur | Mac NAS | 待确认 | 客户端（未来 NAS） |

某台开发机上的 OpenClaw **Gateway 端口**等局部配置以该机 `OPENCLAW_DEPLOY.md` / 实际环境为准，**不与**「API 必须跑在 vanguard001」混为一谈。

### 本地开发示例（可选）

在仓库内调试 API 时，使用上文「启动 API 服务」；联网团队机请仍通过 `SMART_FACTORY_API` 指向内网 vanguard001。

## 开发

### 目录结构

```
# 仓库根目录（摘要）
├── core/                      # 运行时：API、SQLite、migrations、devops
│   ├── api/server.py          # Flask 主服务
│   ├── db/                    # 数据库文件、migrations、snapshot
│   └── devops/                # Windows Runner 等
├── openclaw-knowledge/        # 工作流、standards、CLI、skills、MCP、组织
│   ├── workflows/            # OPENCLAW_* 流程与通信说明
│   ├── subsystems/tools/     # 飞书等 CLI 包装
│   └── skills/
├── docs/                      # REQUIREMENTS、ORGANIZATION、REDIS 等规格
├── tests/                     # pytest（test_api.py、test_modules.py）
├── AGENTS.md
└── README.md                  # 知识库入口；本文件为历史/扩展说明时可与 README 对照
```

### 添加新功能

1. 在 `core/db/migrations/`（及必要时 `core/database/schema.sql`）演进表结构
2. 在 `core/api/server.py` 添加 API 接口
3. 更新 `docs/REQUIREMENTS.md`
4. 若影响 OpenClaw 行为，同步 `openclaw-knowledge/workflows/` 中相关叙述
5. 在 `tests/test_api.py` 添加单元测试并运行通过后再提交

### 测试

#### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
python -m pytest tests/ -v

# 运行模块测试
python -m pytest tests/test_modules.py -v

# 运行 API 测试
python -m pytest tests/test_api.py -v

# 生成覆盖率报告（覆盖 core/api 下服务代码）
python3 -m pytest tests/ --cov=core/api --cov-report=html
```

#### 测试要求

**代码提交前必须通过所有测试：**

1. **模块测试** (`test_modules.py`): 验证数据库结构和数据
   - 表存在性检查
   - 字段检查 (step, note)
   - 数据完整性检查

2. **单元测试** (`test_api.py`): 验证 API 功能
   - Projects API
   - Requirements API (包括 step, note 字段)
   - Tasks API
   - Machines API
   - Tools API
   - Pipeline API
   - CI/CD API
   - 飞书集成 API
   - DevOps API

#### 测试数据库

测试使用 `core/db/factory.db` SQLite 数据库。

**核心字段 (step 流程):**
- `not start` - 未开始
- `analyse` - 分析中
- `implement` - 实现中
- `test` - 测试中
- `verify` - 验证中
- `done` - 已完成

#### CI/CD 集成

建议配置 GitHub Actions 自动运行测试：

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install pytest pytest-cov
          python -m pytest tests/ -v
```

## 集成

### 飞书集成

飞书群 "福渊研发部" 已配置，可通过群聊交互。

### OpenClaw 集成

智慧工厂可被 OpenClaw 通过 **CLI / MCP** 调用 API，并以 **Redis** 承载跨团队派发与结果流（见 `docs/REDIS_COLLABORATION.md`）。典型能力：

- 查询项目/需求/任务状态；领取与分配需求（`take` / `assign`）
- 团队状态上报、阻塞与 Hera 决策（`discussion/blockage` 等）
- 触发 CI/CD 构建；飞书日报与汇总

角色节奏与命令映射见 **`openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`**。

## 许可证

内部使用
