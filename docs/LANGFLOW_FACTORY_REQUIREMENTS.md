# LangFlow Factory — 需求规格文档

**状态:** v3.0 (重构版)
**版本:** 2026-04-28

---

## 1. 项目概述

**LangFlow Factory** 是一个基于 LangChain/LangGraph 的智能软件开发流水线引擎。用户输入自然语言需求（如"开发一个三国跑酷游戏"），系统通过 LangGraph 编排工作流，自动完成需求分析、架构设计、详细设计，并将代码实现委托给本地 OpenClaw 实例（Claude Code / Codex），最终输出完整的软件产品（游戏或应用）。

**核心洞察**: lang-smart-factory 通过 LangGraph 编排流程，但将实际的代码生成委托给本地 OpenClaw 实例。它不直接调用 LLM 进行代码生成。

---

## 2. 核心特性

| 特性 | 描述 |
|------|------|
| **状态机驱动** | 所有开发阶段通过 LangGraph StateGraph 定义，确保流程可控 |
| **分层架构** | 编排层 (LangGraph) → 分析层 (LLM) → 执行层 (OpenClaw) |
| **文件队列通信** | 基于文件系统的任务队列，替代不稳定的 Redis |
| **结构化 IO** | 每个 Agent 有显式输入/输出 Schema，自动验证 |
| **可追溯** | 每次执行自动生成执行追踪 (Run Trace)、产物版本、验证证据 |

---

## 3. 技术栈

| 层级 | 技术选型 |
|------|----------|
| **编排框架** | LangChain + LangGraph |
| **LLM (分析/设计)** | MiniMax M2.7 (仅用于需求分析、架构设计、任务拆分) |
| **代码执行** | OpenClaw (Claude Code / Codex) |
| **任务队列** | 文件系统 (`/home/pi/.openclaw/workspace/{project_id}/work/input/` & `output/`) |
| **状态存储** | GraphState (LangGraph 内置) |
| **API 层** | LangServe / FastAPI |
| **通知** | 飞书 Webhook |

---

## 4. Agent 定义

| Agent | 功能 | 输入 | 输出 | LLM 调用 |
|-------|------|------|------|----------|
| **DemandAnalyst** | 需求理解与拆解 | 自然语言需求 | 结构化 Requirements | ✅ 是 |
| **Architect** | 系统架构设计 | Requirements | ArchitectureSpec | ✅ 是 |
| **DetailDesigner** | 详细设计 & 任务拆分 | ArchitectureSpec | TaskList + TestCases | ✅ 是 |
| **TaskCoordinator** | 任务派发与验证 | TaskList | 任务文件写入 + 结果验证 | ❌ 否 |
| **Tester** | 测试执行 | CodeArtifacts + TestCases | TestReport | ✅ 是 |

> **注意**: TaskCoordinator 不直接生成代码，它将任务写入文件队列，由 OpenClaw 的编码代理执行。

---

## 5. 工作流状态机

```
┌─────────┐     ┌─────────────┐     ┌────────────┐
│ Trigger │ ──▶ │ DemandAnalyst │ ──▶ │  Architect  │
└─────────┘     └─────────────┘     └──────┬─────┘
                                            │
                                            ▼
┌─────────┐     ┌─────────────┐     ┌────────────┐
│ Release │ ◀── │ Acceptance  │ ◀── │   Tester   │
└─────────┘     └─────────────┘     └──────┬─────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │ DetailDesigner   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ TaskCoordinator│ ──▶ 写入文件队列
                                      └───────┬──────┘
                                              │
                                              ▼
                                    ┌───────────────────┐
                                    │  OpenClaw Agent    │ ◀── 读取任务文件
                                    │  (Claude/Codex)     │
                                    └─────────┬─────────┘
                                              │
                                              ▼
                                      ┌───────────────────┐
                                      │  写入输出文件      │
                                      └───────────────────┘
```

### 节点列表

| 步骤 | 节点 | Agent | 说明 |
|------|------|-------|------|
| 1 | `trigger` | - | 接收用户输入 |
| 2 | `analyze` | DemandAnalyst | 需求分析 (LLM) |
| 3 | `architect` | Architect | 架构设计 (LLM) |
| 4 | `detail_design` | DetailDesigner | 详细设计 (LLM) |
| 5 | `dispatch` | TaskCoordinator | 任务派发 (文件队列) |
| 6 | `implement` | OpenClaw Agent | 代码实现 (外部代理) |
| 7 | `verify` | TaskCoordinator | 验证输出文件 |
| 8 | `test` | Tester | 测试验证 |
| 9 | `accept` | - | 人工确认 |
| 10 | `release` | - | 交付产物 |

---

## 6. 数据 Schema

### 6.1 GraphState

```python
class GraphState(TypedDict):
    project_id: str
    requirement_id: str
    original_requirement: str
    requirements: Requirements
    architecture: ArchitectureSpec
    tasks: list[Task]
    test_cases: list[TestCase]
    code_artifacts: list[CodeArtifact]
    test_report: TestReport
    execution_trace: list[TraceEntry]
    current_step: str
    status: str  # pending/running/completed/failed
```

### 6.2 Requirements

```python
class Requirements(TypedDict):
    summary: str
    type: str  # game/application
    features: list[str]
    constraints: list[str]
    target_platform: str
    tech_stack: list[str]
```

### 6.3 Task

```python
class Task(TypedDict):
    task_id: str
    title: str
    description: str
    requirements: str  # 完整需求描述
    project_id: str
    acceptance_criteria: list[str]
    priority: str  # high/medium/low
    status: str  # pending/in_progress/completed
    created_at: str
```

---

## 7. 文件队列通信协议

### 7.1 任务文件 (Input)

**路径**: `/home/pi/.openclaw/workspace/{project_id}/work/input/{task_id}.json`

```json
{
  "id": "task_001",
  "title": "实现主菜单",
  "requirements": "创建一个游戏主菜单，包含开始游戏、设置、退出按钮...",
  "project_id": "proj_abc123",
  "acceptance_criteria": [
    "主菜单显示在屏幕中央",
    "点击开始游戏进入游戏场景",
    "设置按钮打开设置面板"
  ],
  "created_at": "2026-04-28T10:00:00Z"
}
```

### 7.2 结果文件 (Output)

**路径**: `/home/pi/.openclaw/workspace/{project_id}/work/output/{task_id}.json`

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/home/pi/.openclaw/workspace/proj_abc123/src/Menu.ts",
  "error": null,
  "completed_at": "2026-04-28T10:05:00Z"
}
```

---

## 8. API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/projects` | 创建项目 |
| POST | `/api/v1/requirements` | 提交需求 |
| GET | `/api/v1/projects/{id}/status` | 查询状态 |
| POST | `/api/v1/projects/{id}/approve` | 人工审批 |
| GET | `/api/v1/projects/{id}/artifacts` | 下载产物 |

---

## 9. 验收标准

- [x] LangGraph 状态机完整实现
- [x] 4 个分析/设计 Agent 正常工作 (DemandAnalyst, Architect, DetailDesigner, Tester)
- [x] TaskCoordinator 正确写入/读取文件队列
- [x] OpenClaw 编码代理正确执行任务
- [x] MiniMax M2.7 用于分析/设计（不直接生成代码）
- [x] 无 Redis 依赖
- [x] 关键节点飞书通知
- [x] 执行追踪可追溯

---

## 10. 非功能需求

| 需求 | 目标 |
|------|------|
| 响应时间 | 单节点 < 30s |
| 并发 | 支持 10 个项目并行 |
| 错误恢复 | 单点失败不影响整体 |
| 日志 | 完整执行日志 |

---

## 11. 与 v2.0 的区别

| 特性 | v2.0 (旧) | v3.0 (新) |
|------|----------|----------|
| 代码生成 | Developer Agent 调用 LLM | TaskCoordinator 委托给 OpenClaw |
| 任务队列 | Redis Stream | 文件系统 |
| 消费者组 | XREADGROUP | 文件轮询 |
| LLM 用途 | 全部 Agent | 仅分析/设计 Agent |
| 文件扩展名 | 限制 .gd/.py | 无限制 (OpenClaw 决定) |
