# 协作scrum.md - Jarvis（开发团队）

> 用途：记录「需求分析→任务拆解→executor 分配→子 agent 是否已启动（spawned）」的全过程，避免把任务分配给未启动的 agent 导致 `pending/兜底`。

## 角色与会话（建议）
- Team Manager：`jarvis`
- Architect：`athena`
- Scrum Master：`chiron`
- 可能的 executor：`cerberus`、`hermes`、`apollo`

## Spawn Enforcement（硬规则）
- 只有当子任务 executor 已满足 `executor_spawned=true` 时，Scrum Master 才能把该 executor 作为子任务执行者落到任务流转中。
- Team Manager 每 20 分钟检查一次：
  - 若发现 `executor_spawned=false`：先询问 sub-agent；若仍未 spawn/无响应，立即触发 OpenClaw `sessions_spawn` 启动 executor，并更新 `executor_spawned_at`。
  - 若已 spawn 但子任务卡住（stale >= 20 分钟）：再次询问；必要时触发会诊/再次 spawn。

## 维护字段（Architect/Scrum Master/Team Manager 更新）
- Architect：更新 `architect_session.executor_spawned` / `architect_session.executor_spawned_at`，并在完成分析后给出拆解要点（可选）。
- Scrum Master：更新 `scrum_master_session` 与 `subtasks[]`（executor/status/next_action），并在“落库分配前”确保 `executor_spawned=true`。
- Team Manager：维护 spawned 时间戳、处理 stale 无进展的询问/再 spawn。
last_team_manager_check_at:
last_spawn_action_at:

requirements:
  - requirement_id:
    requirement_title:
    architect_session:
      agent_id: athena
      executor_spawned: true|false
      executor_spawned_at:
    scrum_master_session:
      agent_id: chiron
      executor_spawned: true|false
      executor_spawned_at:
    subtasks:
      - task_id:
        title:
        executor: cerberus|hermes|apollo
        status: todo|in_progress|blocked|done
        executor_spawned: true|false
        executor_spawned_at:
        last_progress_at:
        next_action: spawn|ask|work|report

