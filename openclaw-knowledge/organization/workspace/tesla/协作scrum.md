# 协作scrum.md - Tesla（测试 + 玩家体验）

> 用途：记录测试/体验相关子 executor 的 spawn 状态，避免测试会话未启动导致任务长期 `pending` 或被动兜底。

## 角色与会话（建议）
- Team Manager：`tesla`
- 可能的 executor：`model_s`、`model_3`、`model_x`、`model_y`、`cybertruck`

## Spawn Enforcement（硬规则）
- Team Manager 每 20 分钟检查一次：
  - 若发现某 executor 相关会话尚未 spawn（`executor_spawned=false`）：先询问 sub-agent；若仍未 spawn/无响应，立即触发 OpenClaw `sessions_spawn` 启动并更新 `executor_spawned_at`。
  - 若已 spawn 但测试/体验输出无进展（stale >= 20 分钟）：再次询问；必要时再次 spawn 并启动。

## 维护字段（Team Manager 更新）
last_team_manager_check_at:
last_spawn_action_at:

requirements:
  - requirement_id:
    requirement_title:
    subtasks:
      - task_id:
        title:
        executor: model_s|model_3|model_x|model_y|cybertruck
        status: todo|in_progress|blocked|done
        executor_spawned: true|false
        executor_spawned_at:
        last_progress_at:
        next_action: spawn|ask|work|report

