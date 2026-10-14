"""
`get_all_attempts_for_calibration` feeds scripts/train_calibrator.py and scripts/monthly_metrics.py.
On SQLite it turned each row tuple into a dict with `dict(row)`, which raises as soon as there is
one attempt, so both scripts crashed on SQLite. Both engines return the same rows.
"""

from tests.integration.conftest import answer, make_course, make_student

COLUMNS = {
    "id",
    "user_id",
    "item_id",
    "is_correct",
    "expected_score",
    "elo_valid",
    "time_taken",
    "education_level",
}


def test_calibration_reads_the_valid_attempts(repo):
    _, items = make_course(repo, ["Fracciones"], items_per_topic=2)
    first, second = items["Fracciones"]
    student = make_student(repo, education_level="colegio")
    answer(repo, student, first, correct=True)
    answer(repo, student, second, correct=False, seconds=0)  # invalid time: not for calibration

    rows = [r for r in repo.get_all_attempts_for_calibration() if r["user_id"] == student]

    assert len(rows) == 1
    assert set(rows[0]) == COLUMNS
    assert (rows[0]["item_id"], bool(rows[0]["is_correct"]), rows[0]["elo_valid"]) == (
        first,
        True,
        1,
    )
    by_level = repo.get_all_attempts_for_calibration(education_level="colegio")
    assert [r["item_id"] for r in by_level if r["user_id"] == student] == [first]
    assert not [
        r
        for r in repo.get_all_attempts_for_calibration(education_level="universidad")
        if r["user_id"] == student
    ]
