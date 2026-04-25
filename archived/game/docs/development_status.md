# 开发状态 - 数据来源说明

**项目:** pinball-experience  
**状态数据来源:** Smart Factory 数据库

---

## 本文件不再维护状态

开发状态、进度、待办任务均以 **Smart Factory 数据库** 为准。本文件仅作说明，不存储与 DB 冲突的内容。

---

## 查询方式

| 方式 | 说明 |
|------|------|
| API | `GET http://localhost:5000/api/requirements?status=new` 等 |
| Dashboard | `GET http://localhost:5000/api/dashboard/stats` |
| 计划同步 | `python -m skills.sync_game_plan` 或 project_mcp 工具 `sync_pinball_plan`；CLI 包装：`openclaw-knowledge/subsystems/tools/sync_pinball_plan.py` |

---

## OpenClaw 行为

- **不要** 在本目录创建或更新 `development_status.md`、`pending_tasks.md` 等状态类 Markdown
- **应当** 通过 Smart Factory API 读写需求与任务
- **应当** 使用 `skills.sync_game_plan` 或 project_mcp 工具 `sync_pinball_plan` 同步计划到 DB

---

*见 [game/README.md](../README.md)*
