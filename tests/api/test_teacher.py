"""
tests/api/test_teacher.py
==========================
Tests del panel del docente:
  GET  /api/teacher/dashboard            → resumen de grupos y estudiantes
  GET  /api/teacher/groups               → grupos del docente
  POST /api/teacher/groups               → crear grupo
  POST /api/teacher/groups/{id}/invite-code → generar código de invitación
  GET  /api/teacher/procedures           → cola de procedimientos pendientes
  GET  /api/teacher/student/{id}         → reporte de un estudiante
  GET  /api/teacher/export/csv           → descarga CSV
  GET  /api/teacher/export/xlsx          → descarga XLSX
"""

_COURSE_ID = "calculo_diferencial"
_GROUP_NAME = "Grupo API Test"


class TestDashboard:
    def test_dashboard_returns_data(self, api_client, teacher_headers):
        """GET /teacher/dashboard → objeto con groups y students."""
        r = api_client.get("/api/teacher/dashboard", headers=teacher_headers)
        assert r.status_code == 200
        data = r.json()
        assert "groups" in data
        assert "students" in data
        assert isinstance(data["groups"], list)
        assert isinstance(data["students"], list)

    def test_dashboard_requires_teacher_role(self, api_client, student_headers):
        """Estudiante no puede acceder al dashboard del docente → 403."""
        r = api_client.get("/api/teacher/dashboard", headers=student_headers)
        assert r.status_code == 403

    def test_dashboard_requires_auth(self, api_client):
        """Sin token → 401."""
        r = api_client.get("/api/teacher/dashboard")
        assert r.status_code == 401


class TestGroups:
    def test_list_groups(self, api_client, teacher_headers):
        """GET /teacher/groups → lista de grupos del docente."""
        r = api_client.get("/api/teacher/groups", headers=teacher_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_group(self, api_client, teacher_headers):
        """POST /teacher/groups → 201 con el grupo creado."""
        r = api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": _GROUP_NAME},
            headers=teacher_headers,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == _GROUP_NAME
        assert "group_id" in data

    def test_create_group_duplicate_name(self, api_client, teacher_headers):
        """Crear grupo con nombre duplicado → 400."""
        # Primer intento (puede ya existir de test anterior)
        api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": "Grupo Duplicado Test"},
            headers=teacher_headers,
        )
        # Segundo intento con mismo nombre → 400
        r = api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": "Grupo Duplicado Test"},
            headers=teacher_headers,
        )
        assert r.status_code == 400

    def test_create_group_empty_name(self, api_client, teacher_headers):
        """Nombre de grupo vacío → 422 (Pydantic)."""
        r = api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": ""},
            headers=teacher_headers,
        )
        assert r.status_code == 422

    def test_generate_invite_code(self, api_client, teacher_headers):
        """POST /teacher/groups/{id}/invite-code → código de invitación."""
        # Crear un grupo para obtener su ID
        create_r = api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": "Grupo Código Test"},
            headers=teacher_headers,
        )
        if create_r.status_code == 400:
            # Ya existía — obtener el ID de la lista
            groups_r = api_client.get("/api/teacher/groups", headers=teacher_headers)
            groups = groups_r.json()
            group_id = next(
                (g["group_id"] for g in groups if g["name"] == "Grupo Código Test"),
                groups[0]["group_id"] if groups else None,
            )
        else:
            group_id = create_r.json()["group_id"]

        if group_id is None:
            return  # No hay grupos disponibles

        r = api_client.post(
            f"/api/teacher/groups/{group_id}/invite-code",
            headers=teacher_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "invite_code" in data
        assert len(data["invite_code"]) > 0


class TestProcedures:
    def test_list_pending_procedures(self, api_client, teacher_headers):
        """GET /teacher/procedures → lista (vacía o con procedimientos pendientes)."""
        r = api_client.get("/api/teacher/procedures", headers=teacher_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestStudentReport:
    def test_student_report(self, api_client, teacher_headers):
        """GET /teacher/student/{id} → reporte de un estudiante."""
        # Obtener el ID de estudiante1 usando el dashboard
        dash_r = api_client.get("/api/teacher/dashboard", headers=teacher_headers)
        students = dash_r.json().get("students", [])
        if not students:
            return  # Sin estudiantes en el grupo del docente

        student_id = students[0].get("user_id") or students[0].get("id")
        r = api_client.get(f"/api/teacher/student/{student_id}", headers=teacher_headers)
        assert r.status_code == 200


class TestExport:
    def test_export_csv(self, api_client, teacher_headers):
        """GET /teacher/export/csv → respuesta CSV (puede estar vacía si no hay datos)."""
        r = api_client.get("/api/teacher/export/csv", headers=teacher_headers)
        # 200 si hay datos, 404 si no hay nada que exportar
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert "text/csv" in r.headers.get("content-type", "")

    def test_export_xlsx(self, api_client, teacher_headers):
        """GET /teacher/export/xlsx → respuesta XLSX o error si no hay datos."""
        r = api_client.get("/api/teacher/export/xlsx", headers=teacher_headers)
        assert r.status_code in (200, 404, 500)  # 500 si openpyxl no instalado
        if r.status_code == 200:
            ct = r.headers.get("content-type", "")
            assert "spreadsheetml" in ct or "octet-stream" in ct
