"""Can the app itself use MIGRATION_DATABASE_URL? Read only; prints no part of the URL.

pg_dump, psql and psycopg2.connect(url) hand the URL to libpq, which reads a `?query` part and
decodes `%XX` in the password. The app does not: PostgresRepository splits the URL with its own
pattern and passes each part as is, and scripts/migrate.py builds it from MIGRATION_DATABASE_URL.
So a URL that works for the backup can still stop the switch. This connects exactly as migrate.py
will (RUN_MIGRATIONS=0: no schema step, no write) and runs one read-only query.
"""

import os
import sys

sys.path.insert(0, ".")
os.environ["DATABASE_URL"] = os.environ.get("MIGRATION_DATABASE_URL", "")
os.environ["RUN_MIGRATIONS"] = "0"

from src.infrastructure.persistence.postgres_repository import PostgresRepository  # noqa: E402


def reason(exc: Exception) -> str:
    """Why it failed, in words that quote nothing from the URL or the server's message."""
    text = f"{exc} {exc.__cause__ or ''}"
    if "Cannot parse DATABASE_URL" in text:
        return "the app cannot parse it; it expects postgresql://user:password@host:port/database"
    if "database" in text and "does not exist" in text:
        return "wrong database name; the app does not read a ?query part, remove it"
    if "password authentication failed" in text:
        return "password rejected; the app does not decode %XX, so write the password as is"
    if "Tenant or user not found" in text or ("role" in text and "does not exist" in text):
        return "user not found; the Supabase pooler expects postgres.<project-ref> as the user"
    return f"cannot connect ({type(exc.__cause__ or exc).__name__})"


try:
    repo = PostgresRepository()
except Exception as exc:  # the exact error can carry host or user names
    print(f"::error::APP URL CHECK: FAIL — {reason(exc)}")
    sys.exit(1)
conn = repo.get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SET TRANSACTION READ ONLY")
    cursor.execute("SELECT 1")
    conn.rollback()
finally:
    repo.put_connection(conn)
print(
    "APP URL CHECK: PASS — the app parses MIGRATION_DATABASE_URL and connects, as migrate.py will"
)
