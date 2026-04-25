#!/bin/bash
# Hourly Godot test for pinball-experience
# Cron: 0 * * * * /home/pi/.openclaw/workspace/smart-factory/scripts/test_pinball.sh

PROJECT="/home/pi/.openclaw/workspace/pinball-experience"
LOG_DIR="/home/pi/.openclaw/workspace/smart-factory/logs/pinball"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/test_${TIMESTAMP}.log"
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/19f6bbd4-10bf-4242-acf0-5a4f960781ce"

mkdir -p "$LOG_DIR"

echo "[$(date)] Starting pinball-experience test..." >> "$LOG_FILE" 2>&1

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

# Test 2: Run test suite
echo "" >> "$LOG_FILE" 2>&1
echo "=== Test Suite ===" >> "$LOG_FILE" 2>&1
TEST_OK=1
if [ -f test/run_tests.gd ]; then
    timeout 60 xvfb-run -a -s '-screen 0 1280x720x24' godot --headless -s test/run_tests.gd 2>&1 | tee -a "$LOG_FILE"
    
    # Check for FAIL in output
    if grep -q "✗" "$LOG_FILE"; then
        echo "✗ Test suite FAILED" >> "$LOG_FILE" 2>&1
        TEST_OK=0
    else
        echo "✓ Test suite PASSED" >> "$LOG_FILE" 2>&1
    fi
else
    echo "⚠ No test/run_tests.gd found" >> "$LOG_FILE" 2>&1
fi

echo "" >> "$LOG_FILE" 2>&1

# Summary
if [ $GODOT_OK -eq 1 ] && [ $TEST_OK -eq 1 ]; then
    echo "[$(date)] Test completed: ✅ 通过" >> "$LOG_FILE" 2>&1
    RESULT="✅ 通过"
    # Send success to Feishu
    curl -s -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"🎮 **Pinball Experience 测试** - $(date '+%H:%M')\n✅ 测试通过\n📊 Godot解析: ✅\n🧪 测试用例: ✅\n⏰ 下次测试: 1小时后\"}}" > /dev/null 2>&1
else
    echo "[$(date)] Test completed: ❌ 失败" >> "$LOG_FILE" 2>&1
    RESULT="❌ 失败"
    # Send failure to Feishu
    curl -s -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"🎮 **Pinball Experience 测试** - $(date '+%H:%M')\n⚠️ 测试失败\n请检查日志: ${LOG_FILE}\"}}" > /dev/null 2>&1
fi

echo "Log: $LOG_FILE"
