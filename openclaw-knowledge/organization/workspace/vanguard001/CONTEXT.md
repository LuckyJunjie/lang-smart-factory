# Smart Factory Context — Vanguard001

Read: `organization/SMART_FACTORY_CONTEXT.md`

- Flow: `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`
- Role: 任务派发与汇总
- Dispatch: `PUBLISH smartfactory:task:dispatch` + `XADD smartfactory:stream:tasks`
- Collect: consume `smartfactory:stream:results`
- Blocker awareness: subscribe `smartfactory:task:blocker`
