-- Remote repository metadata for projects (URL already in repo_url; these fields track branch, head, last sync time)

ALTER TABLE projects ADD COLUMN repo_default_branch TEXT;
ALTER TABLE projects ADD COLUMN repo_last_sync_at TEXT;
ALTER TABLE projects ADD COLUMN repo_head_commit TEXT;
ALTER TABLE projects ADD COLUMN repo_remote_notes TEXT;
