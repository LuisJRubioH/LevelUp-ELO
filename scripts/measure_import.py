"""
scripts/measure_import.py — ¿cuánto tarda importar 500 estudiantes? (spec 009, SC-002, P12)

Recorre el camino real de la importación inicial por la API —vista previa, confirmación y el
trabajador que crea las cuentas en bloques de 25— con un archivo inventado de N estudiantes, y
mide el tiempo de reloj y de CPU de cada paso, en SQLite y, si se indica, en un PostgreSQL local.

    python scripts/measure_import.py --students 500
    POSTGRES_TEST_DATABASE_URL=postgresql://… \
        python scripts/measure_import.py --students 500 --postgres

Solo identificaciones inventadas (el repositorio es público). Nunca se ejecuta contra una base que
no sea local: la URL de PostgreSQL debe apuntar a localhost.

Lo que esta medición NO cubre:
  - La red hasta Supabase ni la CPU compartida de Render: el resultado de aquí es un suelo.
  - El coste dominante es el hash Argon2id de cada contraseña inicial (~100 ms y 64 MiB cada
    uno, a lo sumo dos a la vez por proceso); ese coste se traslada a cualquier máquina.
"""

import argparse
import csv
import io
import json
import os
import resource
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
_HEADER = ["Número de documento", "Nombres", "Apellidos", "Grado que cursas en 2027", "Institución"]
_SURNAMES = "Pérez Gómez Rodríguez López Martínez García Sánchez Ramírez Torres Rojas".split()


def _repo(postgres: bool):
    if postgres:
        url = os.environ.get("POSTGRES_TEST_DATABASE_URL", "")
        if urlsplit(url).hostname not in _LOCAL_HOSTS:
            sys.exit("POSTGRES_TEST_DATABASE_URL debe apuntar a una base local desechable.")
        os.environ["DATABASE_URL"] = url
        os.environ.setdefault("DATABASE_SSLMODE", "disable")
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        return PostgresRepository()
    os.environ.pop("DATABASE_URL", None)
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    return SQLiteRepository(db_name=os.path.join(tempfile.mkdtemp(), "measure_import.db"))


def _sql(repo, statement, params=()):
    conn = repo.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            statement.replace("?", "%s") if hasattr(repo, "put_connection") else statement, params
        )
        rows = cursor.fetchall() if cursor.description else []
        conn.commit()
        return rows
    finally:
        repo.put_connection(conn) if hasattr(repo, "put_connection") else conn.close()


def _setup(repo):
    """Un admin, un docente aprobado, un curso y un grupo de 9.º para una institución inventada."""
    tag = uuid.uuid4().hex[:8]
    for username in (f"measure_admin_{tag}", f"measure_teacher_{tag}"):
        ok, message = repo.register_user(username, "measure-only-1", "teacher")
        assert ok, message
    admin = _sql(repo, "SELECT id FROM users WHERE username = ?", (f"measure_admin_{tag}",))[0][0]
    teacher = _sql(repo, "SELECT id FROM users WHERE username = ?", (f"measure_teacher_{tag}",))[0][
        0
    ]
    _sql(repo, "UPDATE users SET role = 'admin', approved = 1 WHERE id = ?", (admin,))
    _sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    course_id = f"measure_course_{tag}"
    _sql(
        repo,
        "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Semillero', '')",
        (course_id, course_id),
    )
    institution = f"Colegio Medición {tag}"
    ok, message, group_id = repo.create_group_for_teacher(
        admin, teacher, f"Semillero 9 {tag}", course_id, institution=institution, grade=9
    )
    assert ok, message
    return admin, institution


def _file(students: int, institution: str) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_HEADER)
    base = int(uuid.uuid4().int % 10**6) * 10**3
    for n in range(students):
        writer.writerow(
            [str(5_000_000_000 + base + n), "Ana", _SURNAMES[n % 10], "Noveno", institution]
        )
    return buffer.getvalue().encode("utf-8")


def _timed(step):
    wall, cpu = time.perf_counter(), time.process_time()
    result = step()
    return result, time.perf_counter() - wall, time.process_time() - cpu


def measure(postgres: bool, students: int) -> dict:
    import logging

    logging.disable(logging.WARNING)
    os.environ.setdefault("ADMIN_PASSWORD", "measure-import")
    repo = _repo(postgres)
    import api.dependencies as deps
    from api.dependencies import create_access_token
    from api.main import app
    from starlette.testclient import TestClient

    deps._repo_instance = repo
    client = TestClient(app, base_url="https://measure.local")
    admin, institution = _setup(repo)
    headers = {"Authorization": "Bearer " + create_access_token(admin, "admin", "admin")}
    data = _file(students, institution)
    last_day = (datetime.now(timezone.utc) + timedelta(days=60)).date().isoformat()
    form = {
        "mapping": json.dumps(
            {
                "identification": "Número de documento",
                "name": ["Nombres", "Apellidos"],
                "grade": "Grado que cursas en 2027",
                "institution": "Institución",
            }
        ),
        "batch": json.dumps({"level": "semillero", "access_until": last_day}),
        "pairing": "[]",
    }
    files = {"file": ("medicion.csv", data, "text/csv")}

    preview, preview_wall, preview_cpu = _timed(
        lambda: client.post("/api/admin/imports/preview", headers=headers, files=files, data=form)
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["counts"]["new"] == students, preview.json()["counts"]

    def run():
        confirmed = client.post(
            "/api/admin/imports",
            headers=headers,
            files=files,
            data={**form, "digest": preview.json()["digest"]},
        )
        assert confirmed.status_code == 202, confirmed.text
        import_id = confirmed.json()["import_id"]
        while True:
            record = client.get(f"/api/admin/imports/{import_id}", headers=headers).json()
            if record["state"] != "running":
                return record
            time.sleep(0.5)

    record, import_wall, import_cpu = _timed(run)
    return {
        "engine": "PostgreSQL (local)" if postgres else "SQLite",
        "students": students,
        "state": record["state"],
        "created": record["counts"]["created"],
        "preview_s": round(preview_wall, 2),
        "preview_cpu_s": round(preview_cpu, 2),
        "import_s": round(import_wall, 2),
        "import_cpu_s": round(import_cpu, 2),
        "per_student_ms": round(1000 * import_wall / students, 1),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--students", type=int, default=500)
    parser.add_argument("--postgres", action="store_true", help="PostgreSQL local, no SQLite")
    args = parser.parse_args()
    print(json.dumps(measure(args.postgres, args.students), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
