"""
Smart Factory MCP Server Module
Model Context Protocol server for external agents
"""

from .server import SmartFactoryMCPServer, create_mcp_routes

__all__ = ['SmartFactoryMCPServer', 'create_mcp_routes']