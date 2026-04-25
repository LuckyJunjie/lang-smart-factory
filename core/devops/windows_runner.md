# Windows Runner 部署配置

## 概述

Windows Runner 用于在 Windows 系统上执行 CI/CD 构建任务。

## 部署要求

- Windows 10/11 或 Windows Server 2019+
- Docker Desktop (Linux containers mode)
- 至少 4GB RAM
- 至少 20GB 可用磁盘空间

## 快速开始

### 1. 安装 Docker

下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### 2. 配置 Drone Runner

```powershell
# 拉取 Drone Runner 镜像
docker pull drone/drone-runner-docker

# 启动 Runner (替换以下变量)
# DRONE_RPC_HOST: Drone Server 地址
# DRONE_RPC_SECRET: 与 Drone Server 相同的密钥

docker run --detach `
  --volume //./pipe/docker_engine://./pipe/docker_engine `
  --env DRONE_RPC_PROTO=http `
  --env DRONE_RPC_HOST=192.168.3.75:3001 `
  --env DRONE_RPC_SECRET=your-shared-secret `
  --env DRONE_RUNNER_CAPACITY=2 `
  --env DRONE_RUNNER_NAME=windows-runner `
  --env DRONE_DEBUG=true `
  --publish 3002:3000 `
  --restart=always `
  --name=drone-runner-windows `
  drone/drone-runner-docker
```

### 3. 验证 Runner

```powershell
# 查看 Runner 日志
docker logs drone-runner-windows

# 查看 Runner 列表 (在 Drone Server 上)
curl http://192.168.3.75:3001/api/runner
```

## 配置说明

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| DRONE_RPC_PROTO | RPC 协议 | http |
| DRONE_RPC_HOST | Drone Server 地址 | 192.168.3.75:3001 |
| DRONE_RPC_SECRET | 共享密钥 | super-secret-token |
| DRONE_RUNNER_CAPACITY | 并行任务数 | 2 |
| DRONE_RUNNER_NAME | Runner 名称 | windows-runner |
| DRONE_DEBUG | 调试模式 | true |

### Windows 特定配置

#### 使用 PowerShell 执行器

```yaml
# .drone.yml
kind: pipeline
type: docker
name: windows-build

platform:
  os: windows
  arch: amd64

steps:
  - name: build
    image: mcr.microsoft.com/windows/servercore:ltsc2022
    commands:
      - powershell -Command "Write-Host 'Hello from Windows Runner'"
      - dotnet build
```

#### Windows 容器池配置

在 Windows 上，Docker 容器需要使用 Windows 容器:

```powershell
# 切换到 Windows 容器
& 'C:\Program Files\Docker\Docker\DockerCli.exe' -SwitchDaemon
```

## 故障排查

### Runner 未连接

1. 检查网络连通性
```powershell
Test-NetConnection -ComputerName 192.168.3.75 -Port 3001
```

2. 检查 Runner 日志
```powershell
docker logs drone-runner-windows
```

### 权限问题

确保 Docker daemon API 可访问:
```powershell
# 检查 Docker 服务状态
Get-Service Docker
```

### Windows 容器问题

如果使用 Windows 容器，确保:
1. 已启用 Windows 容器功能
2. 基础镜像正确 (servercore 或 nanoserver)

## 流水线示例

### .NET 项目构建

```yaml
kind: pipeline
type: docker
name: dotnet-build

platform:
  os: windows
  arch: amd64

steps:
  - name: restore
    commands:
      - dotnet restore

  - name: build
    commands:
      - dotnet build --configuration Release

  - name: test
    commands:
      - dotnet test --no-build

  - name: publish
    commands:
      - dotnet publish -o ./publish
```

### Godot 项目构建

```yaml
kind: pipeline
type: docker
name: godot-build

platform:
  os: windows
  arch: amd64

steps:
  - name: setup
    commands:
      - choco install godot -y
      - choco install godot-tools -y

  - name: build
    commands:
      - godot --headless --export-release "Windows" build.exe

  - name: artifacts
    commands:
      - powershell Compress-Archive -Path build.exe -DestinationPath artifact.zip
    when:
      status:
        - success
```

## 监控

检查 Runner 状态:

```powershell
# 查看 Runner 容器
docker ps | grep drone-runner

# 查看资源使用
docker stats drone-runner-windows
```

## 更新 Runner

```powershell
# 停止容器
docker stop drone-runner-windows

# 删除容器
docker rm drone-runner-windows

# 拉取最新镜像
docker pull drone/drone-runner-docker

# 重新运行 (使用之前的命令)
```
