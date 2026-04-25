# Node Exporter Installation Script for Linux/macOS
# Run on: vanguard (Raspberry Pi), jarvis (Mac mini)

#!/bin/bash

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Start Node Exporter container
echo "Starting Node Exporter..."
docker run -d \
    --name node_exporter \
    --net="host" \
    --restart unless-stopped \
    prom/node-exporter \
    --collector.systemd \
    --collector.cpu \
    --collector.meminfo \
    --collector.diskstats

echo "Node Exporter installed!"
echo "Metrics available at: http://localhost:9100/metrics"
