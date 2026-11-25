"""
Spec 008 delivery R (US6; FR-035, FR-036): an item reserved for templates.

A bank item marked `"reserved": true` is stamped by the sync and served only through a teacher's
template: never in practice, the diagnostic, a standard exam, PvP (which draws from the same read),
the course map or the block counts. A teacher sees it when building a template, and a student
who starts that template gets it. Removing the mark puts it back in circulation. Both engines.
"""

import pytest

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    sql,
)
from tests.integration.test_spec008_l_item_life import LifeBank, stored


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _reserve(repo, bank, item_id, reserved=True):
    bank.item(item_id)["reserved"] = reserved
    bank.sync(repo)


def test_spec008_r_a_reserved_item_is_stamped_and_released(repo, tmp_path, monkeypatch):
    """FR-035: the sync stamps the mark; removing it (or false) clears it; a new id may arrive
    reserved."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    bank.item(bank.ids[2])["reserved"] = True
    bank.sync(repo)
    assert stored(repo, bank.ids[2], "reserved_at") is not None

    _reserve(repo, bank, bank.ids[0])
    assert stored(repo, bank.ids[0], "reserved_at") is not None
    assert stored(repo, bank.ids[1], "reserved_at") is None

    _reserve(repo, bank, bank.ids[0], reserved=False)
    assert stored(repo, bank.ids[0], "reserved_at") is None


def test_spec008_r_practice_never_serves_a_reserved_item(repo, tmp_path, monkeypatch):
    """FR-035: the read every serving path shares — practice, the diagnostic, standard exams and
    PvP — skips a reserved item, by course, by block and by topic; practice never draws it."""
    from src.application.services.student_service import StudentService

    bank = LifeBank(tmp_path, monkeypatch, n=3, block="Bloque R")
    reserved = bank.ids[0]
    _reserve(repo, bank, reserved)

    reads = [
        repo.get_items_from_db(course_id=bank.course),
        repo.get_items_from_db(course_id=bank.course, block="Bloque R"),
        repo.get_items_from_db(topic="Vida"),
    ]
    assert [{i["id"] for i in r} & set(bank.ids) for r in reads] == [set(bank.ids[1:])] * 3
    every = repo.get_items_from_db(course_id=bank.course, include_reserved=True)
    assert {i["id"] for i in every} == set(bank.ids)
    assert repo.get_course_blocks(bank.course) == [{"block": "Bloque R", "item_count": 2}]

    student = make_student(repo)
    enroll(repo, student, bank.course)
    service = StudentService(repository=repo)
    drawn = set()
    for _ in range(30):
        item, _status = service.get_next_question(
            student_id=student, course_id=bank.course, session_correct_ids=set()
        )
        drawn.add(item["id"])
    assert reserved not in drawn


def test_spec008_r_exams_and_the_diagnostic_skip_a_reserved_item(
    repo, client, tmp_path, monkeypatch
):
    """FR-035: a standard exam and the diagnostic asked for more items than the course holds
    never draw the reserved one."""
    bank = LifeBank(tmp_path, monkeypatch, n=4)
    _reserve(repo, bank, bank.ids[0])
    student = make_student(repo)
    enroll(repo, student, bank.course)
    headers = headers_for(repo, student)

    exam = client.post(
        "/api/student/exam/start",
        headers=headers,
        json={"course_id": bank.course, "n_questions": 4, "time_limit_minutes": 10},
    )
    diagnostic = client.get(f"/api/student/diagnostic/{bank.course}", headers=headers)

    assert exam.status_code == 200, exam.text
    assert {i["id"] for i in exam.json()["items"]} == set(bank.ids[1:])
    assert diagnostic.status_code == 200, diagnostic.text
    assert {q["id"] for q in diagnostic.json()["questions"]} == set(bank.ids[1:])


def test_spec008_r_a_template_serves_a_reserved_item(repo, client, tmp_path, monkeypatch):
    """FR-035: the teacher's catalogue lists a reserved item, a template may hold it, and the
    student who starts the template gets it."""
    bank = LifeBank(tmp_path, monkeypatch, n=3)
    reserved = bank.ids[0]
    _reserve(repo, bank, reserved)
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, bank.course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, bank.course, group)
    teacher_headers = headers_for(repo, teacher)

    catalogue = client.get(f"/api/teacher/items?course_id={bank.course}", headers=teacher_headers)
    assert catalogue.status_code == 200, catalogue.text
    assert reserved in {i["id"] for i in catalogue.json()}

    created = client.post(
        "/api/teacher/exam-templates",
        headers=teacher_headers,
        json={"course_id": bank.course, "title": "R", "time_limit_min": 10, "item_ids": bank.ids},
    )
    assert created.status_code == 201, created.text
    template = created.json()["id"]
    edited = client.patch(
        f"/api/teacher/exam-templates/{template}",
        headers=teacher_headers,
        json={"item_ids": [reserved, bank.ids[1]]},
    )
    assert edited.status_code == 200, edited.text
    assigned = client.post(
        f"/api/teacher/exam-templates/{template}/assignments",
        headers=teacher_headers,
        json={"group_ids": [group], "starts_at": None, "ends_at": None},
    )
    assert assigned.status_code in (200, 201), assigned.text

    started = client.post(
        "/api/student/exam/start",
        headers=headers_for(repo, student),
        json={"course_id": bank.course, "template_id": template},
    )
    assert started.status_code == 200, started.text
    assert {i["id"] for i in started.json()["items"]} == {reserved, bank.ids[1]}
