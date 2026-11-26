"""Command-line entry point.

Run with the local `.env` so the database credentials reach the process:

    uv run --env-file .env fse db init
    uv run --env-file .env fse load all
"""

from __future__ import annotations

import argparse
import time

from fse.config import get_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fse", description="Football Scouting & Valuation Engine")
    sub = parser.add_subparsers(dest="command")

    db = sub.add_parser("db", help="database management")
    db.add_argument("action", choices=["init"], help="init: apply sql/schema/*.sql (idempotent)")

    load = sub.add_parser("load", help="load source files into the raw schema (idempotent)")
    load.add_argument("source", choices=["wyscout", "transfermarkt", "all"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    from fse.db import apply_schema, connect

    settings = get_settings()
    with connect(settings) as conn:
        if args.command == "db":
            for name in apply_schema(conn):
                print(f"applied {name}")
        elif args.command == "load":
            from fse.ingest.transfermarkt import load_transfermarkt
            from fse.ingest.wyscout import load_wyscout

            start = time.monotonic()
            if args.source in ("wyscout", "all"):
                load_wyscout(conn, settings.data_root)
            if args.source in ("transfermarkt", "all"):
                load_transfermarkt(conn, settings.data_root)
            print(f"done in {time.monotonic() - start:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
