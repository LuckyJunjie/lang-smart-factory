# Godot 游戏游玩与测试方法（2026-04 最新）

> 更新日期: 2026-04-16
> 来源: smart-factory docs + pinball-experience 测试实践

---

## 1. 测试工具链

| 工具 | 用途 | 状态 |
|------|------|------|
| **GDSnap** | 截图测试（截图对比） | ✅ 已安装 (`addons/gdsnap/`) |
| **GdUnit4** | 单元测试框架 | ⚠️ 插件损坏 |
| **GUT** | 替代测试框架 | ✅ 已安装 (`addons/gut/`) |
| **MCP Server** | 远程控制 Godot | ✅ 已部署 |
| **FFmpeg** | 视频转码 | ✅ 已安装 |

---

## 2. 测试脚本编写规范

### 2.1 测试脚本结构（SceneTree 模式）

```gdscript
extends SceneTree

var tests_passed := 0
var tests_failed := 0

func _initialize() -> void:
    # 加载主场景
    var main = load("res://scenes/Main.tscn").instantiate()
    root.add_child(main)
    await create_timer(1.0).timeout
    
    run_all_tests()
    
    print("测试结果: %d 通过, %d 失败" % [tests_passed, tests_failed])
    
    # 清理资源
    cleanup()
    quit()

func run_all_tests() -> void:
    test_example()

func test_example() -> void:
    var node = root.find_child("NodeName", true, false)
    if node:
        print("✓ test_example PASS")
        tests_passed += 1
    else:
        print("✗ test_example FAIL")
        tests_failed += 1
```

### 2.2 截图测试

```gdscript
extends SceneTree

var screenshot_dir = "res://test/screenshot/"

func _initialize():
    await take_screenshots()
    quit()

func take_screenshots():
    var main = load("res://scenes/Main.tscn").instantiate()
    root.add_child(main)
    await process_frame
    
    var viewport = get_viewport()
    var image = viewport.get_texture().get_image()
    image.save_png(screenshot_dir + "current/main_scene.png")
    main.free()
```

---

## 3. 运行测试命令

### 3.1 本地运行（无显示器）

```bash
# 使用 Xvfb 运行
xvfb-run -a -s '-screen 0 1280x720x24' godot --headless --quit

# 或使用显示编号
DISPLAY=:99 godot --headless --quit

# 运行测试脚本
xvfb-run -a -s '-screen 0 1280x720x24' godot --headless -s test/run_tests.gd
```

### 3.2 GPU 运行（截图/视频）

```bash
# 检测 GPU
GPU_DISPLAY=""
for lock in /tmp/.X*-lock; do
    d=":${lock##/tmp/.X}"; d="${d%-lock}"
    if DISPLAY=$d timeout 2 glxinfo 2>/dev/null | grep -qi nvidia; then
        GPU_DISPLAY=$d; break
    fi
done

# 截图（GPU 加速）
DISPLAY=$GPU_DISPLAY godot --rendering-method forward_plus --write-movie screenshots/output.png --fixed-fps 10 --quit-after 30 -s test/run_tests.gd

# 视频（需 GPU）
DISPLAY=$GPU_DISPLAY godot --rendering-method forward_plus --write-movie screenshots/output.avi --fixed-fps 30 --quit-after 900 -s test/run_tests.gd
```

### 3.3 CI 持续集成

```bash
# 自动测试脚本 (pinball-experience)
cd /path/to/game
xvfb-run -a -s '-screen 0 1280x720x24' godot --headless -s test/run_tests.gd

# 检查退出码
if [ $? -eq 0 ]; then
    echo "所有测试通过"
else
    echo "测试失败"
fi
```

---

## 4. MCP Server 远程控制

### 4.1 部署架构

```
┌──────────────────────────────────────┐
│  MCP Server (Newton / 192.168.3.82)  │
│  Python Daemon (:9876)               │
│  Node.js MCP Subprocess             │
│  Godot (headless)                   │
└──────────────────────────────────────┘
         ▲ HTTP API
         │
┌──────────────────────────────────────┐
│  OpenClaw Agents (Tesla等)          │
└──────────────────────────────────────┘
```

### 4.2 API 端点

```bash
# 健康检查
curl http://192.168.3.82:9876/health

# 截图
curl http://192.168.3.82:9876/screenshot > screenshot.json

# 启动 Godot
curl http://192.168.3.82:9876/start

# 发送按键
curl "http://192.168.3.82:9876/key?key=space"

# 执行 GDScript
curl -X POST http://192.168.3.82:9876/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "game_eval", "arguments": {"code": "print(GameManager.score)"}}'
```

### 4.3 Python 调用示例

```python
import requests, base64, json

MCP_HOST = "http://192.168.3.82:9876"

def screenshot():
    r = requests.get(f"{MCP_HOST}/screenshot")
    d = r.json()
    img_data = d["result"]["content"][0]["data"]
    return base64.b64decode(img_data)

def send_key(key="space"):
    requests.get(f"{MCP_HOST}/key?key={key}")

def game_state():
    requests.post(f"{MCP_HOST}/call", json={
        "tool": "game_eval",
        "arguments": {"code": "print(GameManager.score)"}
    })
```

---

## 5. 截图对比（Visual QA）

### 5.1 静态场景对比

```bash
mkdir -p visual-qa
N=$(ls visual-qa/*.md 2>/dev/null | wc -l); N=$((N + 1))

python3 openclaw-knowledge/skills/godot-task/scripts/visual_qa.py \
  --context "Goal: 验证场景正确性..." \
  reference.png screenshots/task/frame0003.png > visual-qa/${N}.md
```

### 5.2 动态场景对比（多帧）

```bash
# 示例: 10fps 捕获, 每5帧采样
STEP=5  # capture_fps / 2
FRAMES=$(ls screenshots/{task}/frame*.png | awk "NR % $STEP == 0")

python3 openclaw-knowledge/skills/godot-task/scripts/visual_qa.py \
  --context "Goal: 验证游戏玩法..." \
  reference.png $FRAMES > visual-qa/${N}.md
```

---

## 6. 玩家体验游玩（Tesla 测试团队）

### 6.1 游玩命令

```bash
# 启动游戏并游玩关键流程
cd /path/to/game
xvfb-run -a -s '-screen 0 1280x720x24' godot --quit

# 运行玩家视角测试
godot --headless -s test/player_perspective.gd
```

### 6.2 游玩检查清单

- [ ] 游戏启动无崩溃
- [ ] 主菜单可正常访问
- [ ] 游戏核心玩法可执行
- [ ] UI 元素显示正确
- [ ] 视觉效果符合预期
- [ ] 无明显卡顿或掉帧

### 6.3 体验改进点记录

发现体验问题时：
1. 截图记录
2. 记录具体问题（UI重叠、引导不足、平衡问题等）
3. 创建 `enhancement` 类型需求

```bash
# 创建体验改进需求
cli project create-requirement \
  --type enhancement \
  --title "改进: XXX引导" \
  --description "问题描述..."
```

---

## 7. 测试报告输出

### 7.1 测试报告模板

```markdown
# 测试报告 - [需求名称]

**测试时间:** YYYY-MM-DD
**测试人:** Tesla
**测试结果:** ✅ 通过 / ❌ 失败

## 测试用例

| 用例ID | 描述 | 结果 | 备注 |
|--------|------|------|------|
| TC001 | 场景加载 | ✅ | |
| TC002 | UI显示 | ✅ | |

## 问题记录

| 问题ID | 描述 | 严重程度 | 状态 |
|--------|------|----------|------|
| BUG001 | XXX | 高 | 待修复 |

## 证据截图

![screenshot1](screenshots/xxx.png)
```

---

## 8. Smart Factory 集成

### 8.1 测试任务工作流

```
收到需求 (status=developed, assignee=tesla)
    ↓
领取任务
    ↓
运行测试 (cli godot run-tests / cli test run-unit-tests)
    ↓
发现 Bug → 创建 bug 需求 → 上报
    ↓
测试通过 → 更新状态为 tested → 上报
```

### 8.2 关键命令

```bash
# 领取测试任务
cli project take-requirement <id> --team tesla --agent tesla

# 运行 Godot 场景测试
cli godot run-scene <scene_path>

# 运行单元测试
cli test run-unit-tests

# 更新需求状态
cli project update-requirement <id> --fields '{"status":"tested"}'

# 上报状态
cli project report-status
```

---

## 9. 常见问题处理

### 9.1 截图为空
- 检查 GPU 驱动是否正常
- 确认 `--write-movie` 路径可写

### 9.2 测试脚本无响应
- 添加 `quit()` 调用
- 检查 `root.add_child()` 是否正确

### 9.3 Godot 进程卡死
- 使用 `timeout` 命令包装
- 检查内存泄漏（清理 `queue_free()`）

---

## 10. 参考文档

- [GODOT_SKILLS_AND_TESTING.md](./GODOT_SKILLS_AND_TESTING.md)
- [GODOT_MCP_DEPLOYMENT.md](./GODOT_MCP_DEPLOYMENT.md)
- [HIGH_REQUIREMENTS.md](./HIGH_REQUIREMENTS.md)
- [godot-task SKILL.md](../openclaw-knowledge/skills/godot-task/SKILL.md)
- [GAME_DEVELOPMENT_GOLDEN_RULES.md](./GAME_DEVELOPMENT_GOLDEN_RULES.md)
