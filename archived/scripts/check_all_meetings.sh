#!/bin/bash
# Meeting check cron wrapper - checks all agents
# Runs every 15 minutes

cd /home/pi/.openclaw/workspace/implementation/smart-factory

# Source virtualenv
source .venv/bin/activate

# List of agents to check
AGENTS="hera vanguard001 einstein curie galileo hawking darwin newton model_s model_3 model_x model_y cybertruck"

# Only submit for agents that need to submit (dry-run first)
for agent in $AGENTS; do
    python check_meeting.py --agent $agent 2>&1 | head -20
done

echo "--- Meeting check completed at $(date) ---"
