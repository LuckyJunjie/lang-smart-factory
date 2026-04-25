# Smart Factory Context — CodeForge

Read: `organization/SMART_FACTORY_CONTEXT.md`

- Flow: `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`
- Role: 开发任务消费与执行（Redis）
- Consume: `smartfactory:stream:tasks`（assignee=codeforge）
- Publish: `smartfactory:stream:results`
- Blocker: `smartfactory:task:blocker` / `smartfactory:stream:blockers`
- Sub-agents: use `sessions_spawn` when needed
