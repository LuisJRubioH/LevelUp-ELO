"""
Survey 007 V14: `/api/student/pvp/history` sends the shown delta (half up, spec 001 FR-028j)
next to the applied one. Both engines.
"""

from tests.integration.conftest import headers_for, make_student, set_rating

COURSE, TOPIC = "calculo_diferencial", "Límites"


def test_the_history_sends_the_shown_delta(repo, client):
    a, b = make_student(repo, "universidad"), make_student(repo, "universidad")
    set_rating(repo, a, COURSE, TOPIC, 1000.0)
    set_rating(repo, b, COURSE, TOPIC, 1000.0)
    match_id = repo.create_pvp_match(COURSE, a, b, ["i1"])
    repo.finish_pvp_match(
        match_id=match_id,
        winner_id=b,
        score_p1=0,
        score_p2=1,
        elo_delta_p1=-2.5,
        elo_delta_p2=2.5,
        p1_id=a,
        p2_id=b,
    )

    response = client.get("/api/student/pvp/history", headers=headers_for(repo, a))

    assert response.status_code == 200, response.text
    row = response.json()[0]
    assert (row["elo_delta"], row["elo_delta_display"]) == (-2.5, -3)
