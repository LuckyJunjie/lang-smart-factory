# Report templates

Templates for team and task reporting used by OpenClaw flows (`../../workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` → `report_templates`).

| File | Use |
|------|-----|
| `DEVELOPMENT_TASK_REPORT_TEMPLATE.md` | Development task completion |
| `TEST_TASK_REPORT_TEMPLATE.md` | Test task completion |
| `TEAM_STATUS_REPORT_TEMPLATE.md` | Periodic team status |
| `FINAL_DAILY_REPORT_TEMPLATE.md` | End-of-day summary |

**实体 `code`**：分层编码 `P…-REQ…-TASK…-TC…` 见 **[../../../docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md) §2.0**；填报任务/用例 id 时优先与 API 返回的 **`code`** 一致。

**任务 LLM 用量（粗略）**：`tasks.est_tokens_total`、`tasks.prompt_rounds`，上报见 **`cli project record-task-usage`** / **`skills.record_task_usage`** 或 **report-status** `tasks[]`；规范 §3.4。

**工作产物与协作事件（各模版 §0 或清单已强调）**：

- **目录**：目标项目（`repo_url` 检出根）下 **`work/<current_agent>/<timestamp>-<worktype>/`**，与 [DEVELOPMENT_FLOW.md](../DEVELOPMENT_FLOW.md)、[DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md) 一致。
- **API**：任务/需求状态以 **HTTP API / `cli project`** 写 DB 为准（如 **`PATCH /api/tasks/<id>`**、**`report-status`** 且 **tasks[]** 含 **id**）。
- **Redis（优先）**：**`smartfactory:stream:results`**、**`smartfactory:agent:heartbeat`**（建议 ≤15 min）、阻塞流/频道；详见 [REDIS_COLLABORATION.md](../../../docs/REDIS_COLLABORATION.md)。
- **周期**：**30 分钟–1 小时**（或团队约定）上报 **机器（machine_info）+ 任务**，与里程碑/终报叠加。

**CLI / Skills 对齐**：

- 命令形式 **`python3 -m cli <domain> <subcommand>`**（kebab-case 子命令）与域名表见 **[../../cli/README.md](../../cli/README.md)**；与 **HTTP API** 对照见 **[../../../docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md)**。
- 角色必备 Skills（`develop_requirement`、`test_requirement`、`report_team_status`、`generate_daily_report`、`handle_blockage` 等）以 **`../../workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`** 的 `role_skill_policy` / `skills` 为准；实现脚本在 **`../../skills/`**。

Definition of done: [../DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md).
