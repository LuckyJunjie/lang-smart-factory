# macOS Exporter Installation Guide

Mac runner 使用 macOS exporter 收集系统指标。

## Method 1: Homebrew (Recommended)

```bash
# Install prometheus with macOS support
brew install prometheus

# Or install just the exporter
brew install prometheus/prometheus/macOS_exporter
```

## Method 2: Manual Installation

1. Download macOS exporter from: https://github.com/prometheus-community/macOS_exporter/releases
2. Extract and run:
```bash
./macos_exporter --web.listen-address=:9100
```

## Configuration

- Default port: 9100 (与 Node Exporter 相同)
- Metrics URL: http://localhost:9100/metrics

## Service Management (LaunchDaemon)

创建 `/Library/LaunchDaemons/com.macos.exporter.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.macos.exporter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/macos_exporter</string>
        <string>--web.listen-address=:9100</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

加载服务:
```bash
sudo launchctl load /Library/LaunchDaemons/com.macos.exporter.plist
```

## Prometheus 配置

添加到 `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mac-mini'
    static_configs:
      - targets: ['192.168.3.79:9100']
        labels:
          instance: 'jarvis'
          os: 'macos'
```

## 收集的指标

| 指标 | 说明 |
|------|------|
| macos_cpu_usage | CPU 使用率 |
| macos_memory_usage | 内存使用 |
| macos_disk_usage | 磁盘使用 |
| macos_network_io | 网络 I/O |
| macos_process_count | 进程数量 |

## 状态检查

```bash
# 检查服务状态
sudo launchctl list | grep macos.exporter

# 检查指标
curl http://localhost:9100/metrics | head -20
```

## 防火墙配置

```bash
# 允许 exporter 端口
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --addapp=/usr/local/bin/macos_exporter
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unsetappaslegacyapp=/usr/local/bin/macos_exporter
```
