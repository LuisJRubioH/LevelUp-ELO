"""
api/routers/admin_import.py
===========================
Spec 009 delivery I1 — the initial import of students from the Google Form's export, admin only
(FR-012; plan-i1.md § API):

  POST   /admin/imports/columns            → the header, five example rows and suggested mapping
  POST   /admin/imports/preview            → each row's status and reasons, the pairs, the digest
  POST   /admin/imports                    → 202 {import_id}: the confirmed import, in a worker
  GET    /admin/imports                    → the admin's imports, most recent first
  GET    /admin/imports/{import_id}        → state, counts and each row's result
  PUT    /admin/users/{id}/identification  → links an identification explicitly (FR-007)
  DELETE /admin/users/{id}/identification  → removes a link made by mistake (FR-017)
  POST   /admin/teachers/{id}/groups       → a group for a teacher, institution and grade (N25)
  GET    /admin/courses                    → the catalogue's courses, for that group

The file is never stored: the preview saves nothing, and the confirmation sends the same file
again, which is read again and must give the same digest (FR-003, FR-011). Only the mapped columns
leave the reader (FR-016). No identification, display name or file reaches a log (FR-011): the
worker logs the import's ID and an error's type, never its text.
"""

import json
import logging
import threading

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field, ValidationError

from api.dependencies import CurrentUser, RepoDep, require_role
from src.domain.entities import VALID_LEVELS
from src.domain.identity import access_expired, parse_last_day
from src.domain.student_import import (
    classify_rows,
    file_pairs,
    preview_digest,
    read_identification,
    suggest_mapping,
    suggest_pairing,
)
from src.infrastructure.importing.spreadsheet_reader import (
    MAX_BYTES,
    SpreadsheetError,
    read_spreadsheet,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[require_role("admin")])

CHUNK_SIZE = 25  # rows created per transaction (plan § Running the import)
EXAMPLE_ROWS = 5  # what the mapping step shows (N23)

_FILE_PROBLEMS = {
    "too_large": "El archivo pasa de 5 MB.",
    "format": "El archivo debe ser .xlsx o .csv.",
    "encoding": "El archivo .csv debe estar en UTF-8.",
    "unreadable": "No se pudo leer el archivo de Excel.",
    "empty": "El archivo no tiene filas.",
    "duplicate_header": "Dos columnas del archivo tienen el mismo nombre.",
    "unknown_column": "Una de las columnas elegidas no está en el archivo.",
    "too_many_rows": "El archivo pasa de 500 estudiantes.",
}
_CHANGED = "La vista previa cambió desde que la viste: vuelve a generarla antes de confirmar."
_BUSY = "Ya hay una importación en curso; espera a que termine."


class ImportMapping(BaseModel):
    """FR-001, N19: the identification's column, one or two for the display name in order, and
    optionally level, grade, institution and recovery e-mail."""

    identification: str = Field(..., max_length=200)
    name: list[str] = Field(..., min_length=1, max_length=2)
    level: str | None = Field(default=None, max_length=200)
    grade: str | None = Field(default=None, max_length=200)
    institution: str | None = Field(default=None, max_length=200)
    recovery_email: str | None = Field(default=None, max_length=200)

    def columns(self) -> list:
        mapped = [self.identification, *self.name]
        mapped += [c for c in (self.level, self.grade, self.institution, self.recovery_email) if c]
        return list(dict.fromkeys(mapped))


class ImportBatch(BaseModel):
    """FR-001, N20: the level and grade where not mapped, and the last day of access."""

    level: str | None = Field(default=None, max_length=20)
    grade: int | None = None
    access_until: str | None = Field(default=None, max_length=20)


class PairChoice(BaseModel):
    """N21: one (institution, grade) pair of the file and the group the admin paired it with."""

    institution: str | None = Field(default=None, max_length=200)
    grade: int | None = None
    group_id: int


class ConfirmedChange(BaseModel):
    """FR-008, N27: the changes to one existing account the admin confirms."""

    row: int
    changes: list[str] = Field(default_factory=list, max_length=3)


class LinkRequest(BaseModel):
    identification: str = Field(..., max_length=40)


class GroupForTeacherRequest(BaseModel):
    """N25, N26 (a). Checked by the account rules; loose on purpose, as spec 004's creation."""

    name: str = Field(..., max_length=100)
    course_id: str | None = Field(default=None, max_length=200)
    institution: str | None = Field(default=None, max_length=200)
    grade: int | None = None


def _parsed(model, text, many=False):
    try:
        value = json.loads(text) if text else ([] if many else None)
        if many:
            return [model.model_validate(v) for v in value]
        return model.model_validate(value)
    except (ValueError, TypeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las opciones de la importación no son válidas.",
        ) from None


def _read_upload(request: Request, file: UploadFile) -> bytes:
    """P12: the size limit before reading the whole file — from Content-Length, then while
    reading."""
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BYTES + 64 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, _FILE_PROBLEMS["too_large"])
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, _FILE_PROBLEMS["too_large"])
    return data


def _sheet(data: bytes, filename: str, keep=None):
    try:
        return read_spreadsheet(data, filename, keep=keep)
    except SpreadsheetError as refused:
        code = (
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            if refused.code == "too_large"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=_FILE_PROBLEMS[refused.code]) from None


def _checked_batch(batch: ImportBatch, mapping: ImportMapping) -> dict:
    """The batch's choices, refused as spec 004's creation refuses them: a last day already past or
    not a date, and a level that is not one of the four when the file does not map it."""
    from datetime import datetime, timezone

    try:
        last_day = parse_last_day(batch.access_until)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None
    if access_expired(last_day, datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El último día de acceso ya pasó."
        )
    if not mapping.level and batch.level not in VALID_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Elige el nivel del lote: colegio, universidad, concursos o semillero.",
        )
    return {
        "level": batch.level,
        "grade": batch.grade,
        "access_until": last_day.isoformat() if last_day else None,
    }


def _preview(repo, data, filename, mapping: ImportMapping, batch: ImportBatch, pairing):
    """Plan § Preview: every row's status, the file's pairs with their suggested and chosen groups,
    and the digest of what the admin sees. Saves nothing."""
    batch_choices = _checked_batch(batch, mapping)
    sheet = _sheet(data, filename, keep=mapping.columns())
    rows = [(row.number, row.values) for row in sheet.rows]
    mapping_dict = mapping.model_dump()
    pairs = file_pairs(rows, mapping_dict, batch_choices)
    groups = repo.get_all_groups()
    known = {g["id"] for g in groups}
    suggested = suggest_pairing(
        pairs,
        [
            {"group_id": g["id"], "institution": g.get("institution"), "grade": g.get("grade")}
            for g in groups
        ],
    )
    chosen = {(p.institution, p.grade): p.group_id for p in pairing}
    effective = {}
    for pair in pairs:
        group_id = chosen.get(pair, suggested.get(pair))
        if group_id in known:
            effective[pair] = group_id
    identifications = []
    for _number, values in rows:
        identification, _ = read_identification(values.get(mapping.identification))
        if identification is not None:
            identifications.append(identification)
    lookups = repo.get_import_lookups(identifications)
    statuses = classify_rows(
        rows, mapping_dict, batch_choices, effective, lookups["linked"], lookups["usernames"]
    )
    seen_batch = {
        **batch_choices,
        "pairing": sorted(
            ([inst, grade, gid] for (inst, grade), gid in effective.items()),
            key=lambda p: (p[0] or "", p[1] or 0),
        ),
    }
    digest = preview_digest(data, mapping_dict, seen_batch, statuses)
    pair_view = [
        {
            "institution": institution,
            "grade": grade,
            "group_id": effective.get((institution, grade)),
            "suggested_group_id": suggested.get((institution, grade)),
        }
        for institution, grade in pairs
    ]
    return statuses, pair_view, digest, batch_choices


def _counts(statuses) -> dict:
    counts = dict.fromkeys(("new", "existing", "duplicate", "error"), 0)
    for row in statuses:
        counts[row["status"]] += 1
    return counts


@router.post("/imports/columns")
def import_columns(request: Request, user: CurrentUser, file: UploadFile = File(...)):
    """FR-001, N23: the file's header, up to five example rows — shown to the admin to choose the
    columns, never stored — and the mapping the form's headers suggest (T024)."""
    data = _read_upload(request, file)
    sheet = _sheet(data, file.filename)
    examples = [
        ["" if row.values.get(c) is None else str(row.values.get(c)) for c in sheet.header]
        for row in sheet.rows[:EXAMPLE_ROWS]
    ]
    return {
        "header": sheet.header,
        "examples": examples,
        "rows": len(sheet.rows),
        "suggested": suggest_mapping(sheet.header),
    }


@router.post("/imports/preview")
def import_preview(
    request: Request,
    user: CurrentUser,
    repo: RepoDep,
    file: UploadFile = File(...),
    mapping: str = Form(...),
    batch: str = Form(...),
    pairing: str = Form("[]"),
):
    """FR-002, US1-AS1: each row as new, existing, duplicate or error with its reasons, and the
    level, grade and group it would get; each (institution, grade) pair with its group, suggested
    under N26 (a). Nothing is saved; the digest goes back with the confirmation (FR-003)."""
    data = _read_upload(request, file)
    statuses, pairs, digest, _ = _preview(
        repo,
        data,
        file.filename,
        _parsed(ImportMapping, mapping),
        _parsed(ImportBatch, batch),
        _parsed(PairChoice, pairing, many=True),
    )
    return {"rows": statuses, "counts": _counts(statuses), "pairs": pairs, "digest": digest}


def _run_import(repo, import_id, admin_id, statuses, access_until, confirmed):
    """The confirmed import, in a worker thread (plan § Running the import): the new rows in
    chunks, then each existing account's confirmed changes through the existing operations, then
    every other row's result. A chunk that finds the import no longer running stops it."""
    try:
        new_rows = [
            {
                "row": s["row"],
                "identification": s["identification"],
                "display_name": s["display_name"],
                "level": s["level"],
                "grade": s["grade"],
                "group_id": s["group_id"],
                "access_until": access_until,
                "recovery_email": s["recovery_email"],
            }
            for s in statuses
            if s["status"] == "new"
        ]
        for start in range(0, len(new_rows), CHUNK_SIZE):
            if repo.import_student_chunk(import_id, new_rows[start : start + CHUNK_SIZE]) is None:
                logger.warning("Import %s stopped: no longer running.", import_id)
                return
        others = []
        for s in statuses:
            if s["status"] == "existing":
                others.append(_apply_changes(repo, admin_id, s, confirmed.get(s["row"], set())))
            elif s["status"] == "duplicate":
                others.append({"row": s["row"], "result": "duplicate"})
            elif s["status"] == "error":
                reason = s["reasons"][0] if s["reasons"] else None
                others.append({"row": s["row"], "result": "error", "reason": reason})
        if others and not repo.record_import_rows(import_id, others):
            logger.warning("Import %s stopped: no longer running.", import_id)
            return
        repo.finish_import(import_id)
    except Exception as exc:  # the text may hold a row's values (FR-011): only its type
        logger.error("Import %s failed: %s", import_id, type(exc).__name__)


def _apply_changes(repo, admin_id, status_row, fields) -> dict:
    """FR-008, N27: only the confirmed changes of one existing account, each through its own
    audited operation; nothing else of the account is touched."""
    user_id, changes = status_row["account_id"], status_row["changes"]
    applied, refused = 0, None
    for field in ("group_id", "access_until", "recovery_email"):
        if field not in fields or field not in changes:
            continue
        target = changes[field]["to"]
        if field == "group_id":
            ok, _ = repo.change_student_group(user_id, target, admin_id)
        elif field == "access_until":
            ok, _ = repo.set_access_until(admin_id, user_id, target)
        else:
            ok, _ = repo.set_recovery_email(admin_id, user_id, target)
        if ok:
            applied += 1
        else:
            refused = f"{field}_refused"
    return {
        "row": status_row["row"],
        "result": "updated" if applied else "unchanged",
        "user_id": user_id,
        "reason": refused,
    }


@router.post("/imports", status_code=status.HTTP_202_ACCEPTED)
def confirm_import(
    request: Request,
    user: CurrentUser,
    repo: RepoDep,
    file: UploadFile = File(...),
    mapping: str = Form(...),
    batch: str = Form(...),
    pairing: str = Form("[]"),
    digest: str = Form(..., max_length=128),
    confirm: str = Form("[]"),
):
    """FR-003, FR-010, US1-AS2, US1-AS8: the same file and choices again, with the preview's
    digest and the changes to existing accounts the admin confirms one by one. A different digest
    asks for a new preview; a retry of the same confirmation returns the same import; another
    while one runs is refused. The import runs in a worker thread; poll its state."""
    data = _read_upload(request, file)
    statuses, _, current, batch_choices = _preview(
        repo,
        data,
        file.filename,
        _parsed(ImportMapping, mapping),
        _parsed(ImportBatch, batch),
        _parsed(PairChoice, pairing, many=True),
    )
    if current != digest:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_CHANGED)
    existing = {s["row"]: s for s in statuses if s["status"] == "existing"}
    confirmed = {}
    for choice in _parsed(ConfirmedChange, confirm, many=True):
        row = existing.get(choice.row)
        if row is None or not set(choice.changes) <= set(row["changes"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un cambio confirmado no aparece en la vista previa.",
            )
        confirmed[choice.row] = set(choice.changes)
    outcome, record = repo.start_import(user["user_id"], digest, len(statuses))
    if outcome == "refused":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el administrador.")
    if outcome == "busy":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_BUSY)
    if outcome == "started":
        threading.Thread(
            target=_run_import,
            args=(
                repo,
                record["import_id"],
                user["user_id"],
                statuses,
                batch_choices["access_until"],
                confirmed,
            ),
            name=f"student-import-{record['import_id'][:8]}",
            daemon=True,
        ).start()
    return {"import_id": record["import_id"], "state": record["state"], "retry": outcome == "retry"}


@router.get("/imports")
def list_imports(user: CurrentUser, repo: RepoDep):
    """FR-009: the admin's imports, most recent first, with their counts."""
    return {"imports": repo.list_imports(user["user_id"])}


@router.get("/imports/{import_id}")
def get_import(import_id: str, user: CurrentUser, repo: RepoDep):
    """US1-AS7: the import's state, counts and each row's result with internal IDs and reason
    codes."""
    record = repo.get_import(import_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Importación no encontrada."
        )
    return record


@router.put("/users/{user_id}/identification")
def link_identification(user_id: int, body: LinkRequest, user: CurrentUser, repo: RepoDep):
    """FR-007, US1-AS5: links an identification to a student account without one; later imports
    find it. Nothing is merged by name and the username does not change."""
    ok, message = repo.link_identification(user["user_id"], user_id, body.identification)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {
        "user_id": user_id,
        "identification": repo.get_student_identification(user_id)["identification"],
    }


@router.delete("/users/{user_id}/identification", status_code=status.HTTP_204_NO_CONTENT)
def unlink_identification(user_id: int, user: CurrentUser, repo: RepoDep):
    """FR-017 (N18): removes a link made by mistake; recorded, username and credentials kept."""
    ok, message = repo.unlink_identification(user["user_id"], user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.get("/courses")
def list_courses(user: CurrentUser, repo: RepoDep):
    """N25: the catalogue's courses, for the group the admin creates for a teacher."""
    return {
        "courses": [
            {"id": c["id"], "name": c["name"], "block": c.get("block")} for c in repo.get_courses()
        ]
    }


@router.post("/teachers/{teacher_id}/groups", status_code=status.HTTP_201_CREATED)
def create_group_for_teacher(
    teacher_id: int, body: GroupForTeacherRequest, user: CurrentUser, repo: RepoDep
):
    """N25, N26 (a): a group owned by the teacher, for an institution and grade, through the
    teacher's own group creation."""
    ok, message, group_id = repo.create_group_for_teacher(
        user["user_id"],
        teacher_id,
        body.name,
        body.course_id,
        institution=body.institution,
        grade=body.grade,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"group_id": group_id, "name": body.name.strip()}
