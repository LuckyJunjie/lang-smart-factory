# 协作scrum.md - Vanguard001（主控/协调）

> 用途：跨团队任务分配看板（需求分配、阻塞决策），并为团队 manager 提供“哪些子 agent 应该尽快 spawn”的上下文入口。

## 角色与会话（建议）
- Team Manager：`vanguard001`
- Architect（可选）：`fuxi`
- Blockage/Risk 决策：`hera`
- Q&A/秘书（可选）：`penny`

## 交付规则（协调侧）
- Vanguard001 负责把 `status=new` 需求 assign 给开发团队/或把 `status=developed` 需求 assign 给 Tesla。
- 具体子 agent spawn enforcement 由各团队 Team Manager 在各自的 `organization/workspace/<team>/协作scrum.md` 中执行并维护。

## 维护字段（Vanguard001 更新）
last_vanguard_check_at:

assignments:
  - requirement_id:
    title:
    assigned_team:
    assigned_agent:
    decision_note:
    next_action:

