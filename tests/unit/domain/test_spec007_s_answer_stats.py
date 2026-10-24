"""
Spec 007 delivery S (FR-070, O-S3, O-S4): the League's answers counted per topic and per item,
marked as League answers — pure functions over the raw rows the repositories return.
"""

from src.domain.pvp.answer_stats import league_export_rows, league_summary


def _row(item, correct, at, topic="Fracciones", course="aritmetica", **extra):
    return {
        "course_id": course,
        "course_name": course.title(),
        "topic": topic,
        "item_id": item,
        "is_correct": correct,
        "answered_at": at,
        **extra,
    }


def test_spec007_league_summary_counts_per_topic_and_item():
    """FR-070, O-S3: answers, correct and the share per (course, topic), weakest first; per item
    only the missed ones, most missed first (then the most recent), at most `top_items`; every
    row marked as a League answer."""
    rows = [
        # Fracciones: 1 of 4 right — the weakest topic.
        _row("f1", False, "2026-10-20 10:00:00"),
        _row("f1", False, "2026-10-21 10:00:00"),
        _row("f2", False, "2026-10-21 11:00:00"),
        _row("f3", True, "2026-10-21 12:00:00"),
        # Potencias: 2 of 3 right.
        _row("p1", True, "2026-10-20 09:00:00", topic="Potencias"),
        _row("p1", True, "2026-10-20 09:01:00", topic="Potencias"),
        _row("p2", False, "2026-10-22 08:00:00", topic="Potencias"),
        # The same topic name in another course is another row.
        _row("g1", True, "2026-10-19 08:00:00", course="geometria"),
    ]

    summary = league_summary(rows, top_items=2)

    assert (summary["answers"], summary["correct"]) == (8, 4)
    assert [
        (t["course_id"], t["topic"], t["answers"], t["correct"]) for t in summary["topics"]
    ] == [
        ("aritmetica", "Fracciones", 4, 1),
        ("aritmetica", "Potencias", 3, 2),
        ("geometria", "Fracciones", 1, 1),
    ]
    assert summary["topics"][0]["share_correct"] == 0.25
    assert summary["topics"][0]["course_name"] == "Aritmetica"
    # f1 missed twice; p2 and f2 once each, p2 the more recent; f3, p1 and g1 never missed.
    assert [(i["item_id"], i["answers"], i["missed"]) for i in summary["items"]] == [
        ("f1", 2, 2),
        ("p2", 1, 1),
    ]
    assert summary["items"][0]["last_answered_at"] == "2026-10-21 10:00:00"
    assert summary["items"][0]["topic"] == "Fracciones"
    assert all(r["source"] == "league" for r in summary["topics"] + summary["items"])


def test_spec007_league_summary_of_no_answers_is_empty():
    """FR-070: no League answer → nothing to show (the screens hide the section)."""
    assert league_summary([]) == {"answers": 0, "correct": 0, "topics": [], "items": []}


def test_spec007_league_summary_ties_are_stable():
    """FR-070: equal shares order by the most answered, then course and topic; equal misses and
    times by item id — the same input always gives the same report."""
    rows = [
        _row("a", False, "2026-10-21 10:00:00", topic="B"),
        _row("b", False, "2026-10-21 10:00:00", topic="A"),
        _row("c", False, "2026-10-21 10:00:00", topic="A"),
    ]
    summary = league_summary(rows)
    assert [t["topic"] for t in summary["topics"]] == ["A", "B"]
    assert [i["item_id"] for i in summary["items"]] == ["a", "b", "c"]


def test_spec007_league_export_rows_one_per_student_topic_item():
    """FR-070, O-S4: one row per student × course × topic × item with answers and correct, the
    student named as in «Intentos»; ordered by name, course, topic and item."""
    rows = [
        _row("f1", False, "2026-10-20 10:00:00", user_id=7, student_name="Zoe"),
        _row("f1", True, "2026-10-21 10:00:00", user_id=7, student_name="Zoe"),
        _row("f2", True, "2026-10-21 10:00:00", user_id=7, student_name="Zoe"),
        _row("f1", False, "2026-10-21 10:00:00", user_id=3, student_name="Ana"),
    ]

    assert league_export_rows(rows) == [
        {
            "student_id": 3,
            "name": "Ana",
            "course_id": "aritmetica",
            "course_name": "Aritmetica",
            "topic": "Fracciones",
            "item_id": "f1",
            "answers": 1,
            "correct": 0,
        },
        {
            "student_id": 7,
            "name": "Zoe",
            "course_id": "aritmetica",
            "course_name": "Aritmetica",
            "topic": "Fracciones",
            "item_id": "f1",
            "answers": 2,
            "correct": 1,
        },
        {
            "student_id": 7,
            "name": "Zoe",
            "course_id": "aritmetica",
            "course_name": "Aritmetica",
            "topic": "Fracciones",
            "item_id": "f2",
            "answers": 1,
            "correct": 1,
        },
    ]
