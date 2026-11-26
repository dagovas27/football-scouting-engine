"""Builds the core schema from raw by running sql/etl/*.sql in order."""

from __future__ import annotations

from pathlib import Path

import psycopg

from fse.db import SQL_DIR


def etl_files(sql_dir: Path = SQL_DIR) -> list[Path]:
    return sorted((sql_dir / "etl").glob("*.sql"))


def build_core(conn: psycopg.Connection, sql_dir: Path = SQL_DIR) -> list[str]:
    """Rebuild every core table in one transaction (idempotent)."""
    built = []
    with conn.transaction():
        for path in etl_files(sql_dir):
            conn.execute(path.read_text(encoding="utf-8"))
            built.append(path.name)
    return built
