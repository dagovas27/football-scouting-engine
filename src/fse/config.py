"""Runtime settings read from environment variables (never from committed files)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_root: Path
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str | None

    @property
    def conninfo(self) -> str:
        parts = {
            "host": self.db_host,
            "port": str(self.db_port),
            "dbname": self.db_name,
            "user": self.db_user,
        }
        if self.db_password:
            parts["password"] = self.db_password
        return " ".join(f"{k}={v}" for k, v in parts.items())


def get_settings() -> Settings:
    """Build settings from the environment.

    Database variables reuse the names Docker Compose reads from `.env`
    (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) so there is one source of truth.
    """
    return Settings(
        data_root=Path(os.environ.get("FSE_DATA_ROOT", "~/Documents/data-sc")).expanduser(),
        db_host=os.environ.get("FSE_DB_HOST", "localhost"),
        db_port=int(os.environ.get("FSE_DB_PORT", "5432")),
        db_name=os.environ.get("POSTGRES_DB", "fse"),
        db_user=os.environ.get("POSTGRES_USER", "fse"),
        db_password=os.environ.get("POSTGRES_PASSWORD"),
    )
