# Windows Exporter Installation Guide

## Method 1: Chocolatey (Recommended)
```powershell
# Install Chocolatey if not present
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install windows_exporter
choco install windows_exporter -y
```

## Method 2: Manual Download
1. Download from: https://github.com/prometheus-community/windows_exporter/releases
2. Run the MSI installer
3. Configure service to start automatically

## Configuration
- Default port: 9182
- Metrics URL: http://localhost:9182/metrics

## Service Management
```powershell
# Start service
Start-Service windows_exporter

# Check status
Get-Service windows_exporter
```
