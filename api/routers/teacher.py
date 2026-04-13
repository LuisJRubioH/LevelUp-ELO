"""
api/routers/teacher.py
======================
Endpoints del panel del docente:
  GET  /teacher/dashboard         → resumen de grupos y estudiantes
  GET  /teacher/groups            → grupos del docente
  POST /teacher/groups            → crear grupo
  POST /teacher/groups/{id}/invite-code → generar código de invitación
  GET  /teacher/procedures        → cola de procedimientos pendientes
  POST /teacher/procedures/grade  → calificar procedimiento
  GET  /teacher/student/{id}      → reporte detallado de un estudiante
  GET  /teacher/export            → descarga CSV/XLSX de datos
"""

import io

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from api.dependencies import CurrentUser, RepoDep, require_role
from api.schemas.teacher import (
    ApproveTeacherRequest,
    ChangeGroupRequest,
    CreateGroupRequest,
    GradeRequest,
    GradeResponse,
    GroupResponse,
    PendingProcedure,
    StudentReportResponse,
    UserAdminRow,
)
from src.application.services.teacher_service import TeacherService

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"],
    dependencies=[require_role("teacher", "admin")],
)


def _svc(repo) -> TeacherService:
    return TeacherService(repository=repo)


# ── Dashboard ─────────────────────────────────────────────────────────────────


@router.get("/dashboard")
def dashboard(user: CurrentUser, repo: RepoDep):
    """Resumen de grupos, ELO promedio y últimos intentos de los estudiantes."""
    svc = _svc(repo)
    students, groups = svc.get_dashboard_data(user["user_id"])
    return {"students": students, "groups": groups}


# ── Grupos ────────────────────────────────────────────────────────────────────


@router.get("/groups", response_model=list[GroupResponse])
def get_groups(user: CurrentUser, repo: RepoDep):
    """Lista de grupos del docente con contador de estudiantes."""
    rows = repo.get_groups_by_teacher(user["user_id"])
    result = []
    for r in rows:
        row = (
            dict(r)
            if isinstance(r, dict)
            else {
                "id": r[0],
                "name": r[1],
                "course_id": r[2] if len(r) > 2 else None,
                "invite_code": r[3] if len(r) > 3 else None,
                "student_count": r[4] if len(r) > 4 else 0,
            }
        )
        result.append(
            GroupResponse(
                group_id=row["id"],
                name=row["name"],
                course_id=row.get("course_id"),
                invite_code=row.get("invite_code"),
                student_count=row.get("student_count", 0),
            )
        )
    return result


@router.post("/groups", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
def create_group(body: CreateGroupRequest, user: CurrentUser, repo: RepoDep):
    """Crea un nuevo grupo para el docente."""
    svc = _svc(repo)
    ok, msg, group_id = svc.create_new_group(user["user_id"], body.course_id, body.group_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return GroupResponse(
        group_id=group_id,
        name=body.group_name,
        course_id=body.course_id,
        invite_code=None,
        student_count=0,
    )


@router.post("/groups/{group_id}/invite-code")
def generate_invite_code(group_id: int, user: CurrentUser, repo: RepoDep):
    """Genera o renueva el código de invitación del grupo."""
    code = repo.generate_group_invite_code(group_id)
    return {"invite_code": code}


# ── Procedimientos ────────────────────────────────────────────────────────────


@router.get("/procedures", response_model=list[PendingProcedure])
def pending_procedures(user: CurrentUser, repo: RepoDep):
    """Cola de procedimientos pendientes de calificación."""
    rows = repo.get_pending_submissions_for_teacher(user["user_id"])
    result = []
    for r in rows:
        row = dict(r) if isinstance(r, dict) else {}
        if not row:
            continue
        result.append(
            PendingProcedure(
                submission_id=row.get("id", 0),
                student_id=row.get("user_id", 0),
                student_username=row.get("username", ""),
                item_id=row.get("item_id", ""),
                item_content=row.get("item_content"),
                ai_score=row.get("ai_proposed_score"),
                status=row.get("status", "pending"),
                created_at=str(row.get("created_at", "")),
            )
        )
    return result


@router.post("/procedures/grade", response_model=GradeResponse)
def grade_procedure(body: GradeRequest, user: CurrentUser, repo: RepoDep):
    """Califica un procedimiento y aplica el delta ELO al estudiante."""
    svc = _svc(repo)
    ok, msg, elo_delta = svc.validate_procedure(
        teacher_id=user["user_id"],
        submission_id=body.submission_id,
        teacher_score=body.teacher_score,
        teacher_feedback=body.teacher_feedback or "",
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    # Notificar al estudiante en tiempo real (WebSocket)
    try:
        submission = repo.get_procedure_submission(body.submission_id)
        if submission:
            student_id = submission["user_id"] if isinstance(submission, dict) else submission[1]
            from api.websocket.notifications import notify_sync

            notify_sync(
                room=f"student_{student_id}",
                event="procedure_graded",
                data={
                    "submission_id": body.submission_id,
                    "teacher_score": body.teacher_score,
                    "elo_delta": elo_delta or 0.0,
                    "feedback": body.teacher_feedback or "",
                },
            )
    except Exception:
        pass  # No fallar el endpoint si la notificación falla

    return GradeResponse(
        submission_id=body.submission_id,
        teacher_score=body.teacher_score,
        elo_delta=elo_delta or 0.0,
        status="graded",
    )


# ── Reporte por estudiante ────────────────────────────────────────────────────


@router.get("/student/{student_id}")
def student_report(student_id: int, user: CurrentUser, repo: RepoDep):
    """Reporte detallado de un estudiante (ELO, intentos, procedimientos)."""
    svc = _svc(repo)
    return svc.get_student_dashboard(student_id)


# ── Exportación ───────────────────────────────────────────────────────────────


@router.get("/export/csv")
def export_csv(user: CurrentUser, repo: RepoDep):
    """Exporta los datos de intentos de los estudiantes del docente como CSV."""
    import csv
    import io

    rows = repo.export_teacher_student_data(user["user_id"])
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sin datos para exportar."
        )

    output = io.StringIO()
    keys = list(rows[0].keys()) if isinstance(rows[0], dict) else []
    writer = csv.DictWriter(output, fieldnames=keys)
    writer.writeheader()
    writer.writerows([dict(r) for r in rows])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=levelup_data.csv"},
    )


@router.get("/export/xlsx")
def export_xlsx(user: CurrentUser, repo: RepoDep):
    """Exporta los datos de los estudiantes como Excel con 4 hojas."""
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="openpyxl no instalado en el servidor.",
        )

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    datasets = {
        "Intentos": repo.export_teacher_student_data(user["user_id"]),
        "Matrículas": repo.export_teacher_enrollments(user["user_id"]),
        "Procedimientos": repo.export_teacher_procedures(user["user_id"]),
        "KatIA": repo.export_teacher_katia_interactions(user["user_id"]),
    }

    for sheet_name, rows in datasets.items():
        ws = wb.create_sheet(title=sheet_name)
        if rows:
            headers = list(rows[0].keys()) if isinstance(rows[0], dict) else []
            ws.append(headers)
            for row in rows:
                ws.append(list(dict(row).values()))

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=levelup_data.xlsx"},
    )
