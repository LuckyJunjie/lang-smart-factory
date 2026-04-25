# Requirements


| id | project_id | title | description | priority | status | type | assigned_to | assigned_team | assigned_agent | taken_at | plan_step_id | plan_phase | step | progress_percent | created_at | updated_at | note | design_doc_path | acceptance_criteria | depends_on | project_name |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 1 | REQ-A: API健康检查 | 对API可用性检查 | P2 | in_progress | feature | newton | newton | newton | 2026-03-14T09:58:23.329598 | 24h |  | implement | 25 | 2026-03-12T17:18:37.034520 | 2026-03-17T15:34:07.255165 |  |  |  |  | smart-factory |
| 11 | 1 | REQ-B: 测试质量检查 | 测试环境检查 | P2 | new | feature | codeforge | newton |  | 2026-03-12T17:18:37.034520 | 24h |  | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:25.005405 |  |  |  |  | smart-factory |
| 12 | 1 | REQ-C: 部署与机器状态检查 | 部署流程检查 | P2 | new | feature | newton | newton |  | 2026-03-12T17:18:37.034520 | 24h |  | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:25.021633 |  |  |  |  | smart-factory |
| 13 | 1 | REQ-D: 文档与通信检查 | 文档通信流程检查 | P2 | new | feature | tesla | newton |  | 2026-03-12T17:18:37.034520 | 24h |  | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:25.044858 |  |  |  |  | smart-factory |
| 1 | 2 | pinball 0.1-0.5 | 基础功能开发 | P0 | in_progress | feature | tesla | tesla |  | 2026-03-12T17:18:37.034520 | 0.1 | baseline | test | 0 | 2026-03-12T17:18:37.034520 | 2026-03-20T11:18:44.016700 |  |  |  |  | pinball-experience |
| 2 | 2 | Step 0.1 | Baseline 0.1 | P0 | done | feature |  |  |  | 2026-03-12T17:18:37.034520 | 0.1 | baseline | done | 100 | 2026-03-12T17:18:37.034520 | 2026-03-12T17:18:37.034520 |  |  |  |  | pinball-experience |
| 3 | 2 | Step 0.2 | Baseline 0.2 | P0 | done | feature |  |  |  | 2026-03-12T17:18:37.034520 | 0.2 | baseline | done | 100 | 2026-03-12T17:18:37.034520 | 2026-03-12T17:18:37.034520 |  |  |  |  | pinball-experience |
| 4 | 2 | Step 0.3 | Baseline 0.3 | P0 | done | feature |  |  |  | 2026-03-12T17:18:37.034520 | 0.3 | baseline | done | 100 | 2026-03-12T17:18:37.034520 | 2026-03-12T17:18:37.034520 |  |  |  |  | pinball-experience |
| 5 | 2 | Step 0.4 | Baseline 0.4 | P0 | done | feature |  |  |  | 2026-03-12T17:18:37.034520 | 0.4 | baseline | done | 100 | 2026-03-12T17:18:37.034520 | 2026-03-12T17:18:37.034520 |  |  |  |  | pinball-experience |
| 6 | 2 | Step 0.5 | Baseline 0.5 | P0 | done | feature |  |  |  | 2026-03-12T17:18:37.034520 | 0.5 | baseline | done | 100 | 2026-03-12T17:18:37.034520 | 2026-03-12T17:18:37.034520 |  |  |  |  | pinball-experience |
| 7 | 2 | Step 0.6 | Baseline 0.6 | P0 | new | feature |  | newton |  | 2026-03-12T17:18:37.034520 | 0.6 | baseline | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:24.947359 |  |  |  |  | pinball-experience |
| 8 | 2 | Step 0.7 | Baseline 0.7 | P1 | new | feature |  | newton |  | 2026-03-12T17:18:37.034520 | 0.7 | baseline | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:24.970595 |  |  |  |  | pinball-experience |
| 9 | 2 | Step 0.8 | Baseline 0.8 | P1 | new | feature |  | newton |  | 2026-03-12T17:18:37.034520 | 0.8 | baseline | not start | 0 | 2026-03-12T17:18:37.034520 | 2026-03-17T22:04:24.990542 |  |  |  |  | pinball-experience |
| 21 | 2 | 创建 pinball 场景文件 (main.tscn, start_screen.tscn, game_over.tscn) | 为 pinball-experience 项目创建基础场景文件，供 Tesla 团队开发使用 | P0 | new | feature |  | newton |  |  |  |  | not start | 0 | 2026-03-19 15:57:25 | 2026-03-20T00:00:56.397644 |  |  |  |  | pinball-experience |
| 14 | 3 | 持仓管理功能 | F1.1 持仓数据录入, F1.2 持仓数据校验, F1.3 持仓快照 | P0 | done | feature |  | tesla | einstein | 2026-03-16T13:09:50.870763 |  |  | done | 100 | 2026-03-16 00:34:42 | 2026-03-16T22:55:41.865989 |  |  |  |  | stock-analyzer |
| 15 | 3 | 监控列表管理 | F2.1 监控列表配置, F2.2 列表同步 | P0 | done | feature |  | newton | einstein | 2026-03-16T13:51:28.093074 |  |  | done | 100 | 2026-03-16 00:34:46 | 2026-03-16T22:55:45.130099 |  |  |  |  | stock-analyzer |
| 16 | 3 | 数据自动收集模块 | F3.1 公司信息采集, F3.2 宏观数据采集, F3.3 增量更新, F3.4 采集容错 | P0 | done | feature |  | newton | einstein | 2026-03-16T14:44:46.712029 |  |  | implement | 100 | 2026-03-16 00:34:51 | 2026-03-17T00:03:17.201357 |  |  |  |  | stock-analyzer |
| 17 | 3 | 数据处理与存储 | F4.1 数据清洗, F4.2 数据补全, F4.3 数据存储, F4.4 数据版本 | P0 | done | feature |  | newton |  |  |  |  | implement | 100 | 2026-03-16 00:34:55 | 2026-03-17T00:03:17.264069 |  |  |  |  | stock-analyzer |
| 18 | 3 | 分析与预测模块 | F5.1 指标计算, F5.2 预测模型, F5.3 模型管理, F5.4 置信区间 | P1 | done | feature |  | newton |  |  |  |  | implement | 100 | 2026-03-16 00:34:59 | 2026-03-17T00:03:17.322708 |  |  |  |  | stock-analyzer |
| 19 | 3 | 告警与报告输出 | F6.1 告警规则引擎, F6.2 实时告警, F6.3 每日报告 | P1 | done | feature |  | newton |  |  |  |  | implement | 100 | 2026-03-16 00:35:04 | 2026-03-17T00:03:17.368914 |  |  |  |  | stock-analyzer |
| 20 | 3 | 系统监控与自愈 | F7.1 任务监控, F7.2 资源监控, F7.3 自启动与恢复 | P1 | done | feature |  | newton |  |  |  |  | implement | 100 | 2026-03-16 00:35:09 | 2026-03-17T00:03:17.409798 |  |  |  |  | stock-analyzer |
