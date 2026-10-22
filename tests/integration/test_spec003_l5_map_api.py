"""
Spec 003 L5 (FR-050, SC-003; US5-AS2; N3, N4): the map and the API read the same rules.

Over every node of the catalogue, a set of progress states and two diagnostic bands, the map
shows a node blocked (or hides it) exactly when the API refuses to open it. Every hub completes on
the server once all its cards are opened, and practice topics are never blocked by the path.
Both engines.
"""

import pytest

from src.domain.learning import prealgebra
from tests.integration.conftest import enroll, headers_for, make_student, sql

COURSE = "algebra_basica"
ALL = list(prealgebra._LESSONS)
N1 = [n for n in ALL if n.startswith("PREALG-N1-")]
N2 = [n for n in ALL if n.startswith("PREALG-N2-")]

PROGRESS_SETS = {
    "nothing": [],
    "level-1": N1,
    "level-2-but-E06": N1 + [n for n in N2 if not n.startswith("PREALG-N2-E06")],
    "all-but-last": ALL[:-1],
}


def _student_with(repo, completed, score_pct=None):
    user = make_student(repo)
    enroll(repo, user, COURSE)
    for node_id in completed:
        sql(
            repo,
            "INSERT INTO lesson_progress (user_id, course_id, node_id, state) "
            "VALUES (?, ?, ?, 'completed')",
            (user, COURSE, node_id),
        )
    if score_pct is not None:
        sql(
            repo,
            "INSERT INTO diagnostics (user_id, course_id, initial_elo, score_pct) "
            "VALUES (?, ?, 1000, ?)",
            (user, COURSE, score_pct),
        )
    return user


@pytest.mark.parametrize("band_score", [10.0, 60.0], ids=["basico", "intermedio"])
@pytest.mark.parametrize("progress", list(PROGRESS_SETS), ids=list(PROGRESS_SETS))
def test_map_and_api_agree_over_every_node_and_progress_set(repo, client, progress, band_score):
    """US5-AS2, FR-050, SC-003: map blocked or hidden ⇔ API 403, node by node."""
    user = _student_with(repo, PROGRESS_SETS[progress], band_score)
    headers = headers_for(repo, user)
    shown = {
        n["node_id"]: n["state"]
        for n in client.get(f"/api/student/map/{COURSE}", headers=headers).json()["nodes"]
        if n.get("node_id")
    }
    disagreements = []
    for node_id in ALL:
        offered = node_id in shown and shown[node_id] != "blocked"
        opened = client.get(f"/api/student/lessons/{COURSE}/{node_id}", headers=headers)
        if offered != (opened.status_code == 200):
            disagreements.append((node_id, shown.get(node_id, "hidden"), opened.status_code))
    assert disagreements == []


HUBS = [
    n for n, lesson in prealgebra._LESSONS.items() if lesson["node_type"].startswith("level_hub")
]


@pytest.mark.parametrize("hub", HUBS)
def test_every_hub_completes_when_its_cards_are_opened(repo, client, hub):
    """N3: one server rule — a hub completes when every card is opened, for all five hubs."""
    route = list(prealgebra._LESSONS)
    user = _student_with(repo, route[: route.index(hub)])
    headers = headers_for(repo, user)
    for interaction in prealgebra._LESSONS[hub]["interactions"]:
        response = client.post(
            f"/api/student/lessons/{COURSE}/{hub}/interactions",
            headers=headers,
            json={
                "interaction_id": interaction["interaction_id"],
                "selected_option": interaction["option_keys"][0],
            },
        )
        assert response.status_code == 200, response.text
    state = sql(
        repo,
        "SELECT state FROM lesson_progress WHERE user_id = ? AND node_id = ?",
        (user, hub),
    )
    assert state and state[0][0] == "completed"


def test_practice_topics_are_not_blocked_by_the_path(repo, client):
    """N4: practice ignores the path (spec 001), so the map does not block its topics."""
    user = _student_with(repo, [])
    nodes = client.get(f"/api/student/map/{COURSE}", headers=headers_for(repo, user)).json()[
        "nodes"
    ]
    topics = [n for n in nodes if not n.get("node_id")]
    assert topics, "the course has practice topics"
    assert all(n["state"] != "blocked" for n in topics)
