-- HIGH_REQUIREMENTS: project metadata (category, purpose, benefits, outcome, priority)
-- Sub-requirements + V-model test case tracking for OpenClaw workflows

ALTER TABLE projects ADD COLUMN category TEXT;
ALTER TABLE projects ADD COLUMN purpose TEXT;
ALTER TABLE projects ADD COLUMN benefits TEXT;
ALTER TABLE projects ADD COLUMN outcome TEXT;
ALTER TABLE projects ADD COLUMN priority TEXT CHECK(priority IN ('P0', 'P1', 'P2', 'P3')) DEFAULT 'P2';

ALTER TABLE requirements ADD COLUMN parent_requirement_id INTEGER REFERENCES requirements(id);

CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    task_id INTEGER,
    layer TEXT CHECK(layer IN ('unit', 'component', 'integration', 'screenshot', 'console', 'system')) DEFAULT 'unit',
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('planned', 'skipped', 'passed', 'failed', 'blocked')) DEFAULT 'planned',
    result_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_test_cases_requirement ON test_cases(requirement_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_task ON test_cases(task_id);
CREATE INDEX IF NOT EXISTS idx_requirements_parent ON requirements(parent_requirement_id);
