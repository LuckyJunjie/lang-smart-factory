# OpenClaw knowledge base

Single place for **workflows**, **standards**, **agent workspaces**, **CLI**, **skills**, **MCP**, and **scripts** used by OpenClaw teams.

**Quick picker (CLI vs skills vs MCP vs scripts):** [TOOLS_INDEX.md](TOOLS_INDEX.md)

| Path | Contents |
|------|----------|
| `workflows/` | `OPENCLAW_DEVELOPMENT_FLOW.yaml`, communication system, workspace layout, 24h test design |
| `standards/` | DoD, development flow, projects, report templates |
| `organization/` | Team structure and per-agent workspace definitions (`USER.md`, `TOOLS.md`, …) |
| `cli/` | Smart Factory CLI (`python3 -m cli`) |
| `skills/` | High-level Python skills (`python3 -m skills.*`) |
| `mcp/` | MCP server implementations (optional; CLI preferred) |
| `scripts/` | Workspace bootstrap, seeds, utilities |
| `subsystems/` | Legacy subsystem tools and wrappers |

Product API and database: [../core/README.md](../core/README.md).  
**Redis 协作（多机优先）:** [../docs/REDIS_COLLABORATION.md](../docs/REDIS_COLLABORATION.md).  
High-level requirements: [../docs/HIGH_REQUIREMENTS.md](../docs/HIGH_REQUIREMENTS.md).

**运维与技能补充（本知识库）**

| 主题 | 文档 |
|------|------|
| **GitHub 网络 / `git push` 失败**、**5 分钟 cron 重试至成功后自卸** | [docs/GITHUB_NETWORK_AND_PUSH_RETRY.md](docs/GITHUB_NETWORK_AND_PUSH_RETRY.md)（脚本：`scripts/git_push_retry_until_ok.sh`） |
| **Godot：`godogen` / `godot-task`、游戏测试入口** | [docs/GODOT_SKILLS_AND_TESTING.md](docs/GODOT_SKILLS_AND_TESTING.md) |
| **环境与工具安装基线**（Git、Godot 4.5.1、pytest、FFmpeg 等） | [docs/TOOLCHAIN.md](docs/TOOLCHAIN.md)；工具总表另见根目录 [../docs/TOOLCHAIN.md](../docs/TOOLCHAIN.md) |
