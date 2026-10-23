"""
Spec 009 delivery I1 — what the import stores, on both engines (plan-i1.md; tasks T007 … T011,
T039 … T042): the import's tables and columns (schema version 8), the creation in chunks with the
identification as credentials, one running import per admin, the audit without personal data,
linking and unlinking an identification, the name of an imported account, the recovery e-mail and
the groups the admin creates for a teacher.

[CHANGE] tests: the base branch has no import. Invented identifications only (the repository is
public).
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.identity import colombia_today
from src.infrastructure.persistence.schema_version import SCHEMA_VERSION
from tests.integration.conftest import (
    is_postgres,
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


def _approved_teacher(repo) -> int:
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _identification() -> str:
    """An invented ten-digit identification, unique per call (PostgreSQL persists)."""
    return "88" + str(uuid.uuid4().int)[:8]


def _day(offset: int) -> str:
    return (colombia_today(datetime.now(timezone.utc)) + timedelta(days=offset)).isoformat()


def _group_with_course(repo):
    teacher = _approved_teacher(repo)
    course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=2)
    return make_group(repo, teacher, course_id), course_id


def _row(number, identification, group_id, **overrides) -> dict:
    row = {
        "row": number,
        "identification": identification,
        "display_name": "Ana Pérez",
        "level": "semillero",
        "grade": 9,
        "group_id": group_id,
        "access_until": _day(60),
        "recovery_email": None,
    }
    row.update(overrides)
    return row


def _digest() -> str:
    return uuid.uuid4().hex * 2


def _started(repo, admin, total_rows=1) -> str:
    outcome, record = repo.start_import(admin, _digest(), total_rows)
    assert outcome == "started", outcome
    return record["import_id"]


def _user_named(repo, username):
    rows = sql(repo, "SELECT id FROM users WHERE username = ?", (username,))
    return rows[0][0] if rows else None


def _events(repo, user_id, action) -> list:
    return [
        tuple(r)
        for r in sql(
            repo,
            "SELECT actor_id, detail FROM audit_account_events WHERE user_id = ? AND action = ?",
            (user_id, action),
        )
    ]


def _make_idle(repo, import_id, minutes=11) -> None:
    if is_postgres(repo):
        statement = (
            "UPDATE student_imports SET updated_at = CURRENT_TIMESTAMP - INTERVAL '%s minutes'"
            % minutes
        )
    else:
        statement = (
            "UPDATE student_imports SET updated_at = datetime('now', '-%s minutes')" % minutes
        )
    sql(repo, statement + " WHERE import_id = ?", (import_id,))


# ── The migration (T040, FR-018, R8) ─────────────────────────────────────────────────────────


def test_spec009_the_migration_adds_the_import_tables_and_columns(repo):
    """Schema version 8: three new tables and three nullable columns, additive on both engines
    (the D3 parity test compares the rest)."""
    assert SCHEMA_VERSION >= 8
    assert sql(repo, "SELECT MAX(version) FROM schema_versions")[0][0] == SCHEMA_VERSION
    for statement in (
        "SELECT recovery_email FROM users",
        "SELECT institution, grade FROM groups",
        "SELECT user_id, identification, origin, linked_by, linked_at FROM student_identifications",
        "SELECT import_id, admin_id, digest, state, total_rows, started_at, updated_at,"
        " finished_at FROM student_imports",
        "SELECT import_id, row_number, result, user_id, reason FROM student_import_rows",
    ):
        assert sql(repo, statement + " WHERE 1 = 0") == []


# ── Creation in chunks (T007, FR-003, FR-005, FR-006, FR-018) ─────────────────────────────────


def test_spec009_an_import_creates_students_with_the_identification_as_credentials(repo):
    admin = _admin(repo)
    group, course_id = _group_with_course(repo)
    first, second = _identification(), _identification()
    import_id = _started(repo, admin, 2)

    results = repo.import_student_chunk(
        import_id,
        [
            _row(2, first, group, recovery_email="familia@example.com"),
            _row(3, second, group, display_name="Luis Gómez", level="colegio", grade=None),
        ],
    )

    assert [(r["row"], r["result"], r["reason"]) for r in results] == [
        (2, "created", None),
        (3, "created", None),
    ]
    user_id = results[0]["user_id"]
    assert user_id == _user_named(repo, first)
    account = repo.get_user_by_id(user_id)
    assert account["role"] == "student" and account["group_id"] == group
    assert account["display_name"] == "Ana Pérez"
    assert account["must_change_password"] is False  # FR-005: no change at first access
    assert account["access_until"] == _day(60)
    assert repo.verify_user_password(user_id, first)  # the identification is the password
    assert {e["id"] for e in repo.get_user_enrollments(user_id)} == {course_id}
    stored = sql(
        repo,
        "SELECT education_level, grade, recovery_email, email, created_by FROM users WHERE id = ?",
        (user_id,),
    )[0]
    assert tuple(stored) == ("semillero", "9", "familia@example.com", None, admin)
    second = sql(
        repo, "SELECT grade, recovery_email FROM users WHERE id = ?", (results[1]["user_id"],)
    )[0]
    assert tuple(second) == (None, None)
    assert repo.get_student_identification(user_id) == {
        "identification": first,
        "origin": "import",
        "imported": True,
    }
    # The identification signs in; the recovery e-mail never does (FR-018).
    assert repo.login_user(first, first)[0] == user_id
    assert repo.login_user("familia@example.com", first) is None
    assert repo.login_account_id("familia@example.com") is None
    assert [actor for actor, _ in _events(repo, user_id, "student_imported")] == [admin]


def test_spec009_a_row_linked_or_taken_meanwhile_is_skipped_never_duplicated(repo):
    """FR-006, FR-007: each row is checked again inside its transaction; importing the same rows
    twice creates nothing the second time."""
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    linked, taken, fresh = _identification(), _identification(), _identification()
    linked_student = make_student(repo)
    assert repo.link_identification(admin, linked_student, linked)[0]
    taken_by = make_student(repo)
    sql(repo, "UPDATE users SET username = ? WHERE id = ?", (taken, taken_by))
    import_id = _started(repo, admin, 3)
    rows = [_row(2, linked, group), _row(3, taken, group), _row(4, fresh, group)]

    results = repo.import_student_chunk(import_id, rows)

    assert [(r["result"], r["reason"]) for r in results] == [
        ("skipped", "identification_linked"),
        ("skipped", "identification_is_username"),
        ("created", None),
    ]
    assert results[0]["user_id"] is None and results[1]["user_id"] is None
    again = repo.import_student_chunk(import_id, [_row(5, fresh, group)])
    assert [(r["result"], r["reason"]) for r in again] == [("skipped", "identification_linked")]
    assert sql(repo, "SELECT COUNT(*) FROM users WHERE username = ?", (fresh,))[0][0] == 1
    assert sql(repo, "SELECT username FROM users WHERE id = ?", (linked_student,))[0][0] != linked


@pytest.mark.parametrize(
    "overrides, result, reason",
    [
        ({"display_name": "Elver Galarga"}, "error", "name_refused"),
        ({"display_name": "  "}, "error", "name_missing"),
        ({"level": "semillero", "grade": None}, "error", "level_grade"),
        ({"level": "colegio", "grade": 9}, "error", "level_grade"),
        ({"access_until": "past"}, "error", "access_expired"),
        ({"identification": "1.234.567"}, "error", "identification_not_digits"),
        ({"group_id": 987654321}, "skipped", "group_missing"),
    ],
)
def test_spec009_a_chunk_applies_spec004_creation_rules(repo, overrides, result, reason):
    """FR-003: the import creates through spec 004's validations (FR-040, FR-043, FR-044); a row
    they refuse creates nothing and keeps its reason code."""
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    identification = _identification()
    if overrides.get("access_until") == "past":
        overrides["access_until"] = _day(-1)
    row = {**_row(2, identification, group), **overrides}
    import_id = _started(repo, admin)

    results = repo.import_student_chunk(import_id, [row])

    assert [(r["result"], r["reason"], r["user_id"]) for r in results] == [(result, reason, None)]
    assert _user_named(repo, row["identification"]) is None


# ── One import at a time (T008, FR-010, US1-AS8) ──────────────────────────────────────────────


def test_spec009_one_running_import_per_admin_and_a_retry_returns_it(repo):
    admin, other_admin = _admin(repo), _admin(repo)
    group, _ = _group_with_course(repo)
    digest = _digest()

    outcome, first = repo.start_import(admin, digest, 30)
    assert outcome == "started" and first["state"] == "running" and first["total_rows"] == 30
    retry_outcome, retry = repo.start_import(admin, digest, 30)
    assert (retry_outcome, retry["import_id"]) == ("retry", first["import_id"])
    busy_outcome, busy = repo.start_import(admin, _digest(), 30)
    assert busy_outcome == "busy" and busy["import_id"] == first["import_id"]
    assert repo.start_import(other_admin, _digest(), 1)[0] == "started"
    assert repo.start_import(make_student(repo), _digest(), 1) == ("refused", None)

    assert repo.finish_import(first["import_id"])
    assert repo.get_import(first["import_id"])["state"] == "finished"
    # A retried confirmation returns the first result, even once it has finished.
    assert repo.start_import(admin, digest, 30)[0] == "retry"
    # A finished import takes no more rows.
    assert (
        repo.import_student_chunk(first["import_id"], [_row(2, _identification(), group)]) is None
    )
    assert repo.record_import_rows(first["import_id"], [{"row": 3, "result": "error"}]) is False
    assert sql(repo, "SELECT COUNT(*) FROM student_imports WHERE admin_id = ?", (admin,))[0][0] == 1


def test_spec009_an_idle_import_becomes_interrupted(repo):
    """Plan § Running the import: a worker that dies leaves the import running; after 10 minutes
    without progress it reads as interrupted, takes no more rows, and the admin can start again."""
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    digest = _digest()
    _, record = repo.start_import(admin, digest, 2)
    _make_idle(repo, record["import_id"], minutes=9)
    assert repo.get_import(record["import_id"])["state"] == "running"

    _make_idle(repo, record["import_id"], minutes=11)

    assert repo.get_import(record["import_id"])["state"] == "interrupted"
    assert [i["state"] for i in repo.list_imports(admin)] == ["interrupted"]
    outcome, again = repo.start_import(admin, digest, 2)  # same file: a new import, not a retry
    assert outcome == "started" and again["import_id"] != record["import_id"]
    assert (
        repo.import_student_chunk(record["import_id"], [_row(2, _identification(), group)]) is None
    )
    assert [i["import_id"] for i in repo.list_imports(admin)] == [
        again["import_id"],
        record["import_id"],
    ]


# ── The audit (T009, FR-009, US1-AS7) ─────────────────────────────────────────────────────────


def test_spec009_the_audit_holds_ids_and_codes_never_the_data(repo):
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    created, refused = _identification(), _identification()
    import_id = _started(repo, admin, 4)
    results = repo.import_student_chunk(
        import_id,
        [
            _row(2, created, group, display_name="Rosa Díaz", recovery_email="rosa@example.com"),
            _row(3, refused, group, display_name="Elver Galarga"),
        ],
    )
    assert repo.record_import_rows(
        import_id,
        [
            {"row": 4, "result": "duplicate"},
            {"row": 5, "result": "error", "reason": "identification_altered"},
        ],
    )
    assert repo.finish_import(import_id)

    record = repo.get_import(import_id)

    assert record["admin_id"] == admin and record["state"] == "finished"
    assert record["started_at"] and record["finished_at"]
    assert record["counts"] == {
        "created": 1,
        "updated": 0,
        "unchanged": 0,
        "skipped": 0,
        "duplicate": 1,
        "error": 2,
    }
    assert [(r["row"], r["result"], r["user_id"], r["reason"]) for r in record["rows"]] == [
        (2, "created", results[0]["user_id"], None),
        (3, "error", None, "name_refused"),
        (4, "duplicate", None, None),
        (5, "error", None, "identification_altered"),
    ]
    stored = sql(repo, "SELECT * FROM student_imports WHERE import_id = ?", (import_id,))
    stored += sql(repo, "SELECT * FROM student_import_rows WHERE import_id = ?", (import_id,))
    stored += sql(
        repo,
        "SELECT * FROM audit_account_events WHERE user_id = ?",
        (results[0]["user_id"],),
    )
    text = repr([tuple(r) for r in stored])
    password_hash = sql(
        repo, "SELECT password_hash FROM users WHERE id = ?", (results[0]["user_id"],)
    )[0][0]
    for secret in (created, refused, "Rosa", "Elver", "rosa@example.com", password_hash):
        assert secret not in text


# ── Linking and unlinking (T010, T039, FR-007, FR-017, US1-AS5) ──────────────────────────────


def test_spec009_the_admin_links_an_identification_explicitly(repo):
    admin, teacher = _admin(repo), _approved_teacher(repo)
    student, other = make_student(repo), make_student(repo)
    username = sql(repo, "SELECT username FROM users WHERE id = ?", (student,))[0][0]
    identification = _identification()

    assert not repo.link_identification(teacher, student, identification)[0]
    assert not repo.link_identification(admin, teacher, identification)[0]
    assert not repo.link_identification(admin, student, "1.234.567")[0]
    other_username = sql(repo, "SELECT username FROM users WHERE id = ?", (other,))[0][0]
    assert not repo.link_identification(admin, student, other_username)[0]
    assert repo.get_student_identification(student) == {
        "identification": None,
        "origin": None,
        "imported": False,
    }

    ok, message = repo.link_identification(admin, student, f"  {identification} ")

    assert ok, message
    assert repo.get_student_identification(student) == {
        "identification": identification,
        "origin": "admin_link",
        "imported": False,
    }
    assert sql(repo, "SELECT username FROM users WHERE id = ?", (student,))[0][0] == username
    assert _events(repo, student, "identification_linked") == [(admin, None)]
    assert not repo.link_identification(admin, student, _identification())[0]  # one per account
    assert not repo.link_identification(admin, other, identification)[0]  # one account per id
    lookups = repo.get_import_lookups([identification, _identification()])
    assert lookups["linked"][identification]["user_id"] == student
    assert list(lookups["linked"]) == [identification]
    accounts = {a["id"]: a for a in repo.get_accounts_admin()}
    assert accounts[student]["identification"] == identification
    assert accounts[other]["identification"] is None


def test_spec009_removing_a_link_keeps_the_account_as_it_is(repo):
    admin, teacher = _admin(repo), _approved_teacher(repo)
    group, _ = _group_with_course(repo)
    identification = _identification()
    import_id = _started(repo, admin)
    user_id = repo.import_student_chunk(import_id, [_row(2, identification, group)])[0]["user_id"]

    assert not repo.unlink_identification(teacher, user_id)[0]
    ok, message = repo.unlink_identification(admin, user_id)

    assert ok, message
    assert repo.get_student_identification(user_id)["identification"] is None
    assert sql(repo, "SELECT username FROM users WHERE id = ?", (user_id,))[0][0] == identification
    assert repo.verify_user_password(user_id, identification)
    assert _events(repo, user_id, "identification_unlinked") == [(admin, None)]
    # A later import no longer matches it; the identification is still that account's username,
    # so a row with it is an error (FR-007).
    lookups = repo.get_import_lookups([identification])
    assert lookups["linked"] == {} and lookups["usernames"] == {identification}
    assert not repo.unlink_identification(admin, user_id)[0]  # nothing left to remove


# ── The name of an imported account (T011, FR-014, FR-015, US3) ──────────────────────────────


def test_spec009_only_the_admin_renames_an_imported_account(repo):
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    identification = _identification()
    import_id = _started(repo, admin)
    user_id = repo.import_student_chunk(import_id, [_row(2, identification, group)])[0]["user_id"]

    ok, message = repo.set_display_name(user_id, user_id, "Otro Nombre")

    assert not ok and message
    assert repo.get_user_by_id(user_id)["display_name"] == "Ana Pérez"
    assert _events(repo, user_id, "display_name_changed") == []
    assert repo.set_display_name(admin, user_id, "Ana María Pérez") == (True, "Ana María Pérez")
    assert _events(repo, user_id, "display_name_changed") == [(admin, None)]
    # Still an imported account once its link is removed.
    assert repo.unlink_identification(admin, user_id)[0]
    assert not repo.set_display_name(user_id, user_id, "Otro Nombre")[0]
    assert repo.get_student_identification(user_id)["imported"] is True
    # A student created otherwise keeps changing their own name (spec 004 FR-025).
    student = make_student(repo)
    assert repo.set_display_name(student, student, "Nombre Propio")[0]


def test_spec009_a_one_by_one_username_that_is_a_linked_identification_is_refused(repo):
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    linked_to, identification = make_student(repo), _identification()
    assert repo.link_identification(admin, linked_to, identification)[0]

    ok, message, user_id = repo.create_student_account(
        admin, identification, "Temporal-1234", "Luis Gómez", group, "colegio"
    )

    assert (ok, user_id) == (False, None) and message
    assert _user_named(repo, identification) is None
    assert repo.create_student_account(
        admin, _identification(), "Temporal-1234", "Luis Gómez", group, "colegio"
    )[0]


# ── The recovery e-mail of an existing account (T041, N27) ───────────────────────────────────


def test_spec009_a_recovery_email_change_is_applied_only_by_the_admin(repo):
    admin, teacher, student = _admin(repo), _approved_teacher(repo), make_student(repo)
    sql(repo, "UPDATE users SET email = ? WHERE id = ?", (f"{student}@login.example", student))

    assert not repo.set_recovery_email(teacher, student, "casa@example.com")[0]
    assert not repo.set_recovery_email(admin, student, "no es un correo")[0]
    assert not repo.set_recovery_email(admin, teacher, "casa@example.com")[0]
    ok, message = repo.set_recovery_email(admin, student, " casa@example.com ")

    assert ok, message
    stored = sql(repo, "SELECT recovery_email, email FROM users WHERE id = ?", (student,))[0]
    assert tuple(stored) == ("casa@example.com", f"{student}@login.example")
    assert _events(repo, student, "recovery_email_changed") == [(admin, None)]
    lookups = repo.get_import_lookups([])
    assert lookups == {"linked": {}, "usernames": set()}


def test_spec009_the_lookups_give_what_the_preview_compares(repo):
    """The preview's two reads (plan § Preview): each linked identification's account — group,
    last day, recovery e-mail — and the identifications that are usernames in use."""
    admin = _admin(repo)
    group, _ = _group_with_course(repo)
    linked, taken, unknown = _identification(), _identification(), _identification()
    import_id = _started(repo, admin)
    user_id = repo.import_student_chunk(
        import_id, [_row(2, linked, group, recovery_email="familia@example.com")]
    )[0]["user_id"]
    sql(repo, "UPDATE users SET username = ? WHERE id = ?", (taken, make_student(repo)))

    lookups = repo.get_import_lookups([linked, taken, unknown])

    assert lookups["linked"] == {
        linked: {
            "user_id": user_id,
            "group_id": group,
            "access_until": _day(60),
            "recovery_email": "familia@example.com",
        }
    }
    assert lookups["usernames"] == {linked, taken}


# ── Groups the admin creates for a teacher (T042, N25, N26 (a)) ───────────────────────────────


def test_spec009_the_admin_creates_a_group_for_a_teacher(repo):
    admin, teacher, other_teacher = _admin(repo), _approved_teacher(repo), _approved_teacher(repo)
    course_id, _ = make_course(repo, ["Fracciones"])
    name = "Semillero 9 " + uuid.uuid4().hex[:6]

    ok, message, group_id = repo.create_group_for_teacher(
        admin, teacher, name, course_id, institution="Colegio San José", grade=9
    )

    assert ok, message
    mine = {g["group_id"]: g for g in repo.get_groups_by_teacher(teacher)}
    assert mine[group_id]["name"] == name and mine[group_id]["course_id"] == course_id
    assert (mine[group_id]["institution"], mine[group_id]["grade"]) == ("Colegio San José", 9)
    every = {g["id"]: g for g in repo.get_all_groups()}
    assert every[group_id]["teacher_id"] == teacher
    assert (every[group_id]["institution"], every[group_id]["grade"]) == ("Colegio San José", 9)
    assert every[group_id]["course_id"] == course_id
    assert group_id not in {g["group_id"] for g in repo.get_groups_by_teacher(other_teacher)}


@pytest.mark.parametrize(
    "case",
    ["not_admin", "not_teacher", "grade", "duplicate", "empty_name"],
)
def test_spec009_a_refused_group_creation_creates_nothing(repo, case):
    admin, teacher = _admin(repo), _approved_teacher(repo)
    name = "Grupo " + uuid.uuid4().hex[:6]
    actor, owner, grade = admin, teacher, 9
    if case == "not_admin":
        actor = teacher
    elif case == "not_teacher":
        owner = make_student(repo)
    elif case == "grade":
        grade = 12
    elif case == "duplicate":
        assert repo.create_group_for_teacher(admin, teacher, name, None, "Colegio A", 9)[0]
    elif case == "empty_name":
        name = "   "
    before = sql(repo, "SELECT COUNT(*) FROM groups")[0][0]

    ok, message, group_id = repo.create_group_for_teacher(
        actor, owner, name, None, institution="Colegio A", grade=grade
    )

    assert (ok, group_id) == (False, None) and message
    assert sql(repo, "SELECT COUNT(*) FROM groups")[0][0] == before
