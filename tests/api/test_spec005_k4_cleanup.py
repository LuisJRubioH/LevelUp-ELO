"""
Spec 005 delivery K4 (FR-040): what nothing uses any more is gone.

The legacy `POST /api/ai/review-procedure` (unused by the frontend, synchronous inside `async def`,
no PDF conversion) no longer exists; the procedure review is `/api/student/procedure/analyze`. No
setting is read for a student analysis, and the provider is never read from a setting: the key's
prefix decides (FR-010).
"""

import io

import pytest


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def test_the_legacy_review_endpoint_is_gone(api_client, student_headers):
    response = api_client.post(
        "/api/ai/review-procedure",
        headers=student_headers,
        data={"item_id": "q21"},
        files={"file": ("p.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )

    assert response.status_code == 404
    paths = {route.path for route in api_client.app.routes}
    assert "/api/ai/review-procedure" not in paths
    assert "/api/student/procedure/analyze" in paths


def test_no_setting_for_student_analysis(monkeypatch):
    """`AI_KEY_STUDENT_ANALYSIS` and `SYSTEM_AI_PROVIDER` are read by nothing; set in an old host's
    environment they are ignored, not an error."""
    from api.config import Settings

    monkeypatch.setenv("AI_KEY_STUDENT_ANALYSIS", "gsk_old")
    monkeypatch.setenv("SYSTEM_AI_PROVIDER", "anthropic")
    settings = Settings(system_ai_api_key="general")

    assert "ai_key_student_analysis" not in Settings.model_fields
    assert "system_ai_provider" not in Settings.model_fields
    assert settings.get_ai_key("student_analysis") == "general"
