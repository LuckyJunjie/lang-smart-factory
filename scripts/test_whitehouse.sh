#!/bin/bash
# Hourly Godot test for whitehouse-decision
# Cron: 30 * * * * /home/pi/.openclaw/workspace/smart-factory/scripts/test_whitehouse.sh

PROJECT="/home/pi/.openclaw/workspace/whitehouse-decision"
LOG_DIR="/home/pi/.openclaw/workspace/smart-factory/logs/whitehouse"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/test_${TIMESTAMP}.log"
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/19f6bbd4-10bf-4242-acf0-5a4f960781ce"

mkdir -p "$LOG_DIR"

echo "[$(date)] Starting whitehouse-decision test..." >> "$LOG_FILE" 2>&1

# Change to project directory
cd "$PROJECT"

# Test 1: Godot headless parse check
echo "=== Godot Parse Check ===" >> "$LOG_FILE" 2>&1
timeout 30 godot --headless --quit 2>&1 | tee -a "$LOG_FILE"
GODOT_EXIT=$?

if [ $GODOT_EXIT -eq 0 ]; then
    echo "✓ Godot parse check PASSED" >> "$LOG_FILE" 2>&1
    GODOT_OK=1
else
    echo "✗ Godot parse check FAILED (exit $GODOT_EXIT)" >> "$LOG_FILE" 2>&1
    GODOT_OK=0
fi

# Test 2: Run Python test suite
echo "" >> "$LOG_FILE" 2>&1
echo "=== Python Test Suite ===" >> "$LOG_FILE" 2>&1
PYTEST_OK=1
if [ -d test ]; then
    timeout 60 python3 -m pytest test/ -v 2>&1 | tee -a "$LOG_FILE"
    
    # Check for FAILED in output
    if grep -q "FAILED" "$LOG_FILE"; then
        echo "✗ Python tests FAILED" >> "$LOG_FILE" 2>&1
        PYTEST_OK=0
    else
        echo "✓ Python tests PASSED" >> "$LOG_FILE" 2>&1
    fi
else
    echo "⚠ No test directory found" >> "$LOG_FILE" 2>&1
fi

# Test 3: Godot scene tests
echo "" >> "$LOG_FILE" 2>&1
echo "=== Godot Scene Tests ===" >> "$LOG_FILE" 2>&1
SCENE_OK=1
if [ -f test/test_godot_scenes.py ]; then
    timeout 60 python3 test/test_godot_scenes.py 2>&1 | tee -a "$LOG_FILE"
    
    # Check for FAILED in output
    if grep -q "FAILED" "$LOG_FILE"; then
        echo "✗ Godot scene tests FAILED" >> "$LOG_FILE" 2>&1
        SCENE_OK=0
    else
        echo "✓ Godot scene tests PASSED" >> "$LOG_FILE" 2>&1
    fi
fi

echo "" >> "$LOG_FILE" 2>&1

# Summary
if [ $GODOT_OK -eq 1 ] && [ $PYTEST_OK -eq 1 ] && [ $SCENE_OK -eq 1 ]; then
    echo "[$(date)] Test completed: ✅ 通过" >> "$LOG_FILE" 2>&1
    RESULT="✅ 通过"
    # Send success to Feishu
    curl -s -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"🏛️ **Whitehouse Decision 测试** - $(date '+%H:%M')\n✅ 测试通过\n📊 Godot解析: ✅\n🧪 Python用例: ✅\n🖼️ 场景测试: ✅\n⏰ 下次测试: 1小时后\"}}" > /dev/null 2>&1
else
    echo "[$(date)] Test completed: ❌ 失败" >> "$LOG_FILE" 2>&1
    RESULT="❌ 失败"
    # Send failure to Feishu
    curl -s -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"🏛️ **Whitehouse Decision 测试** - $(date '+%H:%M')\n⚠️ 测试失败\n请检查日志: ${LOG_FILE}\"}}" > /dev/null 2>&1
fi

echo "" >> "$LOG_FILE" 2>&1
echo "Log: $LOG_FILE"
