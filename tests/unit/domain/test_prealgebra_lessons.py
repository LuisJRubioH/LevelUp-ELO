import json

import pytest

from src.domain.learning.nodes import NODE_MODULES
from src.domain.learning.prealgebra import (
    ALG_HUB_NODE_ID,
    ALG_N1_NODE_IDS,
    ALG_VARIABLES_NODE_ID,
    INTEGERS_NODE_ID,
    COMPLEX_NODE_ID,
    IRRATIONALS_NODE_ID,
    N2_HUB_NODE_ID,
    N2_OPERATION_NODE_IDS,
    N3_MACHINE_NODE_IDS,
    N2_RADICATION_NODE_ID,
    N2_SUBTRACTION_NODE_ID,
    N2_SUM_NODE_ID,
    N3_ASSOCIATIVE_NODE_ID,
    N3_COMMUTATIVE_NODE_ID,
    N3_HUB_NODE_ID,
    N3_IDENTITY_NODE_ID,
    N3_INVERSES_NODE_ID,
    N4_CONCEPT_NODE_IDS,
    N4_DIVISIBILITY_NODE_ID,
    N4_FACTORIZATION_NODE_ID,
    N4_GCD_NODE_ID,
    N4_HUB_NODE_ID,
    N4_LCM_NODE_ID,
    N4_MULTIPLES_NODE_ID,
    N4_PRIMES_NODE_ID,
    NATURALS_NODE_ID,
    RATIONALS_NODE_ID,
    REALS_NODE_ID,
    STAIRCASE_NODE_ID,
    TRIGGER_NODE_ID,
    WELCOME_NODE_ID,
    CLASSIFIER_BASIC_NODE_ID,
    _INTERACTION_RULES,
    _LESSONS,
    _MAP_PRESENTATION,
    curriculum_map_rows,
    evaluate_interaction,
    get_lesson,
    presentation_band,
    recommended_node_for_misconception,
    route_position,
)


def test_welcome_lesson_is_safe_and_non_evaluative():
    lesson = get_lesson(WELCOME_NODE_ID)

    assert lesson is not None
    assert lesson["node_type"] == "content_intro"
    assert lesson["is_safe_zone"] is True
    assert lesson["affects_elo"] is False


def test_lesson_catalog_returns_a_copy():
    first = get_lesson(WELCOME_NODE_ID)
    first["node_type"] = "changed"

    assert get_lesson(WELCOME_NODE_ID)["node_type"] == "content_intro"


def test_presentation_band_uses_diagnostic_cuts():
    assert presentation_band(None) == "basico"
    assert presentation_band(49.9) == "basico"
    assert presentation_band(50) == "intermedio"
    assert presentation_band(79.9) == "intermedio"
    assert presentation_band(80) == "avanzado"


def test_trigger_question_is_safe_and_uses_closed_interactions():
    lesson = get_lesson(TRIGGER_NODE_ID)

    assert lesson["unlock_after"] == WELCOME_NODE_ID
    assert lesson["affects_elo"] is False
    assert all(item["type"] == "single_select" for item in lesson["interactions"])
    assert all("free_text" not in item for item in lesson["interactions"])


def test_trigger_question_feedback_is_evaluated_in_domain():
    misconception = evaluate_interaction(TRIGGER_NODE_ID, "PREALG-N1-B02-Q01", "yes")
    intuition = evaluate_interaction(TRIGGER_NODE_ID, "PREALG-N1-B02-Q02", "bread")

    assert misconception["is_expected"] is False
    assert misconception["misconception_tag"] == "cree_que_todo_numero_sirve_para_contar"
    assert intuition["is_expected"] is None
    assert intuition["feedback_key"] == "sharing_needs_fractions"
    assert evaluate_interaction(TRIGGER_NODE_ID, "PREALG-N1-B02-Q01", "free text") is None


def test_staircase_has_five_core_steps_and_optional_complex_detour():
    lesson = get_lesson(STAIRCASE_NODE_ID)

    assert lesson["unlock_after"] == TRIGGER_NODE_ID
    assert lesson["staircase"]["core_steps"] == [
        "naturals",
        "integers",
        "rationals",
        "irrationals",
        "reals",
    ]
    assert lesson["staircase"]["optional_detour"] == "complex"
    assert lesson["affects_elo"] is False


def test_staircase_trap_catches_the_set_that_gets_replaced():
    """La misconception de B03: el conjunto nuevo NO reemplaza al anterior."""
    trap = evaluate_interaction(STAIRCASE_NODE_ID, f"{STAIRCASE_NODE_ID}-E5", "true_moved")
    ok = evaluate_interaction(STAIRCASE_NODE_ID, f"{STAIRCASE_NODE_ID}-E5", "false_both")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "conjuntos_se_reemplazan"
    assert ok["is_expected"] is True
    # El explorador de peldaños es propio de este nodo y de ningún otro.
    staircase = get_lesson(STAIRCASE_NODE_ID)["content"]["staircase"]
    assert len(staircase["steps"]) == 5
    assert [m.NODE_ID for m in NODE_MODULES if "staircase" in m.CONTENT] == [STAIRCASE_NODE_ID]


ELEVEN_BLOCK_NODES = [m.NODE_ID for m in NODE_MODULES]


@pytest.mark.parametrize("node_id", ELEVEN_BLOCK_NODES)
def test_eleven_block_node_has_the_eleven_blocks(node_id):
    """Contrato estructural de la arquitectura de 11 bloques, nodo por nodo."""
    content = get_lesson(node_id)["content"]

    assert content["kind"] == "eleven_block_node"
    for block in (
        "intro",
        "diagnostic",
        "katia",
        "discovery",
        "definition_katex",
        "worked_examples",
        "bridge",
        "method_comparison",
        "practice",
        "closure",
        "abstraction_question",
        "closing_item",
        "post_diagnostic",
        "footer",
    ):
        assert block in content, f"{node_id}: falta el bloque {block}"

    # El intento genuino nunca se califica: vive en katia, no en interactions.
    assert content["katia"]["attempt"]["format"] == "acotado"
    # Exactamente UNA autoexplicación focal en todo el nodo.
    explanations = [e for e in content["worked_examples"] if "self_explanation" in e]
    assert len(explanations) == 1
    # La última tarjeta es la trampa, con calibración y contraste.
    trap = content["worked_examples"][-1]
    assert trap["trap"] is True
    assert trap["confidence_prompt"] and trap["correct_version"] and trap["explain_prompt"]
    # Práctica: al menos un detecta_error, una trampa y una transferencia.
    tipos = {item.get("tipo") for item in content["practice"]}
    assert {"detecta_error", "trampa", "transferencia"} <= tipos
    # Cada ítem de práctica trae la escalera de tres pistas.
    for item in content["practice"]:
        assert set(item["hints"]) == {"n1", "n2", "n3"}, f"{node_id}: pistas de {item['id']}"
    # El post-diagnóstico compara contra el diagnóstico de entrada.
    assert content["post_diagnostic"]["compara_con"] == "diagnostic"


@pytest.mark.parametrize("node_id", ELEVEN_BLOCK_NODES)
def test_eleven_block_node_gates_only_practice_and_closing(node_id):
    """Diagnóstico, puente y post-diagnóstico guían pero no bloquean el nodo."""
    content = get_lesson(node_id)["content"]
    gating = {i["interaction_id"] for i in get_lesson(node_id)["interactions"]}

    expected = {f"{node_id}-{item['id']}" for item in content["practice"]}
    expected.add(f"{node_id}-{content['closing_item']['id']}")
    assert gating == expected

    non_gating = (
        [item["id"] for item in content["diagnostic"]["items"]]
        + [item["id"] for item in content["post_diagnostic"]["items"]]
        + [b["id"] for it in content["bridge"]["items"] for b in it["blanks"]]
    )
    for item_id in non_gating:
        assert f"{node_id}-{item_id}" not in gating


@pytest.mark.parametrize("node_id", ELEVEN_BLOCK_NODES)
def test_eleven_block_practice_answers_are_reachable(node_id):
    """Toda respuesta esperada se evalúa como correcta por el motor real."""
    content = get_lesson(node_id)["content"]
    items = content["practice"] + [{**content["closing_item"], "kind": "numeric"}]

    for item in items:
        if item["kind"] in ("numeric", "text_exact"):
            answer = item["answer"]
        elif item["kind"] == "multi_select":
            # El motor recibe la selección como cadena separada por comas.
            answer = ",".join(item["expected"])
        else:
            answer = item["expected"]
        result = evaluate_interaction(node_id, f"{node_id}-{item['id']}", answer)
        assert result is not None, f"{node_id}-{item['id']} no está registrado"
        assert result["is_expected"] is True, f"{node_id}-{item['id']} rechaza su propia clave"


def test_naturals_trap_catches_the_zero_that_is_not_a_number():
    """La misconception de B04: el 0 no es «nada», es el número del montón vacío."""
    trap = evaluate_interaction(NATURALS_NODE_ID, f"{NATURALS_NODE_ID}-E5", "false_nothing")
    ok = evaluate_interaction(NATURALS_NODE_ID, f"{NATURALS_NODE_ID}-E5", "true_counts")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "cero_no_es_numero"
    assert ok["is_expected"] is True
    # ℕ no es cerrado bajo resta: ese hueco es el que abre B05.
    closure = get_lesson(NATURALS_NODE_ID)["content"]["closure"]["rows"]
    assert closure[0]["closed"] == "no"


def test_integers_trap_catches_magnitude_without_sign():
    """La misconception de B05: −8 > −3 porque 8 > 3."""
    trap = evaluate_interaction(INTEGERS_NODE_ID, f"{INTEGERS_NODE_ID}-E5", "true_size")
    ok = evaluate_interaction(INTEGERS_NODE_ID, f"{INTEGERS_NODE_ID}-E5", "false_left")
    transfer = evaluate_interaction(INTEGERS_NODE_ID, f"{INTEGERS_NODE_ID}-E6", "second_bigger")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "magnitud_sin_signo"
    assert ok["is_expected"] is True
    # La misma misconception reaparece en el ítem de transferencia.
    assert transfer["misconception_tag"] == "magnitud_sin_signo"


def test_rationals_trap_catches_the_truncated_decimal():
    """La misconception del nodo: el decimal cortado NO es el número."""
    trap = evaluate_interaction(RATIONALS_NODE_ID, f"{RATIONALS_NODE_ID}-E5", "true_same")
    ok = evaluate_interaction(RATIONALS_NODE_ID, f"{RATIONALS_NODE_ID}-E5", "false_cut")
    transfer = evaluate_interaction(RATIONALS_NODE_ID, f"{RATIONALS_NODE_ID}-E6", "exact")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "decimal_truncado_es_el_numero"
    assert ok["is_expected"] is True
    # La misma misconception reaparece en el ítem de transferencia.
    assert transfer["misconception_tag"] == "decimal_truncado_es_el_numero"


def test_irrationals_trap_catches_the_infinite_decimal():
    """La misconception de B07: un decimal infinito PERIÓDICO sigue siendo racional."""
    lesson = get_lesson(IRRATIONALS_NODE_ID)
    assert lesson["unlock_after"] == RATIONALS_NODE_ID
    assert lesson["affects_elo"] is False

    trap = evaluate_interaction(IRRATIONALS_NODE_ID, f"{IRRATIONALS_NODE_ID}-E5", "true_rule")
    ok = evaluate_interaction(IRRATIONALS_NODE_ID, f"{IRRATIONALS_NODE_ID}-E5", "false_periodic")
    periodic = evaluate_interaction(IRRATIONALS_NODE_ID, f"{IRRATIONALS_NODE_ID}-E3", "periodic")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "decimal_infinito_es_irracional"
    assert ok["is_expected"] is True
    # La misma misconception reaparece al clasificar 0,8181…
    assert periodic["misconception_tag"] == "decimal_infinito_es_irracional"
    # Y la simétrica: no toda raíz es irracional.
    root = evaluate_interaction(IRRATIONALS_NODE_ID, f"{IRRATIONALS_NODE_ID}-E7", "sqrt2")
    assert root["misconception_tag"] == "toda_raiz_es_irracional"


def test_reals_trap_catches_the_next_number():
    """La misconception de B08: en ℝ ningún número tiene siguiente."""
    lesson = get_lesson(REALS_NODE_ID)
    assert lesson["unlock_after"] == IRRATIONALS_NODE_ID
    assert lesson["nucleus_closing_node"] is True
    assert lesson["affects_elo"] is False

    trap = evaluate_interaction(REALS_NODE_ID, f"{REALS_NODE_ID}-E5", "ninety_one")
    ok = evaluate_interaction(REALS_NODE_ID, f"{REALS_NODE_ID}-E5", "none")
    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "existe_el_siguiente"
    assert ok["is_expected"] is True

    # El diagnóstico de entrada pregunta lo mismo en ℤ, donde SÍ hay siguiente:
    # el post-diagnóstico lo repite en ℝ, donde la respuesta se invierte.
    content = get_lesson(REALS_NODE_ID)["content"]
    assert content["diagnostic"]["items"][0]["expected"] == "eight"
    assert content["post_diagnostic"]["items"][0]["expected"] == "none"
    # opción inválida → None (nunca acepta texto/llaves desconocidas).
    assert evaluate_interaction(REALS_NODE_ID, f"{REALS_NODE_ID}-E5", "free text") is None


def test_complex_trap_catches_the_always_positive_square():
    """La misconception de B09: «todo cuadrado es positivo» solo vale dentro de ℝ."""
    trap = evaluate_interaction(COMPLEX_NODE_ID, f"{COMPLEX_NODE_ID}-E5", "one")
    ok = evaluate_interaction(COMPLEX_NODE_ID, f"{COMPLEX_NODE_ID}-E5", "minus_one")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "cuadrado_siempre_positivo"
    assert ok["is_expected"] is True
    # ℂ es el desvío: no cuelga de la escalera, así que no declara `scene`.
    content = get_lesson(COMPLEX_NODE_ID)["content"]
    assert "scene" not in content
    # Y su escalera de cierre termina cerrada en ℂ.
    assert content["closure"]["rows"][-1]["closed"] == "yes"


def test_level_two_hub_unlocks_after_level_one_closing_and_is_non_elo():
    lesson = get_lesson(N2_HUB_NODE_ID)

    assert lesson["unlock_after"] == "PREALG-N1-B13-CIERRE-DIAGNOSTICO"
    assert lesson["affects_elo"] is False
    assert lesson["is_safe_zone"] is True
    assert lesson["content"]["gating"]["cards_required"] == 6
    assert len(lesson["interactions"]) == 6


def test_level_two_buildings_have_distinct_names_and_misconceptions():
    """Cada operación vive en su propio edificio con su propio error focal.

    Sin esto, N2 vuelve a ser seis variaciones del mismo nodo.
    """
    contents = [get_lesson(node_id)["content"] for node_id in N2_OPERATION_NODE_IDS]
    buildings = [c["building"] for c in contents]
    misconceptions = [c["misconception"] for c in contents]

    assert len(set(buildings)) == 6, buildings
    assert len(set(misconceptions)) == 6, misconceptions
    # El edificio se nombra en la tarjeta del hub y en el nodo: mismo nombre.
    hub_buildings = [b["building"] for b in get_lesson(N2_HUB_NODE_ID)["content"]["buildings"]]
    assert hub_buildings == buildings


def test_level_two_closure_always_carries_the_six_sets():
    for node_id in N2_OPERATION_NODE_IDS:
        rows = get_lesson(node_id)["content"]["closure"]["rows"]
        assert [row["name"] for row in rows] == [
            "Naturales",
            "Enteros",
            "Racionales",
            "Irracionales",
            "Reales",
            "Complejos",
        ], node_id


def test_level_two_accepts_decimal_comma():
    result = evaluate_interaction(N2_SUM_NODE_ID, f"{N2_SUM_NODE_ID}-E3", "0.75")

    assert result["selected_option"] == "0,75"
    assert result["is_expected"] is True


def test_level_two_radication_trap_is_the_split_over_a_sum():
    trap = evaluate_interaction(N2_RADICATION_NODE_ID, f"{N2_RADICATION_NODE_ID}-E5", "true")
    ok = evaluate_interaction(N2_RADICATION_NODE_ID, f"{N2_RADICATION_NODE_ID}-E5", "false_sum")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "raiz_de_suma_es_suma_de_raices"
    assert ok["is_expected"] is True


def test_level_three_hub_and_machines_follow_storytelling_contract():
    hub = get_lesson(N3_HUB_NODE_ID)
    conmutative = get_lesson(N3_COMMUTATIVE_NODE_ID)
    identity = get_lesson(N3_IDENTITY_NODE_ID)

    assert hub["unlock_after"] == N2_RADICATION_NODE_ID
    assert hub["content"]["gating"]["machines_required"] == 5
    assert len(hub["interactions"]) == 5
    assert conmutative["unlock_after"] == N3_HUB_NODE_ID
    assert conmutative["content"]["misconception"] == "todas_las_operaciones_son_conmutativas"
    assert identity["content"]["misconception"] == "neutro_es_el_mismo_para_toda_operacion"


def test_level_three_stations_have_distinct_names_and_misconceptions():
    """Cada propiedad vive en su estación con su propio error focal.

    Sin esto, N3 vuelve a ser cinco variaciones del mismo nodo — que es lo que
    pasó con la versión anterior del nivel.
    """
    contents = [get_lesson(node_id)["content"] for node_id in N3_MACHINE_NODE_IDS]
    stations = [c["station"] for c in contents]
    misconceptions = [c["misconception"] for c in contents]

    assert len(set(stations)) == 5, stations
    assert len(set(misconceptions)) == 5, misconceptions
    hub_stations = [
        m["station"].split(" · ")[0] for m in get_lesson(N3_HUB_NODE_ID)["content"]["machines"]
    ]
    assert hub_stations == stations


def test_level_three_closure_is_by_operation_except_inverses():
    """V2-R13: escalera MIXTA — por operación salvo en M05, que va por conjunto."""
    for node_id in N3_MACHINE_NODE_IDS:
        rows = get_lesson(node_id)["content"]["closure"]["rows"]
        names = [row["name"] for row in rows]
        if node_id == N3_INVERSES_NODE_ID:
            assert names == [
                "Naturales",
                "Enteros",
                "Racionales",
                "Irracionales",
                "Reales",
                "Complejos",
            ]
        else:
            assert "Naturales" not in names, (node_id, names)


def test_level_three_accepts_decimal_comma():
    decimal = evaluate_interaction(
        N3_INVERSES_NODE_ID,
        f"{N3_INVERSES_NODE_ID}-E2",
        "0.125",
    )

    assert decimal["selected_option"] == "0,125"
    assert decimal["is_expected"] is True


def test_n3_chains_into_n4_hub():
    inverses = get_lesson(N3_INVERSES_NODE_ID)
    hub = get_lesson(N4_HUB_NODE_ID)

    assert inverses["next_node_id"] == N4_HUB_NODE_ID
    assert hub["unlock_after"] == N3_INVERSES_NODE_ID
    assert hub["content"]["gating"]["cards_required"] == 6
    assert len(hub["content"]["cards"]) == 6
    assert hub["content"]["cards"][0]["node_id"] == N4_DIVISIBILITY_NODE_ID


def test_n4_lesson_content_is_json_serializable():
    # Regresion: los items multi_select se autoraban como sets (no serializables
    # en JSON) al vivir dentro de `content`, que sí viaja al frontend.
    for node_id in (N4_HUB_NODE_ID, *N4_CONCEPT_NODE_IDS):
        lesson = get_lesson(node_id)
        json.dumps(lesson["content"])


@pytest.mark.parametrize("node_id", N4_CONCEPT_NODE_IDS)
def test_n4_nodes_mix_interaction_types(node_id):
    """V2-R14: cada destino mezcla numeric / single_select / multi_select."""
    kinds = {item["kind"] for item in get_lesson(node_id)["content"]["practice"]}

    assert "numeric" in kinds, (node_id, kinds)
    assert "single_select" in kinds, (node_id, kinds)
    assert "multi_select" in kinds, (node_id, kinds)


def test_n4_destinations_have_distinct_names_and_misconceptions():
    contents = [get_lesson(node_id)["content"] for node_id in N4_CONCEPT_NODE_IDS]
    destinations = [c["destination"] for c in contents]
    misconceptions = [c["misconception"] for c in contents]

    assert len(set(destinations)) == 6, destinations
    assert len(set(misconceptions)) == 6, misconceptions
    hub_destinations = [c["destination"] for c in get_lesson(N4_HUB_NODE_ID)["content"]["cards"]]
    assert hub_destinations == destinations


def test_n4_multi_select_options_are_lists_not_sets():
    """V2-R14 (b): `content` viaja a JSON, así que un set no serializa."""
    for node_id in N4_CONCEPT_NODE_IDS:
        for item in get_lesson(node_id)["content"]["practice"]:
            if item["kind"] != "multi_select":
                continue
            for key in ("valid_options", "expected", "trap_options"):
                assert isinstance(item.get(key, []), list), (node_id, item["id"], key)


def test_n4_lcm_trap_is_the_product():
    node = N4_LCM_NODE_ID
    trap = evaluate_interaction(node, f"{node}-E5", "true")
    ok = evaluate_interaction(node, f"{node}-E5", "false_coprime")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "mcm_es_el_producto_de_los_numeros"
    assert ok["is_expected"] is True


def test_n4_sequence_unlocks_sequentially():
    lessons = [get_lesson(node_id) for node_id in N4_CONCEPT_NODE_IDS]
    assert lessons[0]["unlock_after"] == N4_HUB_NODE_ID
    for previous, current in zip(lessons, lessons[1:]):
        assert current["unlock_after"] == previous["node_id"]
    assert lessons[-1]["node_id"] == N4_LCM_NODE_ID
    # El MCM ya no cierra la ruta: entrega el paso al módulo de Álgebra.
    assert lessons[-1]["next_node_id"] == ALG_HUB_NODE_ID


# ── ALG-N1 · El Papiro de las Cuatro Casas ───────────────────────────────────


def test_algebra_module_lands_on_a_hub_after_prealgebra():
    """Álgebra es mundo narrativo nuevo, pero continuación técnica de la ruta.

    Se entra por el hub, que presenta las cuatro casas; el primer nodo cuelga de él.
    """
    hub = get_lesson(ALG_HUB_NODE_ID)
    assert hub["unlock_after"] == N4_LCM_NODE_ID
    assert hub["content"]["kind"] == "level_hub_cards"
    assert len(hub["content"]["cards"]) == 4
    # Cada tarjeta abre una casa que existe.
    for card in hub["content"]["cards"]:
        assert get_lesson(card["node_id"]) is not None, card["node_id"]

    primero = get_lesson(ALG_VARIABLES_NODE_ID)
    assert primero["unlock_after"] == ALG_HUB_NODE_ID
    assert primero["content"]["kind"] == "eleven_block_node"


def test_algebra_nodes_declare_house_and_guide():
    """Cada sala de Kemet tiene nombre propio; el hub no es una lección."""
    houses, guides = set(), set()
    for node_id in [n for n in ALG_N1_NODE_IDS if n != ALG_HUB_NODE_ID]:
        content = get_lesson(node_id)["content"]
        assert content["house"], f"{node_id}: sin casa"
        assert content["guide"], f"{node_id}: sin personaje guía"
        houses.add(content["house"])
        guides.add(content["guide"])
    assert len(houses) == len(ALG_N1_NODE_IDS) - 1  # el hub no declara sala


def test_every_focal_misconception_is_distinct():
    """Escribir muchos nodos seguidos tiende a repetir el mismo error focal."""
    tags = [get_lesson(module.NODE_ID)["content"]["misconception"] for module in NODE_MODULES]
    assert len(set(tags)) == len(tags), "hay un misconception focal repetido"


def test_algebra_l01_trap_reads_the_letter_as_a_label():
    node = ALG_VARIABLES_NODE_ID
    trap = evaluate_interaction(node, f"{node}-E5", "label")
    ok = evaluate_interaction(node, f"{node}-E5", "count")

    assert trap["is_expected"] is False
    assert trap["misconception_tag"] == "variable_como_etiqueta"
    assert ok["is_expected"] is True


# ── Respuestas tecleadas (`text_exact`) ──────────────────────────────────────


@pytest.mark.parametrize(
    "typed,expected",
    [
        ("6r+3", True),  # la clave tal cual
        ("6r + 3", True),  # los espacios dan igual
        ("3+6r", True),  # forma equivalente declarada en `accepted`
        ("7r", False),  # combinó lo que no era semejante
        ("6r", False),  # perdió la constante
        ("2(r+1)", None),  # con paréntesis no se evalúa: el motor lo rechaza
        ("'; drop table users", None),
    ],
)
def test_typed_answers_are_validated_before_being_compared(typed, expected):
    """El campo de texto es entrada de usuario: lista blanca, no parser."""
    node = "ALG-N1-O01-SEMEJANTES"
    result = evaluate_interaction(node, f"{node}-E3", typed)

    if expected is None:
        assert result is None
    else:
        assert result["is_expected"] is expected


# ── Ruta de repaso (C4) ──────────────────────────────────────────────────────


def test_every_focal_misconception_routes_to_its_own_node():
    """El nodo que enseña un error es el que se recomienda para repasarlo."""
    for module in NODE_MODULES:
        tag = module.CONTENT.get("misconception")
        if not tag:
            continue
        assert recommended_node_for_misconception(tag) == module.NODE_ID, tag


def test_no_misconception_the_engine_can_emit_is_left_without_a_route():
    """Un distractor sin ruta deja al estudiante sin recomendación de repaso."""
    tags = set()
    for rule in _INTERACTION_RULES.values():
        tags.update(t for t in (rule.get("misconception_by_option") or {}).values() if t)
        if rule.get("default_misconception"):
            tags.add(rule["default_misconception"])

    huerfanos = sorted(t for t in tags if recommended_node_for_misconception(t) is None)
    assert not huerfanos, f"{len(huerfanos)} tags sin ruta: {huerfanos[:5]}"


def test_review_order_survives_nodes_outside_the_first_level():
    """`route_position` ordena cualquier nodo; la lista de N1 no es índice global."""
    orden = [route_position(n) for n in (NATURALS_NODE_ID, N4_LCM_NODE_ID, ALG_HUB_NODE_ID)]
    assert orden == sorted(orden)
    assert route_position("NODO-QUE-NO-EXISTE") >= max(orden)


# ── Mapa derivado de la ruta (B4) ────────────────────────────────────────────


def test_every_lesson_has_a_row_in_the_map_presentation():
    """Un nodo sin fila desaparece del mapa; que falle aquí y no en producción."""
    faltan = [node_id for node_id in _LESSONS if node_id not in _MAP_PRESENTATION]
    sobran = [node_id for node_id in _MAP_PRESENTATION if node_id not in _LESSONS]
    assert not faltan, f"sin etiqueta de mapa: {faltan}"
    assert not sobran, f"etiqueta de un nodo que ya no existe: {sobran}"


def test_map_states_come_from_unlock_after():
    """Sin progreso: se abre el primero y todo lo demás queda bloqueado."""
    rows = curriculum_map_rows(lambda _node_id: "not_started")
    assert [r["node_id"] for r in rows] == list(_LESSONS)
    assert rows[0]["state"] == "current"
    assert all(r["state"] == "blocked" for r in rows[1:])


def test_completing_a_node_opens_exactly_the_next_one():
    completados = {WELCOME_NODE_ID}
    rows = curriculum_map_rows(lambda n: "completed" if n in completados else "not_started")
    por_id = {r["node_id"]: r["state"] for r in rows}
    assert por_id[WELCOME_NODE_ID] == "completed"
    assert por_id[TRIGGER_NODE_ID] == "current"
    assert por_id[STAIRCASE_NODE_ID] == "blocked"


def test_the_optional_complex_detour_is_never_the_next_step():
    """B09 y B10 se abren a la vez tras los Reales; el siguiente paso es B10."""
    hasta_reales = set(list(_LESSONS)[: list(_LESSONS).index(REALS_NODE_ID) + 1])
    rows = curriculum_map_rows(lambda n: "completed" if n in hasta_reales else "not_started")
    por_id = {r["node_id"]: r["state"] for r in rows}
    assert por_id[COMPLEX_NODE_ID] == "available"
    assert por_id[CLASSIFIER_BASIC_NODE_ID] == "current"

    banda_basica = curriculum_map_rows(
        lambda n: "completed" if n in hasta_reales else "not_started",
        complex_visible=False,
    )
    assert COMPLEX_NODE_ID not in {r["node_id"] for r in banda_basica}


def test_every_definition_symbol_carries_its_spoken_reading():
    """`reads` es lo que un lector de pantalla vocaliza en vez del MathML.

    El renderer lo pasa como `aria-label` de la fórmula (con `role="img"`, sin el
    cual el navegador lo ignora). Un símbolo sin `reads` se lee deletreado.
    """
    sin_lectura = [
        (modulo.NODE_ID, simbolo.get("symbol"))
        for modulo in NODE_MODULES
        for simbolo in modulo.CONTENT.get("definition_symbols") or []
        if not simbolo.get("reads") or not simbolo.get("means")
    ]
    assert sin_lectura == []


def test_no_two_nodes_share_a_room_name():
    """Cada nodo de escenario tiene su sala, y ninguna se repite.

    El mapa de Álgebra 8 proponía «patio de los mosaicos» para productos
    notables sin ver que E03 ya era «El Taller de Mosaicos». Un choque así
    rompe la regla de vocabulario sin cruces y no lo detectaba ningún test:
    el de ALG-N1 solo miraba sus propios nodos.
    """
    nombres = [
        modulo.CONTENT[clave].lower()
        for modulo in NODE_MODULES
        for clave in ("house", "building", "station", "destination")
        if modulo.CONTENT.get(clave)
    ]
    repetidos = {n for n in nombres if nombres.count(n) > 1}
    assert repetidos == set()


def test_a_content_error_seen_in_many_nodes_has_a_node_that_teaches_it():
    """Un error que aparece en varios nodos necesita saber a cuál se repasa.

    Dos clases distintas de tag:

    - **Error de contenido** — tiene dueño: el nodo que enseña el concepto. Si
      lo emiten tres o más nodos y ninguno lo declara focal, la ruta de repaso
      cae en «el primero de la ruta que pueda emitirlo», que acierta por
      accidente y deja de acertar en cuanto se reordena algo.
    - **Hábito de proceso** (`habito_*`) — no verificar, no decidir, no
      simplificar. No tiene dueño y no debe tenerlo: no hay ningún nodo que
      enseñe «verificar». Se marcan con prefijo para quedar fuera de la regla.
    """
    focales = {m.CONTENT["misconception"] for m in NODE_MODULES if m.CONTENT.get("misconception")}
    emisores: dict[str, set[str]] = {}
    for regla in _INTERACTION_RULES.values():
        tags = list((regla.get("misconception_by_option") or {}).values())
        if regla.get("default_misconception"):
            tags.append(regla["default_misconception"])
        for tag in tags:
            emisores.setdefault(tag, set()).add(regla["node_id"])

    huerfanos = sorted(
        tag
        for tag, nodos in emisores.items()
        if len(nodos) > 2 and tag not in focales and not tag.startswith("habito_")
    )
    # Los de abajo son deuda conocida: errores de contenido de Preálgebra que
    # ningún nodo declara focal todavía. No deben crecer.
    conocidos = {
        "cree_que_todo_decimal_infinito_es_irracional",
        "invierte_cociente",
        "irracional_no_existe",
        "negativo_no_es_real",
        "no_busca_el_minimo",
        "olvida_el_caso_de_igualdad",
        "representacion_define_el_numero",
        "toda_raiz_es_irracional",
        "confunde_la_operacion_dictada",
    }
    assert (
        set(huerfanos) <= conocidos
    ), f"tags de contenido nuevos sin nodo dueño: {set(huerfanos) - conocidos}"
