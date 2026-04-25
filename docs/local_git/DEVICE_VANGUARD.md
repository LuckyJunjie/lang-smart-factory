# vanguard（Raspberry Pi，arm64）— 软件清单与安装要点

**角色**：**Gitea Runner（arm64）**、可选 **Docker**、现有 **OpenClaw 编排 / Smart Factory API** 宿主；CI Webhook 的常见接收端。

---

## 1. 必装 / 推荐软件

| 软件 | 目的 |
|------|------|
| **Gitea Runner (`act_runner`)** | arm64 构建或轻量检查（需从 Gitea 下载对应架构） |
| **Git** | Runner checkout |
| **Python 3** + **pip/venv** | 测试脚本、调用 Smart Factory API、`requests` |
| **OpenClaw Agent 环境** | 保持现有任务分发与汇报（见 AGENTS.md） |

## 2. 可选软件

| 软件 | 目的 |
|------|------|
| **Docker**（arm64） | 隔离执行 CI step；注意镜像需 **arm64** 或 QEMU（性能差） |
| **build-essential** / 交叉编译链 | 若 Job 需要本地编译 arm64 二进制 |

## 3. 安装与配置提示

1. **Runner**：在 Gitea 注册实例级或组织级 Runner；**labels** 建议包含 `arm64`、`linux`，与 workflow `runs-on` 一致。
2. **并发**：RPi 资源有限，在 Runner 配置中设置较低 **`concurrent`**（如 1–2），避免 OOM。
3. **网络**：确保能访问 `http(s)://dinosaur:3000`（Gitea）及本机或同网段 **Smart Factory API**（`SMART_FACTORY_API` 环境变量，见 [REQUIREMENTS.md](../REQUIREMENTS.md) 文首）。
4. **Redis**：多机协作时配置 **`REDIS_URI`**（见 [REDIS_COLLABORATION.md](../REDIS_COLLABORATION.md)）。

## 4. API / Webhook

Smart Factory 已提供 **`POST /api/webhook/github`**；Gitea 若配置为兼容 payload 可指向该 URL，或后续增加专用 Gitea 适配路由。构建状态回写使用 **`PATCH /api/cicd/builds/<id>/status`**。

---

返回：[README.md](./README.md)
