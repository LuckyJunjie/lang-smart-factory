-- Smart Factory - Enhanced Project Tracking Database Schema

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    github_repo TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'in_progress', 'done', 'archived')),
    description TEXT,
    
    -- Progress Tracking
    progress_percent INTEGER DEFAULT 0,
    start_date DATE,
    estimated_end_date DATE,
    daily_progress_rate REAL DEFAULT 0,  -- % per day
    
    -- Issue Tracking
    main_issues TEXT,
    issue_status TEXT DEFAULT 'new' CHECK(issue_status IN ('new', 'in_progress', 'need_input', 'done', 'blocked')),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Requirements Table
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    
    -- Progress
    progress_percent INTEGER DEFAULT 0,
    start_date DATE,
    estimated_end_date DATE,
    daily_progress_rate REAL DEFAULT 0,
    
    -- Status
    maturity TEXT DEFAULT 'new' CHECK(maturity IN ('new', 'designed', 'in_progress', 'done', 'archived')),
    step TEXT DEFAULT 'not start' CHECK(step IN ('not start', 'analyse', 'implement', 'test', 'verify', 'done')),
    note TEXT,
    priority TEXT DEFAULT 'P2' CHECK(priority IN ('P0', 'P1', 'P2', 'P3')),
    status TEXT DEFAULT 'new' CHECK(status IN ('new', 'in_progress', 'need_input', 'done', 'blocked', 'closed')),
    
    type TEXT CHECK(type IN ('feature', 'bug', 'enhancement', 'asset', 'research')),
    assigned_to TEXT,
    
    -- Issues
    blockers TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

-- Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id INTEGER,
    title TEXT NOT NULL,
    step TEXT DEFAULT 'not start' CHECK(step IN ('not start', 'analyse', 'implement', 'test', 'verify', 'done')),
    note TEXT,
    status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'need_input', 'review', 'done', 'blocked')),
    executor TEXT,
    output_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(req_id) REFERENCES requirements(id)
);

-- Progress History (for tracking daily changes)
CREATE TABLE IF NOT EXISTS progress_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    req_id INTEGER,
    progress_percent INTEGER,
    notes TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(req_id) REFERENCES requirements(id)
);

-- Toolchain Management
CREATE TABLE IF NOT EXISTS toolchain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('mcp', 'skill', 'extension', 'custom')),
    description TEXT,
    location TEXT,  -- URL, file path, or config
    config TEXT,    -- JSON config
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'error')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pipeline Workflows
CREATE TABLE IF NOT EXISTS pipelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    project_id INTEGER,
    trigger_type TEXT DEFAULT 'manual' CHECK(trigger_type IN ('manual', 'commit', 'schedule', 'webhook')),
    stages TEXT,  -- JSON array of stage names
    status TEXT DEFAULT 'inactive' CHECK(status IN ('active', 'inactive', 'running', 'paused')),
    last_run_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

-- Pipeline Runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER,
    run_number INTEGER,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'success', 'failed', 'cancelled')),
    trigger_reason TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    duration_seconds INTEGER,
    log TEXT,
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

-- Pipeline Stage History
CREATE TABLE IF NOT EXISTS pipeline_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    stage_name TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'success', 'failed', 'skipped')),
    started_at DATETIME,
    finished_at DATETIME,
    output TEXT,
    FOREIGN KEY(run_id) REFERENCES pipeline_runs(id)
);

-- CI/CD Triggers
CREATE TABLE IF NOT EXISTS cicd_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER,
    trigger_type TEXT DEFAULT 'commit' CHECK(trigger_type IN ('commit', 'schedule', 'webhook', 'manual')),
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    webhook_secret TEXT,
    schedule_cron TEXT,
    enabled INTEGER DEFAULT 1,
    last_triggered_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

-- CI/CD Build Records
CREATE TABLE IF NOT EXISTS cicd_builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER,
    pipeline_id INTEGER,
    commit_sha TEXT,
    commit_message TEXT,
    branch TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'success', 'failed', 'cancelled')),
    started_at DATETIME,
    finished_at DATETIME,
    build_log TEXT,
    artifacts TEXT,
    FOREIGN KEY(trigger_id) REFERENCES cicd_triggers(id),
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(id)
);

-- Insert Sample Projects with Progress
INSERT INTO projects (name, github_repo, status, description, progress_percent, start_date, issue_status) VALUES
('pinball-experience', 'LuckyJunjie/pinball-experience', 'active', '弹珠机游戏开发', 70, '2026-01-15', 'in_progress'),
('securities-analysis-tool', 'LuckyJunjie/securities-analysis-tool', 'active', '证券分析工具', 30, '2026-02-01', 'need_input'),
('smart-factory', 'LuckyJunjie/smart-factory', 'in_progress', '智慧工厂管理系统', 15, '2026-02-20', 'in_progress'),
('gdsnap', 'LuckyJunjie/gdsnap', 'done', 'Godot截图测试工具', 100, '2025-12-01', 'done'),
('gdunit4', 'LuckyJunjie/gdunit4', 'done', 'Godot单元测试框架', 100, '2025-11-15', 'done'),
('poetryforge', 'LuckyJunjie/poetryforge', 'done', '诗词英文学习工具', 100, '2025-10-01', 'forge', 'Luckydone'),
('scriptJunjie/scriptforge', 'done', '脚本工具集', 100, '2025-09-01', 'done'),
('chinese-poetry-english-tool', 'LuckyJunjie/chinese-poetry-english-tool', 'done', '中文诗词英文学习', 100, '2025-08-01', 'done'),
('spring-boot', 'LuckyJunjie/spring-boot', 'done', 'Spring Boot学习项目', 100, '2025-07-01', 'done'),
('pi-pin-ball', 'LuckyJunjie/pi-pin-ball', 'archived', '树莓派弹珠机', 100, '2025-06-01', 'done'),
('pin-ball', 'LuckyJunjie/pin-ball', 'archived', '弹珠机早期版本', 100, '2025-05-01', 'done');

-- Insert Sample Requirements with Detailed Progress
INSERT INTO requirements (project_id, title, maturity, priority, status, progress_percent, start_date, blockers) VALUES
(1, 'pinball 0.1-0.5 基础功能', 'in_progress', 'P0', 'in_progress', 80, '2026-01-15', NULL),
(1, '弹珠机多人模式', 'new', 'P2', 'new', 0, NULL, NULL),
(2, '证券数据展示页面', 'new', 'P2', 'need_input', 20, '2026-02-01', '需要UI设计'),
(3, '需求管理系统后端API', 'in_progress', 'P1', 'in_progress', 40, '2026-02-20', NULL),
(3, '资源监控系统部署', 'in_progress', 'P1', 'in_progress', 10, '2026-02-22', '需要安装Exporter'),
(3, '工具链管理系统', 'designed', 'P1', 'new', 0, NULL, NULL);

-- Insert Toolchain
INSERT INTO toolchain (name, type, description, location, status) VALUES
('GitHub MCP', 'mcp', 'GitHub API集成', 'github.com', 'active'),
('Feishu MCP', 'mcp', '飞书消息通知', 'feishu.com', 'active'),
('Godot Skill', 'skill', 'Godot开发工具', 'workspace/skills/godot', 'active'),
('Weather Skill', 'skill', '天气查询工具', 'workspace/skills/weather', 'active'),
('Browser MCP', 'mcp', '浏览器控制', 'browser', 'active'),
('Windows MCP', 'mcp', 'Windows自动化', 'windows-mcp', 'active');
