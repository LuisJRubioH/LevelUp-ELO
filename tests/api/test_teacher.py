"""
tests/api/test_teacher.py
==========================
Tests del panel del docente:
  GET  /api/teacher/dashboard            → resumen de grupos y estudiantes
  GET  /api/teacher/groups               → grupos del docente
  POST /api/teacher/groups               → crear grupo
  POST /api/teacher/groups/{id}/invitations → invitaciones de un solo uso (spec 001 INV)
  GET  /api/teacher/groups/{id}/invitations → invitaciones del grupo y su estado
  DELETE /api/teacher/invitations/{id}      → anular una invitación sin usar
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

    def _own_group(self, api_client, teacher_headers, name):
        created = api_client.post(
            "/api/teacher/groups",
            json={"course_id": _COURSE_ID, "group_name": name},
            headers=teacher_headers,
        )
        if created.status_code == 201:
            return created.json()["group_id"]
        groups = api_client.get("/api/teacher/groups", headers=teacher_headers).json()
        return next(g["group_id"] for g in groups if g["name"] == name)

    def test_groups_carry_no_reusable_code(self, api_client, teacher_headers):
        """Spec 001 FR-028u: the group listing no longer returns a reusable code."""
        self._own_group(api_client, teacher_headers, "Grupo Sin Código Test")
        groups = api_client.get("/api/teacher/groups", headers=teacher_headers).json()
        assert groups and all("invite_code" not in g for g in groups)

    def test_generate_list_and_revoke_invitations(self, api_client, teacher_headers):
        """Spec 001 FR-028p, FR-028t: generate, list and revoke the group's invitations."""
        group_id = self._own_group(api_client, teacher_headers, "Grupo Invitaciones Test")
        path = f"/api/teacher/groups/{group_id}/invitations"

        created = api_client.post(path, json={"count": 2}, headers=teacher_headers)
        assert created.status_code == 201, created.text
        tokens = created.json()["tokens"]
        assert len(set(tokens)) == 2 and all(len(t) == 11 and t[5] == "-" for t in tokens)

        listed = api_client.get(path, headers=teacher_headers)
        assert listed.status_code == 200
        body = listed.json()
        assert body["ttl_days"] == 30
        mine = [i for i in body["invitations"] if i["token"] in tokens]
        assert {i["status"] for i in mine} == {"unused"}
        assert set(mine[0]) == {
            "id",
            "token",
            "status",
            "created_at",
            "expires_at",
            "used_at",
            "used_by_name",
        }

        revoked = api_client.delete(
            f"/api/teacher/invitations/{mine[0]['id']}", headers=teacher_headers
        )
        assert revoked.status_code == 204
        states = {
            i["id"]: i["status"]
            for i in api_client.get(path, headers=teacher_headers).json()["invitations"]
        }
        assert states[mine[0]["id"]] == "revoked"
        assert states[mine[1]["id"]] == "unused"

    def test_invitation_count_is_validated(self, api_client, teacher_headers):
        """Spec 001 FR-028p: 1 to 50 at once."""
        group_id = self._own_group(api_client, teacher_headers, "Grupo Invitaciones Test")
        path = f"/api/teacher/groups/{group_id}/invitations"
        for count in (0, 51):
            assert (
                api_client.post(path, json={"count": count}, headers=teacher_headers).status_code
                == 422
            )

    def test_invitations_require_teacher_role(self, api_client, student_headers):
        """A student is refused on every invitation endpoint (403)."""
        for method, path in [
            ("POST", "/api/teacher/groups/1/invitations"),
            ("GET", "/api/teacher/groups/1/invitations"),
            ("DELETE", "/api/teacher/invitations/1"),
        ]:
            response = api_client.request(method, path, headers=student_headers, json={"count": 1})
            assert response.status_code == 403, (method, path)


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
