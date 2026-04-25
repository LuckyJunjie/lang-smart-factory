# 智慧工厂工具链管理系统

> **OpenClaw 环境与版本基线**（Git、**Godot 4.5.1**、pytest、FFmpeg 等安装与自检）以 **[openclaw-knowledge/docs/TOOLCHAIN.md](../openclaw-knowledge/docs/TOOLCHAIN.md)** 为准。  
> **本文档**侧重智慧工厂侧的 **MCP / CLI / Skills 目录、推荐工具表与 JSON 配置示例**。

## 概述

本文档维护智慧工厂使用的所有工具、MCP 服务、扩展和技能。

---

## 一、已安装的工具

### 1. OpenClaw Skills (技能)

| 技能名称 | 功能 | 状态 | 链接 |
|----------|------|------|------|
| feishu-doc | 飞书文档操作 | ✅ 已启用 | 内置 |
| feishu-drive | 飞书云盘管理 | ✅ 已启用 | 内置 |
| feishu-perm | 飞书权限管理 | ✅ 已启用 | 内置 |
| feishu-wiki | 飞书知识库 | ✅ 已启用 | 内置 |
| healthcheck | 安全检查 | ✅ 已启用 | 内置 |
| skill-creator | 技能创建 | ✅ 已启用 | 内置 |
| weather | 天气查询 | ✅ 已启用 | 内置 |

### 2. OpenClaw Extensions (扩展)

| 扩展名称 | 功能 | 状态 | 链接 |
|----------|------|------|------|
| feishu | 飞书消息通道 | ✅ 已启用 | 内置 |
| discord | Discord 消息 | ❌ 未启用 | 内置 |
| telegram | Telegram 消息 | ❌ 未启用 | 内置 |
| slack | Slack 消息 | ❌ 未启用 | 内置 |
| whatsapp | WhatsApp 消息 | ❌ 未启用 | 内置 |
| signal | Signal 消息 | ❌ 未启用 | 内置 |
| memory-core | 记忆核心 | ✅ 已启用 | 内置 |
| memory-lancedb | 向量数据库 | ✅ 已启用 | 内置 |
| llm-task | LLM 任务 | ✅ 已启用 | 内置 |

---

## 二、推荐工具 (待研究/集成)

### 1. 游戏开发相关

| 工具名称 | 功能 | 推荐度 | 链接 |
|----------|------|--------|------|
| Godot | 游戏引擎 | ⭐⭐⭐⭐⭐ | https://godotengine.org |
| GDSnap | Godot 截图测试 | ⭐⭐⭐ | https://github.com/arnoke/GDSnap |
| gdunit4 | Godot 单元测试 | ⭐⭐⭐ | https://github.com/IdiotBoomer/gdUnit4 |

### 2. 自动化相关

| 工具名称 | 功能 | 推荐度 | 链接 |
|----------|------|--------|------|
| Alfred | macOS 效率工具 | ⭐⭐⭐⭐ | https://www.alfredapp.com |
| Hammerspoon | macOS 自动化 | ⭐⭐⭐⭐ | https://www.hammerspoon.org |
| Shortcuts | macOS 快捷指令 | ⭐⭐⭐ | 内置 |
| Keyboard Maestro | macOS 宏 | ⭐⭐⭐⭐ | https://www.keyboardmaestro.com |

### 3. 项目管理相关

| 工具名称 | 功能 | 推荐度 | 链接 |
|----------|------|--------|------|
| Jira | 项目管理 | ⭐⭐⭐⭐ | https://www.atlassian.com/software/jira |
| Linear | 项目管理 | ⭐⭐⭐⭐ | https://linear.app |
| Notion | 知识库 | ⭐⭐⭐⭐ | https://notion.so |
| GitHub Projects | GitHub 项目 | ⭐⭐⭐⭐ | https://github.com/features/issues |

### 4. 图像识别/计算机视觉

| 工具名称 | 功能 | 推荐度 | 链接 |
|----------|------|--------|------|
| OpenCV | 计算机视觉库 | ⭐⭐⭐⭐⭐ | https://opencv.org |
| PyTorch | 深度学习 | ⭐⭐⭐⭐⭐ | https://pytorch.org |
| TensorFlow | 深度学习 | ⭐⭐⭐⭐ | https://tensorflow.org |
| YOLO | 目标检测 | ⭐⭐⭐⭐ | https://ultralytics.com |

### 5. Smart Factory CLI（代理工具，替代 MCP）

#### CLI 命令域（已实现）

| 域 | 功能 | 运行位置 |
|----|------|----------|
| **cli project** | 需求/任务/分配/阻塞（对接 Smart Factory API） | 任意（需 SMART_FACTORY_API） |
| **cli comm** | 飞书消息、邮件、飞书日志分析 | 任意（需 API 或 FEISHU_WEBHOOK_URL） |
| **cli dev** | 文件、Git、构建、白名单命令 | 每台 agent 服务器 |
| **cli godot** | Godot 项目/场景/测试/导出 | 每台有 Godot 的机器 |
| **cli test** | 单元/集成测试、覆盖率、解析输出 | 每台 agent 服务器 |
| **cli analysis** | 代码分析、需求提取、变更摘要 | 每台 agent 服务器 |

详见 [openclaw-knowledge/cli/README.md](../openclaw-knowledge/cli/README.md)。OpenClaw 流程由上述 CLI + Skills 驱动，见 [OPENCLAW_COMMUNICATION_SYSTEM.md](../openclaw-knowledge/workflows/OPENCLAW_COMMUNICATION_SYSTEM.md)（多设备）与 [OPENCLAW_STANDALONE_WORKFLOW.md](../openclaw-knowledge/workflows/OPENCLAW_STANDALONE_WORKFLOW.md)（团队独立）。MCP 服务器实现保留在 [openclaw-knowledge/mcp/README.md](../openclaw-knowledge/mcp/README.md)（可选/兼容）。

#### 其他 MCP（推荐/内置）

| 服务名称 | 功能 | 推荐度 | 链接 |
|----------|------|--------|------|
| filesystem | 文件系统访问 | ⭐⭐⭐⭐⭐ | 内置 |
| git | Git 操作 | ⭐⭐⭐⭐ | 内置 |
| github | GitHub API | ⭐⭐⭐⭐ | 内置 |
| **godot-mcp** | Godot 游戏控制（截图、输入、GDScript） | ⭐⭐⭐⭐ | `docs/GODOT_MCP_DEPLOYMENT.md` |
| Brave Search | 网页搜索 | ⭐⭐⭐ | 需要 API Key |
| puppeteer | 浏览器控制 | ⭐⭐⭐⭐ | - |

---

## 三、开发环境工具

### 1. 代码编辑器

| 工具名称 | 用途 | 状态 |
|----------|------|------|
| VS Code | 主要编辑器 | ✅ 已安装 |
| Godot | 游戏引擎 | ✅ 已安装 |
| Xcode | iOS/macOS 开发 | ✅ 已安装 |

### 2. 版本控制

| 工具名称 | 用途 | 状态 |
|----------|------|------|
| Git | 版本控制 | ✅ 已安装 |
| GitHub CLI | GitHub 操作 | ✅ 已安装 |

### 3. 监控工具

| 工具名称 | 用途 | 状态 |
|----------|------|------|
| Node Exporter | Linux 监控 | TODO |
| macOS Exporter | macOS 监控 | TODO |
| Windows Exporter | Windows 监控 | TODO |
| Prometheus | 时序数据库 | TODO |
| Grafana | 可视化 | TODO |

---

## 四、Smart Factory Skills（已实现）与待集成技能

### Smart Factory 自研 Skills（已实现）

| Skill | 执行者 | 功能 |
|-------|--------|------|
| **assign_tasks_to_teams** | Vanguard | API 持久化 assign + **Redis 派发**（`task:dispatch` / `stream:tasks`）；飞书汇报 |
| **handle_blockage** | Hera | 处理阻塞、决策、重新分配或延后 |
| **generate_daily_report** | Vanguard | 汇总团队状态与风险，发飞书日报 |
| **develop_requirement** | jarvis / codeforge / dinosaur / **Tesla / Newton**（开发分配时） | 领取需求、上报进度、标记 developed |
| **test_requirement** | Tesla / Newton（测试队列主责） | 测试需求、创建 Bug、标记 tested |
| **parse_requirement_doc** | 任意 | 从 PRD 提取需求并批量创建 |

运行方式：`python -m skills.assign_tasks_to_teams` 等（须配置 **`REDIS_URI`**），见 [skills/README.md](../openclaw-knowledge/skills/README.md)、[REDIS_COLLABORATION.md](./REDIS_COLLABORATION.md)。

### Godot 相关 Skills 使用策略（新增）

| Skill | 适用场景 | 主要使用角色 |
|-------|----------|--------------|
| `godogen` | **项目级** Godot 任务：从自然语言生成/更新完整游戏（计划、脚手架、资产、任务编排） | `jarvis` / `codeforge` / `dinosaur`；**Tesla / Newton** 在承担项目级开发分配时同等 |
| `godot-task` | **任务级** Godot 任务：单个 scene/script 调试、构建验证、截图与视觉 QA | `jarvis` / `codeforge` / `dinosaur` / `tesla` / `newton`（通常作为 spawned specialist 执行） |

使用原则：
- 非 Godot 任务优先用 `develop_requirement` / `test_requirement` + `cli dev/test/analysis`
- Godot 项目级需求先用 `godogen` 拆解任务，再由 `godot-task` 执行具体子任务
- Godot 子任务执行必须包含 headless 验证（`godot --headless --quit`）与必要的截图/视觉校验

### 高优先级（待集成/增强）

1. **godot-skill** - Godot 游戏开发辅助
   - 功能：代码生成、场景管理、导出（部分由 **godot-mcp** 已覆盖）
   - 状态：MCP 已实现，Skill 可组合 godot_build_and_test

2. **image-recognition-skill** - 图像识别
   - 功能：截图分析、游戏状态识别
   - 状态：未开发

3. **project-management-skill** - 项目管理
   - 功能：任务创建、进度跟踪、报告生成（由 **project-mcp** + **assign_tasks_to_teams** / **generate_daily_report** 已覆盖）
   - 状态：已实现（MCP + Skills）

### 中优先级

4. **automation-skill** - 自动化任务
   - 功能：定时任务、工作流自动化
   - 状态：部分实现

5. **requirement-analysis-skill** - 需求分析
   - 功能：需求文档解析、任务拆分
   - 状态：未开发

---

## 五、环境与工具自安装基线（OpenClaw 自举）

**已迁移至** **[openclaw-knowledge/docs/TOOLCHAIN.md](../openclaw-knowledge/docs/TOOLCHAIN.md)**，内容包括：

- 全角色：`python3`、`git`、`requests`、`SMART_FACTORY_API`、`REDIS_URI`、Flask/pytest（跑仓库测试时）
- Godot 角色：**Godot 4.5.1-stable**、headless 自检、`xvfb-run`、`ffmpeg`、`gdlint`、Linux 勿用 `godot3` 包装充当 4.x
- 游戏测试：GdUnit4 / GDSnap / `ensure_doc_api` 指针
- MCP 选用：`openclaw-knowledge/mcp/requirements.txt`

机器可执行的 **`environment_bootstrap`** 字段仍见 **[openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml](../openclaw-knowledge/workflows/OPENCLAW_DEVELOPMENT_FLOW.yaml)**（需与上文基线文档同步迭代）。

## 六、配置示例

### OpenClaw 技能配置

```json
{
  "skills": {
    "feishu-doc": "enabled",
    "feishu-wiki": "enabled", 
    "healthcheck": "enabled",
    "weather": "enabled"
  }
}
```

### 扩展配置

```json
{
  "extensions": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx"
    },
    "memory-core": {
      "enabled": true
    }
  }
}
```

---

## 七、更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-02-28 | 初始版本，梳理现有工具 |
| 2026-02-28 | 添加推荐工具列表 |
| 2026-03-12 | 添加 Smart Factory 自研 MCP（project/comm/dev/godot/test/analysis）与 Skills，与 OPENCLAW_COMMUNICATION_SYSTEM 对齐 |
| 2026-03-25 | 新增角色-技能使用策略（godogen/godot-task）与 OpenClaw 自安装环境基线 |
| 2026-04-04 | OpenClaw 环境/版本安装细则迁至 `openclaw-knowledge/docs/TOOLCHAIN.md`；本文保留工具目录与配置示例 |

---

*维护者: Jarvis*
*最后更新: 2026-04-04*
