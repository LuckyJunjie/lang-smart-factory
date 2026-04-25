-- Migration: OpenClaw Communication System
-- team_machine_status for team status reports, machines.team for team mapping

-- Add team to machines (vanguard001, jarvis, codeforge, newton, tesla)
ALTER TABLE machines ADD COLUMN team TEXT;

-- Team machine status reports (custom format per team)
CREATE TABLE IF NOT EXISTS team_machine_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    payload TEXT,
    reporter_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_team_machine_status_team ON team_machine_status(team);
CREATE INDEX IF NOT EXISTS idx_team_machine_status_reported ON team_machine_status(reported_at);
