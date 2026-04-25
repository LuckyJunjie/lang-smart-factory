# Godot MCP Server 实施计划

> 创建时间: 2026-04-16
> 状态: **已实现** ✅
> 参考: pinball-experience/docs/tools/godot_mcp.md, godot_mcp方案.md

## 背景

让 OpenClaw AI Agent "看见"并操作 Godot 游戏，实现自动化测试。

## 已下载的工具

| 工具 | 路径 | 工具数 |
|------|------|--------|
| **tugcantopaloglu/godot-mcp** | `tools/godot-mcp-149` | 149 |
| **GodotIQ (salvo10f/godotiq)** | `tools/godotiq` | 35 |

## 已验证工作的 MCP 服务器

**运行命令：**
```bash
cd /home/pi/.openclaw/workspace/smart-factory/tools && nohup python3 godot-mcp-server.py > /tmp/godot-mcp.log 2>&1 &
```

**HTTP API 端点：**
```
GET /health      - 健康检查 (返回 mcp_running: true)
GET /start      - 启动 Godot 项目
GET /screenshot - 截图 (返回 base64 PNG)
GET /version    - Godot 版本 (返回 4.5.stable)
GET /key        - 按空格键
GET /click      - 点击屏幕中心
GET /eval       - 执行 GDScript
GET /stop       - 停止 Godot 项目
GET /restart    - 重启 MCP 子进程
POST /call      - 调用任意工具
```

**验证结果：**
- ✅ Node.js MCP subprocess 持久运行 (PID 保持不变)
- ✅ Godot 进程在 HTTP 请求间保持运行
- ✅ 截图返回有效 PNG (1357x1018 px, 45KB)
- ✅ 版本查询返回 `4.5.stable.official`
- ✅ 启停控制正常
- ⚠️ `get_scene_tree` 工具未找到

**工作原理：**
- Python daemon 启动 Node.js MCP subprocess (stdio 模式)
- Node subprocess 保持 stdin/stdout 连接
- HTTP 请求通过 Python 调用 MCP JSON-RPC
- MCP 工具 `run_project` 启动 Godot 并通过交互端口连接

**当前限制：**
- Godot 需要通过 `/start` 手动启动
- `game_screenshot` 返回 base64 PNG，需要解码
- 部分高级工具需要 Godot 运行中才能使用

## 关键文件

- `tools/godot-mcp-server.py` - Python 持久化 MCP 守护进程
- `tools/godot-mcp-149/` - MCP 服务器源码 (149 tools)
- `/tmp/pinball.png` - 测试截图 (1357x1018 PNG)

## 安装依赖

```bash
# godot-mcp-149 (TypeScript)
cd tools/godot-mcp-149
npm install
npm run build

# GodotIQ 插件版
# 复制 addons/ 到 Godot 项目
```

## 下一步

- [ ] 集成到 OpenClaw skill (通过 HTTP 调用)
- [ ] 测试游戏输入自动化 (连续按键、方向控制)
- [ ] 测试 GDScript 执行和状态查询
- [ ] 实现 "观察-思考-行动" 循环
- [ ] 截图发送给视觉模型分析

---

## 完整部署文档

**详细部署指南见**: `docs/GODOT_MCP_DEPLOYMENT.md`

包含：
- 集中式 MCP Server 架构
- HTTP API 端点说明
- 远程 OpenClaw Agent 调用方法
- Python/curl 调用示例
- 故障排查指南
