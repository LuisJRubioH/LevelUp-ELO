"""
api/routers/auth.py
===================
Endpoints de autenticación:
  POST /auth/login    → access + refresh tokens
  POST /auth/register → registro de usuario
  POST /auth/refresh  → nuevo access token
  POST /auth/logout   → borra cookie de refresh token
  GET  /auth/me       → perfil del usuario autenticado
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status

from api.config import settings
from api.dependencies import (
    CurrentUser,
    RepoDep,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)
from api.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "levelup_refresh"


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def login(request: Request, body: LoginRequest, response: Response, repo: RepoDep):
    """Autentica usuario y retorna access token + refresh token en cookie HttpOnly."""
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

    access_token = create_access_token(user_id, username, role)
    refresh_token = create_refresh_token(user_id)

    # Refresh token en cookie HttpOnly para no exponerlo en JS
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",  # cross-origin (frontend Vercel ↔ backend Render)
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth",
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id,
        username=username,
        role=role,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
def register(request: Request, body: RegisterRequest, repo: RepoDep):
    """Registra un nuevo usuario (student o teacher)."""
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

    new_access = create_access_token(user_id, profile["username"], profile["role"])
    new_refresh = create_refresh_token(user_id)

    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="none",  # cross-origin (frontend Vercel ↔ backend Render)
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth",
    )

    return TokenResponse(
        access_token=new_access,
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id,
        username=profile["username"],
        role=profile["role"],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Elimina la cookie de refresh token."""
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/auth")


@router.get("/me", response_model=UserProfile)
def me(user: CurrentUser, repo: RepoDep):
    """Retorna el perfil del usuario autenticado."""
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
    )


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
                f"SELECT username, role, approved, education_level, grade, email "
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
    }
