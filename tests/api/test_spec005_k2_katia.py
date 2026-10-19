"""
Spec 005 delivery K2 (US1; FR-020 … FR-023): KatIA guides without the answer.

The prompt holds the item's stored statement and options, the option the student chose and their
message — never the correct answer. Every reply is checked on the server: one that names the
correct option, uses a revealing phrase or runs past 3 sentences is replaced by a fixed guiding
question and is not stored. Only a student enrolled in the item's course reaches KatIA or the
procedure review, and nothing the endpoint reads blocks the event loop.
"""

import os
import sqlite3
import threading
import time

import pytest

from tests.api.test_spec005_k1_providers import Provider

GUIDING = "¿Qué parte del enunciado te genera más dudas? ¿Qué intentaste hasta ahora?"
ITEM, COURSE = "q21", "calculo_diferencial"  # estudiante1 is enrolled in calculo_diferencial


@pytest.fixture(autouse=True)
def _fresh_limits():
    from api.rate_limit import limiter

    limiter.reset()


def _item(item_id=ITEM):
    from api.dependencies import get_repository

    return get_repository().get_item_by_id(item_id)


def _katia(api_client, headers, item_id=ITEM, message="spec005 k2 probe", **extra):
    return api_client.post(
        "/api/ai/socratic",
        headers=headers,
        json={
            "item_id": item_id,
            "item_content": "CLIENT-SENT STATEMENT",
            "student_message": message,
            "course_id": COURSE,
            "api_key": "gsk_k2_test",
            **extra,
        },
    )


def _prompt(call) -> str:
    return "\n".join(str(m.get("content")) for m in call["messages"])


def _saved(message):
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        return [
            r[0]
            for r in conn.execute(
                "SELECT k.text FROM katia_messages s JOIN katia_messages k"
                " ON k.conversation_id = s.conversation_id AND k.role = 'katia'"
                " AND k.id = (SELECT MIN(id) FROM katia_messages n"
                " WHERE n.conversation_id = s.conversation_id AND n.id > s.id)"
                " WHERE s.role = 'student' AND s.text = ?",
                (message,),
            )
        ]


# ── FR-020: the prompt ───────────────────────────────────────────────────────


def _one_item_per_block():
    """An item of each course block, and the course it belongs to."""
    from api.dependencies import get_repository

    repo = get_repository()
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        rows = conn.execute(
            "SELECT c.block, MIN(i.id), i.course_id FROM items i JOIN courses c ON c.id ="
            " i.course_id GROUP BY c.block"
        ).fetchall()
    return repo, [(block, item_id, course) for block, item_id, course in rows]


def test_the_prompt_never_holds_the_correct_answer(api_client, student_headers, monkeypatch):
    """US1-AS1, FR-020, SC-001: over an item of every course block."""
    from api.dependencies import decode_token

    repo, sample = _one_item_per_block()
    assert len(sample) >= 3
    student = int(decode_token(student_headers["Authorization"].split()[1])["sub"])
    provider = Provider(monkeypatch)
    for block, item_id, course in sample:
        repo.enroll_user(student, course, None)
        provider.calls.clear()
        response = _katia(api_client, student_headers, item_id)
        assert response.status_code == 200, (block, response.text)
        prompt = _prompt(provider.calls[0])
        item = repo.get_item_by_id(item_id)
        correct = item["correct_option"]
        # The options are in the prompt, so the correct one appears once among them: never
        # again, and nothing marks it as the answer.
        shown = item["content"].count(correct) + sum(o.count(correct) for o in item["options"])
        assert prompt.count(correct) == shown, block
        rest = prompt.replace(item["content"], "")
        for option in item["options"]:
            rest = rest.replace(option, "")
        assert "RESPUESTA CORRECTA" not in rest.upper(), block  # today's marker


def test_the_statement_comes_from_the_item_not_the_client(api_client, student_headers, monkeypatch):
    """FR-020: the stored statement and options, and the option the student chose."""
    item = _item()
    chosen = next(o for o in item["options"] if o != item["correct_option"])
    calls = Provider(monkeypatch).calls

    _katia(api_client, student_headers, selected_option=chosen)

    prompt = _prompt(calls[0])
    assert "CLIENT-SENT STATEMENT" not in prompt
    assert item["content"] in prompt and chosen in prompt
    assert "spec005 k2 probe" in prompt


# ── FR-022: every reply checked ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "reply",
    [
        "Bien pensado. Es exactamente {correct}.",
        "La respuesta es la segunda opción.",
        "Mira. Piensa. Deriva. Compara. Decide.",
    ],
    ids=["names-the-option", "revealing-phrase", "four-sentences"],
)
def test_a_reply_that_gives_the_answer_is_replaced_and_not_stored(
    api_client, student_headers, monkeypatch, reply
):
    """US1-AS2, FR-022, SC-002."""
    correct = _item()["correct_option"]
    message = f"leak probe {reply[:12]}"
    Provider(monkeypatch, reply=reply.format(correct=correct))

    response = _katia(api_client, student_headers, message=message)

    assert response.status_code == 200, response.text
    assert correct not in response.text
    assert GUIDING in response.text.encode().decode("unicode_escape", "ignore") or (
        "parte del enunciado" in response.text
    )
    assert _saved(message) == []


def test_a_guiding_reply_passes_and_is_stored(api_client, student_headers, monkeypatch):
    """FR-022: a reply that only asks questions reaches the student and is stored."""
    Provider(monkeypatch, reply="¿Qué regla usarías para derivar una potencia?")

    response = _katia(api_client, student_headers, message="guiding probe")

    assert response.status_code == 200
    assert _saved("guiding probe") == ["¿Qué regla usarías para derivar una potencia?"]


def test_katia_asks_for_at_most_120_tokens(api_client, student_headers, monkeypatch):
    """FR-022."""
    calls = Provider(monkeypatch).calls
    _katia(api_client, student_headers)
    assert calls[0]["max_tokens"] == 120


# ── FR-021: access ───────────────────────────────────────────────────────────


@pytest.mark.parametrize("who", ["not-enrolled", "teacher", "admin"])
def test_only_enrolled_students_reach_katia_or_the_review(
    api_client, student_headers, teacher_headers, admin_headers, monkeypatch, who
):
    """US1-AS3, FR-021: 403 before any provider is called."""
    import io

    from PIL import Image

    calls = Provider(monkeypatch).calls
    headers = {"not-enrolled": student_headers, "teacher": teacher_headers}.get(who, admin_headers)
    item_id = "q47" if who == "not-enrolled" else ITEM  # q47: calculo_integral, not enrolled

    katia = _katia(api_client, headers, item_id)
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    review = api_client.post(
        "/api/student/procedure/analyze",
        headers=headers,
        data={"item_id": item_id, "api_key": "gsk_k2_test"},
        files={"file": ("p.png", buffer.getvalue(), "image/png")},
    )

    assert (katia.status_code, review.status_code) == (403, 403), (katia.text, review.text)
    assert calls == []


# ── FR-023: off the event loop ───────────────────────────────────────────────


def test_katia_reads_nothing_on_the_event_loop(api_client, student_headers, monkeypatch):
    """FR-023: a slow rating read inside KatIA does not hold other requests."""
    from src.application.services.rating_read_service import RatingReadService

    original = RatingReadService.ratings_view

    def slow(self, *args, **kwargs):
        time.sleep(2.0)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(RatingReadService, "ratings_view", slow)
    Provider(monkeypatch)
    done = {}
    worker = threading.Thread(target=lambda: done.update(r=_katia(api_client, student_headers)))
    worker.start()
    time.sleep(0.3)
    started = time.monotonic()
    health = api_client.get("/")
    waited = time.monotonic() - started
    worker.join()

    assert health.status_code == 200 and done["r"].status_code == 200
    assert waited < 1.0, f"another request waited {waited:.2f} s behind KatIA"
