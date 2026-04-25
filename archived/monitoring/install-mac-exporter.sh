#!/bin/bash
# macOS Exporter Installation Script for Mac mini (Jarvis)
# Run on: jarvis (Mac mini)

set -e

EXPORTER_PORT=9100
EXPORTER_DIR="$HOME/macos-exporter"
METRICS_URL="http://localhost:$EXPORTER_PORT/metrics"

echo "===== macOS Exporter 安装 ====="

# 检查是否已安装
if curl -s "$METRICS_URL" > /dev/null 2>&1; then
    echo "macOS exporter 已在运行"
    curl -s "$METRICS_URL" | head -5
    exit 0
fi

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 安装 prometheus (包含 macOS exporter)
echo "安装 Prometheus..."
brew install prometheus

# 创建 exporter 配置
mkdir -p "$EXPORTER_DIR"
cat > "$EXPORTER_DIR/config.yml" << 'EOF'
collectors:
  - cpu
  - memory
  - disk
  - network
  - load
  - processes
EOF

# 下载 macOS exporter
echo "下载 macOS exporter..."
cd "$EXPORTER_DIR"

# 尝试下载最新版本
EXPORTER_VERSION="1.2.0"
curl -L -o macos_exporter "https://github.com/prometheus-community/macOS_exporter/releases/download/v${EXPORTER_VERSION}/macOS_exporter-${EXPORTER_VERSION}-darwin-amd64"

chmod +x macos_exporter

# 启动 exporter
echo "启动 macOS exporter..."
./macos_exporter --web.listen-address=:$EXPORTER_PORT &
sleep 2

# 验证
if curl -s "$METRICS_URL" > /dev/null 2>&1; then
    echo "✓ macOS exporter 安装成功!"
    echo "  指标地址: $METRICS_URL"
    curl -s "$METRICS_URL" | head -10
else
    echo "✗ 安装失败"
    exit 1
fi

# 添加到 launchd (可选)
echo ""
echo "如需开机自启，可运行:"
echo "  cp com.macos.exporter.plist ~/Library/LaunchAgents/"
echo "  launchctl load ~/Library/LaunchAgents/com.macos.exporter.plist"
