# Tools index — CLI, Skills, MCP, Scripts

Use this page to **pick the right entry point**. **Vanguard multi-device mode:** set `SMART_FACTORY_API` (e.g. `http://192.168.3.75:5000/api` or `http://127.0.0.1:5000/api`) and **`REDIS_URI`** (e.g. `redis://192.168.3.75:6379`) — see [docs/REDIS_COLLABORATION.md](../docs/REDIS_COLLABORATION.md). **Team standalone:** see [OPENCLAW_STANDALONE_WORKFLOW.md](workflows/OPENCLAW_STANDALONE_WORKFLOW.md) (Redis optional). Put `openclaw-knowledge` on `PYTHONPATH`, or run from a workspace created with `scripts/setup_openclaw_workspaces.py`. **Install and version baseline (Git, Godot 4.5.1, pytest, …):** [docs/TOOLCHAIN.md](docs/TOOLCHAIN.md).

| If you want to… | Prefer | Notes |
|------------------|--------|--------|
| Query/update requirements, tasks, teams, blockages | **`python3 -m cli project …`** | Primary path for OpenClaw agents; JSON on stdout |
| Send Feishu / analyze Feishu logs | **`python3 -m cli comm …`** | Same behaviour as comm-mcp tools |
| Edit files, git, local builds | **`python3 -m cli dev …`** | Whitelisted commands; mirrors dev-mcp |
| Godot project/scene/tests | **`python3 -m cli godot …`** | Mirrors godot-mcp |
| Run pytest / coverage | **`python3 -m cli test …`** | Mirrors test-mcp |
| Lint / diff / doc extraction | **`python3 -m cli analysis …`** | Mirrors analysis-mcp |
| Run a **scheduled team role workflow** (local timer; not inter-team bus) | **`python3 -m skills.<module>`** | Uses HTTP like CLI; **mode A:** cross-team dispatch via Redis; **mode B:** no bus required |
| Use **Cursor/IDE MCP** instead of subprocess CLI | **MCP servers** under `mcp/local/` or `mcp/remote/` | Same capabilities; needs `pip install mcp` |
| One-off DB seed or workspace bootstrap | **`scripts/*.py`** | Operator / setup |
| **GitHub 网络**导致 **`git push` 失败**；**每 5 分钟 cron 重试至成功后卸下** | [docs/GITHUB_NETWORK_AND_PUSH_RETRY.md](docs/GITHUB_NETWORK_AND_PUSH_RETRY.md) · **`scripts/git_push_retry_until_ok.sh`** | 每台机尽量只保留一条此类 cron |
| **Godot：`godogen` / `godot-task`、游戏测试入口** | [docs/GODOT_SKILLS_AND_TESTING.md](docs/GODOT_SKILLS_AND_TESTING.md) | 与 `cli godot`、DoD 测试条款对齐 |

Detail: [OPENCLAW_COMMUNICATION_SYSTEM.md](workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) §4–7 · [OPENCLAW_STANDALONE_WORKFLOW.md](workflows/OPENCLAW_STANDALONE_WORKFLOW.md) · API spec [docs/REQUIREMENTS.md](../docs/REQUIREMENTS.md).

---

## 1. CLI — `python3 -m cli <domain> <subcommand> [args]`

Full reference: [cli/README.md](cli/README.md).

### `cli project` (Smart Factory API)

| Subcommand | Purpose |
|------------|---------|
| `list-requirements` | Filters: `--status`, `--assigned-team`, `--type`, `--assignable true` |
| `get-requirement <id>` | Single requirement |
| `create-requirement` | `--title`, `--description`, `--type`, `--project-id`, `--priority` |
| `update-requirement <id> --fields '<json>'` | PATCH requirement |
| `assign-requirement <id> --team` | Vanguard assign |
| `take-requirement <id> --team --agent` | Team takes |
| `report-status` | `--team`, `--requirement-id`, `--progress`, `--step`, `--tasks` (JSON array) |
| `report-task-detail` | `--detail-type` analysis \| assignment \| development |
| `report-blockage` | Team → Hera |
| `list-blockages` | Hera; `--status pending` |
| `resolve-blockage <id>` | Hera |
| `list-teams-online` | Optional `--within-minutes` |
| `list-tasks <requirement_id>` | Tasks for a requirement |
| `update-task <id> --fields '<json>'` | e.g. `next_step_task_id`, `risk`, `blocker` |
| `get-team-assigned <team>` | Assigned requirements |
| `report-machine-status` | `--team`, `--payload` (JSON) |
| `sync-pinball-plan` | Sync pinball plan steps to DB (server) |

### `cli comm`

| Subcommand | Purpose |
|------------|---------|
| `send-feishu` | `--content`, optional `--webhook-url`, `--title` |
| `send-email` | Placeholder / optional backend |
| `analyze-feishu-logs` | Optional `--log-file` |
| `get-feishu-stats` | `--limit` |
| `analyze-feishu-issues` | Optional `--log-file` |

### `cli dev`

`read-file`, `write-file`, `list-dir`, `git-status`, `git-commit`, `git-push`, `run-command`, `build`.

### `cli godot`

`open-project`, `run-scene`, `export-game`, `get-scene-tree`, `set-node-property`, `run-tests`, `take-screenshot`, `parse-script`.

### `cli test`

`run-unit-tests`, `run-integration-tests`, `check-coverage`, `parse-test-output`.

### `cli analysis`

`analyze-code`, `extract-requirements`, `estimate-complexity`, `summarize-changes`.

---

## 2. Skills — `python3 -m skills.<module> [args]`

Runnable modules under [skills/](skills/). Typical for **local cron-sized** or **orchestrated flows**; they use HTTP like the CLI. **Do not** use skill timers alone as the substitute for **Redis** task dispatch between devices.

| Module | Typical executor | What it does |
|--------|------------------|--------------|
| `assign_tasks_to_teams` | Vanguard | New/assignable → dev teams（含 Tesla/Newton 承担的开发任务）; developed → Tesla/Newton; optional Feishu |
| `generate_daily_report` | Vanguard | Risk + status + dev details → Feishu summary |
| `handle_blockage` | Hera | Pending blockages → decide → assign/update/resolve |
| `hera_monitor` | Hera | Risk report + blockages (visibility; resolution = `handle_blockage`) |
| `develop_requirement` | Dev teams | Glue: get requirement, report status, mark developed |
| `test_requirement` | Tesla / Newton | Test flow; failures → bug requirement |
| `team_sync` | Each team | Pick in_progress or take new assigned |
| `report_team_status` | Each team | Build status-report / DB sync; **prefer mirroring progress to `stream:results` when Redis is up** |
| `record_task_usage` | Any executor | Rough **est_tokens_total** / **prompt_rounds** on a task (`cli project record-task-usage` or same skill) |
| `report_machine_status` | Each team | POST machine-status |
| `meeting_participation` | All | Running meetings for-agent → optional inputs |
| `parse_requirement_doc` | Any | Extract requirements from doc → create via API |
| `sync_game_plan` | Ops (DB server) | Pinball plan → DB |
| `feishu_api_health_report` | Ops | Feishu log health; optional post |
| `create_machine_status_test_requirement` | Ops | One-shot 24h machine-status test requirement |
| `godot_build_and_test` | Dev/Test | Placeholder flow doc for export/tests |
| **godogen** | — | **Cursor Skill** [skills/godogen/SKILL.md](skills/godogen/SKILL.md) — project-level Godot generation |
| **godot-task** | — | **Cursor Skill** [skills/godot-task/SKILL.md](skills/godot-task/SKILL.md) — concrete `.tscn` / `.gd` tasks |

---

## 3. MCP servers — `openclaw-knowledge/mcp/`

Install: `pip install mcp requests` (see [mcp/requirements.txt](mcp/requirements.txt)).

### Remote (usually Vanguard001 / API host)

| Server | Module path | Tools (summary) |
|--------|-------------|-----------------|
| **project-mcp** | `mcp.remote.project_mcp.server` | `list_requirements`, `get_requirement`, `create_requirement`, `update_requirement`, `assign_requirement`, `take_requirement`, `list_tasks`, `get_task`, `update_task`, `report_status`, `report_blockage`, `list_blockages`, `resolve_blockage`, `list_teams_online`, `get_team_assigned`, `report_task_detail`, `report_machine_status`, `sync_pinball_plan` |
| **comm-mcp** | `mcp.remote.comm_mcp.server` | `send_feishu_message`, `send_email`, `analyze_feishu_logs`, `get_feishu_api_stats`, `analyze_feishu_issues` |

### Local (per agent machine)

| Server | Tools (summary) |
|--------|-----------------|
| **dev-mcp** | `read_file`, `write_file`, `list_directory`, `git_status`, `git_commit`, `git_push`, `run_command`, `build_project` |
| **godot-mcp** | `open_project`, `run_scene`, `export_game`, `get_scene_tree`, `set_node_property`, `run_tests`, `take_screenshot`, `parse_script` |
| **test-mcp** | `run_unit_tests`, `run_integration_tests`, `check_coverage`, `parse_test_output` |
| **analysis-mcp** | `analyze_code`, `extract_requirements`, `estimate_complexity`, `summarize_changes` |

**Mapping:** MCP tool names align with **`cli <domain>`** subcommands above; prefer CLI when you do not need a long-lived MCP process.

---

## 4. Scripts — `openclaw-knowledge/scripts/`

| Script | Purpose |
|--------|---------|
| `setup_openclaw_workspaces.py` | Create `.openclaw-workspace/agents/...` symlinks; use `--only-team <name>` for per-device slice |
| `seed_factory_data.py` | Seed projects/requirements from pinball + 24h design |
| `seed_24h_workflow_requirements.py` | Seed REQ-A–D only |
| `seed_openclaw_collab_platform.py` | Seed hypothetical collab platform dataset |
| `auto_archive_context.py` | Archive session transcripts (optional env vars) |
| `vanguard_coordinator.py` | Thin wrapper → `skills.assign_tasks_to_teams` |
| `vanguard_post_feishu_summary.py` | Legacy/summary posting (prefer `skills.generate_daily_report`) |
| `hera_monitor.py` | Legacy wrapper → `skills.hera_monitor` |
| `team_sync.py`, `team_report_status.py`, `team_report_machine_status.py` | Legacy team helpers (prefer `skills.*`) |
| `team_blockage_report.py` | Simple CLI to POST blockage |
| `team_discuss.py`, `team_all_status.py`, `team_member_report.py`, `team_newton_status.py` | Team reporting utilities |
| `create_machine_status_test_requirement.py` | Duplicate of skill (script entry) |

---

## 5. Role → default toolkit (cheat sheet)

| Role | First open | Automations |
|------|------------|-------------|
| **Vanguard** | `OPENCLAW_DEVELOPMENT_FLOW.yaml` (vanguard) | `skills.assign_tasks_to_teams`, `skills.generate_daily_report` |
| **Hera** | `hera_cycle` in YAML | `skills.handle_blockage`, `skills.hera_monitor`, `cli project list-blockages` |
| **Dev team** | Team `CONTEXT.md` | `skills.develop_requirement` / `cli project` + `cli dev` |
| **Tesla** | `tesla_cycle` / `dev_team_cycle` | `skills.test_requirement`, **`skills.develop_requirement`**, `cli test`, `cli dev`, `cli godot` |
| **Newton** | `newton_cycle` / `dev_team_cycle` | 同上 |
| **Any agent** | `AGENTS.md` (repo root) | `cli project`, `skills.meeting_participation` |

---

*Last generated for repo layout under `openclaw-knowledge/`; adjust paths if you symlink from a shallow workspace.*
