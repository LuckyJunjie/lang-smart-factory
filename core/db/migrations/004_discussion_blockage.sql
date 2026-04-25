-- Migration: Discussion / blockage (Team report → Hera coordinate)
-- Teams report blockages; Hera lists and resolves via PATCH

CREATE TABLE IF NOT EXISTS discussion_blockage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    requirement_id INTEGER NOT NULL,
    task_id INTEGER,
    reason TEXT NOT NULL,
    options TEXT,
    level TEXT CHECK(level IN ('L1','L2','L3')) DEFAULT NULL,  -- L1 环境/工具, L2 技术难题, L3 资源/依赖冲突
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'resolved', 'cancelled')),
    decision TEXT,
    knowledge_ref TEXT,  -- 可选：记录关联的知识库条目或文档路径
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY(requirement_id) REFERENCES requirements(id)
);

CREATE INDEX IF NOT EXISTS idx_discussion_blockage_team ON discussion_blockage(team);
CREATE INDEX IF NOT EXISTS idx_discussion_blockage_status ON discussion_blockage(status);
CREATE INDEX IF NOT EXISTS idx_discussion_blockage_reported ON discussion_blockage(reported_at);
