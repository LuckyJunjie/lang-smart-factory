# 一人公司游戏开发生产线

> 基于本地异构集群（树莓派管理 + Mac mini计算 + Windows测试）
> 结合飞书协作与AI生成工具，设计从创意到发布的端到端高效流水线

---

## ⚠️ 当前 vs 目标

| 类型 | 说明 |
|------|------|
| **当前流程** | 遵循 [standards/DEVELOPMENT_FLOW.md](../standards/DEVELOPMENT_FLOW.md)：DB 驱动、团队领取需求、拆解任务、Scrum Master 分配 |
| **本文档** | 描述**目标流程**（未来完整流水线），部分系统尚未就绪，待逐步实现 |

---

## 🏗️ 整体架构（目标）

```mermaid
flowchart LR
    subgraph Human["👤 人类工程师"]
        PM["🎯 制作人/项目经理"]
        Designer["📝 策划/设计师"]
        Artist["🎨 美术师"]
        Dev["💻 程序员"]
    end
    
    subgraph OpenClaw["🤖 OpenClaw Agent集群 (树莓派主控)"]
        PM_Agent["📊 项目管理Agent"]
        Idea_Agent["💡 创意孵化Agent"]
        Asset_Agent["🎁 资源生成Agent"]
        Code_Agent["⚡ 代码辅助Agent"]
        Build_Agent["🔨 构建/测试Agent"]
        Release_Agent["🚀 发布/运维Agent"]
    end
    
    subgraph Tools["🛠️ AI工具/服务"]
        AI_Text["📚 ChatGPT/Claude 文案/故事"]
        AI_Image["🖼️ Midjourney/Stable Diffusion 2D/概念图"]
        AI_3D["🎲 Meshy/CSM 3D模型"]
        AI_Audio["🎵 ElevenLabs/AIVA 语音/音乐"]
        AI_Code["🔧 CodeBuddy/GitHub Copilot 代码生成"]
    end
    
    subgraph Platform["☁️ 协作与存储"]
        Feishu["📲 飞书（文档/任务/审批/机器人）"]
        Git["📦 Git仓库（GitHub）"]
        NAS["💾 本地NAS（资源库/版本存档）"]
    end
    
    Human -->|需求/指令| Feishu
    Feishu -->|触发事件| OpenClaw
    OpenClaw -->|调用| Tools
    OpenClaw -->|分配任务| Human
    Tools -->|生成内容| NAS
    OpenClaw -->|触发构建| Mac_mini
    Mac_mini -->|构建产物| Windows
    Windows -->|测试报告| OpenClaw
    OpenClaw -->|发布包| Release_Agent
```

---

## 🎨 颜色说明

| 颜色 | 角色 | 说明 |
|------|------|------|
| 🟢 **绿色** | 👤 人类工程师 | 创意决策、质量把控、最终审批 |
| 🔵 **蓝色** | 🤖 OpenClaw Agent | 自动化调度、任务分配、流程执行 |
| 🟡 **黄色** | 🛠️ AI工具/服务 | 内容生成、代码补全、构建测试 |
| 🟣 **紫色** | ☁️ 协作平台 | 飞书、Git、NAS等基础设施 |

---

## 📋 七阶段工作流程（目标，未来完整流水线）

### 🟢 阶段1：创意孵化与项目管理启动

| 步骤 | 角色 | 操作 |
|------|------|------|
| 1.1 | 🟢 制作人 | 在飞书撰写游戏创意简报（类型、核心玩法、目标用户） |
| 1.2 | 🔵 创意孵化Agent | 监听飞书文档更新 |
| 1.3 | 🟡 AI (ChatGPT) | 生成3个核心玩法提案、故事背景、竞品分析 |
| 1.4 | 🔵 项目管理Agent | 自动存入飞书文档，@制作人评审 |
| 1.5 | 🟢 制作人 | 确认方向 |
| 1.6 | 🔵 项目管理Agent | 创建飞书项目空间、里程碑日历、任务看板 |

### 🟢 阶段2：概念设计与资源规划

| 步骤 | 角色 | 操作 |
|------|------|------|
| 2.1 | 🟢 策划/美术师 | 填写飞书美术需求表单 |
| 2.2 | 🔵 资源生成Agent | 解析表单，调用AI工具 |
| 2.3 | 🟡 Midjourney | 生成概念图（角色/场景/UI） |
| 2.4 | 🟡 Meshy | 草图转3D白模（可选） |
| 2.5 | 🟡 ElevenLabs | 生成角色语音样本（可选） |
| 2.6 | 🔵 资源生成Agent | 存入NAS，飞书标记待审核 |
| 2.7 | 🟢 美术师 | 挑选/修改，确认入库 |

### 🟢 阶段3：技术设计与开发任务拆分

| 步骤 | 角色 | 操作 |
|------|------|------|
| 3.1 | 🟢 程序+策划 | 编写技术设计文档（架构、模块、数据流） |
| 3.2 | 🔵 代码辅助Agent | 生成项目脚手架、核心类接口、单元测试模板 |
| 3.3 | 🔵 项目管理Agent | 自动创建飞书任务看板，分配给程序员 |
| 3.4 | 🔵 代码辅助Agent | 监听Git仓库，提交时自动代码审查 |

### 🟢 阶段4：资源生产与编码并行

| 步骤 | 角色 | 操作 |
|------|------|------|
| 4.1 | 🟢 美术师 | 飞书提交资源需求 |
| 4.2 | 🔵 资源生成Agent | 调用AI批量生成，存入NAS |
| 4.3 | 🟢 美术师 | 微调后确认，同步到工程 |
| 4.4 | 🟢 程序员 | IDE编码 |
| 4.5 | 🟡 CodeBuddy | 实时补全/建议 |
| 4.6 | 🔵 构建Agent | 触发Mac mini增量编译 |
| 4.7 | 🔵 构建Agent | 编译成功→触发Windows测试机 |

### 🟢 阶段5：集成与每日构建

| 步骤 | 角色 | 操作 |
|------|------|------|
| 5.1 | 🔵 构建Agent | 定时（凌晨）拉取最新代码 |
| 5.2 | 🔵 构建Agent | Mac mini并行构建 |
| 5.3 | 🔵 构建Agent | 部署到Windows测试机 |
| 5.4 | 🔵 测试Agent | 运行自动化测试 |
| 5.5 | 🔵 构建Agent | 生成测试报告→飞书机器人 |
| 5.6 | 🔵 构建Agent | 失败→创建高优任务@程序员 |

### 🟢 阶段6：版本发布与商店上架

| 步骤 | 角色 | 操作 |
|------|------|------|
| 6.1 | 🟢 制作人 | 飞书发起"发布审批"流程 |
| 6.2 | 🔵 发布Agent | 创建release分支并打tag |
| 6.3 | 🔵 发布Agent | Mac mini最终打包 |
| 6.4 | 🔵 发布Agent | 生成更新日志 |
| 6.5 | 🔵 发布Agent | 调用商店API上传（Steam/App Store/Google Play） |
| 6.6 | 🔵 发布Agent | 定期检查审核状态→飞书通知 |

### 🟢 阶段7：运维与社区反馈

| 步骤 | 角色 |操作 |
|------|------|------|
| 7.1 | 🔵 运维Agent | 监控崩溃报告（Crashlytics）→自动分类→创建Bug任务 |
| 7.2 | 🔵 社区Agent | 监听Discord/Telegram→AI提取关键词→飞书汇总 |
| 7.3 | 🔵 运维Agent | 每周生成运营周报→飞书群发送 |

---

## ⚙️ 最小可行工具（MVP）

### Phase 1（立即可启动）
1. **飞书机器人 + OpenClaw基础调度**
   - 树莓派部署飞书自定义机器人
   - 监听关键词触发AI生成

2. **AI资源生成自动化**
   - 轮询飞书表单→调用SD/Midjourney→存入NAS

3. **夜间自动构建 + 飞书通知**
   - Mac mini配置Jenkins/GitHub Actions Runner
   - 凌晨3点构建→飞书推送结果

---

## 🎯 团队与角色

**完整组织架构见 [docs/ORGANIZATION.md](../docs/ORGANIZATION.md)**

- Vanguard001（主控）、Jarvis / CodeForge / Newton（开发团队）、Tesla（专职测试团队）
- 开发团队含：主管、架构师、开发、DevOps、游戏美术、Scrum Master；Tesla 含架构师、Scrum Master、测试成员
- 本文档不重复列举，以 ORGANIZATION.md 为准

---

*文档更新时间: 2026-03-04*
*当前流程：遵循 DEVELOPMENT_FLOW.md；本文档为未来完整流水线目标*
