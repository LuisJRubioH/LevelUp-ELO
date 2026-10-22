"""
Spec 006 C1 (FR-041): the teacher console's figures, computed once on the server.

The browser used to work out the group mean, the rating histogram, the ranking (array positions,
so ties took different places) and the «attention» list. These come from here now: the same
display values and competition ranks a student sees (spec 001 FR-028h, FR-028j). Pure.

Delivery RV (FR-041a … c): each set is ranked on its own basis — a group on its course, the
whole set on the courses that link each student to the teacher — and each place carries the
rating it was ranked on.
"""

from src.domain.elo.aggregation import overall_rating
from src.domain.elo.ranks import rank_competition, rating_display

ATTENTION_RATING = 1100  # below it, a rated student needs attention
ATTENTION_ACCURACY = 60  # percent; below it, too — judged only with attempts in the window
BUCKETS = (
    ("<1100", None, 1100),
    ("1100", 1100, 1300),
    ("1300", 1300, 1500),
    ("1500", 1500, 1700),
    ("1700", 1700, 1900),
    ("1900+", 1900, None),
)


def _pct(accuracy: float) -> int:
    return round(accuracy * 100 if accuracy <= 1 else accuracy)


def _histogram(shown: list[int]) -> list[dict]:
    return [
        {
            "label": label,
            "count": sum(1 for s in shown if (lo is None or s >= lo) and (hi is None or s < hi)),
        }
        for label, lo, hi in BUCKETS
    ]


def linked_rating(course_ratings: dict, courses: set, overall: float | None) -> float | None:
    """FR-041b: a student's rating over the courses that link them to the teacher — the
    equal-weight mean of those that are rated (None while none is), or `overall` when one link
    names no course (None in `courses`: that teacher reviews every course). `course_ratings`:
    course id → full-precision rating (None while pending)."""
    if None in courses:
        return overall
    return overall_rating([course_ratings.get(course) for course in sorted(courses)])


def _figures(entries: list[dict], basis: dict) -> dict:
    shown = [rating_display(e["rating"])["display_rating"] for e in entries]
    rated = [s for s in shown if s is not None]
    ranking = rank_competition([{"user_id": e["user_id"], "rating": e["rating"]} for e in entries])
    answered = [_pct(e["accuracy"]) for e in entries if e["total_attempts"]]
    attention = [
        e["user_id"]
        for e, s in zip(entries, shown)
        if (e["total_attempts"] and _pct(e["accuracy"]) < ATTENTION_ACCURACY)
        or (s is not None and s < ATTENTION_RATING)
    ]
    return {
        "n": len(entries),
        "mean": round(sum(rated) / len(rated)) if rated else None,
        # A student with no attempts in the window has no accuracy: left out, not counted as 0.
        "accuracy": round(sum(answered) / len(answered)) if answered else None,
        "attempts": sum(e["total_attempts"] for e in entries),
        "attention": attention,
        # FR-041c: each place with the number and label it was ranked on.
        "ranking": [
            {
                "user_id": r["user_id"],
                "rank": r["rank"],
                "display_rating": r["rating"],
                "rank_label": r["rank_label"],
            }
            for r in ranking
        ],
        "histogram": _histogram(rated),
        "basis": basis,
    }


def console_summary(entries: list[dict], basis: dict, group_bases: dict) -> dict:
    """`entries`: one per student — user_id, rating (full precision on the whole set's basis,
    None while pending), accuracy (0–1), total_attempts, group_ratings (each of the teacher's
    groups that list them → the rating on that group's basis). `basis` and `group_bases` (group
    id → basis) name what each set is ranked on. The whole set's figures, and the same figures
    per group under `groups` (keyed by the group id as text, as JSON keys are)."""
    group_ids = sorted({g for e in entries for g in e["group_ratings"]})
    groups = {
        str(group_id): _figures(
            [
                {**e, "rating": e["group_ratings"][group_id]}
                for e in entries
                if group_id in e["group_ratings"]
            ],
            group_bases[group_id],
        )
        for group_id in group_ids
    }
    return {**_figures(entries, basis), "groups": groups}
