-- Migration: OpenClaw workflow (priority/depends_on, work log, team reports)
-- Supports OPENCLAW_COMMUNICATION_SYSTEM.md v1.4: assignment strategy, work logs, dev/test reports

-- Requirements: dependency list (JSON array of requirement IDs, e.g. "[1,2,3]")
-- Run only if column missing (safe re-run)
ALTER TABLE requirements ADD COLUMN depends_on TEXT;

-- Work log: 时间、任务名称、任务输出、任务下一步 (all roles: Vanguard, Hera, teams)
CREATE TABLE IF NOT EXISTS work_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_or_team TEXT NOT NULL,
    task_name TEXT NOT NULL,
    task_output TEXT,
    next_step TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_work_log_role_team ON work_log(role_or_team);
CREATE INDEX IF NOT EXISTS idx_work_log_created ON work_log(created_at);

-- Team reports: full development task report or test task report (structured JSON)
CREATE TABLE IF NOT EXISTS team_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    requirement_id INTEGER NOT NULL,
    report_type TEXT NOT NULL CHECK(report_type IN ('development', 'test')),
    content TEXT NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(requirement_id) REFERENCES requirements(id)
);
CREATE INDEX IF NOT EXISTS idx_team_report_team ON team_report(team);
CREATE INDEX IF NOT EXISTS idx_team_report_requirement ON team_report(requirement_id);
CREATE INDEX IF NOT EXISTS idx_team_report_reported ON team_report(reported_at);
