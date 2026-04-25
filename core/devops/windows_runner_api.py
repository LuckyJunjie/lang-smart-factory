# Windows Runner API
# 智慧工厂 DevOps 子系统 - Windows Runner 管理

from flask import Flask, request, jsonify
import subprocess
import platform
import os

app = Flask(__name__)

# Windows Runner 配置
RUNNER_CONTAINER = "drone-runner-windows"
RUNNER_PORT = 3002

def run_docker_command(args):
    """执行 docker 命令"""
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/api/devops/runners', methods=['GET'])
def list_runners():
    """列出所有 Runner"""
    if platform.system() != "Windows":
        return jsonify({"error": "Windows Runner only available on Windows"}), 400
    
    result = run_docker_command(["ps", "-a", "--filter", "name=drone-runner", "--format", "{{.Names}}"])
    
    runners = []
    if result["success"]:
        for name in result["output"].strip().split("\n"):
            if name:
                status = run_docker_command(["ps", "--filter", f"name={name}", "--format", "{{.Status}}"])
                runners.append({
                    "name": name,
                    "status": status["output"].strip() if status["success"] else "unknown",
                    "platform": "windows" if "windows" in name.lower() else "unknown"
                })
    
    return jsonify({
        "runners": runners,
        "platform": platform.system()
    })

@app.route('/api/devops/runners/windows/status', methods=['GET'])
def windows_runner_status():
    """获取 Windows Runner 状态"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    # 检查容器状态
    result = run_docker_command(["ps", "--filter", f"name={RUNNER_CONTAINER}", "--format", "{{.Status}}"])
    status = result["output"].strip() if result["success"] else "not found"
    
    # 获取容器详情
    inspect = run_docker_command(["inspect", RUNNER_CONTAINER])
    details = {}
    if inspect["success"]:
        import json
        try:
            data = json.loads(inspect["output"])
            if data:
                d = data[0]
                details = {
                    "created": d.get("Created", ""),
                    "state": d.get("State", {}).get("Status", ""),
                    "ports": d.get("NetworkSettings", {}).get("Ports", {}),
                    "image": d.get("Config", {}).get("Image", "")
                }
        except:
            pass
    
    return jsonify({
        "name": RUNNER_CONTAINER,
        "status": status,
        "details": details,
        "platform": "windows"
    })

@app.route('/api/devops/runners/windows/start', methods=['POST'])
def windows_runner_start():
    """启动 Windows Runner"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    result = run_docker_command(["start", RUNNER_CONTAINER])
    return jsonify(result)

@app.route('/api/devops/runners/windows/stop', methods=['POST'])
def windows_runner_stop():
    """停止 Windows Runner"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    result = run_docker_command(["stop", RUNNER_CONTAINER])
    return jsonify(result)

@app.route('/api/devops/runners/windows/restart', methods=['POST'])
def windows_runner_restart():
    """重启 Windows Runner"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    stop_result = run_docker_command(["stop", RUNNER_CONTAINER])
    if stop_result["success"]:
        start_result = run_docker_command(["start", RUNNER_CONTAINER])
        return jsonify(start_result)
    return jsonify(stop_result)

@app.route('/api/devops/runners/windows/logs', methods=['GET'])
def windows_runner_logs():
    """获取 Windows Runner 日志"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    lines = request.args.get('lines', 100)
    result = run_docker_command(["logs", "--tail", str(lines), RUNNER_CONTAINER])
    return jsonify({
        "logs": result["output"] if result["success"] else result["error"],
        "success": result["success"]
    })

@app.route('/api/devops/runners/windows/setup', methods=['POST'])
def windows_runner_setup():
    """部署 Windows Runner"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    data = request.json or {}
    drone_server = data.get('drone_server', '192.168.3.75:3001')
    secret = data.get('secret', 'devops-shared-secret')
    runner_name = data.get('runner_name', 'windows-runner-codeforge')
    capacity = data.get('capacity', 2)
    
    # 先停止旧容器
    run_docker_command(["stop", RUNNER_CONTAINER])
    run_docker_command(["rm", RUNNER_CONTAINER])
    
    # 启动新容器
    result = run_docker_command([
        "run", "--detach",
        "--volume", "//./pipe/docker_engine://./pipe/docker_engine",
        "--env", f"DRONE_RPC_PROTO=http",
        "--env", f"DRONE_RPC_HOST={drone_server}",
        "--env", f"DRONE_RPC_SECRET={secret}",
        "--env", f"DRONE_RUNNER_CAPACITY={capacity}",
        "--env", f"DRONE_RUNNER_NAME={runner_name}",
        "--env", f"DRONE_DEBUG=true",
        "--publish", f"{RUNNER_PORT}:3000",
        "--restart=always",
        "--name", RUNNER_CONTAINER,
        "drone/drone-runner-docker"
    ])
    
    return jsonify({
        "success": result["success"],
        "message": f"Windows Runner '{runner_name}' deployed" if result["success"] else result["error"],
        "config": {
            "drone_server": drone_server,
            "runner_name": runner_name,
            "capacity": capacity
        }
    })

@app.route('/api/devops/runners/stats', methods=['GET'])
def runner_stats():
    """获取 Runner 统计信息"""
    if platform.system() != "Windows":
        return jsonify({"error": "Only available on Windows"}), 400
    
    # Docker 统计
    result = run_docker_command(["stats", "--no-stream", "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"])
    
    stats = []
    if result["success"]:
        for line in result["output"].strip().split("\n"):
            if line and "drone-runner" in line:
                parts = line.split("\t")
                if len(parts) >= 3:
                    stats.append({
                        "name": parts[0],
                        "cpu": parts[1],
                        "memory": parts[2]
                    })
    
    return jsonify({
        "platform": platform.system(),
        "runner_stats": stats
    })
