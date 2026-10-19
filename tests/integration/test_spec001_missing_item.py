"""
Spec 001 FR-024m (US9-AS15), amended 2026-10-19: a procedure whose exercise is not in the bank —
removed after the upload, or a free exercise id such as a workshop's — is still graded, applies
nothing to any rating, and the procedure records what was applied: 0, not marked as applied,
never the computed delta. Both engines.
"""

import io
import uuid

import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    set_rating,
    sql,
)

TOPIC = "fr024m"


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _png() -> bytes:
    meta = PngInfo()
    meta.add_text("fr024m", uuid.uuid4().hex)
    output = io.BytesIO()
    Image.new("RGB", (2, 2), (10, 120, 60)).save(output, format="PNG", pnginfo=meta)
    return output.getvalue()


def _classroom(repo):
    course, items = make_course(repo, [TOPIC], items_per_topic=2)
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    group = make_group(repo, teacher, course)
    student = make_student(repo)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    enroll(repo, student, course, group)
    set_rating(repo, student, course, TOPIC, 1000.0)
    return {"teacher": teacher, "course": course, "item": items[TOPIC][0], "student": student}


def _upload(client, repo, student, item_id):
    response = client.post(
        "/api/student/procedure",
        headers=headers_for(repo, student),
        data={"item_id": item_id},
        files={"file": ("work.png", _png(), "image/png")},
    )
    assert response.status_code in (200, 201), response.text
    return response.json()["submission_id"]


def _grade(client, repo, teacher, submission_id):
    return client.post(
        "/api/teacher/procedures/grade",
        headers=headers_for(repo, teacher),
        json={"submission_id": submission_id, "teacher_score": 90, "review_round": 1},
    )


def _record(repo, submission_id):
    return sql(
        repo,
        "SELECT status, teacher_score, elo_applied, elo_delta FROM procedure_submissions"
        " WHERE id = ?",
        (submission_id,),
    )[0]


@pytest.mark.parametrize("case", ["removed", "free_id"])
def test_spec001_an_exercise_not_in_the_bank_records_what_was_applied(repo, client, case):
    """US9-AS15, FR-024m: graded; 0 applied, recorded as 0 and not as applied."""
    c = _classroom(repo)
    item_id = c["item"] if case == "removed" else f"taller_{uuid.uuid4().hex[:6]}_p5"
    submission = _upload(client, repo, c["student"], item_id)
    if case == "removed":
        sql(repo, "DELETE FROM items WHERE id = ?", (item_id,))

    response = _grade(client, repo, c["teacher"], submission)

    assert response.status_code == 200, response.text
    assert response.json()["elo_delta"] == 0
    status, grade, elo_applied, elo_delta = _record(repo, submission)
    assert (status, float(grade)) == ("VALIDATED_BY_TEACHER", 90.0)
    assert (int(elo_applied or 0), float(elo_delta or 0)) == (0, 0.0)
    assert rating_of(repo, c["student"], c["course"], TOPIC) == pytest.approx(1000.0)
    history = sql(
        repo, "SELECT grade, applied FROM procedure_gradings WHERE submission_id = ?", (submission,)
    )
    assert [(float(g), float(a)) for g, a in history] == [(90.0, 0.0)]


def test_spec001_an_exercise_in_the_bank_is_recorded_as_applied(repo, client):
    """FR-024m leaves the ordinary case as it was: applied and marked so."""
    c = _classroom(repo)
    submission = _upload(client, repo, c["student"], c["item"])

    response = _grade(client, repo, c["teacher"], submission)

    assert response.status_code == 200, response.text
    _, _, elo_applied, elo_delta = _record(repo, submission)
    assert (int(elo_applied), float(elo_delta)) == (1, 8.0)  # (90 − 50) × 0.2
    assert rating_of(repo, c["student"], c["course"], TOPIC) == pytest.approx(1008.0)
