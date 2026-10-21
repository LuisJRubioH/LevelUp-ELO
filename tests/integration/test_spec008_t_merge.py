"""
Spec 008 delivery T, the owner's rule A (plan-t.md § Decision): ratings stored on the old fine
topics are merged into their coarse topic by a repair, never at start (spec 002 FR-018).

Per student and course, the fine rows of one coarse topic become one coarse row: the mean rating,
the mean RD (never below 30), approximate, with the fine keys as provenance. A coarse row the
student already has is never touched. The fine rows are copied to
`student_course_topic_elo_archive` and removed from the live store. Attempts are never touched.
Counts by default; writes only with `apply=True`. Both engines.
"""

import uuid

from tests.integration.conftest import make_student, set_rating, sql

FINE_A = "Pensamiento aleatorio — porcentaje sobre un total"
FINE_B = "Pensamiento aleatorio — frecuencia relativa como probabilidad"
FINE_N = "Pensamiento numérico — ecuaciones con decimales"


def _course(repo):
    course_id = f"spec008_merge_{uuid.uuid4().hex[:10]}"
    sql(
        repo,
        "INSERT INTO courses (id, name, block, description) VALUES (?, ?, 'Colegio', '')",
        (course_id, course_id),
    )
    return course_id


def _regrouping(course_id):
    return {
        course_id: {
            FINE_A: "Pensamiento aleatorio",
            FINE_B: "Pensamiento aleatorio",
            FINE_N: "Pensamiento numérico",
        }
    }


def _rows(repo, table, student, course_id):
    return {
        r[0]: (float(r[1]), float(r[2]), r[3])
        for r in sql(
            repo,
            f"SELECT topic, current_elo, rd, origin FROM {table}"
            " WHERE user_id = ? AND course_id = ?",
            (student, course_id),
        )
    }


def _seeded(repo):
    course_id = _course(repo)
    student = make_student(repo)
    set_rating(repo, student, course_id, FINE_A, 1100.0, rd=100.0, origin="practice")
    set_rating(repo, student, course_id, FINE_B, 1200.0, rd=20.0 + 30.0, origin="practice")
    set_rating(repo, student, course_id, FINE_N, 900.0, rd=200.0, origin="practice")
    set_rating(repo, student, course_id, "Pensamiento numérico", 1300.0, rd=80.0, origin="practice")
    return student, course_id


def test_spec008_count_only_writes_nothing(repo):
    student, course_id = _seeded(repo)
    before = _rows(repo, "student_course_topic_elo", student, course_id)

    assert repo.merge_fine_topic_ratings(_regrouping(course_id), apply=False) == 3

    assert _rows(repo, "student_course_topic_elo", student, course_id) == before
    assert _rows(repo, "student_course_topic_elo_archive", student, course_id) == {}


def test_spec008_apply_merges_by_the_mean_and_archives_the_fine_rows(repo):
    student, course_id = _seeded(repo)
    sql(
        repo,
        "INSERT INTO attempts (user_id, item_id, is_correct, elo_before, elo_after)"
        " VALUES (?, 'spec008_any', TRUE, 1000, 1010)",
        (student,),
    )

    assert repo.merge_fine_topic_ratings(_regrouping(course_id), apply=True) == 3

    live = _rows(repo, "student_course_topic_elo", student, course_id)
    assert live == {
        # mean of 1100 and 1200; mean RD of 100 and 50
        "Pensamiento aleatorio": (1150.0, 75.0, "legacy_topic_row"),
        # already there: untouched, the fine row is only archived
        "Pensamiento numérico": (1300.0, 80.0, "practice"),
    }
    merged = sql(
        repo,
        "SELECT approximate, legacy_source_key, reconciled_at FROM student_course_topic_elo"
        " WHERE user_id = ? AND course_id = ? AND topic = 'Pensamiento aleatorio'",
        (student, course_id),
    )[0]
    assert bool(merged[0]) and merged[2] is not None
    assert FINE_A in merged[1] and FINE_B in merged[1]
    assert set(_rows(repo, "student_course_topic_elo_archive", student, course_id)) == {
        FINE_A,
        FINE_B,
        FINE_N,
    }
    attempts = sql(repo, "SELECT COUNT(*) FROM attempts WHERE user_id = ?", (student,))[0][0]
    assert attempts == 1


def test_spec008_the_merged_rd_never_goes_below_30(repo):
    course_id = _course(repo)
    student = make_student(repo)
    set_rating(repo, student, course_id, FINE_A, 1000.0, rd=30.0, origin="practice")

    repo.merge_fine_topic_ratings(_regrouping(course_id), apply=True)

    assert (
        _rows(repo, "student_course_topic_elo", student, course_id)["Pensamiento aleatorio"][1]
        == 30.0
    )


def test_spec008_a_second_run_changes_nothing(repo):
    student, course_id = _seeded(repo)
    repo.merge_fine_topic_ratings(_regrouping(course_id), apply=True)
    after = _rows(repo, "student_course_topic_elo", student, course_id)

    assert repo.merge_fine_topic_ratings(_regrouping(course_id), apply=True) == 0
    assert _rows(repo, "student_course_topic_elo", student, course_id) == after


def test_spec008_the_repair_script_reads_the_committed_regrouping():
    """The script applies the regrouping recorded when the banks were edited: every old fine
    topic of DIAN and EPA8 maps to one of the bank's current topics."""
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    regrouping = json.loads(
        (root / "scripts" / "repairs" / "topic_regrouping_008t.json").read_text("utf-8")
    )
    for course_id, mapping in regrouping.items():
        bank = json.loads((root / "items" / "bank" / f"{course_id}.json").read_text("utf-8"))
        topics = {item["topic"] for item in bank}
        assert mapping and set(mapping.values()) <= topics, course_id
        assert not set(mapping) & topics, course_id
    assert set(regrouping) == {"DIAN", "evaluar_para_avanzar_8"}
