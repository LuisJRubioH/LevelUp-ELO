"""
Spec 009 delivery I1 — the import through the API, on both engines (plan-i1.md § API; tasks T012 …
T016, T018, T041 … T044): columns → preview → confirmation → state; the same file again; changes to
existing accounts confirmed one by one; a confirmation whose preview changed; only the admin; no
identification or name in the logs; linking and unlinking; the groups the admin creates; and the
student's own identification in `/me`.

[CHANGE] tests: the base branch has no import. Invented identifications only (the repository is
public).
"""

import io
import json
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.identity import colombia_today
from tests.integration.conftest import (
    headers_for,
    make_course,
    make_group,
    make_student,
    make_teacher,
    set_rating,
    sql,
)

HEADER = [
    "Marca temporal",
    "Tipo de documento",
    "Número de documento",
    "Nombres",
    "Apellidos",
    "Grado que cursas en 2027",
    "Institución educativa",
    "Sede",
    "Correo electrónico de contacto",
    "Nombre del acudiente",
    "Celular del acudiente",
]
MAPPING = {
    "identification": "Número de documento",
    "name": ["Nombres", "Apellidos"],
    "grade": "Grado que cursas en 2027",
    "institution": "Institución educativa",
    "recovery_email": "Correo electrónico de contacto",
}
GUARDIAN_PHONE = "3157654321"
# Display names take letters only (spec 004 FR-020): one invented surname per row.
SURNAMES = (
    "Pérez Gómez Rodríguez López Martínez García Sánchez Ramírez Torres Flórez Rojas Vargas Moreno"
    " Jiménez Díaz Castro Ortiz Rubio Herrera Medina Aguilar Suárez Mejía Cárdenas Ríos Osorio"
    " Muñoz Restrepo Zapata Cardona"
).split()


def _admin(repo) -> int:
    admin = make_teacher(repo)
    sql(repo, "UPDATE users SET role = 'admin', approved = 1, active = 1 WHERE id = ?", (admin,))
    return admin


def _approved_teacher(repo) -> int:
    teacher = make_teacher(repo)
    sql(repo, "UPDATE users SET approved = 1 WHERE id = ?", (teacher,))
    return teacher


def _day(offset: int) -> str:
    return (colombia_today(datetime.now(timezone.utc)) + timedelta(days=offset)).isoformat()


def _identification() -> str:
    return "77" + str(uuid.uuid4().int)[:8]


def _institution() -> str:
    """A school name unique per test, so PostgreSQL's earlier groups never pair with it."""
    return "Colegio Prueba " + uuid.uuid4().hex[:6]


def _student_row(identification, first, last, grade, institution, email=""):
    return [
        "2026/10/18 9:00:00",
        "Tarjeta de identidad",
        identification,
        first,
        last,
        grade,
        institution,
        "Sede principal",
        email,
        "Acudiente Inventado",
        GUARDIAN_PHONE,
    ]


def _csv(rows) -> bytes:
    import csv

    buffer = io.StringIO()
    csv.writer(buffer).writerows([HEADER] + rows)
    return buffer.getvalue().encode("utf-8")


class _Setup:
    """An admin, a course and two groups — 9.º and 10.º of one invented school."""

    def __init__(self, repo):
        self.repo = repo
        self.admin = _admin(repo)
        self.teacher = _approved_teacher(repo)
        self.course_id, _ = make_course(repo, ["Fracciones"], items_per_topic=2)
        self.institution = _institution()
        self.group9 = make_group(repo, self.teacher, self.course_id)
        self.group10 = make_group(repo, self.teacher, self.course_id)
        self.headers = headers_for(repo, self.admin)

    def students(self, count, grade="Noveno"):
        return [
            _student_row(_identification(), "Ana", SURNAMES[n], grade, self.institution)
            for n in range(count)
        ]

    def form(self, data, batch=None, pairing=None, mapping=None, **extra):
        pairing = (
            pairing
            if pairing is not None
            else [
                {"institution": self.institution, "grade": 9, "group_id": self.group9},
                {"institution": self.institution, "grade": 10, "group_id": self.group10},
            ]
        )
        fields = {
            "mapping": json.dumps(mapping or MAPPING),
            "batch": json.dumps(batch or {"level": "semillero", "access_until": _day(60)}),
            "pairing": json.dumps(pairing),
        }
        fields.update({k: v if isinstance(v, str) else json.dumps(v) for k, v in extra.items()})
        return {"files": {"file": ("respuestas.csv", data, "text/csv")}, "data": fields}


def _wait(client, headers, import_id, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        record = client.get(f"/api/admin/imports/{import_id}", headers=headers).json()
        if record["state"] != "running":
            return record
        time.sleep(0.2)
    raise AssertionError("the import did not finish")


def _import(client, setup, data, confirm=(), **form):
    preview = client.post(
        "/api/admin/imports/preview", headers=setup.headers, **setup.form(data, **form)
    )
    assert preview.status_code == 200, preview.text
    body = preview.json()
    confirmed = client.post(
        "/api/admin/imports",
        headers=setup.headers,
        **setup.form(data, digest=body["digest"], confirm=list(confirm), **form),
    )
    assert confirmed.status_code == 202, confirmed.text
    return body, _wait(client, setup.headers, confirmed.json()["import_id"])


def _imports_of(repo, admin) -> int:
    return sql(repo, "SELECT COUNT(*) FROM student_imports WHERE admin_id = ?", (admin,))[0][0]


def _account(repo, username):
    rows = sql(
        repo,
        "SELECT id, password_hash, group_id, access_until, recovery_email FROM users"
        " WHERE username = ?",
        (username,),
    )
    return tuple(rows[0]) if rows else None


# ── Columns, preview, confirmation, state (T012, US1-AS1, US1-AS2, FR-016) ──────────────────


def test_spec009_columns_then_preview_then_confirm_creates_the_new_rows(repo, client):
    setup = _Setup(repo)
    rows = setup.students(28) + setup.students(2, grade="Décimo")
    rows[3][3:5] = ["", ""]  # no name: an error
    rows.append(list(rows[0]))  # the same identification again: a duplicate
    data = _csv(rows)

    columns = client.post(
        "/api/admin/imports/columns",
        headers=setup.headers,
        files={"file": ("respuestas.csv", data, "text/csv")},
    )
    assert columns.status_code == 200, columns.text
    assert columns.json()["header"] == HEADER
    assert len(columns.json()["examples"]) == 5
    assert columns.json()["suggested"] == MAPPING  # T024: the form's headers suggest the mapping
    assert _imports_of(repo, setup.admin) == 0

    preview = client.post("/api/admin/imports/preview", headers=setup.headers, **setup.form(data))

    assert preview.status_code == 200, preview.text
    body = preview.json()
    assert body["counts"] == {"new": 29, "existing": 0, "duplicate": 1, "error": 1}
    by_row = {r["row"]: r for r in body["rows"]}
    assert by_row[2]["status"] == "new" and by_row[2]["display_name"] == "Ana Pérez"
    assert (by_row[2]["level"], by_row[2]["grade"], by_row[2]["group_id"]) == (
        "semillero",
        9,
        setup.group9,
    )
    assert by_row[30]["group_id"] == setup.group10
    assert by_row[5]["status"] == "error" and by_row[5]["reasons"] == ["name_missing"]
    assert by_row[32]["status"] == "duplicate"
    # Nothing saved by the preview, and the form's other columns never reach it (FR-016).
    assert _account(repo, rows[0][2]) is None
    assert GUARDIAN_PHONE not in preview.text and "Tarjeta de identidad" not in preview.text

    confirmed = client.post(
        "/api/admin/imports", headers=setup.headers, **setup.form(data, digest=body["digest"])
    )

    assert confirmed.status_code == 202, confirmed.text
    record = _wait(client, setup.headers, confirmed.json()["import_id"])
    assert record["state"] == "finished"
    assert record["counts"]["created"] == 29 and record["counts"]["error"] == 1
    assert record["counts"]["duplicate"] == 1
    created = _account(repo, rows[0][2])
    assert created is not None and created[2] == setup.group9
    login = client.post("/api/auth/login", json={"username": rows[0][2], "password": rows[0][2]})
    assert login.status_code == 200, login.text
    assert login.json().get("must_change_password") in (False, None)
    listed = client.get("/api/admin/imports", headers=setup.headers).json()["imports"]
    assert listed[0]["import_id"] == record["import_id"]
    stored = repr(
        [
            tuple(r)
            for r in sql(
                repo,
                "SELECT * FROM student_import_rows WHERE import_id = ?",
                (record["import_id"],),
            )
        ]
    )
    assert rows[0][2] not in stored and GUARDIAN_PHONE not in stored


def test_spec009_an_unusable_file_or_choice_is_refused_with_its_reason(repo, client):
    setup = _Setup(repo)
    data = _csv(setup.students(2))

    too_big = client.post(
        "/api/admin/imports/columns",
        headers=setup.headers,
        files={"file": ("r.csv", b"x" * (5 * 1024 * 1024 + 1), "text/csv")},
    )
    wrong_format = client.post(
        "/api/admin/imports/columns",
        headers=setup.headers,
        files={"file": ("r.txt", data, "text/plain")},
    )
    unknown_column = client.post(
        "/api/admin/imports/preview",
        headers=setup.headers,
        **setup.form(data, mapping={**MAPPING, "identification": "Cédula"}),
    )
    past_day = client.post(
        "/api/admin/imports/preview",
        headers=setup.headers,
        **setup.form(data, batch={"level": "semillero", "access_until": _day(-1)}),
    )

    assert too_big.status_code == 413
    assert wrong_format.status_code == 400 and ".xlsx" in wrong_format.json()["detail"]
    assert unknown_column.status_code == 400
    assert past_day.status_code == 400 and "pasó" in past_day.json()["detail"]


# ── The same file again (T013, US1-AS3, FR-006, SC-001) ───────────────────────────────────────


def test_spec009_the_same_file_again_creates_and_changes_nothing(repo, client):
    setup = _Setup(repo)
    rows = setup.students(3)
    data = _csv(rows)
    _import(client, setup, data)
    before = [_account(repo, r[2]) for r in rows]
    set_rating(repo, before[0][0], setup.course_id, "Fracciones", 1234.0)

    preview, record = _import(client, setup, data)

    assert preview["counts"] == {"new": 0, "existing": 3, "duplicate": 0, "error": 0}
    assert all(r["changes"] == {} for r in preview["rows"])
    assert record["counts"]["created"] == 0 and record["counts"]["unchanged"] == 3
    assert [_account(repo, r[2]) for r in rows] == before
    rating = sql(
        repo,
        "SELECT current_elo FROM student_course_topic_elo WHERE user_id = ? AND course_id = ?",
        (before[0][0], setup.course_id),
    )
    assert float(rating[0][0]) == 1234.0


# ── Changes to existing accounts, one by one (T014, T041, US1-AS6, FR-008, N27) ──────────────


def test_spec009_changes_to_existing_accounts_apply_only_when_confirmed(repo, client):
    setup = _Setup(repo)
    rows = setup.students(3)
    _import(client, setup, _csv(rows))
    before = [_account(repo, r[2]) for r in rows]
    # The file now says 10.º for every row, another last day and, for the third, an e-mail.
    changed = [list(r) for r in rows]
    for row in changed:
        row[5] = "Décimo"
    changed[2][8] = "familia@example.com"
    data = _csv(changed)
    batch = {"level": "semillero", "access_until": _day(90)}

    preview, record = _import(
        client,
        setup,
        data,
        batch=batch,
        confirm=[
            {"row": 2, "changes": ["group_id"]},
            {"row": 4, "changes": ["recovery_email"]},
        ],
    )

    assert preview["counts"]["existing"] == 3
    assert set(preview["rows"][0]["changes"]) == {"group_id", "access_until"}
    assert set(preview["rows"][2]["changes"]) == {"group_id", "access_until", "recovery_email"}
    after = [_account(repo, r[2]) for r in rows]
    assert after[0][2] == setup.group10 and after[0][3] == before[0][3]  # only the group
    assert after[1] == before[1]  # nothing confirmed: nothing changed
    assert after[2][4] == "familia@example.com" and after[2][2] == before[2][2]
    assert after[0][1] == before[0][1]  # no password changes, ever
    assert record["counts"]["updated"] == 2 and record["counts"]["unchanged"] == 1
    audit = sql(
        repo,
        "SELECT student_id, admin_id FROM audit_group_changes WHERE student_id = ?",
        (before[0][0],),
    )
    assert [tuple(a) for a in audit] == [(before[0][0], setup.admin)]


def test_spec009_a_confirmed_change_the_preview_did_not_show_is_refused(repo, client):
    setup = _Setup(repo)
    rows = setup.students(1)
    _import(client, setup, _csv(rows))
    data = _csv(rows)
    preview = client.post("/api/admin/imports/preview", headers=setup.headers, **setup.form(data))

    confirmed = client.post(
        "/api/admin/imports",
        headers=setup.headers,
        **setup.form(
            data,
            digest=preview.json()["digest"],
            confirm=[{"row": 2, "changes": ["group_id"]}],
        ),
    )

    assert confirmed.status_code == 400


# ── A confirmation whose preview changed (T015, FR-003) ───────────────────────────────────────


@pytest.mark.parametrize("change", ["file", "batch", "pairing", "status"])
def test_spec009_a_confirmation_whose_preview_changed_is_refused(repo, client, change):
    setup = _Setup(repo)
    rows = setup.students(2)
    data = _csv(rows)
    preview = client.post("/api/admin/imports/preview", headers=setup.headers, **setup.form(data))
    digest = preview.json()["digest"]
    form = {}
    if change == "file":
        data = _csv(rows + setup.students(1))
    elif change == "batch":
        form["batch"] = {"level": "semillero", "access_until": _day(61)}
    elif change == "pairing":
        form["pairing"] = [
            {"institution": setup.institution, "grade": 9, "group_id": setup.group10}
        ]
    else:  # someone links one of the identifications meanwhile
        assert repo.link_identification(setup.admin, make_student(repo), rows[0][2])[0]

    confirmed = client.post(
        "/api/admin/imports", headers=setup.headers, **setup.form(data, digest=digest, **form)
    )

    assert confirmed.status_code == 409
    assert "vista previa" in confirmed.json()["detail"]
    assert _imports_of(repo, setup.admin) == 0


def test_spec009_a_retried_confirmation_returns_the_first_import(repo, client):
    """FR-010, US1-AS8: the same confirmation twice is one import; another while one runs is
    refused."""
    setup = _Setup(repo)
    data = _csv(setup.students(2))
    preview = client.post("/api/admin/imports/preview", headers=setup.headers, **setup.form(data))
    digest = preview.json()["digest"]

    first = client.post(
        "/api/admin/imports", headers=setup.headers, **setup.form(data, digest=digest)
    )
    again = client.post(
        "/api/admin/imports", headers=setup.headers, **setup.form(data, digest=digest)
    )

    assert first.status_code == 202 and again.status_code == 202
    assert again.json()["import_id"] == first.json()["import_id"]
    _wait(client, setup.headers, first.json()["import_id"])
    assert _imports_of(repo, setup.admin) == 1
    _, record = repo.start_import(setup.admin, "another-confirmation", 1)
    other = _csv(setup.students(1))
    other_preview = client.post(
        "/api/admin/imports/preview", headers=setup.headers, **setup.form(other)
    )
    busy = client.post(
        "/api/admin/imports",
        headers=setup.headers,
        **setup.form(other, digest=other_preview.json()["digest"]),
    )
    assert busy.status_code == 409 and "en curso" in busy.json()["detail"]
    assert repo.finish_import(record["import_id"])


# ── Only the admin (T016, US1-AS9, FR-012) ────────────────────────────────────────────────────


def test_spec009_a_student_or_a_teacher_is_refused_on_every_import_endpoint(repo, client):
    setup = _Setup(repo)
    data = _csv(setup.students(1))
    student = make_student(repo)
    for user_id in (student, setup.teacher):
        headers = headers_for(repo, user_id)
        files = {"file": ("r.csv", data, "text/csv")}
        responses = [
            client.post("/api/admin/imports/columns", headers=headers, files=files),
            client.post("/api/admin/imports/preview", headers=headers, **setup.form(data)),
            client.post("/api/admin/imports", headers=headers, **setup.form(data, digest="0" * 64)),
            client.get("/api/admin/imports", headers=headers),
            client.get("/api/admin/imports/whatever", headers=headers),
            client.put(
                f"/api/admin/users/{student}/identification",
                headers=headers,
                json={"identification": _identification()},
            ),
            client.delete(f"/api/admin/users/{student}/identification", headers=headers),
            client.post(
                f"/api/admin/teachers/{setup.teacher}/groups",
                headers=headers,
                json={"name": "Grupo", "institution": setup.institution, "grade": 9},
            ),
        ]
        assert [r.status_code for r in responses] == [403] * len(responses)
    assert (
        sql(repo, "SELECT COUNT(*) FROM student_identifications WHERE user_id = ?", (student,))[0][
            0
        ]
        == 0
    )


# ── No identification or name in the logs (T018, FR-011) ─────────────────────────────────────


def test_spec009_the_import_writes_no_identification_or_name_to_the_logs(repo, client, caplog):
    setup = _Setup(repo)
    rows = setup.students(2)
    rows[1][3:5] = ["Elver", "Galarga"]  # a refused name, an error row
    caplog.set_level(logging.DEBUG)

    _import(client, setup, _csv(rows))

    logged = caplog.text
    for secret in (rows[0][2], rows[1][2], "Pérez", "Galarga", GUARDIAN_PHONE):
        assert secret not in logged


# ── Linking, unlinking, groups and `/me` (T010, T039, T042, T044, US2-AS1, US3-AS2) ──────────


def test_spec009_the_admin_links_and_unlinks_an_identification(repo, client):
    setup = _Setup(repo)
    student, identification = make_student(repo), _identification()

    linked = client.put(
        f"/api/admin/users/{student}/identification",
        headers=setup.headers,
        json={"identification": identification},
    )
    refused = client.put(
        f"/api/admin/users/{student}/identification",
        headers=setup.headers,
        json={"identification": "12.345"},
    )

    assert linked.status_code == 200, linked.text
    assert refused.status_code == 400
    users = {
        u["id"]: u for u in client.get("/api/admin/users", headers=setup.headers).json()["users"]
    }
    assert users[student]["identification"] == identification
    me = client.get("/api/auth/me", headers=headers_for(repo, student)).json()
    assert me["identification"] == identification and me["display_name_locked"] is False
    removed = client.delete(f"/api/admin/users/{student}/identification", headers=setup.headers)
    assert removed.status_code == 204
    again = client.delete(f"/api/admin/users/{student}/identification", headers=setup.headers)
    assert again.status_code == 400
    assert (
        client.get("/api/auth/me", headers=headers_for(repo, student)).json()["identification"]
        is None
    )


def test_spec009_an_imported_student_sees_the_identification_and_cannot_rename(repo, client):
    setup = _Setup(repo)
    rows = setup.students(1)
    _import(client, setup, _csv(rows))
    user_id = _account(repo, rows[0][2])[0]
    headers = headers_for(repo, user_id)

    me = client.get("/api/auth/me", headers=headers).json()
    renamed = client.put(
        "/api/student/display-name", headers=headers, json={"display_name": "Otro"}
    )

    assert me["identification"] == rows[0][2] and me["display_name_locked"] is True
    assert renamed.status_code == 400
    assert client.get("/api/auth/me", headers=headers).json()["display_name"] == "Ana Pérez"
    by_admin = client.put(
        f"/api/admin/users/{user_id}/display-name",
        headers=setup.headers,
        json={"display_name": "Ana María Pérez"},
    )
    assert by_admin.status_code == 200


def test_spec009_the_admin_creates_a_group_for_a_teacher_and_it_pairs(repo, client):
    setup = _Setup(repo)
    institution = _institution()

    created = client.post(
        f"/api/admin/teachers/{setup.teacher}/groups",
        headers=setup.headers,
        json={
            "name": "Semillero 9 " + uuid.uuid4().hex[:6],
            "course_id": setup.course_id,
            "institution": institution,
            "grade": 9,
        },
    )
    refused = client.post(
        f"/api/admin/teachers/{setup.teacher}/groups",
        headers=setup.headers,
        json={"name": "Grupo 12", "institution": institution, "grade": 12},
    )

    assert created.status_code == 201, created.text
    assert refused.status_code == 400
    group_id = created.json()["group_id"]
    teacher_groups = client.get("/api/teacher/groups", headers=headers_for(repo, setup.teacher))
    assert group_id in {g["group_id"] for g in teacher_groups.json()}
    # N26 (a): the file's (institution, grade) pair is suggested with that group.
    rows = [_student_row(_identification(), "Luis", "Gómez", "noveno ", institution.upper())]
    preview = client.post(
        "/api/admin/imports/preview",
        headers=setup.headers,
        **setup.form(_csv(rows), pairing=[]),
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["pairs"] == [
        {
            "institution": institution.upper(),
            "grade": 9,
            "group_id": group_id,
            "suggested_group_id": group_id,
        }
    ]
    assert preview.json()["rows"][0]["group_id"] == group_id
