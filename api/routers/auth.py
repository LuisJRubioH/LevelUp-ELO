"""
api/routers/auth.py
===================
Endpoints de autenticación:
  POST /auth/login    → access + refresh tokens
  POST /auth/register → registro de usuario
  POST /auth/refresh  → nuevo access token
  POST /auth/logout   → borra cookie de refresh token
  GET  /auth/me       → perfil del usuario autenticado
  POST /auth/password → cambio de contraseña (spec 004 E2)
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status

from api.config import settings
from api.dependencies import (
    SESSION_REVOKED,
    CurrentUserDuringPasswordChange,
    RepoDep,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from api.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)
from api.rate_limit import client_ip, limiter, login_allowed, login_limit_key
from api.websocket.connections import close_user_sync
from src.domain.identity import PASSWORD_MIN_LENGTH, valid_new_password


def _same_site_request(request: Request) -> None:
    """Spec 004 FR-082: a browser sends `Origin` with every state-changing request; one from an
    origin the API does not serve is refused before anything happens (sign-in, renewal, sign-out
    or password change on someone else's behalf). Requests without `Origin` (other programs, tests)
    pass: they carry no browser's cookies to abuse."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    origin = request.headers.get("origin")
    if origin is not None and origin.rstrip("/") not in {
        allowed.rstrip("/") for allowed in settings.cors_origins
    }:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origen no permitido.")


router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(_same_site_request)])

_REFRESH_COOKIE = "levelup_refresh"


_LOGIN_LIMITED = "Demasiados intentos de inicio de sesión. Espera un minuto e inténtalo de nuevo."
_WRONG_CURRENT_PASSWORD = "La contraseña actual no es correcta."
_WEAK_NEW_PASSWORD = (
    f"La nueva contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres sin contar espacios"
    " al principio o al final."
)


def _refresh_cookie_scope() -> dict:
    """Spec 004 FR-081: HttpOnly, Secure, only for the auth paths, SameSite from the setting —
    the same attributes to set it and to delete it."""
    return {
        "httponly": True,
        "secure": True,
        "samesite": settings.auth_cookie_samesite,
        "path": "/api/auth",
    }


def _issue_session(response: Response, user_id: int, account: dict) -> TokenResponse:
    """Access token and refresh cookie for `account` (a `get_user_by_id` row), both bound to its
    current security version (spec 004 FR-027)."""
    version = int(account.get("security_version") or 0)
    access_token = create_access_token(user_id, account["username"], account["role"], version)
    refresh_token = create_refresh_token(user_id, version)
    # Refresh token en cookie HttpOnly para no exponerlo en JS
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 86400,
        **_refresh_cookie_scope(),
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id,
        username=account["username"],
        role=account["role"],
        must_change_password=bool(account.get("must_change_password")),
    )


_REGISTRATION_CLOSED = "El registro público está cerrado. Pide tu cuenta a tu colegio."


@router.post("/login", response_model=TokenResponse)
def login(request: Request, body: LoginRequest, response: Response, repo: RepoDep):
    """Autentica usuario y retorna access token + refresh token en cookie HttpOnly.

    Spec 004 E1: limited per account and overall, never per address, so a class on one school
    network signs in (FR-006 … FR-008). A refusal is the same whether the account exists (FR-010).
    """
    key = login_limit_key(repo.login_account_id(body.username), body.username)
    if not login_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_LOGIN_LIMITED,
            headers={"Retry-After": "60"},
        )
    result = repo.login_user(body.username, body.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o usuario inactivo.",
        )
    user_id, username, role, approved = result

    if role == "teacher" and not approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de docente está pendiente de aprobación.",
        )

    # Spec 004 FR-030: a temporary password signs in, and the screen then asks for a new one.
    account = repo.get_user_by_id(user_id) or {"username": username, "role": role}
    return _issue_session(response, user_id, account)


@router.get("/registration")
def registration_status():
    """Spec 004 FR-003: whether public registration is open, for the login screen."""
    return {"enabled": settings.public_registration_enabled}


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: settings.rate_limit_register, key_func=client_ip)
def register(request: Request, body: RegisterRequest, repo: RepoDep):
    """Registra un nuevo usuario (student o teacher) — solo con el registro público abierto.

    Spec 004 FR-001/FR-002: closed by default and refused here, on the server; its own
    per-address limit applies (FR-004). A teacher still waits for approval (FR-005).
    """
    if not settings.public_registration_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_REGISTRATION_CLOSED)
    ok, msg = repo.register_user(
        username=body.username,
        password=body.password,
        role=body.role,
        education_level=body.education_level,
        grade=body.grade,
        email=body.email,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    response: Response,
    repo: RepoDep,
    body: RefreshRequest | None = None,
    cookie_token: Annotated[str | None, Cookie(alias=_REFRESH_COOKIE)] = None,
):
    """Emite un nuevo access token a partir del refresh token."""
    token = cookie_token or (body.refresh_token if body else None)
    if not token:
        raise HTTPException(status_code=401, detail="Token de refresh requerido.")
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de refresh inválido."
        )
    user_id = int(payload["sub"])

    # Verificar que el usuario sigue activo
    profile = _get_profile_row(repo, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo."
        )
    # Spec 004 FR-027: a renewal issued before a password change or a reset no longer works.
    if int(payload.get("sv", 0)) != int(profile.get("security_version") or 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=SESSION_REVOKED)

    return _issue_session(response, user_id, profile)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Elimina la cookie de refresh token, con los mismos atributos con que se creó (FR-081):
    sin Secure ni SameSite=None, un navegador no borra una cookie de otro sitio."""
    response.delete_cookie(key=_REFRESH_COOKIE, **_refresh_cookie_scope())


@router.get("/me", response_model=UserProfile)
def me(user: CurrentUserDuringPasswordChange, repo: RepoDep):
    """Retorna el perfil del usuario autenticado, también mientras debe cambiar una contraseña
    temporal (spec 004 FR-030)."""
    profile = _get_profile_row(repo, user["user_id"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return UserProfile(
        user_id=user["user_id"],
        username=profile["username"],
        role=profile["role"],
        approved=bool(profile.get("approved", True)),
        education_level=profile.get("education_level"),
        grade=profile.get("grade"),
        email=profile.get("email"),
        must_change_password=user["must_change_password"],
    )


@router.post("/password", response_model=TokenResponse)
def change_password(
    body: PasswordChangeRequest,
    response: Response,
    user: CurrentUserDuringPasswordChange,
    repo: RepoDep,
):
    """Spec 004 FR-026, FR-028, FR-030: the signed-in user replaces their password, giving the
    current one. The security version advances: every other session's tokens, renewals and open
    connections stop working, and this session receives new credentials.

    Attempts count against the account's sign-in limit (FR-006): a stolen session cannot test
    current passwords faster than the login screen.
    """
    user_id = user["user_id"]
    if not login_allowed(login_limit_key(user_id, user["username"])):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_LOGIN_LIMITED,
            headers={"Retry-After": "60"},
        )
    if not repo.verify_user_password(user_id, body.current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_WRONG_CURRENT_PASSWORD)
    if not valid_new_password(body.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_WEAK_NEW_PASSWORD)
    if repo.set_user_password(user_id, body.new_password, must_change=False) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    close_user_sync(user_id)
    return _issue_session(response, user_id, repo.get_user_by_id(user_id))


# ── helper interno ────────────────────────────────────────────────────────────


def _get_profile_row(repo, user_id: int) -> dict | None:
    """Lee username/role/approved/education_level/grade/email para un user_id activo."""
    try:
        conn = repo.get_connection()
        try:
            cur = conn.cursor()
            # PostgreSQL usa %s, SQLite usa ? como placeholder
            ph = "%s" if hasattr(repo, "put_connection") else "?"
            cur.execute(
                f"SELECT username, role, approved, education_level, grade, email, "
                f"security_version, must_change_password "
                f"FROM users WHERE id = {ph} AND active = 1",
                (user_id,),
            )
            row = cur.fetchone()
        finally:
            # Devuelve conexión al pool (PostgreSQL) o la cierra (SQLite)
            if hasattr(repo, "put_connection"):
                repo.put_connection(conn)
            else:
                conn.close()
    except Exception:
        return None

    if not row:
        return None

    # Soporta tanto dict (RealDictCursor PG) como tuple (SQLite)
    if isinstance(row, dict):
        return dict(row)
    return {
        "username": row[0],
        "role": row[1],
        "approved": row[2],
        "education_level": row[3],
        "grade": row[4],
        "email": row[5],
        "security_version": row[6],
        "must_change_password": row[7],
    }
