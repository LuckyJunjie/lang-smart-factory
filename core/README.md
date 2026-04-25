# Smart Factory core

Runtime services and persistence for the Smart Factory product:

| Path | Purpose |
|------|---------|
| `api/` | Flask REST API (`server.py`)；人机界面 **`/`**（`static/index.html` + `dashboard.js` / `dashboard-mgmt.js`：仪表盘、项目/需求/任务/测试用例/团队与阻塞的读写，与 `docs/REQUIREMENTS.md` 对齐） |
| `db/` | SQLite files, migrations, `run_migrations.py` |
| `database/` | Extended / reference schema (toolchain, pipelines) |
| `devops/` | Deployment and ops helpers |
| `db/snapshot/` | Timestamped markdown exports of DB state (run `python3 core/db/export_snapshot.py`) |

API specification: [../docs/REQUIREMENTS.md](../docs/REQUIREMENTS.md)（**生产默认**：API 与 DB 跑在 **vanguard001**，其他设备设 `SMART_FACTORY_API=http://<vanguard001>:5000/api` 远程调用）。

OpenClaw-facing workflows, skills, and MCP implementations live under [../openclaw-knowledge/](../openclaw-knowledge/).
