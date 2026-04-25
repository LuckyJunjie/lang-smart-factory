#!/usr/bin/env python3
"""Godot MCP Daemon - Persistent wrapper for godot-mcp stdio server"""
import subprocess
import json
import sys
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

GODOT_MCP = "/home/pi/.openclaw/workspace/smart-factory/tools/godot-mcp-149/build/index.js"
GODOT_BIN = "/home/pi/.local/bin/godot"
PROJECT = "/home/pi/.openclaw/workspace/pinball-experience"
PORT = 9876

class MCPSession:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()
        self.running = False
        
    def send_jsonrpc(self, method, params=None, id=1):
        """Send JSON-RPC request and get response"""
        with self.lock:
            env = os.environ.copy()
            env["GODOT_PATH"] = GODOT_BIN
            
            req = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": id}
            
            # Use node directly
            script = f"""
const {{ spawn }} = require('child_process');
const env = Object.assign({{}}, process.env, {{ 'GODOT_PATH': '{GODOT_BIN}' }});
const child = spawn('node', ['{GODOT_MCP}'], {{ env, stdio: ['pipe', 'pipe', 'pipe'] }});

child.stdin.write(JSON.stringify({json.dumps(req)}) + '\\n');
child.stdin.end();

let output = '';
child.stdout.on('data', (data) => {{ output += data.toString(); }});
child.stderr.on('data', (data) => {{ console.error(data.toString()); }});

setTimeout(() => {{
    child.kill();
    console.log(output);
}}, 8000);
"""
            result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=10, env=env)
            return result.stdout

    def start_godot(self):
        """Start Godot via MCP"""
        return self.send_jsonrpc("tools/call", {"name": "run_project", "arguments": {"projectPath": PROJECT}})
    
    def screenshot(self):
        """Take screenshot"""
        return self.send_jsonrpc("tools/call", {"name": "game_screenshot", "arguments": {}})
    
    def get_version(self):
        return self.send_jsonrpc("tools/call", {"name": "get_godot_version", "arguments": {}})

session = MCPSession()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok", "running": session.running})
        elif self.path == "/version":
            out = session.get_version()
            self.send_json({"result": out})
        elif self.path == "/start":
            out = session.start_godot()
            session.running = True
            self.send_json({"result": out})
        elif self.path == "/screenshot":
            out = session.screenshot()
            self.send_json({"result": out})
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == "/call":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            tool = data.get("tool")
            args = data.get("arguments", {})
            out = session.send_jsonrpc("tools/call", {"name": tool, "arguments": args})
            self.send_json({"result": out})
        else:
            self.send_json({"error": "Not found"}, 404)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Godot MCP Daemon running on http://0.0.0.0:{PORT}")
    sys.stdout.flush()
    server.serve_forever()
