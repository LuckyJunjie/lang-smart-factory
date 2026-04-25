-- Smart Factory Database Schema
-- 智慧工厂需求与项目管理数据库

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT CHECK(type IN ('game', 'app', 'finance', 'tool', 'research')) DEFAULT 'game',
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gdd_path TEXT,
    repo_url TEXT,
    repo_default_branch TEXT,
    repo_last_sync_at TEXT,
    repo_head_commit TEXT,
    repo_remote_notes TEXT,
    category TEXT,
    purpose TEXT,
    benefits TEXT,
    outcome TEXT,
    priority TEXT CHECK(priority IN ('P0', 'P1', 'P2', 'P3')) DEFAULT 'P2'
);

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT CHECK(priority IN ('P0', 'P1', 'P2', 'P3')) DEFAULT 'P2',
    status TEXT DEFAULT 'new' CHECK(status IN ('new', 'in_progress', 'need_input', 'done', 'blocked', 'closed')),
    type TEXT CHECK(type IN ('feature', 'bug', 'enhancement', 'asset', 'research')) DEFAULT 'feature',
    assigned_to TEXT,
    assigned_team TEXT,           -- e.g. jarvis, codeforge (team that took the requirement)
    assigned_agent TEXT,           -- e.g. athena, cerberus (team member who took it)
    taken_at DATETIME,             -- when requirement was taken
    plan_step_id TEXT,             -- e.g. "0.6", "2.1" links to plan
    plan_phase TEXT,               -- "baseline" | "feature"
    step TEXT DEFAULT 'not start' CHECK(step IN ('not start', 'analyse', 'implement', 'test', 'verify', 'done')),
    progress_percent INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    design_doc_path TEXT,
    acceptance_criteria TEXT,
    parent_requirement_id INTEGER REFERENCES requirements(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'need_input', 'review', 'done', 'blocked')),
    step TEXT DEFAULT 'not start' CHECK(step IN ('not start', 'analyse', 'implement', 'test', 'verify', 'done')),
    note TEXT,
    executor TEXT,
    output_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    est_tokens_total INTEGER DEFAULT 0,
    prompt_rounds INTEGER DEFAULT 0,
    FOREIGN KEY(req_id) REFERENCES requirements(id)
);

-- 机器资源表
CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    port INTEGER DEFAULT 18789,
    role TEXT,
    status TEXT DEFAULT 'offline',
    last_seen DATETIME,
    capabilities TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 工具链表 (MCP, Skills, Extensions)
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('mcp', 'skill', 'extension', 'script')) NOT NULL,
    source TEXT,
    path TEXT,
    status TEXT DEFAULT 'active',
    config TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 吞吐量记录
CREATE TABLE IF NOT EXISTS throughput (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hour TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    req_created INTEGER DEFAULT 0,
    req_completed INTEGER DEFAULT 0,
    tasks_created INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_req_project ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_req_status ON requirements(status);
CREATE INDEX IF NOT EXISTS idx_tasks_req ON tasks(req_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_requirements_parent ON requirements(parent_requirement_id);

-- V-model / test plan cases (per HIGH_REQUIREMENTS §3.3)
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
