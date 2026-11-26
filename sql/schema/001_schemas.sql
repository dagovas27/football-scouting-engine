-- Database layers (see CLAUDE.md §7):
--   raw       faithful load of the source files, no cleaning
--   core      clean, typed entities built from raw
--   analytics model outputs
--   app       delivery tables (e.g. directivos)
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS app;

-- One row per table load: lets every count in a report be traced to a source file.
CREATE TABLE IF NOT EXISTS raw.load_log (
    load_id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name   text        NOT NULL,
    source_path  text        NOT NULL,
    source_bytes bigint      NOT NULL,
    source_mtime timestamptz NOT NULL,
    row_count    bigint      NOT NULL,
    loaded_at    timestamptz NOT NULL DEFAULT now()
);
