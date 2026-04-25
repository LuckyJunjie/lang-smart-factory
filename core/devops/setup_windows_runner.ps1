# Windows Runner Setup Script
# 智慧工厂 DevOps - Windows Runner 部署脚本
# 
# 使用方法: .\setup_windows_runner.ps1 -DroneServer "192.168.3.75:3001" -Secret "your-secret"

param(
    [Parameter(Mandatory=$false)]
    [string]$DroneServer = "192.168.3.75:3001",
    
    [Parameter(Mandatory=$false)]
    [string]$Secret = "devops-shared-secret",
    
    [Parameter(Mandatory=$false)]
    [string]$RunnerName = "windows-runner-codeforge",
    
    [Parameter(Mandatory=$false)]
    [int]$Capacity = 2,
    
    [Parameter(Mandatory=$false)]
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "智慧工厂 - Windows Runner 部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Runner {
    Write-Host "[1/4] 检查 Docker..." -ForegroundColor Yellow
    
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        Write-Host "错误: Docker 未安装" -ForegroundColor Red
        Write-Host "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host "  Docker 已安装: $(docker.Source)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[2/4] 检查 Docker 服务..." -ForegroundColor Yellow
    
    $dockerService = Get-Service -Name Docker -ErrorAction SilentlyContinue
    if ($dockerService.Status -ne "Running") {
        Write-Host "  启动 Docker 服务..." -ForegroundColor Yellow
        Start-Service Docker
        Start-Sleep -Seconds 5
    }
    Write-Host "  Docker 状态: $($dockerService.Status)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[3/4] 拉取 Drone Runner 镜像..." -ForegroundColor Yellow
    
    docker pull drone/drone-runner-docker
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  拉取镜像失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "  镜像拉取完成" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[4/4] 配置并启动 Runner..." -ForegroundColor Yellow
    
    # 检查是否已存在
    $existing = docker ps -a --filter "name=drone-runner-windows" --format "{{.Names}}"
    if ($existing) {
        Write-Host "  移除旧的 Runner 容器..." -ForegroundColor Yellow
        docker stop drone-runner-windows 2>$null
        docker rm drone-runner-windows 2>$null
    }
    
    # 启动新的 Runner
    $env:DRONE_RPC_PROTO = "http"
    $env:DRONE_RPC_HOST = $DroneServer
    $env:DRONE_RPC_SECRET = $Secret
    $env:DRONE_RUNNER_CAPACITY = $Capacity
    $env:DRONE_RUNNER_NAME = $RunnerName
    $env:DRONE_DEBUG = "true"
    
    docker run --detach `
        --volume //./pipe/docker_engine://./pipe/docker_engine `
        --env DRONE_RPC_PROTO=http `
        --env DRONE_RPC_HOST=$DroneServer `
        --env DRONE_RPC_SECRET=$Secret `
        --env DRONE_RUNNER_CAPACITY=$Capacity `
        --env DRONE_RUNNER_NAME=$RunnerName `
        --env DRONE_DEBUG=true `
        --publish 3002:3000 `
        --restart=always `
        --name=drone-runner-windows `
        drone/drone-runner-docker
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Runner 启动成功!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "部署完成!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Runner 名称: $RunnerName" -ForegroundColor White
        Write-Host "Drone Server: $DroneServer" -ForegroundColor White
        Write-Host "并行任务数: $Capacity" -ForegroundColor White
        Write-Host ""
        Write-Host "查看日志: docker logs drone-runner-windows" -ForegroundColor Cyan
        Write-Host "查看状态: docker ps | grep drone-runner" -ForegroundColor Cyan
    } else {
        Write-Host "  Runner 启动失败" -ForegroundColor Red
        exit 1
    }
}

function Uninstall-Runner {
    Write-Host "卸载 Windows Runner..." -ForegroundColor Yellow
    
    docker stop drone-runner-windows 2>$null
    docker rm drone-runner-windows 2>$null
    
    Write-Host "卸载完成" -ForegroundColor Green
}

# 主程序
if (-not (Test-Admin)) {
    Write-Host "错误: 请以管理员身份运行此脚本" -ForegroundColor Red
    Write-Host "右键点击 PowerShell -> 以管理员身份运行" -ForegroundColor Yellow
    exit 1
}

if ($Uninstall) {
    Uninstall-Runner
} else {
    Install-Runner
}
