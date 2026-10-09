"""Rate limiting compartido para operaciones costosas de la API."""

import hashlib

from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings


def _client_key(request) -> str:
    """Separa usuarios autenticados sin almacenar ni registrar su token."""
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        digest = hashlib.sha256(authorization[7:].encode("utf-8")).hexdigest()
        return f"token:{digest}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_client_key, storage_uri=settings.rate_limit_storage_uri)
