"""
Spec 009 delivery I1 — who sees an identification (FR-013, US2-AS2, SC-003; task T017), on both
engines. An imported student's username is their identification, so any response that shows a
username to someone else would show it. Two imported students share a group, practise, play a
League match and appear in their teacher's views; every student and teacher GET endpoint, and the
teacher's exports, are walked: no response to a classmate or to the teacher holds an
identification.

[CHANGE] test: the base branch has no import. Invented identifications only (the repository is
public).
"""

import io
import uuid
import zipfile
from datetime import datetime, timedelta, timezone

from src.domain.identity import colombia_today
from tests.integration.conftest import (
    answer,
    headers_for,
    make_course,
    make_group,
    make_teacher,
    sql,
)

# Path parameters the walk fills; any other path is reached with these values or skipped.
_STUDENT_PATHS = [
    "/api/auth/me",
    "/api/student/stats",
    "/api/student/courses",
    "/api/student/blocks/{course_id}",
    "/api/student/pvp/history",
    "/api/student/history",
    "/api/student/activity",
    "/api/student/streak/{course_id}",
    "/api/student/group-ranking",
    "/api/student/achievements",
    "/api/student/procedures",
    "/api/student/exam/templates",
    "/api/student/exam/pending",
    "/api/student/exam/history",
    "/api/student/diagnostic/{course_id}",
    "/api/student/map/{course_id}",
    "/api/meta/ranks",
]
_TEACHER_PATHS = [
    "/api/auth/me",
    "/api/teacher/dashboard",
    "/api/teacher/groups",
    "/api/teacher/groups/{group_id}/invitations",
    "/api/teacher/procedures",
    "/api/teacher/procedures/copies",
    "/api/teacher/student/{student_id}",
    "/api/teacher/student/{student_id}/path/{course_id}",
    "/api/teacher/student/{student_id}/elo-history",
    "/api/teacher/student/{student_id}/katia-history",
    "/api/teacher/metrics",
    "/api/teacher/student/{student_id}/ranking",
    "/api/teacher/export/csv",
    "/api/teacher/export/xlsx",
    "/api/teacher/exam-templates",
    "/api/teacher/courses",
]


def _identification() -> str:
    return "66" + str(uuid.uuid4().int)[:8]


def _imported_pair(repo):
    """An admin's import of two students into one teacher's group, who then practise and play."""
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    course_id, items = make_course(repo, ["Fracciones"], items_per_topic=3)
    group = make_group(repo, teacher, course_id)
    first, second = _identification(), _identification()
    last_day = (colombia_today(datetime.now(timezone.utc)) + timedelta(days=30)).isoformat()
    _, record = repo.start_import(admin, uuid.uuid4().hex, 2)
    results = repo.import_student_chunk(
        record["import_id"],
        [
            {
                "row": number,
                "identification": identification,
                "display_name": name,
                "level": "semillero",
                "grade": 9,
                "group_id": group,
                "access_until": last_day,
                "recovery_email": None,
            }
            for number, identification, name in ((2, first, "Ana Pérez"), (3, second, "Luis Gómez"))
        ],
    )
    a, b = (r["user_id"] for r in results)
    for user_id, correct in ((a, True), (b, False)):
        for item_id in items["Fracciones"][:2]:
            answer(repo, user_id, item_id, correct=correct)
    match_id = repo.create_pvp_match(course_id, a, b, items["Fracciones"][:1])
    repo.finish_pvp_match(match_id, a, 1, 0, 8.0, -8.0, a, b)
    return {
        "teacher": teacher,
        "course_id": course_id,
        "group_id": group,
        "students": {a: first, b: second},
    }


def _texts(response) -> str:
    """A response's text; an `.xlsx` is opened, so its cells are read, not its compressed bytes."""
    body = response.content
    if body[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(body)) as book:
            return "".join(book.read(name).decode("utf-8", "replace") for name in book.namelist())
    return body.decode("utf-8", "replace")


def _walk(client, headers, paths, values):
    for path in paths:
        url = path.format(**values)
        response = client.get(url, headers=headers)
        assert response.status_code < 500, (url, response.status_code)
        yield url, response


def test_spec009_no_classmate_or_teacher_response_holds_an_identification(repo, client):
    setup = _imported_pair(repo)
    (a, first), (b, second) = setup["students"].items()

    for me, other_identification in ((a, second), (b, first)):
        reached = []
        for url, response in _walk(
            client,
            headers_for(repo, me),
            _STUDENT_PATHS,
            {"course_id": setup["course_id"]},
        ):
            reached.append(response.status_code)
            assert other_identification not in _texts(response), url
        assert reached.count(200) >= 10  # the walk really read the student's views
    seen_by_teacher = []
    for student_id in (a, b):
        for url, response in _walk(
            client,
            headers_for(repo, setup["teacher"]),
            _TEACHER_PATHS,
            {
                "course_id": setup["course_id"],
                "group_id": setup["group_id"],
                "student_id": student_id,
            },
        ):
            seen_by_teacher.append((url, response.status_code))
            text = _texts(response)
            assert first not in text and second not in text, url
    assert sum(1 for _, code in seen_by_teacher if code == 200) >= 20
    # The teacher's views do name the students — by their display names.
    dashboard = client.get("/api/teacher/dashboard", headers=headers_for(repo, setup["teacher"]))
    assert "Ana Pérez" in dashboard.text and "Luis Gómez" in dashboard.text
