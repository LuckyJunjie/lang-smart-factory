#!/usr/bin/env python3
"""
Vanguard001 Coordinator - Run hourly via cron.
Preferred: python -m skills.assign_tasks_to_teams (from smart-factory root).
This script invokes the skill for backward compatibility.
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SMART_FACTORY_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SMART_FACTORY_ROOT not in sys.path:
    sys.path.insert(0, _SMART_FACTORY_ROOT)

if __name__ == "__main__":
    from skills.assign_tasks_to_teams import main
    sys.exit(main())
