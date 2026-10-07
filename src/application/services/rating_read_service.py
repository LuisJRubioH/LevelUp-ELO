"""
The one place that turns stored rating rows into course ratings, overall ratings, ranks and
rankings (spec 001, contracts/domain.md). Orchestration only: the arithmetic is the domain's
(`src/domain/elo/aggregation.py`, `ranks.py`); the repository returns raw rows and participants.
"""

from collections import defaultdict

from src.application.interfaces.repositories import IRatingReadRepository
from src.domain.elo.aggregation import course_rating, overall_rating
from src.domain.elo.model import rating_delta
from src.domain.elo.ranks import RANKS, rank_competition, rating_display

_OVERALL = {"kind": "overall", "course_id": None, "source": "overall"}


def rank_scale() -> list[dict]:
    """The single 16-level scale, ascending, as served by GET /api/meta/ranks (FR-031)."""
    return [{"label": label, "min": float(minimum)} for minimum, label in RANKS]


class RatingReadService:
    def __init__(self, repository: IRatingReadRepository):
        self.repository = repository

    # ── A student's ratings ──────────────────────────────────────────────────

    def ratings_view(self, user_id: int) -> dict:
        return self.ratings_view_bulk([user_id])[user_id]

    def ratings_view_bulk(self, user_ids: list[int]) -> dict:
        """Per student: overall (FR-028a/b), courses current and past (FR-028c), topics.

        `overall`/`rating` keep full precision; `display_rating` and `rank_label` come from one
        half-up rounding of that value (FR-028i, FR-028j).
        """
        rows = self.repository.get_course_topic_ratings_bulk(user_ids)
        current = self.repository.get_current_context_course_ids_bulk(user_ids)
        names = {c["id"]: c["name"] for c in self.repository.get_courses()}
        by_user = defaultdict(lambda: defaultdict(list))
        for row in rows:
            by_user[row["user_id"]][row["course_id"]].append(row)

        views = {}
        for user_id in user_ids:
            topics_by_course = by_user[user_id]
            current_ids = current.get(user_id, [])
            courses = []
            for course_id in dict.fromkeys([*current_ids, *sorted(topics_by_course)]):
                topic_rows = topics_by_course.get(course_id, [])
                rating = course_rating([r["elo"] for r in topic_rows])
                courses.append(
                    {
                        "course_id": course_id,
                        "course_name": names.get(course_id, course_id),
                        "rating": rating,
                        **rating_display(rating),
                        "current_context": course_id in current_ids,
                        "topics": [
                            {k: r[k] for k in ("topic", "elo", "rd", "origin", "approximate")}
                            for r in topic_rows
                        ],
                    }
                )
            overall = overall_rating([c["rating"] for c in courses if c["current_context"]])
            views[user_id] = {
                "overall": overall,
                **rating_display(overall),
                "overall_status": "pending_diagnostic" if overall is None else "rated",
                "courses": courses,
            }
        return views

    def course_rating_of(self, user_id: int, course_id: str) -> float | None:
        """The derived course rating; None when the course has no rated topic (FR-029a)."""
        rows = self.repository.get_course_topic_ratings(user_id, course_id=course_id)
        return course_rating([r["elo"] for r in rows])

    def selection_rating(self, user_id: int, course_id: str, topic=None) -> float:
        """The rating item selection uses (FR-016–019): the topic's rating when practising one
        topic, otherwise the derived course rating; 1000 when nothing is rated (FR-004)."""
        rows = self.repository.get_course_topic_ratings(user_id, course_id=course_id)
        if topic is not None:
            rows = [r for r in rows if r["topic"] == topic]
        rating = course_rating([r["elo"] for r in rows])
        return 1000.0 if rating is None else rating

    def answer_preview(self, user_id: int, course_id: str, item: dict) -> dict:
        """The change the engine will apply for each outcome (FR-030): the same formula as the
        update, on the item's (course, topic) rating — 1000/350 when unrated (FR-004)."""
        rows = self.repository.get_course_topic_ratings(user_id, course_id=course_id)
        row = next((r for r in rows if r["topic"] == item["topic"]), None)
        rating, rd = (row["elo"], row["rd"]) if row else (1000.0, 350.0)
        difficulty = float(item["difficulty"])
        return {
            "on_correct": round(rating_delta(rating, rd, difficulty, 1.0), 1),
            "on_wrong": round(rating_delta(rating, rd, difficulty, 0.0), 1),
        }

    # ── Rankings ─────────────────────────────────────────────────────────────

    def group_basis(self, group_id: int, requested_course_id=None, requester=None) -> dict:
        """Requested course → the group's course → overall (FR-028d, research R19).

        Unknown requested course → ValueError (400); a student requester not enrolled in it →
        PermissionError (403).
        """
        if requested_course_id is not None:
            if requested_course_id not in {c["id"] for c in self.repository.get_courses()}:
                raise ValueError(f"Unknown course {requested_course_id!r}.")
            if requester is not None and requester.get("role") == "student":
                enrolled = {
                    e["id"] for e in self.repository.get_user_enrollments(requester["user_id"])
                }
                if requested_course_id not in enrolled:
                    raise PermissionError("The student is not enrolled in that course.")
            return {"kind": "course", "course_id": requested_course_id, "source": "requested"}
        group_course = self.repository.get_group_course_id(group_id)
        if group_course:
            return {"kind": "course", "course_id": group_course, "source": "group"}
        return dict(_OVERALL)

    def ranking_view(
        self,
        scope: str,
        *,
        group_id=None,
        course_id=None,
        education_level=None,
        grade=None,
        limit=None,
        requester=None,
    ) -> dict:
        """Who appears comes from the repository; what they are ranked by is one basis for all.

        Participants without a rating on the basis are pending, last, unranked — never ranked on
        another rating (FR-028d). `limit` shortens the list after ranking (FR-028h).
        """
        if scope in ("group", "weekly"):
            basis = self.group_basis(group_id, course_id, requester)
        elif scope == "course":
            basis = {"kind": "course", "course_id": course_id, "source": "requested"}
        else:
            basis = dict(_OVERALL)
        participants = self.repository.get_ranking_participants(
            scope,
            group_id=group_id,
            course_id=course_id if scope == "course" else None,
            education_level=education_level,
            grade=grade,
        )
        ratings = self._basis_ratings([p["user_id"] for p in participants], basis)
        entries = rank_competition(
            [{**p, "rating": ratings.get(p["user_id"])} for p in participants]
        )
        for entry in entries:
            entry["status"] = "pending_diagnostic" if entry["rank"] is None else "rated"
        return {"basis": basis, "entries": entries if limit is None else entries[:limit]}

    def ranking_rank(self, user_id: int, scope: str, **kwargs) -> int | None:
        """The rank on the student's own entry of the unlimited list (FR-028f, FR-028h)."""
        kwargs.pop("limit", None)
        entries = self.ranking_view(scope, **kwargs)["entries"]
        return next((e["rank"] for e in entries if e["user_id"] == user_id), None)

    def _basis_ratings(self, user_ids: list[int], basis: dict) -> dict:
        if not user_ids:
            return {}
        if basis["kind"] == "overall":
            views = self.ratings_view_bulk(user_ids)
            return {u: views[u]["overall"] for u in user_ids}
        per_user = defaultdict(list)
        for row in self.repository.get_course_topic_ratings_bulk(user_ids, basis["course_id"]):
            per_user[row["user_id"]].append(row["elo"])
        return {u: course_rating(per_user[u]) for u in user_ids}
