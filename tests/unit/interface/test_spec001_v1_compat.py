"""
V1 regression (spec 001, task T037): the call `student_view.handle_answer_topic` makes into
`StudentService.process_answer` lands on the item's course and topic in the new store.
"""

import json
import uuid

import pytest

pytest.importorskip("streamlit", reason="V1 stack (requirements.txt) not installed")


def test_spec001_v1_answer_lands_on_the_items_course_and_topic(tmp_path):
    from src.application.services.student_service import StudentService
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    repo = SQLiteRepository(db_name=str(tmp_path / "v1_compat.db"))
    conn = repo.get_connection()
    try:
        course_id = "spec001_v1_" + uuid.uuid4().hex[:8]
        conn.execute(
            "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Colegio', '')",
            (course_id, "Curso V1"),
        )
        conn.execute(
            "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
            " rating_deviation, course_id) VALUES (?, 'Fracciones', 'x', ?, 'A', 1000, 350, ?)",
            ("spec001_v1_item", json.dumps(["A", "B"]), course_id),
        )
        conn.commit()
    finally:
        conn.close()
    ok, msg = repo.register_user("spec001_v1_student", "password123", "student", "colegio")
    assert ok, msg
    user_id = repo.login_user("spec001_v1_student", "password123")[0]
    item_data = repo.get_item_by_id("spec001_v1_item")

    # The call shape of handle_answer_topic (student_view.py): no start time → None.
    StudentService(repo).process_answer(user_id, item_data, "A", "", None)

    conn = repo.get_connection()
    try:
        rows = conn.execute(
            "SELECT course_id, topic, current_elo FROM student_course_topic_elo WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()
    assert rows == [(course_id, "Fracciones", 1016.0)]


@pytest.mark.parametrize("option,shown_index", [("A", 0), ("B", 1)])
def test_spec001_v1_stakes_preview_is_the_applied_change(tmp_path, option, shown_index):
    """T076 (FR-030, SC-006): V1's "points at stake" equal the change the engine applies to
    the item's (course, topic) — not a recomputation from the course rating and RD."""
    from src.application.services.student_service import StudentService
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
    from src.interface.streamlit.views.student_view import _stakes

    repo = SQLiteRepository(db_name=str(tmp_path / "v1_stakes.db"))
    ok, msg = repo.register_user("spec001_v1_stakes", "password123", "student", "colegio")
    assert ok, msg
    user_id = repo.login_user("spec001_v1_stakes", "password123")[0]
    course_id = "spec001_v1_" + uuid.uuid4().hex[:8]
    conn = repo.get_connection()
    try:
        conn.execute(
            "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Colegio', '')",
            (course_id, "Curso V1"),
        )
        conn.execute(
            "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
            " rating_deviation, course_id) VALUES (?, 'Fracciones', 'x', ?, 'A', 1150, 350, ?)",
            ("spec001_v1_stakes_item", json.dumps(["A", "B"]), course_id),
        )
        # The course rating (1100, mean RD 225) differs from the item's topic (1300, RD 100).
        conn.executemany(
            "INSERT INTO student_course_topic_elo (user_id, course_id, topic, current_elo, rd,"
            " origin) VALUES (?, ?, ?, ?, ?, 'practice')",
            [
                (user_id, course_id, "Fracciones", 1300.0, 100.0),
                (user_id, course_id, "Decimales", 900.0, 350.0),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    item_data = repo.get_item_by_id("spec001_v1_stakes_item")
    service = StudentService(repo)

    shown = _stakes(service.ratings, user_id, course_id, item_data)[shown_index]
    service.process_answer(user_id, item_data, option, "", 20.0)

    conn = repo.get_connection()
    try:
        after = conn.execute(
            "SELECT current_elo FROM student_course_topic_elo WHERE user_id = ? AND topic = ?",
            (user_id, "Fracciones"),
        ).fetchone()[0]
    finally:
        conn.close()
    assert float(shown.replace("−", "-")) == pytest.approx(after - 1300.0, abs=0.1)


def test_spec001_v1_teacher_topic_table_marks_approximate_baselines():
    """FR-034a (T077): V1's per-topic table names the course and flags reconciled baselines."""
    from src.interface.streamlit.views.teacher_view import _rating_topic_rows

    dash = {
        "course_ratings": [
            {
                "course_name": "Álgebra",
                "current_context": True,
                "topics": [
                    {"topic": "a", "elo": 1100.04, "rd": 200.0, "approximate": True},
                    {"topic": "b", "elo": 1200.0, "rd": 120.0, "approximate": False},
                ],
            },
            {
                "course_name": "Anterior",
                "current_context": False,
                "topics": [
                    {"topic": "a", "elo": 900.0, "rd": 300.0, "approximate": False},
                ],
            },
        ]
    }

    assert _rating_topic_rows(dash) == [
        {"Curso": "Álgebra", "Tópico": "b", "ELO": 1200.0, "RD ±": 120.0, "Aproximado": ""},
        {"Curso": "Álgebra", "Tópico": "a", "ELO": 1100.0, "RD ±": 200.0, "Aproximado": "sí"},
    ]


@pytest.mark.parametrize(
    "value,text,rank",
    [
        (999.6, "1000", "🔰 Iniciado"),
        (999.4, "999", "🌱 Punto de Partida"),
        (None, "—", "Diagnóstico pendiente"),
    ],
)
def test_spec001_v1_number_and_rank_come_from_one_display_value(value, text, rank):
    """FR-028j (T082): V1 shows the half-up display value and the rank of that same value."""
    from src.interface.streamlit.rankings import v1_rated

    assert v1_rated(value)[:2] == (text, rank)


def test_spec001_v1_views_rank_only_through_the_display_value():
    """FR-028j (T082): no V1 view ranks a full-precision rating itself."""
    from pathlib import Path

    views = Path(__file__).parents[3] / "src" / "interface" / "streamlit" / "views"
    offenders = [p.name for p in views.glob("*.py") if "get_rank(" in p.read_text(encoding="utf-8")]
    assert offenders == []
