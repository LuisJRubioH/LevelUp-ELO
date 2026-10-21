"""
Spec 008 delivery T, rule A (owner, 2026-10-20): what the stored ratings of old fine topics become
once the bank regroups them under one coarse topic.

Per student and course, the fine rows of one coarse topic are records of different, smaller parts
of that topic, so their faithful summary is the mean — unlike spec 001's legacy reconciliation,
which never averages alternative records of the same thing (its FR-035). A coarse row the student
already has wins and is never touched. Pure: no I/O.
"""

from statistics import fmean

RD_FLOOR, RD_CEILING = 30.0, 350.0


def plan_topic_merge(fine_rows, regrouping, existing) -> list[dict]:
    """The coarse rows to insert.

    `fine_rows`: dicts with user_id, course_id, topic, current_elo, rd. `regrouping`:
    {course_id: {old_topic: new_topic}}. `existing`: {(user_id, course_id, topic)} already stored.
    Each result has user_id, course_id, topic, rating, rd and source (the fine keys, sorted).
    """
    groups: dict[tuple, list[dict]] = {}
    for row in fine_rows:
        coarse = regrouping[row["course_id"]][row["topic"]]
        groups.setdefault((row["user_id"], row["course_id"], coarse), []).append(row)
    planned = []
    for (user_id, course_id, coarse), rows in sorted(groups.items(), key=lambda g: g[0]):
        if (user_id, course_id, coarse) in existing:
            continue
        rd = fmean(float(r["rd"]) for r in rows)
        planned.append(
            {
                "user_id": user_id,
                "course_id": course_id,
                "topic": coarse,
                "rating": fmean(float(r["current_elo"]) for r in rows),
                "rd": min(RD_CEILING, max(RD_FLOOR, rd)),
                "source": "spec 008 T merge: " + " | ".join(sorted(r["topic"] for r in rows)),
            }
        )
    return planned
