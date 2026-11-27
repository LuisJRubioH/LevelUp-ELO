"""Spec 006 AB (FR-062, FR-064, FR-065): the short answer's equivalences, the rubric, the vision
prompt and its reading, as pure rules."""

import json

import pytest

from src.domain.exams.open_answers import (
    CRITERIA,
    MAX_SCORE,
    answer_code,
    as_number,
    blank_levels,
    normalize_text,
    parse_rubric,
    rubric_prompt,
    score,
    short_answer_is_right,
    valid_levels,
)

LEVELS = {"comprension": 3, "estrategia": 2, "ejecucion": 2, "justificacion": 1}


# ── Short answers (FR-062) ────────────────────────────────────────────────────


@pytest.mark.parametrize("answer", ["5/2", "2,5", "2.5", " 5 / 2 ", "10/4", "+2,50"])
def test_numbers_of_equal_value_are_one_answer(answer):
    """FR-062: a decimal comma or point, or a fraction — compared by value."""
    assert short_answer_is_right(answer, ["5/2"])


@pytest.mark.parametrize(
    "answer, accepted",
    [
        ("Triángulo", ["triangulo"]),
        ("  NUEVE  ", ["nueve"]),
        ("número primo.", ["numero primo"]),
        ("-3", ["-3"]),
        ("-6/2", ["-3"]),
    ],
)
def test_case_accents_and_spaces_are_ignored(answer, accepted):
    assert short_answer_is_right(answer, accepted)


@pytest.mark.parametrize(
    "answer, accepted",
    [("3", ["5/2"]), ("", ["0"]), ("   ", ["x"]), ("2,51", ["2,5"]), ("cuadrado", ["triangulo"])],
)
def test_other_answers_are_wrong(answer, accepted):
    assert not short_answer_is_right(answer, accepted)


def test_what_counts_as_a_number():
    assert as_number("2,5") == as_number("5/2")
    assert as_number("1/0") is None
    assert as_number("dos") is None
    assert normalize_text(" Á b  C. ") == "abc"


# ── Procedures: the rubric and the vision prompt (FR-064, FR-065) ────────────


def test_the_prompt_names_the_code_and_never_a_person():
    """FR-064: the statement, the reference and the code go beside the photo; nothing of the
    student."""
    prompt = rubric_prompt(answer_code(42), "¿Cuánto es 2+2?", "4")

    assert "R-000042" in prompt
    assert "¿Cuánto es 2+2?" in prompt and "4" in prompt
    assert all(c in prompt for c in CRITERIA)


def test_a_reply_is_read_into_four_levels_and_a_comment():
    reply = "Aquí va: " + json.dumps({**LEVELS, "comentario": "Bien planteado."}) + " fin"

    assert parse_rubric(reply) == (LEVELS, "Bien planteado.")


@pytest.mark.parametrize(
    "reply",
    [
        None,
        "",
        "sin json",
        json.dumps({**LEVELS, "comprension": 4}),
        json.dumps({**LEVELS, "estrategia": -1}),
        json.dumps({**LEVELS, "ejecucion": 1.5}),
        json.dumps({**LEVELS, "justificacion": True}),
        json.dumps({k: v for k, v in LEVELS.items() if k != "estrategia"}),
        "[1, 2, 3]",
    ],
)
def test_an_unreadable_reply_is_none(reply):
    """FR-064: a missing criterion, a level outside 0–3 or no object leaves it to the teacher."""
    assert parse_rubric(reply) is None


def test_scores_and_blanks():
    assert score(LEVELS) == 8
    assert score(blank_levels()) == 0
    assert MAX_SCORE == 12


def test_a_teachers_levels_must_name_the_four_criteria():
    """FR-065."""
    assert valid_levels(LEVELS)
    assert not valid_levels({**LEVELS, "comprension": 4})
    assert not valid_levels({k: v for k, v in LEVELS.items() if k != "estrategia"})
    assert not valid_levels({**LEVELS, "extra": 1})
