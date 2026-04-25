# 假想项目：OpenClaw 协作平台（协调能力测试）

## 目的

在 Smart Factory 中预置一个**假想产品 Backlog**，用于验证 OpenClaw 集群的协作流程：

- **需求分配**：项目管理 Agent 从 Backlog 识别高优先级需求并分配给对应团队。
- **任务分解**：各团队架构师将需求拆解为可执行任务并明确依赖。
- **跨团队协作**：多团队需求（如 WebSocket、飞书集成）的任务分配与进度同步。
- **风险上报**：在预设风险点，Scrum Master/架构师向 Program Manager 上报，并验证协调闭环。
- **汇总上报**：迭代结束后各团队提交完成清单，Program Manager 生成飞书报告。

## 项目与数据位置

- **项目名称：** OpenClaw 协作平台  
- **数据库：** Smart Factory `core/db/factory.db`，项目 `projects.id = 3`  
- **需求：** 15 条迭代需求（`plan_phase = 'iteration'`，`plan_step_id = '1'`～`'15'`），状态 `new`，未分配 `assigned_team`  
- **任务：** 每条需求下已拆解 2～3 个子任务，`executor` 标注建议执行方（前端/后端/数据库/运维/测试团队）

## 迭代与风险点概要

| 迭代 | 主题             | 预设风险触发点 |
|------|------------------|----------------|
| 1    | 用户认证基础     | 数据库选型 → 数据库团队上报，PM 协调技术调研 |
| 2    | 项目与看板模型   | 权限设计复杂 → 后端架构师上报，PM 组织设计评审 |
| 3    | 任务卡片基础功能 | 前端拖拽库兼容性 → 前端架构师上报，PM 安排预研 |
| 4    | 任务分配与成员管理 | 无预设风险（正常流程） |
| 5    | 实时协作 WebSocket | 后端学习成本 → SM 上报，PM 协调培训/引入库 |
| 6    | 风险跟踪模块     | 状态流转与任务系统关联 → 后端上报，PM 协调产品确认 |
| 7    | 飞书集成基础     | API 限频 → 后端上报，PM 联系飞书技术支持 |
| 8    | 迭代报表生成     | 统计性能 → 数据库团队上报，PM 安排索引优化 |
| 9    | 搜索功能         | ES 运维复杂度 → 运维上报，PM 决策 LIKE 或 ES |
| 10   | 通知中心         | SMTP 不稳定 → 后端上报，PM 协调备用服务 |
| 11   | 性能优化（缓存） | 缓存一致性 → 后端架构师上报，PM 组织设计评审 |
| 12   | 安全性增强       | 限流误伤 → 测试团队上报，PM 协调灰度发布 |
| 13   | 移动端适配       | 组件库移动端样式 → 前端架构师上报，PM 安排修复 |
| 14   | 多语言 i18n      | 翻译资源缺失 → 前端 SM 上报，PM 联系翻译团队 |
| 15   | 插件系统原型     | 沙箱安全 → 测试团队上报，PM 组织安全评审 |

## 如何重新录入

若需清空后重新录入（例如在新环境）：

1. 在 DB 中删除该项目下需求与任务（或删除项目再建）  
2. 执行：
   ```bash
   cd workspace/implementation/smart-factory
   python3 openclaw-knowledge/scripts/seed_openclaw_collab_platform.py [--db PATH] [--init]
   ```
   `--init` 仅在 DB 文件不存在时创建并执行 schema。若该项目下已有 `plan_phase='iteration'` 的需求，脚本会跳过插入。

## 相关文档

- 流程与角色：见需求文档中的「团队结构」「项目管理与协调角色」「风险上报与处理流程」「汇总上报机制」  
- API：`workspace/implementation/docs/REQUIREMENTS.md`  
- Flow：`OPENCLAW_DEVELOPMENT_FLOW.yaml`
