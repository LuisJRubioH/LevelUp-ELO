"""
Spec 001, delivery INV (User Story 10; FR-028l, FR-028p … FR-028u): single-use invitations. The
teacher generates them for their own group; the first student who redeems one consumes it and joins
the group's course; nobody else can use it afterwards; an unused one expires or can be revoked; the
group's reusable code of the old system no longer enrols anyone. Both engines, through the API
where a screen reaches them.

[CHANGE] tests: the base branch has no single-use invitation.
"""

import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.domain.invitations import new_token
from tests.integration.conftest import (
    enroll,
    headers_for,
    is_postgres,
    make_group,
    make_student,
    make_teacher,
    sql,
)

COLEGIO_COURSE = "algebra_basica"
UNIVERSIDAD_COURSE = "calculo_diferencial"
TTL = 30
SHOWN = re.compile(r"[A-HJKMNP-Z2-9]{5}-[A-HJKMNP-Z2-9]{5}")

INVALID = "Código de invitación inválido."
USED = "Este código ya fue usado. Pide uno nuevo a tu docente."
EXPIRED = "Este código venció. Pide uno nuevo a tu docente."
MEMBER = "Ya estás en este grupo."


# ── Helpers ──────────────────────────────────────────────────────────────────


def _approved_teacher(repo):
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _group(repo, course_id=COLEGIO_COURSE):
    teacher = _approved_teacher(repo)
    return teacher, make_group(repo, teacher, course_id)


def _tokens(repo, teacher, group, count=1):
    return repo.create_group_invitations(teacher, group, count, TTL)


def _redeem(client, repo, student, code):
    return client.post(
        "/api/student/enroll-by-code",
        headers=headers_for(repo, student),
        json={"invite_code": code},
    )


def _listed(client, repo, teacher, group):
    response = client.get(
        f"/api/teacher/groups/{group}/invitations", headers=headers_for(repo, teacher)
    )
    assert response.status_code == 200, response.text
    return response.json()


def _used_by(repo, token):
    return sql(repo, "SELECT used_by FROM group_invitations WHERE token = ?", (token,))[0][0]


def _membership(repo, student, course_id):
    """(the enrolment's group, the student's group); the enrolment's is None if not enrolled."""
    enrolment = sql(
        repo,
        "SELECT group_id FROM enrollments WHERE user_id = ? AND course_id = ?",
        (student, course_id),
    )
    user_group = sql(repo, "SELECT group_id FROM users WHERE id = ?", (student,))[0][0]
    return (enrolment[0][0] if enrolment else "not enrolled", user_group)


def _lifetimes_in_days(repo, group):
    if is_postgres(repo):
        statement = (
            "SELECT EXTRACT(EPOCH FROM expires_at - created_at) / 86400.0"
            " FROM group_invitations WHERE group_id = ?"
        )
    else:
        statement = (
            "SELECT julianday(expires_at) - julianday(created_at)"
            " FROM group_invitations WHERE group_id = ?"
        )
    return [round(float(row[0]), 3) for row in sql(repo, statement, (group,))]


def _admin(repo):
    rows = sql(
        repo,
        "INSERT INTO users (username, password_hash, role, approved, active)"
        " VALUES (?, 'unused', 'admin', 1, 1) RETURNING id",
        (f"spec001_admin_{new_token()}",),
    )
    return rows[0][0]


# ── FR-028p: the teacher generates them ──────────────────────────────────────


def test_spec001_teacher_generates_single_use_invitations(repo, client, monkeypatch):
    """US10-AS1, FR-028p: three different unused tokens shown as XXXXX-XXXXX, each expiring the
    configured number of days after its creation (30 unless INVITATION_TTL_DAYS says otherwise)."""
    from api.config import settings

    assert settings.invitation_ttl_days == 30
    teacher, group = _group(repo)
    headers = headers_for(repo, teacher)

    response = client.post(
        f"/api/teacher/groups/{group}/invitations", headers=headers, json={"count": 3}
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ttl_days"] == 30
    tokens = body["tokens"]
    assert len(tokens) == len(set(tokens)) == 3
    assert all(SHOWN.fullmatch(t) for t in tokens), tokens
    listed = _listed(client, repo, teacher, group)
    assert listed["ttl_days"] == 30
    assert sorted(i["token"] for i in listed["invitations"]) == sorted(tokens)
    assert {(i["status"], i["used_by_name"], i["used_at"]) for i in listed["invitations"]} == {
        ("unused", None, None)
    }
    assert all(i["expires_at"][:10] > i["created_at"][:10] for i in listed["invitations"])
    assert _lifetimes_in_days(repo, group) == [30.0, 30.0, 30.0]

    monkeypatch.setattr(settings, "invitation_ttl_days", 7)
    other, other_group = _group(repo)
    shorter = client.post(
        f"/api/teacher/groups/{other_group}/invitations",
        headers=headers_for(repo, other),
        json={"count": 1},
    )
    assert shorter.status_code == 201 and shorter.json()["ttl_days"] == 7
    assert _lifetimes_in_days(repo, other_group) == [7.0]


def test_spec001_one_to_fifty_invitations_at_once(repo, client):
    """FR-028p: the count goes from 1 to 50, at the API and in the repository."""
    teacher, group = _group(repo)
    headers = headers_for(repo, teacher)
    for count in (0, 51, -1):
        refused = client.post(
            f"/api/teacher/groups/{group}/invitations", headers=headers, json={"count": count}
        )
        assert refused.status_code == 422, refused.text
        with pytest.raises(ValueError):
            repo.create_group_invitations(teacher, group, count, TTL)
    accepted = client.post(
        f"/api/teacher/groups/{group}/invitations", headers=headers, json={"count": 50}
    )
    assert accepted.status_code == 201, accepted.text
    assert len(set(accepted.json()["tokens"])) == 50
    assert len(_listed(client, repo, teacher, group)["invitations"]) == 50


def test_spec001_a_token_collision_is_drawn_again(repo, monkeypatch):
    """FR-028p: tokens are unique across all invitations; a drawn token that already exists is
    replaced by a new draw."""
    teacher, group = _group(repo)
    first, second = new_token(), new_token()
    draws = iter([first, first, second])
    module = sys.modules[type(repo).__module__]
    monkeypatch.setattr(module, "new_token", lambda: next(draws))

    assert _tokens(repo, teacher, group) == [first]
    assert _tokens(repo, teacher, group) == [second]
    assert sorted(i["token"] for i in repo.get_group_invitations(teacher, group)) == sorted(
        [first, second]
    )


# ── FR-028q, FR-028l: redeeming ──────────────────────────────────────────────


def test_spec001_redeeming_an_invitation_enrols_the_student(repo, client):
    """US10-AS2, FR-028q, FR-028l: typed in lower case, with spaces and without the hyphen, the
    invitation enrols a colegio student in the group's universidad course with the group; their
    level does not change and the course stays outside their catalogue; the teacher sees it used
    by the student's display name."""
    teacher, group = _group(repo, UNIVERSIDAD_COURSE)
    (token,) = _tokens(repo, teacher, group)
    student = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET display_name = ? WHERE id = ?", ("Ana Pérez", student))

    response = _redeem(client, repo, student, f"  {token[:5].lower()} {token[5:].lower()} ")

    assert response.status_code == 201, response.text
    assert response.json()["course_id"] == UNIVERSIDAD_COURSE
    assert _membership(repo, student, UNIVERSIDAD_COURSE) == (group, group)
    assert _used_by(repo, token) == student
    level = sql(repo, "SELECT education_level FROM users WHERE id = ?", (student,))[0][0]
    assert level == "colegio"
    courses = client.get("/api/student/courses", headers=headers_for(repo, student)).json()
    invited = next(c for c in courses if c["id"] == UNIVERSIDAD_COURSE)
    assert (invited["enrolled"], invited["in_catalogue"]) == (True, False)
    (row,) = _listed(client, repo, teacher, group)["invitations"]
    assert (row["status"], row["used_by_name"]) == ("used", "Ana Pérez")
    assert row["used_at"]


def test_spec001_the_teacher_sees_the_public_name_of_who_used_it(repo, client):
    """FR-028t (spec 004 FR-023): the display name, else the username; never anything else."""
    teacher, group = _group(repo)
    named_token, plain_token = _tokens(repo, teacher, group, 2)
    named = make_student(repo, "colegio")
    sql(repo, "UPDATE users SET display_name = ? WHERE id = ?", ("Luis Gómez", named))
    plain = make_student(repo, "colegio")
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (plain,))[0][0]

    assert _redeem(client, repo, named, named_token).status_code == 201
    assert _redeem(client, repo, plain, plain_token).status_code == 201

    names = {
        i["token"].replace("-", ""): i["used_by_name"]
        for i in _listed(client, repo, teacher, group)["invitations"]
    }
    assert names == {named_token: "Luis Gómez", plain_token: username}
    rows = repo.get_group_invitations(teacher, group)
    assert {r["token"]: r["used_by_name"] for r in rows} == names
    assert all("username" not in r and "used_by" not in r for r in rows)


def test_spec001_a_used_invitation_is_refused(repo, client):
    """US10-AS3, FR-028r: the second student is refused and not enrolled; the invitation stays
    used by the first."""
    teacher, group = _group(repo)
    (token,) = _tokens(repo, teacher, group)
    first, second = make_student(repo, "colegio"), make_student(repo, "colegio")
    assert _redeem(client, repo, first, token).status_code == 201

    refused = _redeem(client, repo, second, token)

    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == USED
    assert _membership(repo, second, COLEGIO_COURSE) == ("not enrolled", None)
    assert _used_by(repo, token) == first


def test_spec001_an_expired_invitation_is_refused(repo, client):
    """US10-AS4, FR-028r, FR-028t: past its expiry an unused invitation is refused, is not
    consumed, reads «expired» and can no longer be revoked."""
    teacher, group = _group(repo)
    (token,) = _tokens(repo, teacher, group)
    sql(
        repo,
        "UPDATE group_invitations SET expires_at = ? WHERE token = ?",
        ("2000-01-01 00:00:00", token),
    )
    student = make_student(repo, "colegio")

    refused = _redeem(client, repo, student, token)

    assert refused.status_code == 410, refused.text
    assert refused.json()["detail"] == EXPIRED
    assert _membership(repo, student, COLEGIO_COURSE) == ("not enrolled", None)
    assert _used_by(repo, token) is None
    (row,) = _listed(client, repo, teacher, group)["invitations"]
    assert row["status"] == "expired"
    revoke = client.delete(
        f"/api/teacher/invitations/{row['id']}", headers=headers_for(repo, teacher)
    )
    assert revoke.status_code == 409, revoke.text


def test_spec001_a_revoked_invitation_is_refused(repo, client):
    """US10-AS5, FR-028r, FR-028t: the teacher revokes an unused invitation; it is then refused as
    invalid and enrols no one. Only an unused, unexpired invitation can be revoked."""
    teacher, group = _group(repo)
    revoked_token, used_token = _tokens(repo, teacher, group, 2)
    headers = headers_for(repo, teacher)
    ids = {
        i["token"].replace("-", ""): i["id"]
        for i in _listed(client, repo, teacher, group)["invitations"]
    }

    revoke = client.delete(f"/api/teacher/invitations/{ids[revoked_token]}", headers=headers)

    assert revoke.status_code == 204, revoke.text
    student = make_student(repo, "colegio")
    refused = _redeem(client, repo, student, revoked_token)
    assert refused.status_code == 404, refused.text
    assert refused.json()["detail"] == INVALID
    assert _membership(repo, student, COLEGIO_COURSE) == ("not enrolled", None)
    assert _used_by(repo, revoked_token) is None
    again = client.delete(f"/api/teacher/invitations/{ids[revoked_token]}", headers=headers)
    assert again.status_code == 409, again.text

    assert _redeem(client, repo, student, used_token).status_code == 201
    not_revocable = client.delete(f"/api/teacher/invitations/{ids[used_token]}", headers=headers)
    assert not_revocable.status_code == 409, not_revocable.text
    states = {
        i["token"].replace("-", ""): i["status"]
        for i in _listed(client, repo, teacher, group)["invitations"]
    }
    assert states == {revoked_token: "revoked", used_token: "used"}


# ── FR-028u: the reusable group code is gone ─────────────────────────────────


def test_spec001_the_old_reusable_code_no_longer_enrols(repo, client):
    """US10-AS6, FR-028u: a group's reusable code — still in `groups.invite_code`, which V1 keeps
    writing — is refused as invalid; the API neither generates nor returns it."""
    teacher, group = _group(repo)
    old_code = repo.generate_group_invite_code(group)
    student = make_student(repo, "colegio")

    refused = _redeem(client, repo, student, old_code)

    assert refused.status_code == 404, refused.text
    assert refused.json()["detail"] == INVALID
    assert _membership(repo, student, COLEGIO_COURSE) == ("not enrolled", None)
    headers = headers_for(repo, teacher)
    groups = client.get("/api/teacher/groups", headers=headers).json()
    assert groups and all("invite_code" not in g for g in groups)
    dashboard = client.get("/api/teacher/dashboard", headers=headers).json()["groups"]
    assert dashboard and all("invite_code" not in g for g in dashboard)
    gone = client.post(f"/api/teacher/groups/{group}/invite-code", headers=headers)
    assert gone.status_code == 404
    assert sql(repo, "SELECT invite_code FROM groups WHERE id = ?", (group,))[0][0] == old_code


def test_spec001_invitations_are_an_additive_migration(repo):
    """FR-028u, AGENTS R8: the bootstrap creates `group_invitations` and keeps
    `groups.invite_code`; running the migration again changes nothing."""
    repo._migrate_db()
    repo._migrate_db()
    if is_postgres(repo):
        rows = sql(
            repo,
            "SELECT table_name, column_name FROM information_schema.columns"
            " WHERE table_name IN ('group_invitations', 'groups')",
        )
        columns = {(t, c) for t, c in rows}
    else:
        columns = {
            ("group_invitations", r[1]) for r in sql(repo, "PRAGMA table_info(group_invitations)")
        }
        columns |= {("groups", r[1]) for r in sql(repo, "PRAGMA table_info(groups)")}
    expected = {
        "id",
        "group_id",
        "token",
        "created_by",
        "created_at",
        "expires_at",
        "used_by",
        "used_at",
        "revoked_at",
    }
    assert {("group_invitations", c) for c in expected} <= columns
    assert ("groups", "invite_code") in columns


# ── FR-028q: one redemption wins ─────────────────────────────────────────────


def test_spec001_simultaneous_redemptions_enrol_exactly_one(repo):
    """US10-AS7, FR-028q: two students redeem one invitation at the same moment: exactly one is
    enrolled and the invitation is used by that one; the other is told it was used."""
    teacher, group = _group(repo)
    for _ in range(3):
        (token,) = _tokens(repo, teacher, group)
        students = [make_student(repo, "colegio"), make_student(repo, "colegio")]
        barrier = threading.Barrier(2)

        def redeem(student, token=token, barrier=barrier):
            barrier.wait()
            return repo.redeem_group_invitation(student, token)["status"]

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(redeem, students))

        assert sorted(outcomes) == ["ok", "used"]
        winner = students[outcomes.index("ok")]
        assert _used_by(repo, token) == winner
        enrolled = [
            s for s in students if _membership(repo, s, COLEGIO_COURSE)[0] != "not enrolled"
        ]
        assert enrolled == [winner]


def test_spec001_one_student_redeeming_two_invitations_at_once_uses_one(repo):
    """FR-028q, FR-028s: the same student redeems two invitations of one group at the same moment:
    one enrols them, the other is refused as already a member and stays unused."""
    teacher, group = _group(repo)
    tokens = _tokens(repo, teacher, group, 2)
    student = make_student(repo, "colegio")
    barrier = threading.Barrier(2)

    def redeem(token):
        barrier.wait()
        return repo.redeem_group_invitation(student, token)["status"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(redeem, tokens))

    assert sorted(outcomes) == ["already_member", "ok"]
    assert sorted(_used_by(repo, t) is None for t in tokens) == [False, True]


# ── FR-028s: refused without consuming ───────────────────────────────────────


def test_spec001_a_gradeless_semillero_leaves_the_invitation_unused(repo, client):
    """US10-AS8, FR-028s, FR-028l: a semillero student without a grade is refused before the
    invitation is consumed; another student can still use it."""
    teacher, group = _group(repo)
    (token,) = _tokens(repo, teacher, group)
    gradeless = make_student(repo, "semillero", "6")
    sql(repo, "UPDATE users SET grade = NULL WHERE id = ?", (gradeless,))

    refused = _redeem(client, repo, gradeless, token)

    assert refused.status_code == 403, refused.text
    assert "grado" in refused.json()["detail"]
    assert _used_by(repo, token) is None
    assert _membership(repo, gradeless, COLEGIO_COURSE) == ("not enrolled", None)
    other = make_student(repo, "colegio")
    assert _redeem(client, repo, other, token).status_code == 201
    assert _used_by(repo, token) == other


def test_spec001_a_member_of_the_group_is_refused_without_consuming(repo, client):
    """US10-AS9, FR-028s: a student already enrolled in the course with this group is refused and
    the invitation stays unused; one enrolled in the course without the group joins it."""
    teacher, group = _group(repo)
    first, second = _tokens(repo, teacher, group, 2)
    member = make_student(repo, "colegio")
    assert _redeem(client, repo, member, first).status_code == 201

    refused = _redeem(client, repo, member, second)

    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == MEMBER
    assert _used_by(repo, second) is None

    from_catalogue = make_student(repo, "colegio")
    enroll(repo, from_catalogue, COLEGIO_COURSE)
    assert _membership(repo, from_catalogue, COLEGIO_COURSE) == (None, None)
    assert _redeem(client, repo, from_catalogue, second).status_code == 201
    assert _membership(repo, from_catalogue, COLEGIO_COURSE) == (group, group)


def test_spec001_a_group_without_course_is_refused_without_consuming(repo, client):
    """FR-028s: the group has no course to open — refused, and the invitation stays unused."""
    teacher, group = _group(repo, course_id=None)
    (token,) = _tokens(repo, teacher, group)
    student = make_student(repo, "colegio")

    refused = _redeem(client, repo, student, token)

    assert refused.status_code == 400, refused.text
    assert refused.json()["detail"] == "El grupo no tiene un curso asignado."
    assert _used_by(repo, token) is None


def test_spec001_only_a_student_redeems_an_invitation(repo, client):
    """FR-028s: a teacher or an admin account is refused and the invitation stays unused."""
    teacher, group = _group(repo)
    (token,) = _tokens(repo, teacher, group)
    for account in (_approved_teacher(repo), _admin(repo)):
        refused = _redeem(client, repo, account, token)
        assert refused.status_code == 403, refused.text
    assert _used_by(repo, token) is None


def test_spec001_repository_redemption_statuses(repo):
    """FR-028q, FR-028r, FR-028s: what the repository answers for each case; only `ok` consumes."""
    teacher, group = _group(repo)
    tokens = _tokens(repo, teacher, group, 4)
    live, used, expired, revoked = tokens
    sql(
        repo,
        "UPDATE group_invitations SET expires_at = ? WHERE token = ?",
        ("2000-01-01 00:00:00", expired),
    )
    invitation_id = next(
        i["id"] for i in repo.get_group_invitations(teacher, group) if i["token"] == revoked
    )
    assert repo.revoke_group_invitation(teacher, invitation_id) == "revoked"
    student, other = make_student(repo, "colegio"), make_student(repo, "colegio")
    assert repo.redeem_group_invitation(other, used)["status"] == "ok"

    assert repo.redeem_group_invitation(student, live) == {
        "status": "ok",
        "course_id": COLEGIO_COURSE,
        "group_id": group,
    }
    for token, status in [
        ("ZZZZZZZZZZ", "invalid"),
        (revoked, "invalid"),
        (used, "used"),
        (expired, "expired"),
    ]:
        outcome = repo.redeem_group_invitation(make_student(repo, "colegio"), token)
        assert outcome["status"] == status, token
    assert repo.redeem_group_invitation(other, live)["status"] == "used"
    assert [_used_by(repo, t) for t in tokens] == [student, other, None, None]


# ── FR-028p, FR-028t: only the group's own teacher ───────────────────────────


def test_spec001_only_the_groups_teacher_manages_its_invitations(repo, client):
    """US10-AS10, FR-028p, FR-028t: another teacher and an admin are answered «not found» for the
    group and its invitations, a student is refused, and nothing changes; the group's teacher
    stops managing them once no longer an approved, active teacher."""
    owner, group = _group(repo)
    (token,) = _tokens(repo, owner, group)
    (row,) = repo.get_group_invitations(owner, group)
    other, admin = _approved_teacher(repo), _admin(repo)

    for account in (other, admin):
        headers = headers_for(repo, account)
        created = client.post(
            f"/api/teacher/groups/{group}/invitations", headers=headers, json={"count": 1}
        )
        listed = client.get(f"/api/teacher/groups/{group}/invitations", headers=headers)
        revoked = client.delete(f"/api/teacher/invitations/{row['id']}", headers=headers)
        assert (created.status_code, listed.status_code, revoked.status_code) == (404, 404, 404)
        assert repo.create_group_invitations(account, group, 1, TTL) is None
        assert repo.get_group_invitations(account, group) is None
        assert repo.revoke_group_invitation(account, row["id"]) == "not_found"

    student_headers = headers_for(repo, make_student(repo, "colegio"))
    for method, path, body in [
        ("POST", f"/api/teacher/groups/{group}/invitations", {"count": 1}),
        ("GET", f"/api/teacher/groups/{group}/invitations", None),
        ("DELETE", f"/api/teacher/invitations/{row['id']}", None),
    ]:
        response = client.request(method, path, headers=student_headers, json=body)
        assert response.status_code == 403, (method, path)

    owner_headers = headers_for(repo, owner)
    assert (
        client.get("/api/teacher/groups/99999999/invitations", headers=owner_headers).status_code
        == 404
    )
    assert (
        client.delete("/api/teacher/invitations/99999999", headers=owner_headers).status_code == 404
    )
    assert [i["token"] for i in repo.get_group_invitations(owner, group)] == [token]
    assert _used_by(repo, token) is None

    sql(repo, "UPDATE users SET approved = 0 WHERE id = ?", (owner,))
    assert repo.create_group_invitations(owner, group, 1, TTL) is None
    assert repo.get_group_invitations(owner, group) is None
    assert repo.revoke_group_invitation(owner, row["id"]) == "not_found"
