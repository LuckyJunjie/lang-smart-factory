# OpenClaw self-service deployment (Smart Factory)

Use this when an **OpenClaw device or instance** (e.g. Tesla Pi, Jarvis Mac) should run only **its slice** of Smart Factory: clone or sync the repo **into that machine’s OpenClaw workspace**, **merge** Smart Factory layout into the existing workspace, and **point OpenClaw config** at the shared knowledge (development flow, CLI, skills).

## Principles

1. **Deploy only this instance** — Do not bootstrap every agent in `openclaw-knowledge/organization/workspace/`. Each device runs one team (or one coordinator) and its sub-agents as defined under that folder in the organization tree (e.g. `tesla/` → `tesla`, `model_s`, `model_3`, …).
2. **Smart Factory is usually nested under the OpenClaw workspace** — Typical clone locations:
   - `<openclaw-workspace>/smart-factory`
   - `<openclaw-workspace>/implementation/smart-factory`  
   Treat that directory as **`<repo-root>`** below (the folder that contains `core/`, `openclaw-knowledge/`, and `docs/`).
3. **Merge, don’t wipe** — OpenClaw already owns most files under its workspace. Deployment **adds** the Smart Factory tree and generated per-agent directories; it does **not** replace the whole workspace.
4. **Update OpenClaw configuration** — Ensure each agent entry (gateway / runner / launcher) uses the **prepared agent directory** and can **read** the canonical docs for behavior: [AGENTS.md](AGENTS.md), [openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml), [openclaw-knowledge/TOOLS_INDEX.md](openclaw-knowledge/TOOLS_INDEX.md).

## Preconditions

- `python3` on PATH
- You know **`<repo-root>`** (Smart Factory checkout; see paths above)
- You know **`<team>`** — top-level folder name under `openclaw-knowledge/organization/workspace/` for this device (e.g. `tesla`, `jarvis`, `newton`, `vanguard001`)

Authoritative layout of agents: browse `openclaw-knowledge/organization/workspace/<team>/` in this repo.

## Step 1 — Place the repository

Clone or sync Smart Factory into the OpenClaw workspace path your org uses, for example:

```bash
cd <openclaw-workspace>
git clone <smart-factory-url> smart-factory
# or: implementation/smart-factory
```

Then:

```bash
cd <repo-root>   # e.g. .../workspace/smart-factory
test -d core && test -d openclaw-knowledge && test -d docs && echo ok
```

## Step 2 — Bootstrap only this team’s agents

From **`<repo-root>`**, run the workspace script **scoped to the team folder** so only that coordinator and sub-agents get `.openclaw-workspace/agents/<agent_id>/` trees:

```bash
python3 openclaw-knowledge/scripts/setup_openclaw_workspaces.py --only-team <team>
```

**Example (Tesla device):** deploy manager + test sub-agents defined under `organization/workspace/tesla/`:

```bash
python3 openclaw-knowledge/scripts/setup_openclaw_workspaces.py --only-team tesla
```

That prepares `tesla`, `model_s`, `model_3`, `model_x`, `model_y`, `cybertruck` (whatever exists with identity files), not Jarvis/Newton/etc.

Options:

- `--force` — fix broken or wrong symlinks / identity links
- `--only-agent <agent_id>` — a single agent folder name (e.g. `model_3`). Can be combined with `--only-team` to narrow further.

Expected: `OpenClaw workspaces prepared: N agent(s)` and `Workspace root: <repo-root>/.openclaw-workspace`. Exit code `0`.

## Step 3 — Point each OpenClaw agent at its prepared directory

For **every** agent this instance runs, set **workspace** in OpenClaw config to:

```text
<repo-root>/.openclaw-workspace/agents/<agent_id>
```

Example paths if the repo is `.../workspace/smart-factory`:

```text
.../workspace/smart-factory/.openclaw-workspace/agents/tesla
.../workspace/smart-factory/.openclaw-workspace/agents/model_3
```

Restart OpenClaw (gateway / agents) so paths reload.

## Step 4 — Merge OpenClaw configuration (knowledge references)

In the OpenClaw workspace (or agent) config, **add or align** references so agents load Smart Factory behavior and tools, for example:

| Intent | Point to (under `<repo-root>`) |
|--------|--------------------------------|
| Entry / obligations | `AGENTS.md` |
| Roles & workflows | `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` |
| Communication / assignment flow | `openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md` (if used) |
| CLI / skills / MCP index | `openclaw-knowledge/TOOLS_INDEX.md` |
| HTTP API | `docs/REQUIREMENTS.md`; runtime: set `SMART_FACTORY_API` to your deployment’s `/api` base |
| **Redis 协作（多机优先）** | `docs/REDIS_COLLABORATION.md`; set **`REDIS_URI`** (e.g. `redis://192.168.3.75:6379` — server on vanguard001) |

Exact keys depend on your OpenClaw version (skills paths, `AGENTS.md` discovery, MCP roots). Goal: **one** checkout of Smart Factory and **paths relative to `<repo-root>`** or to each agent’s prepared folder (which already symlinks `openclaw-knowledge`, `docs`, `core`, …).

## Step 5 — Heartbeat and scheduling (cron / timers)

**They are not in the bootstrap script** — operators must wire **heartbeat behavior** and any **recurring jobs** on each device after deployment.

1. **Per-agent heartbeat spec** — After Step 2, each prepared folder contains **`HEARTBEAT.md`** (symlinked from `openclaw-knowledge/organization/workspace/...`). Read that file for the role: Redis channels/streams, when to publish `smartfactory:agent:heartbeat`, meeting checks, and idle behavior (e.g. `HEARTBEAT_OK`).
2. **Not API-polling loops** — [openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) defines **event-driven** coordination (Redis Pub/Sub + Streams). Do **not** use cron only to poll `GET /api/requirements` as a substitute for dispatch (see `rules.communication` and `schedule` in that file).
3. **Where cron/systemd *is* appropriate** — You may still install **cron jobs or systemd timers** on the host to:
   - run specific **`python3 -m skills.<module>`** actions on an interval (reporting, maintenance) as required by role or [openclaw-knowledge/TOOLS_INDEX.md](openclaw-knowledge/TOOLS_INDEX.md);
   - trigger **meeting participation** or other heartbeat checks at the cadence described in [openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md](openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) / the agent’s `HEARTBEAT.md`.
   Align intervals with those docs; keep **communication** on Redis when that stack is enabled.

## Step 6 — Smart Factory API (usually vanguard001 only)

**Convention:** Run **`python3 server.py`** from `<repo-root>/core/api` on **vanguard001** (see `docs/REQUIREMENTS.md` and `docs/ORGANIZATION.md`). That process owns the **canonical SQLite DB** and REST API; all other OpenClaw hosts set:

```bash
export SMART_FACTORY_API=http://192.168.3.75:5000/api   # replace host/port if needed
```

Teams **update requirements and tasks through this remote API** (via `cli project`, project-mcp, or HTTP)—not by running a second API on each dev machine unless you deliberately isolate a sandbox DB.

On **non-vanguard** devices after deploy, **do not** start a duplicate API for production; point env vars at vanguard001.

## Verify

```bash
cd <repo-root>/.openclaw-workspace/agents/<agent_id>
test -L cli && test -L skills && test -L openclaw-knowledge && echo "symlinks ok"
```

Optional: from that directory, run a harmless CLI invocation (see `openclaw-knowledge/cli/README.md`).

## More detail

- Layout, sessions env vars: [openclaw-knowledge/workflows/OPENCLAW_WORKSPACE_LAYOUT.md](openclaw-knowledge/workflows/OPENCLAW_WORKSPACE_LAYOUT.md)
- Organization tree: [docs/ORGANIZATION.md](docs/ORGANIZATION.md)
- Heartbeat channel design: [openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md](openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)
