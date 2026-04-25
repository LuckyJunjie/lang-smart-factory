#!/usr/bin/env python3
"""
Shared logging for Smart Factory skills. Writes logs to disk for troubleshooting.
Log directory: SMART_FACTORY_LOGS or <repo>/logs/skills. One file per skill: <skill_name>.log
"""

import logging
import os
from pathlib import Path

# Default: logs/skills (repo = parent of skills package)
_skills_dir = Path(__file__).resolve().parent
_repo_dir = _skills_dir.parent
_DEFAULT_LOG_DIR = _repo_dir / "logs" / "skills"
LOG_DIR = Path(os.environ.get("SMART_FACTORY_LOGS", str(_DEFAULT_LOG_DIR)))
_LOG_DIR_ENSURE = False


def _ensure_log_dir():
    global _LOG_DIR_ENSURE
    if _LOG_DIR_ENSURE:
        return
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _LOG_DIR_ENSURE = True
    except OSError:
        pass


def get_logger(skill_name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger for the given skill. Logs to LOG_DIR/<skill_name>.log."""
    _ensure_log_dir()
    name = f"skills.{skill_name}"
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    logger.propagate = False
    log_file = LOG_DIR / f"{skill_name}.log"
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8")
    except OSError:
        # fallback: no file, only memory (e.g. permission denied)
        return logger
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(fh)
    return logger
