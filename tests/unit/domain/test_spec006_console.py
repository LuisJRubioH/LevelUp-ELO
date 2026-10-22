"""
Spec 006 delivery C1 (FR-041): the teacher console's figures, computed once on the server.

Competition ranks with pending students last, the mean over rated display values, the
histogram, the «attention» list, and the same figures per group (a student in two of the
teacher's groups counts in both). Delivery RV (FR-041a … c): each set on its own basis, and each
place with the rating it was ranked on. Pure domain.
"""

from src.domain.elo.console import console_summary, linked_rating

ALL = {"kind": "linked_courses"}
BASES = {1: {"kind": "course", "course_id": "X", "course_name": "X"}, 2: ALL}


def _e(user_id, rating, accuracy, attempts, groups=(1,)):
    return {
        "user_id": user_id,
        "rating": rating,
        "accuracy": accuracy,
        "total_attempts": attempts,
        "group_ratings": {g: rating for g in groups},
    }


def _summary(entries):
    return console_summary(entries, ALL, BASES)


ENTRIES = [
    _e(1, 1200.2, 0.9, 10),
    _e(2, 1199.8, 0.8, 10, groups=(1, 2)),  # same displayed rating as 1: same place
    _e(3, 1000.0, 0.9, 10),  # rated below 1100: attention
    _e(4, None, 0.0, 0),  # pending, no attempts: no accuracy to judge
    _e(5, 1500.0, 0.4, 5, groups=(2,)),  # accuracy below 60 %: attention
]


def test_ranks_are_competition_ranks_with_pending_last():
    ranking = _summary(ENTRIES)["ranking"]
    assert [(r["user_id"], r["rank"]) for r in ranking] == [
        (5, 1),
        (1, 2),
        (2, 2),
        (3, 4),
        (4, None),
    ]


def test_mean_accuracy_and_attempts():
    summary = _summary(ENTRIES)
    assert summary["n"] == 5
    assert summary["mean"] == round((1500 + 1200 + 1200 + 1000) / 4)
    # The student with no attempts is out of the mean accuracy.
    assert summary["accuracy"] == round((90 + 80 + 90 + 40) / 4)
    assert summary["attempts"] == 35


def test_attention_needs_a_low_rating_or_low_accuracy_with_attempts():
    assert _summary(ENTRIES)["attention"] == [3, 5]


def test_histogram_counts_rated_students():
    histogram = {b["label"]: b["count"] for b in _summary(ENTRIES)["histogram"]}
    assert histogram == {"<1100": 1, "1100": 2, "1300": 0, "1500": 1, "1700": 0, "1900+": 0}


def test_each_group_has_its_own_figures():
    groups = _summary(ENTRIES)["groups"]
    assert set(groups) == {"1", "2"}
    assert [r["user_id"] for r in groups["2"]["ranking"]] == [5, 2]
    assert groups["2"]["mean"] == round((1500 + 1200) / 2)
    assert groups["1"]["n"] == 4 and groups["1"]["attention"] == [3]


def test_no_students_is_an_empty_summary():
    summary = _summary([])
    assert (summary["n"], summary["mean"], summary["accuracy"]) == (0, None, None)
    assert summary["ranking"] == [] and summary["groups"] == {}


def test_each_set_ranks_on_its_basis():
    """FR-041a, FR-041c: a group ranks on its own rating of each student, names its basis, and
    each place carries the number and label it was ranked on."""
    entries = [
        {**_e(1, 1500.0, 0.9, 10), "group_ratings": {1: 1000.0}},
        {**_e(2, 1200.4, 0.9, 10), "group_ratings": {1: 1299.6}},
    ]

    summary = _summary(entries)
    group = summary["groups"]["1"]

    assert [(r["user_id"], r["rank"], r["display_rating"]) for r in summary["ranking"]] == [
        (1, 1, 1500),
        (2, 2, 1200),
    ]
    assert [(r["user_id"], r["rank"], r["display_rating"]) for r in group["ranking"]] == [
        (2, 1, 1300),
        (1, 2, 1000),
    ]
    assert group["ranking"][0]["rank_label"] == "Platino II"
    assert group["mean"] == 1150 and group["attention"] == [1]
    assert (summary["basis"], group["basis"]) == (ALL, BASES[1])


def test_the_linked_rating():
    """FR-041b: the mean of the rated courses that link the student to the teacher; the overall
    rating when one link names no course; pending when none of them is rated."""
    courses = {"X": 1200.0, "Y": 1800.0, "Z": None}
    assert linked_rating(courses, {"X"}, overall=1500.0) == 1200.0
    assert linked_rating(courses, {"X", "Y"}, overall=1100.0) == 1500.0
    assert linked_rating(courses, {"X", "Z", "W"}, overall=1500.0) == 1200.0
    assert linked_rating(courses, {None, "X"}, overall=1500.0) == 1500.0
    assert linked_rating(courses, {"Z"}, overall=1500.0) is None
