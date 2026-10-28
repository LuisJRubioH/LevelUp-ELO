"""
The bank's answer keys are consistent: no item offers the same answer twice, and two copies of a
question never disagree on its key. Read from items/bank/ and items/bank/semillero/, the folders
the sync loads.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BANK = ROOT / "items" / "bank"


def _items():
    for path in sorted([*BANK.glob("*.json"), *(BANK / "semillero").glob("*.json")]):
        for item in json.loads(path.read_text(encoding="utf-8")):
            yield path.name, item


def _same(text):
    """Text as the student reads it: spacing, TeX spacing commands included, does not count."""
    return re.sub(r"\s+|\\[,;:! ]", "", str(text))


def test_no_item_offers_the_same_answer_twice():
    """Two options that read the same make the item unanswerable: only one of them is the key."""
    repeated = []
    for name, item in _items():
        seen = defaultdict(list)
        for option in item["options"]:
            seen[_same(option)].append(option)
        repeated += [(name, item["id"], same) for same in seen.values() if len(same) > 1]
    assert repeated == []


def test_copies_of_a_question_share_the_key():
    """The same statement with the same options, in two courses, has one right answer."""
    copies = defaultdict(list)
    for name, item in _items():
        question = (_same(item["content"]), tuple(sorted(_same(o) for o in item["options"])))
        copies[question].append((name, item["id"], _same(item["correct_option"])))
    disagreeing = [group for group in copies.values() if len({key for *_, key in group}) > 1]
    assert disagreeing == []


# ── Spec 008 delivery T (B19): the coarse topic carries the rating ─────────────────────────────

EPA8_TOPICS = {
    "Pensamiento aleatorio",
    "Pensamiento variacional",
    "Pensamiento espacial",
    "Pensamiento métrico",
    "Pensamiento numérico",
}
DIAN_TOPICS = {
    "Constitución Política",
    "MIPG",
    "Régimen Tributario",
    "Gerencia de Proyectos (PMI)",
    "Derecho Administrativo (CPACA)",
    "Aprendizaje Continuo",
    "Orientación al Ciudadano",
    "Trabajo en Equipo",
    "Ética",
    "Comportamiento Ético",
    "PQRSF",
    "Régimen Aduanero",
    "Gestión Documental",
    "Ley de Transparencia",
    "Régimen Cambiario",
    "Compromiso / Toma de Decisiones",
    "Responsabilidad / Gestión del Tiempo",
    "Gestión del Talento Humano",
    "Sistemas de Gestión SG-SST",
}


def _bank(name):
    return {i["id"]: i for i in json.loads((BANK / name).read_text(encoding="utf-8"))}


def test_dian_and_epa8_are_regrouped():
    """FR-041, US5-AS1: EPA8 has its five «Pensamiento …» topics and P01 keeps its fine label as
    `subtopic`; DIAN's topics are the plan's table (specs/008-item-bank/plan-t.md)."""
    epa8, dian = _bank("evaluar_para_avanzar_8.json"), _bank("DIAN.json")

    assert {i["topic"] for i in epa8.values()} == EPA8_TOPICS
    p01 = epa8["EPA8-C1-2020-P01"]
    assert (p01["topic"], p01["subtopic"]) == ("Pensamiento aleatorio", "porcentaje sobre un total")
    assert {i["topic"] for i in dian.values()} == DIAN_TOPICS
    cpaca = dian["q_user_04"]
    assert cpaca["topic"] == "Derecho Administrativo (CPACA)"
    assert cpaca["subtopic"] == "CPACA - Competencia y Traslado"
    assert (dian["A4_1"]["topic"], dian["A4_1"]["subtopic"]) == ("Ética", "Código de Integridad")
    const = dian["A_Const_01"]
    assert (const["topic"], const["subtopic"]) == ("Constitución Política", "Deberes del Ciudadano")
    assert "subtopic" not in dian["A1_1"]  # no separator, no remap: unchanged


# ── Spec 008 delivery V: the real bank under D1 and D4 ────────────────────────────────────────


def test_spec008_v_every_bank_difficulty_is_an_integer_in_400_2000():
    """SC-002, FR-010: every difficulty is a JSON integer (not a bool) in 400–2000."""
    wrong = [
        (name, item["id"], item["difficulty"])
        for name, item in _items()
        if type(item["difficulty"]) is not int or not 400 <= item["difficulty"] <= 2000
    ]
    assert wrong == []


def test_spec008_v_the_committed_manifest_matches_the_bank():
    """SC-004, FR-011: every bank id is in `items/id_manifest.json` with its course (the file
    name) and topic, and every manifest id is still in the bank (O-V6)."""
    manifest = json.loads((ROOT / "items" / "id_manifest.json").read_text(encoding="utf-8"))
    bank = {item["id"]: [name.removesuffix(".json"), item["topic"]] for name, item in _items()}

    assert {i: manifest.get(i) for i in bank} == bank
    assert sorted(set(manifest) - set(bank)) == []
