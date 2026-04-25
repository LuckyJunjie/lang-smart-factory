-- Migration: Team status report (for Team -> Hera -> Vanguard channel)
-- Teams report status + task details to Hera; Vanguard posts to Feishu

CREATE TABLE IF NOT EXISTS team_status_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reporter_agent TEXT,
    payload TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_team_status_report_team ON team_status_report(team);
CREATE INDEX IF NOT EXISTS idx_team_status_report_reported ON team_status_report(reported_at);
