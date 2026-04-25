# TOOLS.md - Vanguard001

Skills define _how_ tools work. This file is for _your_ specifics. **工作方式与节奏**以 `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml` 及 `organization/workspace/WORKFLOW.md` 为准。

## Smart Factory

- **API:** 设置 `SMART_FACTORY_API`（如 http://192.168.3.75:5000 或 localhost:5000）
- **CLI:** `python3 -m cli <domain> <subcommand> [args]`；需求/任务用 **cli project**，飞书用 **cli comm**。见 `openclaw-knowledge/cli/README.md`
- **Feishu:** 飞书群「福渊研发部」；汇报对象 **Master Jay**
- **工作日志:** 每步后 `POST /api/work-log`（role_or_team, task_name, task_output, next_step）

## Hardware

- **Vanguard001:** 树莓派 192.168.3.75 (主控)
- **Jarvis:** Mac mini 192.168.3.79
- **CodeForge:** Windows 192.168.3.4

## Examples

```markdown
### SSH
- vanguard → 192.168.3.75
- jarvis → 192.168.3.79
- codeforge → 192.168.3.4
```

---

Add whatever helps you do your job. This is your cheat sheet.
