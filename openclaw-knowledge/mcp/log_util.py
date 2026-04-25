#!/usr/bin/env python3
"""
Shared logging for MCP servers. Writes logs to disk for troubleshooting.
Set MCP_LOG_DIR to override log directory (default: repo logs/mcp or ~/.cursor/mcp-logs).
"""

import os
import logging
import functools
from pathlib import Path
from typing import Any, Callable, Optional

# Default: MCP_LOG_DIR, or cwd/logs/mcp when mcp/ exists, else ~/.cursor/mcp-logs
def _log_dir() -> Path:
    if os.environ.get("MCP_LOG_DIR"):
        p = Path(os.environ["MCP_LOG_DIR"]).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    cwd = Path.cwd()
    if (cwd / "mcp").is_dir() or (cwd / "src" / "mcp").is_dir():
        logs = cwd / "logs" / "mcp"
    else:
        logs = Path(os.path.expanduser("~/.cursor/mcp-logs"))
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def get_logger(server_name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger that writes to a file under MCP_LOG_DIR (or default)."""
    log_dir = _log_dir()
    # Sanitize server name for filename (e.g. "dev-mcp" -> dev-mcp.log)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in server_name)
    log_file = log_dir / f"{safe_name}.log"
    logger = logging.getLogger(f"mcp.{server_name}")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.info("log_file=%s", str(log_file))
    return logger


def log_tool_call(logger: logging.Logger) -> Callable:
    """Decorator to log tool invocations and results (for troubleshooting)."""

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Short args summary (avoid huge content in logs)
            args_repr = repr((args, kwargs))
            if len(args_repr) > 300:
                args_repr = args_repr[:300] + "..."
            logger.info("tool_call %s %s", f.__name__, args_repr)
            try:
                out = f(*args, **kwargs)
                success = True
                if isinstance(out, dict):
                    success = out.get("success", True)
                elif isinstance(out, (list, str)):
                    success = True
                logger.info("tool_done %s success=%s", f.__name__, success)
                return out
            except Exception as e:
                logger.exception("tool_error %s: %s", f.__name__, e)
                raise

        return wrapper

    return decorator
