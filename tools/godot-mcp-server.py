#!/usr/bin/env python3
"""
Godot MCP Persistent Server v2
- Starts Godot via MCP tools/call in a persistent Node.js subprocess
- Node subprocess stays alive between requests
- HTTP API for tools
"""
import subprocess
import json
import time
import threading
import os
import sys
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler

GODOT_MCP = "/home/pi/.openclaw/workspace/smart-factory/tools/godot-mcp-149/build/index.js"
GODOT_BIN = "/home/pi/.local/bin/godot"
PROJECT = "/home/pi/.openclaw/workspace/pinball-experience"
PORT = 9876

class PersistentMCPServer:
    def __init__(self):
        self.proc = None
        self.running = False
        self.lock = threading.Lock()
        self.buffer = []
        self.thread = None
        
    def start(self):
        """Start MCP subprocess, keep it alive"""
        env = os.environ.copy()
        env["GODOT_PATH"] = GODOT_BIN
        
        # Use node directly to run the MCP server
        self.proc = subprocess.Popen(
            ["node", GODOT_MCP],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        self.running = True
        
        # Reader thread
        def reader():
            while self.running and self.proc and self.proc.poll() is None:
                try:
                    import select
                    if select.select([self.proc.stdout], [], [], 0.5)[0]:
                        line = self.proc.stdout.readline()
                        if line:
                            self.buffer.append(line.strip())
                            # Keep buffer limited
                            if len(self.buffer) > 100:
                                self.buffer.pop(0)
                except:
                    break
        
        self.thread = threading.Thread(target=reader, daemon=True)
        self.thread.start()
        
        # Initialize
        init_req = {"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":0}
        self._send(init_req)
        time.sleep(0.3)
        
        # Send initialized notification
        self._send({"jsonrpc":"2.0","method":"initialized","params":{}})
        time.sleep(0.3)
        
        # Drain initial output
        self.buffer.clear()
        
        print("MCP subprocess running, PID:", self.proc.pid, flush=True)
    
    def _send(self, msg):
        """Send JSON-RPC message"""
        with self.lock:
            line = json.dumps(msg)
            self.proc.stdin.write(line + "\n")
            self.proc.stdin.flush()
    
    def call(self, tool_name, arguments=None):
        """Call tool, return response"""
        if not self.proc or self.proc.poll() is not None:
            return {"error": "MCP not running"}
        
        req_id = int(time.time() * 1000)
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": req_id
        }
        
        before = len(self.buffer)
        self._send(req)
        
        # Wait for response
        for _ in range(30):  # 3 seconds max
            time.sleep(0.1)
            with self.lock:
                if len(self.buffer) > before:
                    resp = self.buffer[-1]
                    try:
                        return json.loads(resp)
                    except:
                        return {"raw": resp}
        return {"error": "timeout"}
    
    def stop(self):
        self.running = False
        if self.proc:
            self.proc.terminate()
            self.proc.wait()

server = PersistentMCPServer()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        path = self.path
        
        if path == "/health":
            running = server.proc and server.proc.poll() is None
            self.send_json({"status": "ok", "mcp_running": running})
        elif path == "/start":
            result = server.call("run_project", {"projectPath": PROJECT})
            self.send_json({"result": result})
        elif path == "/screenshot":
            result = server.call("game_screenshot", {})
            self.send_json({"result": result})
        elif path == "/version":
            result = server.call("get_godot_version", {})
            self.send_json({"result": result})
        elif path == "/key":
            result = server.call("game_key_press", {"keyName": "space"})
            self.send_json({"result": result})
        elif path == "/click":
            result = server.call("game_click", {"x": 640, "y": 360})
            self.send_json({"result": result})
        elif path == "/eval":
            result = server.call("game_eval", {"code": "print('hello')"})
            self.send_json({"result": result})
        elif path == "/scene":
            result = server.call("get_scene_tree", {})
            self.send_json({"result": result})
        elif path == "/stop":
            result = server.call("stop_project", {})
            self.send_json({"result": result})
        elif path == "/restart":
            server.stop()
            time.sleep(1)
            server.start()
            self.send_json({"status": "restarted"})
        else:
            self.send_json({"error": "Try /health, /start, /screenshot, /version, /key, /click, /eval, /scene, /stop, /restart"}, 404)
    
    def do_POST(self):
        if self.path == "/call":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            result = server.call(data.get("tool", ""), data.get("arguments", {}))
            self.send_json({"result": result})
        else:
            self.send_json({"error": "Unknown endpoint"}, 404)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s,f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s,f: sys.exit(0))
    
    print("Starting Godot MCP Persistent Server v2...", flush=True)
    server.start()
    
    httpd = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"HTTP API: http://0.0.0.0:{PORT}", flush=True)
    print(f"Endpoints: /health, /start, /screenshot, /version, /key, /click, /eval, /scene, /stop, /restart", flush=True)
    httpd.serve_forever()
