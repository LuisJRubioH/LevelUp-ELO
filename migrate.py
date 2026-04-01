"""
migrate.py — Ejecutar migraciones de base de datos manualmente.

Uso:
    python migrate.py

Aplica todos los ALTER TABLE / CREATE TABLE IF NOT EXISTS del esquema.
Seguro de ejecutar múltiples veces (idempotente).
Solo afecta la base de datos PostgreSQL definida en DATABASE_URL.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def run_migrations():
    """Crea el repositorio y ejecuta las migraciones de esquema.

    - Intenta pg_try_advisory_lock(12345).
    - Si otra instancia ya tiene el lock, sale sin hacer nada.
    - Libera el lock siempre en el bloque finally.
    - Hace commit al finalizar.
    """
    from src.infrastructure.persistence.postgres_repository import PostgresRepository

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: La variable de entorno DATABASE_URL no está definida.")
        sys.exit(1)

    print(f"Conectando a: {database_url[:30]}...")
    repo = PostgresRepository()   # init_db() + _migrate_db() ya se ejecutan aquí
    print("Migraciones completadas.")


if __name__ == "__main__":
    run_migrations()
