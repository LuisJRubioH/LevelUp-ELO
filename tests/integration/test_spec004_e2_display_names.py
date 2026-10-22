"""
Spec 004, delivery E2 — display names on both engines (US3, FR-020 … FR-025, FR-033, SC-005).

Classmates and teachers see a student by display name, or by username while the account has none
(N5); no response addressed to a student or a teacher carries the username of a student who has a
display name. The admin sees both and changes any student's name; a student changes their own;
registration asks students for one. Every change is recorded.

[CHANGE] tests: the base branch has no display name.
"""

import json
import uuid

import pytest

from tests.integration.test_pvp_enrolment import live_api  # noqa: F401 (fixture)

from tests.integration.conftest import (
    answer,
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    sql,
)


def _admin(repo) -> int:
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _username(repo, user_id) -> str:
    return sql(repo, "SELECT username FROM users WHERE id = ?", (user_id,))[0][0]


def _display_name(repo, user_id):
    return sql(repo, "SELECT display_name FROM users WHERE id = ?", (user_id,))[0][0]


def _name(repo, user_id, name) -> None:
    sql(repo, "UPDATE users SET display_name = ? WHERE id = ?", (name, user_id))


def _join(repo, user_id, group_id) -> None:
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group_id, user_id))


def _name_events(repo, user_id) -> list:
    return sql(
        repo,
        "SELECT actor_id, action FROM audit_account_events WHERE user_id = ? AND action = ?",
        (user_id, "display_name_changed"),
    )


def _classroom(repo):
    """A teacher's group with a named student, an existing student without a name and a viewer."""
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    course_id, items = make_course(repo, ["Fracciones"], items_per_topic=2)
    group = make_group(repo, teacher, course_id)
    named, unnamed, viewer = make_student(repo), make_student(repo), make_student(repo)
    for student in (named, unnamed, viewer):
        _join(repo, student, group)
        enroll(repo, student, course_id, group)
    _name(repo, named, "Ana María Pérez")
    answer(repo, named, items["Fracciones"][0])  # so the exports hold a row of theirs
    return {
        "teacher": teacher,
        "group": group,
        "course_id": course_id,
        "named": named,
        "unnamed": unnamed,
        "viewer": viewer,
        "display": "Ana María Pérez",
    }


# ── Repository ───────────────────────────────────────────────────────────────────────────────


def test_spec004_register_user_keeps_a_normalised_display_name(repo):
    """FR-020: the name is stored trimmed with its spaces collapsed, apart from the username;
    an account registered without one keeps working (existing accounts)."""
    username = "e2n_" + uuid.uuid4().hex[:10]
    ok, msg = repo.register_user(
        username, "password123", "student", education_level="colegio", display_name="  Ana   Ruiz "
    )
    assert ok, msg
    user_id = sql(repo, "SELECT id FROM users WHERE username = ?", (username,))[0][0]

    assert repo.get_user_by_id(user_id)["display_name"] == "Ana Ruiz"
    assert repo.get_user_by_id(make_student(repo))["display_name"] is None


def test_spec004_set_display_name_rules_and_audit(repo):
    """FR-025, FR-033: the student changes their own, the admin any student's; a teacher, another
    student or a refused name changes nothing; a teacher account gets no display name (out of
    scope); each change is recorded — who, which account, when — without the name."""
    admin, teacher = _admin(repo), make_teacher(repo)
    student, other = make_student(repo), make_student(repo)

    assert repo.set_display_name(student, student, "Laura Gómez")[0]
    assert _display_name(repo, student) == "Laura Gómez"
    assert repo.set_display_name(admin, student, "  Laura   Gómez-Díaz ")[0]
    assert _display_name(repo, student) == "Laura Gómez-Díaz"
    assert [tuple(e) for e in _name_events(repo, student)] == [
        (student, "display_name_changed"),
        (admin, "display_name_changed"),
    ]

    for actor, target, name in [
        (teacher, student, "Otro Nombre"),
        (other, student, "Otro Nombre"),
        (student, student, "Puta"),
        (student, student, "A"),
        (admin, teacher, "Profe Ana"),
    ]:
        ok, message = repo.set_display_name(actor, target, name)
        assert not ok and message
    assert _display_name(repo, student) == "Laura Gómez-Díaz"
    assert _display_name(repo, teacher) is None
    assert len(_name_events(repo, student)) == 2
    detail = sql(repo, "SELECT detail FROM audit_account_events WHERE user_id = ?", (student,))
    assert all("Laura" not in (d[0] or "") for d in detail)


def test_spec004_lists_carry_the_public_name(repo):
    """FR-021 … FR-023 (N5): the rows behind rankings, PvP history and the teacher's dashboard
    carry `name` — the display name, else the username."""
    room = _classroom(repo)
    participants = {
        p["user_id"]: p["name"]
        for p in repo.get_ranking_participants("group", group_id=room["group"])
    }
    assert participants[room["named"]] == room["display"]
    assert participants[room["unnamed"]] == _username(repo, room["unnamed"])

    stats = {s["user_id"]: s for s in repo.get_teacher_dashboard_stats(room["teacher"])}
    assert stats[room["named"]]["name"] == room["display"]
    assert stats[room["unnamed"]]["name"] == _username(repo, room["unnamed"])

    match = repo.create_pvp_match(room["course_id"], room["viewer"], room["named"], ["i1"])
    repo.finish_pvp_match(
        match_id=match, winner_id=None, score_p1=0, score_p2=0,
        elo_delta_p1=0.0, elo_delta_p2=0.0, p1_id=room["viewer"], p2_id=room["named"],
    )  # fmt: skip
    assert repo.get_pvp_history(room["viewer"])[0]["opponent"] == room["display"]


# ── API: what classmates and teachers see (SC-005) ───────────────────────────────────────────


def test_spec004_group_ranking_shows_classmates_by_name(repo, client):
    """US3-AS1, US3-AS3, FR-021, FR-022: each classmate by display name, an existing account
    without one by its username; no username of a classmate who has a display name."""
    room = _classroom(repo)
    r = client.get("/api/student/group-ranking", headers=headers_for(repo, room["viewer"]))

    assert r.status_code == 200
    names = {e["user_id"]: e["name"] for e in r.json()["ranking"]}
    assert names[room["named"]] == room["display"]
    assert names[room["unnamed"]] == _username(repo, room["unnamed"])
    assert _username(repo, room["named"]) not in r.text
    assert all("username" not in e for e in r.json()["ranking"])


def test_spec004_pvp_history_shows_the_rival_by_name(repo, client):
    """US3-AS2, FR-021: the rival of a finished match appears by display name."""
    room = _classroom(repo)
    match = repo.create_pvp_match(room["course_id"], room["viewer"], room["named"], ["i1"])
    repo.finish_pvp_match(
        match_id=match, winner_id=room["viewer"], score_p1=1, score_p2=0,
        elo_delta_p1=0.0, elo_delta_p2=0.0, p1_id=room["viewer"], p2_id=room["named"],
    )  # fmt: skip

    r = client.get("/api/student/pvp/history", headers=headers_for(repo, room["viewer"]))

    assert r.status_code == 200
    assert r.json()["matches"][0]["opponent"] == room["display"]
    assert _username(repo, room["named"]) not in r.text


def test_spec004_teacher_views_show_name_and_group(repo, client):
    """US3-AS4, FR-023: dashboard, procedures, a student's group ranking and the exports show the
    display name (or the username of FR-022) and group, and no username of a named student."""
    room = _classroom(repo)
    hidden = _username(repo, room["named"])
    # A file nobody sent before: PostgreSQL keeps earlier runs' files, and another student's file
    # is graded at once as a copy (spec 001 FR-024i), which would empty the queue below.
    file_hash = "e2h-" + uuid.uuid4().hex
    repo.save_procedure_submission(
        room["named"], "item-e2", "c", b"\x89PNG", "image/png", file_hash
    )
    headers = headers_for(repo, room["teacher"])

    dashboard = client.get("/api/teacher/dashboard", headers=headers)
    assert dashboard.status_code == 200
    rows = {s["user_id"]: s for s in dashboard.json()["students"]}
    assert rows[room["named"]]["name"] == room["display"]
    assert rows[room["named"]]["group_name"]
    assert rows[room["unnamed"]]["name"] == _username(repo, room["unnamed"])
    assert all("username" not in s for s in dashboard.json()["students"])

    procedures = client.get("/api/teacher/procedures", headers=headers)
    assert procedures.status_code == 200
    assert [p["student_name"] for p in procedures.json()] == [room["display"]]

    ranking = client.get(f"/api/teacher/student/{room['viewer']}/ranking", headers=headers)
    assert {e["name"] for e in ranking.json()["ranking"]} >= {room["display"]}

    csv_export = client.get("/api/teacher/export/csv", headers=headers)
    assert csv_export.status_code == 200
    for response in (dashboard, procedures, ranking, csv_export):
        assert hidden not in response.text


def test_spec004_admin_sees_username_and_display_name(repo, client):
    """US3-AS5, FR-024: the admin's list carries both, to find and correct a name."""
    room = _classroom(repo)
    r = client.get("/api/admin/users", headers=headers_for(repo, _admin(repo)))

    assert r.status_code == 200
    row = next(u for u in r.json()["users"] if u["id"] == room["named"])
    assert row["username"] == _username(repo, room["named"])
    assert row["display_name"] == room["display"]


# ── API: who changes a name ──────────────────────────────────────────────────────────────────


def test_spec004_admin_changes_a_students_name(repo, client):
    """US3-AS6, FR-025, FR-033: the admin's change applies and is recorded; a teacher or another
    student is refused and nothing changes; a teacher account has no display name."""
    admin, teacher = _admin(repo), make_teacher(repo)
    student, other = make_student(repo), make_student(repo)
    url = f"/api/admin/users/{student}/display-name"

    r = client.put(url, json={"display_name": "Camila Ríos"}, headers=headers_for(repo, admin))
    assert r.status_code == 200
    assert r.json()["display_name"] == "Camila Ríos"
    assert _display_name(repo, student) == "Camila Ríos"
    assert [tuple(e) for e in _name_events(repo, student)] == [(admin, "display_name_changed")]

    for actor in (teacher, other):
        refused = client.put(url, json={"display_name": "X Y"}, headers=headers_for(repo, actor))
        assert refused.status_code == 403
    on_teacher = client.put(
        f"/api/admin/users/{teacher}/display-name",
        json={"display_name": "Profe Ana"},
        headers=headers_for(repo, admin),
    )
    assert on_teacher.status_code == 400
    assert _display_name(repo, student) == "Camila Ríos"
    assert _display_name(repo, teacher) is None


def test_spec004_student_changes_their_own_name(repo, client):
    """US3-AS7, FR-025: an allowed name is saved and recorded; a refused one changes nothing and
    the message does not repeat it; a teacher has no display name to change."""
    student, teacher = make_student(repo), make_teacher(repo)
    headers = headers_for(repo, student)

    ok = client.put(
        "/api/student/display-name", json={"display_name": " Sofía  Vélez "}, headers=headers
    )
    assert ok.status_code == 200
    assert ok.json()["display_name"] == "Sofía Vélez"
    assert client.get("/api/auth/me", headers=headers).json()["display_name"] == "Sofía Vélez"
    assert [tuple(e) for e in _name_events(repo, student)] == [(student, "display_name_changed")]

    for refused_name in ("Elver Galarga", "Sofía2", "S"):
        refused = client.put(
            "/api/student/display-name", json={"display_name": refused_name}, headers=headers
        )
        assert refused.status_code == 400
        if len(refused_name) > 2:  # the message never repeats the name
            assert refused_name.lower() not in refused.text.lower()
    assert _display_name(repo, student) == "Sofía Vélez"
    assert len(_name_events(repo, student)) == 1

    as_teacher = client.put(
        "/api/student/display-name",
        json={"display_name": "Profe Ana"},
        headers=headers_for(repo, teacher),
    )
    assert as_teacher.status_code == 403


@pytest.fixture
def open_registration(monkeypatch):
    from api.config import settings

    monkeypatch.setattr(settings, "public_registration_enabled", True)


def test_spec004_registration_asks_students_for_a_name(repo, client, open_registration):
    """US3-AS8, FR-020: with registration open, a student needs an allowed display name; a
    teacher registers as before (no display name is decided for teachers)."""

    def register(**extra):
        body = {"username": "e2r_" + uuid.uuid4().hex[:10], "password": "password123"}
        return body["username"], client.post("/api/auth/register", json={**body, **extra})

    _, missing = register(role="student", education_level="colegio")
    _, refused = register(role="student", education_level="colegio", display_name="Mierda")
    username, ok = register(role="student", education_level="colegio", display_name="Tomás Ruiz")
    _, teacher = register(role="teacher")

    assert missing.status_code == 400
    assert refused.status_code == 400
    assert ok.status_code == 201
    assert teacher.status_code == 201
    stored = sql(repo, "SELECT display_name FROM users WHERE username = ?", (username,))
    assert stored[0][0] == "Tomás Ruiz"


def test_spec004_pvp_rival_is_named_in_the_match(repo, live_api):
    """US3-AS2, FR-021: in a live match each player sees the other by display name — or by
    username while they have none — and no message carries the username of a named rival."""
    from websockets.sync.client import connect

    from tests.integration.test_pvp_enrolment import _course, _token, _until

    course_id = _course(repo)
    named, unnamed = make_student(repo), make_student(repo)
    for student in (named, unnamed):
        enroll(repo, student, course_id)
    _name(repo, named, "Laura Gómez")
    url = f"{live_api}/api/ws/pvp/{course_id}"

    with connect(url) as waiting, connect(url) as joining:
        waiting.send(json.dumps({"token": _token(repo, named)}))
        _until(waiting, "waiting")
        joining.send(json.dumps({"token": _token(repo, unnamed)}))
        starts = {
            who: _until(socket, "game_start")
            for who, socket in (("named", waiting), ("unnamed", joining))
        }

    assert starts["unnamed"]["opponent"]["name"] == "Laura Gómez"
    assert starts["named"]["opponent"]["name"] == _username(repo, unnamed)
    assert _username(repo, named) not in json.dumps(starts["unnamed"])
