# Smart Factory CLI

OpenClaw agents call the CLI instead of long-lived MCP processes. Set `SMART_FACTORY_API` to the Smart Factory HTTP base URL (see `docs/REQUIREMENTS.md`).

## Run

From the repository root (with `openclaw-knowledge` on `PYTHONPATH`, or use a workspace symlink created by `openclaw-knowledge/scripts/setup_openclaw_workspaces.py`):

```bash
python3 -m cli <domain> <subcommand> [args...]
```

Successful results are **JSON on stdout**; errors go to stderr. Domains: `project`, `comm`, `dev`, `godot`, `test`, `analysis`.

**Task LLM usage (approx.)**: `python3 -m cli project record-task-usage <task_id> --add-tokens 5000 --add-prompts 3`（或 `--set-tokens` / `--set-prompts`）；写入 `tasks.est_tokens_total` / `prompt_rounds`，见 `docs/REQUIREMENTS.md` §3.4。

## Domains (summary)

| Domain | Role |
|--------|------|
| `project` | Requirements, tasks, assignment, status, teams |
| `comm` | Feishu / communication helpers |
| `dev` | Development workflow helpers |
| `godot` | Godot-related commands |
| `test` | Test workflow helpers |
| `analysis` | Analysis / reporting helpers |

Full command tables and **Redis-first** collaboration (multi-device): [docs/REDIS_COLLABORATION.md](../../docs/REDIS_COLLABORATION.md), [OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) §4–§7. Team standalone (no mandatory Redis): [OPENCLAW_STANDALONE_WORKFLOW.md](../workflows/OPENCLAW_STANDALONE_WORKFLOW.md).
