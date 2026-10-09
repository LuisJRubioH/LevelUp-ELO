"""
The teacher's image endpoint falls back to the bytes kept in the submission row when the Storage
download fails (AGENTS R9: if Storage fails, use `image_data`). Found by the persistence survey
(docs/sdd/persistence-survey.md, P10): on PostgreSQL the teacher queue returns `image_data` only
when `storage_url` is NULL, so a failed download answered 404 although the bytes were stored.
"""

import uuid

from api.routers import teacher as teacher_router
from tests.integration.conftest import is_postgres, sql

PNG = b"\x89PNG\r\n\x1a\n" + b"bytes kept in the row"


class _StorageDown:
    """Uploads succeed, downloads fail — a Storage outage after the student submitted."""

    available = True

    def upload_file(self, bucket, path, data, mime_type="image/jpeg"):
        return path

    def get_file(self, bucket, path):
        return None


def _user_id(repo, username) -> int:
    return sql(repo, "SELECT id FROM users WHERE username = ?", (username,))[0][0]


def _teacher_and_student(repo):
    suffix = uuid.uuid4().hex[:10]
    ok, msg = repo.register_user(f"img_teacher_{suffix}", "password123", role="teacher")
    assert ok, msg
    teacher_id = _user_id(repo, f"img_teacher_{suffix}")
    repo.approve_teacher(teacher_id)
    ok, msg, group_id = repo.create_group(f"img group {suffix}", teacher_id)
    assert ok, msg
    ok, msg = repo.register_user(
        f"img_student_{suffix}",
        "password123",
        role="student",
        group_id=group_id,
        education_level="colegio",
    )
    assert ok, msg
    student_id = _user_id(repo, f"img_student_{suffix}")
    return teacher_id, student_id


def test_image_falls_back_to_the_row_when_storage_fails(repo, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # the SQLite engine also writes a local copy
    if is_postgres(repo):
        monkeypatch.setattr(repo, "_storage", _StorageDown())
    teacher_id, student_id = _teacher_and_student(repo)
    item_id = sql(repo, "SELECT id FROM items ORDER BY id LIMIT 1")[0][0]
    repo.save_procedure_submission(
        student_id, item_id, "statement", PNG, "image/png", file_hash=uuid.uuid4().hex
    )
    submission_id = sql(
        repo, "SELECT id FROM procedure_submissions WHERE student_id = ?", (student_id,)
    )[0][0]

    response = teacher_router.procedure_image(
        submission_id, {"user_id": teacher_id, "role": "teacher"}, repo
    )

    assert response.status_code == 200
    assert response.body == PNG
