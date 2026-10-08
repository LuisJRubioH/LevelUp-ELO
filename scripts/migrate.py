"""
scripts/migrate.py — Aplica esquema, seeds y backfills. Un paso, una vez.

Uso:
    python scripts/migrate.py

Va SEPARADO del arranque HTTP y así debe quedarse. `_migrate_db()` toma
`pg_try_advisory_lock`, que es un lock de sesión: sobre el pooler de
transacciones de Supabase (puerto 6543) la sesión física no sobrevive al
commit, así que el lock puede acabar liberándose desde otra sesión y dejar de
proteger nada. Este script debe correr por conexión DIRECTA (puerto 5432) o
por pooler de SESIÓN, que es lo que aporta MIGRATION_DATABASE_URL.

Variables de entorno:
    MIGRATION_DATABASE_URL  conexión directa/sesión — la preferida
    DATABASE_URL            respaldo si no se define la anterior

En Render encabeza el startCommand (preDeployCommand no existe en plan free),
con el servicio web en RUN_MIGRATIONS=0. Si falla, uvicorn no arranca.
Es idempotente: solo ALTER TABLE ADD COLUMN IF NOT EXISTS y seeds que no
sobrescriben (AGENTS.md R8).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_migrations() -> None:
    """Construye el repositorio con el bootstrap forzado y sale."""
    database_url = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: define MIGRATION_DATABASE_URL o DATABASE_URL.")
        sys.exit(1)

    # El repositorio lee DATABASE_URL al construirse; apuntarlo a la conexión
    # de migración antes de instanciarlo.
    os.environ["DATABASE_URL"] = database_url
    os.environ["RUN_MIGRATIONS"] = "1"

    host = database_url.split("@")[-1].split("/")[0] if "@" in database_url else "?"
    if ":6543" in host:
        print(
            f"AVISO: {host} es el pooler de transacciones. Los locks de sesión no "
            "son fiables ahí — usa el puerto directo 5432 o un pooler de sesión."
        )
    print(f"Migrando contra {host} ...")

    from src.infrastructure.persistence.postgres_repository import PostgresRepository

    PostgresRepository()  # __init__ ejecuta _bootstrap_schema()
    print("Migraciones completadas.")


if __name__ == "__main__":
    run_migrations()
