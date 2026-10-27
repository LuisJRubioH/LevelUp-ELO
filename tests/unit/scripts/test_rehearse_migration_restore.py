"""
rehearse_migration.py: which pg_restore errors leave the restored copy intact.

A dump from a newer pg_dump starts with session settings an older server does not know: pg_dump
17 and later write `SET transaction_timeout = 0`, which PostgreSQL 16 refuses while restoring
every table and row (seen in CI: pg_dump 18.6 against a 16.15 server). Any other error still
fails the rehearsal.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from rehearse_migration import restore_errors  # noqa: E402

NEWER_CLIENT = (
    "pg_restore: error: could not execute query: ERROR:  unrecognized configuration parameter"
    ' "transaction_timeout"\nCommand was: SET transaction_timeout = 0;\n'
    "pg_restore: warning: errors ignored on restore: 1\n"
)


def test_a_newer_clients_session_setting_does_not_fail_the_restore():
    errors, benign = restore_errors(NEWER_CLIENT)
    assert errors and errors == benign


def test_the_existing_public_schema_does_not_fail_the_restore():
    errors, benign = restore_errors(
        'pg_restore: error: could not execute query: ERROR:  schema "public" already exists\n'
    )
    assert errors and errors == benign


def test_any_other_restore_error_fails_it():
    stderr = NEWER_CLIENT + (
        "pg_restore: error: could not execute query: ERROR:  relation"
        ' "users" already exists\n'
        "pg_restore: error: could not execute query: ERROR:  unrecognized configuration"
        ' parameter "search_path_typo"\n'
    )
    errors, benign = restore_errors(stderr)
    assert len(errors) == 3
    assert [e for e in errors if e not in benign] == errors[1:]
