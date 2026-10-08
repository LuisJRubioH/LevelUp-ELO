"""
api/dependencies.py
===================
Dependencias FastAPI reutilizables:
  - get_repository()  → instancia del repositorio (SQLite o PostgreSQL)
  - create_tokens()   → par (access_token, refresh_token)
  - get_current_user() → verifica JWT y retorna payload del usuario
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import InvalidTokenError

from api.config import settings
from src.application.interfaces.repositories import IRepository

# ── Bearer token extractor ────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer(auto_error=False)


# ── Repositorio (singleton por proceso) ──────────────────────────────────────

_repo_instance = None


def get_repository():
    """
    Retorna la instancia singleton del repositorio.
    La instancia se crea una sola vez por proceso; init_db() solo corre al
    arrancar (en el lifespan de main.py), no en cada petición.

    DATABASE_URL presente → PostgresRepository; ausente → SQLiteRepository.
    """
    global _repo_instance
    if _repo_instance is not None:
        return _repo_instance

    if os.environ.get("DATABASE_URL"):
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        _repo_instance = PostgresRepository()
    else:
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

        _repo_instance = SQLiteRepository()

    return _repo_instance


RepoDep = Annotated[IRepository, Depends(get_repository)]


# ── JWT helpers ───────────────────────────────────────────────────────────────


def create_access_token(user_id: int, username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": uuid.uuid4().hex,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_procedure_review_token(
    user_id: int, item_id: str, file_hash: str, score: float | None, feedback: str
) -> str:
    payload = {
        "sub": str(user_id),
        "type": "procedure_review",
        "item_id": item_id,
        "file_hash": file_hash,
        "score": score,
        "feedback": feedback[:4000],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decodifica y valida el token JWT. Lanza HTTPException si es inválido."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Dependencia de usuario autenticado ────────────────────────────────────────


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    repo: RepoDep,
) -> dict:
    """
    Extrae el usuario del JWT Bearer token.
    Retorna dict con: user_id (int), username (str), role (str).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authenticate_access_token(credentials.credentials, repo)


def authenticate_access_token(token: str, repo) -> dict:
    """Valida un access token y el estado actual de la cuenta, también para WebSockets."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere access token, no refresh token.",
        )
    user_id = int(payload["sub"])
    current = repo.get_user_by_id(user_id)
    if not current or not current.get("active", False):
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo.")
    if current["role"] == "teacher" and not current.get("approved", False):
        raise HTTPException(status_code=403, detail="Cuenta docente pendiente de aprobación.")
    return {"user_id": user_id, "username": current["username"], "role": current["role"]}


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    """Factory que retorna una dependencia que exige uno de los roles dados."""

    def _check(user: CurrentUser):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {list(roles)}",
            )
        return user

    return Depends(_check)
