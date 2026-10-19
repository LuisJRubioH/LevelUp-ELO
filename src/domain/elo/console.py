"""
Spec 006 C1 (FR-041): the teacher console's figures, computed once on the server.

The browser used to work out the group mean, the rating histogram, the ranking (array positions,
so ties took different places) and the «attention» list. These come from here now: the same
display values and competition ranks a student sees (spec 001 FR-028h, FR-028j). Pure.
"""

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


def _figures(entries: list[dict]) -> dict:
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
        "ranking": [{"user_id": r["user_id"], "rank": r["rank"]} for r in ranking],
        "histogram": _histogram(rated),
    }


def console_summary(entries: list[dict]) -> dict:
    """`entries`: one per student — user_id, rating (full precision, None while pending),
    accuracy (0–1), total_attempts, group_ids (the teacher's groups that list them). The whole
    set's figures, and the same figures per group under `groups` (keyed by the group id as text,
    as JSON keys are)."""
    group_ids = sorted({g for e in entries for g in e["group_ids"]})
    groups = {
        str(group_id): _figures([e for e in entries if group_id in e["group_ids"]])
        for group_id in group_ids
    }
    return {**_figures(entries), "groups": groups}
