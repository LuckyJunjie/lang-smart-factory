# HEARTBEAT — Jarvis (Redis)

- Consume `smartfactory:stream:tasks` where assignee is `jarvis`
- Execute task / spawn executors if needed
- Publish progress/result to `smartfactory:stream:results`
- If blocked: publish `smartfactory:task:blocker` and `smartfactory:stream:blockers`
- If no task pending: `HEARTBEAT_OK`
