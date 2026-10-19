"""
Spec 006 delivery X2 (FR-033): a template's results from the stored responses.

Only the teacher's students count, each one's first submission only; the results are given per
student and per item, with the option each student chose. Pure domain.
"""

from src.domain.exams.results import template_results


def _row(session, user, item, correct, option, at, topic="t", content=None):
    return {
        "session_id": session,
        "user_id": user,
        "submitted_at": at,
        "score_pct": None,
        "item_id": item,
        "topic": topic,
        "content": content or item,
        "is_correct": correct,
        "selected_option": option,
    }


ROWS = [
    # student 1: first try (session 10) 1/2, retake (session 11) 2/2
    _row(10, 1, "a", True, "A", "2026-10-19 10:00:00", "álgebra"),
    _row(10, 1, "b", False, "C", "2026-10-19 10:00:00", "límites"),
    _row(11, 1, "a", True, "A", "2026-10-19 11:00:00", "álgebra"),
    _row(11, 1, "b", True, "B", "2026-10-19 11:00:00", "límites"),
    # student 2: one try 0/2
    _row(20, 2, "a", False, "D", "2026-10-19 10:30:00", "álgebra"),
    _row(20, 2, "b", False, "C", "2026-10-19 10:30:00", "límites"),
    # student 3: not the teacher's
    _row(30, 3, "a", True, "A", "2026-10-19 09:00:00", "álgebra"),
    _row(30, 3, "b", True, "B", "2026-10-19 09:00:00", "límites"),
]
NAMES = {1: "Ana", 2: "Bea"}


def test_only_my_students_first_submission_count():
    results = template_results(ROWS, NAMES)

    assert results["n_students"] == 2
    assert results["n_sessions"] == 2
    assert results["avg_score"] == 25.0  # (50 + 0) / 2
    assert [(s["name"], s["score_pct"]) for s in results["students"]] == [
        ("Ana", 50.0),
        ("Bea", 0.0),
    ]


def test_each_student_keeps_the_option_chosen():
    ana = template_results(ROWS, NAMES)["students"][0]
    assert ana["answers"] == [
        {"item_id": "a", "is_correct": True, "selected_option": "A"},
        {"item_id": "b", "is_correct": False, "selected_option": "C"},
    ]


def test_per_item_counts_the_wrong_options():
    questions = {q["item_id"]: q for q in template_results(ROWS, NAMES)["questions"]}

    assert (questions["a"]["correct"], questions["a"]["total"]) == (1, 2)
    assert questions["a"]["accuracy"] == 50.0
    assert questions["b"]["choices"] == {"C": 2}
    assert template_results(ROWS, NAMES)["worst_question"]["item_id"] == "b"


def test_per_topic_and_the_topic_to_reinforce():
    results = template_results(ROWS, NAMES)
    topics = {t["topic"]: t["accuracy"] for t in results["topics"]}
    assert topics == {"álgebra": 50.0, "límites": 0.0}
    assert results["reinforce_topic"]["topic"] == "límites"


def test_no_submission_is_an_empty_result():
    results = template_results([], NAMES)
    assert results["n_sessions"] == 0 and results["students"] == []
    assert results["best_question"] is None and results["reinforce_topic"] is None
