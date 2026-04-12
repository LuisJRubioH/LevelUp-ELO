"""
api/routers/admin.py
====================
Endpoints del panel de administración:
  GET  /admin/users              → lista de todos los usuarios
  GET  /admin/teachers/pending   → docentes pendientes de aprobación
  POST /admin/teachers/approve   → aprobar o rechazar docente
  PATCH /admin/users/{id}/deactivate → desactivar usuario
  PATCH /admin/users/{id}/reactivate → reactivar usuario
  PATCH /admin/students/group    → reasignar estudiante a otro grupo
  GET  /admin/groups             → todos los grupos
  DELETE /admin/groups/{id}      → eliminar grupo
  GET  /admin/reports            → reportes de problemas técnicos pendientes
  PATCH /admin/reports/{id}/resolve → marcar reporte como resuelto
"""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import CurrentUser, RepoDep, require_role
from api.schemas.teacher import ChangeGroupRequest

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[require_role("admin")],
)


# ── Usuarios ──────────────────────────────────────────────────────────────────


@router.get("/users")
def all_users(user: CurrentUser, repo: RepoDep):
    """Lista completa de usuarios con rol, estado y grupo."""
    rows = repo.get_all_students_admin()
    return {"users": [dict(r) if isinstance(r, dict) else _row_to_dict(r) for r in rows]}


@router.get("/teachers/pending")
def pending_teachers(user: CurrentUser, repo: RepoDep):
    """Docentes pendientes de aprobación."""
    rows = repo.get_pending_teachers()
    return {"teachers": [dict(r) if isinstance(r, dict) else _row_to_dict(r) for r in rows]}


@router.post("/teachers/approve")
def approve_teacher(body: dict, user: CurrentUser, repo: RepoDep):
    """Aprueba o rechaza un docente. Body: {user_id, action: approve|reject}"""
    teacher_id = body.get("user_id")
    action = body.get("action")
    if not teacher_id or action not in ("approve", "reject"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere user_id y action (approve/reject).",
        )
    if action == "approve":
        repo.approve_teacher(teacher_id)
        return {"message": f"Docente {teacher_id} aprobado."}
    repo.reject_teacher(teacher_id)
    return {"message": f"Docente {teacher_id} rechazado."}


@router.patch("/users/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate(user_id: int, user: CurrentUser, repo: RepoDep):
    """Desactiva un usuario (no lo borra)."""
    repo.deactivate_user(user_id)


@router.patch("/users/{user_id}/reactivate", status_code=status.HTTP_204_NO_CONTENT)
def reactivate(user_id: int, user: CurrentUser, repo: RepoDep):
    """Reactiva un usuario."""
    repo.reactivate_user(user_id)


# ── Reasignación de grupos ────────────────────────────────────────────────────


@router.patch("/students/group", status_code=status.HTTP_204_NO_CONTENT)
def change_group(body: ChangeGroupRequest, user: CurrentUser, repo: RepoDep):
    """Reasigna a un estudiante a otro grupo (auditado en audit_group_changes)."""
    repo.change_student_group(
        student_id=body.student_id,
        new_group_id=body.new_group_id,
        admin_id=user["user_id"],
        allow_null=body.new_group_id is None,
    )


# ── Grupos ────────────────────────────────────────────────────────────────────


@router.get("/groups")
def all_groups(user: CurrentUser, repo: RepoDep):
    """Todos los grupos del sistema."""
    rows = repo.get_all_groups()
    return {"groups": [dict(r) if isinstance(r, dict) else _row_to_dict(r) for r in rows]}


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, user: CurrentUser, repo: RepoDep):
    """Elimina un grupo (mueve estudiantes a sin grupo)."""
    repo.delete_group(group_id, admin_id=user["user_id"])


# ── Reportes técnicos ─────────────────────────────────────────────────────────


@router.get("/reports")
def problem_reports(user: CurrentUser, repo: RepoDep):
    """Reportes de problemas técnicos pendientes."""
    rows = repo.get_problem_reports(status="pending")
    return {"reports": [dict(r) if isinstance(r, dict) else _row_to_dict(r) for r in rows]}


@router.patch("/reports/{report_id}/resolve", status_code=status.HTTP_204_NO_CONTENT)
def resolve_report(report_id: int, user: CurrentUser, repo: RepoDep):
    """Marca un reporte técnico como resuelto."""
    repo.mark_problem_resolved(report_id)


# ── helper ────────────────────────────────────────────────────────────────────


def _row_to_dict(row) -> dict:
    """Convierte una row de sqlite3 (tuple) a dict genérico."""
    if hasattr(row, "keys"):
        return dict(row)
    return {f"col_{i}": v for i, v in enumerate(row)}
