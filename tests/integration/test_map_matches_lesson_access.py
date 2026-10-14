"""
The course map never offers a lesson the API refuses. The N3 laboratory and its machines open only
when all six N2 buildings are complete (the API's rule), but the map followed `unlock_after` alone
(the laboratory hangs from E06): a student who finished E06 first saw the laboratory available
and got 403 «Completa el Nivel 2 primero» on opening it (learning-path survey, L5).
"""

import pytest

from src.domain.learning.prealgebra import (
    N2_OPERATION_NODE_IDS,
    N3_HUB_NODE_ID,
    N3_MACHINE_NODE_IDS,
    _LESSONS,
)
from tests.integration.conftest import headers_for, make_student

COURSE = "algebra_basica"


def _ancestors(node_id):
    chain = []
    while _LESSONS[node_id].get("unlock_after"):
        node_id = _LESSONS[node_id]["unlock_after"]
        chain.append(node_id)
    return chain


def _complete(repo, user, node_ids):
    for node_id in node_ids:
        repo.record_lesson_event(user, COURSE, node_id, "node_completed")


@pytest.mark.parametrize(
    "done_in_level_2",
    [
        N2_OPERATION_NODE_IDS[-1:],  # only E06, the laboratory's own prerequisite
        N2_OPERATION_NODE_IDS[:-1],  # all but E06
        N2_OPERATION_NODE_IDS,  # the whole level
    ],
    ids=["only-E06", "all-but-E06", "all-six"],
)
def test_every_lesson_the_map_offers_opens(repo, client, done_in_level_2):
    user = make_student(repo)
    level_1_and_hub = [n for n in _ancestors(N3_HUB_NODE_ID) if n not in N2_OPERATION_NODE_IDS]
    _complete(repo, user, level_1_and_hub + list(done_in_level_2))
    headers = headers_for(repo, user)

    response = client.get(f"/api/student/map/{COURSE}", headers=headers)
    assert response.status_code == 200, response.text
    shown = {n["node_id"]: n["state"] for n in response.json()["nodes"] if n.get("node_id")}

    mismatches = []
    for node_id in [N3_HUB_NODE_ID, *N3_MACHINE_NODE_IDS, *N2_OPERATION_NODE_IDS]:
        opened = client.get(f"/api/student/lessons/{COURSE}/{node_id}", headers=headers)
        offered = shown[node_id] != "blocked"
        if offered != (opened.status_code == 200):
            mismatches.append((node_id, shown[node_id], opened.status_code))
    assert mismatches == []
    level_2_done = set(done_in_level_2) == set(N2_OPERATION_NODE_IDS)
    assert (shown[N3_HUB_NODE_ID] != "blocked") == level_2_done
