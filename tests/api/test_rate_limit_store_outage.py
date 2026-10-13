"""Si el almacén compartido de los límites (Redis) no responde, el login y la IA siguen
funcionando con el límite contado en memoria del proceso, en vez de responder 500."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Un puerto donde nada escucha: la conexión se rechaza al instante.
_UNREACHABLE_STORE = "redis://127.0.0.1:1"


def test_limits_keep_working_in_memory_when_the_store_is_down():
    from api.rate_limit import build_limiter

    limiter = build_limiter(_UNREACHABLE_STORE)
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.post("/probe")
    @limiter.limit("3/minute")
    def probe(request: Request):
        return {"ok": True}

    client = TestClient(app, raise_server_exceptions=False)
    statuses = [client.post("/probe").status_code for _ in range(5)]

    assert statuses == [200, 200, 200, 429, 429]


def test_the_app_limiter_is_built_with_the_fallback():
    from api.rate_limit import limiter

    assert limiter._in_memory_fallback_enabled
