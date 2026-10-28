"""
Spec 009 delivery GI — the admin edits a group's institution and grade, on both engines (plan-gi.md
§ The edit, § The audit, § Listing, § API; tasks T005 … T012): the edit and its audit row in spec
004's `audit_account_events` (O-GI1 (a)), a save that changes nothing, no account touched, the
refusals, only an active admin, the groups without institution and their count, the confirmation
asked for the same institution and grade (O-GI5 (a)) and the institutions already recorded, one per
key.

[CHANGE] tests: the base has no edit of a group's institution, no filter of groups without one and
no list of recorded institutions, so each fails there before its implementation. PostgreSQL
persists between tests: every institution here carries a unique suffix.
"""

import json
import uuid

from tests.integration.conftest import (
    enroll,
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    set_rating,
    sql,
)

ACTION = "group_institution_changed"


def _admin(repo) -> int:
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _approved_teacher(repo) -> int:
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _suffix() -> str:
    return uuid.uuid4().hex[:6]


def _group_row(repo, group_id) -> tuple:
    rows = sql(
        repo,
        "SELECT name, teacher_id, course_id, institution, grade FROM groups WHERE id = ?",
        (group_id,),
    )
    return tuple(rows[0]) if rows else None


def _audit(repo, teacher_id) -> list:
    return [
        tuple(r)
        for r in sql(
            repo,
            "SELECT actor_id, detail, created_at FROM audit_account_events"
            " WHERE user_id = ? AND action = ? ORDER BY id",
            (teacher_id, ACTION),
        )
    ]


def _put(client, headers, group_id, institution, grade, confirm_same=False):
    return client.put(
        f"/api/admin/groups/{group_id}/institution",
        json={"institution": institution, "grade": grade, "confirm_same": confirm_same},
        headers=headers,
    )


def _listed(client, headers, **params) -> dict:
    response = client.get("/api/admin/groups", params=params, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


# ── T005 — the edit and its audit (US4-AS1, FR-019, FR-020) ──────────────────────────────────


def test_spec009_gi_the_admin_sets_a_groups_institution_and_grade(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    group = make_group(repo, teacher)  # created by the teacher: no institution, no grade
    assert _group_row(repo, group)[3:] == (None, None)
    institution = f"  Colegio   San José {_suffix()} "
    stored = " ".join(institution.split())
    headers = headers_for(repo, admin)

    response = _put(client, headers, group, institution, 9)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["group_id"] == group
    assert body["institution"] == stored
    assert body["grade"] == 9
    assert body["unchanged"] is False
    assert body["students_with_other_grade"] == 0

    listed = {g["id"]: g for g in _listed(client, headers)["groups"]}
    assert listed[group]["institution"] == stored
    assert listed[group]["grade"] == 9
    assert _group_row(repo, group)[3:] == (stored, 9)

    events = _audit(repo, teacher)
    assert len(events) == 1
    actor, detail, created_at = events[0]
    assert actor == admin
    assert created_at is not None
    assert json.loads(detail) == {
        "group_id": group,
        "before": {"institution": None, "grade": None},
        "after": {"institution": stored, "grade": 9},
    }
    # The account audit the admin reads shows it, with the group's teacher as the account.
    audit = client.get("/api/admin/account-audit", headers=headers).json()["events"]
    entry = next(e for e in audit if e["action"] == ACTION and e["user_id"] == teacher)
    assert entry["actor_id"] == admin
    assert json.loads(entry["detail"])["group_id"] == group

    # A second edit records before and after again.
    response = _put(client, headers, group, stored, None)
    assert response.status_code == 200, response.text
    assert response.json()["grade"] is None
    second = json.loads(_audit(repo, teacher)[-1][1])
    assert second["before"] == {"institution": stored, "grade": 9}
    assert second["after"] == {"institution": stored, "grade": None}


# ── T006 — a save that changes nothing (FR-020) ──────────────────────────────────────────────


def test_spec009_gi_an_unchanged_save_records_nothing(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    group = make_group(repo, teacher)
    institution = f"Liceo Prueba {_suffix()}"
    headers = headers_for(repo, admin)
    assert _put(client, headers, group, institution, 7).status_code == 200
    assert len(_audit(repo, teacher)) == 1

    # The same values, typed with other spaces: stored the same, so nothing changes.
    response = _put(client, headers, group, "  " + institution.replace(" ", "   ") + " ", 7)
    assert response.status_code == 200, response.text
    assert response.json()["unchanged"] is True
    assert response.json()["institution"] == institution
    assert len(_audit(repo, teacher)) == 1

    ok, code, _ = repo.set_group_institution(admin, group, institution, 7)
    assert (ok, code) == (True, "unchanged")
    assert len(_audit(repo, teacher)) == 1


# ── T007 — no account changes (US4-AS2, FR-021, O-GI2 (a)) ───────────────────────────────────


def _snapshot(repo, students, group) -> dict:
    marks = ",".join("?" for _ in students)
    return {
        "users": sorted(
            tuple(r) for r in sql(repo, f"SELECT * FROM users WHERE id IN ({marks})", students)
        ),
        "enrollments": sorted(
            tuple(r)
            for r in sql(repo, f"SELECT * FROM enrollments WHERE user_id IN ({marks})", students)
        ),
        "ratings": sorted(
            tuple(r)
            for r in sql(
                repo,
                f"SELECT * FROM student_course_topic_elo WHERE user_id IN ({marks})",
                students,
            )
        ),
        "group": _group_row(repo, group)[:3],
    }


def test_spec009_gi_an_edit_changes_no_account(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=1)
    group = make_group(repo, teacher, course_id)
    same = make_student(repo, "semillero", "9")
    other = make_student(repo, "semillero", "10")
    tester = make_student(repo, "semillero", "8")
    sql(repo, "UPDATE users SET is_test_user = 1 WHERE id = ?", (tester,))
    students = [same, other, tester]
    for n, student in enumerate(students):
        enroll(repo, student, course_id, group)
        set_rating(repo, student, course_id, "Fracciones", 1000.0 + 25 * n)
    sql(
        repo,
        f"UPDATE users SET access_until = '2099-12-31' WHERE id IN ({','.join('?' * 3)})",
        students,
    )
    before = _snapshot(repo, students, group)
    headers = headers_for(repo, admin)

    response = _put(client, headers, group, f"Colegio Cuentas {_suffix()}", 9)
    assert response.status_code == 200, response.text
    # Only the active, non-test student whose grade is not 9 is counted; nobody is changed.
    assert response.json()["students_with_other_grade"] == 1
    assert _snapshot(repo, students, group) == before

    response = _put(client, headers, group, f"Colegio Otro {_suffix()}", 8)
    assert response.status_code == 200, response.text
    assert response.json()["students_with_other_grade"] == 2
    assert _snapshot(repo, students, group) == before


# ── T008 — refusals (US4-AS3, FR-019, FR-023, O-GI6 (a)) ─────────────────────────────────────


def test_spec009_gi_an_invalid_edit_changes_nothing(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    group = make_group(repo, teacher)
    institution = f"Colegio Válido {_suffix()}"
    headers = headers_for(repo, admin)
    assert _put(client, headers, group, institution, 6).status_code == 200
    stored = _group_row(repo, group)
    events = _audit(repo, teacher)

    for value, grade, reason in (
        ("", 6, "Escribe la institución."),
        ("    ", 6, "Escribe la institución."),
        ("x" * 201, 6, "La institución tiene más de 200 caracteres."),
        (institution, 12, "El grado del grupo va de 6.º a 11.º."),
        (institution, 5, "El grado del grupo va de 6.º a 11.º."),
    ):
        response = _put(client, headers, group, value, grade)
        assert response.status_code == 400, (value, grade, response.text)
        assert response.json()["detail"] == reason
        ok, code, message = repo.set_group_institution(admin, group, value, grade)
        assert (ok, code, message) == (False, "invalid", reason)

    missing = 10_000_000 + int(uuid.uuid4().int % 1_000_000)
    response = _put(client, headers, missing, institution, 6)
    assert response.status_code == 404, response.text
    assert repo.set_group_institution(admin, missing, institution, 6)[:2] == (False, "not_found")

    assert _group_row(repo, group) == stored
    assert _audit(repo, teacher) == events


# ── T009 — only an active admin (US4-AS4, FR-023) ────────────────────────────────────────────


def test_spec009_gi_only_an_active_admin_edits(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    group = make_group(repo, teacher)
    student = make_student(repo)
    other_teacher = _approved_teacher(repo)
    before = _group_row(repo, group)

    for actor in (teacher, other_teacher, student):
        headers = headers_for(repo, actor)
        assert _put(client, headers, group, "Colegio Ajeno", 9).status_code == 403
        assert (
            client.get(
                "/api/admin/groups", params={"without_institution": "true"}, headers=headers
            ).status_code
            == 403
        )
        assert client.get("/api/admin/institutions", headers=headers).status_code == 403
        ok, code, _ = repo.set_group_institution(actor, group, "Colegio Ajeno", 9)
        assert (ok, code) == (False, "forbidden")

    sql(repo, "UPDATE users SET active = 0 WHERE id = ?", (admin,))
    ok, code, _ = repo.set_group_institution(admin, group, "Colegio Ajeno", 9)
    assert (ok, code) == (False, "forbidden")

    assert _group_row(repo, group) == before
    assert _audit(repo, teacher) == []


# ── T010 — the same institution and grade asks for confirmation (US4-AS6, FR-024, O-GI5) ─────


def test_spec009_gi_the_same_institution_and_grade_asks_for_confirmation(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    other_teacher = _approved_teacher(repo)
    suffix = _suffix()
    first = make_group(repo, other_teacher)
    group = make_group(repo, teacher)
    headers = headers_for(repo, admin)
    assert _put(client, headers, first, f"colegio san jose {suffix}", 6).status_code == 200

    typed = f"Colegio  San José {suffix}"
    response = _put(client, headers, group, typed, 6)
    assert response.status_code == 409, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "same_institution_and_grade"
    assert [g["id"] for g in detail["groups"]] == [first]
    named = detail["groups"][0]
    first_row = _group_row(repo, first)
    assert named["name"] == first_row[0]
    teacher_name = sql(repo, "SELECT username FROM users WHERE id = ?", (other_teacher,))[0][0]
    assert named["teacher"] == teacher_name
    assert _group_row(repo, group)[3:] == (None, None)
    assert _audit(repo, teacher) == []

    response = _put(client, headers, group, typed, 6, confirm_same=True)
    assert response.status_code == 200, response.text
    assert response.json()["institution"] == f"Colegio San José {suffix}"  # as typed, collapsed
    assert len(_audit(repo, teacher)) == 1

    # The same institution with another grade is saved at once.
    third = make_group(repo, teacher)
    response = _put(client, headers, third, f"COLEGIO SAN JOSÉ {suffix}", 7)
    assert response.status_code == 200, response.text
    assert _group_row(repo, third)[3:] == (f"COLEGIO SAN JOSÉ {suffix}", 7)


# ── T011 — the groups without institution, with their count (US4-AS5, FR-022) ────────────────


def test_spec009_gi_the_groups_without_institution_are_listed_with_their_count(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=1)
    bare = make_group(repo, teacher, course_id)
    blank = make_group(repo, teacher)
    sql(repo, "UPDATE groups SET institution = '   ' WHERE id = ?", (blank,))
    named = make_group(repo, teacher)
    headers = headers_for(repo, admin)
    assert _put(client, headers, named, f"Colegio Con Nombre {_suffix()}", 9).status_code == 200
    student = make_student(repo)
    enroll(repo, student, course_id, bare)

    everything = _listed(client, headers)
    without = _listed(client, headers, without_institution="true")
    ids = [g["id"] for g in without["groups"]]
    assert bare in ids and blank in ids and named not in ids
    assert without["count"] == len(without["groups"])
    assert all(not (g["institution"] or "").strip() for g in without["groups"])
    # Exactly those: every group of the full list without institution, and no other.
    expected = {g["id"] for g in everything["groups"] if not (g["institution"] or "").strip()}
    assert set(ids) == expected
    # The count is there without the filter too, so the admin sees what is left.
    assert everything["without_institution"] == len(expected)
    row = next(g for g in without["groups"] if g["id"] == bare)
    assert row["student_count"] == 1
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (teacher,))[0][0]
    assert row["teacher_name"] == username

    assert _put(client, headers, bare, f"Colegio Nuevo {_suffix()}", 10).status_code == 200
    after = _listed(client, headers, without_institution="true")
    assert bare not in [g["id"] for g in after["groups"]]
    assert after["count"] == without["count"] - 1 == len(after["groups"])


# ── T012 — the recorded institutions, one per key (FR-024) ───────────────────────────────────


def test_spec009_gi_recorded_institutions_one_per_key(repo, client):
    admin = _admin(repo)
    teacher = _approved_teacher(repo)
    suffix = _suffix()
    oldest = make_group(repo, teacher)
    newer = make_group(repo, teacher)
    pinas = make_group(repo, teacher)
    headers = headers_for(repo, admin)
    assert _put(client, headers, oldest, f"Colegio San José {suffix}", 6).status_code == 200
    assert _put(client, headers, newer, f"colegio  san jose {suffix}", 7).status_code == 200
    assert _put(client, headers, pinas, f"Liceo Piñas {suffix}", 6).status_code == 200

    rows = repo.get_recorded_institutions()
    assert {r["id"]: r["institution"] for r in rows if suffix in (r["institution"] or "")} == {
        oldest: f"Colegio San José {suffix}",
        newer: f"colegio san jose {suffix}",
        pinas: f"Liceo Piñas {suffix}",
    }

    response = client.get("/api/admin/institutions", headers=headers)
    assert response.status_code == 200, response.text
    ours = [i for i in response.json()["institutions"] if suffix in i["institution"]]
    assert sorted((i["institution"], i["groups"]) for i in ours) == [
        (f"Colegio San José {suffix}", 2),
        (f"Liceo Piñas {suffix}", 1),
    ]
