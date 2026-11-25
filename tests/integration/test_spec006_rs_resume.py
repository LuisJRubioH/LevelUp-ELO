"""
Spec 006 delivery RS (US6; FR-025 … FR-027): resuming a started template.

A student who starts a template they started and have not submitted gets the same session — its
items in the same order and the seconds left — instead of a fresh clock; once its time ran out
unsubmitted, the attempt is used: a new start is refused, the template leaves the student's lists,
and the 24-hour sweep keeps that session. Standard exams start fresh. Both engines.
"""

from datetime import datetime, timedelta, timezone

import pytest

from tests.integration.conftest import sql
from tests.integration.test_spec006_x1_exams import _class, _sessions, _start, _submit


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _deadline_in(repo, session_id, seconds):
    """Moves a session's server deadline (which includes the 30-second grace) `seconds` from now."""
    from api.routers.student import EXAM_SUBMIT_GRACE_SECONDS

    at = datetime.now(timezone.utc) + timedelta(seconds=seconds + EXAM_SUBMIT_GRACE_SECONDS)
    sql(
        repo,
        "UPDATE active_exam_sessions SET expires_at = ? WHERE id = ?",
        (at.strftime("%Y-%m-%d %H:%M:%S"), session_id),
    )


def _expire(repo, session_id, when="2000-01-01 00:00:00"):
    sql(repo, "UPDATE active_exam_sessions SET expires_at = ? WHERE id = ?", (when, session_id))


def _listed(client, c):
    templates = client.get(
        f"/api/student/exam/templates?course_id={c['course']}", headers=c["headers"]
    )
    pending = client.get("/api/student/exam/pending", headers=c["headers"])
    assert templates.status_code == 200 and pending.status_code == 200
    return (
        [t["id"] for t in templates.json()],
        [p["template_id"] for p in pending.json()],
    )


def test_a_started_template_resumes_with_the_time_left(repo, client):
    """US6-AS1, FR-025: the same session, its items in order and the seconds left; one session;
    the submission is graded as usual."""
    c = _class(repo, client)
    first = _start(client, c["headers"], c["course"], c["template"])
    assert first.status_code == 200, first.text
    first = first.json()
    assert first.get("resumed") is False
    _deadline_in(repo, first["session_id"], 120)

    again = _start(client, c["headers"], c["course"], c["template"])

    assert again.status_code == 200, again.text
    body = again.json()
    assert body["session_id"] == first["session_id"]
    assert [i["id"] for i in body["items"]] == [i["id"] for i in first["items"]]
    assert 100 <= body["time_limit_seconds"] <= 120
    assert body["resumed"] is True
    assert _sessions(repo, c["student"]) == 1

    submitted = _submit(client, c["headers"], body)
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["total_questions"] == len(c["items"])


def test_resuming_does_not_need_the_window_open(repo, client):
    """US6-AS2, FR-025: a window that closed while the student was answering does not stop them
    from resuming before their time runs out."""
    c = _class(repo, client)
    first = _start(client, c["headers"], c["course"], c["template"]).json()
    sql(
        repo,
        "UPDATE exam_assignments SET ends_at = ? WHERE template_id = ?",
        ("2000-01-01 00:00:00", c["template"]),
    )

    again = _start(client, c["headers"], c["course"], c["template"])

    assert again.status_code == 200, again.text
    assert again.json()["session_id"] == first["session_id"]
    assert again.json()["resumed"] is True


def test_an_attempt_whose_time_ran_out_is_used(repo, client):
    """US6-AS3, FR-026: refused with 409 and a reason; gone from the exams and pending lists."""
    c = _class(repo, client)
    first = _start(client, c["headers"], c["course"], c["template"]).json()
    assert c["template"] in _listed(client, c)[0]
    _deadline_in(repo, first["session_id"], -5)

    again = _start(client, c["headers"], c["course"], c["template"])

    assert again.status_code == 409, again.text
    assert "tiempo" in again.json()["detail"].lower()
    assert _sessions(repo, c["student"]) == 1
    templates, pending = _listed(client, c)
    assert c["template"] not in templates
    assert c["template"] not in pending


def test_the_sweep_keeps_an_unsubmitted_template_attempt(repo, client):
    """US6-AS3, FR-027: a day past its deadline the unsubmitted template session stays, so the
    attempt stays used; a stale standard session still goes (FR-023)."""
    c = _class(repo, client)
    attempt = _start(client, c["headers"], c["course"], c["template"]).json()["session_id"]
    standard = _start(client, c["headers"], c["course"]).json()["session_id"]
    _expire(repo, attempt)
    _expire(repo, standard)

    # Any start runs the sweep (FR-023).
    assert _start(client, c["headers"], c["course"]).status_code == 200

    ids = [
        r[0]
        for r in sql(repo, "SELECT id FROM active_exam_sessions WHERE user_id = ?", (c["student"],))
    ]
    assert attempt in ids and standard not in ids
    assert _start(client, c["headers"], c["course"], c["template"]).status_code == 409
    assert c["template"] not in _listed(client, c)[1]


def test_standard_exams_start_fresh(repo, client):
    """US6-AS4: a standard exam is practice; each start is a new session."""
    c = _class(repo, client)
    one = _start(client, c["headers"], c["course"]).json()
    two = _start(client, c["headers"], c["course"]).json()

    assert one["session_id"] != two["session_id"]
    assert one["resumed"] is False and two["resumed"] is False
    assert _sessions(repo, c["student"]) == 2
