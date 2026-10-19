"""
Spec 006 X2 (FR-033): a template's results from its stored responses.

Only the students the caller names count, each one on their first submission; the results are
given per student and per item, with the option each student chose and, per item, how many chose
each wrong option. Pure: the repository returns rows, this computes.
"""

from collections import OrderedDict


def _pct(correct: int, total: int) -> float:
    return round(correct / total * 100, 1) if total else 0.0


def template_results(rows: list[dict], students: dict[int, str]) -> dict:
    """`rows`: one per answered item — session_id, user_id, submitted_at, item_id, topic,
    content, is_correct, selected_option. `students`: the teacher's students, id → name."""
    first: dict[int, tuple] = {}
    for r in rows:
        if r["user_id"] not in students:
            continue
        key = (str(r["submitted_at"]), r["session_id"])
        if r["user_id"] not in first or key < first[r["user_id"]]:
            first[r["user_id"]] = key
    kept = [r for r in rows if r["user_id"] in first and r["session_id"] == first[r["user_id"]][1]]

    per_student: "OrderedDict[int, dict]" = OrderedDict()
    questions: "OrderedDict[str, dict]" = OrderedDict()
    topics: "OrderedDict[str, dict]" = OrderedDict()
    for r in sorted(kept, key=lambda r: (students[r["user_id"]], r["user_id"])):
        student = per_student.setdefault(
            r["user_id"],
            {
                "user_id": r["user_id"],
                "name": students[r["user_id"]],
                "submitted_at": str(r["submitted_at"]),
                "answers": [],
            },
        )
        student["answers"].append(
            {
                "item_id": r["item_id"],
                "is_correct": bool(r["is_correct"]),
                "selected_option": r["selected_option"],
            }
        )
        q = questions.setdefault(
            r["item_id"],
            {
                "item_id": r["item_id"],
                "content": r.get("content") or r["item_id"],
                "topic": r["topic"],
                "total": 0,
                "correct": 0,
                "choices": {},
            },
        )
        q["total"] += 1
        if r["is_correct"]:
            q["correct"] += 1
        elif r["selected_option"]:
            q["choices"][r["selected_option"]] = q["choices"].get(r["selected_option"], 0) + 1
        t = topics.setdefault(r["topic"] or "Sin tópico", {"total": 0, "correct": 0})
        t["total"] += 1
        t["correct"] += 1 if r["is_correct"] else 0

    for s in per_student.values():
        right = sum(1 for a in s["answers"] if a["is_correct"])
        s["correct"], s["total"] = right, len(s["answers"])
        s["score_pct"] = _pct(right, len(s["answers"]))
    for q in questions.values():
        q["accuracy"] = _pct(q["correct"], q["total"])
    topic_list = [
        {
            "topic": k,
            "total": v["total"],
            "correct": v["correct"],
            "accuracy": _pct(v["correct"], v["total"]),
        }
        for k, v in topics.items()
    ]
    scores = [s["score_pct"] for s in per_student.values()]
    question_list = list(questions.values())
    return {
        "n_sessions": len(per_student),
        "n_students": len(per_student),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0.0,
        "students": list(per_student.values()),
        "questions": question_list,
        "topics": topic_list,
        "best_question": max(question_list, key=lambda q: q["accuracy"], default=None),
        "worst_question": min(question_list, key=lambda q: q["accuracy"], default=None),
        "reinforce_topic": min(topic_list, key=lambda t: t["accuracy"], default=None),
    }
