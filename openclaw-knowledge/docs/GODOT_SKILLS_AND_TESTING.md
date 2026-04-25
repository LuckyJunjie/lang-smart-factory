# Godot：`godogen` / `godot-task` 与游戏测试说明

本页把 **项目级 Godot 生成**、**任务级 Godot 执行** 与 **游戏测试** 的用法收口到 **openclaw-knowledge**（避免只散落在根目录 `docs/` 或归档里）。权威流程仍以 **[OPENCLAW_DEVELOPMENT_FLOW.yaml](../workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)** 与 **`docs/OPENCLAW_DEVELOPMENT_FLOW.yaml` 引用的 role_skill_policy** 为准。

---

## 1. 两个 Cursor / Agent 技能（按粒度选用）

| 技能 | 路径 | 何时用 |
|------|------|--------|
| **godogen** | [skills/godogen/SKILL.md](../skills/godogen/SKILL.md) | **项目级**：从自然语言规划/生成或重构整个 Godot 游戏骨架、计划文件（`PLAN.md`）、资产与任务拆分；适合大粒度需求与设计闭环。 |
| **godot-task** | [skills/godot-task/SKILL.md](../skills/godot-task/SKILL.md) | **任务级**：具体 `.tscn` / `.gd`、headless 运行场景、**截图与视觉 QA**、控制台日志与单点验证；适合子任务与 Tesla/Newton 侧可复现验收。 |

**规则（与 AGENTS.md / YAML 一致）**：**项目级生成/重构 → godogen**；**具体场景与 harness 执行 → godot-task**。`godogen` 产出的子任务应由执行代理按 **godot-task** 工作流跑完并留证（日志/截图路径进 `work/<agent>/…`）。

**Doc API 缺失时**（godot-task）：在仓库内执行（路径以 Smart Factory 检出根为准）：

```bash
bash openclaw-knowledge/skills/godot-task/tools/ensure_doc_api.sh
```

若工作区使用 `.cursor/skills/`  symlink，可参考 `skills/godot-task/SKILL.md` 内说明。

---

## 2. 游戏测试（自动化与 Harness）

- **环境与版本（Godot 4.5.1、FFmpeg、pytest 等）**：[docs/TOOLCHAIN.md](./TOOLCHAIN.md)。  
- **产品级工具/MCP/技能目录表**：根目录 **[docs/TOOLCHAIN.md](../../docs/TOOLCHAIN.md)**（GdUnit4、GDSnap、角色与 `godogen`/`godot-task` 的职责表）。
- **Harness / HIGH_REQUIREMENTS**：**[docs/HIGH_REQUIREMENTS.md](../../docs/HIGH_REQUIREMENTS.md)**（验证层级、stdout 规则、`godot-task` 引用）。
- **归档详细方案（仍可供 Tesla/开发参考）**：**[archived/game/docs/GODOT_TESTING.md](../../archived/game/docs/GODOT_TESTING.md)** — GdUnit4 + GDSnap、命令行示例、多平台注意点。  
  **状态数据**仍以 Smart Factory **DB/API** 为准，不应以归档 Markdown 为权威进度。

**Tesla / Newton**：执行测试需求时优先 **`test_requirement`** / **`godot-task`**（的场景与断言/截图路径），失败建 **Bug 需求**（`type=bug`），见 `docs/REQUIREMENTS.md`。

---

## 3. 索引

- **工具总表**：[TOOLS_INDEX.md](../TOOLS_INDEX.md)（godogen / godot-task 表行）
- **Skills 列表**：[skills/README.md](../skills/README.md)
- **DoD 中的 Godot**：[standards/DEFINITION_OF_DONE.md](../standards/DEFINITION_OF_DONE.md)
