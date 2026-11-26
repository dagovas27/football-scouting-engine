"""Database connection and schema management."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import psycopg

from fse.config import Settings, get_settings

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def connect(settings: Settings | None = None) -> psycopg.Connection:
    settings = settings or get_settings()
    return psycopg.connect(settings.conninfo)


def schema_files(sql_dir: Path = SQL_DIR) -> list[Path]:
    """DDL files applied in lexical order (001_, 020_, ...)."""
    return sorted((sql_dir / "schema").glob("*.sql"))


def apply_schema(conn: psycopg.Connection, sql_dir: Path = SQL_DIR) -> list[str]:
    """Apply every DDL file in one transaction. All statements are idempotent."""
    applied = []
    with conn.transaction():
        for path in schema_files(sql_dir):
            conn.execute(path.read_text(encoding="utf-8"))
            applied.append(path.name)
    return applied


def log_load(conn: psycopg.Connection, table: str, source: Path, rows: int) -> None:
    stat = source.stat()
    conn.execute(
        "INSERT INTO raw.load_log (table_name, source_path, source_bytes, source_mtime, row_count)"
        " VALUES (%s, %s, %s, %s, %s)",
        (table, str(source), stat.st_size, datetime.fromtimestamp(stat.st_mtime, UTC), rows),
    )
