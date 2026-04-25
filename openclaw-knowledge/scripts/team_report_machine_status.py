#!/usr/bin/env python3
"""
Team Machine Status Reporter - Run every 30 min via cron.
Preferred: python -m skills.report_machine_status --team <team> (from smart-factory root).
This script invokes the skill for backward compatibility.
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SMART_FACTORY_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SMART_FACTORY_ROOT not in sys.path:
    sys.path.insert(0, _SMART_FACTORY_ROOT)

if __name__ == "__main__":
    from skills.report_machine_status import main
    sys.exit(main())
