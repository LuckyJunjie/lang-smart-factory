-- Migration: Pipelines and CI/CD tables
-- Required by API: /api/pipelines, /api/cicd/builds, etc.

CREATE TABLE IF NOT EXISTS pipelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    project_id INTEGER,
    trigger_type TEXT DEFAULT 'manual',
    stages TEXT,
    status TEXT DEFAULT 'inactive',
    last_run_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER NOT NULL,
    run_number INTEGER NOT NULL,
    status TEXT DEFAULT 'running',
    trigger_reason TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

CREATE TABLE IF NOT EXISTS cicd_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER NOT NULL,
    trigger_type TEXT DEFAULT 'commit',
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    webhook_secret TEXT,
    schedule_cron TEXT,
    enabled INTEGER DEFAULT 1,
    last_triggered_at DATETIME,
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

CREATE TABLE IF NOT EXISTS cicd_builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER,
    pipeline_id INTEGER NOT NULL,
    commit_sha TEXT,
    commit_message TEXT,
    branch TEXT,
    status TEXT DEFAULT 'running',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    build_log TEXT,
    artifacts TEXT,
    FOREIGN KEY(trigger_id) REFERENCES cicd_triggers(id),
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_pipeline ON pipeline_runs(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_cicd_triggers_pipeline ON cicd_triggers(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_cicd_builds_pipeline ON cicd_builds(pipeline_id);
