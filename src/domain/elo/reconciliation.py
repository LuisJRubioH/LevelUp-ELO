"""Legacy-rating reconciliation plan (spec 001, FR-033–FR-036, FR-034a/b; research R10).

Pure function: the repositories read the raw tables, call `plan_reconciliation`, and insert the
rows it returns with `ON CONFLICT DO NOTHING`. Nothing here replays attempts (FR-036).
"""

from collections import defaultdict


def plan_reconciliation(
    legacy_rows, attempt_keys, diagnostics, course_topics, course_names, existing
) -> list[dict]:
    """Rows to create from legacy ratings.

    legacy_rows:   (user_id, key, elo, rd, updated_at) — a legacy row is keyed by one name that
                   may be a topic label, a course id or a course name.
    attempt_keys:  (user_id, course_id, topic, key) — an attempt on an item of (course_id, topic)
                   recorded under the legacy rating key `key`.
    diagnostics:   (user_id, course_id) — diagnostics taken.
    course_topics: (course_id, topic) of the catalogue's items.
    course_names:  {course_id: name}.
    existing:      (user_id, course_id, topic) already in the new store — never touched (FR-033).

    A (course, topic) is eligible when the student practised it or took that course's diagnostic
    (FR-034). Source (a): the row keyed by the topic label, if attempts on that course's items were
    recorded under that key or the diagnostic was taken. Source (b): the course's row (course id
    or course name, most recent `updated_at`, course id on a tie — FR-035), only if the topic was
    practised in that course. Never summed or averaged. Out-of-range legacy values are clamped to
    the store's invariants (rating ≥ 0, 30 ≤ RD ≤ 350).
    """
    legacy = {(u, key): (elo, rd, str(updated or "")) for u, key, elo, rd, updated in legacy_rows}
    practised = defaultdict(set)  # user → {(course, topic)}
    keys_on_course = defaultdict(set)  # user → {(course, key)}
    for u, course, topic, key in attempt_keys:
        practised[u].add((course, topic))
        keys_on_course[u].add((course, key))
    diagnosed = defaultdict(set)
    for u, course in diagnostics:
        diagnosed[u].add(course)
    topics_of = defaultdict(set)
    for course, topic in course_topics:
        topics_of[course].add(topic)
    done = set(existing)

    rows = []
    for u in sorted({u for u, _ in legacy}):
        eligible = set(practised[u])
        for course in diagnosed[u]:
            eligible |= {(course, topic) for topic in topics_of[course]}
        for course, topic in sorted(eligible):
            if (u, course, topic) in done:
                continue
            source = None
            if (u, topic) in legacy and (
                (course, topic) in keys_on_course[u] or course in diagnosed[u]
            ):
                source = ("legacy_topic_row", topic)
            elif (course, topic) in practised[u]:
                candidates = [k for k in dict.fromkeys((course, course_names.get(course))) if k]
                candidates = [k for k in candidates if (u, k) in legacy]
                if candidates:
                    best = max(candidates, key=lambda k: (legacy[(u, k)][2], k == course))
                    source = ("legacy_course_row", best)
            if source is None:
                continue
            elo, rd, _ = legacy[(u, source[1])]
            rows.append(
                {
                    "user_id": u,
                    "course_id": course,
                    "topic": topic,
                    "elo": max(0.0, float(elo)),
                    "rd": min(350.0, max(30.0, float(rd if rd is not None else 350.0))),
                    "origin": source[0],
                    "legacy_source_key": source[1],
                }
            )
    return rows
