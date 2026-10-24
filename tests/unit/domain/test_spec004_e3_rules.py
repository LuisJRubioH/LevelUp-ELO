"""
Spec 004, delivery E3 — the level and grade of a student the admin creates (FR-040, P9), and the
last day of access in Colombian time (FR-046, FR-047, P7). No I/O.

[CHANGE] tests: the base branch has neither.
"""

from datetime import date, datetime, timezone

import pytest

from src.domain.identity import (
    ACCESS_EXPIRED_MESSAGE,
    access_expired,
    colombia_today,
    parse_last_day,
    student_level_problem,
)


@pytest.mark.parametrize(
    "level, grade",
    [("colegio", None), ("colegio", ""), ("universidad", None), ("concursos", None)]
    + [("semillero", g) for g in ("6", "7", "8", "9", "10", "11")]
    + [("semillero", 9)],
)
def test_spec004_a_level_with_its_grade_is_accepted(level, grade):
    """FR-040 (P9): semillero takes a grade from 6.º to 11.º; the other levels take «No aplica»."""
    assert student_level_problem(level, grade) is None


@pytest.mark.parametrize(
    "level, grade",
    [
        (None, None),
        ("", None),
        ("kinder", None),
        ("Colegio", None),
        ("semillero", None),
        ("semillero", "5"),
        ("semillero", "12"),
        ("colegio", "9"),
        ("universidad", "11"),
    ],
)
def test_spec004_a_level_and_grade_that_do_not_match_are_refused(level, grade):
    """FR-040, US6-AS3: a missing or unknown level, semillero without a valid grade, or a grade
    on a level that has none — refused with a reason, never corrected silently."""
    assert student_level_problem(level, grade)


def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def test_spec004_colombian_day_is_utc_minus_five_all_year():
    """FR-046: Colombia keeps UTC−5 with no daylight saving time."""
    assert colombia_today(_utc(2026, 10, 15, 4, 59)) == date(2026, 10, 14)
    assert colombia_today(_utc(2026, 10, 15, 5, 0)) == date(2026, 10, 15)
    assert colombia_today(_utc(2026, 3, 31, 4, 59)) == date(2026, 3, 30)


@pytest.mark.parametrize(
    "now, expired",
    [
        (_utc(2026, 10, 14, 5, 0), False),  # the last day itself, 00:00 in Colombia
        (_utc(2026, 10, 15, 4, 59, 59), False),  # 23:59:59 of the last day in Colombia
        (_utc(2026, 10, 15, 5, 0), True),  # the start of the next day
        (_utc(2027, 1, 1, 12, 0), True),
    ],
)
def test_spec004_the_last_day_is_inclusive(now, expired):
    """FR-047: access stops from the start of the day after the last day, Colombian time."""
    assert access_expired("2026-10-14", now) is expired
    assert access_expired(date(2026, 10, 14), now) is expired


def test_spec004_an_account_without_a_last_day_never_expires():
    """US7-AS7, FR-047."""
    assert access_expired(None, _utc(2099, 1, 1)) is False
    assert access_expired("", _utc(2099, 1, 1)) is False


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2026-12-31", date(2026, 12, 31)),
        (" 2026-12-31 ", date(2026, 12, 31)),
        (date(2026, 12, 31), date(2026, 12, 31)),
        (datetime(2026, 12, 31, 8, 0), date(2026, 12, 31)),
        (None, None),
        ("", None),
    ],
)
def test_spec004_a_last_day_is_read_as_a_calendar_date(value, expected):
    assert parse_last_day(value) == expected


@pytest.mark.parametrize("value", ["31/12/2026", "2026-02-30", "mañana", 20261231])
def test_spec004_a_last_day_that_is_not_a_date_is_refused(value):
    with pytest.raises(ValueError):
        parse_last_day(value)


def test_spec004_the_expiry_message_is_the_owners():
    """P7: the exact text the student sees."""
    assert ACCESS_EXPIRED_MESSAGE == (
        "El período de acceso de tu cuenta terminó. Tu progreso está guardado. "
        "Contacta al administrador si necesitas ampliar el acceso."
    )
