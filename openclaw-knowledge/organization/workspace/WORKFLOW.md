# OpenClaw Workflow

权威定义：
- `openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md`（**多设备 Vanguard + Redis**）
- `openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md`（**团队独立**：领导直派 Team Manager，无跨设备 Redis 必选）
- `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`（`execution_modes` + `team_standalone_cycle`）
- `openclaw-knowledge/standards/DEVELOPMENT_FLOW.md`（双模式、产物路径 **`work/<agent>/`**、**git push**、DoD）

## Communication Rule（仅模式 A：多设备协调）

- 团队间通信仅使用 Redis：
  - `smartfactory:task:dispatch`
  - `smartfactory:stream:tasks`
  - `smartfactory:stream:results`
  - `smartfactory:task:blocker`
  - `smartfactory:stream:blockers`
- **模式 A 下**禁止使用 API 轮询与 Cron 作为**跨团队**协作主循环（见 [REDIS_COLLABORATION.md](../../../docs/REDIS_COLLABORATION.md)）。**模式 B** 不适用本条的跨团队约束。

## Team Roles

- `vanguard001`: 派发任务与日报汇总
- `hera`: blocker 决策与会诊
- `jarvis/codeforge/dinosaur`: 开发任务消费与执行
- `tesla/newton`: 测试与玩家体验任务消费与执行

## Reporting

- 汇报对象：`Master Jay`
- 渠道：飞书群「福渊研发部」
