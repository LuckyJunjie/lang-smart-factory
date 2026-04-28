# LangFlow Factory — OpenClaw Agent 交互协议

**适用对象**：einstein、curie、galileo、darwin、hawking 等 OpenClaw 编码代理

---

## 系统角色

| 角色 | 系统 | 职责 |
|------|------|------|
| **Newton (LangFlow Factory)** | LangFlow Factory | 编排、分析、设计、验证 |
| **OpenClaw Agents** | OpenClaw | 监控、执行、编码 |

LangFlow Factory 和 OpenClaw 是**两个独立系统**，通过文件系统通信。

---

## OpenClaw Agent 职责

### 核心任务

1. **监控** `work/input/` 目录，发现新任务
2. **执行** 任务（使用 coding-agent: Claude Code 或 Codex）
3. **自验证** 输出是否符合 acceptance_criteria
4. **写入** 结果到 `work/output/{task_id}.json`
5. **处理重试** 读取 `work/feedback/` 中的反馈，重新执行

### 任务生命周期

```
1. Newton 写入任务 → work/input/{task_id}.json
2. OpenClaw 读取任务
3. OpenClaw 执行（coding-agent）
4. OpenClaw 自验证
5. OpenClaw 写入结果 → work/output/{task_id}.json
6. Newton 验证结果
   ├─ 通过 → 下一任务
   └─ 失败 → 写入 feedback → OpenClaw 重试（最多3次）
```

---

## 文件通信协议

### 工作目录

```
/home/pi/.openclaw/workspace/{project_id}/work/
├── input/       # Newton → OpenClaw
├── output/      # OpenClaw → Newton
└── feedback/    # Newton → OpenClaw (重试)
```

### 任务文件 (input/{task_id}.json)

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

### 结果文件 (output/{task_id}.json)

```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_file": "/home/pi/.openclaw/workspace/godot-trk-001/src/MainMenu.ts",
  "errors": [],
  "completed_at": "2026-04-28T10:05:00Z"
}
```

### 反馈文件 (feedback/{task_id}_feedback_N.json)

```json
{
  "task_id": "task_001",
  "attempt": 1,
  "errors": ["主菜单未居中显示"],
  "acceptance_criteria": ["主菜单显示在屏幕中央"],
  "suggestion": "使用 CenterContainer 包裹主菜单节点"
}
```

---

## ReAct 重试流程

OpenClaw 执行任务时，如果发现 `work/feedback/` 中有对应任务的反馈文件，需要：

1. **读取反馈** — 了解上次失败原因
2. **分析错误** — 理解 acceptance_criteria 未满足的点
3. **修正执行** — 根据 suggestion 修复问题
4. **重新验证** — 确保修复后满足验收标准
5. **写入结果** — 覆盖旧的 output 文件

```
attempt 1 → 失败 → feedback_1.json
    ↓
attempt 2 → 读取 feedback_1 → 修复 → 执行 → 失败 → feedback_2.json
    ↓
attempt 3 → 读取 feedback_2 → 修复 → 执行 → 成功 → output.json
```

---

## 自验证清单

在写入 output 之前，OpenClaw 必须确认：

- [ ] 输出文件已创建
- [ ] 代码可编译/可运行（无语法错误）
- [ ] 所有 acceptance_criteria 都已实现
- [ ] 没有未处理的错误

---

## Cron 设置

```bash
# 每5分钟检查一次新任务
*/5 * * * * cd /home/pi/.openclaw/workspace/lang-smart-factory && python3 -m src.skills.langflow_executor >> /tmp/langflow_executor.log 2>&1
```

---

## 命令行工具

```bash
# 扫描待处理任务（不执行）
python3 -m src.skills.langflow_executor --dry-run

# 执行所有待处理任务
python3 -m src.skills.langflow_executor

# 持续监控（后台运行）
python3 -m src.skills.langflow_executor --watch

# 只处理指定项目
python3 -m src.skills.langflow_executor --project godot-trk-001
```

---

## 注意事项

1. **不删除 input 文件** — Newton 需要参考
2. **不覆盖未完成的 output** — 避免 Newton 读到损坏结果
3. **每次重试都包含 feedback** — 帮助自己理解上次的问题
4. **日志记录** — 在 output 中包含 errors 数组，方便 Newton 诊断
5. **超时处理** — 如果执行时间超过 5 分钟，先写部分结果再继续

---

## 与 Newton 通信

- **不直接发消息给 Newton** — 所有通信通过文件
- **完成所有任务后** — Newton 会自动收到 Feishu 通知
- **紧急问题** — 在福渊研发部 飞书群联系 Newton
