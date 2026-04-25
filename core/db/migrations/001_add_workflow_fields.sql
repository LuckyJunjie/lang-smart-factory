-- Migration: Add team/agent assignment and plan linkage for requirement workflow
-- Run after schema.sql on existing databases. Safe to re-run (run_migrations.py skips duplicate column).

-- Requirements: team assignment and plan step linkage
ALTER TABLE requirements ADD COLUMN assigned_team TEXT;
ALTER TABLE requirements ADD COLUMN assigned_agent TEXT;
ALTER TABLE requirements ADD COLUMN taken_at DATETIME;
ALTER TABLE requirements ADD COLUMN plan_step_id TEXT;
ALTER TABLE requirements ADD COLUMN plan_phase TEXT;
ALTER TABLE requirements ADD COLUMN step TEXT DEFAULT 'not start';
ALTER TABLE requirements ADD COLUMN progress_percent INTEGER DEFAULT 0;

-- Tasks: step for workflow tracking
ALTER TABLE tasks ADD COLUMN step TEXT DEFAULT 'not start';
