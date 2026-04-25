#!/usr/bin/env python3
"""
Godot MCP Persistent Daemon
Keeps MCP subprocess alive, communicates via stdin/stdout.
"""
import subprocess
import json
import threading
import time
import sys
import os
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

GODOT_MCP = "/home/pi/.openclaw/workspace/smart-factory/tools/godot-mcp-149/build/index.js"
GODOT_BIN = "/home/pi/.local/bin/godot"
PROJECT = "/home/pi/.openclaw/workspace/pinball-experience"
PORT = 9876

class PersistentMCP:
    def __init__(self):
        self.proc = None
        self.reader_thread = None
        self.responses = {}
        self.counter = 0
        self.lock = threading.Lock()
        self.running = False
        
    def start(self):
        """Start the MCP subprocess and keep it alive"""
        env = os.environ.copy()
        env["GODOT_PATH"] = GODOT_BIN
        
        self.proc = subprocess.Popen(
            [sys.executable, "-c", f"""
import subprocess, sys, os
env = os.environ.copy()
env['GODOT_PATH'] = '{GODOT_BIN}'
proc = subprocess.Popen(
    ['node', '{GODOT_MCP}'],
    env=env,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)
while True:
    line = sys.stdin.readline()
    if not line:
        break
    proc.stdin.write(line)
    proc.stdin.flush()
    # Read until we get a response
    import select
    if select.select([proc.stdout], [], [], 10)[0]:
        resp = proc.stdout.readline()
        sys.stdout.write(resp + '\\n')
        sys.stdout.flush()
"""],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Start reader thread
        self.running = True
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()
        
        print("MCP subprocess started", flush=True)
        
    def _reader(self):
        """Read responses from MCP subprocess"""
        while self.running and self.proc and self.proc.poll() is None:
            try:
                import select
                if select.select([self.proc.stdout], [], [], 1)[0]:
                    line = self.proc.stdout.readline()
                    if line:
                        print(f"MCP: {line[:100]}", flush=True)
            except Exception as e:
                print(f"Reader error: {e}", flush=True)
                
    def call(self, tool_name, arguments=None):
        """Send a tool call to MCP subprocess"""
        if not self.proc or self.proc.poll() is not None:
            return {"error": "MCP process not running"}
        
        with self.lock:
            self.counter += 1
            req_id = self.counter
            
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": req_id
        }
        
        try:
            self.proc.stdin.write(json.dumps(req) + "\n")
            self.proc.stdin.flush()
            # Wait for response
            time.sleep(2)
            return {"status": "ok", "tool": tool_name}
        except Exception as e:
            return {"error": str(e)}
    
    def stop(self):
        self.running = False
        if self.proc:
            self.proc.terminate()

daemon = PersistentMCP()
daemon.start()

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
            daemon.send_json({"status": "ok"})
        elif self.path == "/start":
            result = daemon.call("run_project", {"projectPath": PROJECT})
            daemon.send_json(result)
        elif self.path == "/screenshot":
            result = daemon.call("game_screenshot", {})
            daemon.send_json(result)
        elif self.path == "/version":
            result = daemon.call("get_godot_version", {})
            daemon.send_json(result)
        else:
            daemon.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == "/call":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            tool = data.get("tool")
            args = data.get("arguments", {})
            result = daemon.call(tool, args)
            daemon.send_json(result)
        else:
            daemon.send_json({"error": "Not found"}, 404)

if __name__ == "__main__":
    try:
        server = HTTPServer(("0.0.0.0", PORT), Handler)
        print(f"Godot MCP Persistent Daemon running on http://0.0.0.0:{PORT}", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        daemon.stop()
        server.shutdown()
