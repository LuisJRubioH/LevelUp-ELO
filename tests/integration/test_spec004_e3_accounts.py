"""
Spec 004, delivery E3 — students created one by one, and the last day of access, on both engines
(US6, US7, FR-040, FR-043 … FR-052).

[CHANGE] tests: the base branch has no student creation by the admin and no last day of access.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.identity import ACCESS_EXPIRED_MESSAGE, colombia_today
from tests.integration.conftest import (
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    set_rating,
    sql,
)


def _admin(repo) -> int:
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _today():
    return colombia_today(datetime.now(timezone.utc))


def _day(offset: int) -> str:
    return (_today() + timedelta(days=offset)).isoformat()


def _username() -> str:
    return "e3_" + uuid.uuid4().hex[:10]


def _users_named(repo, username) -> int:
    return sql(repo, "SELECT COUNT(*) FROM users WHERE username = ?", (username,))[0][0]


def _events(repo, user_id, action) -> list:
    return sql(
        repo,
        "SELECT actor_id FROM audit_account_events WHERE user_id = ? AND action = ?",
        (user_id, action),
    )


def _group_with_course(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    course_id, items = make_course(repo, ["Fracciones"], items_per_topic=2)
    return teacher, make_group(repo, teacher, course_id), course_id


def _expire(repo, user_id, last_day=None) -> None:
    sql(repo, "UPDATE users SET access_until = ? WHERE id = ?", (last_day or _day(-1), user_id))


def _login(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password})


# ── Repository ───────────────────────────────────────────────────────────────────────────────


def test_spec004_create_student_account_with_its_group_and_audit(repo):
    """FR-040, FR-044: the admin's student has its own username, a temporary password that must
    be changed, the display name, the group (and its course), level and grade, and optionally a
    last day; who created it is recorded."""
    admin = _admin(repo)
    _, group, course_id = _group_with_course(repo)
    username = _username()

    ok, message, user_id = repo.create_student_account(
        admin, username, "Temporal-1234", "  Ana   Pérez ", group, "semillero", "9", _day(30)
    )

    assert ok, message
    row = repo.get_user_by_id(user_id)
    assert row["role"] == "student" and row["group_id"] == group
    assert row["display_name"] == "Ana Pérez"
    assert row["must_change_password"] is True
    assert row["access_until"] == _day(30)
    assert repo.verify_user_password(user_id, "Temporal-1234")
    assert {e["id"] for e in repo.get_user_enrollments(user_id)} == {course_id}
    created_by = sql(repo, "SELECT created_by, grade FROM users WHERE id = ?", (user_id,))[0]
    assert tuple(created_by) == (admin, "9")
    assert [tuple(e) for e in _events(repo, user_id, "student_created")] == [(admin,)]


@pytest.mark.parametrize(
    "change",
    [
        {"actor": "teacher"},
        {"group": 987654321},
        {"username": "taken"},
        {"display_name": "Elver Galarga"},
        {"display_name": ""},
        {"level": "semillero", "grade": None},
        {"level": "colegio", "grade": "9"},
        {"level": "kinder"},
        {"access_until": "31/12/2026"},
        {"access_until": "past"},
    ],
)
def test_spec004_a_refused_creation_creates_nothing(repo, change):
    """US6-AS2 … AS4, FR-040, FR-043, FR-044: a non-admin, a group that does not exist, a
    username in use, a refused or missing name, a level and grade that do not match, or a last
    day that is not a date or has already passed: refused, and no account appears."""
    admin, teacher = _admin(repo), make_teacher(repo)
    _, group, _ = _group_with_course(repo)
    taken = sql(repo, "SELECT username FROM users WHERE id = ?", (make_student(repo),))[0][0]
    username = taken if change.get("username") == "taken" else _username()
    args = {
        "actor": teacher if change.get("actor") == "teacher" else admin,
        "group": change.get("group", group),
        "display_name": change.get("display_name", "Ana Pérez"),
        "level": change.get("level", "colegio"),
        "grade": change.get("grade"),
        "access_until": (
            _day(-1) if change.get("access_until") == "past" else change.get("access_until")
        ),
    }
    before = _users_named(repo, username)

    ok, message, user_id = repo.create_student_account(
        args["actor"], username, "Temporal-1234", args["display_name"], args["group"],
        args["level"], args["grade"], args["access_until"],
    )  # fmt: skip

    assert not ok and message and user_id is None
    assert _users_named(repo, username) == before


def test_spec004_set_access_until_extends_and_is_recorded(repo):
    """FR-046, FR-050: only an active admin sets, changes, extends or removes a student's or a
    teacher's last day; each change is recorded."""
    admin, teacher, student = _admin(repo), make_teacher(repo), make_student(repo)

    assert repo.set_access_until(admin, student, _day(-1))[0]
    assert repo.get_user_by_id(student)["access_until"] == _day(-1)
    assert repo.set_access_until(admin, student, _day(60))[0]
    assert repo.set_access_until(admin, teacher, _day(5))[0]
    assert repo.get_access_until_bulk([student, teacher, admin]) == {
        student: _day(60),
        teacher: _day(5),
        admin: None,
    }
    assert repo.set_access_until(admin, student, None)[0]
    assert repo.get_user_by_id(student)["access_until"] is None
    assert len(_events(repo, student, "access_until_changed")) == 3

    assert not repo.set_access_until(teacher, student, _day(1))[0]
    assert not repo.set_access_until(admin, admin, _day(1))[0]
    assert not repo.set_access_until(admin, student, "mañana")[0]
    assert repo.get_user_by_id(student)["access_until"] is None


def test_spec004_a_match_is_abandoned_once_and_moves_no_rating(repo):
    """FR-051, FR-052: an abandoned match closes once, without rating effects; a later normal
    close changes nothing, and an abandon after a normal close does nothing."""
    course_id, _ = make_course(repo, ["Fracciones"])
    a, b = make_student(repo), make_student(repo)
    for player in (a, b):
        set_rating(repo, player, course_id, "Fracciones", 1100.0)
    match = repo.create_pvp_match(course_id, a, b, ["i1"])

    assert repo.abandon_pvp_match(match) is True
    assert repo.abandon_pvp_match(match) is False
    closed = repo.finish_pvp_match(
        match_id=match, winner_id=a, score_p1=1, score_p2=0,
        elo_delta_p1=12.0, elo_delta_p2=-12.0, p1_id=a, p2_id=b,
    )  # fmt: skip
    assert closed is None
    status = sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (match,))[0][0]
    assert status == "abandoned"
    ratings = sql(
        repo,
        "SELECT current_elo FROM student_course_topic_elo WHERE user_id IN (?, ?)",
        (a, b),
    )
    assert sorted(r[0] for r in ratings) == [1100.0, 1100.0]

    other = repo.create_pvp_match(course_id, a, b, ["i1"])
    repo.finish_pvp_match(
        match_id=other, winner_id=None, score_p1=0, score_p2=0,
        elo_delta_p1=0.0, elo_delta_p2=0.0, p1_id=a, p2_id=b,
    )  # fmt: skip
    assert repo.abandon_pvp_match(other) is False


# ── API: creation (US6) ──────────────────────────────────────────────────────────────────────


def _create(client, repo, admin, **overrides):
    body = {
        "username": _username(),
        "display_name": "Ana Pérez",
        "group_id": overrides.pop("group_id"),
        "education_level": "colegio",
        **overrides,
    }
    return body, client.post("/api/admin/students", json=body, headers=headers_for(repo, admin))


def test_spec004_admin_creates_a_student_who_changes_the_password_first(repo, client):
    """US6-AS1, FR-040, FR-030: created with a temporary password shown once; at the first
    sign-in only the password change is allowed; the teacher sees the student by name."""
    admin = _admin(repo)
    teacher, group, _ = _group_with_course(repo)

    body, created = _create(client, repo, admin, group_id=group, access_until=_day(30))

    assert created.status_code == 201, created.text
    temporary = created.json()["temporary_password"]
    assert len(temporary) >= 12
    login = _login(client, body["username"], temporary)
    assert login.status_code == 200
    assert login.json()["must_change_password"] is True
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.get("/api/student/courses", headers=headers).status_code == 403
    dashboard = client.get("/api/teacher/dashboard", headers=headers_for(repo, teacher))
    assert "Ana Pérez" in {s["name"] for s in dashboard.json()["students"]}
    assert temporary not in str(sql(repo, "SELECT * FROM audit_account_events"))


@pytest.mark.parametrize(
    "overrides",
    [
        {"username": "a"},
        {"username": "con espacio"},
        {"display_name": "Mierda"},
        {"display_name": ""},
        {"group_id": 987654321},
        {"education_level": "semillero"},
        {"education_level": "colegio", "grade": "9"},
        {"access_until": "mañana"},
    ],
)
def test_spec004_a_refused_creation_answers_and_creates_nothing(repo, client, overrides):
    """US6-AS2, US6-AS3: a username or a name the rules refuse, a group that does not exist, a
    level and grade that do not match, a last day that is not a date — refused, nothing made."""
    admin = _admin(repo)
    _, group, _ = _group_with_course(repo)
    overrides = {"group_id": group, **overrides}  # a copy: the same dict serves both engines
    body, created = _create(client, repo, admin, **overrides)

    assert created.status_code in (400, 422)
    assert _users_named(repo, body["username"]) == 0


def test_spec004_a_username_in_use_is_refused(repo, client):
    """US6-AS4, FR-043."""
    admin = _admin(repo)
    _, group, _ = _group_with_course(repo)
    taken = sql(repo, "SELECT username FROM users WHERE id = ?", (make_student(repo),))[0][0]

    _, created = _create(client, repo, admin, group_id=group, username=taken)

    assert created.status_code == 400
    assert _users_named(repo, taken) == 1


def test_spec004_only_the_admin_creates_students(repo, client):
    """FR-040: the admin creates students; a teacher or a student is refused."""
    _, group, _ = _group_with_course(repo)
    for actor in (make_teacher(repo), make_student(repo)):
        sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (actor,))
        body, created = _create(client, repo, actor, group_id=group)
        assert created.status_code == 403
        assert _users_named(repo, body["username"]) == 0


def test_spec004_admin_creations_are_limited_per_minute(repo, client, monkeypatch):
    """US6-AS5, FR-045: beyond the per-admin limit (30 by default; 3 here) the rest of the minute
    is refused."""
    from api.config import settings

    monkeypatch.setattr(settings, "rate_limit_admin_creations", "3/minute")
    admin = _admin(repo)
    _, group, _ = _group_with_course(repo)

    statuses = [_create(client, repo, admin, group_id=group)[1].status_code for _ in range(4)]

    assert statuses == [201, 201, 201, 429]


# ── API: the last day (US7) ──────────────────────────────────────────────────────────────────


def test_spec004_an_expired_account_cannot_sign_in(repo, client):
    """US7-AS1, FR-047, FR-048 (N7): with the right password the owner's message; with a wrong
    one, the usual refusal; the last day itself still signs in."""
    student = make_student(repo)
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (student,))[0][0]

    _expire(repo, student, _day(0))
    assert _login(client, username, "password123").status_code == 200

    _expire(repo, student)
    right = _login(client, username, "password123")
    wrong = _login(client, username, "otra-cosa-123")
    assert right.status_code == 403
    assert right.json()["detail"] == ACCESS_EXPIRED_MESSAGE
    assert wrong.status_code == 401
    assert ACCESS_EXPIRED_MESSAGE not in wrong.text


def test_spec004_an_open_session_ends_when_the_account_expires(repo, client):
    """US7-AS2, FR-047: the next request, the renewal and a new persistent connection are
    refused."""
    from starlette.websockets import WebSocketDisconnect

    from api.dependencies import create_refresh_token

    from api.websocket.connections import EXPIRED_CODE

    student = make_student(repo)
    headers = headers_for(repo, student)
    token = headers["Authorization"].removeprefix("Bearer ")
    room = f"/api/ws/notifications/student_{student}"
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    with client.websocket_connect(room) as socket:
        socket.send_json({"token": token})
        assert socket.receive_json()["type"] == "connected"

    _expire(repo, student)

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 401 and me.json()["detail"] == ACCESS_EXPIRED_MESSAGE
    renewal = client.post(
        "/api/auth/refresh", json={"refresh_token": create_refresh_token(student, 0)}
    )
    assert renewal.status_code == 401 and renewal.json()["detail"] == ACCESS_EXPIRED_MESSAGE
    with client.websocket_connect(room) as socket:
        socket.send_json({"token": token})
        with pytest.raises(WebSocketDisconnect) as closed:
            socket.receive_json()
    assert closed.value.code == EXPIRED_CODE


def test_spec004_expiry_keeps_the_data_and_extending_restores_access(repo, client):
    """US7-AS3, US7-AS4, FR-049, FR-050: the account and its academic data are unchanged while
    expired; the admin extends the last day and the student signs in again; the change is
    recorded."""
    admin = _admin(repo)
    _, group, course_id = _group_with_course(repo)
    body, created = _create(client, repo, admin, group_id=group, access_until=_day(10))
    student = created.json()["user_id"]
    set_rating(repo, student, course_id, "Fracciones", 1234.0)
    repo.set_user_password(student, "propia-1234")
    owner_column = {
        "student_course_topic_elo": "user_id",
        "attempts": "user_id",
        "enrollments": "user_id",
        "procedure_submissions": "student_id",
    }

    def snapshot():
        return {
            table: sql(repo, f"SELECT * FROM {table} WHERE {column} = ?", (student,))
            for table, column in owner_column.items()
        }

    before = snapshot()
    _expire(repo, student)
    assert _login(client, body["username"], "propia-1234").status_code == 403
    assert snapshot() == before

    extended = client.put(
        f"/api/admin/users/{student}/access-until",
        json={"access_until": _day(90)},
        headers=headers_for(repo, admin),
    )
    assert extended.status_code == 200
    assert _login(client, body["username"], "propia-1234").status_code == 200
    assert snapshot() == before
    assert len(_events(repo, student, "access_until_changed")) == 1
    listed = client.get("/api/admin/users", headers=headers_for(repo, admin)).json()["users"]
    row = next(u for u in listed if u["id"] == student)
    assert row["access_until"] == _day(90) and row["access_expired"] is False


def test_spec004_only_the_admin_changes_a_last_day(repo, client):
    """FR-046: only an explicit action of the admin sets a last day; a teacher or a student is
    refused."""
    student, teacher = make_student(repo), make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    for actor in (teacher, student):
        r = client.put(
            f"/api/admin/users/{student}/access-until",
            json={"access_until": _day(-1)},
            headers=headers_for(repo, actor),
        )
        assert r.status_code == 403
    assert repo.get_user_by_id(student)["access_until"] is None


def test_spec004_an_account_without_a_last_day_keeps_working(repo, client):
    """US7-AS7, FR-047: existing accounts and accounts with their own credentials have none."""
    student = make_student(repo)
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (student,))[0][0]
    assert repo.get_user_by_id(student)["access_until"] is None
    assert _login(client, username, "password123").status_code == 200
    assert client.get("/api/auth/me", headers=headers_for(repo, student)).status_code == 200


# ── Persistent connections and PvP (US7-AS2, AS5, AS6) ───────────────────────────────────────


class _Socket:
    def __init__(self):
        self.sent, self.closed = [], None

    async def send_json(self, message):
        self.sent.append(message)

    async def close(self, code=1000, reason=""):
        self.closed = (code, reason)


def _live_match(repo, a, b, course_id):
    from api.websocket import pvp

    match_id = repo.create_pvp_match(course_id, a, b, ["i1"])
    match = pvp.ActiveMatch(
        match_id=match_id, course_id=course_id,
        p1=pvp.LobbySlot(user_id=a, name="uno", elo=1100.0, ws=_Socket()),
        p2=pvp.LobbySlot(user_id=b, name="dos", elo=1100.0, ws=_Socket()),
        items=[], correct={}, score={a: 1, b: 0},
        answered={a: set(), b: set()}, done={a: False, b: False},
    )  # fmt: skip
    pvp._matches[match_id] = match
    return match


def test_spec004_the_sweep_closes_expired_sockets_and_abandons_their_matches(repo):
    """US7-AS2, US7-AS5, FR-047, FR-051: an open socket of an expired account is closed; its PvP
    match ends as abandoned, neither rating moves, both players are told why; an account still
    in date keeps its socket."""
    from api.websocket import connections, expiry, pvp

    course_id, _ = make_course(repo, ["Fracciones"])
    a, b, c = make_student(repo), make_student(repo), make_student(repo)
    for player in (a, b):
        set_rating(repo, player, course_id, "Fracciones", 1100.0)
    match = _live_match(repo, a, b, course_id)
    socket_a, socket_c = _Socket(), _Socket()
    connections.register(a, socket_a)
    connections.register(c, socket_c)
    _expire(repo, a)
    try:
        expired = asyncio.run(expiry.sweep_expired_accounts(repo))
    finally:
        connections.unregister(c, socket_c)
        pvp._matches.pop(match.match_id, None)

    assert expired == [a]
    assert socket_a.closed[0] == expiry.EXPIRED_CODE
    assert socket_c.closed is None
    status = sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (match.match_id,))[0][0]
    assert status == "abandoned"
    ends = [m for ws in (match.p1.ws, match.p2.ws) for m in ws.sent if m["type"] == "game_end"]
    assert len(ends) == 2
    assert all(
        e["abandoned"] and e["elo_delta"] == 0 and e["reason"] == "account_expired" for e in ends
    )
    ratings = sql(
        repo, "SELECT current_elo FROM student_course_topic_elo WHERE user_id IN (?, ?)", (a, b)
    )
    assert sorted(r[0] for r in ratings) == [1100.0, 1100.0]


def test_spec004_expiry_and_normal_close_end_a_match_once(repo):
    """US7-AS6, FR-052: whichever comes first decides; the match ends once, in one state, with
    one effect, and each player gets one result."""
    from api.websocket import pvp

    course_id, _ = make_course(repo, ["Fracciones"])
    a, b = make_student(repo), make_student(repo)
    for player in (a, b):
        set_rating(repo, player, course_id, "Fracciones", 1100.0)
    match = _live_match(repo, a, b, course_id)

    async def race():
        await asyncio.gather(pvp._finish_match(match, repo), pvp.abandon_matches_of(a, repo))

    try:
        asyncio.run(race())
    finally:
        pvp._matches.pop(match.match_id, None)

    status = sql(repo, "SELECT status FROM pvp_matches WHERE id = ?", (match.match_id,))[0][0]
    assert status in ("finished", "abandoned")
    for ws in (match.p1.ws, match.p2.ws):
        assert len([m for m in ws.sent if m["type"] == "game_end"]) == 1
    ratings = sorted(
        r[0]
        for r in sql(
            repo, "SELECT current_elo FROM student_course_topic_elo WHERE user_id IN (?, ?)", (a, b)
        )
    )
    if status == "abandoned":
        assert ratings == [1100.0, 1100.0]
    else:
        assert ratings[0] < 1100.0 < ratings[1]
