"""Local readiness probes. Uses a fresh disposable SQLite DB, never remote services.

Run from repository root: python scripts/audit_production_readiness.py
Writes sanitized evidence to docs/auditoria-produccion-evidencia.json.
Exit 1 means at least one readiness check failed (expected before remediation).
"""

import contextlib
import io
import json
import logging
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.update(
    TESTING="1",
    PYTHON_DOTENV_DISABLED="1",
    DATABASE_URL="",
    JWT_SECRET_KEY="audit-only-disposable-local-key-not-for-deployment",
    ADMIN_PASSWORD="audit-local-admin-only",
    SYSTEM_AI_API_KEY="",
    AI_KEY_KATIA="",
    AI_KEY_PROCEDURE="",
    AI_KEY_TEACHER_ANALYSIS="",
    AI_KEY_STUDENT_ANALYSIS="",
    SUPABASE_URL="",
    SUPABASE_KEY="",
)


@contextlib.contextmanager
def database(repo):
    with contextlib.closing(repo.get_connection()) as conn:
        with conn:
            yield conn


def run():
    from starlette.testclient import TestClient
    from api.main import app
    import api.dependencies as deps
    from src.application.services.rating_read_service import RatingReadService
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    logging.disable(logging.CRITICAL)
    results = []

    def record(name, passed, observed):
        results.append({"check": name, "status": "PASS" if passed else "FAIL", "observed": observed})

    # Never reuse, migrate or delete a user DB. Only this new temporary directory.
    (ROOT / ".tmp").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="readiness-", dir=ROOT / ".tmp") as temp:
        with contextlib.redirect_stdout(io.StringIO()):
            repo = SQLiteRepository(str(Path(temp) / "audit.db"))
        deps._repo_instance = repo
        # No lifespan is required: the isolated repository was initialized above.
        client = TestClient(app, base_url="https://audit.local", raise_server_exceptions=False)
        try:
            login = client.post("/api/auth/login", json={"username": "estudiante1", "password": "demo1234"})
            assert login.status_code == 200, "Local fixture login failed"
            student = login.json()["user_id"]
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
            teacher_login = client.post("/api/auth/login", json={"username": "profesor1", "password": "demo1234"})
            teacher_id = teacher_login.json()["user_id"]
            teacher_headers = {"Authorization": "Bearer " + teacher_login.json()["access_token"]}

            cookie_path = next(c.path for c in client.cookies.jar if c.name == "levelup_refresh")
            record("refresh_cookie_path", cookie_path.startswith("/api/auth"), {"path": cookie_path})
            refresh = client.post("/api/auth/refresh")
            record("browser_cookie_refresh", refresh.status_code == 200, {"http": refresh.status_code})

            original_get_repository = deps.get_repository
            try:
                def unavailable_repository():
                    raise RuntimeError("private readiness detail")

                deps.get_repository = unavailable_repository
                degraded = client.get("/api/health")
            finally:
                deps.get_repository = original_get_repository
            record(
                "readiness_fails_closed",
                degraded.status_code == 503 and "private readiness detail" not in degraded.text,
                {"http": degraded.status_code},
            )

            from api.config import Settings

            insecure = Settings(
                _env_file=None,
                environment="production",
                database_url="postgresql://db.example/levelup",
                jwt_secret_key="short",
                cors_origins=["https://app.example"],
                rate_limit_storage_uri="redis://cache.example:6379/0",
            )
            try:
                insecure.validate_runtime()
                rejected = False
            except RuntimeError:
                rejected = True
            record("production_config_fails_closed", rejected, {"rejected": rejected})

            from api.rate_limit import limiter

            limiter._storage.reset()
            ai_probe = {
                "item_id": "rate-limit-probe",
                "item_content": "probe",
                "student_message": "Ayúdame",
            }
            limited = [
                client.post("/api/ai/socratic", headers=headers, json=ai_probe).status_code
                for _ in range(11)
            ]
            limiter._storage.reset()
            record(
                "ai_rate_limit_enforced",
                limited[:10] == [422] * 10 and limited[10] == 429,
                {"http": limited},
            )

            auth_limited = [
                client.post(
                    "/api/auth/login",
                    json={"username": "audit-missing", "password": "invalid-password"},
                ).status_code
                for _ in range(21)
            ]
            limiter._storage.reset()
            record(
                "auth_rate_limit_enforced",
                auth_limited[:20] == [401] * 20 and auth_limited[20] == 429,
                {"last_http": auth_limited[-1]},
            )

            cache_files = [
                ROOT / "frontend/src/pages/Layout.tsx",
                ROOT / "frontend/src/pages/Student/StudentLayout.tsx",
                ROOT / "frontend/src/pages/Teacher/TeacherLayout.tsx",
            ]
            cache_clear_count = sum("queryClient.clear()" in path.read_text(encoding="utf-8") for path in cache_files)
            record(
                "account_cache_cleared_on_logout",
                cache_clear_count == len(cache_files),
                {"layouts": cache_clear_count},
            )

            invalid_upload = client.post(
                "/api/student/procedure", headers=headers,
                data={"item_id": "audit-invalid-upload"},
                files={"file": ("fake.png", b"not an image", "image/png")},
            )
            record(
                "upload_content_validated",
                invalid_upload.status_code == 415,
                {"http": invalid_upload.status_code},
            )

            from PIL import Image

            image_buffer = io.BytesIO()
            Image.new("RGB", (2, 2), (15, 70, 130)).save(image_buffer, format="PNG")
            procedure_image = image_buffer.getvalue()
            procedure_item = "audit-procedure-security"
            forged = client.post(
                "/api/student/procedure", headers=headers,
                data={"item_id": procedure_item, "ai_proposed_score": "99"},
                files={"file": ("work.png", procedure_image, "image/png")},
            )
            forged_saved = repo.get_student_submission(student, procedure_item)
            record(
                "client_ai_score_ignored",
                forged.status_code == 200 and forged_saved.get("ai_proposed_score") is None,
                {"http": forged.status_code, "saved_score": forged_saved.get("ai_proposed_score")},
            )

            repo.register_user("audit_upload_other", "audit-only-password", "student")
            with database(repo) as conn:
                other_student = conn.execute(
                    "SELECT id FROM users WHERE username='audit_upload_other'"
                ).fetchone()[0]
            other_student_headers = {
                "Authorization": "Bearer "
                + deps.create_access_token(other_student, "audit_upload_other", "student")
            }
            copied = client.post(
                "/api/student/procedure", headers=other_student_headers,
                data={"item_id": procedure_item},
                files={"file": ("copy.png", procedure_image, "image/png")},
            )
            record(
                "procedure_antiplagiarism_enforced",
                copied.status_code == 409,
                {"http": copied.status_code},
            )

            # A teacher account with no relationship to any existing student/group.
            repo.register_user("audit_teacher", "audit-only-password", "teacher")
            with database(repo) as conn:
                conn.execute("UPDATE users SET approved=1 WHERE username='audit_teacher'")
                foreign_teacher = conn.execute("SELECT id FROM users WHERE username='audit_teacher'").fetchone()[0]
            other_headers = {"Authorization": "Bearer " + deps.create_access_token(foreign_teacher, "audit_teacher", "teacher")}
            groups = repo.get_groups_by_teacher(teacher_id)
            group_id = groups[0]["group_id"]
            student_paths = [
                f"/api/teacher/student/{student}",
                f"/api/teacher/student/{student}/elo-history",
                f"/api/teacher/student/{student}/katia-history",
                f"/api/teacher/student/{student}/ranking",
            ]
            denied = [client.get(path, headers=other_headers).status_code for path in student_paths]
            allowed = [client.get(path, headers=teacher_headers).status_code for path in student_paths]
            record(
                "foreign_student_denied",
                all(code in (403, 404) for code in denied) and all(code == 200 for code in allowed),
                {"foreign_http": denied, "owner_http": allowed},
            )
            original_code = repo.generate_group_invite_code(group_id)
            response = client.post(f"/api/teacher/groups/{group_id}/invite-code", headers=other_headers)
            code_unchanged = repo.get_group_by_invite_code(original_code) is not None
            owner_response = client.post(
                f"/api/teacher/groups/{group_id}/invite-code", headers=teacher_headers
            )
            record(
                "foreign_group_invite_denied",
                response.status_code in (403, 404)
                and code_unchanged
                and owner_response.status_code == 200,
                {
                    "foreign_http": response.status_code,
                    "unchanged_after_rejection": code_unchanged,
                    "owner_http": owner_response.status_code,
                },
            )

            item = repo.get_items_from_db(course_id="calculo_diferencial")[0]
            topic = item["topic"]
            repo.register_user("audit_diagnostic", "audit-only-password", "student")
            with database(repo) as conn:
                diagnostic_student = conn.execute(
                    "SELECT id FROM users WHERE username='audit_diagnostic'"
                ).fetchone()[0]
            repo.save_diagnostic(
                diagnostic_student, "calculo_diferencial", 1234.0, 75.0, "{}"
            )
            repo.set_topic_rating_baseline(
                diagnostic_student, "calculo_diferencial", topic, 1234.0
            )
            ratings = RatingReadService(repo)
            topic_recovered = ratings.selection_rating(
                diagnostic_student, "calculo_diferencial", topic
            )
            course_recovered = ratings.course_rating_of(diagnostic_student, "calculo_diferencial")
            record(
                "diagnostic_baseline_recovered",
                topic_recovered == 1234.0 and course_recovered == 1234.0,
                {
                    "stored": 1234.0,
                    "topic_recovered": topic_recovered,
                    "course_recovered": course_recovered,
                },
            )
            with database(repo) as conn:
                attempt_before = conn.execute(
                    "SELECT COUNT(*) FROM attempts WHERE user_id=?", (student,)
                ).fetchone()[0]
            body = {"item_id": item["id"], "item_data": {**item, "difficulty": 1777.0}, "selected_option": item["correct_option"], "time_taken": 30}
            response = client.post("/api/student/answer", headers=headers, json=body)
            with database(repo) as conn:
                attempt_after = conn.execute(
                    "SELECT COUNT(*) FROM attempts WHERE user_id=?", (student,)
                ).fetchone()[0]
                saved = conn.execute(
                    "SELECT item_id, difficulty, topic FROM attempts "
                    "WHERE user_id=? ORDER BY id DESC LIMIT 1",
                    (student,),
                ).fetchone()
            canonical_saved = bool(
                response.status_code == 200
                and attempt_after == attempt_before + 1
                and saved
                and saved[0] == item["id"]
                and saved[1] == item["difficulty"]
                and saved[2] == item["topic"]
            )
            record(
                "canonical_item_difficulty",
                canonical_saved,
                {
                    "http": response.status_code,
                    "new_attempts": attempt_after - attempt_before,
                    "canonical": item["difficulty"],
                    "submitted": 1777,
                    "saved": saved[1] if saved else None,
                },
            )

            body["item_data"] = item
            with database(repo) as conn:
                before = conn.execute("SELECT COUNT(*) FROM attempts WHERE user_id=?", (student,)).fetchone()[0]
            idem_headers = {**headers, "Idempotency-Key": "audit-one-logical-submission"}
            client.post("/api/student/answer", headers=idem_headers, json=body)
            client.post("/api/student/answer", headers=idem_headers, json=body)
            with database(repo) as conn:
                after = conn.execute("SELECT COUNT(*) FROM attempts WHERE user_id=?", (student,)).fetchone()[0]
            record("answer_retry_idempotent", after - before == 1, {"new_attempts": after - before})

            with database(repo) as conn:
                submission = conn.execute(
                    "INSERT INTO procedure_submissions "
                    "(student_id, item_id, item_content, image_data, status, ai_proposed_score) "
                    "VALUES (?, ?, ?, ?, 'PENDING_TEACHER_VALIDATION', 99)",
                    (student, item["id"], item["content"], b"audit fixture"),
                ).lastrowid
            foreign_grade = client.post(
                "/api/teacher/procedures/grade",
                headers=other_headers,
                json={"submission_id": submission, "teacher_score": 0},
            )
            owner_grade = client.post(
                "/api/teacher/procedures/grade",
                headers=teacher_headers,
                json={"submission_id": submission, "teacher_score": 80},
            )
            repeated_grade = client.post(
                "/api/teacher/procedures/grade",
                headers=teacher_headers,
                json={"submission_id": submission, "teacher_score": 50},
            )
            with database(repo) as conn:
                graded = conn.execute(
                    "SELECT teacher_score, final_score, ai_proposed_score, elo_delta, status "
                    "FROM procedure_submissions WHERE id=?",
                    (submission,),
                ).fetchone()
            record(
                "grade_contract_handles_request",
                foreign_grade.status_code in (403, 404)
                and owner_grade.status_code == 200
                and owner_grade.json().get("elo_delta") == 6
                and repeated_grade.status_code in (400, 404)
                and graded == (80, 80, 99, 6, "VALIDATED_BY_TEACHER"),
                {
                    "foreign_http": foreign_grade.status_code,
                    "owner_http": owner_grade.status_code,
                    "repeat_http": repeated_grade.status_code,
                    "persisted": list(graded) if graded else None,
                },
            )

            own_template = repo.create_exam_template(foreign_teacher, "calculo_diferencial", "Audit own", 10, [item["id"]])
            victim_template = repo.create_exam_template(teacher_id, "calculo_diferencial", "Audit foreign", 10, [item["id"]])
            assignment = repo.create_exam_assignment(victim_template, group_id, "2099-01-01T00:00:00", "2099-01-02T00:00:00")
            response = client.post("/api/student/exam/start", headers=headers, json={"course_id": "calculo_diferencial", "template_id": victim_template})
            record("future_exam_window_enforced", response.status_code in (403, 404), {"http": response.status_code})
            response = client.delete(f"/api/teacher/exam-templates/{own_template}/assignments/{assignment}", headers=other_headers)
            remaining = repo.list_assignments_for_template(victim_template)
            own_assignment = repo.create_exam_assignment(
                own_template, group_id, "2099-01-01T00:00:00", "2099-01-02T00:00:00"
            )
            owner_delete = client.delete(
                f"/api/teacher/exam-templates/{own_template}/assignments/{own_assignment}",
                headers=other_headers,
            )
            record(
                "foreign_assignment_delete_denied",
                response.status_code in (403, 404)
                and [row["id"] for row in remaining] == [assignment]
                and owner_delete.status_code == 204
                and repo.list_assignments_for_template(own_template) == [],
                {
                    "foreign_http": response.status_code,
                    "victim_assignment_ids": [row["id"] for row in remaining],
                    "owner_http": owner_delete.status_code,
                },
            )

            exam = client.post(
                "/api/student/exam/start", headers=headers,
                json={"course_id": "calculo_diferencial", "n_questions": 1},
            ).json()
            response = client.post(
                "/api/student/exam/submit", headers=headers,
                json={"session_id": exam["session_id"], "course_id": "calculo_diferencial",
                      "answers": [{"item_id": exam["items"][0]["id"],
                                   "selected_option": exam["items"][0]["options"][0]}] * 3},
            )
            record("duplicate_exam_items_rejected", response.status_code in (400, 422), {"http": response.status_code, "correct_count": response.json().get("correct_count")})

            with database(repo) as conn:
                conn.execute("UPDATE users SET active=0 WHERE id=?", (student,))
            response = client.get("/api/student/courses", headers=headers)
            record("disabled_user_token_rejected", response.status_code in (401, 403), {"http": response.status_code})
        finally:
            client.close()
            deps._repo_instance = None

    target = ROOT / "docs/auditoria-produccion-evidencia.json"
    target.write_text(json.dumps({"scope": "fresh local SQLite + TestClient; no remote services", "results": results}, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["status"], result["check"], json.dumps(result["observed"]))
    return 1 if any(r["status"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(run())
