# 待处理任务 (Pending Tasks)

**项目:** pinball-experience  
**数据来源:** Smart Factory DB（本文件为导出参考，非权威）

---

## 数据说明

**本目录遵循 DB，不维护独立状态。** 需求与任务以 Smart Factory 数据库为准，本 Markdown 仅作快速参考。

- **API 查询:** `GET http://localhost:5000/api/requirements?status=new` 或 `status=in_progress`；Vanguard 模式下团队查 `GET /api/teams/<team>/assigned-requirements`
- **计划同步:** 运行 `python -m skills.sync_game_plan`（在 DB 所在服务器）或 `cli project sync-pinball-plan`；包装脚本：`openclaw-knowledge/subsystems/tools/sync_pinball_plan.py`
- **开发流程:** 见 `standards/DEVELOPMENT_FLOW.md`；多设备协调见 `docs/OPENCLAW_COMMUNICATION_SYSTEM.md`

---

## 当前待办（来自 DB 同步）

### Baseline 未完成 (0.6–0.10)

| Step | 需求 | 状态 |
|------|------|------|
| 0.6 | Skill shot | new |
| 0.7 | Multiplier | new |
| 0.8 | Multiball | new |
| 0.9 | Combo (optional) | new |
| 0.10 | Polish (physics, animation, audio) | new |

### Baseline 已完成 (0.1–0.5)

| Step | 需求 | 状态 |
|------|------|------|
| 0.1 | Launcher + flippers | done |
| 0.2 | Drain | done |
| 0.3 | Walls and boundaries | done |
| 0.4 | Obstacles + scoring | done |
| 0.5 | Rounds + game over | done |

### Feature 阶段 (2.1–2.44)

共 44 个步骤，详见 FEATURE-STEPS.md。全部初始状态为 new，需团队按序领取并实现。

---

## 开发流程摘要

- **Vanguard 模式**：Vanguard 每小时按 id 分配（开发团队拿 new 含 type=bug，Tesla 拿 step=test/verify）；Tesla 测试出问题则创建 Bug 需求（`POST /api/requirements` type=bug），下一轮分配修复；团队每 30 分钟查 `GET /api/teams/<team>/assigned-requirements` → take → 架构师拆解、Scrum Master 分配、负责人上报；遇阻塞 `POST /api/discussion/blockage`，Hera 每 15 分钟处理；依赖阻塞时 Hera 可重新 assign 另一任务给该团队并将原任务延后。
- **自管模式**：1）团队检查 `GET /api/requirements?status=new` 2）领取 `POST /api/requirements/<id>/take` 3）分析拆解、Scrum Master 分配 4）执行完成，需求 status=done 后领取下一需求。

---

*智慧工厂 - 以 DB 为单一事实来源*
