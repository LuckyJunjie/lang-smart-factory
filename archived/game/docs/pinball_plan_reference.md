# Pinball-Experience 计划参考

**项目:** pinball-experience  
**计划来源:** 外部仓库 `/Users/junjiepan/Game/pinball-experience/plan/`

---

## 计划文件

| 文件 | 说明 |
|------|------|
| BASELINE-STEPS.md | Phase 0 基础步骤 0.1–0.10 |
| FEATURE-STEPS.md | Phase 2 功能步骤 2.1–2.44 |

---

## 同步到 Smart Factory DB

将计划同步为 requirements 记录：

```bash
# 方式1：Skill（在 DB 所在服务器执行，推荐）
cd smart-factory && python -m skills.sync_game_plan

# 方式2：project_mcp 工具 sync_pinball_plan（由代理调用）

# 方式3：CLI 包装（向后兼容）
cd subsystems/tools
python sync_pinball_plan.py
# 或指定路径：PINBALL_PLAN_DIR=/path/to/pinball-experience python sync_pinball_plan.py
```

**前置条件:** 先运行 `db/run_migrations.py` 确保 DB 有 workflow 字段。

---

## 实现状态（来自 development_status）

- **0.1–0.5**: 已完成
- **0.6–0.10**: 待实现
- **2.1–2.44**: 待实现

---

*DB 为单一事实来源，本文件仅作路径与同步说明*
