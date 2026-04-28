# LangFlow Factory 详细设计文档

**版本:** 1.0
**更新:** 2026-04-28

---

## 1. 节点定义

### 1.1 trigger 节点

**功能**: 接收用户输入，初始化 GraphState

```python
def trigger_node(state: GraphState) -> GraphState:
    return {
        "project_id": generate_project_id(),
        "requirement_id": generate_requirement_id(),
        "original_requirement": state["original_requirement"],
        "status": "running",
        "current_step": "analyze",
        "execution_trace": [{
            "node": "trigger",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }]
    }
```

### 1.2 analyze 节点 (DemandAnalyst)

**功能**: 解析自然语言需求，生成结构化 Requirements

```python
def analyze_node(state: GraphState) -> GraphState:
    prompt = ANALYST_SYSTEM_PROMPT.format(
        requirement=state["original_requirement"]
    )
    result = llm.invoke(prompt)
    requirements = parse_json(result)
    
    return {
        "requirements": requirements,
        "current_step": "architect",
        "execution_trace": state["execution_trace"] + [{
            "node": "analyze",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "output": requirements
        }]
    }
```

### 1.3 architect 节点 (Architect)

**功能**: 根据需求生成系统架构设计

```python
def architect_node(state: GraphState) -> GraphState:
    prompt = ARCHITECT_SYSTEM_PROMPT.format(
        requirements=json.dumps(state["requirements"], ensure_ascii=False)
    )
    result = llm.invoke(prompt)
    architecture = parse_json(result)
    
    return {
        "architecture": architecture,
        "current_step": "detail_design",
        "execution_trace": state["execution_trace"] + [{
            "node": "architect",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "output": architecture
        }]
    }
```

### 1.4 detail_design 节点 (DetailDesigner)

**功能**: 生成详细设计文档和任务列表

```python
def detail_design_node(state: GraphState) -> GraphState:
    prompt = DESIGNER_SYSTEM_PROMPT.format(
        architecture=json.dumps(state["architecture"], ensure_ascii=False)
    )
    result = llm.invoke(prompt)
    design_output = parse_json(result)
    
    return {
        "tasks": design_output["tasks"],
        "test_cases": design_output["test_cases"],
        "current_step": "dispatch",
        "execution_trace": state["execution_trace"] + [{
            "node": "detail_design",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "output": design_output
        }]
    }
```

### 1.5 dispatch 节点

**功能**: 将任务派发到 Redis 队列

```python
def dispatch_node(state: GraphState) -> GraphState:
    for task in state["tasks"]:
        job = {
            "job_id": f"{state['project_id']}_{task['task_id']}",
            "type": "implement",
            "project_id": state["project_id"],
            "task": task,
            "context": {
                "requirements": state["requirements"],
                "architecture": state["architecture"]
            },
            "created_at": datetime.now().isoformat()
        }
        redis.lpush("tasks", json.dumps(job, ensure_ascii=False))
    
    return {
        "current_step": "implement",
        "execution_trace": state["execution_trace"] + [{
            "node": "dispatch",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "dispatched_tasks": len(state["tasks"])
        }]
    }
```

### 1.6 implement 节点 (Developer)

**功能**: 从队列消费任务并执行代码实现

```python
def implement_node(state: GraphState) -> GraphState:
    # Worker 模式: 阻塞等待任务
    while True:
        job_json = redis.brpop("tasks", timeout=300)
        if job_json:
            job = json.loads(job_json[1])
            # 执行代码生成
            code = generate_code(job["task"], job["context"])
            artifacts.append(code)
    
    return {
        "code_artifacts": artifacts,
        "current_step": "test",
        "execution_trace": state["execution_trace"] + [{
            "node": "implement",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }]
    }
```

### 1.7 test 节点 (Tester)

**功能**: 执行测试并生成报告

```python
def test_node(state: GraphState) -> GraphState:
    prompt = TESTER_SYSTEM_PROMPT.format(
        artifacts=json.dumps(state["code_artifacts"], ensure_ascii=False),
        test_cases=json.dumps(state["test_cases"], ensure_ascii=False)
    )
    result = llm.invoke(prompt)
    test_report = parse_json(result)
    
    return {
        "test_report": test_report,
        "current_step": "accept",
        "execution_trace": state["execution_trace"] + [{
            "node": "test",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "output": test_report
        }]
    }
```

### 1.8 accept 节点

**功能**: 人工审批确认

```python
def accept_node(state: GraphState) -> GraphState:
    # 发送飞书审批卡片
    feishu.send_approval_card(state)
    
    # 等待审批结果 (可通过回调 API 更新)
    return state  # 实际状态由外部 API 更新
```

### 1.9 release 节点

**功能**: 交付最终产物

```python
def release_node(state: GraphState) -> GraphState:
    # 打包产物、清理资源
    return {
        "status": "completed",
        "current_step": "release",
        "execution_trace": state["execution_trace"] + [{
            "node": "release",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }]
    }
```

---

## 2. Agent Prompt 模板

### 2.1 DemandAnalyst Prompt

```
你是一个资深需求分析师。请分析以下用户需求，生成结构化需求文档。

## 用户需求
{requirement}

## 输出要求
请生成 JSON 格式的需求文档，包含以下字段：
- summary: 需求摘要
- type: 项目类型 (game/application)
- features: 核心功能列表
- constraints: 约束条件
- target_platform: 目标平台
- tech_stack: 技术栈建议

请只输出 JSON，不要其他内容。
```

### 2.2 Architect Prompt

```
你是一个系统架构师。请根据需求文档设计系统架构。

## 需求文档
{requirements}

## 输出要求
请生成 JSON 格式的架构文档，包含：
- overview: 架构概述
- modules: 模块划分
- tech_stack: 技术选型
- data_model: 数据模型
- api_design: API 设计

请只输出 JSON，不要其他内容。
```

### 2.3 DetailDesigner Prompt

```
你是详细设计师。请根据���构��档进行任务拆解。

## 架构文档
{architecture}

## 输出要求
请生成 JSON，包含：
- tasks: 任务列表，每项包含 task_id, title, description, priority
- test_cases: 测试用例列表，每项包含 case_id, title, steps, expected

请只输出 JSON，不要其他内容。
```

### 2.4 Developer Prompt

```
你是资开发工程师。请根据任务要求实现代码。

## 任务
{task}

## 上下文
{context}

## 要求
- 生成完整、可运行的代码
- 包含必要的配置文件
- 遵循最佳实践

请只输出代码，不要其他解释。
```

### 2.5 Tester Prompt

```
你是测试工程师。请执行测试并生成报告。

## 代码产物
{artifacts}

## 测试用例
{test_cases}

## 输出要求
请生成 JSON 格式的测试报告：
- summary: 测试摘要
- passed: 通过的用例
- failed: 失败的用例
- issues: 发现的问题

请只输出 JSON，不要其他内容。
```

---

## 3. 数据 Schema

### 3.1 GraphState

```python
from typing import TypedDict, NotRequired
from datetime import datetime

class TraceEntry(TypedDict):
    node: str
    timestamp: str
    status: str
    output: NotRequired[dict]

class GraphState(TypedDict):
    # 核心 ID
    project_id: str
    requirement_id: str
    
    # 输入
    original_requirement: str
    
    # 中间产物
    requirements: NotRequired[dict]
    architecture: NotRequired[dict]
    tasks: NotRequired[list[dict]]
    test_cases: NotRequired[list[dict]]
    code_artifacts: NotRequired[list[dict]]
    test_report: NotRequired[dict]
    
    # 执行追踪
    execution_trace: list[TraceEntry]
    
    # 状态
    current_step: str
    status: str  # pending/running/completed/failed
```

### 3.2 Requirements Schema

```python
class Requirements(TypedDict):
    summary: str                    # "开发一个三国跑酷游戏"
    type: str                       # "game" | "application"
    features: list[str]             # ["角色奔跑", "障碍物", "积分系统"]
    constraints: list[str]          # ["移动端", "单文件"]
    target_platform: str            # "iOS/Android/Web"
    tech_stack: list[str]          # ["Unity/Cocos/原生"]
```

### 3.3 Task Schema

```python
class Task(TypedDict):
    task_id: str                    # "task_001"
    title: str                      # "实现主菜单"
    description: str                # "创建游戏主菜单界面"
    priority: str                   # "high" | "medium" | "low"
    assignee: NotRequired[str]     # "Developer"
    status: str                     # "pending" | "in_progress" | "completed"
```

### 3.4 TestCase Schema

```python
class TestCase(TypedDict):
    case_id: str                    # "tc_001"
    title: str                      # "登录功能测试"
    steps: list[str]               # ["输入用户名", "输入密码", "点击登录"]
    expected: str                   # "登录成功，跳转首页"
    priority: str                   # "high" | "medium" | "low"
```

### 3.5 CodeArtifact Schema

```python
class CodeArtifact(TypedDict):
    artifact_id: str                # "art_001"
    task_id: str                    # 对应的任务 ID
    file_path: str                  # "src/main.js"
    content: str                    # 代码内容
    language: str                   # "javascript"
    created_at: str                 # ISO timestamp
```

---

## 4. API 规范

### 4.1 项目管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects` | 列出项目 |
| GET | `/api/v1/projects/{project_id}` | 获取项目详情 |
| DELETE | `/api/v1/projects/{project_id}` | 删除项目 |

### 4.2 需求管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/projects/{project_id}/requirements` | 提交需求 |
| GET | `/api/v1/projects/{project_id}/requirements/{req_id}` | 获取需求 |
| PUT | `/api/v1/projects/{project_id}/requirements/{req_id}` | 更新需求 |

### 4.3 执行控制

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/projects/{project_id}/start` | 启动执行 |
| POST | `/api/v1/projects/{project_id}/approve` | 审批通过 |
| POST | `/api/v1/projects/{project_id}/reject` | 审批拒绝 |
| GET | `/api/v1/projects/{project_id}/status` | 获取状态 |
| GET | `/api/v1/projects/{project_id}/trace` | 获取执行追踪 |

### 4.4 产物管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/projects/{project_id}/artifacts` | 列出产物 |
| GET | `/api/v1/projects/{project_id}/artifacts/{artifact_id}` | 下载产物 |
| GET | `/api/v1/projects/{project_id}/test-report` | 获取测试报告 |

### 4.5 请求/响应示例

**POST /api/v1/projects**
```json
// Request
{
  "name": "三国跑酷游戏",
  "description": "开发一个三国主题的跑酷游戏"
}

// Response
{
  "project_id": "proj_abc123",
  "name": "三国跑酷游戏",
  "status": "pending",
  "created_at": "2026-04-28T10:00:00Z"
}
```

**POST /api/v1/projects/{project_id}/requirements**
```json
// Request
{
  "requirement": "开发一个三国跑酷游戏"
}

// Response
{
  "requirement_id": "req_xyz789",
  "status": "accepted",
  "created_at": "2026-04-28T10:00:01Z"
}
```

---

## 5. Worker 协议

### 5.1 Worker 启动

```bash
python -m worker --queue tasks --worker-id worker_001
```

### 5.2 任务消费流程

```
1. Worker 启动，连接 Redis
2. 执行 BRPOP tasks 等待任务
3. 收到任务后解析 JSON
4. 调用 Developer Agent 生成代码
5. 将产物存储到本地/云存储
6. 通过 PUBLISH task_completed 通知主流程
7. 继续等待下一个任务
```

### 5.3 任务消息格式

```json
{
  "job_id": "proj_xxx_task_001",
  "type": "implement",
  "project_id": "proj_xxx",
  "task": {
    "task_id": "task_001",
    "title": "实现主菜单",
    "description": "创建游戏主菜单界面",
    "priority": "high"
  },
  "context": {
    "requirements": {
      "summary": "三国跑酷游戏",
      "type": "game",
      "features": ["角色奔跑", "障碍物", "道具系统"],
      "target_platform": "iOS/Android"
    },
    "architecture": {
      "modules": ["GameEngine", "UI", "Audio"],
      "tech_stack": ["Cocos Creator", "TypeScript"]
    }
  },
  "created_at": "2026-04-28T10:00:00Z"
}
```

### 5.4 完成事件格式

```json
{
  "event": "task_completed",
  "job_id": "proj_xxx_task_001",
  "project_id": "proj_xxx",
  "status": "success",
  "artifacts": [
    {
      "artifact_id": "art_001",
      "file_path": "src/scenes/Menu.ts",
      "size": 1234
    }
  ],
  "completed_at": "2026-04-28T10:05:00Z"
}
```

---

## 6. 配置

### 6.1 环境变量

```bash
# LLM
MINIMAX_API_KEY=your_api_key
MINIMAX_BASE_URL=https://api.minimax.chat/v1

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 飞书
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 6.2 配置文件 (config.yaml)

```yaml
llm:
  model: MiniMax-M2.7
  temperature: 0.7
  max_tokens: 8192

redis:
  host: localhost
  port: 6379
  queue_name: tasks

api:
  host: 0.0.0.0
  port: 8000

feishu:
  webhook_url: "https://open.feishu.cn/..."

workflow:
  max_retries: 3
  timeout: 600
```

---

## 7. 全局 ReAct 验证环

ReAct (Reasoning + Acting) 贯穿所有 LLM 环节，每个 Agent 的输出都经过验证，不合格则重试。

### 7.1 ReAct 循环定义

```python
def react_loop(agent_func, input_data, max_retries=3):
    """
    通用 ReAct 循环。
    执行 agent_func(input_data)，验证输出，不合格则反馈重试。
    """
    for attempt in range(max_retries):
        result = agent_func(input_data)
        
        # 验证输出
        is_valid, errors = validate(result)
        
        if is_valid:
            return result
        
        if attempt < max_retries - 1:
            # 将错误反馈给 Agent，重新生成
            feedback = {
                "attempt": attempt + 1,
                "errors": errors,
                "suggestion": generate_suggestion(errors, result)
            }
            input_data["_feedback"] = feedback
            print(f"[ReAct] Attempt {attempt+1} failed: {errors}, retrying...")
    
    # 超过最大重试次数，返回最后结果（标记为部分成功）
    result["_react_status"] = "max_retries_exceeded"
    return result
```

### 7.2 各环节 ReAct 验证点

| 环节 | 验证函数 | 失败标准 |
|------|----------|----------|
| DemandAnalyst | `validate_requirements()` | JSON 格式错误、缺少必填字段、priority 无效 |
| Architect | `validate_architecture()` | 模块缺失、循环依赖、架构不合理 |
| DetailDesigner | `validate_tasks()` | 任务覆盖不完整、依赖有环、估计工时缺失 |
| OpenClaw 执行 | `verify_output()` | acceptance_criteria 未满足、文件不存在 |

### 7.3 validate_requirements 实现

```python
def validate_requirements(requirements) -> tuple[bool, list]:
    """验证结构化需求是否符合规格"""
    errors = []
    
    if not isinstance(requirements, list):
        errors.append("requirements must be a list")
        return False, errors
    
    required_fields = ["id", "title", "type", "priority", "description", "acceptance_criteria"]
    valid_types = ["feature", "performance", "ux", "security"]
    valid_priorities = ["high", "medium", "low"]
    
    for i, req in enumerate(requirements):
        for field in required_fields:
            if field not in req:
                errors.append(f"REQ[{i}] missing field: {field}")
        
        if req.get("type") not in valid_types:
            errors.append(f"REQ[{i}] invalid type: {req.get('type')}")
        
        if req.get("priority") not in valid_priorities:
            errors.append(f"REQ[{i}] invalid priority: {req.get('priority')}")
        
        if not isinstance(req.get("acceptance_criteria", []), list):
            errors.append(f"REQ[{i}] acceptance_criteria must be list")
    
    return len(errors) == 0, errors
```

### 7.4 verify_output 实现

```python
def verify_output(result: dict, task: dict) -> tuple[bool, list]:
    """验证 OpenClaw 输出是否符合 acceptance_criteria"""
    errors = []
    
    # 检查状态
    if result.get("status") != "completed":
        errors.append(f"Task status is {result.get('status')}, expected completed")
    
    # 检查输出文件存在
    output_file = result.get("output_file")
    if output_file and not os.path.exists(output_file):
        errors.append(f"Output file does not exist: {output_file}")
    
    # 检查错误日志
    if result.get("errors"):
        errors.extend(result["errors"])
    
    return len(errors) == 0, errors
```

### 7.5 ReAct 集成到 DemandAnalyst

```python
class DemandAnalyst:
    def process(self, state: Dict) -> Dict:
        requirement = state.get("raw_requirement", "")
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(requirement=requirement)
        
        # 使用 ReAct 循环
        result = react_loop(self._call_llm, prompt)
        
        try:
            requirements = json.loads(result["content"])
            is_valid, errors = validate_requirements(requirements)
            
            if not is_valid:
                state["_react_feedback"] = {"errors": errors}
                # 下次调用时会带上 feedback
            
            state["structured_requirements"] = requirements
        except json.JSONDecodeError:
            state["error"] = "Failed to parse requirements JSON"
        
        state["current_step"] = "architect"
        return state
```

### 7.6 ReAct Loop 数据流

```
Agent 生成输出
      ↓
validate(output)
      ↓
 ┌───┴───┐
Pass    Fail → 写 feedback → Agent 读取 feedback → 重新生成
                                ↑                        │
                                └────────────────────────┘
                          (最多 3 次重试)
```

---

*详细设计版本: 2.0 | 适用于 LangFlow Factory v3.0*

## 8. OpenClaw Agent 集成 (Mode B)

### 8.1 任务文件格式

见 README.md 和 AGENTS.md。

### 8.2 Executor 入口

```bash
python3 -m src.skills.langflow_executor --watch  # 持续监控
python3 -m src.skills.langflow_executor --project <id>  # 单项目
python3 -m src.skills.langflow_executor --dry-run  # 预览不执行
```

### 8.3 OpenClaw Cron 配置

```cron
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m src.skills.langflow_executor >> /tmp/langflow_executor.log 2>&1
```

---

*详细设计版本: 2.0 | 适用于 LangFlow Factory v3.0*