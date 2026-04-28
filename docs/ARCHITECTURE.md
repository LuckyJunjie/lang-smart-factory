# LangFlow Factory 架构文档

**版本:** v3.0
**更新:** 2026-04-28

---

## 1. 系统概述

LangFlow Factory 是基于 LangChain/LangGraph 的智能软件开发流水线引擎。用户输入自然语言需求，系统通过 LangGraph StateGraph 驱动的 Agent 协作，自动完成需求分析、架构设计、详细设计，然后将任务派发给本地 OpenClaw 实例执行代码实现，最终通过测试验证并交付完整的软件产品。

**核心设计原则**: 编排层与分析层使用 LLM，执行层委托给 OpenClaw。

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      LangFlow Factory                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   LangGraph StateGraph                       ││
│  │                                                              ││
│  │   trigger → analyze → architect → detail_design → dispatch  ││
│  │                                                        ↓     ││
│  │                      release ← accept ← test ← verify       ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                    │
│  ┌───────────────────────────┼───────────────────────────────┐│
│  │                    Agent Layer                               ││
│  │  ┌─────────────┐ ┌─────────┐ ┌──────────┐ ┌────────────┐   ││
│  │  │DemandAnalyst│ │ Architect│ │DetailDesign│ │TaskCoord  │   ││
│  │  └─────────────┘ └─────────┘ └──────────┘ └────────────┘   ││
│  │  ┌─────────────┐                                             ││
│  │  │  Tester    │                                              ││
│  │  └─────────────┘                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                    │
│  ┌───────────────────────────┼───────────────────────────────┐│
│  │                    Tools Layer                               ││
│  │  ┌─────────────┐ ┌─────────────────┐ ┌───────┐              ││
│  │  │FileQueue   │ │   OpenClawProxy  │ │GitTools│              ││
│  │  └─────────────┘ └─────────────────┘ └───────┘              ││
│  │  ┌─────────────┐                                            ││
│  │  │FeishuNotifier│                                          ││
│  │  └─────────────┘                                            ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────────┬─────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│  MiniMax M2.7 │    │   文件系统       │    │  飞书 Bot      │
│   (分析/设计)  │    │  /workspace/   │    │   (通知)       │
└───────────────┘    └─────────────────┘    └────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    OpenClaw 实例        │
              │  (Claude Code / Codex)  │
              │    执行代码生成         │
              └────────────────────────┘
```

---

## 3. 核心组件

### 3.1 LangGraph StateGraph (核心编排器)

StateGraph 是整个系统的核心，负责：
- 定义工作流节点和边
- 管理 GraphState 状态传递
- 控制流程条件分支
- 维护执行追踪

```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import tool_node

workflow = StateGraph(GraphState)
workflow.add_node("trigger", trigger_node)
workflow.add_node("analyze", analyze_agent)
workflow.add_node("architect", architect_agent)
workflow.add_node("detail_design", detail_designer_agent)
workflow.add_node("dispatch", task_coordinator_node)
workflow.add_node("verify", task_coordinator_verify_node)
workflow.add_node("test", tester_agent)

workflow.set_entry_point("trigger")
workflow.add_edge("trigger", "analyze")
workflow.add_edge("analyze", "architect")
workflow.add_edge("architect", "detail_design")
workflow.add_edge("detail_design", "dispatch")
workflow.add_edge("dispatch", "verify")  # OpenClaw 执行后返回
workflow.add_edge("verify", "test")
workflow.add_edge("test", "release")
```

---

## 4. Agent 职责

### 4.1 DemandAnalyst
- **输入**: 自然语言需求
- **输出**: 结构化 Requirements
- **LLM**: ✅ 是 (MiniMax M2.7)
- **Prompt**: 分析用户意图、提取关键特性、判断项目类型

### 4.2 Architect
- **输入**: Requirements
- **输出**: ArchitectureSpec
- **LLM**: ✅ 是 (MiniMax M2.7)
- **Prompt**: 设计系统架构、选择技术方案

### 4.3 DetailDesigner
- **输入**: ArchitectureSpec
- **输出**: TaskList + TestCases
- **LLM**: ✅ 是 (MiniMax M2.7)
- **Prompt**: 拆解任务、编写测试用例

### 4.4 TaskCoordinator
- **输入**: TaskList
- **输出**: 任务文件写入 + 结果验证
- **LLM**: ❌ 否 (仅文件操作)
- **职责**: 
  - 将任务写入 `/workspace/{project_id}/work/input/{task_id}.json`
  - 轮询 `/workspace/{project_id}/work/output/` 等待结果
  - 验证输出文件是否符合 acceptance_criteria

### 4.5 Tester
- **输入**: CodeArtifacts + TestCases
- **输出**: TestReport
- **LLM**: ✅ 是 (MiniMax M2.7)
- **Prompt**: 执行测试、生成报告

---

## 5. 数据流

```
用户输入 (自然语言)
        │
        ▼
   ┌─────────┐
   │ Trigger │ ── 初始化 GraphState
   └────┬────┘
        │
        ▼
┌───────────────┐
│ DemandAnalyst │ ── LLM 生成 Requirements
└───────┬───────┘
        │
        ▼
┌───────────┐
│  Architect │ ── LLM 生成 ArchitectureSpec
└─────┬─────┘
      │
      ▼
┌───────────────┐
│DetailDesigner │ ── LLM 生成 TaskList + TestCases
└───────┬───────┘
        │
        ▼
   ┌──────────────┐
   │TaskCoordinator│ ── 写入任务文件到 input/
   └──────┬──────┘
          │
          ▼
   ┌─────────────────┐
   │  OpenClaw Agent  │ ◀── 读取 input/{task_id}.json
   │ (Claude/Codex)  │
   └────────┬────────┘
           │
           ▼
   ┌─────────────────┐
   │  写输出文件      │ ── output/{task_id}.json
   └────────┬────────┘
           │
   ┌──────────────┐
   │TaskCoordinator│ ◀── 轮询等待验证
   │   (Verify)   │
   └──────┬──────┘
          │
          ▼
   ┌────────────┐
   │  Tester    │ ── 执行测试生成 TestReport
   └─────┬──────┘
         │
         ▼
   ┌─────────┐
   │ Release │ ── 交付产物
   └─────────┘
```

---

## 6. 文件队列通信

### 6.1 目录结构

```
/home/pi/.openclaw/workspace/
└── {project_id}/
    └── work/
        ├── input/           # 任务输入目录
        │   ├── task_001.json
        │   ├── task_002.json
        │   └── ...
        └── output/          # 任务输出目录
            ├── task_001.json
            ├── task_002.json
            └── ...
```

### 6.2 任务文件格式 (input/{task_id}.json)

```json
{
  "id": "task_001",
  "title": "实现主菜单",
  "requirements": "创建一个游戏主菜单,包含开始游戏、设置、退出按钮...",
  "project_id": "proj_abc123",
  "acceptance_criteria": [
    "主菜单显示在屏幕中央",
    "点击开始游戏进入游戏场景",
    "设置按钮打开设置面板"
  ],
  "created_at": "2026-04-28T10:00:00Z"
}
```

### 6.3 结果文件格式 (output/{task_id}.json)

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/home/pi/.openclaw/workspace/proj_abc123/src/Menu.ts",
  "error": null,
  "completed_at": "2026-04-28T10:05:00Z"
}
```

### 6.4 轮询机制

```python
def poll_for_result(project_id: str, task_id: str, timeout: int = 300) -> dict:
    """轮询等待任务结果"""
    output_dir = f"/home/pi/.openclaw/workspace/{project_id}/work/output"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result_file = os.path.join(output_dir, f"{task_id}.json")
        if os.path.exists(result_file):
            with open(result_file) as f:
                return json.load(f)
        time.sleep(2)  # 每 2 秒轮询一次
    
    return {"status": "timeout", "error": " Timeout waiting for result"}
```

---

## 7. OpenClaw 集成

### 7.1 调用方式

TaskCoordinator 通过以下方式调用 OpenClaw 编码代理：

1. **方式一: 直接调用** - 写入任务文件后，由外部进程（cron 或 watchdog）监控并触发 OpenClaw
2. **方式二: sessions_spawn** - 使用 OpenClaw 的 `sessions_spawn` API 启动子会话执行

### 7.2 推荐的工作流程

```python
# 1. 写入任务文件
task_file = f"/workspace/{project_id}/work/input/{task_id}.json"
with open(task_file, "w") as f:
    json.dump(task_data, f)

# 2. 触发 OpenClaw (通过监控目录或 API)
# OpenClaw 会读取任务文件、执行、写入 output/

# 3. 轮询等待结果
result = poll_for_result(project_id, task_id)
```

---

## 8. LLM 集成

- **模型**: MiniMax M2.7
- **用途**: DemandAnalyst, Architect, DetailDesigner, Tester (分析/设计/测试)
- **不用于**: 代码生成 (委托给 OpenClaw)
- **调用方式**: LangChain ChatOpenAI 兼容接口
- **配置**:
  ```python
  llm = ChatOpenAI(
      model="MiniMax-M2.7",
      base_url="https://api.minimax.chat/v1",
      api_key=os.getenv("MINIMAX_API_KEY")
  )
  ```

---

## 9. 文件结构

```
lang-smart-factory/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 入口
│   ├── graph_state.py             # 状态定义
│   ├── schema.py                  # 数据 Schema
│   ├── config.py                  # 配置
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Agent 基类
│   │   ├── demand_analyst.py
│   │   ├── architect.py
│   │   ├── detail_designer.py
│   │   ├── task_coordinator.py
│   │   └── tester.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── development_workflow.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── trigger.py
│   │   ├── dispatch.py
│   │   ├── verify.py
│   │   ├── accept.py
│   │   └── release.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_queue.py          # 文件队列工具
│   │   ├── openclaw_proxy.py    # OpenClaw 代理
│   │   ├── api_tools.py
│   │   ├── git_tools.py
│   │   └── feishu_tools.py
│   └── llm/
│       ├── __init__.py
│       └── client.py
├── cli.py
├── api_server.py
├── requirements.txt
├── Makefile
└── tests/
    └── unit/
```

---

## 10. 扩展性

- **新增 Agent**: 在 `agents/` 目录添加类，继承 `BaseAgent`
- **自定义节点**: 在 `nodes/` 目录添加，调用 `workflow.add_node()`
- **条件分支**: 使用 `add_conditional_edges`
- **工具扩展**: 在 `tools/` 目录添加新工具类

---

## 11. 错误处理

| 错误类型 | 处理策略 |
|----------|----------|
| JSON 解析失败 | 回退到 DemandAnalyst 重试 |
| API 调用失败 | 重试 3 次，标记失败 |
| 文件队列超时 | 重试或标记失败 |
| 测试失败 | 自动创建 Bug 任务 |
| OpenClaw 执行失败 | 记录错误到输出文件 |

---

*架构版本: v3.0 | 技术栈: LangChain/LangGraph + MiniMax M2.7 (分析/设计) + OpenClaw (执行)*