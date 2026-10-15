"""
Spec 004, delivery E2 — the display name and its filter (FR-020, N17), and the name other people
see (FR-021, FR-022). No I/O.

[CHANGE] tests: the base branch has no display name.
"""

import pytest

from src.domain.identity import (
    DISPLAY_NAME_MAX_LENGTH,
    display_name_problem,
    normalize_display_name,
    public_name,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  Ana   María  Pérez ", "Ana María Pérez"),
        ("Jean-Luc\tO'Neil", "Jean-Luc O'Neil"),
        ("", None),
        ("   ", None),
        (None, None),
        (42, None),
    ],
)
def test_spec004_display_name_is_trimmed_and_its_spaces_collapsed(raw, expected):
    """FR-020: outer spaces go, inner runs of spaces become one; nothing left is no name."""
    assert normalize_display_name(raw) == expected


@pytest.mark.parametrize(
    "name",
    [
        "Ana María Pérez",
        "Jean-Luc O'Neil",
        "D’Angelo Rossi",  # typographic apostrophe
        "Søren Kierkegaard",
        "Zoë Ñúñez",
        "李明",  # two letters of another script
        "Mary-Kate Olsen-Smith",
        "Vergara",  # holds a refused word, but is not one
        "Morón",
        "Año Nuevo",
        "-".join(["Abcdefghi"] * 8),  # 79 characters: long names with hyphens are names
    ],
)
def test_spec004_names_of_any_language_with_hyphens_are_accepted(name):
    """FR-020 (N17): 2 to 80 letters of any language, spaces, apostrophes and hyphens."""
    assert display_name_problem(normalize_display_name(name)) is None


@pytest.mark.parametrize(
    "name",
    [None, "A", "x" * (DISPLAY_NAME_MAX_LENGTH + 1), "Ana2", "Ana_María", "Ana 🙂", "Ana.", "--"],
)
def test_spec004_names_out_of_the_format_are_refused(name):
    """FR-020: missing, shorter than 2 or longer than 80 characters, or with anything but letters,
    spaces, apostrophes and hyphens."""
    assert display_name_problem(normalize_display_name(name)) is not None


@pytest.mark.parametrize(
    "name",
    [
        "puta",
        "PUTA",
        "Pútá",  # accents do not hide a word
        "Hijo de puta",
        "Juan Hijueputa",
        "Malparido Gómez",
        "Gonorrea",
        "Coño",
        "Puuuuta",  # repeated letters do not hide it
        "p u t a",  # nor spaces between the letters
        "Pu-ta",
        "Fuck",
        "Fuuuuck You",
        "Bitch",
        "Mierda",
        "Elver Galarga",  # well-known mocking names
        "Rosa Melano",
        "Dolores Delano",
        "Mike Hunt",
        "Ben Dover",
    ],
)
def test_spec004_offensive_or_mocking_names_are_refused_in_spanish_and_english(name):
    """FR-020 (N17): an offensive or mocking word in Spanish or English, compared without accents
    or letter case, is refused."""
    problem = display_name_problem(normalize_display_name(name))
    assert problem is not None
    assert name.lower() not in problem.lower()  # the message never repeats the name


def test_spec004_the_name_others_see_is_the_display_name_else_the_username():
    """FR-021, FR-022 (N5): the display name; an account without one shows its username."""
    assert public_name("Ana María", "ana.m7") == "Ana María"
    assert public_name(None, "estudiante1") == "estudiante1"
    assert public_name("", "estudiante1") == "estudiante1"
