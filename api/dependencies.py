"""
api/dependencies.py
===================
Dependencias FastAPI reutilizables:
  - get_repository()  → instancia del repositorio (SQLite o PostgreSQL)
  - create_tokens()   → par (access_token, refresh_token)
  - get_current_user() → verifica JWT y retorna payload del usuario
  - build_vector_rating() → reconstruye VectorRating desde DB para un usuario
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from api.config import settings

# ── Bearer token extractor ────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer(auto_error=False)


# ── Repositorio ───────────────────────────────────────────────────────────────


def get_repository():
    """
    Retorna la instancia correcta del repositorio según el entorno.
    DATABASE_URL presente → PostgresRepository; ausente → SQLiteRepository.
    """
    if os.environ.get("DATABASE_URL") or settings.database_url:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        return PostgresRepository()
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    return SQLiteRepository()


RepoDep = Annotated[object, Depends(get_repository)]


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
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decodifica y valida el token JWT. Lanza HTTPException si es inválido."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Dependencia de usuario autenticado ────────────────────────────────────────


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
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
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere access token, no refresh token.",
        )
    return {
        "user_id": int(payload["sub"]),
        "username": payload["username"],
        "role": payload["role"],
    }


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


# ── VectorRating desde DB ─────────────────────────────────────────────────────


def build_vector_rating(user_id: int, repo) -> object:
    """
    Reconstruye el VectorRating del estudiante cargando su historial de ELO
    por tópico desde la DB. Retorna una instancia fresca de VectorRating.
    """
    from src.domain.elo.vector_elo import VectorRating

    vector = VectorRating()
    topic_elos = repo.get_latest_elo_by_topic(user_id)
    for row in topic_elos:
        topic = row["topic"] if isinstance(row, dict) else row[0]
        elo = row["elo_after"] if isinstance(row, dict) else row[1]
        rd = (
            row["rating_deviation"]
            if isinstance(row, dict)
            else (row[2] if len(row) > 2 else 350.0)
        )
        # Inyectar directamente en el dict interno (sin pasar por update)
        vector.ratings[topic] = (float(elo), float(rd) if rd else 350.0)
    return vector
