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


def build_limiter(storage_uri: str) -> Limiter:
    """Limiter con los contadores en `storage_uri` (Redis en producción).

    Si ese almacén no responde, cuenta en memoria del proceso hasta que vuelva: sin esto, una
    caída de Redis convierte en 500 el login, el registro y la IA. Con un solo proceso (R18) el
    límite en memoria es el mismo límite; solo se pierde lo contado antes de la caída.
    """
    return Limiter(key_func=_client_key, storage_uri=storage_uri, in_memory_fallback_enabled=True)


limiter = build_limiter(settings.rate_limit_storage_uri)
