"""
Spec 009 delivery I1: the import's rules without I/O (src/domain/student_import.py) — reading an
identification (FR-004, N16), the form's grade words (N20), the display name from one or two
columns (N19), the preview's digest (FR-003) and its classification of every row (FR-002, FR-007,
FR-018, N21). Invented identifications only.
"""

import pytest

from src.domain.student_import import (
    classify_rows,
    file_pairs,
    join_display_name,
    preview_digest,
    read_grade,
    read_identification,
    suggest_pairing,
)

# ── Identification (FR-004, US1-AS4, N16) ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1012345678", "1012345678"),
        ("  1012345678 ", "1012345678"),  # only outer spaces are removed
        ("0012345", "0012345"),  # text keeps every digit as written
        (1012345678, "1012345678"),  # a numeric cell holding a whole number (N16)
        (1012345678.0, "1012345678"),
        (123456789012345, "123456789012345"),  # 15 digits: what a spreadsheet keeps
    ],
)
def test_spec009_an_identification_is_read_as_its_digits(raw, expected):
    assert read_identification(raw) == (expected, None)


@pytest.mark.parametrize(
    "raw, reason",
    [
        (None, "identification_missing"),
        ("", "identification_missing"),
        ("   ", "identification_missing"),
        ("10.123.456", "identification_not_digits"),
        ("10-123-456", "identification_not_digits"),
        ("10 123 456", "identification_not_digits"),
        ("AB123456", "identification_not_digits"),
        ("１２３４５", "identification_not_digits"),  # full-width digits are not ASCII digits
        ("1,2E+09", "identification_altered"),  # scientific notation typed back as text
        ("1.23457E+11", "identification_altered"),
        (1012345678.5, "identification_altered"),  # a decimal in a numeric cell
        (1234567890123456, "identification_altered"),  # more digits than a spreadsheet keeps
        (1.2e15, "identification_altered"),
        (-123456, "identification_not_digits"),
        (True, "identification_not_digits"),
    ],
)
def test_spec009_any_other_identification_is_refused_and_never_rebuilt(raw, reason):
    assert read_identification(raw) == (None, reason)


# ── Grade from the form's words (N20, P9) ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw, grade",
    [
        ("Sexto", 6),
        ("Séptimo", 7),
        ("septimo", 7),
        ("OCTAVO", 8),
        (" Noveno ", 9),
        ("Décimo", 10),
        ("Undécimo", 11),
        ("undecimo", 11),
    ],
)
def test_spec009_the_forms_grade_words_read_as_six_to_eleven(raw, grade):
    assert read_grade(raw) == (grade, None)


@pytest.mark.parametrize(
    "raw, reason",
    [
        (None, "grade_missing"),
        ("", "grade_missing"),
        ("6", "grade_unknown"),  # never guessed: only the form's words
        ("6.º", "grade_unknown"),
        ("Quinto", "grade_unknown"),
        ("Duodécimo", "grade_unknown"),
        ("Sexto grado", "grade_unknown"),
        (6, "grade_unknown"),
    ],
)
def test_spec009_any_other_grade_is_an_error_never_guessed(raw, reason):
    assert read_grade(raw) == (None, reason)


# ── Display name from one or two columns (N19, US1-AS10) ─────────────────────────────────────────


def test_spec009_two_name_columns_join_with_one_space_in_the_order_chosen():
    assert join_display_name(["  Ana  María ", "Pérez Gómez"]) == "Ana María Pérez Gómez"
    assert join_display_name(["Pérez Gómez", "Ana María"]) == "Pérez Gómez Ana María"
    assert join_display_name(["Ana María Pérez"]) == "Ana María Pérez"


def test_spec009_an_empty_part_is_left_out_and_nothing_gives_no_name():
    assert join_display_name(["Ana", ""]) == "Ana"
    assert join_display_name([None, "Pérez"]) == "Pérez"
    assert join_display_name(["", "  "]) is None
    assert join_display_name([None, None]) is None


# ── The preview's digest (FR-003) ────────────────────────────────────────────────────────────────

FILE = b"documento;nombres\n1012345678;Ana\n"
MAPPING = {"identification": "documento", "name": ["nombres"]}
BATCH = {"level": "semillero", "access_until": "2027-12-15"}
STATUSES = [{"row": 2, "status": "new"}]


def test_spec009_the_digest_is_stable_for_the_same_preview():
    first = preview_digest(FILE, MAPPING, BATCH, STATUSES)
    again = preview_digest(
        FILE,
        {"name": ["nombres"], "identification": "documento"},  # same mapping, other key order
        {"access_until": "2027-12-15", "level": "semillero"},
        [{"status": "new", "row": 2}],
    )
    assert first == again
    assert len(first) == 64


@pytest.mark.parametrize(
    "change",
    [
        {"file": FILE + b"1098765432;Luis\n"},
        {"mapping": {"identification": "documento", "name": ["nombres", "apellidos"]}},
        {"batch": {"level": "semillero", "access_until": "2027-12-16"}},
        {"statuses": [{"row": 2, "status": "existing"}]},
    ],
)
def test_spec009_the_digest_changes_with_the_file_mapping_batch_or_any_status(change):
    base = preview_digest(FILE, MAPPING, BATCH, STATUSES)
    changed = preview_digest(
        change.get("file", FILE),
        change.get("mapping", MAPPING),
        change.get("batch", BATCH),
        change.get("statuses", STATUSES),
    )
    assert changed != base


# ── The preview's classification (FR-002, FR-007, FR-018, N21, US1-AS1, US1-AS10) ────────────────

MAP = {
    "identification": "Número de documento",
    "name": ["Nombres", "Apellidos"],
    "grade": "Grado",
    "institution": "Institución",
    "recovery_email": "Correo",
}
SEMILLERO = {"level": "semillero", "grade": None, "access_until": "2027-12-15"}
PAIRING = {("IE San José", 7): 41, ("IE San José", 8): 42, ("Colegio Central", 7): 51}


def _row(number, doc, first="Ana", last="Pérez", grade="Séptimo", school="IE San José", mail=""):
    return (
        number,
        {
            "Número de documento": doc,
            "Nombres": first,
            "Apellidos": last,
            "Grado": grade,
            "Institución": school,
            "Correo": mail,
        },
    )


def _classify(rows, linked=None, usernames=(), batch=SEMILLERO, mapping=MAP):
    return classify_rows(rows, mapping, batch, PAIRING, linked or {}, set(usernames))


def test_spec009_a_valid_unknown_row_is_new_with_its_level_grade_and_group():
    [row] = _classify([_row(2, "1012345678", mail="familia@example.org")])

    assert row["status"] == "new" and row["reasons"] == []
    assert (row["identification"], row["display_name"]) == ("1012345678", "Ana Pérez")
    assert (row["level"], row["grade"], row["group_id"]) == ("semillero", 7, 41)
    assert row["recovery_email"] == "familia@example.org"


def test_spec009_the_group_comes_from_the_rows_institution_and_grade():
    """N21: one group per institution and grade; a pair with no group — «Otro» included — is an
    error to correct before confirming."""
    rows = _classify(
        [
            _row(2, "1000000001", grade="Octavo"),
            _row(3, "1000000002", school="Colegio Central"),
            _row(4, "1000000003", school="Otro"),
            _row(5, "1000000004", school="Colegio Central", grade="Noveno"),
        ]
    )
    assert [(r["status"], r["group_id"], r["reasons"]) for r in rows] == [
        ("new", 42, []),
        ("new", 51, []),
        ("error", None, ["group_missing"]),
        ("error", None, ["group_missing"]),
    ]


def test_spec009_a_linked_identification_is_existing_with_the_differences_to_confirm():
    """FR-006, FR-008: an existing account is matched only by its linked identification; a
    different group or last day is shown as a change, never applied by the preview."""
    linked = {
        "1000000001": {"user_id": 7, "group_id": 41, "access_until": "2027-12-15"},
        "1000000002": {"user_id": 8, "group_id": 51, "access_until": None},
    }
    same, moved = _classify([_row(2, "1000000001"), _row(3, "1000000002")], linked)

    assert (same["status"], same["account_id"], same["changes"]) == ("existing", 7, {})
    assert (moved["status"], moved["account_id"]) == ("existing", 8)
    assert moved["changes"] == {
        "group_id": {"from": 51, "to": 41},
        "access_until": {"from": None, "to": "2027-12-15"},
    }


def test_spec009_the_second_occurrence_of_an_identification_is_a_duplicate():
    rows = _classify([_row(2, "1000000001"), _row(3, " 1000000001 ", first="Otra")])
    assert [(r["row"], r["status"]) for r in rows] == [(2, "new"), (3, "duplicate")]


@pytest.mark.parametrize(
    "row, reason",
    [
        (_row(2, "10.000.001"), "identification_not_digits"),
        (_row(2, ""), "identification_missing"),
        (_row(2, "1000000001", first="", last=""), "name_missing"),
        (_row(2, "1000000001", first="Rosa", last="Melano"), "name_refused"),  # spec 004 FR-020
        (_row(2, "1000000001", grade="Quinto"), "grade_unknown"),
        (_row(2, "1000000001", mail="no es un correo"), "email_invalid"),
    ],
)
def test_spec009_a_row_with_a_problem_is_an_error_with_its_reason(row, reason):
    [result] = _classify([row])
    assert result["status"] == "error"
    assert reason in result["reasons"]


def test_spec009_an_identification_that_is_another_accounts_username_is_an_error():
    """FR-007: never merged, never renamed — the admin links it explicitly or corrects it."""
    [result] = _classify([_row(2, "1000000001")], usernames={"1000000001"})
    assert (result["status"], result["reasons"]) == ("error", ["identification_is_username"])


def test_spec009_the_batch_level_must_go_with_the_grade():
    """P9: a level other than semillero takes no grade, so a grade column is a mismatch."""
    colegio = {"level": "colegio", "grade": None, "access_until": "2027-12-15"}
    [result] = _classify([_row(2, "1000000001")], batch=colegio)
    assert (result["status"], result["reasons"]) == ("error", ["level_grade"])


def test_spec009_the_same_recovery_email_on_several_rows_is_allowed():
    rows = _classify(
        [
            _row(2, "1000000001", mail="casa@example.org"),
            _row(3, "1000000002", mail="casa@example.org"),
        ]
    )
    assert [r["status"] for r in rows] == ["new", "new"]


def test_spec009_an_unmapped_recovery_email_leaves_it_empty():
    mapping = {key: value for key, value in MAP.items() if key != "recovery_email"}
    [result] = _classify([_row(2, "1000000001", mail="casa@example.org")], mapping=mapping)
    assert (result["status"], result["recovery_email"]) == ("new", None)


# ── An existing account's recovery e-mail (FR-018, N27) ──────────────────────────────────────────


def test_spec009_an_existing_accounts_different_recovery_email_is_a_change_to_confirm():
    """N27: like the group and the last day (FR-008), shown in the preview and applied only when
    the admin confirms it for that account; an empty cell proposes nothing."""
    account = {"group_id": 41, "access_until": "2027-12-15", "recovery_email": "vieja@example.org"}
    linked = {
        "1000000001": {"user_id": 7, **account},
        "1000000002": {"user_id": 8, **account},
        "1000000003": {"user_id": 9, **account},
    }
    rows = _classify(
        [
            _row(2, "1000000001", mail="nueva@example.org"),
            _row(3, "1000000002", mail="vieja@example.org"),
            _row(4, "1000000003", mail=""),
        ],
        linked,
    )
    assert [r["changes"] for r in rows] == [
        {"recovery_email": {"from": "vieja@example.org", "to": "nueva@example.org"}},
        {},
        {},
    ]


# ── Pairing each (institution, grade) with its group (N21, N26) ──────────────────────────────────


def test_spec009_the_files_pairs_are_listed_once_in_the_order_they_appear():
    rows = [
        _row(2, "1", grade="Séptimo"),
        _row(3, "2", grade="Octavo"),
        _row(4, "3", grade="Séptimo"),
        _row(5, "4", grade="Quinto"),  # a grade that does not read is no pair
        _row(6, "5", school="Otro"),
    ]
    assert file_pairs(rows, MAP, SEMILLERO) == [
        ("IE San José", 7),
        ("IE San José", 8),
        ("Otro", 7),
    ]


def test_spec009_a_pair_is_suggested_the_group_with_that_institution_and_grade():
    """N26 (a): the group records its institution and grade; the suggestion ignores case, accents
    and outer spaces, is never made for «Otro» or for two groups that match, and the admin can
    change every pairing before the preview."""
    groups = [
        {"group_id": 41, "institution": "IE San José", "grade": 7},
        {"group_id": 42, "institution": " ie san jose", "grade": 8},
        {"group_id": 51, "institution": "Colegio Central", "grade": 7},
        {"group_id": 52, "institution": "Colegio Central", "grade": 7},
        {"group_id": 60, "institution": None, "grade": None},
    ]
    pairs = [
        ("IE San José", 7),
        ("IE SAN JOSÉ", 8),
        ("Colegio Central", 7),
        ("Otro", 7),
        ("IE San José", 9),
    ]
    assert suggest_pairing(pairs, groups) == {("IE San José", 7): 41, ("IE SAN JOSÉ", 8): 42}


# ── Header suggestions for the mapping (T024) ────────────────────────────────────────────────


def test_spec009_the_forms_headers_suggest_the_mapping():
    from src.domain.student_import import suggest_mapping

    header = [
        "Marca temporal",
        "Tipo de documento",
        " NÚMERO DE DOCUMENTO ",
        "Nombres",
        "Apellidos",
        "Grado que cursas en 2027",
        "Institución educativa",
        "Sede",
        "Correo electrónico de contacto",
        "Nombre del acudiente",
    ]

    assert suggest_mapping(header) == {
        "identification": " NÚMERO DE DOCUMENTO ",
        "name": ["Nombres", "Apellidos"],
        "grade": "Grado que cursas en 2027",
        "institution": "Institución educativa",
        "recovery_email": "Correo electrónico de contacto",
    }


def test_spec009_headers_the_form_does_not_have_suggest_nothing():
    from src.domain.student_import import suggest_mapping

    assert suggest_mapping(["Documento", "Nombre completo", "Sede"]) == {}
    assert suggest_mapping(["Apellidos", "Nombres"]) == {"name": ["Nombres", "Apellidos"]}
