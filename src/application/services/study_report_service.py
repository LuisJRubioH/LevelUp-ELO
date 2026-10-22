"""
Spec 008 FR-042: a student's results per subtopic, across their courses — for study only. The
repository returns raw counts; nothing here reads or keys a rating.
"""


class StudyReportService:
    def __init__(self, repository):
        self.repository = repository

    def subtopic_report(self, user_id: int) -> list[dict]:
        """Each (course, topic, subtopic) with attempts, correct answers and the share correct,
        weakest first (then the most attempted)."""
        report = []
        for row in self.repository.get_subtopic_attempts(user_id):
            attempts, correct = int(row["attempts"]), int(row["correct"] or 0)
            report.append(
                {
                    "course_id": row["course_id"],
                    "course_name": row.get("course_name") or row["course_id"],
                    "topic": row["topic"],
                    "subtopic": row["subtopic"],
                    "attempts": attempts,
                    "correct": correct,
                    "share_correct": correct / attempts if attempts else 0.0,
                }
            )
        report.sort(
            key=lambda r: (r["share_correct"], -r["attempts"], r["course_id"], r["subtopic"])
        )
        return report
