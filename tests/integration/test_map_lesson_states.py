"""
The course map reads the student's lesson progress in one query.

It used to read it node by node: 59 repository round trips per map for `algebra_basica`, each
costing about three network round trips on PostgreSQL (BEGIN, SELECT, the pool's ROLLBACK). With
a simulated 10 ms database round trip the map took 2 s, with 30 ms 5.6 s. The states, and so the
map, must stay exactly what the per-node reads gave.
"""

from src.domain.learning.prealgebra import curriculum_map_rows
from tests.integration.conftest import make_student, headers_for

COURSE = "algebra_basica"
WELCOME = "PREALG-N1-B01-BIENVENIDA"
TRIGGER = "PREALG-N1-B02-PREGUNTA-DETONADORA"
STAIRCASE = "PREALG-N1-B03-ESCALERA-NECESIDAD"


def _progress(repo, user):
    repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")
    repo.record_lesson_event(user, COURSE, TRIGGER, "node_completed")
    repo.record_lesson_event(user, COURSE, STAIRCASE, "node_viewed")


def test_lesson_states_are_the_per_node_states_in_one_read(repo):
    user, other = make_student(repo), make_student(repo)
    _progress(repo, user)
    repo.record_lesson_event(other, COURSE, STAIRCASE, "node_completed")
    repo.record_lesson_event(user, "calculo_diferencial", STAIRCASE, "node_completed")

    assert repo.get_lesson_states(user, COURSE) == {
        WELCOME: "completed",
        TRIGGER: "completed",
        STAIRCASE: "viewed",
    }
    assert repo.get_lesson_states(make_student(repo), COURSE) == {}


def test_the_map_shows_the_same_states_with_a_bounded_number_of_reads(repo, client, monkeypatch):
    user = make_student(repo)
    _progress(repo, user)
    expected = curriculum_map_rows(
        lambda node_id: repo.get_lesson_progress(user, COURSE, node_id)["state"],
        complex_visible=False,
    )

    checkouts = []
    real_get_connection = repo.get_connection

    def counting_get_connection(*args, **kwargs):
        checkouts.append(1)
        return real_get_connection(*args, **kwargs)

    monkeypatch.setattr(repo, "get_connection", counting_get_connection)
    response = client.get(f"/api/student/map/{COURSE}", headers=headers_for(repo, user))

    assert response.status_code == 200, response.text
    curriculum = response.json()["nodes"][: len(expected)]
    assert [(n["topic"], n["state"]) for n in curriculum] == [
        (row["topic"], row["state"]) for row in expected
    ]
    assert len(checkouts) <= 10, f"{len(checkouts)} repository reads for one map"
