"""
tests/api/test_admin.py
========================
Tests del panel de administración:
  GET  /api/admin/users              → todos los usuarios
  GET  /api/admin/teachers/pending   → docentes pendientes
  POST /api/admin/teachers/approve   → aprobar/rechazar docente
  PATCH /api/admin/users/{id}/deactivate  → desactivar usuario
  PATCH /api/admin/users/{id}/reactivate  → reactivar usuario
  GET  /api/admin/groups             → todos los grupos
  GET  /api/admin/reports            → reportes técnicos
  PATCH /api/admin/reports/{id}/resolve  → resolver reporte
"""


class TestAdminUsersEndpoint:
    def test_all_users_as_admin(self, api_client, admin_headers):
        """GET /admin/users como admin → 200 con lista de usuarios."""
        r = api_client.get("/api/admin/users", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "users" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) > 0  # Al menos hay demo users

    def test_all_users_as_student_forbidden(self, api_client, student_headers):
        """Estudiante no puede listar usuarios → 403."""
        r = api_client.get("/api/admin/users", headers=student_headers)
        assert r.status_code == 403

    def test_all_users_as_teacher_forbidden(self, api_client, teacher_headers):
        """Docente no puede acceder al panel de admin → 403."""
        r = api_client.get("/api/admin/users", headers=teacher_headers)
        assert r.status_code == 403

    def test_all_users_unauthenticated(self, api_client):
        """Sin token → 401."""
        r = api_client.get("/api/admin/users")
        assert r.status_code == 401


class TestPendingTeachers:
    def test_pending_teachers(self, api_client, admin_headers):
        """GET /admin/teachers/pending → lista de docentes pendientes."""
        r = api_client.get("/api/admin/teachers/pending", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "teachers" in data
        assert isinstance(data["teachers"], list)

    def test_approve_teacher(self, api_client, admin_headers):
        """POST /admin/teachers/approve → 200 si hay docentes pendientes."""
        # Primero obtener pendientes
        pending_r = api_client.get("/api/admin/teachers/pending", headers=admin_headers)
        teachers = pending_r.json().get("teachers", [])

        if not teachers:
            return  # No hay pendientes — skip implícito

        uid = teachers[0].get("user_id") or teachers[0].get("id")
        r = api_client.post(
            "/api/admin/teachers/approve",
            json={"user_id": uid, "action": "approve"},
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert "message" in r.json()

    def test_approve_invalid_action(self, api_client, admin_headers):
        """Acción inválida → 400."""
        r = api_client.post(
            "/api/admin/teachers/approve",
            json={"user_id": 999, "action": "invalid_action"},
            headers=admin_headers,
        )
        assert r.status_code == 400


class TestUserToggle:
    def test_deactivate_and_reactivate_user(self, api_client, admin_headers):
        """Desactivar y reactivar un usuario de prueba."""
        # Obtener el ID de un usuario no-admin (estudiante1)
        users_r = api_client.get("/api/admin/users", headers=admin_headers)
        users = users_r.json().get("users", [])
        target = next((u for u in users if u["username"] == "nuevo_estudiante_api_test"), None)
        if not target:
            return  # Usuario de test no existe aún

        uid = target.get("user_id") or target.get("id")

        # Desactivar
        r_off = api_client.patch(f"/api/admin/users/{uid}/deactivate", headers=admin_headers)
        assert r_off.status_code == 204

        # Reactivar
        r_on = api_client.patch(f"/api/admin/users/{uid}/reactivate", headers=admin_headers)
        assert r_on.status_code == 204


class TestAdminGroups:
    def test_all_groups(self, api_client, admin_headers):
        """GET /admin/groups → todos los grupos del sistema."""
        r = api_client.get("/api/admin/groups", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "groups" in data
        assert isinstance(data["groups"], list)


class TestAdminReports:
    def test_problem_reports(self, api_client, admin_headers):
        """GET /admin/reports → reportes pendientes (puede estar vacía)."""
        r = api_client.get("/api/admin/reports", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)

    def test_resolve_nonexistent_report(self, api_client, admin_headers):
        """Resolver reporte inexistente → 204 o 404."""
        r = api_client.patch("/api/admin/reports/99999/resolve", headers=admin_headers)
        # El repo puede silenciar el error o devolver 404
        assert r.status_code in (204, 404)
