"""
scripts/measure_capacity.py — ¿cuánto cuesta atender a un estudiante?

Mide el **coste de CPU por petición** del ciclo real de práctica
(`/next-question` → `/answer`) con N estudiantes en paralelo, y lo traduce a
cuántos estudiantes concurrentes caben en una CPU dada.

    python scripts/measure_capacity.py --students 30 --rounds 6

Por qué CPU y no tiempo de reloj: el reloj de esta máquina no dice nada sobre
Render. El coste de CPU por petición sí se traslada — es trabajo de Python que
hay que hacer en cualquier sitio. La cuenta final es:

    peticiones/s que aguanta = (CPU disponible) / (CPU por petición)

Lo que esta medición NO cubre, y hay que tener presente al leerla:
  - Corre contra SQLite en local, no contra PostgreSQL en Supabase. No mide
    latencia de red a la base ni espera por el pool de 5 conexiones.
  - Usa TestClient (en proceso): sin red, sin TLS, sin proxy.
  - Una máquina de desarrollo tiene una CPU bastante más rápida que 0.1 vCPU
    compartida; por eso el resultado se expresa en CPU-ms, no en req/s de aquí.

Es decir: da el **suelo** del coste. La realidad solo puede ser peor.
"""

import argparse
import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# La consola de Windows por defecto es cp1252 y no puede imprimir flechas.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

COURSE = "algebra_basica"


def _bootstrap(db_path: str):
    """Arranca la API contra un SQLite temporal. Devuelve (client, repo, deps)."""
    import logging

    os.environ.pop("DATABASE_URL", None)
    os.environ["DB_PATH"] = db_path
    os.environ.setdefault("ADMIN_PASSWORD", "capacity-measure")
    os.environ.setdefault("ADMIN_USER", "admin")

    import api.dependencies as deps

    deps._repo_instance = None
    from api.main import app
    from starlette.testclient import TestClient

    os.environ.pop("DATABASE_URL", None)
    for noisy in ("httpx", "api", "api.ws"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    client = TestClient(app)
    client.__enter__()
    return client, deps.get_repository(), deps


def _make_student(repo, deps, n: int) -> dict:
    """Alta directa por repositorio: el rate limiter de /auth no es lo que se mide."""
    username = f"carga_{n}"
    repo.register_user(username, "password123", "student", education_level="colegio")
    user_id = repo.login_user(username, "password123")[0]
    repo.enroll_user(user_id, COURSE)
    token = deps.create_access_token(user_id, username, "student")
    return {"Authorization": f"Bearer {token}"}


def _practice_round(client, headers, latencies: list, errors: list):
    """Un ciclo real: pedir pregunta, responderla."""
    try:
        t0 = time.perf_counter()
        r = client.post(
            "/api/student/next-question",
            json={"course_id": COURSE, "session_questions_count": 0},
            headers=headers,
        )
        latencies.append(("next-question", (time.perf_counter() - t0) * 1000))
        if r.status_code != 200:
            errors.append(f"next-question {r.status_code}")
            return
        item = r.json().get("item")
        if not item:
            return

        t0 = time.perf_counter()
        r = client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "selected_option": item["options"][0],
                "time_taken": 30.0,
                "elo_topic": item["topic"],
            },
            headers=headers,
        )
        latencies.append(("answer", (time.perf_counter() - t0) * 1000))
        if r.status_code != 200:
            errors.append(f"answer {r.status_code}: {r.text[:120]}")
    except Exception as exc:  # noqa: BLE001 — se reporta al final
        errors.append(f"{type(exc).__name__}: {exc}")


def _pct(values: list, p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(round(p / 100 * (len(ordered) - 1))))
    return ordered[idx]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--students", type=int, default=30, help="estudiantes en paralelo")
    ap.add_argument("--rounds", type=int, default=6, help="preguntas por estudiante")
    ap.add_argument(
        "--think-time",
        type=float,
        default=25.0,
        help="segundos que un estudiante real tarda entre respuestas",
    )
    ap.add_argument(
        "--pace",
        action="store_true",
        help="espaciar las peticiones con --think-time (escenario realista). "
        "Sin esta bandera se mide el techo con todos respondiendo a la vez.",
    )
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        print(f"Preparando API sobre SQLite temporal ({args.students} estudiantes)...")
        client, repo, deps = _bootstrap(os.path.join(tmp, "capacity.db"))

        students = [_make_student(repo, deps, i) for i in range(args.students)]
        print(f"{len(students)} estudiantes listos. Midiendo...")

        latencies: list = []
        errors: list = []
        lock = threading.Lock()
        start_barrier = threading.Barrier(args.students)

        def worker(headers):
            local_lat, local_err = [], []
            start_barrier.wait(timeout=60)
            for i in range(args.rounds):
                if args.pace and i:
                    # Un estudiante real piensa entre pregunta y pregunta. Sin
                    # esta pausa se mide una cola artificial, no la capacidad.
                    time.sleep(args.think_time)
                _practice_round(client, headers, local_lat, local_err)
            with lock:
                latencies.extend(local_lat)
                errors.extend(local_err)

        threads = [threading.Thread(target=worker, args=(h,)) for h in students]

        cpu0 = time.process_time()
        wall0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall = time.perf_counter() - wall0
        cpu = time.process_time() - cpu0

        client.__exit__(None, None, None)

    n = len(latencies)
    if not n:
        print("No se registró ninguna petición.")
        return

    print(f"\n{'':-<62}")
    print(f"{args.students} estudiantes × {args.rounds} rondas — {n} peticiones en {wall:.1f}s")
    print(f"{'':-<62}")

    for endpoint in ("next-question", "answer"):
        vals = [ms for name, ms in latencies if name == endpoint]
        if not vals:
            continue
        print(
            f"{endpoint:<15} n={len(vals):<5} "
            f"p50={_pct(vals, 50):7.1f}ms  p95={_pct(vals, 95):7.1f}ms  "
            f"p99={_pct(vals, 99):7.1f}ms  max={max(vals):7.1f}ms"
        )

    cpu_per_req = cpu / n * 1000
    print(f"\nCPU total {cpu:.2f}s → {cpu_per_req:.1f} CPU-ms por petición")
    print(f"Reloj total {wall:.1f}s → {n / wall:.1f} peticiones/s en esta máquina")

    # Extrapolación: un estudiante genera 2 peticiones (pregunta + respuesta)
    # por cada `think_time` segundos de trabajo real.
    req_per_student_per_s = 2.0 / args.think_time
    print(
        f"\nUn estudiante real ≈ {req_per_student_per_s:.3f} peticiones/s "
        f"(2 por cada {args.think_time:.0f}s de reflexión)"
    )
    print(f"{'CPU disponible':>16} | {'peticiones/s':>13} | {'estudiantes':>12}")
    print(f"{'':->16}-+-{'':->13}-+-{'':->12}")
    for label, cores in (("0.1 vCPU (free)", 0.1), ("0.5 vCPU", 0.5), ("1 vCPU", 1.0)):
        rps = cores * 1000 / cpu_per_req
        print(f"{label:>16} | {rps:>13.1f} | {rps / req_per_student_per_s:>12.0f}")
    print(
        "\nSuelo optimista: SQLite local, sin red, sin pool de PostgreSQL, y una\n"
        "CPU más rápida que una vCPU compartida. La realidad solo puede ser peor."
    )
    if errors:
        print(f"\n{len(errors)} errores. Primeros 5:")
        for e in errors[:5]:
            print("  -", e)


if __name__ == "__main__":
    main()
