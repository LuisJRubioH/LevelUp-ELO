"""
Spec 001 (R15, constitution II): every rating writer applies its effect exactly once, also when it
commits while an answer on the same (course, topic) is between its read and its write.

Survey 002 P1 (docs/sdd/persistence-survey.md § 4.1) reproduced the loss on PostgreSQL: the answer
read 1000, a procedure committed +10, and the answer wrote 1005 — the +10 was gone. Block 7 made
the procedure writer lock the student first, as the answer does; the finished PvP match did not.
Here each writer is started from inside the answer's `compute` and given time to commit: SQLite's
BEGIN IMMEDIATE and PostgreSQL's student lock must make it wait for the answer instead.
"""

import hashlib
import threading
import uuid

from src.domain.elo.model import procedure_grading
from src.domain.procedures import classify_upload
from tests.integration.conftest import make_course, make_student, rating_of, set_rating

TOPIC = "Escritores"


def _answer_plus_five_while(repo, student, item_id, writer):
    """An answer worth +5 whose `compute` starts `writer` in another thread and gives it a moment
    to commit before the answer writes; returns the writer's errors, if any."""
    errors: list[BaseException] = []

    def run():
        try:
            writer()
        except BaseException as exc:  # noqa: BLE001 — checked by the caller
            errors.append(exc)

    other = threading.Thread(target=run)

    def compute(state):
        other.start()
        other.join(timeout=1.5)  # a writer that does not wait for the answer commits here
        return (
            {
                "is_correct": True,
                "difficulty": state["item_difficulty"],
                "topic": state["topic"],
                "elo_after": state["elo"] + 5.0,
                "elo_before": state["elo"],
                "prob_failure": 0.5,
                "expected_score": 0.5,
                "time_taken": 30.0,
                "confidence_score": None,
                "error_type": None,
                "rating_deviation": 300.0,
                "elo_valid": True,
            },
            state["item_difficulty"],
            state["item_rd"],
        )

    repo.save_answer_transaction(user_id=student, item_id=item_id, compute=compute)
    other.join(timeout=60)
    assert not other.is_alive()
    return errors


def test_spec001_a_procedure_graded_during_an_answer_keeps_its_delta(repo):
    course, items = make_course(repo, [TOPIC], items_per_topic=2)
    answered, procedure_item = items[TOPIC]
    student = make_student(repo)
    set_rating(repo, student, course, TOPIC, 1000.0)
    content = f"p1 {uuid.uuid4().hex}".encode()
    submission = repo.submit_procedure(
        student,
        procedure_item,
        "p1",
        content,
        "image/png",
        hashlib.sha256(content).hexdigest(),
        classify_upload,
        lambda contribution, rating: procedure_grading(0.0, contribution, rating),
    )["submission_id"]

    errors = _answer_plus_five_while(
        repo,
        student,
        answered,
        lambda: repo.grade_procedure_transaction(
            submission, 100.0, lambda c, r: procedure_grading(100.0, c, r)
        ),
    )

    assert errors == []
    assert rating_of(repo, student, course, TOPIC) == 1015.0  # +5 answer, +10 procedure


def test_spec001_a_pvp_result_applied_during_an_answer_keeps_its_delta(repo):
    course, items = make_course(repo, [TOPIC], items_per_topic=2)
    answered, played = items[TOPIC]
    student, rival = make_student(repo), make_student(repo)
    set_rating(repo, student, course, TOPIC, 1000.0)
    set_rating(repo, rival, course, TOPIC, 1000.0)
    match = repo.create_pvp_match(course, student, rival, [played])

    errors = _answer_plus_five_while(
        repo,
        student,
        answered,
        lambda: repo.finish_pvp_match(
            match_id=match,
            winner_id=student,
            score_p1=3,
            score_p2=0,
            elo_delta_p1=10.0,
            elo_delta_p2=-10.0,
            p1_id=student,
            p2_id=rival,
        ),
    )

    assert errors == []
    assert rating_of(repo, student, course, TOPIC) == 1015.0  # +5 answer, +10 match
    assert rating_of(repo, rival, course, TOPIC) == 990.0
