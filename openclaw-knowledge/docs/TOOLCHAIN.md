# OpenClaw 工具链与环境基线

> **用途**：给 OpenClaw 代理与运维人员一份可执行的**安装、版本与自检**说明。  
> **更全的工具/MCP/技能目录表**仍见仓库根目录 **[../../docs/TOOLCHAIN.md](../../docs/TOOLCHAIN.md)**（本文件专注「装什么、什么版本、怎么验」）。

**流程对齐**：自举清单还以 **[workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](../workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)** 中的 `environment_bootstrap` 为准；二者冲突时以**本文件版本基线**更新 YAML。

---

## 1. 按角色的最短检查表

| 角色 / 场景 | 必须具备 | 建议具备 |
|-------------|----------|----------|
| **所有代理** | `python3`、`git`、`requests`、环境变量 `SMART_FACTORY_API`；多机再加 `REDIS_URI` | `FEISHU_WEBHOOK_URL`（要发飞书时） |
| **跑 Smart Factory 本机 API / pytest** | `flask`、`pytest`、`pytest-cov`（见 §4） | 与 `pytest.ini` 一致：`pythonpath = core openclaw-knowledge` |
| **Godot 开发 / 测试**（Jarvis、CodeForge、Dinosaur、Tesla、Newton） | **Godot 4.5.1**（headless 可用）、`timeout` 或等价 | `xvfb-run`（Linux 无显示）、`ffmpeg`、`gdlint`（见 §5） |
| **选用 MCP 而非仅 CLI** | `pip install -r openclaw-knowledge/mcp/requirements.txt` | `mcp` 包与网络 |

---

## 2. 通用：Git、Python、协作变量

### 2.1 Git

- **安装**：随发行版包管理器或 [git-scm.com](https://git-scm.com/)。
- **自检**：`git --version`
- **推送受网络影响**：见同目录 **[GITHUB_NETWORK_AND_PUSH_RETRY.md](./GITHUB_NETWORK_AND_PUSH_RETRY.md)**（含 5 分钟 cron 重试脚本）。

### 2.2 Python 与最小依赖

- **版本**：`python3` 建议 **3.10+**（与当前 CI/本机一致即可）。
- **全代理最小**：`python3 -m pip install 'requests>=2.28'`
- **仓库根运行 pytest（API 测试）**：至少需要：
  ```bash
  python3 -m pip install flask pytest pytest-cov requests pyyaml
  ```
  在**仓库根**执行（`pytest.ini` 已配置 `pythonpath = core openclaw-knowledge`）：
  ```bash
  python3 -m pytest tests/ -v
  python3 -m pytest tests/ --cov=core/api --cov-report=html
  ```

### 2.3 环境变量（常见）

| 变量 | 说明 |
|------|------|
| `SMART_FACTORY_API` | HTTP API 基地址，须含 `/api`，例：`http://192.168.3.75:5000/api` |
| `REDIS_URI` | 多机协作，例：`redis://192.168.3.75:6379` |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook（需要群发时） |

详见根目录 **`docs/REQUIREMENTS.md`**、**`docs/REDIS_COLLABORATION.md`**。

### 2.4 CLI / Skills 的运行方式

- 将 **`openclaw-knowledge`** 加入 `PYTHONPATH`，或在仓库根执行（与 **`openclaw-knowledge/scripts/setup_openclaw_workspaces.py`** 生成的工作区一致）。
- 入口：**[../cli/README.md](../cli/README.md)**、**[../TOOLS_INDEX.md](../TOOLS_INDEX.md)**。

---

## 3. Godot **4.5.1**（团队基线版本）

**约定**：自动化与文档以 **Godot 4.5.1-stable** 为基线；其他小版本仅作过渡，合入前应在目标项目内跑通 headless / 测试。

- **发布页**：[Godot 4.5.1-stable on GitHub Releases](https://github.com/godotengine/godot/releases/tag/4.5.1-stable)
- **自检**：
  ```bash
  godot --version
  # 应出现 4.5.1（或构建串中含 4.5.1-stable）
  timeout 30 godot --headless --quit 2>&1
  ```
- **资源变更后**（大 import）：`timeout 120 godot --headless --import`（超时按项目调大）

### 3.1 按平台安装要点

| 平台 | 建议方式 | 注意 |
|------|----------|------|
| **macOS** | 从 **4.5.1-stable** 下载 **.dmg / .zip**，将 `Godot.app` 或二进制加入 `PATH`；或 `brew install --cask godot` 后**务必** `godot --version` 确认为 4.5.1 | Homebrew 常为最新版，**不等于** 4.5.1 时改用官方包 |
| **Windows** | 官方 **win64.exe** 或压缩包；`winget install -e --id GodotEngine.GodotEngine` 后**验证版本** | winget 可能落后于或超前于 4.5.1，以 `godot --version` 为准 |
| **Linux** | 官方 **Linux.x86_64**（或对应架构）可执行文件，放到如 `/usr/local/bin/godot` 并 `chmod +x` | **不要用** 发行版里的 `godot3` 包作为 4.x 基线；`apt` 若仅有 3.x，请用官方 4.5.1 二进制 |

### 3.2 常用伴生工具

- **`coreutils`（macOS）**：GNU `timeout`：`brew install coreutils`（必要时用 `gtimeout` 或把 `timeout` 配进 PATH）。
- **`xvfb-run`（Linux 无头/无显示器）**：`sudo apt-get install -y xvfb`，用法示例：`xvfb-run -a godot --headless --quit`。
- **`ffmpeg`**：截图序列、录屏与部分 harness；macOS `brew install ffmpeg`，Windows `winget install -e --id Gyan.FFmpeg`。

---

## 4. 测试工具（Python / Smart Factory）

| 工具 | 用途 |
|------|------|
| **pytest** | 仓库 `tests/` 下 API 与模块测试 |
| **pytest-cov** | 覆盖率（默认覆盖 `core/api`，见根目录 `pytest.ini`） |
| **Flask** | API 实现与测试客户端依赖 |

**运行**：在仓库根执行 `python3 -m pytest tests/ -v`。  
与 `cli test` 域的对应关系见 **[../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md](../workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)**。

---

## 5. 游戏与 GdUnit / GDScript 侧

| 工具 | 用途 |
|------|------|
| **GdUnit4** | Godot 4 插件；在**游戏项目**内启用后随 `godot` 跑测试；架构与命令细节见 **[../../archived/game/docs/GODOT_TESTING.md](../../archived/game/docs/GODOT_TESTING.md)** |
| **GDSnap** | 截图对比类测试（项目可选） |
| **gdlint** | GDScript 静态检查；常见安装：`python3 -m pip install gdtoolkit`（提供 `gdlint`） |

**技能与流程**：**[./GODOT_SKILLS_AND_TESTING.md](./GODOT_SKILLS_AND_TESTING.md)**（`godogen` / `godot-task`）。

**godot-task Doc API**：`bash openclaw-knowledge/skills/godot-task/tools/ensure_doc_api.sh`（在仓库检出根执行）。

---

## 6. 选用 MCP 时的 Python 依赖

```bash
python3 -m pip install -r openclaw-knowledge/mcp/requirements.txt
```

详情：**[../mcp/README.md](../mcp/README.md)**。

---

## 7. 变更记录

| 日期 | 内容 |
|------|------|
| 2026-04-04 | 新建 OpenClaw 专属环境基线：Godot **4.5.1**、Git/Python/pytest/FFmpeg/xvfb/gdlint、与根目录 TOOLCHAIN 分工 |

*维护：与 `docs/TOOLCHAIN.md` 目录表同步时，优先更新根目录「智慧工厂工具列表」，版本与安装命令以本文件为准。*
