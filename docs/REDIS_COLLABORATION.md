# Redis 协作：技术架构与使用指南

> 版本: 1.1 | 更新日期: 2026-04-08  
> **配套**：[REQUIREMENTS.md](./REQUIREMENTS.md)（HTTP API）、[OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)、[OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)  
> **范围**：本文描述 **多设备 Vanguard 协调** 下的 Redis 主路径。**单团队独立闭环**（领导直派、无跨机协调必选）见 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)，**不要求**按本文部署消费组即可交付。

OpenClaw **多设备**之间的 **项目管理、任务分发、任务协调、执行状态上报** 以 **Redis** 为主路径：**Redis Pub/Sub** 做实时信号，**Redis Streams** 做可持久化、可 ACK 的任务与结果队列。Smart Factory **HTTP API** 负责项目/需求/任务等 **持久化与查询**，并在 Redis 不可用时作为 **降级（fallback）** 协作手段（见 [REQUIREMENTS.md §4.5](./REQUIREMENTS.md)）。

---

## 1. 部署拓扑

| 节点 | 角色 | 说明 |
|------|------|------|
| **vanguard001 设备**（树莓派，默认 `192.168.3.75`，与 [ORGANIZATION.md](./ORGANIZATION.md) 一致） | **Redis Server + Smart Factory API 宿主** | 运行 **`redis-server`** 与 **`core/api/server.py`（Flask）**。全厂通过 **`REDIS_URI`** 连 Redis，通过 **`SMART_FACTORY_API`**（如 `http://192.168.3.75:5000/api`）读写项目/需求/任务；详见 [REQUIREMENTS.md](./REQUIREMENTS.md) 文首「API 服务部署」。 |
| **其余设备**（Jarvis、CodeForge、Tesla、Newton、Hera 等） | **Redis Client + API 远程客户端** | 订阅/消费 Redis；**不**在本机托管 Smart Factory API（开发机本地可起临时 API 仅作自担风险调试）。 |

环境变量（建议统一）：

- `REDIS_URI` — 例如 `redis://192.168.3.75:6379`（生产应配密码与 TLS，按运维策略）
- `SMART_FACTORY_API` — 指向 vanguard001 上 API 的 **`/api` 基地址**（与各团队 **cli project** / project-mcp 一致）
- 应用内前缀固定为下文 `smartfactory`（与 YAML / 通信文档一致）

---

## 2. 键空间与职责一览

统一前缀：**`smartfactory`**

### 2.1 Pub/Sub 频道（即时通知）

| 频道名 | 用途 |
|--------|------|
| `smartfactory:task:dispatch` | Vanguard 侧：**任务已派发**（通知各团队立刻拉流或处理） |
| `smartfactory:task:blocker` | 执行侧：**阻塞/需决策**（Hera 等订阅） |
| `smartfactory:agent:heartbeat` | **机器/代理存活与心跳**（低延迟在线信号；需 **按时** 发布，见 §5） |

### 2.2 Streams（持久化队列）

| Stream | 用途 |
|--------|------|
| `smartfactory:stream:tasks` | 任务队列：派发 payload、assignee、关联 requirement/task id |
| `smartfactory:stream:results` | 结果与进度：完成、失败、进度百分比、摘要 |
| `smartfactory:stream:blockers` | 阻塞单持久化副本，便于 Hera 消费组重放 |

生产消费须使用 **Consumer Group**（`XGROUP CREATE`、`XREADGROUP`），处理完毕后 **`XACK`**。规范化消费组名称（与 `OPENCLAW_DEVELOPMENT_FLOW.yaml` 中 `redis.consumer_groups` 一致）：

| 逻辑角色 | Consumer group 名 | 典型消费者 |
|----------|-------------------|------------|
| 开发团队 | `dev-teams` | jarvis, codeforge, dinosaur |
| 测试团队 | `test-teams` | tesla, newton |
| 阻塞决策 | `hera-group` | hera |

> 实现侧应保证：**同一 stream 上各消费组名称与生产环境配置一致**，否则会出现重复消费或无人消费。

---

## 3. 消息形态（约定）

以下为 **逻辑 JSON**；写入 Redis 时通常为 **单字段** `payload` 存 JSON 字符串，或按团队脚手架约定的字段名（与 OpenClaw `redis-events` 插件一致即可）。

### 3.1 派发（dispatch + task stream）

**Pub/Sub** `smartfactory:task:dispatch`：轻量通知（可只含 `taskId`，细节以 Stream 为准）。

**Stream** `smartfactory:stream:tasks` 建议字段示例：

```json
{
  "taskId": "TASK_1742890000_ab12",
  "requirementId": "74",
  "assignee": "jarvis",
  "type": "development",
  "priority": "high",
  "payload": {
    "title": "实现网络模块",
    "deadline": "2026-04-10"
  },
  "callbackStream": "smartfactory:stream:results"
}
```

### 3.2 结果上报

**Stream** `smartfactory:stream:results`：

```json
{
  "taskId": "TASK_1742890000_ab12",
  "requirementId": "74",
  "team": "jarvis",
  "status": "completed",
  "progress": 100,
  "result": { "summary": "已实现并通过本地验证" },
  "durationSec": 120
}
```

### 3.3 阻塞

**Pub/Sub** `smartfactory:task:blocker` + **Stream** `smartfactory:stream:blockers`：

```json
{
  "taskId": "TASK_1742890000_ab12",
  "requirementId": "74",
  "team": "jarvis",
  "level": "L2",
  "reason": "依赖冲突 / 需 Hera 决策"
}
```

更完整的示例与禁令列表见 [OPENCLAW_COMMUNICATION_SYSTEM.md §3](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)。

---

## 4. 团队流程摘要

| 角色 | Redis 动作（摘要） |
|------|-------------------|
| **vanguard001** | 可分配需求确定后：`PUBLISH task:dispatch`，`XADD stream:tasks`；可选监听 `stream:results` 做汇总与飞书（飞书为业务通知，不是团队事件总线）。 |
| **jarvis / codeforge / dinosaur** | `XREADGROUP dev-teams … tasks` → 执行 → `XADD stream:results` → `XACK`；阻塞时 `PUBLISH task:blocker`、`XADD stream:blockers`。 |
| **tesla / newton** | `XREADGROUP test-teams … tasks` → 测试/体验 → `XADD stream:results`；Bug/enhancement 仍通过 **API** 创建需求（持久化），并在 result 中引用新需求 id。 |
| **hera** | 订阅 blocker 与（或）`XREADGROUP hera-group … blockers` → 决策 → `XADD stream:results`。 |

细粒度步骤与技能绑定见 [OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)。

---

## 5. 机器状态与心跳（须按时）

- **主路径**：定期向 `smartfactory:agent:heartbeat` **PUBLISH** 结构化心跳（至少包含：`team`、`agent_id`、`host`、时间戳、可选负载摘要）。间隔建议 **≤ 15 分钟**（与现有 `HEARTBEAT.md` 描述对齐），以便 Vanguard/Hera 判断设备与代理在线。
- **补充路径**：仍可使用 HTTP `POST /api/teams/<team>/machine-status` 与 `status-report`（见 [REQUIREMENTS.md §4.5](./REQUIREMENTS.md)）将状态 **持久化到 DB**，供仪表盘、飞书汇总与 **API fallback** 场景使用。
- **原则**：Redis 心跳负责 **实时协作层** 在线感知；API 上报负责 **审计、历史与离线分析**。两者可同时启用。

---

## 6. 与 HTTP API 的分工与 Fallback

| 能力 | 首选 | Fallback / 辅助 |
|------|------|-----------------|
| 派发任务、通知团队开工 | Redis Pub/Sub + Streams | API `assign` + 人工通知；或短暂恢复后轮询 `assigned-requirements`（**降级**） |
| 进度与结果流 | `stream:results` | `POST .../status-report`（降低实时性） |
| 阻塞与决策 | `task:blocker` / `stream:blockers` | `POST /api/discussion/blockage` |
| 项目/需求/任务 CRUD、报表查询 | **HTTP API** | — |
| 机器在线汇总（DB） | API `online`、`machine-status` | 以 Redis heartbeat 为实时真相源之一 |

**禁止**（**多设备 Vanguard 模式**下的协作主路径）：以 **仅** `GET /api/requirements` 轮询作为**跨团队**任务发现机制；以 **仅** Cron 拉 API 作为**团队间**派发方式。例外：**Redis 宕机或网络隔离** 时，启用 API 降级并记录运维事件。  
**不适用**：**单团队独立闭环**（无跨团队派发）以领导 brief 与项目文档为任务来源，不强制 Redis Streams；若仍用 DB 仅作台账，轮询/API 规则不与此「跨团队主路径」冲突。

---

## 7. OpenClaw 侧配置提示

插件与 URI 示例见 [OPENCLAW_COMMUNICATION_SYSTEM.md §5](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)。请将示例中的 Redis 主机改为 **实际 Vanguard001 / Redis 服务地址**（如 `192.168.3.75`）。

推荐能力：`PUBLISH`、`SUBSCRIBE`、`XADD`、`XREADGROUP`、`XACK`、`XGROUP CREATE`（初始化消费组时由运维或启动脚本执行一次）。

---

## 8. 运维检查清单

1. **vanguard001** 上 `redis-server` 进程与持久化策略（AOF/RDB）按环境要求启用。  
2. 所有客户端 `REDIS_URI` 指向同一主节点；防火墙放行 **6379**（或实际端口）。  
3. 为 `stream:tasks` / `stream:results` / `stream:blockers` 创建消费组（若尚未由应用自动创建）。  
4. 验证：`PUBLISH smartfactory:task:dispatch` 后，各团队消费者能收到或读到对应 `XADD` 条目。  
5. 监控：Stream 滞后、未 ACK 条目数、heartbeat 缺失告警。

---

## 9. 相关文档

- [REQUIREMENTS.md](./REQUIREMENTS.md) — HTTP API 全表；§4.5 团队通信在 Redis 降级时使用  
- [ORGANIZATION.md](./ORGANIZATION.md) — 设备与 IP  
- [OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md) — 通信设计细节与示例 JSON  
- [OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) — 角色、技能、Redis 步骤（含 `execution_modes` / `team_standalone_cycle`）  
- [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md) — 团队独立闭环（Redis 非必选）
