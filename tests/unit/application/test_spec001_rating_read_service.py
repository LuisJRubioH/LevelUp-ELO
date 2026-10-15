"""
Spec 001: RatingReadService with a fake repository (task T032; contracts/domain.md).

[CHANGE]: written before the service existed. The fake returns raw rows the way the
repositories do; every number below comes from the service and the domain functions.
"""

import pytest

from src.application.services.rating_read_service import RatingReadService


def _r(user_id, course_id, topic, elo):
    return {
        "user_id": user_id,
        "course_id": course_id,
        "topic": topic,
        "elo": elo,
        "rd": 350.0,
        "origin": "practice",
        "approximate": False,
    }


class FakeRepo:
    def __init__(
        self,
        rows=(),
        current=None,
        participants=(),
        group_course=None,
        enrollments=None,
        courses=("X", "Y", "Z"),
    ):
        self.rows = list(rows)
        self.current = current or {}
        self.participants = list(participants)
        self.group_course = group_course
        self.enrollments = enrollments or {}
        self.courses = courses
        self.participant_calls = []

    def get_course_topic_ratings(self, user_id, course_id=None):
        return [
            {k: v for k, v in r.items() if k != "user_id"}
            for r in self.get_course_topic_ratings_bulk([user_id], course_id)
        ]

    def get_course_topic_ratings_bulk(self, user_ids, course_id=None):
        return [
            r
            for r in self.rows
            if r["user_id"] in user_ids and (course_id is None or r["course_id"] == course_id)
        ]

    def get_current_context_course_ids(self, user_id):
        return self.current.get(user_id, [])

    def get_current_context_course_ids_bulk(self, user_ids):
        return {u: self.current.get(u, []) for u in user_ids}

    def get_ranking_participants(
        self, scope, group_id=None, course_id=None, education_level=None, grade=None, window_days=7
    ):
        self.participant_calls.append((scope, group_id, course_id, education_level, grade))
        return [dict(p) for p in self.participants]

    def get_group_course_id(self, group_id):
        return self.group_course

    def get_courses(self, block=None):
        return [{"id": c, "name": f"Curso {c}"} for c in self.courses]

    def get_user_enrollments(self, user_id):
        return [{"id": c} for c in self.enrollments.get(user_id, [])]


def _p(user_id, attempts=0):
    return {"user_id": user_id, "username": f"u{user_id}", "attempts_in_window": attempts}


# ── ratings_view (FR-028a/b/c, FR-028i, FR-028j, FR-029a) ──────────────────


def test_spec001_overall_is_the_mean_of_course_ratings():
    """US6-AS1: X has 1100 and 1300 (→ 1200), Y has 1000 → overall 1100, not 1133.33."""
    repo = FakeRepo(
        rows=[_r(1, "X", "a", 1100.0), _r(1, "X", "b", 1300.0), _r(1, "Y", "a", 1000.0)],
        current={1: ["X", "Y"]},
    )

    view = RatingReadService(repo).ratings_view(1)

    assert view["overall"] == 1100.0
    assert (view["display_rating"], view["rank_label"]) == (1100, "Oro II")
    assert view["overall_status"] == "rated"
    x = next(c for c in view["courses"] if c["course_id"] == "X")
    assert (x["course_name"], x["rating"], x["display_rating"], x["rank_label"]) == (
        "Curso X",
        1200.0,
        1200,
        "Oro I",
    )
    assert x["current_context"] is True
    assert sorted(t["topic"] for t in x["topics"]) == ["a", "b"]


def test_spec001_pending_diagnostic_and_history_courses():
    """US6-AS5/AS6: no rated current course → pending; an earlier-grade course stays visible."""
    repo = FakeRepo(rows=[_r(1, "X", "a", 1300.0)], current={1: ["Y"]})

    view = RatingReadService(repo).ratings_view(1)

    assert view["overall"] is None
    assert view["overall_status"] == "pending_diagnostic"
    assert (view["display_rating"], view["rank_label"]) == (None, None)
    by_id = {c["course_id"]: c for c in view["courses"]}
    assert by_id["X"]["current_context"] is False and by_id["X"]["rating"] == 1300.0
    assert by_id["Y"]["current_context"] is True and by_id["Y"]["rating"] is None


def test_spec001_full_precision_until_the_one_rounding():
    """FR-028i/j: averages are never rounded; 999.6 shows as 1000 "Plata I", kept as 999.6."""
    repo = FakeRepo(
        rows=[
            _r(1, "X", "a", 1200.4),
            _r(1, "X", "b", 1200.4),
            _r(1, "X", "c", 1201.4),
            _r(2, "X", "a", 999.6),
        ],
        current={1: ["X"], 2: ["X"]},
    )

    views = RatingReadService(repo).ratings_view_bulk([1, 2])

    assert views[1]["overall"] == pytest.approx(1200.7333333)
    assert views[1]["display_rating"] == 1201
    assert views[2]["overall"] == 999.6
    assert (views[2]["display_rating"], views[2]["rank_label"]) == (1000, "Plata I")


def test_spec001_course_rating_of():
    repo = FakeRepo(rows=[_r(1, "X", "a", 1100.0), _r(1, "X", "b", 1300.0)])
    service = RatingReadService(repo)

    assert service.course_rating_of(1, "X") == 1200.0
    assert service.course_rating_of(1, "Y") is None


# ── group_basis (FR-028d) ────────────────────────────────────────────────────


def test_spec001_group_basis_precedence():
    service = RatingReadService(FakeRepo(group_course="X", enrollments={7: ["Y"]}))
    student = {"user_id": 7, "role": "student"}

    assert service.group_basis(1, "Y", requester=student) == {
        "kind": "course",
        "course_id": "Y",
        "source": "requested",
    }
    assert service.group_basis(1) == {"kind": "course", "course_id": "X", "source": "group"}
    assert RatingReadService(FakeRepo()).group_basis(1) == {
        "kind": "overall",
        "course_id": None,
        "source": "overall",
    }
    with pytest.raises(ValueError):
        service.group_basis(1, "NOPE", requester=student)
    with pytest.raises(PermissionError):
        service.group_basis(1, "Z", requester=student)


# ── ranking_view / ranking_rank (FR-028d, FR-028f, FR-028h) ─────────────────


def test_spec001_group_ranking_on_the_group_course_without_substitution():
    """US6-AS7: A 1200 and B 1100 on course X; D unrated on X is pending, never ranked on Y."""
    repo = FakeRepo(
        rows=[
            _r(1, "X", "a", 1200.0),
            _r(2, "X", "a", 1100.0),
            _r(2, "Y", "a", 1900.0),
            _r(4, "Y", "a", 1500.0),
        ],
        current={1: ["X"], 2: ["X", "Y"], 4: ["Y"]},
        participants=[_p(4), _p(2), _p(1)],
        group_course="X",
    )

    ranking = RatingReadService(repo).ranking_view("group", group_id=9)

    assert ranking["basis"] == {"kind": "course", "course_id": "X", "source": "group"}
    assert [(e["user_id"], e["rating"], e["rank"], e["status"]) for e in ranking["entries"]] == [
        (1, 1200, 1, "rated"),
        (2, 1100, 2, "rated"),
        (4, None, None, "pending_diagnostic"),
    ]
    assert ranking["entries"][0]["rank_label"] == "Oro I"


def test_spec001_competition_ranks_and_limit():
    """US6-AS8: 1250, 1200, 1200, 1150 + pending → 1, 2, 2, 4, None; limit keeps ranks."""
    repo = FakeRepo(
        rows=[
            _r(1, "X", "a", 1250.0),
            _r(3, "X", "a", 1199.6),
            _r(2, "X", "a", 1200.2),
            _r(5, "X", "a", 1150.0),
        ],
        current={u: ["X"] for u in (1, 2, 3, 5, 6)},
        participants=[_p(1, 1), _p(2, 9), _p(3, 2), _p(5, 1), _p(6, 4)],
    )
    service = RatingReadService(repo)

    full = service.ranking_view("global")
    cut = service.ranking_view("global", limit=2)

    assert full["basis"] == {"kind": "overall", "course_id": None, "source": "overall"}
    assert [(e["user_id"], e["rating"], e["rank"]) for e in full["entries"]] == [
        (1, 1250, 1),
        (2, 1200, 2),
        (3, 1200, 2),
        (5, 1150, 4),
        (6, None, None),
    ]
    assert all(isinstance(e["rating"], int) for e in full["entries"][:4])
    assert [(e["user_id"], e["rank"]) for e in cut["entries"]] == [(1, 1), (2, 2)]
    assert service.ranking_rank(3, "global") == 2
    assert service.ranking_rank(6, "global") is None
    assert service.ranking_rank(99, "global") is None


def test_spec001_course_and_global_scopes_pass_their_filters():
    repo = FakeRepo(rows=[_r(1, "X", "a", 1000.0)], current={1: ["X"]}, participants=[_p(1, 3)])
    service = RatingReadService(repo)

    course = service.ranking_view("course", course_id="X")
    service.ranking_view("global", education_level="semillero", grade="6")

    assert course["basis"] == {"kind": "course", "course_id": "X", "source": "requested"}
    assert course["entries"][0]["attempts_in_window"] == 3
    assert repo.participant_calls == [
        ("course", None, "X", None, None),
        ("global", None, None, "semillero", "6"),
    ]
