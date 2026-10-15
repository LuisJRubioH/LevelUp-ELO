"""Set a new password for an existing admin account.

ADMIN_USER / ADMIN_PASSWORD only *create* the admin on first start (`_seed_admin` never updates an
existing admin), and the app has no endpoint to change a password, so changing ADMIN_PASSWORD in
the host's settings does not change the admin's password. This script does, directly in the
database, with the app's own Argon2id hashing.

Usage (run from the repository root, on your own machine, after
`pip install -r requirements-api.txt`):

    # PostgreSQL: asks for the database URL with a hidden prompt (never typed into a command, so
    # it stays out of the shell history), then for the new password twice
    python scripts/reset_admin_password.py --username admin

    # SQLite (local development)
    python scripts/reset_admin_password.py --sqlite data/elo_database.db --username admin

Without a terminal, the URL comes from MIGRATION_DATABASE_URL (or DATABASE_URL) and the password
from NEW_ADMIN_PASSWORD. Neither is ever printed, logged or passed as an argument. The script never
builds a repository (so it runs no migration); it changes one row, `users.password_hash` of the
named user whose role is `admin`, in one transaction, and exits 1 if that is not exactly one row.
"""

from __future__ import annotations

import argparse
import getpass
import os
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.security.hashing_service import HashingService  # noqa: E402

MIN_LENGTH = 12
_UPDATE = "UPDATE users SET password_hash = {p} WHERE username = {p} AND role = 'admin'"


def read_new_password(env=os.environ, prompt=getpass.getpass) -> str:
    """The new password from NEW_ADMIN_PASSWORD or a hidden prompt (asked twice)."""
    password = env.get("NEW_ADMIN_PASSWORD")
    if password is None:
        password = prompt("New admin password: ")
        if prompt("Repeat it: ") != password:
            raise ValueError("the two entries differ")
    if len(password) < MIN_LENGTH or password.strip() != password:
        raise ValueError(f"use at least {MIN_LENGTH} characters, without surrounding spaces")
    return password


def set_admin_password(conn, placeholder: str, username: str, password_hash: str) -> int:
    """Update one admin's hash in one transaction; returns the number of rows changed."""
    cursor = conn.cursor()
    try:
        cursor.execute(_UPDATE.format(p=placeholder), (password_hash, username))
        changed = cursor.rowcount
        if changed != 1:
            conn.rollback()
            return changed
        conn.commit()
        return changed
    except Exception:
        conn.rollback()
        raise


def database_url(env=os.environ, prompt=getpass.getpass, interactive=None) -> str | None:
    """The PostgreSQL URL from the environment or, in a terminal, from a hidden prompt."""
    url = env.get("MIGRATION_DATABASE_URL") or env.get("DATABASE_URL")
    if url:
        return url
    if interactive is None:
        interactive = sys.stdin.isatty()
    return (prompt("PostgreSQL URL (hidden): ").strip() or None) if interactive else None


def connection_error(exc: Exception, url: str | None) -> str:
    """The reason a connection failed, without the URL or its password.

    libpq quotes a malformed URL back in its error, password included
    (`invalid percent-encoded token: "<password>"`), so that error is never shown as given.
    """
    message = str(exc).strip()
    if "invalid dsn" in message:
        return "the URL is not a valid PostgreSQL URL (postgresql://user:password@host:port/db)"
    if url:
        password = url.split("://", 1)[-1].rpartition("@")[0].partition(":")[2]
        for secret in (url, password):
            if secret:
                message = message.replace(secret, "***")
    return message


def _connect(args, url):
    if args.sqlite:
        return sqlite3.connect(args.sqlite), "?"
    import psycopg2

    sslmode = os.environ.get("DATABASE_SSLMODE", "require")
    return psycopg2.connect(url, sslmode=sslmode, connect_timeout=15), "%s"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--username", default=os.environ.get("ADMIN_USER", "admin"))
    ap.add_argument("--sqlite", help="path of a local SQLite database instead of PostgreSQL")
    args = ap.parse_args(argv)

    url = None if args.sqlite else database_url()
    if not args.sqlite and not url:
        print(
            "ERROR: no database URL. Run it in a terminal, set MIGRATION_DATABASE_URL, "
            "or pass --sqlite PATH. Nothing changed.",
            file=sys.stderr,
        )
        return 2
    try:
        password = read_new_password()
    except ValueError as exc:
        print(f"ERROR: {exc}. Nothing changed.", file=sys.stderr)
        return 2

    password_hash = HashingService().hash_password(password)
    del password
    try:
        conn, placeholder = _connect(args, url)
    except Exception as exc:
        print(
            f"ERROR: cannot connect: {connection_error(exc, url)}. Nothing changed.",
            file=sys.stderr,
        )
        return 1
    try:
        changed = set_admin_password(conn, placeholder, args.username, password_hash)
    finally:
        conn.close()
    if changed != 1:
        print(
            f"ERROR: no admin account named {args.username!r} ({changed} rows matched). "
            "Nothing changed.",
            file=sys.stderr,
        )
        return 1
    print(f"Admin password updated for {args.username!r}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
