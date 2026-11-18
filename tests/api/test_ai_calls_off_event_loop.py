"""
A procedure review waits seconds (up to minutes, with the SDK's own retries) on an AI provider.
The API is one process (AGENTS R18): while that wait runs on the event loop, every other request
and every PvP socket waits too. R17: blocking work in an `async def` goes through a thread. With
a provider that takes 3 s, the API must keep answering other requests meanwhile.

The margin is wide on purpose: a request blocked behind the review would wait about 2.7 s, a
free one answers in milliseconds, and a shared CI runner can pause a thread for most of a second
(a 1.5 s provider with a 0.5 s limit failed once that way, 2026-10-19).
"""

import io
import threading
import time

import pytest

SLOW = 3.0


def _png() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


def _slow_groq_review(*_args, **_kwargs):
    time.sleep(SLOW)
    return {"score_procedimiento": 70, "evaluacion_global": "bien"}


def _slow_katia(*_args, **_kwargs):
    time.sleep(SLOW)
    return "¿Qué observas?"


def _review_request(api_client, headers):
    return api_client.post(
        "/api/student/procedure/analyze",
        headers=headers,
        data={"item_id": "calc_1", "api_key": "gsk_fake_test_key"},
        files={"file": ("work.png", _png(), "image/png")},
    )


def _katia_request(api_client, headers):
    return api_client.post(
        "/api/ai/socratic",
        headers=headers,
        json={
            "item_id": "q21",
            "item_content": "x",
            "student_message": "off-loop probe",
            "course_id": "calculo_diferencial",
            "api_key": "gsk_fake_test_key",
        },
    )


# Spec 005 K1 removed the generic vision review (Groq only, FR-014); KatIA's provider call now
# runs before its stream starts, so it is checked here too (FR-023).
@pytest.mark.parametrize(
    "target, fake, send",
    [
        ("math_procedure_review.review_math_procedure", _slow_groq_review, _review_request),
        ("ai_client.get_socratic_guidance", _slow_katia, _katia_request),
    ],
    ids=["groq-review", "katia"],
)
def test_the_api_answers_while_a_procedure_is_reviewed(
    api_client, student_headers, monkeypatch, target, fake, send
):
    from api.rate_limit import limiter

    module, name = target.split(".")
    monkeypatch.setattr(f"src.infrastructure.external_api.{module}.{name}", fake)
    limiter.reset()

    review = {}

    def analyze():
        review["response"] = send(api_client, student_headers)

    worker = threading.Thread(target=analyze)
    worker.start()
    time.sleep(0.3)  # the review is now waiting on the provider
    started = time.monotonic()
    health = api_client.get("/")
    waited = time.monotonic() - started
    worker.join()

    assert health.status_code == 200
    assert review["response"].status_code == 200, review["response"].text
    assert waited < 1.0, f"another request waited {waited:.2f} s behind the review"


@pytest.mark.parametrize(
    "send",
    [_review_request, _katia_request],
    ids=["procedure", "katia"],
)
def test_provider_setup_does_not_block_the_event_loop(
    api_client, student_headers, monkeypatch, send
):
    """FR-023 / R17: other requests finish while provider setup is still blocked.

    A fresh provider import may read the SSL trust store. Hold setup explicitly rather than
    relying on that machine-dependent import time to expose an event-loop stall.
    """
    import builtins

    from api.rate_limit import limiter

    original_import = builtins.__import__
    setup_started = threading.Event()
    release_setup = threading.Event()
    health_done = threading.Event()
    responses = {}
    errors = []

    def blocked_ai_import(name, *args, **kwargs):
        if name == "src.infrastructure.external_api.ai_client":
            setup_started.set()
            assert release_setup.wait(10), "provider setup was not released"
        return original_import(name, *args, **kwargs)

    def request(name, call):
        try:
            responses[name] = call()
        except Exception as exc:
            errors.append(exc)
        finally:
            if name == "health":
                health_done.set()

    monkeypatch.setattr(
        "src.infrastructure.external_api.math_procedure_review.review_math_procedure",
        lambda *_args, **_kwargs: {"score_procedimiento": 70, "evaluacion_global": "bien"},
    )
    monkeypatch.setattr(
        "src.infrastructure.external_api.ai_client.get_socratic_guidance",
        lambda *_args, **_kwargs: "¿Qué observas?",
    )
    # Intercept even cached imports: the test must not depend on certificate-loading speed.
    monkeypatch.setattr(builtins, "__import__", blocked_ai_import)
    limiter.reset()
    review = threading.Thread(
        target=request, args=("review", lambda: send(api_client, student_headers))
    )
    health = threading.Thread(target=request, args=("health", lambda: api_client.get("/")))
    review.start()
    try:
        assert setup_started.wait(5), "the request did not reach provider setup"
        health.start()
        assert health_done.wait(1), "health request stalled behind provider setup"
        assert "review" not in responses, "setup must remain blocked during the health check"
    finally:
        release_setup.set()
        review.join(timeout=10)
        if health.ident is not None:
            health.join(timeout=10)

    assert not review.is_alive() and not health.is_alive()
    if errors:
        raise errors[0]
    assert responses["health"].status_code == 200
    assert responses["review"].status_code == 200
