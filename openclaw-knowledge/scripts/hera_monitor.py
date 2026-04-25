#!/usr/bin/env python3
"""
Hera Monitor - Run every 15–30 min via cron.
Preferred: python -m skills.hera_monitor (from smart-factory root).
For resolution use: python -m skills.handle_blockage
This script invokes the skill for backward compatibility.
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SMART_FACTORY_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SMART_FACTORY_ROOT not in sys.path:
    sys.path.insert(0, _SMART_FACTORY_ROOT)

if __name__ == "__main__":
    from skills.hera_monitor import main
    sys.exit(main())
