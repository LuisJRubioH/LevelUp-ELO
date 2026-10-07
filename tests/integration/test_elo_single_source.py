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

from src.domain.elo.model import is_valid_response_time
from tests.integration.conftest import rating_of, set_rating
from tests.integration.conftest import sql as _sql

# Spec 001: the rating is the item's own (course, topic) row of student_course_topic_elo.

# Two-engine fixtures (`repo`, `student`, `_postgres_repo`) live in tests/integration/conftest.py.


# ── Utilidades ────────────────────────────────────────────────────────────────


def _any_item(repo) -> tuple[str, str, str]:
    """Un ítem real del banco: (id, course_id, topic). El bootstrap ya sincronizó items."""
    rows = _sql(repo, "SELECT id, course_id, topic FROM items LIMIT 1")
    assert rows, "El banco de ítems está vacío; sync_items_from_bank_folder no corrió."
    return tuple(rows[0])


def _answer(repo, user_id, item_id, elo_after, time_taken=30.0):
    """Una respuesta que fija el ELO indicado; la validez la decide el dominio, como en el servicio."""

    def compute(state):
        valid = is_valid_response_time(time_taken)
        return (
            {
                "is_correct": True,
                "difficulty": state["item_difficulty"],
                "topic": state["topic"],
                "elo_after": elo_after if valid else state["elo"],
                "elo_before": state["elo"],
                "prob_failure": 0.5,
                "expected_score": 0.5,
                "time_taken": time_taken,
                "confidence_score": None,
                "error_type": None,
                "rating_deviation": 300.0,
                "elo_valid": valid,
            },
            state["item_difficulty"],
            state["item_rd"],
        )

    return repo.save_answer_transaction(user_id=user_id, item_id=item_id, compute=compute)


def _elo(repo, user_id, item) -> float:
    return rating_of(repo, user_id, item[1], item[2])


# ── Fuente única de ELO (#2) ──────────────────────────────────────────────────


def test_diagnostic_baseline_survives_until_the_first_practice(repo, student):
    """El baseline del diagnóstico se lee aunque no exista ningún intento."""
    item = _any_item(repo)
    repo.set_topic_rating_baseline(student, item[1], item[2], 1300.0)

    assert _elo(repo, student, item) == 1300.0

    _answer(repo, student, item[0], elo_after=1320.0)

    assert _elo(repo, student, item) == 1320.0


def test_an_invalid_attempt_does_not_move_the_rating(repo, student):
    """Un intento fuera del rango [3s, 600s] se registra pero no altera el rating."""
    item = _any_item(repo)
    set_rating(repo, student, item[1], item[2], 1200.0)

    _answer(repo, student, item[0], elo_after=1220.0, time_taken=45.0)
    assert _elo(repo, student, item) == 1220.0

    # 1 segundo = adivinanza sin leer: se guarda el intento, no el rating.
    _answer(repo, student, item[0], elo_after=9999.0, time_taken=1.0)

    assert _elo(repo, student, item) == 1220.0

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


# test_global_elo_stays_the_average_of_the_canonical_topics was removed by spec 001
# (FR-028, research R4): users.current_elo is a legacy column, never written; the overall
# rating is derived by RatingReadService (tests/unit/application/test_spec001_rating_read_service.py).


# ── Unidad de trabajo bajo concurrencia (#3) ──────────────────────────────────


def test_concurrent_answers_on_the_same_item_compose_serially(repo, student):
    """Ocho respuestas simultáneas no pierden ninguna actualización.

    Cada una suma +10 al rating que lee, así que el resultado solo puede ser
    baseline + 80 si el ciclo leer→calcular→escribir se serializó. Sin el
    bloqueo, varias parten del mismo rating y se pisan entre sí.
    """
    item = _any_item(repo)
    item_id = item[0]
    set_rating(repo, student, item[1], item[2], 1000.0)

    errors: list[BaseException] = []
    start = threading.Barrier(8)

    def answer_once():
        def compute(state):
            return (
                {
                    "is_correct": True,
                    "difficulty": state["item_difficulty"],
                    "topic": state["topic"],
                    "elo_after": state["elo"] + 10.0,
                    "elo_before": state["elo"],
                    "prob_failure": 0.5,
                    "expected_score": 0.5,
                    "time_taken": 30.0,
                    "confidence_score": None,
                    "error_type": None,
                    "rating_deviation": 300.0,
                    "elo_valid": True,
                },
                state["item_difficulty"],
                state["item_rd"],
            )

        try:
            start.wait(timeout=10)
            repo.save_answer_transaction(user_id=student, item_id=item_id, compute=compute)
        except BaseException as exc:  # noqa: BLE001 — se revisa en el hilo principal
            errors.append(exc)

    threads = [threading.Thread(target=answer_once) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=120)

    assert not errors, errors
    assert _elo(repo, student, item) == 1080.0
