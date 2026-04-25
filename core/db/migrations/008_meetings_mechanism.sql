-- Migration: Meetings mechanism (risk/blockage decision via multi-agent meeting)
-- Adds:
--   - meetings
--   - meeting_participants
--   - meeting_participant_inputs
--   - links discussion_blockage.meeting_id -> meetings.id

-- -----------------------------
-- Meetings (host sets topic & participants; participants submit analysis/comments)
-- -----------------------------
CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,                       -- meeting theme / title
    problem_to_solve TEXT,                   -- what we need to resolve
    status TEXT DEFAULT 'running' CHECK(status IN ('running', 'concluded', 'cancelled')) ,
    host_agent TEXT NOT NULL,                -- vanguard001 or hera
    initiated_by_agent TEXT,                -- same as host_agent typically
    current_round INTEGER DEFAULT 1,
    conclusion_summary TEXT,               -- host final summary
    conclusion_decision TEXT,             -- optional structured text/JSON
    finalized_at DATETIME,
    created_requirement_ids TEXT,         -- JSON array of requirement ids created at finalize
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);
CREATE INDEX IF NOT EXISTS idx_meetings_host_agent ON meetings(host_agent);

-- -----------------------------
-- Participants invited to a meeting
-- -----------------------------
CREATE TABLE IF NOT EXISTS meeting_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    role_label TEXT,                         -- e.g. architect/scrum_master/devops (optional)
    contribute_focus TEXT,                 -- what this agent should contribute
    status TEXT DEFAULT 'invited' CHECK(status IN ('invited', 'acknowledged', 'submitted')) ,
    acknowledged_at DATETIME,
    submitted_at DATETIME,
    UNIQUE(meeting_id, agent_id),
    FOREIGN KEY(meeting_id) REFERENCES meetings(id)
);

CREATE INDEX IF NOT EXISTS idx_meeting_participants_meeting ON meeting_participants(meeting_id);
CREATE INDEX IF NOT EXISTS idx_meeting_participants_agent ON meeting_participants(agent_id);
CREATE INDEX IF NOT EXISTS idx_meeting_participants_status ON meeting_participants(status);

-- -----------------------------
-- Inputs submitted by participants per round
-- -----------------------------
CREATE TABLE IF NOT EXISTS meeting_participant_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    round_number INTEGER NOT NULL DEFAULT 1,
    analysis TEXT,
    comments TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_id, agent_id, round_number),
    FOREIGN KEY(meeting_id) REFERENCES meetings(id)
);

CREATE INDEX IF NOT EXISTS idx_meeting_inputs_meeting ON meeting_participant_inputs(meeting_id);
CREATE INDEX IF NOT EXISTS idx_meeting_inputs_agent ON meeting_participant_inputs(agent_id);
CREATE INDEX IF NOT EXISTS idx_meeting_inputs_round ON meeting_participant_inputs(round_number);

-- -----------------------------
-- Link blockages <-> meetings
-- -----------------------------
ALTER TABLE discussion_blockage ADD COLUMN meeting_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_discussion_blockage_meeting_id ON discussion_blockage(meeting_id);

