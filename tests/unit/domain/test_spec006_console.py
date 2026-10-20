"""
Spec 006 delivery C1 (FR-041): the teacher console's figures, computed once on the server.

Competition ranks with pending students last, the mean over rated display values, the
histogram, the «attention» list, and the same figures per group (a student in two of the
teacher's groups counts in both). Pure domain.
"""

from src.domain.elo.console import console_summary


def _e(user_id, rating, accuracy, attempts, groups=(1,)):
    return {
        "user_id": user_id,
        "rating": rating,
        "accuracy": accuracy,
        "total_attempts": attempts,
        "group_ids": list(groups),
    }


ENTRIES = [
    _e(1, 1200.2, 0.9, 10),
    _e(2, 1199.8, 0.8, 10, groups=(1, 2)),  # same displayed rating as 1: same place
    _e(3, 1000.0, 0.9, 10),  # rated below 1100: attention
    _e(4, None, 0.0, 0),  # pending, no attempts: no accuracy to judge
    _e(5, 1500.0, 0.4, 5, groups=(2,)),  # accuracy below 60 %: attention
]


def test_ranks_are_competition_ranks_with_pending_last():
    ranking = console_summary(ENTRIES)["ranking"]
    assert [(r["user_id"], r["rank"]) for r in ranking] == [
        (5, 1),
        (1, 2),
        (2, 2),
        (3, 4),
        (4, None),
    ]


def test_mean_accuracy_and_attempts():
    summary = console_summary(ENTRIES)
    assert summary["n"] == 5
    assert summary["mean"] == round((1500 + 1200 + 1200 + 1000) / 4)
    # The student with no attempts is out of the mean accuracy.
    assert summary["accuracy"] == round((90 + 80 + 90 + 40) / 4)
    assert summary["attempts"] == 35


def test_attention_needs_a_low_rating_or_low_accuracy_with_attempts():
    assert console_summary(ENTRIES)["attention"] == [3, 5]


def test_histogram_counts_rated_students():
    histogram = {b["label"]: b["count"] for b in console_summary(ENTRIES)["histogram"]}
    assert histogram == {"<1100": 1, "1100": 2, "1300": 0, "1500": 1, "1700": 0, "1900+": 0}


def test_each_group_has_its_own_figures():
    groups = console_summary(ENTRIES)["groups"]
    assert set(groups) == {"1", "2"}
    assert [r["user_id"] for r in groups["2"]["ranking"]] == [5, 2]
    assert groups["2"]["mean"] == round((1500 + 1200) / 2)
    assert groups["1"]["n"] == 4 and groups["1"]["attention"] == [3]


def test_no_students_is_an_empty_summary():
    summary = console_summary([])
    assert (summary["n"], summary["mean"], summary["accuracy"]) == (0, None, None)
    assert summary["ranking"] == [] and summary["groups"] == {}
