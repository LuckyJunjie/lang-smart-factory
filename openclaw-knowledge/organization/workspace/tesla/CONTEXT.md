# Smart Factory Context — Tesla

Read: `organization/SMART_FACTORY_CONTEXT.md`

- Flow: `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`
- Role: 测试与玩家体验任务消费（Redis）
- Consume: `smartfactory:stream:tasks`（assignee=tesla）
- Publish: `smartfactory:stream:results`
- Blocker: `smartfactory:task:blocker` / `smartfactory:stream:blockers`
- Enhancement/Bug discovery: publish result event with created requirement metadata
