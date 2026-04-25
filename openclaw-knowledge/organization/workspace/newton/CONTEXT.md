# Smart Factory Context — Newton

Read: `organization/SMART_FACTORY_CONTEXT.md`

- Flow: `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`
- Role: 测试与玩家体验任务消费（Redis）
- Consume: `smartfactory:stream:tasks`（assignee=newton）
- Publish: `smartfactory:stream:results`
- Blocker: `smartfactory:task:blocker` / `smartfactory:stream:blockers`
- Sub-agents: use `sessions_spawn` when needed
