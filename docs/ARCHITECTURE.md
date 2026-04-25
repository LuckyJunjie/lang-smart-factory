# LangFlow Factory 架构文档

## 1. 系统概述

LangFlow Factory 是一个基于 LangChain/LangGraph 的智能软件开发流水线引擎，通过严格的状态机和契约式 IO 保证开发流程的稳定性和可追溯性。

## 2. 核心组件

### 2.1 GraphState (状态管理)
- 所有流程状态存储在 GraphState 中
- 支持执行追踪 (execution_trace)
- 支持审批状态管理
- 包含 project_id, requirement_id, current_step 等核心字段

### 2.2 Agent 层
| Agent | 职责 |
|-------|------|
| BaseAgent | 所有 Agent 的基类 |
| DemandAnalyst | 需求分析与拆解 |
| Architect | 架构设计 |
| DetailDesigner | 详细设计与任务拆分 |
| Developer | 代码实现 |
| Tester | 测试执行 |
| GamePlayEvaluator | 游戏性评估 |

### 2.3 Tools 层
| 工具 | 职责 |
|------|------|
| RedisTools | 任务派发与结果收集 (Stream) |
| SmartFactoryAPI | 项目/需求/任务 CRUD |
| GitTools | 代码版本控制 |
| FeishuNotifier | 飞书通知 |

### 2.4 Workflow 层
- StateGraph: LangGraph 状态机定义
- 节点链: `analysis → architecture → detail_design → dispatch → implementation → testing → acceptance → release`

## 3. 数据流

```
用户输入 → Trigger → DemandAnalyst → Architect → DetailDesigner
                                              ↓
                                         Dispatch (Redis)
                                              ↓
                              Implementation (Worker 执行)
                                              ↓
                                        Testing
                                              ↓
                                       Acceptance
                                              ↓
                                         Release
```

## 4. 文件结构

```
lang-smart-factory/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── graph_state.py         # 状态定义
│   ├── agents/
│   │   ├── base_agent.py      # Agent 基类
│   │   └── demand_analyst.py # 需求分析
│   ├── workflows/
│   │   └── development_workflow.py  # 工作流
│   └── tools/
│       ├── redis_tools.py     # Redis 操作
│       ├── api_tools.py       # API 客户端
│       ├── git_tools.py       # Git 操作
│       └── feishu_tools.py    # 飞书通知
├── cli.py                     # CLI 入口
├── api_server.py              # REST API
├── requirements.txt            # 依赖
├── Makefile                   # 快捷命令
└── tests/
    └── unit/                 # 单元测试
```

## 5. 错误处理

每个节点都有错误处理和回退机制：
- JSON 解析失败 → 回退到需求分析节点
- API 调用失败 → 重试 3 次后标记失败
- 测试失败 → 自动创建 Bug 需求

## 6. 扩展性

- 可添加新的 Agent 类型
- 可自定义 Workflow 节点
- 支持条件分支和循环
- 工具层可扩展支持更多外部系统
