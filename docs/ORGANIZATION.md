# OpenClaw 组织架构

> 本文档维护 OpenClaw 团队完整结构，供代理学习与协作参考。
> 最后更新: 2026-04-04

---

## 📊 组织层级

```
🟢 Master Jay (CEO), 🟢 Winnie (My Lord) (CTO)
│
├── 🟢 协调与项目管理（树莓派 192.168.3.75 — vanguard001 与 hera 共进一台设备）
│   ├── vanguard001（项目管理 + 技术主控；任务派发、协调、日报与网关；**Smart Factory API + Redis 服务宿主**）
│   │   - 可动态 Spawn：`coding-assistant`、`tech-researcher`、`stock-analyzer`（及子任务）
│   └── hera（项目管理；阻塞处理、风险与跨团队决策支持）
│       - 可动态 Spawn：`demand-analyst`、`risk-manager`、`reporter`
│
├── 🟢 Jarvis 团队 (Mac mini - 192.168.3.79)
│   └── jarvis（Mac 开发团队主管；主责开发，兼测试与体验验证）
│       - 可动态 Spawn：`mac-developer`、`bug-fixer`、`render-engineer`
│       - 命名 sub-agents（spawn-only）：`athena`、`cerberus`、`apollo`、`hermes`、`chiron`
│
├── 🟢 CodeForge 团队 (Windows - 192.168.3.4)
│   └── codeforge（Windows 开发团队主管；主责开发，兼测试与体验验证）
│       - 可动态 Spawn：`win-developer`、`bug-fixer`、`render-engineer`
│       - 命名 sub-agents（spawn-only）：`pangu`、`nuwa`、`luban`、`yu`、`shennong`
│
├── 🟢 Tesla 团队 (树莓派 - 192.168.3.83)
│   └── tesla（游戏测试与开发团队主管；**主责**测试与玩家体验；**同等具备** feature/fix/工具与自动化开发闭环）
│       - 可动态 Spawn：`game-tester`、`ux-reviewer`；开发任务下可 Spawn：`mac-developer`、`bug-fixer` 等（与开发主管团队对齐）
│
├── 🟢 Newton 团队 (树莓派 - 192.168.3.82)
│   └── newton（游戏测试与开发团队主管；**主责**测试与玩家体验；**同等具备** feature/fix/工具与自动化开发闭环）
│       - 可动态 Spawn：`game-tester`、`ux-reviewer`；开发任务下可 Spawn：`mac-developer`、`bug-fixer` 等
│
└── 🟢 未来 NAS 团队 (Mac NAS - 待确认)
    └── dinosaur（开发/渲染/NAS 服务主管；主责开发/渲染/NAS，兼测试与集成验证）
        - 可动态 Spawn：`mac-developer`、`bug-fixer`、`render-engineer`、`nas-manager`
        - 命名 sub-agents（spawn-only）：`trex`、`raptor`、`ptero`、`bronto`
```

**能力模型（重要）**  
各设备团队**默认同时具备开发与测试能力**。上文中「开发团队主管」「测试团队主管」等表述指**主责侧重**（工作量与流程入口），**不是**能力边界：开发向团队仍需做测试、用例与验收；测试向团队仍需参与开发协作（如脚本、环境、缺陷定位）。

**独立团队开发模式（Sub-Agent 预定义与饱和运作）**  
独立团队开发的核心在于：**Sub-Agent 不是随机生成的临时工，而是预定义在配置中的正式团队成员**。每个团队有固定花名册（如 Jarvis 的 `athena`、`cerberus`、`apollo`、`hermes`、`chiron`），每个成员拥有独立 workspace 与身份文件。**当任务数量足够时，应让所有 sub-agent 始终保持 1-2 个任务持续工作**，实现团队产能最大化（详见 [独立团队开发模式文档](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md#8-独立团队开发模式--sub-agent-人员预定义与持续饱和运作)）。

---

## 🖥️ 硬件与网络

| 团队 / 常驻代理 | 主机 | IP | 角色 |
|----------------|------|-----|------|
| vanguard001 + hera（同机） | 树莓派 | 192.168.3.75 | 项目管理与主控、阻塞决策、Gateway；**全厂 `SMART_FACTORY_API` 与 `REDIS_URI` 默认指向本机** |
| Jarvis | Mac mini | 192.168.3.79 | 开发（主责）+ 测试；**远程访问** vanguard001 上 API/Redis |
| CodeForge | Windows | 192.168.3.4 | 开发（主责）+ 测试；**远程访问** API/Redis |
| Newton | 树莓派 | 192.168.3.82 | 测试与体验（主责）+ 开发协作；**远程访问** API/Redis |
| Tesla | 树莓派 | 192.168.3.83 | 测试与体验（主责）+ 开发协作；**远程访问** API/Redis |
| Dinosaur | Mac NAS | 待确认 | 开发/渲染/NAS（主责）+ 测试 |

---

## 👥 角色职责

| 角色 | 职责 |
|------|------|
| 主管/项目协调 | 任务分配、进度跟踪、跨团队沟通 |
| 需求分析 | 需求拆解、验收标准、优先级 |
| 架构师 | 技术选型、架构设计、代码 Review |
| 开发 | 功能实现、代码编写、集成 |
| 测试 | 测试计划、用例、自动化、截图验证 |
| DevOps | CI/CD、Runner、部署 |
| 游戏美术 | 美术资源、UI、场景 |
| Scrum Master | 流程管理、敏捷实践 |

*vanguard001 承担项目管理与技术主控（协调派发、网关）；hera 侧重阻塞与项目风险决策。全体成员可在主责之外承担开发与测试工作。*

---

## 📋 协作规范

1. **汇报对象**：向 Master Jay 汇报任务进度与状态
2. **沟通渠道**：飞书群「福渊研发部」
3. **文档维护**：智慧工厂负责需求、项目、工具链文档
4. **身份定义**：各代理可维护 SOUL.md 或类似身份文档
5. **流程执行**：**多设备模式**下任务分配、上报、阻塞处理、日报等由 **Skills** 与 `sessions_spawn` 驱动：Vanguard（`assign_tasks_to_teams`、`generate_daily_report`）、Hera（`handle_blockage`）、开发/测试主管（在本地 spawn 专业智能体并上报状态），详见 [OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)、[openclaw-knowledge/skills/README.md](../openclaw-knowledge/skills/README.md)。**领导直派、单团队闭环**见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)（无需跨设备 Redis 协调必选）。

---

## 📁 Agent 配置

各团队代理配置位于 `openclaw-knowledge/organization/workspace/`：

- **Managers**: 各设备常驻主智能体 (vanguard001, hera, jarvis, codeforge, tesla, newton, dinosaur)；其中 **vanguard001 与 hera 部署在同一树莓派（192.168.3.75）**
- **Members（按需 spawn）**: 专业智能体使用命名 workspace（如 `jarvis/athena`、`codeforge/pangu`、`dinosaur/trex`），但必须由 Team Main 显式 spawn 后执行任务
- **Context**: `openclaw-knowledge/organization/SMART_FACTORY_CONTEXT.md` 含 DoD、工作流、API
- **身份文件指南**: `openclaw-knowledge/organization/workspace/IDENTITY_FILES_GUIDE.md` 含 SOUL/IDENTITY/USER/CONTEXT 最佳实践

## 🔗 相关文档

- [智慧工厂 README](./README.md)
- [OpenClaw 通信与 MCP/Skills 流程（多设备）](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)
- [团队独立闭环工作流](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)
- [开发流程 YAML（团队/联系人/成员与本组织一致）](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)
- [MCP 服务器（local/remote）](../openclaw-knowledge/mcp/README.md)
- [Skills（高层技能）](../openclaw-knowledge/skills/README.md)
- [需求管理 REQUIREMENTS](./REQUIREMENTS.md)
- [工具链 TOOLCHAIN](./TOOLCHAIN.md)
- [身份文件指南（工作区）](../openclaw-knowledge/organization/workspace/IDENTITY_FILES_GUIDE.md)
