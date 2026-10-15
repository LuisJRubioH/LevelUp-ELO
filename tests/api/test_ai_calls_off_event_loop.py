"""
A procedure review waits seconds (up to minutes, with the SDK's own retries) on an AI provider.
The API is one process (AGENTS R18): while that wait runs on the event loop, every other request
and every PvP socket waits too. R17: blocking work in an `async def` goes through a thread. With
a provider that takes 1.5 s, the API must keep answering other requests meanwhile.
"""

import io
import threading
import time

import pytest

SLOW = 1.5


def _png() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


def _slow_groq_review(*_args, **_kwargs):
    time.sleep(SLOW)
    return {"score_procedimiento": 70, "evaluacion_global": "bien"}


def _slow_vision_review(*_args, **_kwargs):
    time.sleep(SLOW)
    return "bien"


@pytest.mark.parametrize(
    "api_key, target, fake",
    [
        ("gsk_fake_test_key", "math_procedure_review.review_math_procedure", _slow_groq_review),
        ("sk-ant-fake-test-key", "ai_client.analyze_procedure_image", _slow_vision_review),
    ],
    ids=["groq-review", "vision-review"],
)
def test_the_api_answers_while_a_procedure_is_reviewed(
    api_client, student_headers, monkeypatch, api_key, target, fake
):
    from api.rate_limit import limiter

    module, name = target.split(".")
    monkeypatch.setattr(f"src.infrastructure.external_api.{module}.{name}", fake)
    limiter.reset()

    review = {}

    def analyze():
        review["response"] = api_client.post(
            "/api/student/procedure/analyze",
            headers=student_headers,
            data={"item_id": "calc_1", "api_key": api_key},
            files={"file": ("work.png", _png(), "image/png")},
        )

    worker = threading.Thread(target=analyze)
    worker.start()
    time.sleep(0.3)  # the review is now waiting on the provider
    started = time.monotonic()
    health = api_client.get("/")
    waited = time.monotonic() - started
    worker.join()

    assert health.status_code == 200
    assert review["response"].status_code == 200, review["response"].text
    assert waited < 0.5, f"another request waited {waited:.2f} s behind the review"
