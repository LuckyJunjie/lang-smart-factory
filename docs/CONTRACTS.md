# Contract 定义文档

## 概述

每个节点的输入输出都通过 JSON Schema 定义，确保类型安全和数据完整性。

## GraphState Schema

```json
{
  "type": "object",
  "properties": {
    "project_id": {"type": "string"},
    "requirement_id": {"type": "string"},
    "current_step": {
      "type": "string",
      "enum": ["trigger", "analysis", "architecture", "detail_design", "dispatch", "implementation", "testing", "gameplay_eval", "acceptance", "release"]
    },
    "raw_requirement": {"type": "string"},
    "structured_requirements": {"type": "array"},
    "acceptance_criteria": {"type": "array"},
    "architecture_doc": {"type": "object"},
    "detailed_tasks": {"type": "array"},
    "artifacts": {"type": "object"},
    "execution_trace": {"type": "array"},
    "approval_status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
    "approval_comment": {"type": "string"}
  },
  "required": ["project_id", "current_step"]
}
```

## ExecutionResult Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "status": {"type": "string", "enum": ["success", "failed", "blocked"]},
    "commit_id": {"type": "string"},
    "test_results": {
      "type": "object",
      "properties": {
        "passed": {"type": "integer"},
        "failed": {"type": "integer"}
      }
    },
    "artifacts": {"type": "array"},
    "token_usage": {"type": "object"}
  },
  "required": ["task_id", "status"]
}
```

## TestReport Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "passed": {"type": "integer"},
    "failed": {"type": "integer"},
    "logs": {"type": "string"},
    "screenshots": {"type": "array"}
  }
}
```

## GameEvalReport Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "fun_rating": {"type": "integer", "minimum": 1, "maximum": 5},
    "control_feel": {"type": "string", "enum": ["responsive", "sluggish"]},
    "visual_feedback_quality": {"type": "string", "enum": ["good", "poor"]},
    "difficulty_balance": {"type": "string", "enum": ["too_easy", "appropriate", "too_hard"]},
    "suggestions": {"type": "array", "items": {"type": "string"}},
    "bugs": {"type": "array", "items": {"type": "string"}}
  }
}
```

## 阶段 Contract 汇总

| 阶段 | 输入 Schema | 输出 Schema | 验证方法 |
|------|------------|----------------------|----------|
| 需求分析 | RawText | StructuredRequirements | 检查是否所有需求创建成功 |
| 架构设计 | StructuredRequirements | ArchitectureDoc | 静态分析模块覆盖 |
| 详细设计 | Architecture | DetailedTasks | 验证任务图覆盖所有验收项 |
| 实现 | Task | ExecutionResult | 单元测试全部通过 |
| 测试 | Task + Build | TestReport | 用例通过率 100% |
| 游戏性评估 | GameTask | GameEvalReport | fun_rating≥4 |
| CI/CD | 全部通过 | ReleaseArtifact | 构建成功 |
