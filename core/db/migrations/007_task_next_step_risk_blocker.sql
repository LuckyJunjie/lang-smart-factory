-- Migration: Task next-step, risk, blocker (sub-team report & server reassignment)
-- Supports: blocked task → do next_step_task (e.g. bug fix) first → then resume.
-- Sub-teams report requirement analysis/breakdown (task-detail), task status, risk/blocker;
-- server can update/reassign tasks and set next_step_task_id.

-- Optional next-step task: do this task before resuming current task (e.g. fix bug first)
ALTER TABLE tasks ADD COLUMN next_step_task_id INTEGER;

-- Risk and blocker text (reported by sub-team; server/Hera can reassign)
ALTER TABLE tasks ADD COLUMN risk TEXT;
ALTER TABLE tasks ADD COLUMN blocker TEXT;

CREATE INDEX IF NOT EXISTS idx_tasks_next_step ON tasks(next_step_task_id);
