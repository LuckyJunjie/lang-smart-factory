# newton（x86_64，离线待恢复）— 软件清单与安装要点

**角色**：恢复后作为 **额外编译/文档节点**，与 jarvis 类似，可分担重 CPU 构建或文档生成类 Job。

---

## 1. 恢复后推荐软件

| 软件 | 目的 |
|------|------|
| **Gitea Runner (`act_runner`)** | 领取 `linux-x64` / `build` 等 label 的 Job |
| **Git** | checkout |
| **Docker**（可选） | 与 jarvis 一致的容器构建 |
| **Python 3** + 项目依赖 | 测试与脚本 |
| **OpenClaw Agent 环境** | 与团队为 newton 设定的角色一致 |

## 2. 与 jarvis 的分工建议

- **jarvis**：默认主构建、日常开发。
- **newton**：长时间编译、全量测试矩阵、文档站点构建等可 **通过 label** 单独引流，避免单点过载。

## 3. 离线恢复检查清单

- [ ] 操作系统与安全补丁
- [ ] 与 dinosaur 的 **网络**（Gitea）、与 vanguard 的 **API/Redis** 可达
- [ ] Runner 重新注册（旧 token 可能失效）
- [ ] `TOOLCHAIN` 版本与 jarvis/tesla **对齐**

---

返回：[README.md](./README.md)
