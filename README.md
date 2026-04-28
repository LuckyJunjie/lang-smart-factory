# LangFlow Factory

**基于 LangChain/LangGraph 的智能软件开发流水线**

输入自然语言需求 → LangGraph 编排 → OpenClaw 执行 → 输出软件产物

---

## 系统架构

```
用户输入自然语言需求
        ↓
DemandAnalyst (MiniMax LLM 分析)
        ↓
Architect (MiniMax LLM 设计)
        ↓
DetailDesigner (MiniMax LLM 拆解)
        ↓
TaskCoordinator (写入任务文件)
        ↓
OpenClaw (Claude Code/Codex) 读取任务，执行，写入结果
        ↓
验证 → 交付
```

### 核心组件

| 组件 | 职责 |
|------|------|
| `cli.py` | 命令行入口 |
| `api_server.py` | REST API 服务 (port 5666) |
| `src/workflows/development_workflow.py` | 工作流引擎 |
| `src/agents/demand_analyst.py` | 需求分析 (LLM) |
| `src/agents/architect.py` | 架构设计 (LLM) |
| `src/agents/detail_designer.py` | 详细设计 (LLM) |
| `src/llm/minimax_client.py` | MiniMax M2.7 LLM 客户端 |
| `workers/task_coordinator.py` | 任务协调器 (文件队列) |

---

## 目录结构

```
lang-smart-factory/
├── cli.py                          # CLI: python cli.py run "<需求>" --project-id <id>
├── api_server.py                   # API: POST http://localhost:5666/api/v1/workflow/run
├── src/
│   ├── llm/
│   │   └── minimax_client.py        # MiniMax M2.7 LLM 统一入口
│   ├── agents/
│   │   ├── demand_analyst.py       # 需求分析 Agent
│   │   ├── architect.py            # 架构设计 Agent
│   │   └── detail_designer.py      # 详细设计 Agent
│   ├── workflows/
│   │   └── development_workflow.py # 工作流 (7个节点)
│   ├── graph_state.py              # 状态定义
│   ├── models.py                   # 数据模型
│   └── tools/
│       ├── api_tools.py            # 飞书通知
│       ├── git_tools.py            # Git 操作
│       └── godot_tools.py           # Godot 工具
├── workers/
│   └── task_coordinator.py         # 任务协调器 (文件队列)
├── docs/
│   ├── LANGFLOW_FACTORY_REQUIREMENTS.md  # 需求规格
│   ├── ARCHITECTURE.md             # 架构文档
│   └── DETAILED_DESIGN.md          # 详细设计
└── openclaw-knowledge/             # OpenClaw 知识库
```

---

## 工作流节点

```
trigger → analysis → architect → detail_design → dispatch → implementation → testing → release
```

| 节点 | 说明 |
|------|------|
| `trigger` | 接收用户输入 |
| `analysis` | DemandAnalyst 分析需求 (LLM) |
| `architect` | Architect 设计架构 (LLM) |
| `detail_design` | DetailDesigner 拆解任务 (LLM) |
| `dispatch` | 写入任务文件到 work/input/ |
| `implementation` | 轮询 work/output/ 等待 OpenClaw 结果 |
| `testing` | 汇总测试结果 |
| `release` | 交付产物 |

---

## 使用方法

### CLI 方式

```bash
cd /home/pi/.openclaw/workspace/lang-smart-factory
python cli.py run "开发一个三国跑酷游戏" --project-id godot-trk-001
```

### API 方式

```bash
curl -X POST http://localhost:5666/api/v1/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"requirement": "开发一个三国跑酷游戏", "project_id": "godot-trk-001"}'
```

### 启动 API 服务

```bash
python api_server.py
```

---

## 文件队列通信协议

OpenClaw 通过文件系统与 LangFlow Factory 通信：

| 文件类型 | 路径 |
|----------|------|
| 输入任务 | `/home/pi/.openclaw/workspace/{project_id}/work/input/{task_id}.json` |
| 输出结果 | `/home/pi/.openclaw/workspace/{project_id}/work/output/{task_id}.json` |

### TaskCoordinator 工作流程
1. 创建 `work/input/` 和 `work/output/` 目录
2. 写入任务 JSON 到 input 目录
3. 轮询 output 目录等待结果 (每2秒，超时300秒)
4. 收集结果并返回

---

## LLM 使用策略

| Agent | LLM | 用途 |
|-------|-----|------|
| DemandAnalyst | ✅ 是 | 需求分析、需求拆解 |
| Architect | ✅ 是 | 系统架构设计 |
| DetailDesigner | ✅ 是 | 任务拆分与详细设计 |
| TaskCoordinator | ❌ 否 | 纯文件操作，委托 OpenClaw 执行 |

**注意**: 代码实现由 OpenClaw (Claude Code/Codex) 完成，LangFlow Factory 不直接生成代码。

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/LANGFLOW_FACTORY_REQUIREMENTS.md](docs/LANGFLOW_FACTORY_REQUIREMENTS.md) | 需求规格：系统目标、技术栈、Agent定义、工作流状态机、数据Schema |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构文档：分层架构、数据流、文件队列通信、部署 |
| [docs/DETAILED_DESIGN.md](docs/DETAILED_DESIGN.md) | 详细设计：节点实现代码、Agent Prompt模板、API规范 |
