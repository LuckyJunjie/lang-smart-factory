# OpenClaw Workspace Layout (Smart Factory)

本页描述如何把 OpenClaw 的每个 Agent `workspace` 绑定到本仓库内的统一目录，同时不破坏现有的 `openclaw-knowledge/mcp/`、`openclaw-knowledge/skills/` 与 `openclaw-knowledge/cli/` 调用约定。

## 目标
- 让多智能体团队在同一个 `smart-factory` 代码基座上可复用（`openclaw-knowledge/mcp/`、`openclaw-knowledge/skills/`、`openclaw-knowledge/cli/` 保持在仓库中）
- 把运行时数据（sessions/memory）放到仓库内的 `.openclaw-workspace/` 中，便于迁移与清理

## 目录结构
脚本会生成：

```text
<repo-root>/
  .openclaw-workspace/
    agents/
      <agent_id>/
        SOUL.md / USER.md / CONTEXT.md / TOOLS.md / IDENTITY.md ...
        memory/                # 由 OpenClaw 创建/写入
        sessions/             # 由 OpenClaw 创建/写入（本仓库已配置忽略）
        cli@ / skills@ / mcp@  # 指向仓库  下的目录符号链接
        smart-factory@        # 指向仓库 （兼容原有 markdown 路径引用）
    global/                  # 可选：全局知识目录（当前脚本不强制写入内容）
```

符号链接用于保证：
- `python -m cli ...` / `python -m skills...` 在 Agent workspace 根目录下可直接运行
- 原本文档中以 `...` 开头的路径引用仍可用

## 初始化命令

在仓库根目录运行：

```bash
python3 openclaw-knowledge/scripts/setup_openclaw_workspaces.py
```

常用参数：
- `--only-team <name>`：仅处理 `organization/workspace/<name>/`（如 `tesla`），适合单机只部署本设备对应团队主管与子代理
- `--only-agent <id>`：仅生成指定 Agent（可与 `--only-team` 联用）
- `--force`：当目标路径存在但不匹配时替换

## OpenClaw 配置怎么填
把每个 Agent 的 `workspace` 指向：

```text
<repo-root>/.openclaw-workspace/agents/<agent_id>
```

然后重启 OpenClaw gateway / Agent 进程使其生效。

## sessions/归档脚本的兼容
旧版 `scripts/auto_archive_context.py` 写死了 `/home/pi/.openclaw/agents/.../sessions`。
现在支持环境变量/参数：
- `OPENCLAW_SESSIONS_DIR`：直接指定 sessions 目录
- `OPENCLAW_AGENTS_DIR`：指定 `~/.openclaw/agents` 的父目录
- `OPENCLAW_AGENT_ID` 或 `--agent-id`：默认 `vanguard001`

示例：
```bash
python3 openclaw-knowledge/scripts/auto_archive_context.py --agent-id vanguard001
```

## Git 策略
`.gitignore` 已忽略整个 `.openclaw-workspace/`，避免运行时生成的 sessions/memory/符号链接污染版本库。

如果你确实希望将 `MEMORY.md` 之类的“长期记忆”纳入 Git 版本控制，可以在运行时后把对应 ignore 规则调整为更细粒度（我可以再帮你改）。

