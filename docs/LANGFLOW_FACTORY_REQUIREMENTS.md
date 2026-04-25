# LangFlow Factory — 基于 LangChain 的新一代智能软件工厂

**状态:** Phase 0 - 需求文档
**创建日期:** 2026-04-25

---

## 📌 项目目标

- **稳定性**: 每一个开发阶段都有显式状态机、结构化 IO Schema 和自动验证步骤
- **可控性**: 所有 Agent 行为通过 LangChain Chain/Graph 定义，人类可任意节点介入
- **可追溯性**: 每次执行自动生成执行图（Run trace）、产物版本、验证证据

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────┐
│           LangFlow Factory 引擎 (Python)          │
│  ┌───────────────────┐  ┌─────────────────────┐  │
│  │ LangGraph 状态机    │  │ LangServe / API     │  │
│  └────────┬──────────┘  └──────────┬──────────┘  │
│  ┌────────┴────────────────────────┴──────────┐   │
│  │  Agent: DemandAnalyst, Architect, Developer│   │
│  └────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────┘
```

---

## 🔁 开发流水线状态机 (LangGraph)

| 步骤 | 节点名称 | Agent |
|------|----------|-------|
| 1 | Trigger | - |
| 2 | Analysis | DemandAnalyst |
| 3 | Architecture | Architect |
| 4 | DetailDesign | DetailDesigner |
| 5 | Dispatch | - |
| 6 | Implementation | Developer |
| 7 | Testing | Tester |
| 8 | GameplayEval | GamePlayEvaluator |
| 9 | Acceptance | - |
| 10 | Release | CICDOrchestrator |

---

## 📦 Phase 实施路线图

| Phase | 内容 |
|-------|------|
| Phase 1 | LangGraph 状态机骨架 |
| Phase 2 | Worker 协议与 Redis 集成 |
| Phase 3 | 游戏感知评估 Agent |
| Phase 4 | 人工审批、CI/CD、飞书卡片 |
| Phase 5 | 仪表盘与监控 |

---

## 🛠️ 核心 Agent 列表

| Agent | 功能 |
|-------|------|
| DemandAnalyst | 需求分析与拆解 |
| Architect | 系统架构设计 |
| DetailDesigner | 任务拆分与测试用例 |
| Developer | 代码实现 |
| Tester | 测试执行 |
| GamePlayEvaluator | 游戏性评估 |
| CICDOrchestrator | 流水线编排 |

---

## 🔗 与现有 Smart Factory 集成

- **数据库**: 共享 SQLite（通过 HTTP API）
- **Redis**: LangFlow 负责 PUBLISH 派发、XADD Streams
- **飞书**: 消息通知与人工审批卡片
- **知识库**: openclaw-knowledge/ 继续作为参考
