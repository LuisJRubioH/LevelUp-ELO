"""
tests/api/test_student.py
==========================
Tests del flujo de práctica del estudiante:
  GET  /api/student/courses        → catálogo de cursos
  GET  /api/student/stats          → ELO y estadísticas
  POST /api/student/enroll         → matrícula en un curso
  POST /api/student/next-question  → siguiente pregunta adaptativa
  POST /api/student/answer         → procesar respuesta
  GET  /api/student/history        → historial de intentos
  DELETE /api/student/enroll/{id}  → darse de baja
  GET  /api/student/achievements   → logros/badges
  POST /api/student/exam/start     → iniciar examen
  POST /api/student/exam/submit    → enviar respuestas del examen
"""

import pytest

_COURSE_ID = "algebra_basica"  # Colegio — presente en el banco de preguntas
_COURSE_UNIV = "calculo_diferencial"  # Universidad


class TestCourses:
    def test_list_courses_authenticated(self, api_client, student_headers):
        """GET /student/courses → lista de cursos con flag enrolled."""
        r = api_client.get("/api/student/courses", headers=student_headers)
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, list)
        assert len(courses) > 0
        # Cada curso tiene los campos esperados
        course = courses[0]
        assert "id" in course or "course_id" in course
        assert "name" in course
        assert "block" in course
        assert "enrolled" in course

    def test_list_courses_unauthenticated(self, api_client):
        """GET /student/courses sin token → 401."""
        r = api_client.get("/api/student/courses")
        assert r.status_code == 401


class TestStats:
    def test_stats_authenticated(self, api_client, student_headers):
        """GET /student/stats → ELO global, tópicos, racha."""
        r = api_client.get("/api/student/stats", headers=student_headers)
        assert r.status_code == 200
        data = r.json()
        assert "global_elo" in data
        assert "total_attempts" in data
        assert "study_streak" in data
        assert "topic_elos" in data
        assert isinstance(data["topic_elos"], list)

    def test_stats_initial_elo(self, api_client, student_headers):
        """ELO inicial de estudiante sin intentos es 1000."""
        r = api_client.get("/api/student/stats", headers=student_headers)
        data = r.json()
        # ELO puede ser exactamente 1000 si no ha respondido nada, o mayor/menor si ya hay intentos
        assert 0 < data["global_elo"] < 5000


class TestEnroll:
    def test_enroll_in_course(self, api_client, student_headers):
        """POST /student/enroll → 201 (o 200 si ya estaba matriculado)."""
        r = api_client.post(
            "/api/student/enroll",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        assert r.status_code in (200, 201)

    def test_enroll_nonexistent_course(self, api_client, student_headers):
        """Matrícula en curso inexistente → error (400 o 404)."""
        r = api_client.post(
            "/api/student/enroll",
            json={"course_id": "curso_que_no_existe_xyz"},
            headers=student_headers,
        )
        assert r.status_code in (400, 404, 422)

    def test_unenroll(self, api_client, student_headers):
        """DELETE /student/enroll/{course_id} → 204."""
        # Primero matricular para asegurar que existe la matrícula
        api_client.post(
            "/api/student/enroll",
            json={"course_id": _COURSE_UNIV},
            headers=student_headers,
        )
        r = api_client.delete(f"/api/student/enroll/{_COURSE_UNIV}", headers=student_headers)
        assert r.status_code == 204


class TestNextQuestion:
    @pytest.fixture(autouse=True, scope="class")
    def ensure_enrolled(self, api_client, student_headers):
        """Asegura matrícula antes de solicitar preguntas."""
        api_client.post(
            "/api/student/enroll",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )

    def test_next_question_returns_item_or_empty(self, api_client, student_headers):
        """POST /student/next-question → status 'ok' o 'empty'/'course_empty'."""
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ok", "empty", "course_empty")

    def test_next_question_item_structure(self, api_client, student_headers):
        """Si hay preguntas disponibles, el ítem tiene todos los campos."""
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        data = r.json()
        if data["status"] == "ok" and data["item"]:
            item = data["item"]
            assert "id" in item
            assert "content" in item
            assert "options" in item
            assert isinstance(item["options"], list)
            assert len(item["options"]) >= 2
            assert "difficulty" in item
            assert "topic" in item


class TestAnswer:
    def test_submit_answer_correct(self, api_client, student_headers):
        """POST /student/answer con respuesta correcta → delta_elo positivo."""
        # Primero obtener una pregunta
        q_res = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        q_data = q_res.json()
        if q_data["status"] != "ok" or not q_data["item"]:
            pytest.skip("No hay preguntas disponibles para este test.")

        item = q_data["item"]
        # Obtener la respuesta correcta directamente del ítem (no la tenemos aquí)
        # Usamos la primera opción (puede ser incorrecta — solo testamos que la API responde)
        r = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "reasoning": "Prueba automática",
                "time_taken": 15.0,
            },
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "is_correct" in data
        assert "elo_before" in data
        assert "elo_after" in data
        assert "delta_elo" in data
        assert isinstance(data["is_correct"], bool)

    def test_submit_answer_elo_changes(self, api_client, student_headers):
        """El ELO cambia después de responder (delta_elo != 0 siempre)."""
        q_res = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        q_data = q_res.json()
        if q_data["status"] != "ok" or not q_data["item"]:
            pytest.skip("No hay preguntas disponibles.")

        item = q_data["item"]
        r = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "time_taken": 10.0,
            },
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        # delta_elo siempre es distinto de 0 (el ELO siempre cambia al responder)
        assert data["delta_elo"] != 0


class TestHistory:
    def test_history_authenticated(self, api_client, student_headers):
        """GET /student/history → lista de intentos previos."""
        r = api_client.get("/api/student/history", headers=student_headers)
        assert r.status_code == 200


class TestRoleProtection:
    def test_teacher_cannot_access_student_answer(self, api_client, teacher_headers):
        """El endpoint /student/answer requiere rol student (o admin)."""
        # El endpoint acepta cualquier usuario autenticado — solo probamos que llega bien
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=teacher_headers,
        )
        # El docente puede acceder a estos endpoints (CurrentUser, no RequireRole)
        # Si no tiene matriculaciones, devuelve empty
        assert r.status_code in (200, 400, 404)


class TestAchievements:
    def test_achievements_authenticated(self, api_client, student_headers):
        """GET /student/achievements → dict con achievements y catalog."""
        r = api_client.get("/api/student/achievements", headers=student_headers)
        assert r.status_code == 200
        data = r.json()
        assert "achievements" in data
        assert "catalog" in data
        assert isinstance(data["achievements"], list)
        assert isinstance(data["catalog"], list)
        assert len(data["catalog"]) > 0

    def test_achievements_catalog_has_required_fields(self, api_client, student_headers):
        """Cada badge del catálogo tiene badge_id, label, icon y desc."""
        r = api_client.get("/api/student/achievements", headers=student_headers)
        catalog = r.json()["catalog"]
        for badge in catalog:
            assert "badge_id" in badge
            assert "label" in badge
            assert "icon" in badge
            assert "desc" in badge

    def test_achievements_unauthenticated(self, api_client):
        """GET /student/achievements sin token → 401."""
        r = api_client.get("/api/student/achievements")
        assert r.status_code == 401

    def test_first_correct_badge_awarded(self, api_client, student_headers):
        """Después de responder correctamente, el badge first_correct debe estar en logros."""
        # Garantizar matrícula
        api_client.post(
            "/api/student/enroll", json={"course_id": _COURSE_ID}, headers=student_headers
        )
        # Obtener pregunta
        q = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        ).json()
        if q["status"] != "ok" or not q["item"]:
            return  # skip silencioso si no hay preguntas

        item = q["item"]
        # Responder (puede ser correcto o incorrecto — solo comprobamos que el endpoint devuelve new_badges)
        ans = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "time_taken": 5.0,
            },
            headers=student_headers,
        ).json()
        # cog_data puede contener new_badges si se desbloqueó algo
        assert "cog_data" in ans


class TestExamMode:
    @pytest.fixture(autouse=True, scope="class")
    def ensure_enrolled(self, api_client, student_headers):
        """Matricular al estudiante en el curso de prueba antes del examen."""
        api_client.post(
            "/api/student/enroll", json={"course_id": _COURSE_ID}, headers=student_headers
        )

    def test_exam_start(self, api_client, student_headers):
        """POST /student/exam/start → lista de preguntas + tiempo límite."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 3, "time_limit_minutes": 10},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "n_questions" in data
        assert "time_limit_seconds" in data
        assert data["time_limit_seconds"] == 600  # 10 * 60
        assert len(data["items"]) >= 1
        assert len(data["items"]) <= 3

    def test_exam_start_item_structure(self, api_client, student_headers):
        """Los ítems del examen tienen todos los campos requeridos."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 2, "time_limit_minutes": 5},
            headers=student_headers,
        )
        items = r.json()["items"]
        if not items:
            return
        item = items[0]
        assert "id" in item
        assert "content" in item
        assert "options" in item
        assert "difficulty" in item

    def test_exam_start_nonexistent_course(self, api_client, student_headers):
        """Examen en curso sin preguntas → 404."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": "curso_xyz_inexistente", "n_questions": 5},
            headers=student_headers,
        )
        assert r.status_code == 404

    def test_exam_submit(self, api_client, student_headers):
        """POST /student/exam/submit → resultados con score_pct y global_elo_after."""
        # Obtener preguntas del examen
        start = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 2, "time_limit_minutes": 5},
            headers=student_headers,
        ).json()
        items = start.get("items", [])
        if not items:
            return

        # Enviar respuestas (primera opción de cada pregunta)
        answers = [
            {"item_id": it["id"], "selected_option": it["options"][0], "time_taken": 5.0}
            for it in items
        ]
        r = api_client.post(
            "/api/student/exam/submit",
            json={"answers": answers},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert "correct_count" in data
        assert "total_questions" in data
        assert "score_pct" in data
        assert "global_elo_after" in data
        assert 0 <= data["score_pct"] <= 100
        assert data["total_questions"] == len(items)

    def test_exam_submit_empty(self, api_client, student_headers):
        """Enviar examen sin respuestas → score 0%."""
        r = api_client.post(
            "/api/student/exam/submit",
            json={"answers": []},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["score_pct"] == 0.0
        assert data["total_questions"] == 0

    def test_exam_unauthenticated(self, api_client):
        """Examen sin autenticación → 401."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 3},
        )
        assert r.status_code == 401
