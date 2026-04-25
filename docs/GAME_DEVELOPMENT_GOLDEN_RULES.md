# Game development golden rules (OpenClaw + Smart Factory)

**Purpose:** Capture repeatable practices that produced a **playable, shippable Godot game** from a **raw product intent**, so future OpenClaw runs can follow and extend the same pattern.  
**Case study (read-only reference, not part of this repo):** [whitehouse-decision](https://github.com/LuckyJunjie/whitehouse-decision) — raw requirement → coordinator-led analysis/design → in-repo GDD/architecture/plan → iterative dev assignments → headless regression gates → current runnable build.

**Align with:** [HIGH_REQUIREMENTS.md](./HIGH_REQUIREMENTS.md) (harness I/O, §3 design layer), [openclaw-knowledge/standards/DEFINITION_OF_DONE.md](../openclaw-knowledge/standards/DEFINITION_OF_DONE.md), [openclaw-knowledge/standards/DEVELOPMENT_FLOW.md](../openclaw-knowledge/standards/DEVELOPMENT_FLOW.md), [openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml).  
**Archived seven-phase reference:** [archived/game/development-pipeline.md](../archived/game/development-pipeline.md).

---

## 1. Coordinator owns “raw → structured” before heavy coding

- **Rule:** A **management/coordinator** role (in the case study: **Hera**) turns a **short human brief** into **explicit API-backed work**: analysis tasks, design tasks, and later implementation tasks—with **dependencies** and **acceptance hints**, not a single undifferentiated “build the game” blob.
- **Why it worked:** Design and scope were **decomposed** before executors burned tokens on code; teams could take **small, verifiable** slices.
- **Smart Factory alignment:** [HIGH_REQUIREMENTS.md §3.2–3.3](./HIGH_REQUIREMENTS.md) (decomposition, design/test plan in DB + `work/`). Requirements should be **`POST`’d** with clear `type`, priority, and `depends_on` where needed.
- **Gap / risk:** [OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) **`hera_cycle`** is framed around **blockage** consumption; **`assign_tasks_to_teams`** is **`vanguard001`**. A **greenfield** game still needs an **explicit convention**: *who* creates the first analysis/design requirements and *who* assigns them (Hera + meeting finalize, Vanguard assign skill, or both in sequence). Treating “only Hera, never Vanguard” without documenting assign authority is a **process hole**.

---

## 2. Product truth lives in the **game repo** under `docs/` (not only in Smart Factory DB)

- **Rule:** Commit and maintain **versioned design artifacts** next to the code, at minimum:
  - **GDD** (game design),
  - **architecture** (systems, data flow, autoloads),
  - **development plan** / milestones (phases, ordering),
  - **tech choices** (engine version, language, constraints).
- **Case study layout:** `docs/GDD.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_PLAN.md`, `docs/TECH_CHOICE.md` in the game repository; README summarizes run instructions and structure.
- **Why it worked:** Executors and humans **shared one canonical tree**; diffs on design were reviewable in Git; Smart Factory rows could point to paths without duplicating prose.
- **Smart Factory alignment:** HIGH_REQUIREMENTS §3.3 allows design in **tasks / metadata / `work/`**; golden rule **adds** that for **games**, the **`repo_url` checkout** should carry **`docs/*`** as the **long-lived** source so the project remains understandable without DB access.
- **Gap / risk:** If teams put design **only** under `work/<agent>/` and never promote to `docs/`, the game repo drifts and onboarding breaks. **DoD** should treat “design promoted to repo `docs/` or equivalent” as the default for **game** projects.

---

## 3. Lock the engine version; treat project config as source of truth

- **Rule:** One **Godot minor line** (case study: **4.5.1 stable**). Document it in **README**, **AGENT** entry doc, and **`project.godot`** (`config/features`); reject “works on my machine” ambiguity.
- **Why it worked:** Headless CI and all agents agreed on **API and import behavior**; fewer silent breakage from version skew.
- **Smart Factory alignment:** [OPENCLAW_DEVELOPMENT_FLOW.yaml `environment_bootstrap.godot_development`](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) (`godot_baseline_version: "4.5.1-stable"`).

---

## 4. Two-tier agent docs: orientation vs merge gate

- **Rule:** Split **“how to work in this repo”** from **“what must pass before merge”**:
  - **Orientation** (case study: `AGENT.md`): engine, skills pointer (`godot-task` / `godogen`), autoloads, optional Smart Factory / Redis notes.
  - **Merge gate** (case study: `AGENTS.md`): **API traps** (e.g. `PopupPanel`/`Window` sizing), scene path consistency, and **mandatory headless commands** with **pass criteria** (exit code 0, no script errors in stderr).
- **Why it worked:** Stopped “smoke = reached main menu” from masking **UI/runtime** failures; knowledge **compounded** in-repo.
- **Smart Factory alignment:** DoD §2–3 (tests, evidence in `work/`). Golden rule **tightens** game projects: **player-facing interaction changes** require **headless-automatable** coverage or an **explicit waiver** with reason (same spirit as case study `AGENTS.md`).

---

## 5. Skill policy: **godogen** (whole-game / plan) vs **godot-task** (single task execution)

- **Rule:** Use **project-level** generation/planning/scaffold skills for **milestones and structure**; use **task-level** skills for **concrete** `.tscn` / `.gd` / harness work. Do not blur the two.
- **Case study:** `AGENT.md` documents this split explicitly; implementation follows **godot-task** + `quirks.md` for day-to-day changes.
- **Smart Factory alignment:** `role_skill_policy.*.godot_skills_policy` in [OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) (`project_level: godogen`, `task_level: godot-task`). **Already correct** if agents obey it; the golden rule makes it **normative for success**, not optional taste.

---

## 6. Headless harness is non-negotiable for games

- **Rule:** After **asset** changes, run **import** (`godot --headless --import` or timeout-wrapped equivalent). Run **full project parse/quit** (`godot --path <root> --headless --quit`). Run **targeted test scripts** for **gameplay loop** and **UI regression** (case study: `play_one_round`, `regression_ui`).
- **Why it worked:** Caught parse errors and **invalid property assignments** before human playtesting.
- **Smart Factory alignment:** DoD game row + HIGH_REQUIREMENTS §5.5 (coding/test verification). **`develop_requirement`** skill lists `cli godot run-tests` — teams should **bind** those CLI steps to the **same commands** recorded in the game repo’s `AGENTS.md` (or equivalent).

---

## 7. Accumulate engine **quirks** as a living list

- **Rule:** Maintain a **short, searchable** list of engine/API footguns (case study: `.cursor/skills/godot-task/quirks.md` + grep checklist in `AGENT.md`). Update when a new class of bug appears.
- **Why it worked:** Prevented repeat mistakes across spawn agents and sessions.
- **Smart Factory alignment:** Not spelled out in YAML; treat as **game repo** responsibility alongside skills copied into workspace.

---

## 8. Team Main spawns executors; executors do not “own” the plan

- **Rule:** **Team Main** (e.g. Tesla/Newtwon/Jarvis resident) **takes** the requirement, **splits** work, **spawn** specialists, merges results, and **reports** (to **Redis/API** in Vanguard mode, or to **leadership / Feishu** in [team standalone](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)). Sub-agents do not silently widen scope or skip reporting.
- **Why it worked:** Matched **one coherent integration point** per team; matched the case study’s “manager + spawn” pattern.
- **Smart Factory alignment:** [DEVELOPMENT_FLOW.md §3–4](../openclaw-knowledge/standards/DEVELOPMENT_FLOW.md), `dev_team_cycle` or `team_standalone_cycle` in YAML (spawn, stale detection). **Violations (mode A):** executor completes code but **no** `stream:results` / no **push** / no **task status** update — breaks downstream assigners. **Violations (mode B):** no **push**, no evidence under `work/<agent>/`, or no **closure report** to Master Jay.

---

## 9. Iterate in the loop: design → develop → test → bug requirements → repeat

- **Rule:** After design tasks, assign **implementation** in **thin vertical slices** (playable increments). **Test** teams file **`type=bug` / `type=enhancement`** requirements; coordinator **re-assigns**; no premature “done.”
- **Why it worked:** Preserved **playability** at each iteration (case study reached a **runnable** game early and expanded).
- **Smart Factory alignment:** Vanguard workflow assigns **developed → Tesla/Newton**; blockage and bug creation in [DEVELOPMENT_FLOW.md §7](../openclaw-knowledge/standards/DEVELOPMENT_FLOW.md).

---

## 10. Optional Smart Factory wiring: Redis + `work/` without forking product layout

- **Rule:** If using Smart Factory, keep **per-agent** transcripts and handoffs under **`<game_repo>/work/<agent>/`**, while **product** docs stay under **`docs/`**. **When the org runs Vanguard + Redis (mode A)**, do not skip Redis/API reporting. **Team standalone (mode B)** may omit the bus; still keep `work/` and leadership reporting per [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md).
- **Case study:** `AGENT.md` documents `work/hera`, `work/tesla`, etc., and sample Redis stream consumption.
- **Smart Factory alignment:** [DEVELOPMENT_FLOW.md](../openclaw-knowledge/standards/DEVELOPMENT_FLOW.md) paths + [REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md).

---

## Summary: rules vs current docs

| Golden rule | Already strong in Smart Factory? | Action |
|-------------|-----------------------------------|--------|
| 1 Coordinator decomposition | Partial (API model yes; greenfield owner split vague) | Name **assign + decompose** owner for new games (Vanguard/Hera/meeting). |
| 2 Repo `docs/` as product truth | Implied, not mandatory | Treat as **default for `projects.type=game`**. |
| 3 Engine lock | Yes (YAML baseline) | Keep project README/AGENT in sync. |
| 4 AGENT vs AGENTS split | DoD mentions tests; not two-file pattern | Recommend pattern for game repos. |
| 5 godogen vs godot-task | Yes (YAML) | Enforce in task briefs. |
| 6 Headless harness | Yes (DoD + skills) | Require repo-listed commands in task acceptance. |
| 7 Quirks list | Not in factory docs | Game repo + skill maintenance. |
| 8 Team Main + spawn | Yes | Watch for missing Redis/API sync. |
| 9 Iteration + bugs | Yes | No change. |
| 10 work/ vs docs/ | Yes | Clarify **dual tree** in planning. |

---

## Iteration clause

After each **successful** game delivery, append **one line** to a short “**Verified practices**” subsection (date, repo, what worked) in this file, or open a PR that updates these rules—so the golden rules **learn** from real runs without bloating the YAML on every tweak.
