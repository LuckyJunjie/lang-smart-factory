# Smart Factory MCP servers (local + remote)
import sys
import importlib.util

# Dynamically load the system mcp
_system_mcp_path = '/home/pi/.local/lib/python3.13/site-packages/mcp'

# Load fastmcp module (it's a package)
_spec = importlib.util.spec_from_file_location("mcp_server_fastmcp", f"{_system_mcp_path}/server/fastmcp/__init__.py")
_fastmcp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fastmcp)
sys.modules['mcp.server.fastmcp'] = _fastmcp

# Also register mcp.server
_server_path = f"{_system_mcp_path}/server/__init__.py"
_spec = importlib.util.spec_from_file_location("mcp_server", _server_path)
_server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_server)
sys.modules['mcp.server'] = _server
