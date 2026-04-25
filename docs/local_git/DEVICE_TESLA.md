# tesla（x86_64）— 软件清单与安装要点

**角色**：**渲染、游戏引擎测试、自动化测试**（含 headless）、媒体处理；OpenClaw **测试向** Agent 常用机。

---

## 1. 必装 / 推荐软件

| 软件 | 目的 |
|------|------|
| **Gitea Runner (`act_runner`)** | 执行测试/渲染类 Job |
| **Git** | checkout |
| **Python 3** + **pytest**（或项目约定测试框架） | 自动化测试 |
| **OpenClaw Agent 环境** | `test_requirement` 等与流程一致 |

## 2. 按项目可选

| 软件 | 目的 |
|------|------|
| **Godot 4.x**（团队基线如 4.5.1，见 TOOLCHAIN） | 游戏项目 headless、导出、截图/VQA |
| **Unity**（若项目使用） | 对应 LTS 与许可 |
| **FFmpeg**、**ImageMagick** | 视频/图像产物处理 |
| **xvfb-run**（Linux） | 无显示器运行部分 GUI/引擎测试 |

环境基线：**`openclaw-knowledge/docs/TOOLCHAIN.md`**、**`docs/TOOLCHAIN.md`**。

## 3. Runner 标签建议

- `linux-x64`、`test`
- 若承担 GPU 任务：`gpu`（与 workflow 约定一致）

## 4. 与 CI 的衔接

构建产物由 jarvis/windows 产生后，可通过 **artifact 下载**、**共享目录** 或 **MinIO** 同步到 tesla，再在 workflow 中触发测试 Job；或在同一仓库中用 **workflow_run** 类依赖（以 Gitea 实际支持为准）。

---

返回：[README.md](./README.md)
