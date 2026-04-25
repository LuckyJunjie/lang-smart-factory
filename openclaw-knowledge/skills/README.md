# OpenClaw skills (Python modules)

Runnable as `python3 -m skills.<module>` when `openclaw-knowledge` is on `PYTHONPATH` (see repository `pytest.ini` or workspace symlinks from `openclaw-knowledge/scripts/setup_openclaw_workspaces.py`).

Examples:

- `python3 -m skills.assign_tasks_to_teams`
- `python3 -m skills.handle_blockage`
- `python3 -m skills.generate_daily_report`
- `python3 -m skills.develop_requirement`
- `python3 -m skills.test_requirement`
- `python3 -m skills.record_task_usage --task-id <id> --add-tokens <n> --add-prompts <n>`（任务级粗略 token / prompt 次数；等价 `cli project record-task-usage`）

Process flow and when to invoke each skill: [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)（多设备）、[OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md)（团队独立）、[OPENCLAW_DEVELOPMENT_FLOW.yaml](../workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)，以及 **[docs/REDIS_COLLABORATION.md](../../docs/REDIS_COLLABORATION.md)**（模式 A 下跨团队派发/结果以 Redis 为主）。
