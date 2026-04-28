# LangFlow Factory

**基于自然语言输入的智能软件开发流水线**

> LangFlow Factory = LangChain/LangGraph 编排层 + OpenClaw 执行层 + 文件队列通信 + 全局 ReAct 验证环

---

## 核心理念

**输入**：自然语言需求（例如"开发一个三国跑酷游戏"）
**输出**：完整可运行的游戏或应用

LangFlow Factory 不直接生成代码——它编排流程、分析需求、设计架构，然后将任务交给 OpenClaw 编码代理执行。全局 ReAct 验证环确保每个环节的输出都符合验收标准，不符合则自动修正重试。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangFlow Factory (Newton)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LangGraph 工作流状态机                      │   │
│  │   trigger → analyze → architect → detail_design          │   │
│  │       ↓                                    ↓             │   │
│  │      end ← release ← test ← verify ← dispatch             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│              ┌───────────────┼───────────────┐                    │
│              ↓               ↓               ↓                    │
│     ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│     │DemandAnalyst│  │ Architect  │  │DetailDesigner│              │
│     │  (LLM分析)  │  │  (LLM设计) │  │  (LLM拆解)  │              │
│     └────────────┘  └────────────┘  └────────────┘              │
│                              │                                    │
│                    ┌─────────┴─────────┐                        │
│                    │  dispatch_node     │                        │
│                    │  写入任务文件      │                        │
│                    └─────────┬─────────┘                        │
│                              │                                    │
│                    ┌─────────┴─────────┐                        │
│                    │ implementation_node│                        │
│                    │  ReAct 验证循环    │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼───────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
   work/input/           work/output/          work/feedback/
   (任务文件)            (结果文件)             (反馈文件)
          │                    ↑                    ↑
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   OpenClaw Agents   │
                    │  (einstein, curie,  │
                    │   galileo, darwin)   │
                    │  Monitor + Execute   │
                    │  + coding-agent      │
                    └─────────────────────┘
```

### 两层系统

| 系统 | 职责 | 技术 |
|------|------|------|
| **LangFlow Factory (Newton)** | 编排、分析、设计、验证 | LangChain/LangGraph + MiniMax LLM |
| **OpenClaw Agents** | 监控、执行、编码 | sessions_spawn + coding-agent |

---

## 工作流节点

```
trigger → analyze → architect → detail_design → dispatch → implementation → verify → test → release
```

| 节点 | 执行者 | LLM调用 | 说明 |
|------|--------|---------|------|
| `trigger` | 系统 | ❌ | 接收输入，初始化状态 |
| `analyze` | DemandAnalyst | ✅ | 需求分析，生成结构化需求 |
| `architect` | Architect | ✅ | 架构设计，生成模块划分 |
| `detail_design` | DetailDesigner | ✅ | 任务拆解，生成任务列表 |
| `dispatch` | 系统 | ❌ | 写入任务文件到 work/input/ |
| `implementation` | OpenClaw | ❌ | 执行任务，写入 work/output/ |
| `verify` | **ReAct Loop** | ✅ | 验证输出，不符合则反馈重试 |
| `test` | Tester | ✅ | 集成测试 |
| `release` | 系统 | ❌ | 交付产物 |

---

## 全局 ReAct 验证环

ReAct (Reasoning + Acting) 验证环贯穿所有 LLM 环节，不是只在 implementation 阶段。

### 每个 LLM Agent 的 ReAct 循环

```
LLM Agent 生成输出
        ↓
验证输出是否符合要求
        ↓
   ┌────┴────┐
 Pass     Fail → 记录问题 → LLM 根据反馈重新生成
                    ↑                      │
                    └──────────────────────┘
              (最多重试 3 次)
```

### 各环节验证点

| 环节 | 验证内容 | 失败处理 |
|------|----------|----------|
| `analyze` | 需求 JSON 格式是否完整、字段是否缺失 | LLM 重新解析 |
| `architect` | 架构是否覆盖所有需求、依赖是否合理 | LLM 重新设计 |
| `detail_design` | 任务是否覆盖架构、依赖是否无环 | LLM 重新拆分 |
| `implementation` | OpenClaw 输出是否符合 acceptance_criteria | 写 feedback 重试 |
| `verify` | 产出物是否可运行、是否满足验收标准 | 写 feedback 重试 |
| `test` | 测试用例是否通过 | 修复代码或修复测试 |

### Verify Node 详细流程

```python
def verify_node(state: Dict) -> Dict:
    """ReAct 验证循环 - 验证 OpenClaw 输出，不符合则触发重试"""
    project_id = state.get("project_id")
    dispatched = state.get("dispatched_tasks", [])
    max_retries = 3
    
    verified = []
    failed = []
    feedback_dir = f"{WORKSPACE_ROOT}/{project_id}/work/feedback"
    os.makedirs(feedback_dir, exist_ok=True)
    
    for task_id in dispatched:
        output_file = f"{WORKSPACE_ROOT}/{project_id}/work/output/{task_id}.json"
        
        # 等待 OpenClaw 写入结果
        for attempt in range(max_retries):
            if not os.path.exists(output_file):
                time.sleep(2)
                continue
            
            with open(output_file, "r") as f:
                result = json.load(f)
            
            # 加载任务规格（含 acceptance_criteria）
            task = load_task(f"work/input/{task_id}.json")
            
            # 验证输出
            is_valid, errors = verify_against_criteria(result, task)
            
            if is_valid:
                verified.append(task_id)
                break
            else:
                # 写反馈文件，触发 OpenClaw 重试
                feedback = {
                    "task_id": task_id,
                    "attempt": attempt + 1,
                    "errors": errors,
                    "acceptance_criteria": task.get("acceptance_criteria", []),
                    "suggestion": generate_fix_suggestion(errors, task),
                }
                feedback_file = f"{feedback_dir}/{task_id}_feedback_{attempt+1}.json"
                with open(feedback_file, "w") as f:
                    json.dump(feedback, f, indent=2)
                
                # 删除旧输出，等待 OpenClaw 重试
                os.remove(output_file)
                print(f"[ReAct] Task {task_id} failed (attempt {attempt+1}), feedback written")
        
        if task_id not in verified:
            failed.append(task_id)
    
    state["verified_tasks"] = verified
    state["failed_tasks"] = failed
    state["current_step"] = "test"
    return state
```

---

## 文件队列通信协议

### 目录结构

```
/home/pi/.openclaw/workspace/{project_id}/work/
├── input/          # LangFlow Factory 写入，OpenClaw 读取
│   └── {task_id}.json
├── output/        # OpenClaw 写入，LangFlow Factory 读取
│   └── {task_id}.json
└── feedback/      # LangFlow Factory 写入，OpenClaw 读取（重试）
    └── {task_id}_feedback_{n}.json
```

### 任务文件 (input)

```json
{
  "id": "task_001",
  "title": "实现主菜单",
  "requirements": "创建游戏主菜单，包含开始游戏、设置、退出按钮...",
  "project_id": "godot-trk-001",
  "acceptance_criteria": [
    "主菜单显示在屏幕中央",
    "点击开始游戏进入游戏场景",
    "设置按钮打开设置面板"
  ],
  "feedback": [],
  "created_at": "2026-04-28T10:00:00Z"
}
```

### 结果文件 (output)

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/home/pi/.openclaw/workspace/godot-trk-001/src/MainMenu.ts",
  "errors": [],
  "completed_at": "2026-04-28T10:05:00Z"
}
```

### 反馈文件 (feedback)

```json
{
  "task_id": "task_001",
  "attempt": 1,
  "errors": ["主菜单未居中显示", "点击事件未绑定"],
  "acceptance_criteria": ["主菜单显示在屏幕中央", "点击开始游戏进入游戏场景"],
  "suggestion": "使用 CenterContainer 包裹主菜单节点，点击事件改用 Button 的 pressed 信号"
}
```

---

## OpenClaw Agent 接入方式

### 模式 B：独立监控

OpenClaw agents 持续监控 `work/input/` 目录，有新任务就执行，无需 LangFlow Factory 直接调用。

### Cron 设置

```bash
# 每5分钟检查一次新任务
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m src.skills.langflow_executor >> /tmp/langflow_executor.log 2>&1
```

### Executor 工作流程

1. 扫描 `work/input/` 中的所有任务
2. 检查 `work/output/` 中是否已有结果（跳过已完成的）
3. 检查 `work/feedback/` 中是否有重试反馈
4. 执行任务（使用 coding-agent）
5. 自验证输出
6. 写入 `work/output/{task_id}.json`

---

## LLM 使用策略

| Agent | LLM | 用途 |
|-------|-----|------|
| DemandAnalyst | ✅ | 需求分析、拆解、结构化 |
| Architect | ✅ | 系统架构设计、模块划分 |
| DetailDesigner | ✅ | 任务拆分、依赖分析 |
| Tester | ✅ | 测试用例生成、测试报告 |
| **所有 Agent** | ReAct | 每个 LLM 输出都经过验证，不合格则重试 |

---

## 目录结构

```
lang-smart-factory/
├── README.md                    # 本文件
├── AGENTS.md                    # OpenClaw Agent 职责与交互协议
├── api_server.py               # REST API (port 5666)
├── cli.py                       # CLI: python cli.py run "<需求>" --project-id <id>
├── src/
│   ├── llm/
│   │   └── minimax_client.py    # MiniMax M2.7 客户端
│   ├── agents/
│   │   ├── demand_analyst.py    # 需求分析 (LLM + ReAct)
│   │   ├── architect.py         # 架构设计 (LLM + ReAct)
│   │   └── detail_designer.py   # 任务拆解 (LLM + ReAct)
│   ├── skills/
│   │   └── langflow_executor.py # OpenClaw 任务执行器
│   ├── workflows/
│   │   └── development_workflow.py  # 7节点工作流
│   ├── graph_state.py
│   └── models.py
├── workers/
│   └── task_coordinator.py      # 任务协调器（辅助）
├── docs/
│   ├── LANGFLOW_FACTORY_REQUIREMENTS.md  # 完整需求规格
│   ├── ARCHITECTURE.md          # 架构详细文档
│   └── DETAILED_DESIGN.md       # 详细设计文档
└── openclaw-knowledge/
    ├── README.md               # OpenClaw 工作区入口
    ├── AGENTS.md               # OpenClaw Agent 指南
    ├── skills/
    │   └── langflow-executor/  # Executor Skill
    │       └── SKILL.md
    └── workflows/
        └── LANGFLOW_WORKFLOW.md  # 工作流交互协议
```

---

## 使用方法

### CLI

```bash
python cli.py run "开发一个三国跑酷游戏" --project-id godot-trk-001
```

### API

```bash
curl -X POST http://localhost:5666/api/v1/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"requirement": "开发一个三国跑酷游戏", "project_id": "godot-trk-001"}'
```

### OpenClaw Agent

```bash
# 查看待处理任务
python3 -m src.skills.langflow_executor --dry-run

# 启动监控模式
python3 -m src.skills.langflow_executor --watch
```

---

## 与旧版本的区别

| 特性 | v1/v2 (旧) | v3 (当前) |
|------|-----------|----------|
| 代码生成 | Developer Agent + LLM | OpenClaw coding-agent |
| 任务队列 | Redis Stream / Consumer Group | 文件系统 |
| OpenClaw 集成 | 无 | Mode B 独立监控 |
| ReAct Loop | 无 | 全局验证，每个 LLM 环节都有 |
| 架构复杂度 | 高 (多 Agent + Redis) | 低 (3 Agent + 文件队列) |
