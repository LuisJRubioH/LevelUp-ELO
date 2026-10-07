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
