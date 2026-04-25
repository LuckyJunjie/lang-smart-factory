# Agent Identity Files - Best Practices

> 基于业界实践（SOUL.md 模式、Context Engineering、Agent Prompt Engineering）的 Agent 身份文件编写指南

---

## 原则概览

| 原则 | 说明 |
|------|------|
| **具体优于模糊** | 可预测性测试：读完后能否预测 Agent 对未见话题的立场？模糊描述产生泛化输出 |
| **包含反模式** | 明确 Agent 不应表现的行为和语气 |
| **技能有边界** | 说明擅长什么、不擅长什么，避免过度承诺 |
| **定期更新** | SOUL 每月、USER 每周或随用户变化更新 |

---

## SOUL.md - 人格与职责

**目的：** 定义 Agent 的人格、沟通风格、价值观，使其行为可预测、有辨识度。

### 推荐结构

```markdown
# SOUL.md - [Name]

**Name:** [Name]
**Role:** [角色]
**Team:** [团队]
**Report to:** [汇报对象]
**Emoji:** [图标]

---

## Identity
[1-2 段：具体身份描述，非泛泛而谈]

## Responsibilities
- [具体职责 1]
- [具体职责 2]
- [可交付成果]

## Communication Style
- [回复长度偏好：简洁 / 详尽]
- [技术解释方式]
- [不确定时的表达方式]

## Values & Priorities
- [优化目标，如：质量 > 速度]
- [核心原则]

## Anti-patterns（不应表现）
- [避免的语气或行为]
- [不擅长的领域，应转交他人]

## Skills & Domain
- [具体技术/方法论，非泛泛的"编程"]
- [边界：不做什么]
```

### 参考：CodeForge-SOUL.md

`docs/agents/CodeForge-SOUL.md` 为较完整示例，含工作准则、技术栈、汇报规范、核心价值观。

---

## IDENTITY.md - 简短身份卡

**目的：** 快速识别，供 Session 启动时加载。保持精简（<15 行）。

### 推荐结构

```markdown
# IDENTITY.md - [Name]

- **Name:** [Name]
- **Role:** [角色，含领域，如「架构师 (Godot/后端)」]
- **Team:** [团队]
- **Vibe:** [2-3 个具体特质，如 Strategic, quality-focused, pragmatic]
- **Emoji:** [图标]
- **Skills:** [核心技能，逗号分隔]
- **Constraints:** [主要边界，1 句]
```

---

## USER.md - 服务对象

**目的：** Agent 对服务对象的理解，便于个性化交互和汇报。

### 推荐结构

```markdown
# USER.md - About Your Human

## [Primary User]
- **Role:** [角色]
- **Timezone:** [时区]
- **偏好/约束:** [汇报方式、决策风格等]

## [Secondary User]
- **Role:** [角色]
- **交互场景:** [何时涉及]

## Smart Factory
- **Location:** `./` in workspace
- **Context:** `organization/SMART_FACTORY_CONTEXT.md`
- **Communication:** 飞书群「福渊研发部」
```

### 更新频率

- 用户偏好、职责变化时更新
- 建议每周或按需检查

---

## CONTEXT.md - 项目上下文

**目的：** 指向 Smart Factory 核心文档与**开发流程 YAML**，避免重复，保持单一事实来源。

### 推荐结构

```markdown
# Smart Factory Context [— 团队/角色]

Read: [SMART_FACTORY_CONTEXT.md](...)

**流程与工作标准（必遵）:**
- Flow YAML: `openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml`
- 摘要: `organization/workspace/WORKFLOW.md`
- 工作日志: 每步后 POST /api/work-log；汇报对象 Master Jay，渠道飞书「福渊研发部」
- [本团队节奏、Skill、assigned_agent 等，见各团队 CONTEXT.md 示例]

**Key paths:**
- DoD: `standards/DEFINITION_OF_DONE.md`
- Organization: `docs/ORGANIZATION.md`
- API: `docs/REQUIREMENTS.md`
- Report: 飞书群「福渊研发部」
```

各团队 CONTEXT 已按 OPENCLAW_DEVELOPMENT_FLOW.yaml 配置节奏与工作标准，Agent 须遵从其定义执行。

---

## 能力充分性检查清单

在编写/更新身份文件后，可自检：

- [ ] **可预测性**：他人能否根据 SOUL 预测你对新需求的反应？
- [ ] **技能边界**：是否明确擅长与不擅长？
- [ ] **反模式**：是否列出应避免的行为？
- [ ] **汇报路径**：是否清楚向谁汇报、如何汇报？
- [ ] **约束**：是否写明不做的事、需请示的事？

---

## 参考来源

- SOUL.md 模式：Learn OpenClaw, Amir Brooks
- Context Engineering：Anthropic, Comet
- Agent Prompt Engineering：bKlug, Clarifai, Agentic Thinking
- Identity Prompt：GPTBots 最佳实践

---

*组织架构与角色定义见 [ORGANIZATION.md](../../docs/ORGANIZATION.md)*
