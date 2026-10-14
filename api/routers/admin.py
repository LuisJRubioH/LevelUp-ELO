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
  GET  /admin/audit              → log de reasignaciones de grupo
  Spec 004 E2:
  POST /admin/users/{id}/reset-password → contraseña temporal; cierra todas sus sesiones
  POST /admin/teachers                  → crea un docente aprobado con contraseña temporal
  GET  /admin/account-audit             → operaciones sobre cuentas (sin contraseñas)
"""

import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from api.dependencies import CurrentUser, RepoDep, require_role
from api.schemas.teacher import ChangeGroupRequest
from api.websocket.connections import close_user_sync
from src.infrastructure.security.hashing_service import generate_temporary_password

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[require_role("admin")],
)


# ── Usuarios ──────────────────────────────────────────────────────────────────


@router.get("/users")
def all_users(user: CurrentUser, repo: RepoDep):
    """Estudiantes y docentes con rol, estado, grupo y si deben cambiar una contraseña temporal
    (spec 004 E2: el admin restablece el acceso de ambos)."""
    return {
        "users": [
            {
                **r,
                "approved": bool(r.get("approved")),
                "active": bool(r.get("active")),
                "must_change_password": bool(r.get("must_change_password")),
                "created_at": str(r["created_at"]) if r.get("created_at") else None,
            }
            for r in repo.get_accounts_admin()
        ]
    }


# ── Spec 004 E2: acceso de las cuentas ────────────────────────────────────────

_USERNAME = re.compile(r"^[A-Za-z0-9._@-]{3,50}$")


class CreateTeacherRequest(BaseModel):
    username: str = Field(..., max_length=50)
    email: str | None = Field(default=None, max_length=254)


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, user: CurrentUser, repo: RepoDep):
    """FR-029: contraseña temporal aleatoria que la persona debe cambiar al entrar; todas sus
    sesiones terminan. Se audita quién, a quién y cuándo — nunca la contraseña. La respuesta la
    muestra una sola vez al administrador."""
    temporary = generate_temporary_password()
    ok, message = repo.reset_user_password(user["user_id"], user_id, temporary)
    if not ok:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND if "no existe" in message else status.HTTP_400_BAD_REQUEST
            ),
            detail=message,
        )
    close_user_sync(user_id)
    return {"user_id": user_id, "temporary_password": temporary}


@router.post("/teachers", status_code=status.HTTP_201_CREATED)
def create_teacher(body: CreateTeacherRequest, user: CurrentUser, repo: RepoDep):
    """FR-031 (P1): docente aprobado, con contraseña temporal aleatoria que cambia en su primer
    acceso; queda registrado quién lo creó."""
    username = body.username.strip()
    if not _USERNAME.match(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario de 3 a 50 caracteres: letras, números, punto, guion, guion bajo o @.",
        )
    temporary = generate_temporary_password()
    ok, message, teacher_id = repo.create_teacher_account(
        user["user_id"], username, temporary, email=body.email
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"user_id": teacher_id, "username": username, "temporary_password": temporary}


@router.get("/account-audit")
def account_audit(user: CurrentUser, repo: RepoDep, limit: int = 100):
    """FR-029, FR-031: quién hizo qué sobre qué cuenta y cuándo, sin contraseñas."""
    rows = repo.get_account_audit(limit=max(1, min(limit, 500)))
    return {
        "events": [
            {**r, "created_at": str(r["created_at"]) if r.get("created_at") else None}
            for r in rows
        ]
    }


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


# ── Auditoría ─────────────────────────────────────────────────────────────────


@router.get("/audit")
def audit_group_changes(user: CurrentUser, repo: RepoDep, limit: int = 100):
    """Log de reasignaciones de grupo (admin_id, student_id, old/new, timestamp)."""
    rows = repo.get_audit_group_changes(limit=limit)
    return {"entries": [dict(r) if isinstance(r, dict) else _row_to_dict(r) for r in rows]}


# ── helper ────────────────────────────────────────────────────────────────────


def _row_to_dict(row) -> dict:
    """Convierte una row de sqlite3 (tuple) a dict genérico."""
    if hasattr(row, "keys"):
        return dict(row)
    return {f"col_{i}": v for i, v in enumerate(row)}
