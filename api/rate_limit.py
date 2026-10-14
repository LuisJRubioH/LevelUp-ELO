"""Rate limiting compartido para operaciones costosas de la API."""

import jwt
from jwt.exceptions import InvalidTokenError
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
