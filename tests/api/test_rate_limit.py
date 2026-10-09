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
