"""Rate limiting compartido para operaciones costosas de la API."""

import hashlib

import jwt
from jwt.exceptions import InvalidTokenError
from limits import parse
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings


def client_ip(request) -> str:
    """Login y registro: quien llama aún no tiene cuenta, así que solo cuenta su origen."""
    return f"ip:{get_remote_address(request)}"


def _client_key(request) -> str:
    """Separa usuarios autenticados por cuenta, sin almacenar ni registrar su token.

    Por cuenta y no por token: un token nuevo (refresh o login) no reinicia el límite, y los
    estudiantes detrás de la misma IP del colegio no lo comparten. Una cabecera que no es un
    access token válido cuenta como ausente; si no, una inventada por petición sería un cupo nuevo.
    """
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        try:
            payload = jwt.decode(
                authorization[7:], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except InvalidTokenError:
            payload = {}
        if payload.get("type") == "access" and payload.get("sub"):
            return f"user:{payload['sub']}"
    return client_ip(request)


limiter = Limiter(key_func=_client_key, storage_uri=settings.rate_limit_storage_uri)


def login_limit_key(account_id: int | None, identifier: str) -> str:
    """Spec 004 FR-006, FR-011: the counter a sign-in attempt goes to.

    An attempt that names an active account — by username or by email — counts for that account.
    Any other identifier counts for itself, after trimming outer spaces and ignoring letter case,
    and only as a one-way digest: the limit store holds no readable identifier (FR-011).
    """
    if account_id is not None:
        return f"account:{account_id}"
    digest = hashlib.sha256(identifier.strip().casefold().encode("utf-8")).hexdigest()
    return f"identifier:{digest}"


def login_allowed(key: str) -> bool:
    """Spec 004 FR-006, FR-007: count one attempt on the global and on the key's counter; False if
    either is over its limit for the current minute. Values come from settings at each call."""
    strategy = limiter.limiter
    overall = strategy.hit(parse(settings.rate_limit_login_global), "login", "all")
    account = strategy.hit(parse(settings.rate_limit_login_account), "login", key)
    return overall and account
