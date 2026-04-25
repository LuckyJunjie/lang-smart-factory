# jarvis（x86_64 Linux）— 软件清单与安装要点

**角色**：**主力构建节点**（多语言编译）、**Docker** 执行环境、日常 **OpenClaw 开发** 机。

---

## 1. 必装 / 推荐软件

| 软件 | 目的 |
|------|------|
| **Gitea Runner (`act_runner`)** | 执行主要 CI Job |
| **Git** | 拉取代码 |
| **Docker**（或 Podman） | 容器化构建、与 workflow 中 `container` 步骤对齐 |
| **OpenClaw Agent 环境** | 与现有开发流程一致 |

## 2. 按项目可选

根据仓库技术栈安装（示例）：

| 栈 | 典型软件 |
|----|----------|
| Node / 前端 | `node` LTS、`npm`/`pnpm`/`yarn` |
| Python | `python3`、`pip`、`venv` |
| Go | `go` toolchain |
| Java | JDK、Maven 或 Gradle |

具体版本基线可参考 **`openclaw-knowledge/docs/TOOLCHAIN.md`** 与根目录 **`docs/TOOLCHAIN.md`**。

## 3. Runner 标签建议

- `linux-x64` 或 `linux` + `amd64`
- 若承担重编译：`build`

workflow 中 `runs-on` 必须与 Gitea 文档及 Runner 注册标签一致。

## 4. 安全与资源

- Runner 默认以某系统用户运行；敏感值用 **Gitea Secrets**，勿写入仓库。
- 限制 **`concurrent`**，避免与本地 IDE/Agent 争抢 CPU/内存。

---

返回：[README.md](./README.md)
