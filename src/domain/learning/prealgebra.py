"""Catálogo curricular puro para Preálgebra, Nivel 1: conjuntos numéricos.

El contenido visible vive en i18n. Este módulo conserva la identidad, el orden,
las reglas de presentación y los invariantes que no dependen de la interfaz.
"""

import re
from copy import deepcopy

from .nodes import NODE_MODULES
from .nodes import a00_hub, s00_hub_bagdad

PREALGEBRA_COURSE_ID = "algebra_basica"
WELCOME_NODE_ID = "PREALG-N1-B01-BIENVENIDA"
TRIGGER_NODE_ID = "PREALG-N1-B02-PREGUNTA-DETONADORA"
STAIRCASE_NODE_ID = "PREALG-N1-B03-ESCALERA-NECESIDAD"
NATURALS_NODE_ID = "PREALG-N1-B04-NATURALES-CONTAR"
INTEGERS_NODE_ID = "PREALG-N1-B05-ENTEROS-DEUDA"
RATIONALS_NODE_ID = "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION"
IRRATIONALS_NODE_ID = "PREALG-N1-B07-IRRACIONALES-DECIMALES"
REALS_NODE_ID = "PREALG-N1-B08-REALES-RECTA"
COMPLEX_NODE_ID = "PREALG-N1-B09-COMPLEJOS-PLANO"
CLASSIFIER_BASIC_NODE_ID = "PREALG-N1-B10-CLASIFICADOR-BASICO"
CLASSIFIER_RIGOROUS_NODE_ID = "PREALG-N1-B11-CLASIFICADOR-RIGUROSO"
DETECTIVE_NODE_ID = "PREALG-N1-B12-DETECTIVE-FALSEDADES"
CLOSING_NODE_ID = "PREALG-N1-B13-CIERRE-DIAGNOSTICO"

N2_HUB_NODE_ID = "PREALG-N2-E00-CIUDAD"
N2_SUM_NODE_ID = "PREALG-N2-E01-SUMA-JUNTAR"
N2_SUBTRACTION_NODE_ID = "PREALG-N2-E02-RESTA-QUITAR"
N2_MULTIPLICATION_NODE_ID = "PREALG-N2-E03-MULTIPLICACION-AGRUPAR"
N2_DIVISION_NODE_ID = "PREALG-N2-E04-DIVISION-REPARTIR"
N2_EXPONENTIATION_NODE_ID = "PREALG-N2-E05-POTENCIACION-CRECER"
N2_RADICATION_NODE_ID = "PREALG-N2-E06-RADICACION-RAIZ"

N3_HUB_NODE_ID = "PREALG-N3-M00-LABORATORIO"
N3_COMMUTATIVE_NODE_ID = "PREALG-N3-M01-CONMUTATIVA"
N3_ASSOCIATIVE_NODE_ID = "PREALG-N3-M02-ASOCIATIVA"
N3_DISTRIBUTIVE_NODE_ID = "PREALG-N3-M03-DISTRIBUTIVA"
N3_IDENTITY_NODE_ID = "PREALG-N3-M04-ELEMENTO-NEUTRO"
N3_INVERSES_NODE_ID = "PREALG-N3-M05-INVERSOS"

N2_OPERATION_NODE_IDS = [
    N2_SUM_NODE_ID,
    N2_SUBTRACTION_NODE_ID,
    N2_MULTIPLICATION_NODE_ID,
    N2_DIVISION_NODE_ID,
    N2_EXPONENTIATION_NODE_ID,
    N2_RADICATION_NODE_ID,
]
N2_NODE_IDS = [N2_HUB_NODE_ID, *N2_OPERATION_NODE_IDS]

N3_MACHINE_NODE_IDS = [
    N3_COMMUTATIVE_NODE_ID,
    N3_ASSOCIATIVE_NODE_ID,
    N3_DISTRIBUTIVE_NODE_ID,
    N3_IDENTITY_NODE_ID,
    N3_INVERSES_NODE_ID,
]
N3_NODE_IDS = [N3_HUB_NODE_ID, *N3_MACHINE_NODE_IDS]

N4_HUB_NODE_ID = "PREALG-N4-C00-PUERTO-DE-LA-POLIS"
N4_DIVISIBILITY_NODE_ID = "PREALG-N4-C01-DIVISIBILIDAD"
N4_MULTIPLES_NODE_ID = "PREALG-N4-C02-MULTIPLOS"
N4_PRIMES_NODE_ID = "PREALG-N4-C03-PRIMOS"
N4_FACTORIZATION_NODE_ID = "PREALG-N4-C04-FACTORIZACION-PRIMA"
N4_GCD_NODE_ID = "PREALG-N4-C05-MCD"
N4_LCM_NODE_ID = "PREALG-N4-C06-MCM"

N4_CONCEPT_NODE_IDS = [
    N4_DIVISIBILITY_NODE_ID,
    N4_MULTIPLES_NODE_ID,
    N4_PRIMES_NODE_ID,
    N4_FACTORIZATION_NODE_ID,
    N4_GCD_NODE_ID,
    N4_LCM_NODE_ID,
]
N4_NODE_IDS = [N4_HUB_NODE_ID, *N4_CONCEPT_NODE_IDS]

_LESSONS = {
    WELCOME_NODE_ID: {
        "node_id": WELCOME_NODE_ID,
        "node_type": "content_intro",
        "topic": "orientacion_intro",
        "i18n_prefix": "prealgebra.n1.b01",
        "next_node_id": "PREALG-N1-B02-PREGUNTA-DETONADORA",
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": [
            "recognize_sets",
            "explain_uses",
            "classify_numbers",
            "identify_membership",
        ],
        "optional_objectives": ["explore_complex"],
        "interactions": [],
    },
    TRIGGER_NODE_ID: {
        "node_id": TRIGGER_NODE_ID,
        "node_type": "safe_interaction",
        "topic": "conflicto_cognitivo_intro",
        "i18n_prefix": "prealgebra.n1.b02",
        "next_node_id": "PREALG-N1-B03-ESCALERA-NECESIDAD",
        "unlock_after": WELCOME_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["identify_limits_of_counting"],
        "optional_objectives": [],
        # Solo se exponen claves estructuradas; nunca texto libre ni respuestas esperadas.
        "interactions": [
            {
                "interaction_id": "PREALG-N1-B02-Q01",
                "type": "single_select",
                "prompt_key": "prealgebra.n1.b02.q01.prompt",
                "option_keys": ["yes", "no"],
            },
            {
                "interaction_id": "PREALG-N1-B02-Q02",
                "type": "single_select",
                "prompt_key": "prealgebra.n1.b02.q02.prompt",
                "option_keys": ["advance", "bread", "debt"],
            },
        ],
    },
    STAIRCASE_NODE_ID: {
        "node_id": STAIRCASE_NODE_ID,
        "node_type": "concept_organizer",
        "topic": "organizador_previo",
        "i18n_prefix": "prealgebra.n1.b03",
        "next_node_id": "PREALG-N1-B04-NATURALES-CONTAR",
        "unlock_after": TRIGGER_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["recognize_progressive_expansion"],
        "optional_objectives": ["preview_complex_plane"],
        "staircase": {
            "core_steps": ["naturals", "integers", "rationals", "irrationals", "reals"],
            "optional_detour": "complex",
        },
        "interactions": [],
    },
    NATURALS_NODE_ID: {
        "node_id": NATURALS_NODE_ID,
        "node_type": "guided_practice",
        "topic": "naturales",
        "i18n_prefix": "prealgebra.n1.b04",
        "next_node_id": "PREALG-N1-B05-ENTEROS-DEUDA",
        "unlock_after": STAIRCASE_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["count_whole_quantities", "recognize_naturals"],
        "optional_objectives": ["explain_zero_convention"],
        "content": {},
        "interactions": [],
    },
    INTEGERS_NODE_ID: {
        "node_id": INTEGERS_NODE_ID,
        "node_type": "guided_practice",
        "topic": "enteros",
        "i18n_prefix": "prealgebra.n1.b05",
        "next_node_id": "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION",
        "unlock_after": NATURALS_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["represent_negative_quantities", "order_integers"],
        "optional_objectives": [],
        "content": {},
        "interactions": [],
    },
    RATIONALS_NODE_ID: {
        "node_id": RATIONALS_NODE_ID,
        "node_type": "guided_practice",
        "topic": "racionales",
        "i18n_prefix": "prealgebra.n1.b06",
        "next_node_id": "PREALG-N1-B07-IRRACIONALES-DECIMALES",
        "unlock_after": INTEGERS_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["interpret_fraction_as_sharing", "connect_fraction_division_decimal"],
        "optional_objectives": ["recognize_repeating_decimal"],
        # `content` e `interactions` se sobrescriben más abajo con _B06_CONTENT
        # (reconstrucción a 11 bloques). Se dejan vacíos aquí a propósito.
        "content": None,
        "interactions": [],
    },
    IRRATIONALS_NODE_ID: {
        "node_id": IRRATIONALS_NODE_ID,
        "node_type": "guided_practice",
        "topic": "irracionales",
        "i18n_prefix": "prealgebra.n1.b07",
        "next_node_id": "PREALG-N1-B08-REALES-RECTA",
        "unlock_after": RATIONALS_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "objectives": ["define_irrational_as_non_fraction", "distinguish_approximation_from_exact"],
        "optional_objectives": ["locate_sqrt2_on_line"],
        "content": {},
        "interactions": [],
    },
    REALS_NODE_ID: {
        "node_id": REALS_NODE_ID,
        "node_type": "guided_practice",
        "topic": "reales",
        "i18n_prefix": "prealgebra.n1.b08",
        # Cierre de la ruta núcleo; de aquí parte la rama opcional de complejos.
        "next_node_id": "PREALG-N1-B09-COMPLEJOS-PLANO",
        "unlock_after": IRRATIONALS_NODE_ID,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "nucleus_closing_node": True,
        "objectives": ["recognize_reals_as_number_line", "classify_membership_in_reals"],
        "optional_objectives": ["reals_are_not_all_numbers"],
        "content": {},
        "interactions": [],
    },
    COMPLEX_NODE_ID: {
        "node_id": COMPLEX_NODE_ID,
        "node_type": "optional_extension",
        "topic": "complejos",
        "i18n_prefix": "prealgebra.n1.b09",
        # Hoja: rama lateral; no continúa la línea principal.
        "next_node_id": None,
        "unlock_after": REALS_NODE_ID,
        # Visible/explorable solo para banda media/alta (gating en el mapa).
        "unlock_rule": "elo_band in ['intermedio','avanzado']",
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": True,
        "skip_penalty": False,
        "objectives": ["identify_real_and_imaginary_parts", "locate_complex_in_plane"],
        "optional_objectives": ["recognize_reals_as_complex_with_zero_imaginary"],
        "interactions": [],
    },
}

_INTERACTION_RULES = {
    "PREALG-N1-B02-Q01": {
        "node_id": TRIGGER_NODE_ID,
        "valid_options": {"yes", "no"},
        "expected": "no",
        "misconception_by_option": {"yes": "cree_que_todo_numero_sirve_para_contar"},
        "feedback_by_option": {"yes": "counting_is_not_enough", "no": "need_new_numbers"},
    },
    "PREALG-N1-B02-Q02": {
        "node_id": TRIGGER_NODE_ID,
        "valid_options": {"advance", "bread", "debt"},
        "expected": None,
        "misconception_by_option": {},
        "feedback_by_option": {
            "advance": "advance_needs_integers",
            "bread": "sharing_needs_fractions",
            "debt": "debt_needs_integers",
        },
    },
    # B06 (Q01–Q04) retiradas: el nodo se reconstruyó a 11 bloques y sus
    # interacciones se registran data-driven desde _B06_CONTENT más abajo.
}


# ── B10 — El Clasificador I: conjunto más específico ──────────────────────────
# Cada tarjeta es una interacción single_select cuya "opción" es la zona elegida.
# Las tarjetas/zonas complejas (2i, 3+2i) solo se muestran con rama compleja
# (gating por banda en el frontend). Aquí se definen igual; el backend solo evalúa.
_B10_ZONES = [
    "naturals",
    "integers",
    "rationals",
    "irrationals",
    "pure_imaginary",
    "complex_general",
]
_B10_REAL_ZONES = ["naturals", "integers", "rationals", "irrationals"]

# value → (expected_zone, {wrong_zone: (feedback_key, misconception_or_None)}, requires_complex)
_B10_CARDS = {
    "minus3": ("integers", {"naturals": ("minus_three_as_natural", None)}, False),
    "zero": (
        "naturals",
        {
            z: ("zero_not_natural", "excluye_cero_de_naturales_pese_a_convencion")
            for z in _B10_ZONES
            if z != "naturals"
        },
        False,
    ),
    "half": (
        "rationals",
        {
            "naturals": ("fraction_as_integer", "clasifica_fraccion_como_entero"),
            "integers": ("fraction_as_integer", "clasifica_fraccion_como_entero"),
            "irrationals": ("fraction_as_irrational", None),
        },
        False,
    ),
    "sqrt2": (
        "irrationals",
        {"rationals": ("sqrt2_as_rational", "clasifica_irracional_como_racional")},
        False,
    ),
    "pi": (
        "irrationals",
        {"rationals": ("pi_as_rational", "clasifica_irracional_como_racional")},
        False,
    ),
    "five": (
        "naturals",
        {"integers": ("five_as_integer", "clasifica_entero_positivo_como_Z_en_vez_de_N")},
        False,
    ),
    "two_i": (
        "pure_imaginary",
        {
            "irrationals": ("2i_as_irrational", "confunde_i_imaginaria_con_I_irracionales"),
            "complex_general": ("2i_as_complex_general", None),
        },
        True,
    ),
    "three_plus_two_i": (
        "complex_general",
        {
            "pure_imaginary": (
                "3plus2i_as_pure",
                "clasifica_complejo_general_como_imaginario_puro",
            ),
            **{
                z: ("3plus2i_as_real", "ubica_complejos_no_reales_en_recta_real")
                for z in _B10_REAL_ZONES
            },
        },
        True,
    ),
    # Cartas extra de banda Avanzado (gating por banda en el frontend; el backend
    # solo evalúa). No requieren rama compleja.
    "decimal_0333": (
        "rationals",
        {
            "irrationals": (
                "decimal_0333_is_rational",
                "cree_que_todo_decimal_infinito_es_irracional",
            ),
        },
        False,
    ),
    "neg7": (
        "integers",
        {
            "naturals": ("neg7_is_integer", None),
        },
        False,
    ),
    "four_fourths": (
        "naturals",
        {
            "rationals": ("four_fourths_is_one", "confunde_fraccion_aparente_con_racional"),
            "integers": ("four_fourths_is_one", "confunde_fraccion_aparente_con_racional"),
        },
        False,
    ),
}

_LESSONS[CLASSIFIER_BASIC_NODE_ID] = {
    "node_id": CLASSIFIER_BASIC_NODE_ID,
    "node_type": "guided_practice",
    "topic": "clasificacion_especifica",
    "i18n_prefix": "prealgebra.n1.b10",
    "next_node_id": "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
    "unlock_after": REALS_NODE_ID,
    "affects_elo": False,
    "is_safe_zone": True,
    "optional_branch": False,
    "objectives": ["classify_in_most_specific_set"],
    "optional_objectives": ["distinguish_specific_from_multiple_membership"],
    "interactions": [],
}

for _value, (_expected, _wrongs, _requires_complex) in _B10_CARDS.items():
    _INTERACTION_RULES[f"PREALG-N1-B10-CARD-{_value}"] = {
        "node_id": CLASSIFIER_BASIC_NODE_ID,
        "input_kind": "single_select",
        "valid_options": set(_B10_ZONES),
        "expected": _expected,
        "misconception_by_option": {z: m for z, (_f, m) in _wrongs.items() if m},
        "feedback_by_option": {
            _expected: "card_correct",
            **{z: f for z, (f, _m) in _wrongs.items()},
        },
        "default_feedback": "classify_generic",
    }


# ── B07 — mini-reto: rejilla de clasificación racional/irracional ─────────────
# Cada número es una interacción single_select con opciones {rational, irrational}.
# value → (expected, (feedback_wrong, misconception_wrong) | None)
_B07_GRID = {
    "dec05": ("rational", None),
    "periodic03": (
        "rational",
        ("periodic_as_irrational", "cree_que_todo_decimal_infinito_es_irracional"),
    ),
    "pi": ("irrational", ("irrational_as_rational", "no_reconoce_irracional_como_real")),
    "sqrt2": ("irrational", ("irrational_as_rational", "no_reconoce_irracional_como_real")),
    "seven": ("rational", ("integer_as_irrational", "cree_que_enteros_no_son_racionales")),
}

_LESSONS[IRRATIONALS_NODE_ID]["interactions"].extend(
    {
        "interaction_id": f"PREALG-N1-B07-G-{value}",
        "type": "single_select",
        "prompt_key": f"prealgebra.n1.b07.grid.items.{value}",
        "option_keys": ["rational", "irrational"],
        "can_retry": True,
    }
    for value in _B07_GRID
)

for _value, (_expected, _wrong) in _B07_GRID.items():
    _other = "irrational" if _expected == "rational" else "rational"
    _fb = {_expected: "grid_correct"}
    _mis = {}
    if _wrong:
        _fb[_other], _mis[_other] = _wrong[0], _wrong[1]
    _INTERACTION_RULES[f"PREALG-N1-B07-G-{_value}"] = {
        "node_id": IRRATIONALS_NODE_ID,
        "input_kind": "single_select",
        "valid_options": {"rational", "irrational"},
        "expected": _expected,
        "misconception_by_option": _mis,
        "feedback_by_option": _fb,
        "default_feedback": "grid_review",
    }


# ── B08 — mini-reto: rejilla verdadero/falso ──────────────────────────────────
# value → (expected, (feedback_wrong, misconception_wrong) | None). Cada afirmación
# es single_select {true, false}. (El drag_to_region del spec se omite: duplica la
# clasificación de B10.)
_B08_TF = {
    "s1": ("true", None),
    "s2": ("true", None),
    "s3": ("true", ("irrational_is_real_false", "no_reconoce_irracionales_como_reales")),
    "s4": ("false", ("real_is_rational_true", "cree_que_todo_real_es_racional")),
    "s5": ("false", ("complex_in_real_line", "ubica_complejos_en_recta_real")),
}

_LESSONS[REALS_NODE_ID]["interactions"].extend(
    {
        "interaction_id": f"PREALG-N1-B08-{key.upper()}",
        "type": "single_select",
        "prompt_key": f"prealgebra.n1.b08.tf.items.{key}",
        "option_keys": ["true", "false"],
        "can_retry": True,
    }
    for key in _B08_TF
)

for _key, (_expected, _wrong) in _B08_TF.items():
    _other = "false" if _expected == "true" else "true"
    _fb = {_expected: "tf_correct"}
    _mis = {}
    if _wrong:
        _fb[_other], _mis[_other] = _wrong[0], _wrong[1]
    _INTERACTION_RULES[f"PREALG-N1-B08-{_key.upper()}"] = {
        "node_id": REALS_NODE_ID,
        "input_kind": "single_select",
        "valid_options": {"true", "false"},
        "expected": _expected,
        "misconception_by_option": _mis,
        "feedback_by_option": _fb,
        "default_feedback": "tf_review",
    }


# ── B11 — El Clasificador II: pertenencia múltiple (matriz) ───────────────────
# Cada fila (número) es un multi_select sobre las columnas/conjuntos a los que
# pertenece. Columna ℂ y filas complejas (2i, 3+2i) requieren rama compleja
# (gating por flag en el frontend). El "descriptor" (imaginario puro / complejo
# no real) se difiere: el núcleo es la matriz de pertenencia.
# value → (expected_sets, complex_row, [error_rules])
_B11_COLS = ["n", "z", "q", "i", "r", "c"]
_B11_ROWS = {
    "minus3": (
        {"z", "q", "r", "c"},
        False,
        [
            {
                "when_missing": "q",
                "feedback": "integer_not_rational",
                "misconception": "no_reconoce_Z_dentro_de_Q_R_C",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
            {
                "when_missing": "r",
                "feedback": "rational_not_real",
                "misconception": "no_reconoce_Q_dentro_de_R_C",
            },
        ],
    ),
    "zero": (
        {"n", "z", "q", "r", "c"},
        False,
        [
            {
                "when_missing": "n",
                "feedback": "zero_not_natural",
                "misconception": "excluye_cero_de_naturales_pese_a_convencion",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
        ],
    ),
    "half": (
        {"q", "r", "c"},
        False,
        [
            {
                "when_missing": "r",
                "feedback": "rational_not_real",
                "misconception": "no_reconoce_Q_dentro_de_R_C",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
        ],
    ),
    "sqrt2": (
        {"i", "r", "c"},
        False,
        [
            {
                "when_selected": "q",
                "feedback": "irrational_as_rational",
                "misconception": "clasifica_irracional_como_racional",
            },
            {
                "when_missing": "r",
                "feedback": "irrational_not_real",
                "misconception": "no_reconoce_irracionales_como_reales",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
        ],
    ),
    "pi": (
        {"i", "r", "c"},
        False,
        [
            {
                "when_selected": "q",
                "feedback": "irrational_as_rational",
                "misconception": "clasifica_irracional_como_racional",
            },
            {
                "when_missing": "r",
                "feedback": "irrational_not_real",
                "misconception": "no_reconoce_irracionales_como_reales",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
        ],
    ),
    "five": (
        {"n", "z", "q", "r", "c"},
        False,
        [
            {
                "when_missing": "z",
                "feedback": "only_most_specific",
                "misconception": "marca_solo_conjunto_mas_especifico",
            },
            {
                "when_missing": "c",
                "feedback": "real_not_complex",
                "misconception": "no_reconoce_reales_como_complejos",
            },
        ],
    ),
    "two_i": (
        {"c"},
        True,
        [
            {
                "when_selected": "r",
                "feedback": "two_i_as_real",
                "misconception": "ubica_complejos_no_reales_en_recta_real",
            },
            {
                "when_selected": "i",
                "feedback": "two_i_as_irrational",
                "misconception": "confunde_imaginario_puro_con_irracional",
            },
        ],
    ),
    "three_plus_two_i": (
        {"c"},
        True,
        [
            {
                "when_selected": "r",
                "feedback": "three_plus_two_i_as_real",
                "misconception": "ubica_complejos_no_reales_en_recta_real",
            },
            {
                "when_selected": "i",
                "feedback": "three_plus_two_i_as_real",
                "misconception": "ubica_complejos_no_reales_en_recta_real",
            },
        ],
    ),
}

_LESSONS[CLASSIFIER_RIGOROUS_NODE_ID] = {
    "node_id": CLASSIFIER_RIGOROUS_NODE_ID,
    "node_type": "guided_practice",
    "topic": "clasificacion_multiple",
    "i18n_prefix": "prealgebra.n1.b11",
    "next_node_id": "PREALG-N1-B12-DETECTIVE-FALSEDADES",
    "unlock_after": CLASSIFIER_BASIC_NODE_ID,
    "affects_elo": False,
    "is_safe_zone": True,
    "optional_branch": False,
    "objectives": ["recognize_multiple_membership"],
    "optional_objectives": [],
    "interactions": [],
}

for _value, (_expected, _complex, _rules) in _B11_ROWS.items():
    _INTERACTION_RULES[f"PREALG-N1-B11-ROW-{_value}"] = {
        "node_id": CLASSIFIER_RIGOROUS_NODE_ID,
        "input_kind": "multi_select",
        "valid_options": set(_B11_COLS),
        "expected": _expected,
        "feedback_correct": "row_correct",
        "default_feedback": "row_review",
        "error_rules": _rules,
    }

# Descriptor (solo filas complejas, requiere rama compleja): imaginario puro /
# complejo no real. Descriptor formal dentro de ℂ, no un conjunto de la cadena.
_B11_DESCRIPTORS = {"two_i": "pure_imaginary", "three_plus_two_i": "complex_non_real"}
_LESSONS[CLASSIFIER_RIGOROUS_NODE_ID]["interactions"].extend(
    {
        "interaction_id": f"PREALG-N1-B11-DESC-{value}",
        "type": "single_select",
        "prompt_key": f"prealgebra.n1.b11.descriptorPrompt.{value}",
        "option_keys": ["pure_imaginary", "complex_non_real", "none"],
        "can_retry": True,
    }
    for value in _B11_DESCRIPTORS
)
for _value, _expected in _B11_DESCRIPTORS.items():
    _wrong_fb = "desc_3plus2i_as_pure" if _value == "three_plus_two_i" else "desc_review"
    _INTERACTION_RULES[f"PREALG-N1-B11-DESC-{_value}"] = {
        "node_id": CLASSIFIER_RIGOROUS_NODE_ID,
        "input_kind": "single_select",
        "valid_options": {"pure_imaginary", "complex_non_real", "none"},
        "expected": _expected,
        "misconception_by_option": {
            (
                "pure_imaginary" if _expected == "complex_non_real" else "complex_non_real"
            ): "confunde_conjunto_formal_con_descriptor",
        },
        "feedback_by_option": {_expected: "desc_correct"},
        "default_feedback": _wrong_fb,
    }


# ── B12 — El Detective de Falsedades: 14 afirmaciones V/F ──────────────────────
# A1–A9 siempre; A10–A14 requieren rama compleja (gating por flag en el frontend).
# key → (expected, misconception_on_error | None, requires_complex)
_B12_STATEMENTS = {
    "a1": ("true", None, False),
    "a2": ("false", "confunde_implicacion_con_reciproca", False),
    "a3": ("true", None, False),
    "a4": ("true", None, False),
    "a5": ("false", "cree_que_todo_real_es_racional", False),
    "a6": ("false", "cree_que_todo_decimal_infinito_es_irracional", False),
    "a7": ("true", "cree_que_todo_decimal_infinito_es_irracional", False),
    "a8": ("false", "cree_que_todo_real_es_racional", False),
    "a9": ("true", "no_reconoce_irracionales_como_reales", False),
    "a10": ("true", "no_reconoce_reales_como_complejos", True),
    "a11": ("false", "cree_que_todo_complejo_es_real", True),
    "a12": ("false", "cree_que_todo_complejo_es_real", True),
    "a13": ("true", None, True),
    "a14": ("true", "confunde_imaginario_puro_con_irracional", True),
}

_LESSONS[DETECTIVE_NODE_ID] = {
    "node_id": DETECTIVE_NODE_ID,
    "node_type": "guided_practice",
    "topic": "evaluacion_conceptual",
    "i18n_prefix": "prealgebra.n1.b12",
    "next_node_id": CLOSING_NODE_ID,
    "unlock_after": CLASSIFIER_RIGOROUS_NODE_ID,
    "affects_elo": False,
    "is_safe_zone": True,
    "optional_branch": False,
    "objectives": ["evaluate_membership_statements"],
    "optional_objectives": [],
    "interactions": [],
}

for _key, (_expected, _mis, _complex) in _B12_STATEMENTS.items():
    _other = "false" if _expected == "true" else "true"
    _INTERACTION_RULES[f"PREALG-N1-B12-{_key.upper()}"] = {
        "node_id": DETECTIVE_NODE_ID,
        "input_kind": "single_select",
        "valid_options": {"true", "false"},
        "expected": _expected,
        "misconception_by_option": ({_other: _mis} if _mis else {}),
        "feedback_by_option": {_expected: f"{_key}_correct", _other: f"{_key}_incorrect"},
    }


# ── B13 — Cierre diagnóstico (nodo de resumen, sin interacciones) ─────────────
_LESSONS[CLOSING_NODE_ID] = {
    "node_id": CLOSING_NODE_ID,
    "node_type": "diagnostic_summary",
    "topic": "cierre_diagnostico",
    "i18n_prefix": "prealgebra.n1.b13",
    "next_node_id": None,
    "unlock_after": DETECTIVE_NODE_ID,
    "affects_elo": False,
    "is_safe_zone": True,
    "optional_branch": False,
    "objectives": ["consolidate_level_progress"],
    "optional_objectives": [],
    "interactions": [],
}

# Nodos formativos que consolida el diagnóstico (orden de ruta). B09 solo cuenta
# si el estudiante exploró la rama compleja.
# Nivel 2 - Operaciones basicas. El contenido marcado como NEW queda con
# validation_status para revision pedagogica antes de publicacion formal.
# Cada operación tiene su EDIFICIO con nombre propio: el nivel se recorre entrando
# a un edificio, no paseando por un mercado. El contexto de cada nodo sale de lo
# que se hace dentro de su edificio, y ningún edificio presta su oficio a otro.
_N2_BUILDINGS = [
    {
        "id": "E01",
        "operation": "suma",
        "symbol": "+",
        "node_id": N2_SUM_NODE_ID,
        "building": "El Granero Público",
        "trade": "Entra y sale grano; todo se anota en una sola tablilla, con signo.",
        "card": "El granero recibe 14 medidas de trigo y despacha 9. ¿Cómo queda la tablilla?",
    },
    {
        "id": "E02",
        "operation": "resta",
        "symbol": "-",
        "node_id": N2_SUBTRACTION_NODE_ID,
        "building": "La Casa de Cuentas",
        "trade": "Se llevan las deudas y los pagos de la ciudad; aquí un saldo puede quedar por debajo de cero.",
        "card": "Un cliente trae 7 óbolos y debe 12. ¿Cómo queda su cuenta?",
    },
    {
        "id": "E03",
        "operation": "multiplicacion",
        "symbol": "x",
        "node_id": N2_MULTIPLICATION_NODE_ID,
        "building": "El Taller de Mosaicos",
        "trade": "Se arman mosaicos por filas y columnas de teselas, y se copian a otras escalas.",
        "card": "Un mosaico lleva 7 filas de 8 teselas. ¿Cuántas teselas se piden a la bodega?",
    },
    {
        "id": "E04",
        "operation": "division",
        "symbol": "÷",
        "node_id": N2_DIVISION_NODE_ID,
        "building": "El Comedor Comunal",
        "trade": "Se sirven raciones iguales a quien llegue; lo que sobra también se reparte.",
        "card": "Hay 12 hogazas para 4 mesas iguales. ¿Cuántas hogazas por mesa?",
    },
    {
        "id": "E05",
        "operation": "potenciacion",
        "symbol": "a^n",
        "node_id": N2_EXPONENTIATION_NODE_ID,
        "building": "El Invernadero",
        "trade": "Se cultivan esquejes que se duplican solos; cada día multiplica al anterior.",
        "card": "Un esqueje se duplica cada día. Si hoy hay 1, ¿cuántos habrá en 3 días?",
    },
    {
        "id": "E06",
        "operation": "radicacion",
        "symbol": "√",
        "node_id": N2_RADICATION_NODE_ID,
        "building": "La Cantera",
        "trade": "Se cortan losas cuadradas: se encarga la superficie y hay que deducir el lado.",
        "card": "Encargan una losa cuadrada de 16 palmos². ¿Cuánto mide cada lado?",
    },
]

_N2_HUB_CONTENT = {
    "kind": "operation_city_hub",
    "level": "Nivel 2 - Operaciones basicas",
    "title": "La Ciudad de las Operaciones Basicas",
    "welcome_text": (
        "Hola, bienvenido a la ciudad de las operaciones basicas. Aqui podras conocer "
        "cada una de las operaciones primordiales de las matematicas, que en ambitos "
        "de la vida cobran mucha importancia. Espero que te diviertas y te deseo el "
        "mayor de los exitos."
    ),
    "scene_text": (
        "La ciudad tiene seis edificios y cada uno vive de una operación: el Granero "
        "Público, la Casa de Cuentas, el Taller de Mosaicos, el Comedor Comunal, el "
        "Invernadero y la Cantera. En cada uno descubrirás cómo esa operación se extiende "
        "desde los naturales hasta los números reales."
    ),
    "icebreaker": {
        "title": "Antes de entrar: calentando motores",
        "intro": "Tres escenas de la obra en construcción para entrar en calor antes de visitar los edificios.",
        "items": [
            {
                "id": "ICE1",
                "kind": "numeric",
                "prompt": (
                    "Un albañil apila 3 filas de ladrillos: la primera con 4 ladrillos, la "
                    "segunda con 4 más, la tercera con 4 más. ¿Cuántos ladrillos apiló en total?"
                ),
                "image_slot": True,
                "image": "/leccion/02-prealg-n2-mercado/e00-ice1-ladrillos-v4.png",
                "expr": "3\\times 4",
                "answer": "12",
            },
            {
                "id": "ICE2",
                "kind": "single_select",
                "story": (
                    "En la obra, un albañil junta 3 pilas de 5 tejas cada una, mientras que otro "
                    "ayudante ya tiene amontonadas 15 tejas sueltas en un solo montón."
                ),
                "image_slot": True,
                "image": "/leccion/02-prealg-n2-mercado/e00-ice2-tejas-v4.png",
                "support_objects": [
                    "3 pilas de 5 tejas cada una",
                    "1 montón suelto de 15 tejas",
                ],
                "prompt": "¿En qué se parecen las dos cantidades de tejas?",
                "options": [
                    {"id": "a", "text": "Ambas son 15 tejas, aunque estén agrupadas distinto."},
                    {"id": "b", "text": "El montón suelto pesa menos."},
                    {"id": "c", "text": "Las pilas se ven más ordenadas."},
                ],
                "expected": "a",
                "feedback_by_option": {
                    "a": "correct",
                    "b": "fb_n2_ice2_b",
                    "c": "fb_n2_ice2_c",
                },
                "misconception_by_option": {
                    "b": "confunde_agrupacion_con_cantidad",
                    "c": "confunde_orden_con_cantidad",
                },
            },
            {
                "id": "ICE3",
                "kind": "numeric",
                "prompt": (
                    "Al abrir la plaza hay 20 puestos vacíos. Durante la mañana llegan "
                    "comerciantes y ocupan 14. ¿Cuántos puestos quedan vacíos?"
                ),
                "image_slot": True,
                "image": "/leccion/02-prealg-n2-mercado/e00-ice3-puestos-v4.png",
                "expr": "20-14",
                "answer": "6",
            },
        ],
    },
    "advance_text": (
        "Ya conociste las seis operaciones de la ciudad. Ahora entra a cada edificio "
        "cuando quieras y descubrelas a fondo. Te recomiendo empezar por la suma."
    ),
    "gating": {"rule": "all_cards_opened", "cards_required": 6},
    "buildings": _N2_BUILDINGS,
    "feedback": {
        "correct": "¡Correcto!",
        "default": "Revisa la respuesta con calma antes de continuar.",
        "fb_n2_ice2_b": "El peso no cambia la cantidad: cuenta cuántas tejas hay en cada agrupación, no cómo se ven.",
        "fb_n2_ice2_c": "El orden o la prolijidad no cambian el total — cuenta las tejas de cada grupo.",
    },
    "validation_status": "NEW_content_pending_pedagogical_validation",
}

_N2_SEQUENCE = [
    (N2_HUB_NODE_ID, "level_hub_3d", "ciudad_operaciones", "prealgebra.n2.e00", CLOSING_NODE_ID),
    (
        N2_SUM_NODE_ID,
        "operation_building_manipulative",
        "suma",
        "prealgebra.n2.e01",
        N2_HUB_NODE_ID,
    ),
    (
        N2_SUBTRACTION_NODE_ID,
        "operation_building_situations",
        "resta",
        "prealgebra.n2.e02",
        N2_HUB_NODE_ID,
    ),
    (
        N2_MULTIPLICATION_NODE_ID,
        "operation_building_progressive",
        "multiplicacion",
        "prealgebra.n2.e03",
        N2_HUB_NODE_ID,
    ),
    (
        N2_DIVISION_NODE_ID,
        "operation_building_manipulative",
        "division",
        "prealgebra.n2.e04",
        N2_HUB_NODE_ID,
    ),
    (
        N2_EXPONENTIATION_NODE_ID,
        "operation_building_growth_table",
        "potenciacion",
        "prealgebra.n2.e05",
        N2_HUB_NODE_ID,
    ),
    (
        N2_RADICATION_NODE_ID,
        "operation_building_geometric_last",
        "radicacion",
        "prealgebra.n2.e06",
        N2_HUB_NODE_ID,
    ),
]

for _index, (_node_id, _node_type, _topic, _prefix, _unlock_after) in enumerate(_N2_SEQUENCE):
    # Los seis edificios traen su contenido de `nodes/eNN_*.py`; el bucle
    # genérico de NODE_MODULES lo inyecta más abajo. Aquí solo se crea la ficha.
    _content = _N2_HUB_CONTENT if _node_id == N2_HUB_NODE_ID else {}
    _next = _N2_SEQUENCE[_index + 1][0] if _index + 1 < len(_N2_SEQUENCE) else None
    _LESSONS[_node_id] = {
        "node_id": _node_id,
        "node_type": _node_type,
        "topic": _topic,
        "i18n_prefix": _prefix,
        "next_node_id": _next,
        "unlock_after": _unlock_after,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "skip_penalty": False,
        "objectives": ["understand_basic_operations", "solve_contextual_situations"],
        "optional_objectives": [],
        "content": _content,
        "interactions": [],
    }

for _building in _N2_BUILDINGS:
    _interaction_id = f"{N2_HUB_NODE_ID}-CARD-{_building['id']}"
    _LESSONS[N2_HUB_NODE_ID]["interactions"].append(
        {
            "interaction_id": _interaction_id,
            "type": "single_select",
            "prompt_key": _building["operation"],
            "option_keys": ["opened"],
            "can_retry": False,
        }
    )
    _INTERACTION_RULES[_interaction_id] = {
        "node_id": N2_HUB_NODE_ID,
        "valid_options": {"opened"},
        "expected": "opened",
        "misconception_by_option": {},
        "feedback_by_option": {"opened": "card_opened"},
    }

# Nivel 3 - Laboratorio de propiedades misteriosas. Guion Fase 3:
# aprendizaje por descubrimiento, hub de laboratorio y cinco máquinas secuenciales.
_N3_MACHINES = [
    {
        "id": "M01",
        "property": "conmutativa",
        "station": "La Prensa de Intercambio · el orden no importa",
        "symbol": "a↔b",
        "node_id": N3_COMMUTATIVE_NODE_ID,
        "demo": "3 + 5 = 8; 5 + 3 = 8",
        "katia_message": "¡Qué curioso! El orden no importa.",
    },
    {
        "id": "M02",
        "property": "asociativa",
        "station": "El Horno de Fundición · agrupar sin reordenar",
        "symbol": "( )",
        "node_id": N3_ASSOCIATIVE_NODE_ID,
        "demo": "(2 + 3) + 4 = 9; 2 + (3 + 4) = 9",
        "katia_message": "¡Extraño! La forma de agrupar no cambia el resultado.",
    },
    {
        "id": "M03",
        "property": "distributiva",
        "station": "La Cinta Repartidora · un factor, muchas piezas",
        "symbol": "×→",
        "node_id": N3_DISTRIBUTIVE_NODE_ID,
        "demo": "3 × (4 + 2) = 18; 3 × 4 + 3 × 2 = 18",
        "katia_message": "¡Increíble! La multiplicación se distribuye sobre la suma.",
    },
    {
        "id": "M04",
        "property": "elemento neutro",
        "station": "El Calibre Cero · el número que no cambia nada",
        "symbol": "0·1",
        "node_id": N3_IDENTITY_NODE_ID,
        "demo": "5 + 0 = 5; 5 × 1 = 5",
        "katia_message": "Hay números que no cambian el resultado.",
    },
    {
        "id": "M05",
        "property": "inversos",
        "station": "La Prensa de Contrapesos · la pieza que cancela",
        "symbol": "±",
        "node_id": N3_INVERSES_NODE_ID,
        "demo": "5 − 5 = 0; 5 × 1/5 = 1",
        "katia_message": "Hay números que se cancelan entre sí.",
    },
]

_N3_HUB_CONTENT = {
    "kind": "property_laboratory_hub",
    "level": "Nivel 3 - Propiedades",
    "title": "El Laboratorio de las Propiedades Misteriosas",
    "welcome_text": (
        "Hola, bienvenido al laboratorio de las propiedades misteriosas. Aquí podrás "
        "conocer algunas de las propiedades más importantes de los números al realizar "
        "operaciones matemáticas. Espero que te diviertas y te deseo el mayor de los éxitos."
    ),
    "scene_text": (
        "El laboratorio tiene cinco máquinas industriales. En cada una descubrirás una "
        "regla secreta de las operaciones mediante una demostración, una serie guiada "
        "y una formalización."
    ),
    "drag_rule": (
        "Al seleccionar un número, la casilla destino se ilumina de verde y las demás "
        "de rojo; solo se permite soltar el número en la casilla correspondiente."
    ),
    "icebreaker": {
        "title": "Antes de calibrar: primeras pesadas",
        "intro": "Tres pesadas de prueba en la balanza del laboratorio para entrar en calor antes de las máquinas.",
        "items": [
            {
                "id": "ICE1",
                "kind": "numeric",
                "prompt": (
                    "Una máquina del laboratorio pesa 3 bloques de 4 kg cada uno en el platillo "
                    "izquierdo. ¿Cuántos kg marca la balanza en total?"
                ),
                "image_slot": True,
                "image": "/leccion/03-prealg-n3-fabrica/m00-ice1-balanza-bloques-v4.png",
                "expr": "3\\times 4",
                "answer": "12",
            },
            {
                "id": "ICE2",
                "kind": "single_select",
                "story": (
                    "Un ayudante coloca primero un engranaje de 5 kg y luego uno de 3 kg en el "
                    "platillo de una balanza. En una balanza idéntica, otro ayudante coloca "
                    "primero el de 3 kg y luego el de 5 kg."
                ),
                "image_slot": True,
                "image": "/leccion/03-prealg-n3-fabrica/m00-ice2-balanzas-orden-v4.png",
                "support_objects": [
                    "2 balanzas de laboratorio idénticas",
                    "un engranaje de 5 kg y uno de 3 kg por balanza",
                ],
                "prompt": "¿Qué marcarán las dos balanzas al final?",
                "options": [
                    {
                        "id": "a",
                        "text": "Lo mismo: 8 kg en ambas, el orden no cambió el peso total.",
                    },
                    {"id": "b", "text": "La segunda balanza marcará menos."},
                    {"id": "c", "text": "No se puede saber sin pesarlos de nuevo."},
                ],
                "expected": "a",
                "feedback_by_option": {
                    "a": "correct",
                    "b": "fb_n3_ice2_b",
                    "c": "fb_n3_ice2_c",
                },
                "misconception_by_option": {
                    "b": "cree_que_el_orden_cambia_el_total",
                    "c": "duda_de_propiedad_verificable",
                },
            },
            {
                "id": "ICE3",
                "kind": "numeric",
                "prompt": (
                    "La balanza marca 9 kg con una pieza de prueba puesta. Al retirar esa "
                    "pieza, que pesa exactamente 9 kg, ¿cuánto marca la balanza?"
                ),
                "image_slot": True,
                "image": "/leccion/03-prealg-n3-fabrica/m00-ice3-retirar-pieza-v4.png",
                "expr": "9-9",
                "answer": "0",
            },
        ],
    },
    "advance_text": (
        "¡Descubriste las cinco propiedades del laboratorio! Ahora entiendes algunas "
        "de las reglas secretas que siguen los números cuando operamos con ellos."
    ),
    "gating": {"rule": "all_machines_introduced", "machines_required": 5},
    "machines": _N3_MACHINES,
    "feedback": {
        "correct": "¡Correcto!",
        "default": "Revisa la respuesta con calma antes de continuar.",
        "fb_n3_ice2_b": "El peso total no depende del orden en que se coloquen las piezas — suma ambas, en cualquier orden.",
        "fb_n3_ice2_c": "Sí se puede saber sin volver a pesar: el orden de las piezas no cambia cuánto pesan juntas.",
    },
    "validation_status": "F3_storytelling_implemented",
}

_N3_SEQUENCE = [
    (
        N3_HUB_NODE_ID,
        "level_hub_laboratory",
        "laboratorio_propiedades",
        "prealgebra.n3.m00",
        N2_RADICATION_NODE_ID,
    ),
    (
        N3_COMMUTATIVE_NODE_ID,
        "property_machine_guided_discovery",
        "conmutativa",
        "prealgebra.n3.m01",
        N3_HUB_NODE_ID,
    ),
    (
        N3_ASSOCIATIVE_NODE_ID,
        "property_machine_guided_discovery",
        "asociativa",
        "prealgebra.n3.m02",
        N3_COMMUTATIVE_NODE_ID,
    ),
    (
        N3_DISTRIBUTIVE_NODE_ID,
        "property_machine_guided_discovery",
        "distributiva",
        "prealgebra.n3.m03",
        N3_ASSOCIATIVE_NODE_ID,
    ),
    (
        N3_IDENTITY_NODE_ID,
        "property_machine_guided_discovery",
        "elemento_neutro",
        "prealgebra.n3.m04",
        N3_DISTRIBUTIVE_NODE_ID,
    ),
    (
        N3_INVERSES_NODE_ID,
        "property_machine_cancellation_last",
        "inversos",
        "prealgebra.n3.m05",
        N3_IDENTITY_NODE_ID,
    ),
]

for _index, (_node_id, _node_type, _topic, _prefix, _unlock_after) in enumerate(_N3_SEQUENCE):
    # Las cinco estaciones traen su contenido de `nodes/mNN_*.py`; el bucle
    # genérico de NODE_MODULES lo inyecta más abajo. Aquí solo se crea la ficha.
    _content = _N3_HUB_CONTENT if _node_id == N3_HUB_NODE_ID else {}
    _next = _N3_SEQUENCE[_index + 1][0] if _index + 1 < len(_N3_SEQUENCE) else None
    _LESSONS[_node_id] = {
        "node_id": _node_id,
        "node_type": _node_type,
        "topic": _topic,
        "i18n_prefix": _prefix,
        "next_node_id": _next,
        "unlock_after": _unlock_after,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "skip_penalty": False,
        "objectives": ["recognize_operation_properties", "compare_property_examples"],
        "optional_objectives": ["connect_properties_to_equations"],
        "content": _content,
        "interactions": [],
    }

for _machine in _N3_MACHINES:
    _interaction_id = f"{N3_HUB_NODE_ID}-MACHINE-{_machine['id']}"
    _LESSONS[N3_HUB_NODE_ID]["interactions"].append(
        {
            "interaction_id": _interaction_id,
            "type": "single_select",
            "prompt_key": _machine["property"],
            "option_keys": ["introduced"],
            "can_retry": False,
        }
    )
    _INTERACTION_RULES[_interaction_id] = {
        "node_id": N3_HUB_NODE_ID,
        "valid_options": {"introduced"},
        "expected": "introduced",
        "misconception_by_option": {},
        "feedback_by_option": {"introduced": "machine_introduced"},
    }

# Respuestas tecleadas (`text_exact`). Es entrada de usuario: lista blanca corta,
# no un parser. Un termino es un numero, una fraccion, una raiz o un monomio; una
# respuesta es un termino o una suma de hasta cuatro.
_TEXT_TERM = (
    r"\d{0,4}[a-z](?:\^\d{1,2})?"  # 8x, x, 12x^5
    r"|\d{1,4}(?:/\d{1,4})?"  # 12, 3/4
    r"|sqrt\d{1,4}(?:/\d{1,4})?|1/sqrt\d{1,4}"  # sqrt2, sqrt2/2, 1/sqrt2
)
_TEXT_ANSWER_RE = re.compile(rf"-?(?:{_TEXT_TERM})(?:[+-](?:{_TEXT_TERM})){{0,3}}")


def _register_mixed_interactions(
    node_id: str,
    concept_slug: str,
    items: list[dict],
    required: bool = True,
) -> None:
    """Registra interacciones de tipo mixto (numeric/single_select/multi_select).

    Nivel 4 mezcla los tres tipos dentro de un mismo nodo (a diferencia de N2/N3,
    que solo generaban `numeric`/`text_exact`), así que un único registrador
    data-driven reemplaza los tres bucles distintos que tendría cada tipo.

    `required=False` (rompe-hielo de un hub): la interacción es evaluable vía
    `/interactions` pero NO se agrega a `_LESSONS[node_id]["interactions"]`, así
    que no cuenta para el gating de `node_completed` — es calentamiento opcional,
    no bloquea "Completar ciudad/Activar laboratorio/Entrar al puerto".
    """
    for item in items:
        interaction_id = f"{node_id}-{item['id']}"
        kind = item["kind"]
        if kind == "numeric":
            if required:
                _LESSONS[node_id]["interactions"].append(
                    {
                        "interaction_id": interaction_id,
                        "type": "numeric_input",
                        "prompt_key": item["id"],
                        "option_keys": [],
                        "can_retry": True,
                    }
                )
            _INTERACTION_RULES[interaction_id] = {
                "node_id": node_id,
                "input_kind": "numeric",
                "expected": item["answer"],
                "misconception_by_option": {},
                "feedback_by_result": {True: "correct", False: "default"},
                "default_misconception": f"error_{concept_slug}",
            }
        elif kind == "text_exact":
            # El estudiante TECLEA la expresion en vez de elegirla. Se usa cuando la
            # respuesta es algebraica (`6r+3`) y ofrecer opciones regalaria el
            # resultado. Sin diagnostico por distractor: para eso esta single_select.
            if required:
                _LESSONS[node_id]["interactions"].append(
                    {
                        "interaction_id": interaction_id,
                        "type": "text_input",
                        "prompt_key": item["id"],
                        "option_keys": [],
                        "can_retry": True,
                    }
                )
            _INTERACTION_RULES[interaction_id] = {
                "node_id": node_id,
                "input_kind": "text_exact",
                "expected": item["answer"],
                # Formas equivalentes que el autor acepta (`3x+2` y `2+3x`).
                "accepted": set(item.get("accepted", [])),
                "misconception_by_option": {},
                "feedback_by_result": {True: "correct", False: "default"},
                "default_misconception": f"error_{concept_slug}",
            }
        elif kind == "single_select":
            option_ids = {opt["id"] for opt in item["options"]}
            if required:
                _LESSONS[node_id]["interactions"].append(
                    {
                        "interaction_id": interaction_id,
                        "type": "single_select",
                        "prompt_key": item["id"],
                        "option_keys": [opt["id"] for opt in item["options"]],
                        "can_retry": True,
                    }
                )
            _INTERACTION_RULES[interaction_id] = {
                "node_id": node_id,
                "valid_options": option_ids,
                "expected": item["expected"],
                "misconception_by_option": item.get("misconception_by_option", {}),
                "feedback_by_option": item.get("feedback_by_option", {}),
                "default_feedback": item.get("default_feedback", "default"),
            }
        elif kind == "multi_select":
            if required:
                _LESSONS[node_id]["interactions"].append(
                    {
                        "interaction_id": interaction_id,
                        "type": "multi_select",
                        "prompt_key": item["id"],
                        "option_keys": sorted(item["valid_options"]),
                        "can_retry": True,
                    }
                )
            _INTERACTION_RULES[interaction_id] = {
                "node_id": node_id,
                "input_kind": "multi_select",
                "valid_options": set(item["valid_options"]),
                "expected": set(item["expected"]),
                "trap_options": set(item.get("trap_options", set())),
                "feedback_correct": item.get("feedback_correct", "correct"),
                "feedback_trap": item.get("feedback_trap", "default"),
                "misconception_trap": item.get("misconception_trap"),
                "feedback_missing": item.get("feedback_missing", "default"),
                "misconception_missing": item.get("misconception_missing"),
                "feedback_incorrect": item.get("feedback_incorrect", "default"),
                "misconception_incorrect": item.get("misconception_incorrect"),
            }
        else:
            raise ValueError(f"unsupported N4 interaction kind: {kind}")


_N4_CARDS = [
    {
        "id": "C01",
        "concept": "divisibilidad",
        "symbol": "b \\mid a",
        "node_id": N4_DIVISIBILITY_NODE_ID,
        "destination": "Corinto · el reparto exacto",
        "teaser": "Reparte la carga de un barco sin que sobre nada.",
    },
    {
        "id": "C02",
        "concept": "multiplos",
        "symbol": "M(b)",
        "node_id": N4_MULTIPLES_NODE_ID,
        "destination": "Rodas · lo que se repite",
        "teaser": "Descubre los barcos que zarpan cada cierto número de días.",
    },
    {
        "id": "C03",
        "concept": "primos",
        "symbol": "p",
        "node_id": N4_PRIMES_NODE_ID,
        "destination": "Delos · la isla indivisible",
        "teaser": "Encuentra las polis con una sola ruta directa al puerto.",
    },
    {
        "id": "C04",
        "concept": "factorizacion_prima",
        "symbol": "2\\times3\\times5",
        "node_id": N4_FACTORIZATION_NODE_ID,
        "destination": "Mileto · piezas fundamentales",
        "teaser": "Desmonta la carga de un barco en sus piezas más pequeñas.",
    },
    {
        "id": "C05",
        "concept": "mcd",
        "symbol": "\\text{MCD}",
        "node_id": N4_GCD_NODE_ID,
        "destination": "Atenas · lo más grande en común",
        "teaser": "Halla el contenedor más grande que reparte exacto dos cargamentos.",
    },
    {
        "id": "C06",
        "concept": "mcm",
        "symbol": "\\text{MCM}",
        "node_id": N4_LCM_NODE_ID,
        "destination": "Esparta · donde coinciden las rutas",
        "teaser": "Calcula cada cuánto coinciden dos barcos en el mismo muelle.",
    },
]

_N4_HUB_CONTENT = {
    "kind": "level_hub_port",
    "level": "Nivel 4 - Divisibilidad",
    "title": "El Puerto de la Polis",
    "welcome_text": (
        "Bienvenido al Puerto de la Polis. Aquí llegan y zarpan los barcos que cargan "
        "ánforas de aceite, sacos de trigo, rollos de tela y cerámica hacia Atenas, Corinto, "
        "Delos, Mileto, Rodas y Esparta. El escriba portuario necesita entender cómo se "
        "reparte, se repite y se combina la carga antes de que cada barco zarpe."
    ),
    "scene_text": (
        "El puerto tiene seis muelles. En cada uno descubrirás una idea distinta sobre cómo "
        "se comportan los números al repartirse, repetirse y combinarse."
    ),
    "icebreaker": {
        "title": "Antes de zarpar: rompiendo el hielo",
        "intro": "Tres escenas del puerto para entrar en calor antes de visitar los muelles.",
        "items": [
            {
                "id": "ICE1",
                "kind": "multi_select",
                "prompt": (
                    "Un mercader tiene 12 naranjas y quiere repartirlas en partes iguales. "
                    "Selecciona con cuántas personas puede repartirlas sin que sobre ninguna: "
                    "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12."
                ),
                "image_slot": True,
                "image": "/leccion/04-prealg-n4-puerto/c00-ice1-naranjas-reparto-v4.png",
                "valid_options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                "expected": ["1", "2", "3", "4", "6", "12"],
                "trap_options": [],
                "feedback_correct": "correct",
                "feedback_trap": "default",
                "feedback_missing": "fb_hub_ice1_missing",
                "misconception_missing": "olvida_verificar_residuo_cero",
                "feedback_incorrect": "default",
                "misconception_incorrect": "error_puerto",
            },
            {
                "id": "ICE2",
                "kind": "single_select",
                "story": (
                    "En el muelle hay cinco postes clavados con tablillas de ruta: 2, 3, 5, 7 y 11 "
                    "escalas. El escriba intenta repartir cada poste en tramos iguales con una cuerda "
                    "y, salvo cortar en 1 tramo o en tantos tramos como escalas tiene, ninguno se deja "
                    "partir parejo."
                ),
                "image_slot": True,
                "image": "/leccion/04-prealg-n4-puerto/c00-ice2-postes-primos-v4.png",
                "support_objects": [
                    "5 postes de madera con tablillas numeradas 2, 3, 5, 7, 11",
                    "una cuerda de medir intentando marcar tramos iguales en cada poste",
                ],
                "prompt": "¿Qué tienen en común los números 2, 3, 5, 7 y 11?",
                "options": [
                    {"id": "a", "text": "Solo tienen dos divisores: 1 y ellos mismos."},
                    {"id": "b", "text": "Son todos impares."},
                    {"id": "c", "text": "La suma de todos es múltiplo de 5."},
                ],
                "expected": "a",
                "feedback_by_option": {
                    "a": "correct",
                    "b": "fb_hub_ice2_b",
                    "c": "fb_hub_ice2_c",
                },
                "misconception_by_option": {
                    "b": "confunde_paridad_con_ser_primo",
                    "c": "inventa_criterio_por_suma_total",
                },
            },
            {
                "id": "ICE3",
                "kind": "numeric",
                "prompt": (
                    "Cada carreta nueva que llega al puerto trae 4 rollos de tela más que la anterior: "
                    "4, 8, 12, 16, 20... Siguiendo el patrón, ¿cuántos rollos de tela trae la 6ª carreta?"
                ),
                "image_slot": True,
                "image": "/leccion/04-prealg-n4-puerto/c00-ice3-carretas-tela-v4.png",
                "expr": "4\\times 6",
                "answer": "24",
            },
        ],
    },
    "advance_text": (
        "Ya viste que reparto exacto, repetición y coincidencia están en todas partes del "
        "puerto. Ahora visita los seis muelles para dominarlas una por una."
    ),
    "gating": {"rule": "all_cards_opened", "cards_required": 6},
    "cards": _N4_CARDS,
    "feedback": {
        "correct": "¡Correcto!",
        "default": "Revisa la respuesta con calma antes de continuar.",
        "fb_hub_ice1_missing": "Te falta al menos una cantidad: verifica que 12 se reparta exacto entre ese número de personas.",
        "fb_hub_ice2_b": "2 es primo y es par; 'impar' no es el criterio correcto — cuenta los divisores.",
        "fb_hub_ice2_c": "La suma total no tiene relación; cuenta los divisores de cada número por separado.",
    },
    "validation_status": "F4_C01_pilot",
}

_N4_SEQUENCE = [
    (
        N4_HUB_NODE_ID,
        "level_hub_port",
        "puerto_de_la_polis",
        "prealgebra.n4.c00",
        N3_INVERSES_NODE_ID,
    ),
    (
        N4_DIVISIBILITY_NODE_ID,
        "divisibility_concept_guided_discovery",
        "divisibilidad",
        "prealgebra.n4.c01",
        N4_HUB_NODE_ID,
    ),
    (
        N4_MULTIPLES_NODE_ID,
        "divisibility_concept_guided_discovery",
        "multiplos",
        "prealgebra.n4.c02",
        N4_DIVISIBILITY_NODE_ID,
    ),
    (
        N4_PRIMES_NODE_ID,
        "divisibility_concept_guided_discovery",
        "primos",
        "prealgebra.n4.c03",
        N4_MULTIPLES_NODE_ID,
    ),
    (
        N4_FACTORIZATION_NODE_ID,
        "divisibility_concept_guided_discovery",
        "factorizacion_prima",
        "prealgebra.n4.c04",
        N4_PRIMES_NODE_ID,
    ),
    (
        N4_GCD_NODE_ID,
        "divisibility_concept_guided_discovery",
        "mcd",
        "prealgebra.n4.c05",
        N4_FACTORIZATION_NODE_ID,
    ),
    (
        N4_LCM_NODE_ID,
        "divisibility_concept_guided_discovery",
        "mcm",
        "prealgebra.n4.c06",
        N4_GCD_NODE_ID,
    ),
]

for _index, (_node_id, _node_type, _topic, _prefix, _unlock_after) in enumerate(_N4_SEQUENCE):
    # Los seis destinos traen su contenido de `nodes/cNN_*.py`; el bucle
    # genérico de NODE_MODULES lo inyecta más abajo. Aquí solo se crea la ficha.
    _content = _N4_HUB_CONTENT if _node_id == N4_HUB_NODE_ID else {}
    _next = _N4_SEQUENCE[_index + 1][0] if _index + 1 < len(_N4_SEQUENCE) else None
    _LESSONS[_node_id] = {
        "node_id": _node_id,
        "node_type": _node_type,
        "topic": _topic,
        "i18n_prefix": _prefix,
        "next_node_id": _next,
        "unlock_after": _unlock_after,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "skip_penalty": False,
        "objectives": ["understand_divisibility_and_multiples", "apply_prime_factorization"],
        "optional_objectives": [],
        "content": _content,
        "interactions": [],
    }

_LESSONS[N3_INVERSES_NODE_ID]["next_node_id"] = N4_HUB_NODE_ID

# ---------------------------------------------------------------------------
# ALG-N1 · El Papiro de las Cuatro Casas (Kemet)
#
# Módulo NARRATIVO nuevo — Preálgebra transcurre en Grecia, Álgebra en Egipto —
# pero continuación TÉCNICA: mismo curso, mismo renderer de 11 bloques, mismo
# registro de interacciones. La posición en la ruta la fija `unlock_after`, no
# el prefijo del ID. Sin hub: se entra por el primer nodo, porque el arco es una
# sola crecida y no un selector de destinos.
#
# Los cuatro nodos son las cuatro secciones del papiro dañado que Meritka debe
# reconstruir: nombrar → combinar → repartir → conservar la relación.
# Ficha del nivel: GUIA_APLICADA_ALGEBRA_N1_ANTIGUO_EGIPTO.md
# ---------------------------------------------------------------------------
ALG_HUB_NODE_ID = a00_hub.NODE_ID
ALG_VARIABLES_NODE_ID = "ALG-N1-L01-VARIABLES"
ALG_CONSTANTS_NODE_ID = "ALG-N1-L02-CONSTANTES"
ALG_TRANSLATION_NODE_ID = "ALG-N1-L03-TRADUCCION"
ALG_NUMERIC_VALUE_NODE_ID = "ALG-N1-L04-VALOR-NUMERICO"
ALG_OPERATIONS_NODE_ID = "ALG-N1-O01-SEMEJANTES"
ALG_SIGNS_NODE_ID = "ALG-N1-O02-SIGNOS"
ALG_PRODUCT_NODE_ID = "ALG-N1-O03-PRODUCTO"
ALG_QUOTIENT_NODE_ID = "ALG-N1-O04-COCIENTE"
ALG_OPERATIONS_NODE_ID = "ALG-N1-O01-SEMEJANTES"
ALG_SIGNS_NODE_ID = "ALG-N1-O02-SIGNOS"
ALG_PRODUCT_NODE_ID = "ALG-N1-O03-PRODUCTO"
ALG_QUOTIENT_NODE_ID = "ALG-N1-O04-COCIENTE"
ALG_FRACTIONS_NODE_ID = "ALG-N1-F01-SIMPLIFICAR"
ALG_FRAC_SUM_NODE_ID = "ALG-N1-F02-SUMA"
ALG_FRAC_PRODUCT_NODE_ID = "ALG-N1-F03-PRODUCTO"
ALG_FRAC_DIVISION_NODE_ID = "ALG-N1-F04-DIVISION"
ALG_RATIOS_NODE_ID = "ALG-N1-R01-RAZONES"
ALG_RULE_OF_THREE_NODE_ID = "ALG-N1-R02-REGLA-DE-TRES"
ALG_PERCENT_NODE_ID = "ALG-N1-R03-PORCENTAJES"
ALG_VARIATION_NODE_ID = "ALG-N1-R04-VARIACION"

_ALG_N1_SEQUENCE = [
    (ALG_HUB_NODE_ID, "level_hub_cards", "papiro_cuatro_casas", "algebra.a00", N4_LCM_NODE_ID),
    (
        ALG_VARIABLES_NODE_ID,
        "algebra_concept_guided_discovery",
        "variables",
        "algebra.n1.l01",
        ALG_HUB_NODE_ID,
    ),
    (
        ALG_CONSTANTS_NODE_ID,
        "algebra_concept_guided_discovery",
        "constantes",
        "algebra.n1.l02",
        ALG_VARIABLES_NODE_ID,
    ),
    (
        ALG_TRANSLATION_NODE_ID,
        "algebra_concept_guided_discovery",
        "traduccion",
        "algebra.n1.l03",
        ALG_CONSTANTS_NODE_ID,
    ),
    (
        ALG_NUMERIC_VALUE_NODE_ID,
        "algebra_concept_guided_discovery",
        "valor_numerico",
        "algebra.n1.l04",
        ALG_TRANSLATION_NODE_ID,
    ),
    (
        ALG_OPERATIONS_NODE_ID,
        "algebra_concept_guided_discovery",
        "terminos_semejantes",
        "algebra.n2.o01",
        ALG_NUMERIC_VALUE_NODE_ID,
    ),
    (
        ALG_SIGNS_NODE_ID,
        "algebra_concept_guided_discovery",
        "signos_y_parentesis",
        "algebra.n2.o02",
        ALG_OPERATIONS_NODE_ID,
    ),
    (
        ALG_PRODUCT_NODE_ID,
        "algebra_concept_guided_discovery",
        "producto_de_monomios",
        "algebra.n2.o03",
        ALG_SIGNS_NODE_ID,
    ),
    (
        ALG_QUOTIENT_NODE_ID,
        "algebra_concept_guided_discovery",
        "cociente_de_monomios",
        "algebra.n2.o04",
        ALG_PRODUCT_NODE_ID,
    ),
    (
        ALG_FRACTIONS_NODE_ID,
        "algebra_concept_guided_discovery",
        "fracciones_algebraicas",
        "algebra.n1.b03",
        ALG_QUOTIENT_NODE_ID,
    ),
    (
        ALG_FRAC_SUM_NODE_ID,
        "algebra_concept_guided_discovery",
        "suma_de_fracciones_algebraicas",
        "algebra.n3.f02",
        ALG_FRACTIONS_NODE_ID,
    ),
    (
        ALG_FRAC_PRODUCT_NODE_ID,
        "algebra_concept_guided_discovery",
        "producto_de_fracciones_algebraicas",
        "algebra.n3.f03",
        ALG_FRAC_SUM_NODE_ID,
    ),
    (
        ALG_FRAC_DIVISION_NODE_ID,
        "algebra_concept_guided_discovery",
        "division_de_fracciones_algebraicas",
        "algebra.n3.f04",
        ALG_FRAC_PRODUCT_NODE_ID,
    ),
    (
        ALG_RATIOS_NODE_ID,
        "algebra_concept_guided_discovery",
        "razones_y_proporciones",
        "algebra.n4.r01",
        ALG_FRAC_DIVISION_NODE_ID,
    ),
    (
        ALG_RULE_OF_THREE_NODE_ID,
        "algebra_concept_guided_discovery",
        "regla_de_tres",
        "algebra.n4.r02",
        ALG_RATIOS_NODE_ID,
    ),
    (
        ALG_PERCENT_NODE_ID,
        "algebra_concept_guided_discovery",
        "porcentajes",
        "algebra.n4.r03",
        ALG_RULE_OF_THREE_NODE_ID,
    ),
    (
        ALG_VARIATION_NODE_ID,
        "algebra_concept_guided_discovery",
        "variacion_directa_e_inversa",
        "algebra.n4.r04",
        ALG_PERCENT_NODE_ID,
    ),
]

ALG_N1_NODE_IDS = [_row[0] for _row in _ALG_N1_SEQUENCE]

# ── ALG-N2 · La sala de los troqueles (Casa de la Sabiduria, Bagdad) ─────────
# Productos notables. Sub-espacio propio: "patio de los mosaicos" del mapa
# chocaba con E03, El Taller de Mosaicos, asi que la sala estampa troqueles.
ALG_BAGDAD_HUB_NODE_ID = s00_hub_bagdad.NODE_ID
ALG_SQUARE_NODE_ID = "ALG-N2-P01-CUADRADO"
ALG_CONJUGATE_NODE_ID = "ALG-N2-P02-CONJUGADOS"
ALG_CUBE_NODE_ID = "ALG-N2-P03-CUBO"
ALG_COMMON_TERM_NODE_ID = "ALG-N2-P04-TERMINO-COMUN"

_ALG_N2_SEQUENCE = [
    (
        ALG_BAGDAD_HUB_NODE_ID,
        "level_hub_cards",
        "casa_de_la_sabiduria",
        "algebra.s00",
        ALG_VARIATION_NODE_ID,
    ),
    (
        ALG_SQUARE_NODE_ID,
        "algebra_concept_guided_discovery",
        "cuadrado_de_binomio",
        "algebra.n5.p01",
        ALG_BAGDAD_HUB_NODE_ID,
    ),
    (
        ALG_CONJUGATE_NODE_ID,
        "algebra_concept_guided_discovery",
        "binomios_conjugados",
        "algebra.n5.p02",
        ALG_SQUARE_NODE_ID,
    ),
    (
        ALG_CUBE_NODE_ID,
        "algebra_concept_guided_discovery",
        "cubo_de_binomio",
        "algebra.n5.p03",
        ALG_CONJUGATE_NODE_ID,
    ),
    (
        ALG_COMMON_TERM_NODE_ID,
        "algebra_concept_guided_discovery",
        "producto_con_termino_comun",
        "algebra.n5.p04",
        ALG_CUBE_NODE_ID,
    ),
]

ALG_N2_NODE_IDS = [_row[0] for _row in _ALG_N2_SEQUENCE]

# ── ALG-N3 · El almacen de la caravana (Casa de la Sabiduria, Bagdad) ────────
# Factorizacion: el camino de vuelta de los troqueles. Guia: Salim.
ALG_COMMON_FACTOR_NODE_ID = "ALG-N3-G01-FACTOR-COMUN"
ALG_SQUARES_NODE_ID = "ALG-N3-G02-CUADRADOS"
ALG_TRINOMIAL_NODE_ID = "ALG-N3-G03-TRINOMIO"
ALG_CUBES_NODE_ID = "ALG-N3-G04-CUBOS"
ALG_FULL_FACTOR_NODE_ID = "ALG-N3-G05-EXPEDICION"

_ALG_N3_SEQUENCE = [
    (
        ALG_COMMON_FACTOR_NODE_ID,
        "algebra_concept_guided_discovery",
        "factor_comun_y_agrupacion",
        "algebra.n6.g01",
        ALG_COMMON_TERM_NODE_ID,
    ),
    (
        ALG_SQUARES_NODE_ID,
        "algebra_concept_guided_discovery",
        "diferencia_de_cuadrados_y_tcp",
        "algebra.n6.g02",
        ALG_COMMON_FACTOR_NODE_ID,
    ),
    (
        ALG_TRINOMIAL_NODE_ID,
        "algebra_concept_guided_discovery",
        "trinomio_general",
        "algebra.n6.g03",
        ALG_SQUARES_NODE_ID,
    ),
    (
        ALG_CUBES_NODE_ID,
        "algebra_concept_guided_discovery",
        "suma_y_diferencia_de_cubos",
        "algebra.n6.g04",
        ALG_TRINOMIAL_NODE_ID,
    ),
    (
        ALG_FULL_FACTOR_NODE_ID,
        "algebra_concept_guided_discovery",
        "factorizacion_completa",
        "algebra.n6.g05",
        ALG_CUBES_NODE_ID,
    ),
]

ALG_N3_NODE_IDS = [_row[0] for _row in _ALG_N3_SEQUENCE]

# Los dos niveles comparten ficha y bucle: lo unico que los separa es el
# `unlock_after` del primer nodo de N2, que apunta al ultimo de N1.
_ALG_SEQUENCE = _ALG_N1_SEQUENCE + _ALG_N2_SEQUENCE + _ALG_N3_SEQUENCE

# Los dos hubs traen su contenido de su modulo; el resto lo inyecta NODE_MODULES.
_ALG_HUB_CONTENT = {
    ALG_HUB_NODE_ID: a00_hub.CONTENT,
    ALG_BAGDAD_HUB_NODE_ID: s00_hub_bagdad.CONTENT,
}

for _index, (_node_id, _node_type, _topic, _prefix, _unlock_after) in enumerate(_ALG_SEQUENCE):
    # Las cuatro casas traen su contenido de `nodes/aNN_*.py`; el bucle genérico
    # de NODE_MODULES lo inyecta más abajo. Aquí solo se crea la ficha.
    _next = _ALG_SEQUENCE[_index + 1][0] if _index + 1 < len(_ALG_SEQUENCE) else None
    _alg_content = _ALG_HUB_CONTENT.get(_node_id, {})
    _LESSONS[_node_id] = {
        "node_id": _node_id,
        "node_type": _node_type,
        "topic": _topic,
        "i18n_prefix": _prefix,
        "next_node_id": _next,
        "unlock_after": _unlock_after,
        "affects_elo": False,
        "is_safe_zone": True,
        "optional_branch": False,
        "skip_penalty": False,
        "objectives": ["represent_quantities_with_letters", "interpret_algebraic_expressions"],
        "optional_objectives": [],
        "content": _alg_content,
        "interactions": [],
    }

_LESSONS[N4_LCM_NODE_ID]["next_node_id"] = ALG_HUB_NODE_ID

for _hub_id, _hub_module, _hub_slug in (
    (ALG_HUB_NODE_ID, a00_hub, "papiro"),
    (ALG_BAGDAD_HUB_NODE_ID, s00_hub_bagdad, "sabiduria"),
):
    for _card in _hub_module.CARDS:
        _interaction_id = f"{_hub_id}-CARD-{_card['id']}"
        _LESSONS[_hub_id]["interactions"].append(
            {
                "interaction_id": _interaction_id,
                "type": "single_select",
                "prompt_key": _card["concept"],
                "option_keys": ["opened"],
                "can_retry": False,
            }
        )
        _INTERACTION_RULES[_interaction_id] = {
            "node_id": _hub_id,
            "valid_options": {"opened"},
            "expected": "opened",
            "misconception_by_option": {},
            "feedback_by_option": {"opened": "card_opened"},
        }
    _register_mixed_interactions(
        _hub_id,
        _hub_slug,
        _hub_module.CONTENT["icebreaker"]["items"],
        required=False,
    )

for _card in _N4_CARDS:
    _interaction_id = f"{N4_HUB_NODE_ID}-CARD-{_card['id']}"
    _LESSONS[N4_HUB_NODE_ID]["interactions"].append(
        {
            "interaction_id": _interaction_id,
            "type": "single_select",
            "prompt_key": _card["concept"],
            "option_keys": ["opened"],
            "can_retry": False,
        }
    )
    _INTERACTION_RULES[_interaction_id] = {
        "node_id": N4_HUB_NODE_ID,
        "valid_options": {"opened"},
        "expected": "opened",
        "misconception_by_option": {},
        "feedback_by_option": {"opened": "card_opened"},
    }

_register_mixed_interactions(
    N4_HUB_NODE_ID, "puerto", _N4_HUB_CONTENT["icebreaker"]["items"], required=False
)
_register_mixed_interactions(
    N2_HUB_NODE_ID, "ciudad", _N2_HUB_CONTENT["icebreaker"]["items"], required=False
)
_register_mixed_interactions(
    N3_HUB_NODE_ID, "laboratorio", _N3_HUB_CONTENT["icebreaker"]["items"], required=False
)

# ---------------------------------------------------------------------------
# B06 — reconstrucción bajo la arquitectura de 11 bloques.
# Spec: Implementacion/specs/PREALG-N1-B06-RACIONALES-FRACCION-DIVISION.md
#
# Nodo piloto de la reestructuración: los bloques que no tenían slot en el
# renderer (diagnostic, katia.attempt, self_explanation, trampa completa,
# bridge, method_comparison, closing_item con Pólya, post_diagnostic) se cablean
# aquí con las claves del contrato de `implementation-mapping.md`, para que
# N2/N3/N4 las hereden sin renegociar nombres.
#
# El contenido vive en el dict (español), siguiendo el precedente de N2–N4
# (V2-R12/R13/R14) en vez del i18n del resto de N1: los componentes de bloque
# son compartidos por los 4 niveles y leen props, no claves de traducción.
# ---------------------------------------------------------------------------
# ── Nodos reconstruidos a 11 bloques ─────────────────────────────────────────
# El contenido vive en `nodes/`, un módulo por nodo. Enganchar uno nuevo es
# crear su módulo y listarlo en `nodes/__init__.py`: aquí no se toca nada.
#
# Solo la práctica y el ítem de cierre condicionan `node_completed`. El
# mini-diagnóstico, el puente y el post-diagnóstico son evaluables pero no
# bloquean: siembran ELO y guían, no califican.
for _node_module in NODE_MODULES:
    _node_id = _node_module.NODE_ID
    _slug = _node_module.CONCEPT_SLUG
    _content = _node_module.CONTENT

    # Las interacciones del molde viejo del nodo quedan retiradas.
    _prefix = "-".join(_node_id.split("-")[:3])
    for _rule_id in [k for k in _INTERACTION_RULES if k.startswith(f"{_prefix}-Q")]:
        _INTERACTION_RULES.pop(_rule_id, None)
    _LESSONS[_node_id]["content"] = _content
    _LESSONS[_node_id]["interactions"] = []

    _register_mixed_interactions(_node_id, _slug, _content.get("practice", []))
    if _content.get("closing_item"):
        _register_mixed_interactions(
            _node_id,
            _slug,
            [{**_content["closing_item"], "kind": "numeric"}],
        )
    for _optional_block in ("diagnostic", "post_diagnostic"):
        _items = (_content.get(_optional_block) or {}).get("items", [])
        _register_mixed_interactions(_node_id, _slug, _items, required=False)
    _register_mixed_interactions(
        _node_id,
        _slug,
        [
            {"id": _blank["id"], "kind": "numeric", "answer": _blank["answer"]}
            for _bridge_item in (_content.get("bridge") or {}).get("items", [])
            for _blank in _bridge_item["blanks"]
        ],
        required=False,
    )

DIAGNOSTIC_NODE_IDS = [
    NATURALS_NODE_ID,
    INTEGERS_NODE_ID,
    RATIONALS_NODE_ID,
    IRRATIONALS_NODE_ID,
    REALS_NODE_ID,
    COMPLEX_NODE_ID,
    CLASSIFIER_BASIC_NODE_ID,
    CLASSIFIER_RIGOROUS_NODE_ID,
    DETECTIVE_NODE_ID,
]

# Posición de cada nodo en la ruta. Sirve para ordenar recomendaciones de repaso
# sin que la lista de un solo nivel haga de índice global.
_ROUTE_POSITION = {_node_id: _i for _i, _node_id in enumerate(_LESSONS)}

# Presentación de cada nodo en el mapa: etiqueta, ítems visibles y clave i18n.
# Vive aquí, junto a la ruta, y no en el endpoint: añadir un nodo es añadir una
# fila (hay test que falla si falta). `label_key` solo existe donde hay
# traducción — N1; el resto va en español hasta cerrar la paridad i18n.
_MAP_PRESENTATION: dict[str, tuple[str, int, str | None]] = {
    WELCOME_NODE_ID: ("Bienvenida", 0, "prealgebra.n1.b01.mapTitle"),
    TRIGGER_NODE_ID: ("Pregunta detonadora", 2, "prealgebra.n1.b02.mapTitle"),
    STAIRCASE_NODE_ID: ("Escalera de la necesidad", 1, "prealgebra.n1.b03.mapTitle"),
    NATURALS_NODE_ID: ("Naturales", 4, "prealgebra.n1.b04.mapTitle"),
    INTEGERS_NODE_ID: ("Enteros", 4, "prealgebra.n1.b05.mapTitle"),
    RATIONALS_NODE_ID: ("Racionales", 3, "prealgebra.n1.b06.mapTitle"),
    IRRATIONALS_NODE_ID: ("Irracionales", 3, "prealgebra.n1.b07.mapTitle"),
    REALS_NODE_ID: ("Reales", 2, "prealgebra.n1.b08.mapTitle"),
    COMPLEX_NODE_ID: ("Complejos", 3, "prealgebra.n1.b09.mapTitle"),
    CLASSIFIER_BASIC_NODE_ID: ("El Clasificador I", 8, "prealgebra.n1.b10.mapTitle"),
    CLASSIFIER_RIGOROUS_NODE_ID: ("El Clasificador II", 8, "prealgebra.n1.b11.mapTitle"),
    DETECTIVE_NODE_ID: ("El Detective de Falsedades", 14, "prealgebra.n1.b12.mapTitle"),
    CLOSING_NODE_ID: ("Diagnóstico del nivel", 0, "prealgebra.n1.b13.mapTitle"),
    N2_HUB_NODE_ID: ("Nivel 2 · Ciudad de operaciones", 6, None),
    N2_SUM_NODE_ID: ("Nivel 2 · Suma", 1, None),
    N2_SUBTRACTION_NODE_ID: ("Nivel 2 · Resta", 1, None),
    N2_MULTIPLICATION_NODE_ID: ("Nivel 2 · Multiplicacion", 1, None),
    N2_DIVISION_NODE_ID: ("Nivel 2 · Division", 1, None),
    N2_EXPONENTIATION_NODE_ID: ("Nivel 2 · Potenciacion", 1, None),
    N2_RADICATION_NODE_ID: ("Nivel 2 · Radicacion", 1, None),
    N3_HUB_NODE_ID: ("Nivel 3 · Laboratorio de propiedades", 5, None),
    N3_COMMUTATIVE_NODE_ID: ("Nivel 3 · Conmutativa", 1, None),
    N3_ASSOCIATIVE_NODE_ID: ("Nivel 3 · Asociativa", 1, None),
    N3_DISTRIBUTIVE_NODE_ID: ("Nivel 3 · Distributiva", 1, None),
    N3_IDENTITY_NODE_ID: ("Nivel 3 · Elemento neutro", 1, None),
    N3_INVERSES_NODE_ID: ("Nivel 3 · Inversos", 1, None),
    N4_HUB_NODE_ID: ("Nivel 4 · El Puerto de la Polis", 9, None),
    N4_DIVISIBILITY_NODE_ID: ("Nivel 4 · Divisibilidad", 1, None),
    N4_MULTIPLES_NODE_ID: ("Nivel 4 · Múltiplos", 1, None),
    N4_PRIMES_NODE_ID: ("Nivel 4 · Números primos", 1, None),
    N4_FACTORIZATION_NODE_ID: ("Nivel 4 · Factorización prima", 1, None),
    N4_GCD_NODE_ID: ("Nivel 4 · Máximo común divisor", 1, None),
    N4_LCM_NODE_ID: ("Nivel 4 · Mínimo común múltiplo", 1, None),
    ALG_HUB_NODE_ID: ("Álgebra · El Papiro de las Cuatro Casas", 1, None),
    ALG_VARIABLES_NODE_ID: ("Álgebra · La sala de los cálamos", 1, None),
    ALG_CONSTANTS_NODE_ID: ("Álgebra · El estante sellado", 1, None),
    ALG_TRANSLATION_NODE_ID: ("Álgebra · La mesa de dictado", 1, None),
    ALG_NUMERIC_VALUE_NODE_ID: ("Álgebra · La cámara del recuento", 1, None),
    ALG_OPERATIONS_NODE_ID: ("Álgebra · La rampa", 1, None),
    ALG_SIGNS_NODE_ID: ("Álgebra · El patio de aparejos", 1, None),
    ALG_PRODUCT_NODE_ID: ("Álgebra · El taller de cinceles", 1, None),
    ALG_QUOTIENT_NODE_ID: ("Álgebra · La caseta del capataz", 1, None),
    ALG_FRACTIONS_NODE_ID: ("Álgebra · La parcela partida", 1, None),
    ALG_FRAC_SUM_NODE_ID: ("Álgebra · El canal madre", 1, None),
    ALG_FRAC_PRODUCT_NODE_ID: ("Álgebra · La era de trilla", 1, None),
    ALG_FRAC_DIVISION_NODE_ID: ("Álgebra · El silo de simiente", 1, None),
    ALG_RATIOS_NODE_ID: ("Álgebra · La cuadrícula del canon", 1, None),
    ALG_RULE_OF_THREE_NODE_ID: ("Álgebra · El tinte de lino", 1, None),
    ALG_PERCENT_NODE_ID: ("Álgebra · El pan de oro", 1, None),
    ALG_VARIATION_NODE_ID: ("Álgebra · La sala de las lámparas", 1, None),
    ALG_BAGDAD_HUB_NODE_ID: ("Álgebra · La Casa de la Sabiduría", 1, None),
    ALG_SQUARE_NODE_ID: ("Álgebra · La matriz cuadrada", 1, None),
    ALG_CONJUGATE_NODE_ID: ("Álgebra · El cuño de la cenefa", 1, None),
    ALG_CUBE_NODE_ID: ("Álgebra · El molde de tres capas", 1, None),
    ALG_COMMON_TERM_NODE_ID: ("Álgebra · La bandeja de parejas", 1, None),
    ALG_COMMON_FACTOR_NODE_ID: ("Álgebra · El pesaje de entrada", 1, None),
    ALG_SQUARES_NODE_ID: ("Álgebra · El cotejo de huellas", 1, None),
    ALG_TRINOMIAL_NODE_ID: ("Álgebra · La mesa de despiece", 1, None),
    ALG_CUBES_NODE_ID: ("Álgebra · La bodega de los toneles", 1, None),
    ALG_FULL_FACTOR_NODE_ID: ("Álgebra · La sala de expedición", 1, None),
}


def curriculum_map_rows(state_of, *, complex_visible: bool = True) -> list[dict]:
    """Los nodos del currículo para el mapa, con su estado.

    `state_of` es una función `node_id -> estado guardado`; el que llama decide
    de dónde sale (repositorio, caché, test). Aquí no se toca la base.

    El estado se deriva de `unlock_after`, que ya declara la ruta entera: un
    nodo se abre cuando su prerrequisito está completo, y de los abiertos sin
    completar el primero de la ruta es `current` y el resto `available`. Los
    desvíos opcionales —los complejos— nunca son `current`: están disponibles,
    pero no son el siguiente paso de nadie.
    """
    rows: list[dict] = []
    current_taken = False
    for node_id, lesson in _LESSONS.items():
        if node_id == COMPLEX_NODE_ID and not complex_visible:
            continue
        label, item_count, label_key = _MAP_PRESENTATION[node_id]
        prerequisite = lesson.get("unlock_after")
        unlocked = prerequisite is None or state_of(prerequisite) == "completed"
        if not unlocked:
            state = "blocked"
        elif state_of(node_id) == "completed":
            state = "completed"
        elif lesson["node_type"] == "optional_extension" or current_taken:
            state = "available"
        else:
            state, current_taken = "current", True
        rows.append(
            {
                "topic": lesson["topic"],
                "label": label,
                "label_key": label_key,
                "node_id": node_id,
                "node_type": lesson["node_type"],
                "elo": 0,
                "rd": 0,
                "item_count": item_count,
                "state": state,
            }
        )
    return rows


# Dónde se ENSEÑA cada error focal. Sale de los propios módulos: si un nodo lo
# declara como su `misconception`, esa es su pantalla de repaso. No hay que
# adivinarlo por palabras clave ni mantener una tabla aparte.
_FOCAL_NODE_BY_TAG = {
    _module.CONTENT["misconception"]: _module.NODE_ID
    for _module in NODE_MODULES
    if _module.CONTENT.get("misconception")
}

# Para los tags que solo existen como distractor: el nodo donde el motor puede
# emitirlos. Es el último recurso, pero cubre los ~300 que no son focales.
_NODE_BY_EMITTED_TAG: dict[str, str] = {}
for _rule in _INTERACTION_RULES.values():
    for _tag in list((_rule.get("misconception_by_option") or {}).values()) + [
        _rule.get("default_misconception")
    ]:
        if _tag:
            _NODE_BY_EMITTED_TAG.setdefault(_tag, _rule["node_id"])


def route_position(node_id: str) -> int:
    """Índice del nodo en la ruta; los desconocidos van al final."""
    return _ROUTE_POSITION.get(node_id, len(_ROUTE_POSITION))


def recommended_node_for_misconception(tag: str) -> str | None:
    """Ruta de repaso: mapea un misconception a la pantalla donde se trabaja.

    Tres pasos, del más fiable al menos:
      1. el nodo que declara ese error como focal — lo dice el propio contenido;
      2. las reglas por palabra clave de N1, que existen porque ahí hay tags que
         se emiten en un nodo y se enseñan en el siguiente (`no_enteros_en_enteros`
         aparece en Naturales y se trabaja en Enteros);
      3. el nodo donde el motor puede emitirlo, para los distractores sueltos.
    """
    if tag in _FOCAL_NODE_BY_TAG:
        return _FOCAL_NODE_BY_TAG[tag]
    t = tag.lower()
    if "natural" in t and any(k in t for k in ("cero", "negativ", "fraccion", "no_enteros")):
        return NATURALS_NODE_ID
    if any(k in t for k in ("equilibrio", "deuda", "abono")) or "no_enteros_en_enteros" in t:
        return INTEGERS_NODE_ID
    if any(
        k in t
        for k in (
            "numerador",
            "reparto",
            "fraccion_como_division",
            "decimal_desde_division",
            "enteros_no_son_racionales",
            "decimal_exacto_periodico",
        )
    ):
        return RATIONALS_NODE_ID
    if any(
        k in t
        for k in (
            "decimal_infinito",
            "periodico",
            "aproximacion",
            "pi_termina",
            "sqrt2",
            "irracional_como_real",
        )
    ):
        return IRRATIONALS_NODE_ID
    if any(
        k in t
        for k in (
            "irracionales_como_reales",
            "reales_con_racionales",
            "todo_real_es_racional",
            "inclusion_de_conjuntos",
            "complejos_en_recta_real",
        )
    ):
        return REALS_NODE_ID
    if any(
        k in t for k in ("imaginaria", "unidad_imaginaria", "parte_real", "complejos_no_reales")
    ):
        return COMPLEX_NODE_ID
    if any(
        k in t
        for k in (
            "conjunto_mas_especifico",
            "_dentro_de_",
            "reales_como_complejos",
            "imaginario_puro_con_irracional",
        )
    ):
        return CLASSIFIER_RIGOROUS_NODE_ID
    if t.startswith("clasifica_"):
        return CLASSIFIER_BASIC_NODE_ID
    if "implicacion" in t or "todo_complejo_es_real" in t:
        return DETECTIVE_NODE_ID
    return _NODE_BY_EMITTED_TAG.get(tag)


def get_lesson(node_id: str) -> dict | None:
    """Devuelve una copia del nodo para evitar mutar el catálogo global."""
    lesson = _LESSONS.get(node_id)
    return deepcopy(lesson) if lesson else None


def evaluate_interaction(node_id: str, interaction_id: str, selected_option: str) -> dict | None:
    """Evalúa una selección cerrada sin aceptar ni conservar texto libre."""
    rule = _INTERACTION_RULES.get(interaction_id)
    if not rule or rule["node_id"] != node_id:
        return None

    input_kind = rule.get("input_kind", "single_select")
    if input_kind == "numeric":
        raw_option = selected_option.strip().replace(" ", "").replace(".", ",").replace("−", "-")
        if not re.fullmatch(r"-?\d{1,6}(,\d{1,4})?", raw_option):
            return None
        selected_option = str(int(raw_option)) if "," not in raw_option else raw_option
        expected = str(rule["expected"]).replace(".", ",").replace("−", "-")
        is_expected = selected_option == expected
        return {
            "interaction_id": interaction_id,
            "selected_option": selected_option,
            "is_expected": is_expected,
            "misconception_tag": None if is_expected else rule["default_misconception"],
            "feedback_key": rule["feedback_by_result"][is_expected],
        }

    if input_kind == "text_exact":

        def _normalize_text_answer(value: str) -> str:
            normalized = value.strip().lower().replace(" ", "").replace("−", "-")
            normalized = re.sub(r"\\frac\{(-?\d{1,4})\}\{(\d{1,4})\}", r"\1/\2", normalized)
            normalized = normalized.replace("\\sqrt", "sqrt").replace("√", "sqrt")
            normalized = normalized.replace("·", "").replace("*", "")
            normalized = normalized.replace("²", "^2").replace("³", "^3")
            normalized = normalized.replace("{", "").replace("}", "")
            return normalized[1:] if normalized.startswith("+") else normalized

        raw_option = _normalize_text_answer(selected_option)
        # Los parentesis NO se borran: `2(c+2)` no es `2c+2`, y borrarlos daria por
        # buena una expresion distinta. Se rechazan en la puerta; si el autor quiere
        # admitir la forma factorizada, la declara en `accepted`.
        if not _TEXT_ANSWER_RE.fullmatch(raw_option):
            return None
        accepted = {rule["expected"], *rule.get("accepted", set())}
        expected_options = {_normalize_text_answer(str(option)) for option in accepted}
        selected_option = raw_option
        is_expected = selected_option in expected_options
        return {
            "interaction_id": interaction_id,
            "selected_option": selected_option,
            "is_expected": is_expected,
            "misconception_tag": None if is_expected else rule["default_misconception"],
            "feedback_key": rule["feedback_by_result"][is_expected],
        }

    if input_kind == "multi_select":
        selected = {part for part in selected_option.split(",") if part}
        if not selected or not selected.issubset(rule["valid_options"]):
            return None
        selected_option = ",".join(sorted(selected))
        is_expected = selected == rule["expected"]
        if "error_rules" in rule:
            # Multi-select genérico, dirigido por datos: primera regla que casa gana
            # (when_missing = falta marcar X; when_selected = marcó X de más).
            if is_expected:
                misconception, feedback = None, rule["feedback_correct"]
            else:
                misconception, feedback = None, rule["default_feedback"]
                for er in rule["error_rules"]:
                    miss, sel = er.get("when_missing"), er.get("when_selected")
                    if (miss and miss not in selected) or (sel and sel in selected):
                        misconception, feedback = er.get("misconception"), er["feedback"]
                        break
            return {
                "interaction_id": interaction_id,
                "selected_option": selected_option,
                "is_expected": is_expected,
                "misconception_tag": misconception,
                "feedback_key": feedback,
            }
        if "feedback_correct" in rule:
            # camino genérico con trampas: prioriza incluir un distractor "trampa"
            # sobre excluir un esperado (B08-Q02 y futuros nodos).
            if is_expected:
                misconception, feedback = None, rule["feedback_correct"]
            elif selected & rule.get("trap_options", set()):
                misconception = rule.get("misconception_trap")
                feedback = rule["feedback_trap"]
            elif rule["expected"] - selected:
                misconception = rule.get("misconception_missing")
                feedback = rule["feedback_missing"]
            else:
                misconception = rule.get("misconception_incorrect")
                feedback = rule["feedback_incorrect"]
            return {
                "interaction_id": interaction_id,
                "selected_option": selected_option,
                "is_expected": is_expected,
                "misconception_tag": misconception,
                "feedback_key": feedback,
            }
        if is_expected:
            misconception = None
            feedback = "naturals_correct"
        elif "zero" not in selected:
            misconception = "excluye_cero_de_naturales_pese_a_convencion"
            feedback = "zero_is_natural"
        elif "negative_two" in selected:
            misconception = "incluye_negativos_en_naturales"
            feedback = "negatives_are_not_natural"
        elif "sqrt_two" in selected:
            misconception = "incluye_no_enteros_en_naturales"
            feedback = "irrationals_not_natural"
        elif "decimal_25" in selected:
            misconception = "incluye_fracciones_en_naturales"
            feedback = "decimals_not_natural"
        else:
            misconception = None
            feedback = "naturals_review"
        return {
            "interaction_id": interaction_id,
            "selected_option": selected_option,
            "is_expected": is_expected,
            "misconception_tag": misconception,
            "feedback_key": feedback,
        }

    if selected_option not in rule["valid_options"]:
        return None
    expected = rule["expected"]
    # default_feedback cubre combinaciones no documentadas (p. ej. clasificador:
    # cualquier zona equivocada sin retro específica cae al mensaje genérico).
    feedback_key = rule["feedback_by_option"].get(selected_option) or rule.get("default_feedback")
    return {
        "interaction_id": interaction_id,
        "selected_option": selected_option,
        "is_expected": None if expected is None else selected_option == expected,
        "misconception_tag": rule["misconception_by_option"].get(selected_option),
        "feedback_key": feedback_key,
    }


def presentation_band(score_pct: float | None) -> str:
    """Traduce los cortes provisionales del diagnóstico a presentación.

    Los cortes son deliberadamente centralizados y deberán recalibrarse con el
    piloto. No afectan el ELO ni la ubicación del estudiante.
    """
    score = float(score_pct or 0.0)
    if score >= 80.0:
        return "avanzado"
    if score >= 50.0:
        return "intermedio"
    return "basico"
