"""Crea un usuario administrador local para desarrollo.

Uso:
    python scripts/create_local_admin.py
"""

import sys
import os

# Resolver imports del proyecto (ejecutar desde la raíz del repo)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

_USERNAME = "admin"
_PASSWORD = "admin123"


def main():
    repo = SQLiteRepository()
    conn = repo.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE role = 'admin'")
    if cursor.fetchone():
        conn.close()
        print("Admin user already exists")
        return

    conn.close()

    repo.register_user(_USERNAME, _PASSWORD, role="admin")

    # Asegurar aprobación (register_user pone approved=0 para teachers, 1 para students)
    conn = repo.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved = 1 WHERE username = ?", (_USERNAME,))
    conn.commit()
    conn.close()

    print("ADMIN USER CREATED\n")
    print(f"username: {_USERNAME}")
    print(f"password: {_PASSWORD}")


if __name__ == "__main__":
    main()
