# HEARTBEAT — Tesla (Redis)

- Consume `smartfactory:stream:tasks` where assignee is `tesla`
- Execute testing/gameplay tasks
- Publish progress/result to `smartfactory:stream:results`
- If blocked: publish `smartfactory:task:blocker` and `smartfactory:stream:blockers`
- If no task pending: `HEARTBEAT_OK`
