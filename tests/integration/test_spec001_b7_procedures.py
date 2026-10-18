"""
Spec 001, delivery B7: a regraded procedure counts once — on both engines.

T002 pins FR-024c (a resubmission returns to review and keeps the rating effect); it passed on the
unchanged code before the domain imports below existed. Every other test is [CHANGE]
(tasks-b7.md T007–T014): written before the code it tests.
"""

import hashlib
import threading
import uuid

import pytest

from src.domain.elo.model import procedure_grading
from src.domain.procedures import (
    ACCEPT,
    COPY,
    REFUSE_OTHER_ITEM,
    REFUSE_SAME_ITEM,
    classify_upload,
)
from tests.integration.conftest import (
    is_postgres,
    make_course,
    make_group,
    make_student,
    make_teacher,
    rating_of,
    set_rating,
    sql,
)

TOPIC = "Procedimientos"


def _course(repo):
    course_id, items = make_course(repo, [TOPIC], items_per_topic=2)
    return course_id, items[TOPIC]


def _file(label: str) -> bytes:
    """A file nobody uploaded before: PostgreSQL keeps every earlier run's files, and a file
    another student sent first is a copy (FR-024i)."""
    return f"b7 {label} {uuid.uuid4().hex}".encode()


def _upload(repo, student, item_id, content: bytes):
    """A student's upload through the repository, with the file's own SHA-256."""
    return repo.save_procedure_submission(
        student,
        item_id,
        "b7 procedure",
        content,
        "image/png",
        file_hash=hashlib.sha256(content).hexdigest(),
    )


def _status(repo, submission_id):
    return sql(repo, "SELECT status FROM procedure_submissions WHERE id = ?", (submission_id,))[0][
        0
    ]


# ── T002 [AS-IS]: pinned on the unchanged code ──────────────────────────────


def test_spec001_b7_resubmission_returns_to_review_and_keeps_the_effect(repo, student):
    """FR-024c, US9-AS4: graded 80 (+6), resubmitted → pending, and the rating keeps the +6."""
    course, (item, _) = _course(repo)
    set_rating(repo, student, course, TOPIC, 1100.0)

    submission = _upload(repo, student, item, _file("first file"))
    assert repo.validate_procedure_submission(submission, teacher_score=80.0)
    assert rating_of(repo, student, course, TOPIC) == 1106.0

    again = _upload(repo, student, item, _file("second file"))

    assert again == submission
    assert _status(repo, submission) == "pending"
    assert rating_of(repo, student, course, TOPIC) == 1106.0


# ── [CHANGE] helpers: the B7 repository methods with the domain's computations ──


def _submit(repo, student, item_id, content: bytes):
    """B7 upload: classification and the copy's automatic 0 come from the domain."""
    return repo.submit_procedure(
        student,
        item_id,
        "b7 procedure",
        content,
        "image/png",
        hashlib.sha256(content).hexdigest(),
        classify_upload,
        lambda contribution, rating: procedure_grading(0.0, contribution, rating),
    )


def _grade(repo, submission_id, grade, review_round=None, teacher_id=None):
    return repo.grade_procedure_transaction(
        submission_id,
        grade,
        lambda contribution, rating: procedure_grading(grade, contribution, rating),
        feedback="",
        teacher_id=teacher_id,
        review_round=review_round,
    )


def _procedure(repo, submission_id):
    row = sql(
        repo,
        "SELECT status, contribution, contribution_origin, review_round, is_copy"
        " FROM procedure_submissions WHERE id = ?",
        (submission_id,),
    )[0]
    return {
        "status": row[0],
        "contribution": None if row[1] is None else float(row[1]),
        "origin": row[2],
        "round": row[3],
        "copy": bool(row[4]),
    }


def _new_procedure(repo, student, item, rating=1000.0):
    """A course item, the student's rating on it, and an accepted first upload."""
    course = sql(repo, "SELECT course_id FROM items WHERE id = ?", (item,))[0][0]
    if rating is not None:
        set_rating(repo, student, course, TOPIC, rating)
    submitted = _submit(repo, student, item, _file("first"))
    assert submitted["outcome"] == ACCEPT
    return course, submitted["submission_id"]


# ── T007: equal, higher and lower regrade (US9-AS1 … AS3; FR-024b, FR-024d) ──


@pytest.mark.parametrize(
    "first, second, moved, contribution",
    [(80.0, 80.0, 0.0, 6.0), (60.0, 90.0, 6.0, 8.0), (80.0, 30.0, -10.0, -4.0)],
    ids=["US9-AS1-equal", "US9-AS2-higher", "US9-AS3-lower"],
)
def test_spec001_b7_a_regrade_moves_the_rating_by_the_difference_only(
    repo, student, first, second, moved, contribution
):
    _, (item, _) = _course(repo)
    course, submission = _new_procedure(repo, student, item)
    assert _grade(repo, submission, first)["created"]
    before = rating_of(repo, student, course, TOPIC)

    assert _submit(repo, student, item, _file("resubmitted file"))["submission_id"] == submission
    result = _grade(repo, submission, second)

    assert rating_of(repo, student, course, TOPIC) == pytest.approx(before + moved)
    assert (result["applied"], result["contribution_after"]) == (moved, contribution)
    assert _procedure(repo, submission)["contribution"] == contribution
    assert _procedure(repo, submission)["origin"] == "grading"


# ── T008: the floor of 0 (US9-AS7; FR-024d) ─────────────────────────────────


def test_spec001_b7_a_floored_penalty_is_corrected_by_what_was_applied(repo, student):
    _, (item, _) = _course(repo)
    course, submission = _new_procedure(repo, student, item, rating=3.0)

    first = _grade(repo, submission, 0.0)
    assert (first["computed_delta"], first["applied"]) == (-10.0, -3.0)
    assert rating_of(repo, student, course, TOPIC) == 0.0

    _submit(repo, student, item, _file("better file"))
    second = _grade(repo, submission, 80.0)

    assert (second["correction"], second["applied"]) == (9.0, 9.0)
    assert rating_of(repo, student, course, TOPIC) == 9.0
    assert _procedure(repo, submission)["contribution"] == 6.0


# ── T009: the history of a procedure (US9-AS8; FR-024e) ─────────────────────


def test_spec001_b7_every_grading_is_kept_across_resubmissions(repo, student):
    _, (item, _) = _course(repo)
    _, submission = _new_procedure(repo, student, item)
    _grade(repo, submission, 80.0)
    _submit(repo, student, item, _file("second version"))
    _grade(repo, submission, 30.0)

    history = repo.get_procedure_gradings(submission)

    assert [
        (h["review_round"], h["grade"], h["computed_delta"], h["correction"], h["applied"])
        for h in history
    ] == [(1, 80.0, 6.0, 6.0, 6.0), (2, 30.0, -4.0, -10.0, -10.0)]
    assert [h["contribution_after"] for h in history] == [6.0, -4.0]
    assert all(h["reason"] == "teacher" and h["created_at"] for h in history)


# ── T010: retries and simultaneous gradings (US9-AS5, US9-AS6; FR-024g) ─────


def test_spec001_b7_a_retried_grading_returns_the_same_result_once(repo, student):
    _, (item, _) = _course(repo)
    course, submission = _new_procedure(repo, student, item)

    first = _grade(repo, submission, 80.0, review_round=1)
    retry = _grade(repo, submission, 80.0, review_round=1)

    assert first["created"] and not retry["created"]
    assert {k: v for k, v in retry.items() if k != "created"} == {
        k: v for k, v in first.items() if k != "created"
    }
    assert rating_of(repo, student, course, TOPIC) == 1006.0
    assert len(repo.get_procedure_gradings(submission)) == 1


def test_spec001_b7_two_simultaneous_gradings_apply_one_correction(repo, student):
    _, (item, _) = _course(repo)
    course, submission = _new_procedure(repo, student, item)
    start = threading.Barrier(2)
    results = []

    def grade(score):
        start.wait()
        results.append(_grade(repo, submission, score, review_round=1))

    threads = [threading.Thread(target=grade, args=(s,)) for s in (70.0, 90.0)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(r["created"] for r in results) == [False, True]
    winner = next(r for r in results if r["created"])
    assert all(r["applied"] == winner["applied"] for r in results)
    assert rating_of(repo, student, course, TOPIC) == pytest.approx(1000.0 + winner["applied"])
    assert len(repo.get_procedure_gradings(submission)) == 1


def test_spec001_b7_a_stale_review_round_is_refused(repo, student):
    _, (item, _) = _course(repo)
    _, submission = _new_procedure(repo, student, item)
    _grade(repo, submission, 80.0, review_round=1)
    _submit(repo, student, item, _file("round two"))

    assert _grade(repo, submission, 90.0, review_round=3) is None
    assert _procedure(repo, submission)["status"] in ("pending", "PENDING_TEACHER_VALIDATION")


# ── T011: one procedure per student and item (FR-024a) ──────────────────────


def test_spec001_b7_two_first_submissions_at_once_leave_one_procedure(repo, student):
    _, (item, _) = _course(repo)
    start = threading.Barrier(2)

    def upload(n):
        start.wait()
        _submit(repo, student, item, _file(f"concurrent {n}"))

    threads = [threading.Thread(target=upload, args=(n,)) for n in (1, 2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    rows = sql(
        repo,
        "SELECT review_round FROM procedure_submissions WHERE student_id = ? AND item_id = ?",
        (student, item),
    )
    assert [r[0] for r in rows] == [2]


# ── T012: installing B7 changes no rating (FR-024h, FR-024a) ────────────────


def _ratings(repo, students):
    marks = ",".join("?" for _ in students)
    return sorted(
        tuple(r)
        for r in sql(
            repo,
            "SELECT user_id, course_id, topic, current_elo FROM student_course_topic_elo"
            f" WHERE user_id IN ({marks})",
            tuple(students),
        )
    )


def _legacy_row(repo, student, item, elo_delta, status="VALIDATED_BY_TEACHER"):
    """A procedure as graded before B7: a stored delta and no contribution recorded."""
    return sql(
        repo,
        "INSERT INTO procedure_submissions (student_id, item_id, item_content, image_data, status,"
        " elo_delta, elo_applied, contribution, contribution_origin)"
        " VALUES (?, ?, 'legacy', ?, ?, ?, 1, 0, NULL) RETURNING id",
        (student, item, b"legacy image", status, elo_delta),
    )[0][0]


def test_spec001_b7_installing_backfills_contributions_without_moving_a_rating(repo):
    _, (item_a, item_b) = _course(repo)
    positive, negative, resubmitted, fresh = (make_student(repo) for _ in range(4))
    course = sql(repo, "SELECT course_id FROM items WHERE id = ?", (item_a,))[0][0]
    for s in (positive, negative, resubmitted, fresh):
        set_rating(repo, s, course, TOPIC, 500.0)
    p = _legacy_row(repo, positive, item_a, 6.0)
    n = _legacy_row(repo, negative, item_a, -4.0)
    r = _legacy_row(repo, resubmitted, item_a, 2.0, status="pending")
    f = sql(
        repo,
        "INSERT INTO procedure_submissions (student_id, item_id, item_content, image_data, status)"
        " VALUES (?, ?, 'never graded', ?, 'pending') RETURNING id",
        (fresh, item_b, b"legacy image"),
    )[0][0]
    before = _ratings(repo, [positive, negative, resubmitted, fresh])

    repo._backfill_procedure_contributions()
    repo._backfill_procedure_contributions()  # a second run changes nothing

    assert (_procedure(repo, p)["contribution"], _procedure(repo, p)["origin"]) == (
        6.0,
        "legacy_delta",
    )
    assert (_procedure(repo, n)["contribution"], _procedure(repo, n)["origin"]) == (
        None,
        "legacy_unknown",
    )
    assert _procedure(repo, r)["contribution"] == 2.0
    assert (_procedure(repo, f)["contribution"], _procedure(repo, f)["origin"]) == (0.0, None)
    assert _ratings(repo, [positive, negative, resubmitted, fresh]) == before

    # FR-024h, B7-P1: an unknown contribution regraded applies nothing until reviewed.
    sql(repo, "UPDATE procedure_submissions SET status = 'pending' WHERE id = ?", (n,))
    result = _grade(repo, n, 90.0)
    assert (result["applied"], result["contribution_after"]) == (0.0, None)
    assert _procedure(repo, n)["origin"] == "legacy_unknown"
    assert _ratings(repo, [positive, negative, resubmitted, fresh]) == before


def _has_unique_pair_index(repo):
    if is_postgres(repo):
        rows = sql(
            repo,
            "SELECT 1 FROM pg_indexes WHERE tablename = 'procedure_submissions'"
            " AND indexname = 'idx_procedure_submissions_student_item'",
        )
    else:
        rows = sql(
            repo,
            "SELECT 1 FROM sqlite_master WHERE type = 'index'"
            " AND name = 'idx_procedure_submissions_student_item'",
        )
    return bool(rows)


def test_spec001_b7_the_unique_pair_index_waits_for_duplicates_to_be_merged(repo, student, caplog):
    _, (item, _) = _course(repo)
    assert _has_unique_pair_index(repo)  # a fresh database has no duplicate pair
    sql(repo, "DROP INDEX IF EXISTS idx_procedure_submissions_student_item")
    first = _legacy_row(repo, student, item, 2.0)
    duplicate = _legacy_row(repo, student, item, 4.0)

    with caplog.at_level("WARNING"):
        created = repo._ensure_procedure_pair_index()
    assert not created and not _has_unique_pair_index(repo)
    assert "duplicate (student_id, item_id) pairs" in caplog.text

    sql(repo, "DELETE FROM procedure_submissions WHERE id = ?", (duplicate,))
    assert repo._ensure_procedure_pair_index() and _has_unique_pair_index(repo)
    assert first


# ── T013: a file another student uploaded (US9-AS10; FR-024i) ───────────────


def test_spec001_b7_another_students_file_is_graded_zero_and_marked(repo):
    _, (item_a, item_b) = _course(repo)
    owner, copier, other_item_copier = (make_student(repo) for _ in range(3))
    course = sql(repo, "SELECT course_id FROM items WHERE id = ?", (item_a,))[0][0]
    for s in (copier, other_item_copier):
        set_rating(repo, s, course, TOPIC, 1000.0)
    content = _file("original work")
    assert _submit(repo, owner, item_a, content)["outcome"] == ACCEPT

    same_item = _submit(repo, copier, item_a, content)
    other_item = _submit(repo, other_item_copier, item_b, content)

    for result, student in ((same_item, copier), (other_item, other_item_copier)):
        assert result["outcome"] == COPY
        assert (result["grading"]["grade"], result["grading"]["applied"]) == (0.0, -10.0)
        assert result["grading"]["reason"] == "copy" and result["grading"]["grader_id"] is None
        procedure = _procedure(repo, result["submission_id"])
        assert procedure["copy"] and procedure["status"] == "VALIDATED_BY_TEACHER"
        assert rating_of(repo, student, course, TOPIC) == 990.0


def test_spec001_b7_two_students_sending_one_new_file_leave_one_first_owner(repo):
    _, (item, _) = _course(repo)
    students = [make_student(repo) for _ in range(2)]
    start = threading.Barrier(2)
    outcomes = []
    content = _file("same new file")

    def upload(student):
        start.wait()
        outcomes.append(_submit(repo, student, item, content)["outcome"])

    threads = [threading.Thread(target=upload, args=(s,)) for s in students]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(outcomes) == sorted([ACCEPT, COPY])


# ── T014: the student's own file again (US9-AS11, US9-AS12; FR-024j, FR-024k) ──


def test_spec001_b7_an_own_file_again_is_refused_and_changes_nothing(repo, student):
    _, (item_a, item_b) = _course(repo)
    content = _file("my own work")
    course, submission = _new_procedure(repo, student, item_a)
    sql(repo, "UPDATE procedure_submissions SET file_hash = ? WHERE id = ?", ("x", submission))
    first = _submit(repo, student, item_a, content)  # a second, different file: resubmission
    assert first["outcome"] == ACCEPT
    _grade(repo, submission, 80.0)
    state = (_procedure(repo, submission), rating_of(repo, student, course, TOPIC))

    same = _submit(repo, student, item_a, content)
    other = _submit(repo, student, item_b, content)

    assert (same["outcome"], same["submission_id"]) == (REFUSE_SAME_ITEM, None)
    assert (other["outcome"], other["submission_id"]) == (REFUSE_OTHER_ITEM, None)
    assert (_procedure(repo, submission), rating_of(repo, student, course, TOPIC)) == state
    assert sql(
        repo,
        "SELECT COUNT(*) FROM procedure_submissions WHERE student_id = ? AND item_id = ?",
        (student, item_b),
    ) == [(0,)]


# ── Review follow-ups (tasks-b7.md T031–T033): written first, each failed on 262e470 ──


def _ai_score(repo, submission_id):
    return sql(
        repo, "SELECT ai_proposed_score FROM procedure_submissions WHERE id = ?", (submission_id,)
    )[0][0]


def test_spec001_b7_an_ai_score_never_reopens_a_graded_procedure_or_a_copy(repo):
    """FR-024i, FR-024k: V1 records the AI's score after every upload, a copy or a refused file
    included; only a procedure waiting for review takes it."""
    _, (item_a, item_b) = _course(repo)
    owner, copier = make_student(repo), make_student(repo)
    content = _file("ai score")
    assert _upload(repo, owner, item_a, content)
    copy = _upload(repo, copier, item_b, content)  # graded 0 by the system, as a copy
    graded = _upload(repo, owner, item_b, _file("graded"))
    assert repo.validate_procedure_submission(graded, teacher_score=80.0)
    pending = _upload(repo, copier, item_a, _file("pending"))
    before = [_procedure(repo, copy), _procedure(repo, graded)]

    for student, item in ((copier, item_b), (owner, item_b), (copier, item_a)):
        repo.save_ai_proposed_score(student, item, 70.0, ai_feedback="sugerencia")

    assert [_procedure(repo, copy), _procedure(repo, graded)] == before
    assert (_ai_score(repo, copy), _ai_score(repo, graded)) == (None, None)
    assert _procedure(repo, pending)["status"] == "PENDING_TEACHER_VALIDATION"
    assert _ai_score(repo, pending) == 70.0


def test_spec001_b7_with_a_duplicate_pair_an_upload_changes_one_procedure(repo, student):
    """FR-024b, FR-024i: while an old duplicate (student, item) pair holds the unique index back
    (FR-024a), an upload resubmits or grades one procedure, never both."""
    _, (item, other) = _course(repo)
    owner = make_student(repo)
    sql(repo, "DROP INDEX IF EXISTS idx_procedure_submissions_student_item")
    first = _legacy_row(repo, student, item, 6.0)
    duplicate = _legacy_row(repo, student, item, 6.0)
    try:
        repo._backfill_procedure_contributions()
        untouched = _procedure(repo, duplicate)
        content = _file("someone else's work")
        assert _submit(repo, owner, other, content)["outcome"] == ACCEPT

        result = _submit(repo, student, item, content)

        assert (result["outcome"], result["submission_id"]) == (COPY, first)
        assert _procedure(repo, first)["copy"]
        assert _procedure(repo, duplicate) == untouched
    finally:
        sql(
            repo, "DELETE FROM procedure_gradings WHERE submission_id IN (?, ?)", (first, duplicate)
        )
        sql(repo, "DELETE FROM procedure_uploads WHERE submission_id IN (?, ?)", (first, duplicate))
        sql(repo, "DELETE FROM procedure_submissions WHERE id = ?", (duplicate,))
        assert repo._ensure_procedure_pair_index()


def test_spec001_b7_the_teacher_export_reports_the_amount_applied(repo, student):
    """FR-024f: graded 80 (+6), resubmitted and graded 30 — the export shows the −10 applied,
    never the computed −4."""
    _, (item, _) = _course(repo)
    teacher = make_teacher(repo)
    group = make_group(repo, teacher)
    sql(repo, "UPDATE users SET group_id = ? WHERE id = ?", (group, student))
    _, submission = _new_procedure(repo, student, item)
    _grade(repo, submission, 80.0)
    assert _submit(repo, student, item, _file("second"))["outcome"] == ACCEPT
    _grade(repo, submission, 30.0)

    rows = [r for r in repo.export_teacher_procedures(teacher) if r["student_id"] == student]

    assert [r["elo_delta"] for r in rows] == [-10.0]
