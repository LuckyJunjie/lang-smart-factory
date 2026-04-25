#!/usr/bin/env python3
"""Godot MCP Persistent Server - keeps subprocess alive, HTTP API for tools"""
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

class GodotMCPServer:
    def __init__(self):
        self.proc = None
        self.running = False
        self.lock = threading.Lock()
        self.reader_thread = None
        self.output_buffer = []
        
    def _reader(self):
        """Read stdout lines into buffer"""
        while self.running:
            try:
                line = self.proc.stdout.readline()
                if line:
                    self.output_buffer.append(line.strip())
                    if len(self.output_buffer) > 50:
                        self.output_buffer.pop(0)
            except:
                break
    
    def start(self):
        """Start MCP subprocess"""
        env = os.environ.copy()
        env["GODOT_PATH"] = GODOT_BIN
        
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
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()
        
        # Send initialize
        init = {"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"godot-mcp-daemon","version":"1.0"}},"id":0}
        self._send(init)
        time.sleep(0.5)
        
        # Send initialized notification
        notif = {"jsonrpc":"2.0","method":"initialized","params":{}}
        self._send(notif)
        time.sleep(0.5)
        
        print("MCP server initialized", flush=True)
        
    def _send(self, msg):
        with self.lock:
            line = json.dumps(msg)
            self.proc.stdin.write(line + "\n")
            self.proc.stdin.flush()
    
    def call_tool(self, tool_name, arguments=None):
        """Call a tool, returns response text"""
        if not self.proc or self.proc.poll() is not None:
            return "ERROR: Process not running"
        
        req_id = int(time.time() * 1000) % 100000
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": req_id
        }
        
        with self.lock:
            before = len(self.output_buffer)
        
        self._send(req)
        
        # Wait for response
        time.sleep(3)
        
        with self.lock:
            if len(self.output_buffer) > before:
                return " | ".join(self.output_buffer[before:])
            return "No response"
    
    def stop(self):
        self.running = False
        if self.proc:
            self.proc.terminate()
            self.proc.wait()

# Global server instance
server = GodotMCPServer()

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
            self.send_json({"status": "ok", "running": server.running})
        elif path == "/start":
            result = server.call_tool("run_project", {"projectPath": PROJECT})
            self.send_json({"result": result})
        elif path == "/screenshot":
            result = server.call_tool("game_screenshot", {})
            self.send_json({"result": result})
        elif path == "/version":
            result = server.call_tool("get_godot_version", {})
            self.send_json({"result": result})
        elif path == "/key":
            result = server.call_tool("game_key_press", {"keyName": "space"})
            self.send_json({"result": result})
        elif path == "/click":
            result = server.call_tool("game_click", {"x": 640, "y": 360})
            self.send_json({"result": result})
        elif path == "/gamestate":
            result = server.call_tool("get_scene_tree", {})
            self.send_json({"result": result})
        elif path == "/eval":
            result = server.call_tool("game_eval", {"code": "print('hello from daemon')"})
            self.send_json({"result": result})
        else:
            self.send_json({"error": "Unknown endpoint. Try /health, /start, /screenshot, /version, /key, /click, /gamestate, /eval"}, 404)
    
    def do_POST(self):
        if self.path == "/call":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            tool = data.get("tool", "")
            args = data.get("arguments", {})
            result = server.call_tool(tool, args)
            self.send_json({"result": result})
        else:
            self.send_json({"error": "Unknown endpoint"}, 404)

def signal_handler(sig, frame):
    print("Shutting down...", flush=True)
    server.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"Starting Godot MCP Persistent Server...", flush=True)
    server.start()
    
    httpd = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"HTTP API running on http://0.0.0.0:{PORT}", flush=True)
    print(f"Endpoints:", flush=True)
    print(f"  GET /health      - Health check", flush=True)
    print(f"  GET /start       - Start Godot project", flush=True)
    print(f"  GET /screenshot  - Take screenshot", flush=True)
    print(f"  GET /version     - Get Godot version", flush=True)
    print(f"  GET /key         - Press space key", flush=True)
    print(f"  GET /click       - Click center screen", flush=True)
    print(f"  GET /gamestate   - Get scene tree", flush=True)
    print(f"  GET /eval        - Eval GDScript", flush=True)
    print(f"  POST /call        - Call any tool {json.dumps({'tool': 'name', 'arguments': {}})}", flush=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        httpd.shutdown()
