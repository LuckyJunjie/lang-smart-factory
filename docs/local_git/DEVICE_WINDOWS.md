# windows（x86_64）— 软件清单与安装要点

**角色**：**.NET / MSVC / Windows 专用打包**、部分游戏或工具链的 **Windows-only** 构建与测试。

---

## 1. 必装 / 推荐软件

| 软件 | 目的 |
|------|------|
| **Gitea Runner（Windows 版 `act_runner`）** | 执行带 `windows` label 的 Job |
| **Git for Windows** | Runner checkout |
| **OpenClaw Agent 环境** | 与团队 Windows 开发角色一致（如 codeforge 相关） |

## 2. 按项目可选

| 软件 | 目的 |
|------|------|
| **Visual Studio Build Tools** 或 **Visual Studio** | MSVC、C++ 工程 |
| **.NET SDK** | C# / .NET 构建 |
| **Docker Desktop** | 需要 Windows 容器或 Linux 子系统时的混合流水线（按项目评估） |

## 3. 安装与配置提示

1. 以 **Windows Service** 或计划任务方式运行 Runner，保证登录会话外仍可执行 Job。
2. Runner **labels** 建议包含 `windows`、`x64`。
3. 路径与行尾：注意 workflow 中脚本使用 **`pwsh`** 或 **`cmd`** 与仓库规范一致。
4. Smart Factory 侧若有 **Windows Runner 管理 API**（`GET/POST /api/devops/runners/windows/...`），可与本机 Runner 并存，职责划分需在团队内约定（见 [REQUIREMENTS.md](../REQUIREMENTS.md) DevOps 章节）。

---

返回：[README.md](./README.md)
