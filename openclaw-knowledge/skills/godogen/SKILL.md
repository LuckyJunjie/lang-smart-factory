---
name: godogen
description: >-
  Generate or update a complete Godot game from a natural language description.
  Use when the user asks to "make a game", "build a game", "generate a game",
  or wants to create a Godot project from scratch, plan game architecture,
  scaffold scenes and scripts, or generate game assets.
---

# Game Generator — Orchestrator

Generate and update Godot games from natural language.

## Capabilities

Read each sub-file **progressively** — only when you reach its pipeline stage, not upfront.

| File | Purpose |
|------|---------|
| [visual-target.md](visual-target.md) | Generate reference image anchoring art direction |
| [decomposer.md](decomposer.md) | Decompose game into a development plan (`PLAN.md`) |
| [scaffold.md](scaffold.md) | Design architecture and produce compilable Godot skeleton |
| [asset-planner.md](asset-planner.md) | Decide what assets the game needs within a budget |
| [asset-gen.md](asset-gen.md) | Generate PNGs (Gemini) and GLBs (Tripo3D) from prompts |

For individual task execution, read the [godot-task skill](../godot-task/SKILL.md).

## Pipeline

```
User request
    |
    +- Check if PLAN.md exists (resume check)
    |   +- If yes: read PLAN.md, STRUCTURE.md, MEMORY.md -> skip to task execution
    |   +- If no: continue with fresh pipeline below
    |
    +- Generate visual target -> reference.png + ASSETS.md (art direction only)
    +- Decompose into tasks -> PLAN.md
    +- Design architecture -> STRUCTURE.md + project.godot + stubs
    |
    +- If budget provided (and no asset tables in ASSETS.md):
    |   +- Plan and generate assets -> ASSETS.md + updated PLAN.md with asset assignments
    |
    +- For every task in PLAN.md:
    |   +- Set `**Status:** pending`
    |   +- Fill `**Targets:**` with concrete project-relative files expected to change
    |     (e.g. scenes/main.tscn, scripts/player_controller.gd, project.godot)
    |     inferred from task text + scene/script mappings in STRUCTURE.md
    |
    +- Show user a concise plan summary (game name, numbered task list)
    |
    +- Find next ready task (pending, deps all done)
    +- While a ready task exists:
    |   +- Update PLAN.md: mark task status -> in_progress
    |   +- Execute the task following the godot-task workflow
    |   +- Mark task completed in PLAN.md OR replan based on the outcome, summarize to user
    |   +- git add . && git commit -m "Task N done"
    |   +- Find next ready task
    |
    +- Summary of completed game
```

PLAN.md task `**Status:**`: one of `pending`, `in_progress`, `done`, `done (partial)`, `skipped`.

## Running Tasks

For each task, follow the workflow defined in the [godot-task skill](../godot-task/SKILL.md). The task block from PLAN.md should include:

```
## N. {Task Name}
- **Status:** in_progress
- **Targets:** scenes/main.tscn, scripts/player_controller.gd
- **Goal:** ...
- **Requirements:** ...
- **Verify:** ...
```

## Mid-Pipeline Recovery

- **Reset scenes/scripts** — regenerate project skeleton when a task has corrupted or outgrown the architecture.
- **Rewrite the plan** — edit PLAN.md when a task reveals the approach is wrong or new requirements emerge.
- **Generate or regenerate assets** — create new assets or fix broken ones mid-run.

## Visual QA

Visual QA runs as part of each task's execution cycle. **Never ignore a fail verdict** — always act on it before marking a task done.

- **pass/warning** — move on.
- **fail** — up to 3 fix cycles attempted. Read the failure report and decide:
  - **Replan** — reset architecture, rewrite plan, and/or regenerate assets if the root cause is upstream.
  - **Escalate** — surface the issue to the user if you can't determine the right fix.

The final task in PLAN.md is a presentation video — a script that showcases gameplay in a ~30-second cinematic MP4.

## Debugging

If a task reports failure or you suspect integration issues:
- Read `MEMORY.md` — task execution logs discoveries and workarounds
- Read screenshots in `screenshots/{task_folder}/`
- Run `timeout 30 godot --headless --quit 2>&1` to check cross-project compilation
