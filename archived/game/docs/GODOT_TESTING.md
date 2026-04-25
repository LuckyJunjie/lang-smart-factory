# Godot 自动化测试方案

**基于 GdUnit4 + GDSnap 的多平台测试框架**

---

## 概述

本文档描述 Godot 项目的自动化测试工具链：单元测试（GdUnit4）、截图对比（GDSnap）、脚本集成、控制台日志校验，以及 Windows / Linux / Mac 多平台测试矩阵。

**数据说明：** 测试结果与需求状态以 Smart Factory 数据库为准，本目录不维护独立状态。

---

## 核心工具

### 1. GdUnit4 - 单元/集成测试

**类比:** Jest (JavaScript)

**功能:**
- 单元测试、集成测试
- Headless 模式、CI/CD 命令行
- 场景模拟 (Scene Runner)
- JUnit XML / HTML 报告

**安装:**
```bash
# AssetLib 搜索 "GdUnit4" 或
# https://github.com/godot-gdunit-labs/gdUnit4
```

**命令行运行:**
```bash
godot --path <project> --headless -s addons/gdunit4/bin/gdunit4_cmdline.gd -t+
godot --path <project> --headless -s addons/gdunit4/bin/gdunit4_cmdline.gd -r junit -o ./reports/
```

### 2. GDSnap - 截图对比

**类比:** jest-image-snapshot

**功能:**
- 保存基准截图
- 自动比对差异，高亮变化区域
- 可与 GdUnit4 集成

**安装:**
```bash
# AssetLib 搜索 "GDSnap" 或
# https://github.com/Nokorpo/GDSnap
```

** standalone 模式:**
```bash
godot --headless --script "res://addons/gdsnap/view/cli.gd"
```

**与 GdUnit4 集成:**
```gdscript
GDSnap.update_base_screenshot()   # 生成基准图
GDSnap.take_screenshot("name")     # 对比并返回差异
```

---

## 测试类型与流程

### 1. GdUnit4 单元/集成测试

```
编写测试 → 本地运行 → CI 运行 → 生成报告
```

### 2. GDSnap 截图测试

```
1. 生成基准图 (update_base_screenshot)
2. 运行场景 → 截图
3. 对比差异 → 失败则输出 diff 图
```

### 3. 脚本测试（集成 GdUnit4 + GDSnap）

脚本可串联：运行 GdUnit4 → 运行 GDSnap 截图测试 → 检查控制台输出。

---

## 脚本测试集成

### 示例：run_tests.sh

```bash
#!/bin/bash
# 运行 GdUnit4 + GDSnap 截图测试，并检查控制台无 ERROR

set -e
PROJECT_PATH="${1:-.}"
GODOT="${GODOT:-godot}"

# 1. 运行 GdUnit4
$GODOT --path "$PROJECT_PATH" --headless \
  -s addons/gdunit4/bin/gdunit4_cmdline.gd -t+ -r junit -o ./reports/
GDUNIT_EXIT=$?

# 2. 运行 GDSnap 截图测试（若存在）
if [ -f "$PROJECT_PATH/addons/gdsnap/view/cli.gd" ]; then
  $GODOT --path "$PROJECT_PATH" --headless \
    --script "res://addons/gdsnap/view/cli.gd" 2>/dev/null || true
fi

# 3. 控制台日志检查（见下方）
exit $GDUNIT_EXIT
```

### 调用 GDSnap 的 GdUnit4 测试用例

```gdscript
# test_pinball.gd
extends GdUnitTest

func test_ball_launch_screenshot() -> void:
    var scene = load("res://scenes/Main.tscn").instantiate()
    add_child(scene)
    await get_tree().process_frame
    
    # 模拟发射
    var input = InputEventAction.new()
    input.action = "ui_accept"
    input.pressed = true
    Input.parse_input_event(input)
    await get_tree().create_timer(1.0).timeout
    
    # GDSnap 截图对比
    GDSnap.take_screenshot("ball_launched")
```

---

## 控制台日志测试

### 问题

Godot 4.x 会输出内部 `ERROR` 级别日志，并非真实错误，导致 CI 误报。

### 方案

**推荐：** 只检测致命错误，忽略 Godot 内部日志：

```bash
# 只检测致命错误（推荐）
if grep -qE "FATAL|CRASH|Segmentation fault|Assertion failed" console_output.log; then
  echo "Fatal error detected"
  exit 1
fi

# 不推荐：检测所有 ERROR（易误报）
# if grep -q "ERROR" console_output.log; then ...
```

### 捕获控制台输出

```bash
$GODOT --path "$PROJECT_PATH" --headless -s addons/gdunit4/bin/gdunit4_cmdline.gd -t+ 2>&1 | tee console_output.log
```

---

## 多平台测试矩阵

### Windows / Linux / Mac

| 平台 | Godot 可执行文件 | 说明 |
|------|------------------|------|
| Linux | `Godot_v4.x-stable_linux.x86_64` | CI 常用 |
| Windows | `Godot_v4.x-stable_win64.exe` | CodeForge 测试机 |
| macOS | `Godot.app/Contents/MacOS/Godot` | Mac mini 开发 |

### GitHub Actions 矩阵示例

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Setup Godot
        run: |
          # 按平台下载对应 Godot
          # Linux: godotengine/godot-builds
          # Windows: 同上
          # macOS: 同上
      - name: Run GdUnit4
        run: godot --path . --headless -s addons/gdunit4/bin/gdunit4_cmdline.gd -t+
      - name: Run GDSnap
        if: hashFiles('addons/gdsnap/**') != ''
        run: godot --path . --headless --script "res://addons/gdsnap/view/cli.gd"
      - name: Check Console
        run: |
          # 仅检测 FATAL/CRASH，不检测通用 ERROR
```

### 本地多平台

| 机器 | 角色 | 测试 |
|------|------|------|
| CodeForge (Windows) | 开发/测试 | Godot 测试、截图 |
| Jarvis (Mac) | 开发 | 构建、GdUnit4 |
| Vanguard 树莓派 | 主控 | 调度，不跑 Godot |

---

## CI/CD 配置

### 最小工作流

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Godot
        uses: godotengine/godot-builds@v4
        with:
          version: "4.2"
      - name: Run GdUnit4
        run: godot --path . --headless -s addons/gdunit4/bin/gdunit4_cmdline.gd -t+
      - name: Run GDSnap
        run: godot --path . --headless --script "res://addons/gdsnap/view/cli.gd"
      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: reports/
```

---

## 实现步骤

### 1. 安装 GdUnit4
1. 打开 Godot 项目
2. AssetLib 搜索 "GdUnit4"
3. 下载并安装到 `addons/gdunit4/`

### 2. 安装 GDSnap
1. AssetLib 搜索 "GDSnap"
2. 下载并安装到 `addons/gdsnap/`

### 3. 创建测试
1. 创建 `test/` 目录
2. 编写 GdUnit4 测试脚本
3. 在测试中调用 `GDSnap.take_screenshot()` 做截图对比

### 4. 脚本测试
1. 编写 `run_tests.sh` 或 `run_tests.ps1`（Windows）
2. 串联 GdUnit4、GDSnap、控制台检查
3. 在 CI 中调用该脚本

### 5. 多平台配置
1. 配置 GitHub Actions 矩阵（Windows / Linux / Mac）
2. 或使用 CodeForge (Windows)、Jarvis (Mac) 分别运行

---

## 与 Smart Factory 集成

- 测试结果、需求状态以 **Smart Factory DB** 为准
- 测试通过/失败可写入需求或任务备注
- 本目录不维护与 DB 冲突的状态文档

---

*最后更新: 2026-03-04*
