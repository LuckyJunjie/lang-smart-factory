# 本地 CI/CD 系统架构设计（基于 OpenClaw Smart Factory）

本文档描述在现有 OpenClaw 多机协作与 **Smart Factory** API/Redis 之上，部署 **Gitea（Git + Actions）** 与分布式 **Gitea Runner** 的蓝图。实现细节以各设备软件清单（`DEVICE_*.md`）与 [BUILD_WORKFLOW.md](./BUILD_WORKFLOW.md) 为准。

---

## 1. 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     dinosaur (Mac)                           │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Gitea Server  │  │ MinIO (备选) │  │ Gitea Runner    │   │
│  │ (Git + CI/CD) │  │ 制品存储     │  │ (本地执行器)    │   │
│  └───────────────┘  └──────────────┘  └────────┬────────┘   │
└─────────────────────────────────────────────────┼───────────┘
                                                  │
                                    (HTTP / SSH / gRPC)
                                                  │
        ┌─────────────────────────────────────────┼─────────────────────────┐
        │                                         │                         │
        ▼                                         ▼                         ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   vanguard    │  │    jarvis     │  │   windows     │  │    tesla      │
│ (RPi arm64)   │  │  (x86_64)     │  │  (x86_64)     │  │  (x86_64)     │
│ Runner +      │  │ Runner +      │  │ Runner +      │  │ Runner +      │
│ Orchestrator  │  │ 开发环境      │  │ 构建/测试     │  │ 渲染/测试     │
└───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘
        │
        ▼ (离线, 待恢复)
┌───────────────┐
│   newton      │
│  (x86_64)     │
│ Runner + 编译 │
└───────────────┘
```

### 设计要点

- **Gitea**：轻量 Git 托管 + 内置 Actions（语法接近 GitHub Actions），适合在 Mac（dinosaur）上作为中心节点。
- **Runner 分布式**：每台物理机注册一个或多个 Runner，用 **label** 区分架构与能力（`arm64`、`linux-x64`、`windows`、`gpu` 等）。
- **制品**：MinIO、NFS/SMB 共享目录，或 Mac 本地路径 + 定时同步备份盘。
- **与 Smart Factory / OpenClaw 对齐**：CI 事件通过 Webhook 或流水线步骤调用现有 HTTP API；可选通过 Redis 发布 CI 结果供 Vanguard/Hera 订阅（见下文「集成」）。

---

## 2. 与 Smart Factory 的集成（当前能力与扩展）

Smart Factory 已提供与「流水线 + 构建记录」相关的 API（详见 [REQUIREMENTS.md](../REQUIREMENTS.md)）：

| 能力 | API / 机制 | 说明 |
|------|------------|------|
| Git 类 Webhook（GitHub 形态） | `POST /api/webhook/github` | 按仓库 URL 与分支匹配 `cicd_triggers`，写入 `cicd_builds`（`running`） |
| 构建列表 / 详情 | `GET /api/cicd/builds`、`GET /api/cicd/builds/<id>` | 查询构建历史 |
| 更新构建状态 | `PATCH /api/cicd/builds/<id>/status` | Runner 或编排脚本在结束时回写 `success` / `failed` 等 |
| 流水线与触发器 | `GET/POST /api/pipelines`、`POST /api/pipelines/<id>/triggers` | 与 Webhook 联动 |

**Gitea 对接建议**

1. **短期**：在 Gitea Webhook 或 Actions 最终步骤中，用 `curl`/CLI 调用 `PATCH /api/cicd/builds/<id>/status`；推送事件若与 GitHub payload 差异大，可在 Smart Factory 侧新增 `POST /api/webhook/gitea`（复用 `github_webhook` 的触发与建表逻辑，仅适配 Gitea JSON 字段）。
2. **需求/任务联动**：CI 失败时由编排层调用 `POST /api/requirements`（类型如 bug/feature）或现有分配流程，与 [OPENCLAW_DEVELOPMENT_FLOW.yaml](../../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml) 一致。
3. **Redis（可选）**：文档 [REDIS_COLLABORATION.md](../REDIS_COLLABORATION.md) 定义 `smartfactory:stream:tasks` / `results` / `blockers`。若需专用 CI 通道，可约定新流 **`smartfactory:stream:ci`**（或等价命名），由 Gitea/Runner 脚本 `XADD`，Vanguard/Hera 消费；实施前与现有消费组约定字段 schema。

---

## 3. 从 GitHub 迁移到本地 Gitea

### 3.1 批量镜像克隆（示例）

假设 `github_repos.txt` 每行为 `org/repo`，Gitea 在 `http://dinosaur:3000`：

```bash
#!/usr/bin/env bash
GITEA_URL="http://dinosaur:3000"
GITEA_TOKEN="your_admin_token"
WORK_DIR="/tmp/git-mirror"

mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1

while read -r repo; do
  [[ -z "$repo" || "$repo" =~ ^# ]] && continue
  name=$(basename "$repo")
  echo "Cloning $repo ..."
  git clone --mirror "https://github.com/$repo.git"
  cd "$name.git" || exit 1
  curl -sS -X POST "$GITEA_URL/api/v1/admin/users/youruser/repos" \
    -H "Authorization: token $GITEA_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"private\":true}"
  git push --mirror "$GITEA_URL/youruser/$name.git"
  cd ..
  rm -rf "$name.git"
done < github_repos.txt
```

**优化**：SSH 推送、`parallel` 并行（注意 Gitea 限流）、大仓先 `git lfs fetch --all` 并确保 Gitea 启用 LFS。

### 3.2 GitHub Actions → Gitea Actions

- 将 `.github/workflows/*.yml` 复制到 `.gitea/workflows/`（或 Gitea 配置要求的路径）。
- 将 Secrets 迁移到 Gitea Secrets。
- 校验不兼容的 Action；`actions/cache` 等可用社区替代或自建。

### 3.3 与 GitHub 双远程（可选）

添加 `remote github`，定期 `git fetch github --prune` 再推送到 Gitea；长期建议以 Gitea 为唯一写入源。

---

## 4. 备份方案

### 4.1 备份范围

- Gitea 数据库（PostgreSQL dump 或 SQLite 文件）
- 仓库存储目录（如 `/var/lib/gitea/repositories`）
- `app.ini` 与 Runner 注册令牌（安全保存）
- CI 缓存与制品（MinIO bucket 或本地目录）
- **Smart Factory 数据库**：仓库内默认路径见 `core/README.md`（如 `core/data.db`），与 Gitea 一并纳入备份策略

### 4.2 策略建议

| 频率 | 方式 | 保留 |
|------|------|------|
| 每小时 | DB 增量（`pg_dump` / `sqlite3 .backup`） | 24h |
| 每天 | 仓库 + DB + 配置打包 | 7 天 |
| 每周 | 全量复制到外置盘/NAS | 4 周 |

示例脚本骨架见用户蓝图（每日 `tar` + `rsync`）；生产环境请把密码与路径改为环境变量或密钥管理。

### 4.3 恢复概要

停止 Gitea → 恢复数据库与仓库目录与配置 → 启动服务 → 抽样 `git fsck` / 登录验证。

---

## 5. 实施路线图

1. dinosaur：Gitea + DB +（可选）首个 Runner。
2. 各节点注册 Runner 并打标签：`arm64`、`linux-x64`、`windows`、`gpu` 等。
3. 试点迁移 1–2 个仓库（如本仓库 `smart-factory`），编写 `.gitea/workflows/*.yml`。
4. 部署备份与恢复演练。
5. 接通 Smart Factory：`PATCH /api/cicd/builds/...` 与（可选）Gitea Webhook 或新 `webhook/gitea`。
6. 团队流程切换：远程 URL、文档与 OpenClaw CLI 中的仓库地址统一为 Gitea。

---

## 6. 风险与应对

| 风险 | 应对 |
|------|------|
| Mac 单点故障 | 定时备份；备机或 jarvis 侧冷备同步 |
| 磁盘占满 | 监控 Gitea 数据目录；制品保留策略（如仅保留最近 N 次成功构建） |
| Runner 过载 | `concurrent` 限制、队列、按 label 分流 |
| 与人工任务抢资源 | 约定优先级：CI 任务低于紧急人工派发（Redis/API 层策略） |

---

## 7. 文档索引

- 工作流时序：[BUILD_WORKFLOW.md](./BUILD_WORKFLOW.md)
- 各机器软件与安装要点：[DEVICE_*.md](./README.md)
