"""Las operaciones de IA deben aplicar los límites declarados en configuración."""


def test_socratic_rate_limit_is_enforced_per_access_token(api_client, student_headers):
    from api.rate_limit import limiter

    limiter._storage.reset()
    payload = {
        "item_id": "rate-limit-probe",
        "item_content": "Contenido de prueba",
        "student_message": "Ayúdame a pensar",
        "course_id": "calculo_diferencial",
    }
    responses = [
        api_client.post("/api/ai/socratic", headers=student_headers, json=payload)
        for _ in range(11)
    ]
    assert all(response.status_code == 422 for response in responses[:10])
    assert responses[10].status_code == 429
    limiter._storage.reset()


def test_login_rate_limit_is_enforced_per_origin(api_client):
    from api.rate_limit import limiter

    limiter._storage.reset()
    responses = [
        api_client.post(
            "/api/auth/login",
            json={"username": "rate-limit-missing", "password": "invalid-password"},
        )
        for _ in range(21)
    ]
    assert all(response.status_code == 401 for response in responses[:20])
    assert responses[20].status_code == 429
    limiter._storage.reset()


def _socratic_payload() -> dict:
    return {
        "item_id": "rate-limit-probe",
        "item_content": "Contenido de prueba",
        "student_message": "Ayúdame a pensar",
        "course_id": "calculo_diferencial",
    }


def test_login_rate_limit_ignores_an_invented_authorization_header(api_client):
    """Login is keyed by origin only: a made-up bearer per request is not a fresh allowance."""
    import secrets

    from api.rate_limit import limiter

    limiter._storage.reset()
    responses = [
        api_client.post(
            "/api/auth/login",
            json={"username": "rate-limit-missing", "password": "invalid-password"},
            headers={"Authorization": f"Bearer {secrets.token_hex(16)}"},
        )
        for _ in range(21)
    ]
    assert all(response.status_code == 401 for response in responses[:20])
    assert responses[20].status_code == 429
    limiter._storage.reset()


def test_ai_rate_limit_follows_the_account_across_new_tokens(
    api_client, student_token, student_headers
):
    """A new access token for the same account (refresh, login again) does not reset the limit."""
    from datetime import datetime, timedelta, timezone

    import jwt

    from api.config import settings
    from api.rate_limit import limiter

    claims = jwt.decode(student_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    claims["exp"] = datetime.now(timezone.utc) + timedelta(minutes=7)
    fresh = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    assert fresh != student_token

    limiter._storage.reset()
    for _ in range(10):
        assert (
            api_client.post(
                "/api/ai/socratic", headers=student_headers, json=_socratic_payload()
            ).status_code
            == 422
        )
    response = api_client.post(
        "/api/ai/socratic",
        headers={"Authorization": f"Bearer {fresh}"},
        json=_socratic_payload(),
    )
    assert response.status_code == 429
    limiter._storage.reset()


def test_ai_rate_limit_is_not_shared_between_accounts(api_client, student_headers):
    """Students behind the same school IP each keep their own allowance."""
    from api.rate_limit import limiter

    other = api_client.post(
        "/api/auth/login", json={"username": "estudiante2", "password": "demo1234"}
    )
    assert other.status_code == 200
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    limiter._storage.reset()
    for _ in range(10):
        api_client.post("/api/ai/socratic", headers=student_headers, json=_socratic_payload())
    assert (
        api_client.post(
            "/api/ai/socratic", headers=student_headers, json=_socratic_payload()
        ).status_code
        == 429
    )
    assert (
        api_client.post(
            "/api/ai/socratic", headers=other_headers, json=_socratic_payload()
        ).status_code
        == 422
    )
    limiter._storage.reset()
