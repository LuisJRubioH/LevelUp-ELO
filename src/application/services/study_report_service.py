"""
Spec 008 FR-042: a student's results per subtopic, across their courses — for study only. The
repository returns raw counts; nothing here reads or keys a rating.

Spec 007 FR-070: the League's answers, counted per topic and per item by the domain and marked as
League answers — beside the practice figures, never inside them.
"""

from src.domain.pvp.answer_stats import league_export_rows, league_summary


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

    def league_report(self, user_id: int) -> dict:
        """Spec 007 FR-070: the student's League answers per topic and the most-missed items."""
        return self._with_statements(league_summary(self.repository.get_league_answers(user_id)))

    def teacher_league_report(self, teacher_id: int, student_id: int) -> dict:
        """Spec 007 FR-070, O-S5: the same report for one of the teacher's students, in the
        courses that link them."""
        rows = self.repository.get_teacher_league_answers(teacher_id, student_id)
        return self._with_statements(league_summary(rows))

    def teacher_league_export(self, teacher_id: int) -> list[dict]:
        """Spec 007 O-S4: the workbook's «Liga» sheet, one row per student, course, topic, item."""
        return league_export_rows(self.repository.get_teacher_league_answers(teacher_id))

    def _with_statements(self, summary: dict) -> dict:
        """The most-missed items get their statement to study (O-S3): the text, the options and
        the image as the match showed them — never the key or the difficulty (FR-032)."""
        for item in summary["items"]:
            stored = self.repository.get_item_by_id(item["item_id"]) or {}
            item["content"] = stored.get("content") or ""
            item["options"] = stored.get("options") or []
            item["image_url"] = stored.get("image_url")
        return summary
