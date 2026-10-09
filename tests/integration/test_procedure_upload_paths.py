"""
`save_procedure_submission` on both engines with a hostile exercise id: the row keeps the id the
student typed, but the Storage key (PostgreSQL) and the local fallback file stay inside the
student's folder / `data/uploads/procedures` (AGENTS R9). See test_storage_paths.py.
"""

from tests.integration.conftest import is_postgres, make_student, sql

HOSTILE = "../../999/victim"
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class _RecordingStorage:
    available = True

    def __init__(self):
        self.paths = []

    def upload_file(self, bucket, path, data, mime_type="image/jpeg"):
        self.paths.append(path)
        return path


class _NoStorage:
    available = False

    def upload_file(self, *args, **kwargs):
        return None


def test_storage_key_stays_in_the_students_folder(_postgres_repo, monkeypatch, tmp_path):
    # Storage exists on PostgreSQL only; SQLite keeps a local file (next test).
    repo = _postgres_repo
    monkeypatch.chdir(tmp_path)
    storage = _RecordingStorage()
    monkeypatch.setattr(repo, "_storage", storage)
    student = make_student(repo)

    repo.save_procedure_submission(student, HOSTILE, "c", PNG, "image/png", file_hash="h1")

    assert storage.paths == [f"{student}/_999_victim/h1.png"]
    stored = sql(
        repo,
        "SELECT item_id, storage_url FROM procedure_submissions WHERE student_id = ?",
        (student,),
    )
    assert stored == [(HOSTILE, f"{student}/_999_victim/h1.png")]


def test_local_fallback_file_stays_in_the_uploads_folder(repo, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    if is_postgres(repo):
        monkeypatch.setattr(repo, "_storage", _NoStorage())
    student = make_student(repo)

    repo.save_procedure_submission(student, HOSTILE, "c", PNG, "image/png", file_hash="h2")

    uploads = (tmp_path / "data" / "uploads" / "procedures").resolve()
    written = [p.resolve() for p in tmp_path.rglob("*.png")]
    assert len(written) == 1
    assert written[0].parent == uploads
    assert written[0].name.startswith(f"{student}__999_victim_")
    rows = sql(repo, "SELECT item_id FROM procedure_submissions WHERE student_id = ?", (student,))
    assert rows == [(HOSTILE,)]
    assert [p.name for p in (tmp_path / "data" / "uploads").iterdir()] == ["procedures"]
