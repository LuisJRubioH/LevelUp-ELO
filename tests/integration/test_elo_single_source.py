"""
tests/integration/test_elo_single_source.py
============================================
Regresión de los hallazgos P1 #2 y #3 de la auditoría de arquitectura
(2026-09-05): "varias fuentes de ELO producen estados incompatibles" y "la
transacción de respuesta no protege el ciclo de lectura y cálculo".

`student_topic_elo` es el único estado canónico del rating. Lo escriben tres
caminos —diagnóstico, respuesta con tiempo válido y validación docente de un
procedimiento— y `get_latest_elo_by_topic` se limita a leerlo. El ciclo
leer→calcular→escribir de una respuesta corre entero dentro de una transacción
con las filas bloqueadas.

Escenarios que la auditoría pide verificar:
  1. baseline → primera práctica
  2. intento inválido → siguiente práctica
  3. procedimiento → dos prácticas sucesivas
  4. respuestas concurrentes sobre el mismo estudiante y el mismo ítem

Corre en LOS DOS motores: SQLite siempre, PostgreSQL cuando hay
POSTGRES_TEST_DATABASE_URL (el job "Guardas PostgreSQL" de CI lo define).
La paridad estática de `db_sync_check.py` no demuestra equivalencia de
resultados; esto sí.
"""

import threading

from tests.integration.conftest import sql as _sql

TOPIC = "Álgebra"

# Two-engine fixtures (`repo`, `student`, `_postgres_repo`) live in tests/integration/conftest.py.


# ── Utilidades ────────────────────────────────────────────────────────────────


def _any_item(repo) -> tuple[str, str]:
    """Un ítem real del banco: (id, topic). El bootstrap ya sincronizó items."""
    rows = _sql(repo, "SELECT id, topic FROM items LIMIT 1")
    assert rows, "El banco de ítems está vacío; sync_items_from_bank_folder no corrió."
    return rows[0][0], rows[0][1]


def _answer(repo, user_id, item_id, topic, elo_after, time_taken=30.0):
    """Una respuesta que fija el ELO indicado, como hace StudentService."""

    def compute(state):
        return (
            {
                "is_correct": True,
                "difficulty": state["item_difficulty"],
                "topic": topic,
                "elo_after": elo_after,
                "elo_before": state["elo"],
                "prob_failure": 0.5,
                "expected_score": 0.5,
                "time_taken": time_taken,
                "confidence_score": None,
                "error_type": None,
                "rating_deviation": 300.0,
            },
            state["item_difficulty"],
            state["item_rd"],
        )

    return repo.save_answer_transaction(
        user_id=user_id, item_id=item_id, topic=topic, compute=compute
    )


def _elo(repo, user_id, topic) -> float:
    return repo.get_latest_elo_by_topic(user_id)[topic][0]


# ── Fuente única de ELO (#2) ──────────────────────────────────────────────────


def test_diagnostic_baseline_survives_until_the_first_practice(repo, student):
    """El baseline del diagnóstico se lee aunque no exista ningún intento."""
    repo.set_topic_elo_baseline(student, TOPIC, 1300.0)

    assert _elo(repo, student, TOPIC) == 1300.0

    item_id, _ = _any_item(repo)
    _answer(repo, student, item_id, TOPIC, elo_after=1320.0)

    assert _elo(repo, student, TOPIC) == 1320.0


def test_an_invalid_attempt_does_not_move_the_rating(repo, student):
    """Un intento fuera del rango [3s, 600s] se registra pero no altera el rating."""
    repo.set_topic_elo_baseline(student, TOPIC, 1200.0)
    item_id, _ = _any_item(repo)

    _answer(repo, student, item_id, TOPIC, elo_after=1220.0, time_taken=45.0)
    assert _elo(repo, student, TOPIC) == 1220.0

    # 1 segundo = adivinanza sin leer: se guarda el intento, no el rating.
    _answer(repo, student, item_id, TOPIC, elo_after=9999.0, time_taken=1.0)

    assert _elo(repo, student, TOPIC) == 1220.0

    invalid = _sql(
        repo,
        "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND elo_valid = 0",
        (student,),
    )[0][0]
    assert invalid == 1, "El intento inválido debe quedar registrado para analítica."


def test_a_validated_procedure_delta_is_applied_exactly_once(repo, student):
    """El ajuste del docente entra una vez, no en cada lectura posterior."""
    item_id, item_topic = _any_item(repo)
    repo.set_topic_elo_baseline(student, item_topic, 1000.0)

    submission_id = _sql(
        repo,
        """INSERT INTO procedure_submissions
           (student_id, item_id, item_content, image_data, status)
           VALUES (?, ?, ?, ?, 'pending') RETURNING id""",
        (student, item_id, "contenido de prueba", b"imagen"),
    )[0][0]

    # procedure_elo_delta(100) = (100 - 50) * 0.2 = +10
    assert repo.validate_procedure_submission(submission_id, teacher_score=100.0)
    assert _elo(repo, student, item_topic) == 1010.0

    # Dos prácticas sucesivas: el +10 ya está dentro del rating y no se re-suma.
    _answer(repo, student, item_id, item_topic, elo_after=1030.0)
    assert _elo(repo, student, item_topic) == 1030.0

    _answer(repo, student, item_id, item_topic, elo_after=1045.0)
    assert _elo(repo, student, item_topic) == 1045.0


def test_global_elo_stays_the_average_of_the_canonical_topics(repo, student):
    """users.current_elo es estado derivado, no una cuarta fuente."""
    repo.set_topic_elo_baseline(student, "Álgebra", 1200.0)
    repo.set_topic_elo_baseline(student, "Geometría", 1000.0)

    current = _sql(repo, "SELECT current_elo FROM users WHERE id = ?", (student,))[0][0]
    assert float(current) == 1100.0


# ── Unidad de trabajo bajo concurrencia (#3) ──────────────────────────────────


def test_concurrent_answers_on_the_same_item_compose_serially(repo, student):
    """Ocho respuestas simultáneas no pierden ninguna actualización.

    Cada una suma +10 al rating que lee, así que el resultado solo puede ser
    baseline + 80 si el ciclo leer→calcular→escribir se serializó. Sin el
    bloqueo, varias parten del mismo rating y se pisan entre sí.
    """
    repo.set_topic_elo_baseline(student, TOPIC, 1000.0)
    item_id, _ = _any_item(repo)

    errors: list[BaseException] = []
    start = threading.Barrier(8)

    def answer_once():
        def compute(state):
            return (
                {
                    "is_correct": True,
                    "difficulty": state["item_difficulty"],
                    "topic": TOPIC,
                    "elo_after": state["elo"] + 10.0,
                    "elo_before": state["elo"],
                    "prob_failure": 0.5,
                    "expected_score": 0.5,
                    "time_taken": 30.0,
                    "confidence_score": None,
                    "error_type": None,
                    "rating_deviation": 300.0,
                },
                state["item_difficulty"],
                state["item_rd"],
            )

        try:
            start.wait(timeout=10)
            repo.save_answer_transaction(
                user_id=student, item_id=item_id, topic=TOPIC, compute=compute
            )
        except BaseException as exc:  # noqa: BLE001 — se revisa en el hilo principal
            errors.append(exc)

    threads = [threading.Thread(target=answer_once) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=120)

    assert not errors, errors
    assert _elo(repo, student, TOPIC) == 1080.0
