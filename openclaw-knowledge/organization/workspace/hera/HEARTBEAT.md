# HEARTBEAT — Hera (Redis)

- Publish machine heartbeat every 15 minutes: `PUBLISH smartfactory:agent:heartbeat`
- Consume `smartfactory:task:blocker` and `smartfactory:stream:blockers`
- Produce decision/result to `smartfactory:stream:results`
- Participate meetings via `meeting_participation` heartbeat check
- Trigger/finalize meeting when needed
- If no blocker pending: `HEARTBEAT_OK`
