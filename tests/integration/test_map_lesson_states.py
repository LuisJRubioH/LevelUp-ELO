"""
The course map and the lessons read the student's lesson progress in one query.

They used to read it node by node: 59 repository round trips per map for `algebra_basica`, each
costing about three network round trips on PostgreSQL (BEGIN, SELECT, the pool's ROLLBACK). With
a simulated 10 ms database round trip the map took 2 s, with 30 ms 5.6 s. The states, and so the
map and the lessons, must stay exactly what the per-node reads gave.
"""

from src.domain.learning.prealgebra import (
    N2_OPERATION_NODE_IDS,
    N3_HUB_NODE_ID,
    N3_MACHINE_NODE_IDS,
    curriculum_map_rows,
    get_lesson,
)
from tests.integration.conftest import make_student, headers_for

COURSE = "algebra_basica"
WELCOME = "PREALG-N1-B01-BIENVENIDA"
TRIGGER = "PREALG-N1-B02-PREGUNTA-DETONADORA"
STAIRCASE = "PREALG-N1-B03-ESCALERA-NECESIDAD"


def _progress(repo, user):
    repo.record_lesson_event(user, COURSE, WELCOME, "node_completed")
    repo.record_lesson_event(user, COURSE, TRIGGER, "node_completed")
    repo.record_lesson_event(user, COURSE, STAIRCASE, "node_viewed")


def _count_reads(repo, monkeypatch):
    """Counts connection checkouts and fails on any per-node progress read."""
    checkouts = []
    real_get_connection = repo.get_connection

    def counting_get_connection(*args, **kwargs):
        checkouts.append(1)
        return real_get_connection(*args, **kwargs)

    monkeypatch.setattr(repo, "get_connection", counting_get_connection)
    return checkouts


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
    headers = headers_for(repo, user)

    per_node_reads = []
    real_get_lesson_progress = repo.get_lesson_progress

    def recording_get_lesson_progress(*args):
        per_node_reads.append(args[-1])
        return real_get_lesson_progress(*args)

    monkeypatch.setattr(repo, "get_lesson_progress", recording_get_lesson_progress)
    checkouts = _count_reads(repo, monkeypatch)
    response = client.get(f"/api/student/map/{COURSE}", headers=headers)

    assert response.status_code == 200, response.text
    curriculum = response.json()["nodes"][: len(expected)]
    assert [(n["node_id"], n["state"]) for n in curriculum] == [
        (row["node_id"], row["state"]) for row in expected
    ]
    assert per_node_reads == []
    assert len(checkouts) <= 10, f"{len(checkouts)} repository reads for one map"


def test_the_laboratory_shows_each_machine_state_from_one_read(repo, client, monkeypatch):
    """N3: the level-2 check, the prerequisite and the machine states come from one snapshot."""
    user = make_student(repo)
    for node_id in N2_OPERATION_NODE_IDS:
        repo.record_lesson_event(user, COURSE, node_id, "node_completed")
    repo.record_lesson_event(user, COURSE, N3_HUB_NODE_ID, "node_completed")
    repo.record_lesson_event(user, COURSE, N3_MACHINE_NODE_IDS[0], "node_completed")
    repo.record_lesson_event(user, COURSE, N3_MACHINE_NODE_IDS[1], "node_viewed")
    headers = headers_for(repo, user)

    checkouts = _count_reads(repo, monkeypatch)
    response = client.get(f"/api/student/lessons/{COURSE}/{N3_HUB_NODE_ID}", headers=headers)

    assert response.status_code == 200, response.text
    machines = response.json()["content"]["machines"]
    assert [(m["node_id"], m["state"]) for m in machines] == list(
        zip(N3_MACHINE_NODE_IDS, ["completed", "current", "blocked", "blocked", "blocked"])
    )
    assert len(checkouts) <= 10, f"{len(checkouts)} repository reads for one lesson"


def test_a_machine_opens_in_the_request_that_repairs_the_laboratory(repo, client):
    """The snapshot is taken after the hub repair, so the repaired hub unlocks M01 at once."""
    user = make_student(repo)
    for node_id in N2_OPERATION_NODE_IDS:
        repo.record_lesson_event(user, COURSE, node_id, "node_completed")
    for interaction in get_lesson(N3_HUB_NODE_ID)["interactions"]:
        repo.save_lesson_interaction(
            user, COURSE, N3_HUB_NODE_ID, interaction["interaction_id"], "introduced", None, None
        )

    response = client.get(
        f"/api/student/lessons/{COURSE}/{N3_MACHINE_NODE_IDS[0]}", headers=headers_for(repo, user)
    )

    assert response.status_code == 200, response.text
    assert repo.get_lesson_progress(user, COURSE, N3_HUB_NODE_ID)["state"] == "completed"
