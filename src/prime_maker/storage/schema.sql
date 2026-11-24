-- Optional SQLite schema for persisted prime-maker run results.
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY,
    command TEXT NOT NULL CHECK (command IN ('check', 'list', 'count', 'analyze', 'random')),
    parameters_json TEXT NOT NULL CHECK (json_valid(parameters_json)),
    result_json TEXT NOT NULL CHECK (json_valid(result_json)),
    seed INTEGER CHECK (seed IS NULL OR seed >= 0),
    package_version TEXT NOT NULL,
    started_at TEXT NOT NULL,
    duration_ms REAL NOT NULL CHECK (duration_ms >= 0)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_runs_command_started_at ON runs (command, started_at);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs (started_at);
