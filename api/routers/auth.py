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

from fastapi import APIRouter, HTTPException, Response, status

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

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "levelup_refresh"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, response: Response, repo: RepoDep):
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
        path="/auth",
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id,
        username=username,
        role=role,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, repo: RepoDep):
    """Registra un nuevo usuario (student o teacher)."""
    ok, msg = repo.register_user(
        username=body.username,
        password=body.password,
        role=body.role,
        education_level=body.education_level,
        grade=body.grade,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshRequest, response: Response, repo: RepoDep):
    """Emite un nuevo access token a partir del refresh token."""
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de refresh inválido."
        )
    user_id = int(payload["sub"])

    # Verificar que el usuario sigue activo
    user_row = repo.login_user.__func__  # no podemos llamar login_user sin password
    # En su lugar consultamos directamente con un método auxiliar
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
        path="/auth",
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
    response.delete_cookie(key=_REFRESH_COOKIE, path="/auth")


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
    )


# ── helper interno ────────────────────────────────────────────────────────────


def _get_profile_row(repo, user_id: int) -> dict | None:
    """Lee username/role/approved/education_level/grade para un user_id activo."""
    try:
        conn = repo.get_connection()
        try:
            cur = conn.cursor()
            # PostgreSQL usa %s, SQLite usa ? como placeholder
            ph = "%s" if hasattr(repo, "put_connection") else "?"
            cur.execute(
                f"SELECT username, role, approved, education_level, grade "
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
    }
