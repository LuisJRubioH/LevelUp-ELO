"""
Spec 009 delivery I1: the import's rules without I/O (src/domain/student_import.py) — reading an
identification (FR-004, N16), the form's grade words (N20), the display name from one or two
columns (N19) and the preview's digest (FR-003). Invented identifications only.
"""

import pytest

from src.domain.student_import import (
    join_display_name,
    preview_digest,
    read_grade,
    read_identification,
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
