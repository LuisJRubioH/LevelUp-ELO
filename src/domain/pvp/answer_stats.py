"""
src/domain/pvp/answer_stats.py
==============================
Spec 007 FR-070 (owner decisions O-S1 … O-S4): the League's answers counted for study — per topic
and per item, marked as League answers. Pure — no clock, no I/O, no rating.

The rows are the raw `pvp_answers` rows the repositories return, one per answer, each with the
match's course and the item's current topic. They never enter `attempts`, a rating or the
selector's history (R15): these counts sit beside the practice figures, not inside them.
"""

SOURCE = "league"  # the spec's "marked as League answers"


def league_summary(rows, top_items: int = 5) -> dict:
    """The student's League answers: totals, each (course, topic) with answers, correct and the
    share correct — weakest first, then the most answered, as the subtopic report — and the
    items missed at least once, most missed first, then the most recent, at most `top_items`
    (O-S3)."""
    topics: dict[tuple, dict] = {}
    items: dict[str, dict] = {}
    for row in rows:
        correct = bool(row["is_correct"])
        topic = topics.setdefault(
            (row["course_id"], row["topic"]),
            {
                "course_id": row["course_id"],
                "course_name": row.get("course_name") or row["course_id"],
                "topic": row["topic"],
                "answers": 0,
                "correct": 0,
                "source": SOURCE,
            },
        )
        topic["answers"] += 1
        topic["correct"] += correct
        item = items.setdefault(
            row["item_id"],
            {
                "item_id": row["item_id"],
                "course_id": row["course_id"],
                "topic": row["topic"],
                "answers": 0,
                "missed": 0,
                "last_answered_at": row["answered_at"],
                "source": SOURCE,
            },
        )
        item["answers"] += 1
        item["missed"] += not correct
        item["last_answered_at"] = max(item["last_answered_at"], row["answered_at"])

    for topic in topics.values():
        topic["share_correct"] = topic["correct"] / topic["answers"]
    by_weakness = sorted(
        topics.values(),
        key=lambda t: (t["share_correct"], -t["answers"], t["course_id"], t["topic"]),
    )
    missed = sorted((i for i in items.values() if i["missed"]), key=lambda i: i["item_id"])
    missed.sort(key=lambda i: i["last_answered_at"], reverse=True)
    missed.sort(key=lambda i: i["missed"], reverse=True)
    return {
        "answers": sum(t["answers"] for t in topics.values()),
        "correct": sum(t["correct"] for t in topics.values()),
        "topics": by_weakness,
        "items": missed[:top_items],
    }


def league_export_rows(rows) -> list[dict]:
    """The workbook's «Liga» sheet (O-S4): one row per student × course × topic × item with
    answers and correct, the student named as in «Intentos» (`student_name`); by name, course,
    topic and item."""
    counted: dict[tuple, dict] = {}
    for row in rows:
        key = (row["user_id"], row["course_id"], row["topic"], row["item_id"])
        entry = counted.setdefault(
            key,
            {
                "student_id": row["user_id"],
                "name": row["student_name"],
                "course_id": row["course_id"],
                "course_name": row.get("course_name") or row["course_id"],
                "topic": row["topic"],
                "item_id": row["item_id"],
                "answers": 0,
                "correct": 0,
            },
        )
        entry["answers"] += 1
        entry["correct"] += bool(row["is_correct"])
    return sorted(
        counted.values(),
        key=lambda r: (r["name"], r["student_id"], r["course_id"], r["topic"], r["item_id"]),
    )
