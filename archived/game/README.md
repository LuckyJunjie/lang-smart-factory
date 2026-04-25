# Game 文档目录

> **本目录遵循 Smart Factory 数据库，不维护独立状态。**

---

## 数据来源

| 内容 | 来源 | 说明 |
|------|------|------|
| 需求与任务 | Smart Factory DB | `GET /api/requirements`, `GET /api/tasks` |
| 项目进度 | Smart Factory DB | 以 DB 为准，本目录不记录 |
| 开发流程 | `standards/DEVELOPMENT_FLOW.md` | 团队领取、拆解、分配 |

**本目录不存储与 DB 冲突的状态。** OpenClaw 应通过 API 读写需求与任务，而非更新本目录下的 Markdown。

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/pending_tasks.md](docs/pending_tasks.md) | 待办参考（导出自 DB，非权威） |
| [docs/pinball_plan_reference.md](docs/pinball_plan_reference.md) | 计划文件路径与同步说明 |
| [docs/GODOT_TESTING.md](docs/GODOT_TESTING.md) | Godot 测试工具与流程（GdUnit4、GDSnap、多平台） |
| [development-pipeline.md](development-pipeline.md) | 游戏开发流水线（目标流程）；当前遵循 [DEVELOPMENT_FLOW](../standards/DEVELOPMENT_FLOW.md) |

---

## 开发状态

**查询方式：** `GET http://localhost:5000/api/requirements?project_id=<id>` 或 Dashboard API

本目录不维护 `development_status.md` 等状态文件，避免与 DB 不一致。
