"""Spec 006 AB (FR-063, FR-064): the rubric, the AI's prompt and its reading, as pure rules."""

import json

import pytest

from src.domain.exams.open_answers import (
    CRITERIA,
    MAX_SCORE,
    answer_code,
    blank_levels,
    is_blank,
    parse_rubric,
    rubric_prompt,
    score,
    valid_levels,
)

LEVELS = {"comprension": 3, "estrategia": 2, "ejecucion": 2, "justificacion": 1}


def test_the_prompt_names_the_code_and_never_a_person():
    """FR-063: the statement, the reference, the answer and the code; nothing else of the student."""
    prompt = rubric_prompt(answer_code(42), "¿Cuánto es 2+2?", "4", "Creo que 4")

    assert "R-000042" in prompt
    assert "¿Cuánto es 2+2?" in prompt and "Creo que 4" in prompt
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
    """FR-063: a missing criterion, a level outside 0–3 or no object leaves it to the teacher."""
    assert parse_rubric(reply) is None


def test_scores_and_blanks():
    assert score(LEVELS) == 8
    assert score(blank_levels()) == 0
    assert MAX_SCORE == 12
    assert is_blank("   \n ") and is_blank(None) and not is_blank("x")


def test_a_teachers_levels_must_name_the_four_criteria():
    """FR-064."""
    assert valid_levels(LEVELS)
    assert not valid_levels({**LEVELS, "comprension": 4})
    assert not valid_levels({k: v for k, v in LEVELS.items() if k != "estrategia"})
    assert not valid_levels({**LEVELS, "extra": 1})
