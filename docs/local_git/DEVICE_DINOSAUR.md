# dinosaur（Mac）— 软件清单与安装要点

**角色**：集群中的 **Gitea 中心节点**（Git + Actions 调度）、可选 **轻量 Runner**、可选 **MinIO** 与备份落地盘。

---

## 1. 必装 / 推荐软件

| 软件 | 版本 / 方式 | 目的 |
|------|-------------|------|
| **Gitea** | 官方最新稳定版（二进制或 Docker） | 仓库托管、`.gitea/workflows`、Webhook |
| **数据库** | PostgreSQL 14+（推荐生产）或 SQLite | Gitea 元数据；SQLite 适合极简单机 |
| **Gitea Runner** | 与 Gitea 版本匹配的官方 `act_runner` | 执行 lint、文档生成等轻量 Job（可选） |
| **Git** | Xcode CLT 或 Homebrew `git` | 管理、镜像脚本 |
| **OpenClaw / Smart Factory CLI** | 链接或克隆 `openclaw-knowledge/cli` | 上报状态、调用 API（与现有流程一致） |

## 2. 可选软件

| 软件 | 目的 |
|------|------|
| **MinIO** | 制品与缓存对象存储 |
| **Docker Desktop** | 容器化 Gitea/Runner/MinIO（注意 Mac 文件权限与 I/O） |
| **rsync** / **restic** | 备份到外置盘或 NAS |
| **PostgreSQL.app** 或 Homebrew `postgresql@16` | 本地 PG（若不用 SQLite） |

## 3. 安装与配置提示

1. **Gitea**：优先阅读 [Gitea 官方文档](https://docs.gitea.com/) 的 installation；生产建议 **PostgreSQL** + 独立用户 + 将 `repositories` 与数据库放在有足够空间的卷。
2. **Mac 性能**：大仓与高频 CI 时，二进制 Gitea 往往比 Docker 卷更省心；若用 Docker，为数据目录使用 **bind mount** 到 APFS 卷并监控空间。
3. **Runner 注册**：在 Gitea 管理界面创建 Runner token，在 Mac 上启动 `act_runner` 并打上例如 `macos`、`light` 等 label。
4. **TLS**：内网可用 HTTP + SSH；跨网段建议 **HTTPS**（反向代理或内置 TLS）。
5. **与 Smart Factory**：Webhook 目标指向运行 API 的主机（常为 vanguard），路径见 [LOCAL_CICD_BLUEPRINT.md](./LOCAL_CICD_BLUEPRINT.md)。

## 4. 备份（本机职责）

定时任务应覆盖：Gitea DB、仓库目录、`app.ini`、MinIO 数据（若有）、以及 Smart Factory `core/data.db`（路径以部署为准）。脚本示例见 [LOCAL_CICD_BLUEPRINT.md](./LOCAL_CICD_BLUEPRINT.md) 第 4 节。

---

返回：[README.md](./README.md)
