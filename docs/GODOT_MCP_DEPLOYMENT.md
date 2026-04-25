# Godot MCP Server 部署指南

> 版本: 1.0 | 创建: 2026-04-16
> 用途: 让 OpenClaw AI Agent 通过 MCP 协议"看见"并操作 Godot 游戏
> 部署架构: **集中式 MCP 服务器** — 一台机器部署，其他 OpenClaw 通过 HTTP API 调用

---

## 架构概述

```
┌─────────────────────────────────────────────────────────┐
│                   集中式 MCP Server                       │
│  ┌─────────────────┐    ┌─────────────────────────┐   │
│  │  Python Daemon  │    │  Node.js MCP Subprocess │   │
│  │  (HTTP API :9876)│◄──►│  (stdio 通信)           │   │
│  └─────────────────┘    └──────────┬──────────────┘   │
│                                      │                   │
│                           ┌──────────▼──────────────┐   │
│                           │  Godot (headless :9090) │   │
│                           │  /tmp/pinball.png       │   │
│                           └─────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
              ▲                 ▲                  ▲
              │ HTTP :9876      │                  │
       ┌──────┴──────┐  ┌───────┴───────┐  ┌────┴────┐
       │ OpenClaw 1  │  │ OpenClaw 2    │  │ OpenClaw N │
       │ (Newton)    │  │ (Einstein)   │  │ (其他)      │
       └─────────────┘  └───────────────┘  └─────────┘
```

**核心思路**：
- MCP Server 部署在**一台机器**（如 Newton / 192.168.3.82）
- 所有 OpenClaw Agent 通过 **HTTP API** 调用工具
- MCP Subprocess 持久运行，Godot 进程按需启停

---

## 快速部署

### Step 1: 部署机器（Newton）安装 MCP Server

```bash
# 克隆 MCP Server
cd /home/pi/.openclaw/workspace/smart-factory/tools

# 下载 godot-mcp (149 tools)
git clone https://github.com/tugcantopaloglu/godot-mcp.git godot-mcp-149

# 安装依赖
cd godot-mcp-149
npm install
npm run build

# 启动持久化 Daemon (后台运行)
cd /home/pi/.openclaw/workspace/smart-factory/tools
nohup python3 godot-mcp-server.py > /tmp/godot-mcp.log 2>&1 &
```

### Step 2: 其他机器（OpenClaw Agents）调用

**直接 curl 调用 HTTP API：**
```bash
# 健康检查
curl http://192.168.3.82:9876/health

# 获取截图
curl http://192.168.3.82:9876/screenshot > screenshot.json

# 启动 Godot
curl http://192.168.3.82:9876/start

# 发送按键
curl http://192.168.3.82:9876/key

# 发送点击
curl http://192.168.3.82:9876/click
```

**Python 调用示例：**
```python
import requests, base64, json

MCP_HOST = "http://192.168.3.82:9876"

def screenshot():
    r = requests.get(f"{MCP_HOST}/screenshot")
    d = r.json()
    img_data = d["result"]["content"][0]["data"]
    return base64.b64decode(img_data)

def send_key(key="space"):
    requests.get(f"{MCP_HOST}/key")

def game_state():
    requests.post(f"{MCP_HOST}/call", json={"tool": "game_eval", "arguments": {"code": "print(GameManager.score)"}})
```

### Step 3: 集成到 OpenClaw Skill

创建 skill 文件：`~/.openclaw/skills/godot-mcp-gateway/`
```python
#!/usr/bin/env python3
"""OpenClaw Godot MCP Gateway - 调用远程 MCP 服务器"""
import requests
import base64
import json
import sys

MCP_HOST = "http://192.168.3.82:9876"

def screenshot():
    r = requests.get(f"{MCP_HOST}/screenshot", timeout=15)
    d = r.json()
    img_data = d["result"]["content"][0]["data"]
    return base64.b64decode(img_data)

def send_key(key="space"):
    requests.get(f"{MCP_HOST}/key", timeout=10)

def send_click(x=640, y=360):
    requests.get(f"{MCP_HOST}/click", timeout=10)

def start_godot(project="/home/pi/.openclaw/workspace/pinball-experience"):
    requests.get(f"{MCP_HOST}/start", timeout=15)

def eval_gdscript(code):
    requests.post(f"{MCP_HOST}/call", json={"tool": "game_eval", "arguments": {"code": code}}, timeout=10)

def health():
    r = requests.get(f"{MCP_HOST}/health", timeout=5)
    return r.json()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "health"
    if cmd == "screenshot":
        with open("/tmp/mcp_screenshot.png", "wb") as f:
            f.write(screenshot())
        print("/tmp/mcp_screenshot.png")
    elif cmd == "key":
        send_key(sys.argv[2] if len(sys.argv) > 2 else "space")
        print("OK")
    elif cmd == "click":
        x = int(sys.argv[2]) if len(sys.argv) > 2 else 640
        y = int(sys.argv[3]) if len(sys.argv) > 3 else 360
        send_click(x, y)
        print("OK")
    elif cmd == "start":
        start_godot()
        print("OK")
    elif cmd == "eval":
        print(eval_gdscript(sys.argv[2] if len(sys.argv) > 2 else "print(1)"))
    else:
        print(json.dumps(health()))
```

---

## HTTP API 端点

| 端点 | 方法 | 说明 | 返回 |
|------|------|------|------|
| `/health` | GET | 健康检查 | `{"status": "ok", "mcp_running": true}` |
| `/start` | GET | 启动 Godot 项目 | 启动结果 |
| `/stop` | GET | 停止 Godot | 停止结果 |
| `/screenshot` | GET | 获取截图 | `{"result": {"content": [{"type": "image", "data": "base64..."}]}}` |
| `/key` | GET | 发送空格键 | 发送结果 |
| `/click` | GET | 点击中心 | 发送结果 |
| `/eval` | GET | 执行 GDScript | 执行结果 |
| `/restart` | GET | 重启 MCP 子进程 | 重启结果 |
| `/call` | POST | 调用任意 MCP 工具 | 工具返回 |

### POST /call 格式

```json
{
  "tool": "game_key_press",
  "arguments": {
    "keyName": "space"
  }
}
```

---

## MCP 工具列表 (部分)

| 工具名 | 说明 |
|--------|------|
| `get_godot_version` | 获取 Godot 版本 |
| `run_project` | 启动 Godot 项目 |
| `stop_project` | 停止 Godot |
| `game_screenshot` | 获取游戏截图 (base64) |
| `game_click` | 鼠标点击 |
| `game_mouse_move` | 鼠标移动 |
| `game_key_press` | 按键 |
| `game_hold_key` | 按住按键 |
| `game_release_key` | 释放按键 |
| `game_eval` | 执行 GDScript |
| `game_get_scene_tree` | 获取场景树 |
| `game_get_property` | 获取对象属性 |
| `game_set_property` | 设置对象属性 |
| `get_screenshot_as_file` | 保存截图到文件 |

全部 149 个工具见：`tools/godot-mcp-149/`

---

## 完整工具链

```
OpenClaw Agent (任意机器)
         │
         │ HTTP :9876
         ▼
┌─────────────────────────────────┐
│   Python Daemon (MCP Gateway)   │
│   tools/godot-mcp-server.py     │
│         │                       │
│         │ stdio (Node.js)       │
│         ▼                       │
│   Node.js MCP Subprocess        │
│   godot-mcp-149/build/index.js  │
│         │                       │
│         │ WebSocket :9090       │
│         ▼                       │
│   Godot Engine (headless)       │
│   --headless --port 9090       │
└─────────────────────────────────┘
```

---

## 部署检查清单

- [x] Godot 安装 (v4.5.stable)
- [x] Node.js 安装
- [x] Python 3 安装
- [x] MCP Server 源码下载
- [x] npm install + npm run build
- [x] Daemon 后台启动
- [x] HTTP API 端口开放 (9876)
- [x] 测试截图功能
- [ ] 测试输入自动化
- [ ] 集成到 OpenClaw Skill
- [ ] 配置其他机器远程调用

---

## 故障排查

```bash
# 检查 daemon 是否运行
curl http://localhost:9876/health

# 查看日志
tail -f /tmp/godot-mcp.log

# 重启 daemon
pkill -f godot-mcp-server
cd /home/pi/.openclaw/workspace/smart-factory/tools
nohup python3 godot-mcp-server.py > /tmp/godot-mcp.log 2>&1 &

# 检查端口
netstat -tlnp | grep 9876
```

---

## 适用场景

| 场景 | 适用性 |
|------|--------|
| AI 玩游戏的自动化测试 | ✅ 完美 |
| 截图 + 视觉模型分析 | ✅ 截图返回 base64 PNG |
| 自动化冒烟测试 | ✅ 连续按键/点击 |
| 游戏状态监控 | ✅ GDScript eval 查询 |
| 跨设备 AI 协作 | ✅ HTTP API 支持远程调用 |

---

## 参考资料

- MCP Server: `tools/godot-mcp-149/` (GitHub: tugcantopaloglu/godot-mcp)
- Daemon 源码: `tools/godot-mcp-server.py`
- Godot 版本: 4.5.stable.official
- MCP 协议: https://modelcontextprotocol.io
