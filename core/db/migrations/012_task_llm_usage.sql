-- Task-level approximate LLM usage (manual or skill/CLI reported; not exact metering)
ALTER TABLE tasks ADD COLUMN est_tokens_total INTEGER DEFAULT 0;
ALTER TABLE tasks ADD COLUMN prompt_rounds INTEGER DEFAULT 0;
