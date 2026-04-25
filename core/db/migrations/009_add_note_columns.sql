-- Migration: add note columns (compat with tests/UI)
ALTER TABLE requirements ADD COLUMN note TEXT;
ALTER TABLE tasks ADD COLUMN note TEXT;

