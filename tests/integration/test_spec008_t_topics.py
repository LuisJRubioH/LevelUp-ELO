"""
Spec 008 delivery T (US5; FR-040, FR-042): the coarse `topic` carries the rating; the fine label is
an item's optional `subtopic`, stored in `items.subtopic`, read only by the study report.

Both engines.
"""

import json
import uuid

from tests.integration.conftest import (
    answer,
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    register_course,
    sql,
)


def _course_with_subtopics(repo, rows):
    """A course whose items are (topic, subtopic) pairs. Returns (course_id, [item ids])."""
    course_id = f"spec008_course_{uuid.uuid4().hex[:10]}"
    sql(
        repo,
        "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Colegio', '')",
        (course_id, f"Curso {course_id[-4:]}"),
    )
    ids = []
    for n, (topic, subtopic) in enumerate(rows):
        item_id = f"spec008_item_{uuid.uuid4().hex[:10]}"
        sql(
            repo,
            "INSERT INTO items (id, topic, subtopic, content, options, correct_option, difficulty,"
            " rating_deviation, course_id) VALUES (?, ?, ?, ?, ?, 'A', 1000.0, 350.0, ?)",
            (item_id, topic, subtopic, f"{topic} #{n}", json.dumps(["A", "B"]), course_id),
        )
        ids.append(item_id)
    return course_id, ids


def test_spec008_the_sync_stores_the_subtopic(repo, tmp_path, monkeypatch):
    """FR-040, US5-AS1: a synced item keeps `topic` and `subtopic` apart; an item without one has
    none."""
    course = f"spec008_sync_{uuid.uuid4().hex[:10]}"
    register_course(monkeypatch, course)  # spec 008 C: a synced course is in the catalogue
    with_sub, without = f"{course}_1", f"{course}_2"
    base = {"content": "¿?", "options": ["A", "B"], "correct_option": "A", "difficulty": 1000}
    (tmp_path / "bank").mkdir()
    (tmp_path / "bank" / f"{course}.json").write_text(
        json.dumps(
            [
                {
                    **base,
                    "id": with_sub,
                    "topic": "Pensamiento aleatorio",
                    "subtopic": "porcentaje sobre un total",
                },
                {**base, "id": without, "topic": "Pensamiento aleatorio"},
            ]
        ),
        encoding="utf-8",
    )

    repo.sync_items_from_bank_folder(str(tmp_path / "bank"))

    rows = dict(
        (r[0], (r[1], r[2]))
        for r in sql(repo, "SELECT id, topic, subtopic FROM items WHERE course_id = ?", (course,))
    )
    assert rows == {
        with_sub: ("Pensamiento aleatorio", "porcentaje sobre un total"),
        without: ("Pensamiento aleatorio", None),
    }


def test_spec008_two_answers_in_one_coarse_topic_move_one_rating(repo):
    """FR-040, US5-AS2: two items of one topic and different subtopics move the one rating of the
    topic; no rating is keyed by a subtopic."""
    course_id, (p01, p05) = _course_with_subtopics(
        repo,
        [
            ("Pensamiento aleatorio", "porcentaje sobre un total"),
            ("Pensamiento aleatorio", "frecuencia relativa como probabilidad"),
        ],
    )
    student = make_student(repo)
    enroll(repo, student, course_id)

    answer(repo, student, p01, correct=True)
    answer(repo, student, p05, correct=True)

    topics = [
        r[0]
        for r in sql(
            repo,
            "SELECT topic FROM student_course_topic_elo WHERE user_id = ? AND course_id = ?",
            (student, course_id),
        )
    ]
    assert topics == ["Pensamiento aleatorio"]
    moved = sql(
        repo,
        "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND elo_valid = 1 AND elo_after > elo_before",
        (student,),
    )[0][0]
    assert moved == 2


def _answered(repo):
    """A student who answered three items of «porcentaje» (2 right) in one course and one of
    «proporcionalidad» (wrong) in another, plus an item without subtopic."""
    first, (a, b, c, plain) = _course_with_subtopics(
        repo,
        [
            ("Pensamiento aleatorio", "porcentaje sobre un total"),
            ("Pensamiento aleatorio", "porcentaje sobre un total"),
            ("Pensamiento aleatorio", "porcentaje sobre un total"),
            ("Pensamiento numérico", None),
        ],
    )
    second, (d,) = _course_with_subtopics(
        repo, [("Pensamiento variacional", "proporcionalidad entre variables")]
    )
    student = make_student(repo)
    for course in (first, second):
        enroll(repo, student, course)
    for item, right in ((a, True), (b, True), (c, False), (plain, True), (d, False)):
        answer(repo, student, item, correct=right)
    return student, first, second


def test_spec008_the_subtopic_report_counts_across_courses(repo):
    """FR-042, US5-AS3: per subtopic, across the student's courses, attempts and correct ones,
    weakest first; an item without a subtopic is not in it."""
    from src.application.services.study_report_service import StudyReportService

    student, first, second = _answered(repo)

    report = StudyReportService(repo).subtopic_report(student)

    assert [
        (r["course_id"], r["topic"], r["subtopic"], r["attempts"], r["correct"]) for r in report
    ] == [
        (second, "Pensamiento variacional", "proporcionalidad entre variables", 1, 0),
        (first, "Pensamiento aleatorio", "porcentaje sobre un total", 3, 2),
    ]
    assert report[1]["share_correct"] == 2 / 3


def test_spec008_stats_and_teacher_view_carry_the_report(repo, client):
    """FR-042, US5-AS3: the student's stats and their teacher's view of the student carry the
    report; a teacher without the student is refused."""
    student, first, _ = _answered(repo)
    teacher, stranger = make_teacher(repo), make_teacher(repo)
    group = make_group(repo, teacher, first)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, first, group)
    for t in (teacher, stranger):
        sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (t,))

    mine = client.get("/api/student/stats", headers=headers_for(repo, student))
    theirs = client.get(f"/api/teacher/student/{student}", headers=headers_for(repo, teacher))
    other = client.get(f"/api/teacher/student/{student}", headers=headers_for(repo, stranger))

    assert mine.status_code == 200, mine.text
    assert [r["subtopic"] for r in mine.json()["subtopics"]] == [
        "proporcionalidad entre variables",
        "porcentaje sobre un total",
    ]
    assert theirs.status_code == 200, theirs.text
    assert theirs.json()["subtopics"] == mine.json()["subtopics"]
    assert other.status_code in (403, 404)
