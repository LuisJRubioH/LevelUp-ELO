"""Derived ratings (spec 001, FR-028a, FR-029a). Full precision: nothing here rounds (FR-028i)."""

from statistics import fmean


def course_rating(topic_ratings: list[float]) -> float | None:
    """Mean of a course's stored topic ratings; None when the course has none."""
    return fmean(topic_ratings) if topic_ratings else None


def overall_rating(course_ratings: list[float | None]) -> float | None:
    """Equal-weight mean of the rated current courses; None = pending diagnostic (FR-028b)."""
    rated = [r for r in course_ratings if r is not None]
    return fmean(rated) if rated else None
