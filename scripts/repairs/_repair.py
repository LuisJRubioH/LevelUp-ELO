"""
Shared runner of the repair scripts (spec 002 FR-018).

A repair is never part of the start: the owner runs it knowingly. Read-only by default (it counts
the rows it would change); `--apply` writes. It prints counts only, never rows (constitution VI).

Engine: PostgreSQL through MIGRATION_DATABASE_URL or DATABASE_URL (the session pooler, port
5432, as scripts/migrate.py); otherwise the local SQLite of DB_PATH. The repository is built with
RUN_MIGRATIONS=0, so running a repair migrates nothing.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _repository():
    os.environ["RUN_MIGRATIONS"] = "0"
    url = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if url:
        os.environ["DATABASE_URL"] = url
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        return PostgresRepository()
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    return SQLiteRepository()


def run(method: str, what: str, doc: str) -> None:
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument("--apply", action="store_true", help="write the changes (default: count)")
    args = parser.parse_args()
    rows = getattr(_repository(), method)(apply=args.apply)
    if args.apply:
        print(f"{rows} rows changed: {what}")
    else:
        print(f"{rows} rows would change: {what} (dry run; --apply to write)")
