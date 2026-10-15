"""
The learning-path persistence on both engines. Production runs PostgreSQL, and until now only
SQLite exercised the lesson methods (docs/sdd/learning-path-survey.md, L12). These pins describe
today's behaviour; where the survey asks the owner to decide (§ 5), the test says which decision
would change it.
"""

from src.domain.learning.prealgebra import DIAGNOSTIC_NODE_IDS
from tests.integration.conftest import make_student, headers_for, sql

COURSE = "algebra_basica"
WELCOME = "PREALG-N1-B01-BIENVENIDA"
TRIGGER = "PREALG-N1-B02-PREGUNTA-DETONADORA"
REALS = "PREALG-N1-B08-REALES-RECTA"
COMPLEX = "PREALG-N1-B09-COMPLEJOS-PLANO"


def _lesson_url(node_id: str, action: str = "") -> str:
    return f"/api/student/lessons/{COURSE}/{node_id}" + (f"/{action}" if action else "")


# ── Repository ───────────────────────────────────────────────────────────────


def test_progress_without_a_row_reads_as_available(repo):
    user = make_student(repo)

    assert repo.get_lesson_progress(user, COURSE, WELCOME) == {
        "state": "available",
        "objectives_viewed": False,
        "math_convention_viewed": False,
        "viewed_at": None,
        "completed_at": None,
    }
    assert repo.get_lesson_interactions(user, COURSE, WELCOME) == {}


def test_lesson_events_only_move_forward(repo):
    user = make_student(repo)

    viewed = repo.record_lesson_event(user, COURSE, WELCOME, "node_viewed")
    assert viewed["state"] == "viewed"
    assert viewed["viewed_at"] is not None
    assert viewed["completed_at"] is None

    repo.record_lesson_event(user, COURSE, WELCOME, "objectives_viewed")
    repo.record_lesson_event(user, COURSE, WELCOME, "math_convention_viewed")
    completed = repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")
    again = repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")
    later_view = repo.record_lesson_event(user, COURSE, WELCOME, "node_viewed")

    assert completed["state"] == "completed"
    assert completed["completed_at"] is not None
    for progress in (again, later_view):
        assert progress["state"] == "completed"
        assert progress["objectives_viewed"] is True
        assert progress["math_convention_viewed"] is True
        assert progress["viewed_at"] == viewed["viewed_at"]
        assert progress["completed_at"] == completed["completed_at"]


def test_progress_is_kept_per_student_course_and_node(repo):
    user, other = make_student(repo), make_student(repo)

    repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")

    assert repo.get_lesson_progress(user, COURSE, WELCOME)["state"] == "completed"
    assert repo.get_lesson_progress(other, COURSE, WELCOME)["state"] == "available"
    assert repo.get_lesson_progress(user, "calculo_diferencial", WELCOME)["state"] == "available"
    assert repo.get_lesson_progress(user, COURSE, TRIGGER)["state"] == "available"


def test_interactions_round_trip_on_both_engines(repo):
    user = make_student(repo)

    repo.save_lesson_interaction(user, COURSE, TRIGGER, "Q-right", "no", True, None)
    repo.save_lesson_interaction(
        user, COURSE, TRIGGER, "Q-wrong", "yes", False, "cree_que_todo_numero_sirve_para_contar"
    )
    repo.save_lesson_interaction(user, COURSE, TRIGGER, "Q-open", "debt", None, None)

    assert repo.get_lesson_interactions(user, COURSE, TRIGGER) == {
        "Q-right": {
            "interaction_id": "Q-right",
            "selected_option": "no",
            "is_expected": True,
            "misconception_tag": None,
        },
        "Q-wrong": {
            "interaction_id": "Q-wrong",
            "selected_option": "yes",
            "is_expected": False,
            "misconception_tag": "cree_que_todo_numero_sirve_para_contar",
        },
        "Q-open": {
            "interaction_id": "Q-open",
            "selected_option": "debt",
            "is_expected": None,
            "misconception_tag": None,
        },
    }
    assert repo.get_lesson_interactions(user, COURSE, WELCOME) == {}


def test_answering_again_replaces_the_earlier_answer(repo):
    """Survey L8: no history is kept. Decision § 5.4 (keep an answer history) would change it."""
    user = make_student(repo)

    repo.save_lesson_interaction(user, COURSE, TRIGGER, "Q", "yes", False, "a_misconception")
    repo.save_lesson_interaction(user, COURSE, TRIGGER, "Q", "no", True, None)

    assert repo.get_lesson_interactions(user, COURSE, TRIGGER) == {
        "Q": {
            "interaction_id": "Q",
            "selected_option": "no",
            "is_expected": True,
            "misconception_tag": None,
        }
    }
    rows = sql(
        repo,
        "SELECT COUNT(*) FROM lesson_interactions WHERE user_id = ? AND node_id = ?",
        (user, TRIGGER),
    )
    assert rows[0][0] == 1


def test_lesson_writes_never_touch_ratings_or_attempts(repo):
    user = make_student(repo)

    repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")
    repo.save_lesson_interaction(user, COURSE, TRIGGER, "Q", "no", True, None)

    for table in ("student_course_topic_elo", "student_topic_elo", "attempts"):
        count = sql(repo, f"SELECT COUNT(*) FROM {table} WHERE user_id = ?", (user,))[0][0]
        assert count == 0, table


# ── HTTP, on the engine under test ───────────────────────────────────────────


def test_a_node_completes_only_after_its_questions_are_answered(repo, client):
    user = make_student(repo)
    headers = headers_for(repo, user)
    repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")

    opened = client.get(_lesson_url(TRIGGER), headers=headers)
    assert opened.status_code == 200, opened.text
    assert opened.json()["state"] == "available"

    early = client.post(
        _lesson_url(TRIGGER, "events"), json={"event": "node_completed"}, headers=headers
    )
    assert early.status_code == 409, early.text

    for interaction_id, option in (("PREALG-N1-B02-Q01", "no"), ("PREALG-N1-B02-Q02", "debt")):
        answered = client.post(
            _lesson_url(TRIGGER, "interactions"),
            json={"interaction_id": interaction_id, "selected_option": option},
            headers=headers,
        )
        assert answered.status_code == 200, answered.text

    done = client.post(
        _lesson_url(TRIGGER, "events"), json={"event": "node_completed"}, headers=headers
    )
    assert done.status_code == 200, done.text
    body = done.json()
    assert body["state"] == "completed"
    assert set(body["progress"]["responses"]) == {"PREALG-N1-B02-Q01", "PREALG-N1-B02-Q02"}
    assert repo.get_lesson_progress(user, COURSE, TRIGGER)["state"] == "completed"


def test_a_locked_node_can_be_neither_read_nor_written(repo, client):
    user = make_student(repo)
    headers = headers_for(repo, user)

    responses = [
        client.get(_lesson_url(TRIGGER), headers=headers),
        client.post(_lesson_url(TRIGGER, "events"), json={"event": "node_viewed"}, headers=headers),
        client.post(
            _lesson_url(TRIGGER, "interactions"),
            json={"interaction_id": "PREALG-N1-B02-Q01", "selected_option": "no"},
            headers=headers,
        ),
    ]

    assert [response.status_code for response in responses] == [403, 403, 403]
    assert repo.get_lesson_progress(user, COURSE, TRIGGER)["state"] == "available"
    assert repo.get_lesson_interactions(user, COURSE, TRIGGER) == {}


def test_the_complex_numbers_node_opens_from_the_intermediate_band(repo, client):
    user = make_student(repo)
    headers = headers_for(repo, user)
    repo.record_lesson_event(user, COURSE, REALS, "node_completed")

    without_diagnostic = client.get(_lesson_url(COMPLEX), headers=headers)
    assert without_diagnostic.status_code == 403, without_diagnostic.text

    repo.save_diagnostic(user, COURSE, 1000.0, 49.9, "{}")
    assert client.get(_lesson_url(COMPLEX), headers=headers).status_code == 403

    repo.save_diagnostic(user, COURSE, 1000.0, 50.0, "{}")
    opened = client.get(_lesson_url(COMPLEX), headers=headers)
    assert opened.status_code == 200, opened.text
    assert opened.json()["presentation"] == "intermedio"


# ── The N1 closing summary (B13), survey L10 ─────────────────────────────────

N1_FOCAL = {
    "PREALG-N1-B04-NATURALES-CONTAR": "cero_no_es_numero",
    "PREALG-N1-B05-ENTEROS-DEUDA": "magnitud_sin_signo",
    "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION": "decimal_truncado_es_el_numero",
    "PREALG-N1-B07-IRRACIONALES-DECIMALES": "decimal_infinito_es_irracional",
    "PREALG-N1-B08-REALES-RECTA": "existe_el_siguiente",
}


def _summary(client, headers):
    response = client.get(f"/api/student/prealgebra-summary/{COURSE}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_summary_of_a_new_student_leaves_the_optional_node_out(repo, client):
    user = make_student(repo)

    assert _summary(client, headers_for(repo, user)) == {
        "course_id": COURSE,
        "completed_nodes": 0,
        "total_nodes": len(DIAGNOSTIC_NODE_IDS) - 1,
        "overall_status": "review",
        "review": [],
    }


def test_summary_counts_the_optional_node_once_it_is_explored(repo, client):
    user = make_student(repo)
    repo.record_lesson_event(user, COURSE, COMPLEX, "node_viewed")

    assert _summary(client, headers_for(repo, user))["total_nodes"] == len(DIAGNOSTIC_NODE_IDS)


def test_summary_is_strong_when_every_node_is_done_without_misconceptions(repo, client):
    user = make_student(repo)
    for node_id in DIAGNOSTIC_NODE_IDS:
        if node_id != COMPLEX:
            repo.record_lesson_event(user, COURSE, node_id, "node_completed")

    summary = _summary(client, headers_for(repo, user))

    assert summary["completed_nodes"] == summary["total_nodes"] == len(DIAGNOSTIC_NODE_IDS) - 1
    assert summary["overall_status"] == "strong"
    assert summary["review"] == []


def test_summary_sends_a_misconception_to_the_node_that_teaches_it(repo, client):
    user = make_student(repo)
    node_id = "PREALG-N1-B05-ENTEROS-DEUDA"
    repo.save_lesson_interaction(user, COURSE, node_id, "Q", "x", False, N1_FOCAL[node_id])

    summary = _summary(client, headers_for(repo, user))

    assert summary["overall_status"] == "review"
    assert summary["review"] == [{"node_id": node_id, "label_key": "prealgebra.n1.b05.mapTitle"}]


def test_summary_lists_at_most_four_nodes_in_route_order(repo, client):
    user = make_student(repo)
    for node_id, tag in reversed(list(N1_FOCAL.items())):
        repo.save_lesson_interaction(user, COURSE, node_id, "Q", "x", False, tag)

    summary = _summary(client, headers_for(repo, user))

    assert summary["overall_status"] == "attention"
    assert [entry["node_id"] for entry in summary["review"]] == list(N1_FOCAL)[:4]
