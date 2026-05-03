"""
tests/api/test_protected_routes.py
====================================
Sprint 7.5 — Tests de integración: control de acceso por rol.

Diseño real de autorización:
- Rutas de estudiante: requieren cualquier usuario autenticado (CurrentUser).
  Docentes y admins también pueden acceder (útil para debugging/soporte).
- Rutas de docente: require_role("teacher", "admin") — estudiantes → 403.
- Rutas de admin: require_role("admin") — estudiantes y docentes → 403.
- Sin token → 401 en todas las rutas protegidas.
"""

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Rutas agrupadas por control de acceso
# ─────────────────────────────────────────────────────────────────────────────

STUDENT_ROUTES_GET = [
    "/api/student/courses",
    "/api/student/stats",
    "/api/student/history",
    "/api/student/activity",
    "/api/student/achievements",
    "/api/student/group-ranking",
    "/api/student/procedures",
]

TEACHER_ROUTES_GET = [
    "/api/teacher/dashboard",
    "/api/teacher/groups",
    "/api/teacher/procedures",
    "/api/teacher/metrics",
    "/api/teacher/export/csv",
    "/api/teacher/export/xlsx",
]

ADMIN_ROUTES_GET = [
    "/api/admin/users",
    "/api/admin/groups",
    "/api/admin/reports",
    "/api/admin/audit",
]

# Rutas públicas (sin auth requerida intencionalmente)
PUBLIC_ROUTES = [
    "/api/student/ai-status",  # consultada por el frontend antes del login
]


# ─────────────────────────────────────────────────────────────────────────────
# 401 — sin token
# ─────────────────────────────────────────────────────────────────────────────


class TestUnauthenticatedAccess:
    """Todas las rutas protegidas deben devolver 401 sin Authorization header."""

    @pytest.mark.parametrize("path", STUDENT_ROUTES_GET)
    def test_student_get_routes_unauthenticated(self, api_client, path):
        r = api_client.get(path)
        assert r.status_code == 401, f"Esperaba 401 en GET {path}, recibí {r.status_code}"

    def test_student_answer_unauthenticated(self, api_client):
        r = api_client.post("/api/student/answer", json={})
        assert r.status_code == 401

    def test_student_enroll_unauthenticated(self, api_client):
        r = api_client.post("/api/student/enroll", json={"course_id": "calculo"})
        assert r.status_code == 401

    def test_student_profile_patch_unauthenticated(self, api_client):
        r = api_client.patch("/api/student/profile", json={})
        assert r.status_code == 401

    @pytest.mark.parametrize("path", TEACHER_ROUTES_GET)
    def test_teacher_get_routes_unauthenticated(self, api_client, path):
        r = api_client.get(path)
        assert r.status_code == 401, f"Esperaba 401 en GET {path}, recibí {r.status_code}"

    def test_teacher_create_group_unauthenticated(self, api_client):
        r = api_client.post("/api/teacher/groups", json={"name": "test"})
        assert r.status_code == 401

    def test_teacher_grade_procedure_unauthenticated(self, api_client):
        r = api_client.post("/api/teacher/procedures/grade", json={})
        assert r.status_code == 401

    def test_ai_socratic_unauthenticated(self, api_client):
        r = api_client.post("/api/ai/socratic", json={})
        assert r.status_code == 401

    @pytest.mark.parametrize("path", PUBLIC_ROUTES)
    def test_public_routes_accessible_without_auth(self, api_client, path):
        r = api_client.get(path)
        assert r.status_code == 200, f"Ruta pública {path} debería ser accesible sin token"


# ─────────────────────────────────────────────────────────────────────────────
# 403 — estudiante en rutas de docente
# ─────────────────────────────────────────────────────────────────────────────


class TestStudentCannotAccessTeacherRoutes:
    """Estudiante no puede acceder a rutas exclusivas de docente (403)."""

    @pytest.mark.parametrize("path", TEACHER_ROUTES_GET)
    def test_student_forbidden_on_teacher_get(self, api_client, student_headers, path):
        r = api_client.get(path, headers=student_headers)
        assert r.status_code == 403, f"Esperaba 403 en GET {path}, recibí {r.status_code}"

    def test_student_cannot_create_group(self, api_client, student_headers):
        r = api_client.post("/api/teacher/groups", json={"name": "test"}, headers=student_headers)
        assert r.status_code == 403

    def test_student_cannot_grade_procedure(self, api_client, student_headers):
        r = api_client.post(
            "/api/teacher/procedures/grade",
            json={"submission_id": 1, "score": 80},
            headers=student_headers,
        )
        assert r.status_code == 403

    def test_student_cannot_access_student_detail(self, api_client, student_headers):
        r = api_client.get("/api/teacher/student/999", headers=student_headers)
        assert r.status_code == 403

    def test_student_cannot_run_ai_analysis(self, api_client, student_headers):
        r = api_client.post(
            "/api/teacher/student/999/ai-analysis", json={}, headers=student_headers
        )
        assert r.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Docente puede acceder a rutas de estudiante (diseño intencional)
# ─────────────────────────────────────────────────────────────────────────────


class TestTeacherCanAccessStudentRoutes:
    """
    Docente puede leer datos de rutas de estudiante (diseño intencional —
    CurrentUser sin require_role en el router de estudiante).
    """

    @pytest.mark.parametrize("path", STUDENT_ROUTES_GET)
    def test_teacher_can_access_student_get(self, api_client, teacher_headers, path):
        r = api_client.get(path, headers=teacher_headers)
        assert r.status_code in (
            200,
            404,
        ), f"Docente debería poder acceder a GET {path}, recibí {r.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# 403 — estudiante/docente en rutas de admin
# ─────────────────────────────────────────────────────────────────────────────


class TestNonAdminCannotAccessAdminRoutes:
    """Estudiantes y docentes no pueden acceder a rutas de admin."""

    @pytest.mark.parametrize("path", ADMIN_ROUTES_GET)
    def test_student_forbidden_on_admin_get(self, api_client, student_headers, path):
        r = api_client.get(path, headers=student_headers)
        assert r.status_code in (
            403,
            404,
        ), f"Esperaba 403/404 en GET {path} con token estudiante, recibí {r.status_code}"

    @pytest.mark.parametrize("path", ADMIN_ROUTES_GET)
    def test_teacher_forbidden_on_admin_get(self, api_client, teacher_headers, path):
        r = api_client.get(path, headers=teacher_headers)
        assert r.status_code in (
            403,
            404,
        ), f"Esperaba 403/404 en GET {path} con token docente, recibí {r.status_code}"


# ─────────────────────────────────────────────────────────────────────────────
# Tokens inválidos / malformados
# ─────────────────────────────────────────────────────────────────────────────


class TestInvalidTokens:
    """Tokens malformados o expirados deben devolver 401 o 403."""

    def test_invalid_bearer_token(self, api_client):
        headers = {"Authorization": "Bearer este-token-es-falso"}
        r = api_client.get("/api/student/courses", headers=headers)
        assert r.status_code in (401, 403)

    def test_malformed_authorization_header(self, api_client):
        headers = {"Authorization": "NotBearer token"}
        r = api_client.get("/api/student/courses", headers=headers)
        assert r.status_code in (401, 403)

    def test_empty_authorization_header(self, api_client):
        headers = {"Authorization": ""}
        r = api_client.get("/api/student/courses", headers=headers)
        assert r.status_code in (401, 403, 422)
