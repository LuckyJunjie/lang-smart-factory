# Smart Factory - OpenClaw 知识库

> 福渊研发部 AI 驱动的软件开发管理系统

## 📋 项目目标

智慧工厂是 OpenClaw 的知识库与管理系统，旨在：

- **工作方式**：定义 OpenClaw 代理/团队的工作流程与协作规范
- **需求管理**：维护需求全生命周期
- **项目管理**：管理项目、进度、GDD 关联
- **资源监控**：监控团队资源（机器、Runner）
- **工具链管理**：记录 CLI、Skills、Extensions 及潜在工具
- **组织架构**：维护完整团队结构，便于代理学习与协作

## 📁 目录结构

```
# 仓库根目录
├── core/                         # Smart Factory 运行时：API、SQLite、migrations、devops
├── openclaw-knowledge/           # OpenClaw 知识库：workflows、standards、组织与工作区、CLI、skills、MCP、scripts
├── docs/                         # API / 系统规格、HIGH_REQUIREMENTS 等
├── tests/                        # pytest
├── archived/                     # 历史游戏文档、监控配置、会议脚本、实验文档（参考用）
├── AGENTS.md
└── README.md                     # 本文件
```

## 🤖 Agent 快速入门

**所有 AI 代理必须：**

1. **明确服务对象** — 在 **`openclaw-knowledge/organization/workspace/<团队>/<代理>/USER.md`**（或 OpenClaw 生成的工作区中的同名文件）确认汇报对象；仓库根目录**没有** `USER.md`。
2. **按角色执行** — 遵循 **[OpenClaw Development Flow](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)** 中为本团队/本代理定义的角色与流程（协调、开发、测试、阻塞处理等），使用其中规定的 CLI、技能与工作流。
3. **遵守报告与 DoD** — 使用流程中规定的报告模板（见 `openclaw-knowledge/standards/report/`），并满足 **[Definition of Done](openclaw-knowledge/standards/DEFINITION_OF_DONE.md)**。

完整入口与必读顺序见 **[AGENTS.md](AGENTS.md)**；详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 🔗 快速导航

| 文档 | 说明 |
|------|------|
| [OPENCLAW_DEPLOY.md](OPENCLAW_DEPLOY.md) | OpenClaw 自助部署：工作区 bootstrap、配置路径、API 可选步骤 |
| [AGENTS.md](AGENTS.md) | Agent 入口、身份与角色（必读） |
| [openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) | 角色与工作流定义（代理按此执行） |
| [openclaw-knowledge/standards/DEFINITION_OF_DONE.md](openclaw-knowledge/standards/DEFINITION_OF_DONE.md) | 游戏/应用等开发与测试 DoD（对齐 HIGH_REQUIREMENTS） |
| [openclaw-knowledge/standards/report/README.md](openclaw-knowledge/standards/report/README.md) | 报告模板与规范 |
| [openclaw-knowledge/README.md](openclaw-knowledge/README.md) | OpenClaw 知识库索引 |
| [core/README.md](core/README.md) | API / 数据库核心说明 |
| [docs/README.md](docs/README.md) | 智慧工厂系统文档 |
| [docs/ORGANIZATION.md](docs/ORGANIZATION.md) | OpenClaw 组织架构 |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | API 需求规格 |
| [archived/game/docs/](archived/game/docs/) | 游戏项目文档（归档参考） |

## 🚀 快速开始

```bash
cd core/api
python3 server.py
```

API 将在 http://localhost:5000 启动。

## 📊 组织架构

详见 [docs/ORGANIZATION.md](docs/ORGANIZATION.md)

- **Master Jay (CEO)**, **Winnie (My Lord) (CTO)**
- **Vanguard001** (树莓派 192.168.3.75): vanguard001, secretary, fuxi, hera
- **Jarvis** (Mac mini 192.168.3.79): jarvis, athena, cerberus, hermes, apollo, chiron
- **CodeForge** (Windows 192.168.3.4): codeforge, pangu, nuwa, yu, luban, shennong
- **Newton** (树莓派 192.168.3.82): newton, einstein, curie, galileo, hawking, darwin
- **Tesla** (树莓派 192.168.3.83): tesla, model_s, model_3, model_x, model_y, cybertruck

---

*智慧工厂 - OpenClaw 知识库与管理系统*
