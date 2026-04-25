-- Migration: Team task development details (for final report: analysis, assignment, development)
-- Teams report per-task details to Hera; Vanguard includes in Feishu summary

CREATE TABLE IF NOT EXISTS team_task_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    requirement_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    detail_type TEXT NOT NULL CHECK(detail_type IN ('analysis', 'assignment', 'development')),
    content TEXT NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_team_task_detail_team ON team_task_detail(team);
CREATE INDEX IF NOT EXISTS idx_team_task_detail_req_task ON team_task_detail(requirement_id, task_id);
CREATE INDEX IF NOT EXISTS idx_team_task_detail_reported ON team_task_detail(reported_at);
