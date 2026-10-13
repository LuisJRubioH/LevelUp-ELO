"""
The model-evaluation harness's arithmetic with a fake tutor (spec 005 § Model evaluation).

These tests never call a model: they check sampling, scoring, cost and the report, so a real run
(owner's step, with keys) measures what it claims to measure.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import evaluate_katia_models as ev  # noqa: E402

from src.application.interfaces.tutor import TutorCompletion, TutorUnavailable  # noqa: E402

ITEM = {
    "id": "q1",
    "course_id": "algebra",
    "topic": "Ecuaciones",
    "difficulty": 950,
    "content": "Si $3x - 5 = 16$, ¿cuánto vale $x$?",
    "options": ["7", "-7", "11/3", "21"],
    "correct_option": "7",
}


class ScriptedTutor:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.systems = []
        self.messages = []

    def complete(self, system, messages):
        self.systems.append(system)
        self.messages.append(messages)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def test_the_sample_is_deterministic_and_spread_over_courses_and_bands():
    items = [
        {
            "id": f"{c}{d}{i}",
            "course_id": c,
            "difficulty": d,
            "options": ["a"],
            "correct_option": "a",
        }
        for c in ("a", "b")
        for d in (700, 1000, 1500)
        for i in range(5)
    ]

    first = ev.sample_items(items, 6, seed=3)

    assert first == ev.sample_items(items, 6, seed=3)
    assert {(i["course_id"], ev.difficulty_band(i["difficulty"])) for i in first} == {
        (c, b) for c in ("a", "b") for b in ("low", "mid", "high")
    }
    assert len(ev.sample_items(items, 100, seed=3)) == len(items)


def test_the_bank_loads_with_its_courses():
    items = ev.load_bank()
    assert len(items) > 1000
    assert all(i["correct_option"] in i["options"] for i in items[:200])


def test_a_conversation_uses_production_checks_and_keeps_only_accepted_turns():
    tutor = ScriptedTutor(
        TutorCompletion(
            "¿Qué operación deshace la resta de 5?", input_tokens=300, output_tokens=20
        ),
        TutorCompletion("¡Correcto! Es 7.", input_tokens=320, output_tokens=8),
        TutorCompletion(
            "¿Qué queda a cada lado si", truncated=True, input_tokens=330, output_tokens=120
        ),
    )
    scenario = ("varios_turnos", False, ["¿Por dónde empiezo?", "¿Es 7?", "¿Y luego?"])

    replies = ev.run_conversation(tutor, "groq:m", ITEM, scenario, "es")

    assert [r.reasons for r in replies][0] == []
    assert "verdict" in replies[1].reasons and "answer_text" in replies[1].reasons
    assert replies[2].truncated and replies[2].reasons == ["empty"]
    assert len(tutor.messages[2]) == 3  # the rejected turn never became history
    assert all("REFERENCIA INTERNA" not in s for s in tutor.systems)


def test_an_answered_scenario_gives_the_key_as_a_reference_and_failures_are_counted():
    tutor = ScriptedTutor(TutorUnavailable("timeout"))

    replies = ev.run_conversation(tutor, "groq:m", ITEM, ("despues", True, ["¿Por qué?"]), "en")

    assert "INTERNAL REFERENCE" in tutor.systems[0]
    assert replies[0].failed == "timeout"


@pytest.mark.parametrize(
    "output, chosen",
    [("7", "7"), ("$7$", "7"), ("La opción correcta es 11/3.", "11/3"), ("No sé", None)],
)
def test_the_solvers_choice_is_matched_to_an_option(output, chosen):
    assert ev.match_option(output, ITEM["options"]) == chosen


def test_the_summary_counts_rates_latency_and_cost():
    replies = [
        ev.Reply("m", "q1", "inicio", "es", "x", "ok", [], False, "", 1.0, 1000, 100),
        ev.Reply("m", "q1", "inicio", "en", "x", "bad", ["verdict"], False, "", 3.0, 3000, 100),
        ev.Reply("m", "q1", "inicio", "es", "x", failed="timeout"),
    ]
    solved = [{"item_id": "q1", "correct": True}, {"item_id": "q2", "correct": False}]

    summary = ev.summarize("m", replies, solved, (0.5, 1.0))

    assert (summary["replies"], summary["failed"], summary["rejected"]) == (3, 1, 1)
    assert summary["rejection_rate"] == 0.5
    assert summary["reasons"] == {"verdict": 1}
    assert summary["by_scenario"] == {"inicio (es)": [0, 1], "inicio (en)": [1, 1]}
    assert (summary["latency_p50"], summary["latency_p95"]) == (1.0, 3.0)  # nearest rank
    # mean 2000 in, 100 out → 1000 × (2000 × 0.5 + 100 × 1.0) / 1e6
    assert summary["cost_per_1000"] == pytest.approx(1.1)
    assert (summary["solver_correct"], summary["solver_total"]) == (1, 2)
    assert [r["text"] for r in summary["sample"]] == ["ok"]


def test_the_report_names_models_prices_and_the_review_sample():
    replies = [
        ev.Reply("groq:a", "q1", "inicio", "es", "x", "¿Qué ves?", [], False, "", 0.5, 10, 5)
    ]
    summary = ev.summarize("groq:a", replies, [{"item_id": "q1", "correct": True}], (0.05, 0.08))

    report = ev.render_markdown([summary], {"date": "2026-10-13", "items": 1, "seed": 7})

    assert "| groq:a | 1/1 |" in report
    assert "0.05 / 0.08 USD per million" in report
    assert "human review" in report and "¿Qué ves?" in report


def test_prices_parse_and_a_missing_key_stops_before_any_call(monkeypatch):
    assert ev.parse_price(["groq:a=0.05/0.08"]) == {"groq:a": (0.05, 0.08)}
    for name in list(ev.KEY_ENV.values()) + ["SYSTEM_AI_API_KEY"]:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(SystemExit, match="No key for groq"):
        ev.make_tutors("groq:llama-3.1-8b-instant", 120)
