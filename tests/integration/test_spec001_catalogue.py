"""
Spec 001, follow-up F-1 (FR-028k, FR-028l, FR-028m, FR-028o, User Story 7; tasks T086–T089,
T098): the catalogue by level and grade, registration, enrolment and invitations. Both engines,
on the real course catalogue the bootstrap loads from items/bank.
"""

import uuid

import pytest

from src.application.services.rating_read_service import RatingReadService
from tests.integration.conftest import (
    enroll,
    headers_for,
    make_group,
    make_student,
    make_teacher,
    set_rating,
    sql,
)

GRADES = ["6", "7", "8", "9", "10", "11"]
# Other tests on the shared PostgreSQL database add courses such as spec001_course_…_semillero_6,
# so a catalogue is checked as: the six real courses of the grade, and nothing of another grade.
SUBJECTS = ["algebra", "aritmetica", "conteo_combinatoria", "geometria", "logica", "probabilidad"]
COLEGIO_COURSE = "algebra_basica"
UNIVERSIDAD_COURSE = "calculo_diferencial"


def _semillero(grade):
    return sorted(f"{subject}_semillero_{grade}" for subject in SUBJECTS)


def _gradeless_semillero(repo):
    """An account created before the rule: semillero with no grade."""
    student = make_student(repo, "semillero", "6")
    sql(repo, "UPDATE users SET grade = NULL WHERE id = ?", (student,))
    return student


def _approved_teacher_group(repo, course_id):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group_id = make_group(repo, teacher, course_id)
    return group_id, repo.generate_group_invite_code(group_id)


def _enrolled(repo, user_id):
    return sorted(e["id"] for e in repo.get_user_enrollments(user_id))


def _user(repo, user_id):
    row = sql(repo, "SELECT education_level, grade FROM users WHERE id = ?", (user_id,))[0]
    return row[0], row[1]


# ── FR-028k: the catalogue ───────────────────────────────────────────────────


def test_spec001_semillero_catalogue_by_grade(repo):
    """US7-AS1, US7-AS5 (repository): grade g → exactly the six `*_semillero_g` courses; no grade
    → none; the other levels keep their block."""
    for grade in GRADES:
        courses = repo.get_available_courses_by_level("semillero", grade=grade)
        ids = {c["id"] for c in courses}
        assert set(_semillero(grade)) <= ids, grade
        assert all(i.endswith(f"_semillero_{grade}") for i in ids), grade
        assert {c["block"] for c in courses} == {"Semillero"}
    assert repo.get_available_courses_by_level("semillero", grade=None) == []
    colegio = {c["id"] for c in repo.get_available_courses_by_level("colegio")}
    assert COLEGIO_COURSE in colegio and UNIVERSIDAD_COURSE not in colegio
    assert {c["block"] for c in repo.get_available_courses_by_level("universidad")} == {
        "Universidad"
    }


def test_spec001_current_courses_are_the_catalogue(repo):
    """US7-AS1: the courses that count as current are the enrolled courses of the catalogue —
    the grade-7 courses for a grade-7 student, none for a grade-less one."""
    student = make_student(repo, "semillero", "7")
    for course_id in _semillero("7")[:2] + _semillero("8")[:1]:
        enroll(repo, student, course_id)
    assert sorted(repo.get_current_context_course_ids(student)) == _semillero("7")[:2]

    gradeless = _gradeless_semillero(repo)
    enroll(repo, gradeless, _semillero("6")[0])
    assert repo.get_current_context_course_ids(gradeless) == []


# ── FR-028m: registration and /enroll ────────────────────────────────────────


@pytest.mark.parametrize("grade", [None, "", "5", "12"])
def test_spec001_register_user_rejects_semillero_without_a_valid_grade(repo, grade):
    """US7-AS2 (storage): rejected on both engines and no account is created."""
    username = "f1_reg_" + uuid.uuid4().hex[:10]
    ok, _ = repo.register_user(
        username, "password123", "student", education_level="semillero", grade=grade
    )
    assert ok is False
    assert sql(repo, "SELECT COUNT(*) FROM users WHERE username = ?", (username,))[0][0] == 0


@pytest.mark.parametrize("grade", [None, "5", "12"])
def test_spec001_api_registration_rejects_semillero_without_a_valid_grade(repo, client, grade):
    """US7-AS2 (API): no grade, or one outside 6–11, is rejected and creates no account."""
    username = "f1_api_" + uuid.uuid4().hex[:10]
    body = {"username": username, "password": "password123", "education_level": "semillero"}
    if grade is not None:
        body["grade"] = grade
    response = client.post("/api/auth/register", json=body)
    assert response.status_code in (400, 422), response.text
    assert sql(repo, "SELECT COUNT(*) FROM users WHERE username = ?", (username,))[0][0] == 0


def test_spec001_courses_of_a_grade_7_student(repo, client):
    """US7-AS1 (API): `GET /api/student/courses` → the six grade-7 courses, all in the
    catalogue."""
    student = make_student(repo, "semillero", "7")
    body = client.get("/api/student/courses", headers=headers_for(repo, student)).json()
    ids = {c["id"] for c in body}
    assert set(_semillero("7")) <= ids
    assert all(i.endswith("_semillero_7") for i in ids)
    assert all(c["in_catalogue"] and not c["enrolled"] for c in body)


@pytest.mark.parametrize(
    "level, grade, outside, inside",
    [
        ("colegio", None, UNIVERSIDAD_COURSE, COLEGIO_COURSE),
        ("semillero", "6", "algebra_semillero_7", "algebra_semillero_6"),
    ],
)
def test_spec001_enrol_only_in_the_catalogue(repo, client, level, grade, outside, inside):
    """US7-AS3: outside the catalogue → 403, nothing enrolled; inside → 201."""
    student = make_student(repo, level, grade)
    headers = headers_for(repo, student)

    refused = client.post("/api/student/enroll", headers=headers, json={"course_id": outside})
    assert refused.status_code == 403, refused.text
    assert _enrolled(repo, student) == []

    accepted = client.post("/api/student/enroll", headers=headers, json={"course_id": inside})
    assert accepted.status_code == 201, accepted.text
    assert _enrolled(repo, student) == [inside]


# ── FR-028l: invitations ─────────────────────────────────────────────────────


def test_spec001_invitation_crosses_levels_without_changing_them(repo, client):
    """US7-AS4: a grade-6 student joins a colegio group by its code: enrolled and able to
    practise; level and grade unchanged; not current; overall rating unchanged."""
    student = make_student(repo, "semillero", "6")
    own = _semillero("6")[0]
    enroll(repo, student, own)
    set_rating(repo, student, own, "Fracciones", 1100.0)
    ratings = RatingReadService(repo)
    before = ratings.ratings_view(student)["overall"]
    group_id, code = _approved_teacher_group(repo, COLEGIO_COURSE)
    headers = headers_for(repo, student)

    response = client.post(
        "/api/student/enroll-by-code", headers=headers, json={"invite_code": code}
    )

    assert response.status_code == 201, response.text
    assert response.json()["course_id"] == COLEGIO_COURSE
    assert _enrolled(repo, student) == sorted([own, COLEGIO_COURSE])
    assert _user(repo, student) == ("semillero", "6")
    assert COLEGIO_COURSE not in repo.get_current_context_course_ids(student)
    assert ratings.ratings_view(student)["overall"] == before == 1100.0
    practice = client.post(
        "/api/student/next-question", headers=headers, json={"course_id": COLEGIO_COURSE}
    )
    assert practice.status_code == 200 and practice.json()["item"], practice.text


def test_spec001_gradeless_semillero_keeps_enrolments_but_no_new_invitation(repo, client):
    """US7-AS5: no grade → a new invitation is refused; the rating reads "pending diagnostic";
    the courses already enrolled stay open for practice."""
    student = _gradeless_semillero(repo)
    earlier = _semillero("6")[0]
    enroll(repo, student, earlier)
    _, code = _approved_teacher_group(repo, COLEGIO_COURSE)
    headers = headers_for(repo, student)

    refused = client.post(
        "/api/student/enroll-by-code", headers=headers, json={"invite_code": code}
    )

    assert refused.status_code == 403, refused.text
    assert _enrolled(repo, student) == [earlier]
    assert _user(repo, student) == ("semillero", None)
    assert RatingReadService(repo).ratings_view(student)["overall_status"] == "pending_diagnostic"
    practice = client.post(
        "/api/student/next-question", headers=headers, json={"course_id": earlier}
    )
    assert practice.status_code == 200 and practice.json()["item"], practice.text


# ── FR-028l, FR-028o: the course list ────────────────────────────────────────


def test_spec001_course_list_marks_invited_courses(repo, client):
    """US7-AS6: an invited universidad course is listed as enrolled and outside the catalogue;
    the catalogue keeps `in_catalogue: true`."""
    student = make_student(repo, "colegio")
    group_id, _ = _approved_teacher_group(repo, UNIVERSIDAD_COURSE)
    enroll(repo, student, UNIVERSIDAD_COURSE, group_id)
    enroll(repo, student, COLEGIO_COURSE)

    body = client.get("/api/student/courses", headers=headers_for(repo, student)).json()
    by_id = {c["id"]: c for c in body}

    catalogue = {c["id"] for c in repo.get_available_courses_by_level("colegio")}
    assert set(by_id) == catalogue | {UNIVERSIDAD_COURSE}
    invited = by_id[UNIVERSIDAD_COURSE]
    assert (invited["enrolled"], invited["in_catalogue"], invited["group_id"]) == (
        True,
        False,
        group_id,
    )
    assert by_id[COLEGIO_COURSE]["enrolled"] and by_id[COLEGIO_COURSE]["in_catalogue"]
    assert all(c["in_catalogue"] for i, c in by_id.items() if i != UNIVERSIDAD_COURSE)


def test_spec001_gradeless_course_list_is_its_enrolments(repo, client):
    """US7-AS5, FR-028o: a grade-less semillero student is offered no catalogue course; the
    courses they are enrolled in are still listed."""
    student = _gradeless_semillero(repo)
    earlier = _semillero("6")[0]
    enroll(repo, student, earlier)

    body = client.get("/api/student/courses", headers=headers_for(repo, student)).json()

    assert [(c["id"], c["enrolled"], c["in_catalogue"]) for c in body] == [(earlier, True, False)]
