# HEARTBEAT — Vanguard001 (Redis)

- Publish machine heartbeat every 15 minutes: `PUBLISH smartfactory:agent:heartbeat`
- Publish dispatch events: `smartfactory:task:dispatch` + `smartfactory:stream:tasks`
- Monitor `smartfactory:stream:results`
- Monitor `smartfactory:task:blocker`
- Participate meetings via `meeting_participation` heartbeat check
- Send summary to Feishu
- If no new dispatch/summary action: `HEARTBEAT_OK`
