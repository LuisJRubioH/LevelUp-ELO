"""
src/interface/streamlit/rankings.py
===================================
V1 (frozen) rankings on the spec 001 model: RatingReadService.ranking_view rows in the shape V1's
tables already use. Who appears follows FR-028f; what they are ranked by is the derived rating;
ties share a rank (FR-028h); pending students come last without a rank.
"""

PENDING = "Diagnóstico pendiente"


def v1_ranking(ratings, scope: str, limit=None, **kwargs) -> list[dict]:
    view = ratings.ranking_view(scope, limit=limit, **kwargs)
    return [
        {
            "rank": e["rank"],
            "user_id": e["user_id"],
            "username": e["username"],
            "global_elo": e["rating"],
            "course_elo": e["rating"],
            "attempts_this_week": e["attempts_in_window"],
        }
        for e in view["entries"]
    ]


def v1_my_rank(ratings, user_id: int, scope: str, **kwargs) -> dict | None:
    """{rank, total_students} from the same list (FR-028f); None while pending or absent."""
    entries = ratings.ranking_view(scope, **kwargs)["entries"]
    rank = next((e["rank"] for e in entries if e["user_id"] == user_id), None)
    if rank is None:
        return None
    return {"rank": rank, "total_students": sum(1 for e in entries if e["rank"] is not None)}


def fmt_rating(value) -> str:
    """A ranking cell: the backend's whole number, or the pending text — never a placeholder."""
    return PENDING if value is None else f"{value:.0f}"


def fmt_position(rank, medals: dict) -> str:
    return "—" if rank is None else medals.get(rank, str(rank))
