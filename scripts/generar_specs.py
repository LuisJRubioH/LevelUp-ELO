"""Genera la spec en Markdown de cada nodo de 11 bloques a partir de su módulo.

El contenido pedagógico ya vive en `src/domain/learning/nodes/`. Esto lo saca a
un documento legible sin Python, que es lo que faltaba de la fase 1 del flujo.

Lo que NO se puede derivar del código queda como hueco marcado `PENDIENTE`:
la ficha curricular (DBA/ICFES), las citas y las notas de handoff a Design.
Esas tres se escriben a mano, una vez, sobre el archivo generado.

    python scripts/generar_specs.py

ponytail: regenerar pisa el archivo entero. Si alguien rellena los huecos a
mano, mover la spec fuera de `specs/generadas/` antes de volver a correrlo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.domain.learning.nodes import NODE_MODULES  # noqa: E402
from src.domain.learning.prealgebra import _INTERACTION_RULES, _LESSONS  # noqa: E402

DESTINO = ROOT / "Implementacion" / "specs" / "generadas"
PENDIENTE = "> **PENDIENTE — se escribe a mano.** No es derivable del código."


def opciones(item: dict) -> list[str]:
    """Opciones de un ítem cerrado, marcando la esperada y el error de cada una."""
    esperado = item.get("expected")
    esperados = esperado if isinstance(esperado, list) else [esperado]
    errores = item.get("misconception_by_option") or {}
    filas = []
    for opcion in item.get("options", []):
        marca = "✅" if opcion["id"] in esperados else "　"
        error = errores.get(opcion["id"])
        filas.append(
            f"| {marca} | `{opcion['id']}` | "
            f"{opcion.get('text') or opcion.get('label') or opcion.get('katex', '')} | "
            f"{'`' + error + '`' if error else '—'} |"
        )
    if not filas:
        return []
    return ["", "| | id | Texto | Error que delata |", "|---|---|---|---|", *filas]


def item(item: dict, titulo: str = "") -> list[str]:
    """Un ítem evaluable: enunciado, tipo, opciones, respuesta y escalera."""
    encabezado = f"**{item.get('id', '?')}**"
    if titulo:
        encabezado += f" · {titulo}"
    if item.get("presentation"):
        encabezado += f" · *nivel {item['presentation']}*"
    lineas = [encabezado, "", item.get("prompt") or item.get("statement") or ""]
    if item.get("statement") and item.get("prompt"):
        lineas.append(item["prompt"])
    lineas += opciones(item)
    if item.get("answer") is not None:
        lineas += ["", f"Respuesta: `{item['answer']}`"]
    if item.get("accepted"):
        lineas.append(f"También válidas: {', '.join('`' + a + '`' for a in item['accepted'])}")
    escalera = item.get("hints") or {}
    if escalera:
        lineas += ["", "Escalera de pistas:"]
        lineas += [
            f"{n}. {escalera[k]}" for n, k in enumerate(("n1", "n2", "n3"), 1) if k in escalera
        ]
    if item.get("polya"):
        lineas += ["", "Pólya: " + " → ".join(item["polya"])]
    return lineas + [""]


def bloque(titulo: str, cuerpo: list[str]) -> list[str]:
    return [f"### {titulo}", ""] + cuerpo + [""]


def spec(modulo) -> str:
    contenido = modulo.CONTENT
    leccion = _LESSONS[modulo.NODE_ID]
    reglas = {k: v for k, v in _INTERACTION_RULES.items() if v["node_id"] == modulo.NODE_ID}

    salida = [
        f"# Nodo: {contenido['title']} — {modulo.NODE_ID}",
        "",
        "*Generado desde el módulo por `scripts/generar_specs.py`. "
        "Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*",
        "",
        "## A0. Ficha del nodo",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| `node_id` | `{modulo.NODE_ID}` |",
        f"| `concept_slug` | `{modulo.CONCEPT_SLUG}` |",
        f"| Error focal | `{contenido.get('misconception', '—')}` |",
        f"| Sala / edificio | {contenido.get('house') or contenido.get('building') or contenido.get('station') or contenido.get('destination') or '—'} |",
        f"| Guía | {contenido.get('guide', 'KatIA')} |",
        f"| Entra después de | `{leccion.get('unlock_after') or '— (primer nodo)'}` |",
        f"| Mueve ELO | {'sí' if leccion.get('affects_elo') else 'no'} |",
        f"| Ítems: diagnóstico / práctica / post | "
        f"{len((contenido.get('diagnostic') or {}).get('items', []))} / "
        f"{len(contenido.get('practice', []))} / "
        f"{len((contenido.get('post_diagnostic') or {}).get('items', []))} |",
        "",
        "**Estándares (DBA / ICFES / grado) y tiempo estimado:**",
        "",
        PENDIENTE,
        "",
        "---",
        "",
        "## PARTE A — Especificación por bloques",
        "",
    ]

    salida += bloque(
        "A1. Encabezado",
        [
            f"**Kicker:** {contenido.get('kicker', '—')}",
            "",
            f"**Título:** {contenido['title']}",
            "",
            contenido.get("intro", ""),
            "",
            f"**Escena:** {(contenido.get('scene') or {}).get('aria', '— (nodo sin peldaño)')}",
        ],
    )

    diagnostico = contenido.get("diagnostic") or {}
    if diagnostico:
        cuerpo = [diagnostico.get("intro", ""), ""]
        for elemento in diagnostico.get("items", []):
            cuerpo += item(elemento)
        cuerpo.append("*No corrige: es la línea base del post-diagnóstico.*")
        salida += bloque("A2. Mini-diagnóstico", cuerpo)

    katia = contenido.get("katia") or {}
    intento = katia.get("attempt") or {}
    salida += bloque(
        "A3. Apertura de KatIA — intento genuino",
        [
            f"*{katia.get('eyebrow', '')}* — **{katia.get('title', '')}**",
            "",
            katia.get("body", ""),
            "",
            f"**Pregunta:** {katia.get('question', '')}",
            "",
            f"**Intento genuino** (`{intento.get('format', '—')}`): {intento.get('prompt', '')}",
        ]
        + opciones(intento),
    )

    descubrimiento = contenido.get("discovery") or {}
    cuerpo = [
        f"*{descubrimiento.get('eyebrow', '')}* — **{descubrimiento.get('title', '')}**",
        "",
        descubrimiento.get("body", ""),
        "",
    ]
    for caso in descubrimiento.get("cases", []):
        cuerpo += [f"- **{caso.get('label', '')}** — {caso.get('note', '')}"]
    cuerpo += [
        "",
        f"**Resolución:** {descubrimiento.get('resolution', '')}",
        "",
        f"**Definición — {contenido.get('definition_title', '')}**",
        "",
        f"$${contenido.get('definition_katex', '')}$$",
        "",
        contenido.get("definition", ""),
    ]
    simbolos = contenido.get("definition_symbols") or []
    if simbolos:
        cuerpo += ["", "| Símbolo | Se lee | Significa |", "|---|---|---|"] + [
            f"| `{s.get('symbol', '')}` | {s.get('reads', '')} | {s.get('means', '')} |"
            for s in simbolos
        ]
    salida += bloque("A4. Descubrimiento guiado + definición formal", cuerpo)

    cuerpo = []
    for tarjeta in contenido.get("worked_examples", []):
        etiqueta = "TRAMPA" if tarjeta.get("trap") else "resuelto"
        cuerpo += [f"#### {tarjeta.get('title', '')} · *{etiqueta}*", ""]
        cuerpo += [tarjeta.get("statement", ""), ""]
        for paso in tarjeta.get("steps", []):
            if isinstance(paso, str):
                cuerpo.append(f"- {paso}")
            else:
                cuerpo.append(
                    f"- {paso.get('label', '')}: "
                    f"{paso.get('detail') or paso.get('katex') or paso.get('text', '')}"
                )
        if tarjeta.get("self_explanation"):
            cuerpo += ["", f"**Autoexplicación (focal):** {tarjeta['self_explanation']}"]
        if tarjeta.get("trap"):
            cuerpo += [
                "",
                f"**Confianza:** {tarjeta.get('confidence_prompt', '')}",
                f"**Versión correcta:** {tarjeta.get('correct_version', '')}",
                f"**¿Por qué falla?:** {tarjeta.get('explain_prompt', '')}",
            ]
        cuerpo.append("")
    salida += bloque("A5. Ejemplos resueltos", cuerpo)

    puente = contenido.get("bridge") or {}
    if puente:
        cuerpo = [puente.get("intro", ""), ""]
        for elemento in puente.get("items", []):
            cuerpo += [
                f"**{elemento['id']}** (*falta: {elemento.get('missing', '?')}*) — {elemento.get('statement', '')}",
                "",
            ]
            for paso in elemento.get("given_steps", []):
                cuerpo.append(f"- dado: ${paso}$")
            for hueco in elemento.get("blanks", []):
                cuerpo.append(
                    f"- hueco `{hueco['id']}`: ${hueco.get('label', '')}$ → `{hueco['answer']}`"
                )
            cuerpo.append("")
        salida += bloque("A6. Puente — parcialmente resueltos", cuerpo)

    comparacion = contenido.get("method_comparison") or {}
    if comparacion:
        cuerpo = [f"**{comparacion.get('title', '')}**", "", comparacion.get("intro", ""), ""]
        for metodo in comparacion.get("methods", []):
            cuerpo += [
                f"- **{metodo.get('label', '')}** — {metodo.get('body', metodo.get('summary', ''))}"
            ]
        cuerpo += [
            "",
            f"**Pregunta:** {comparacion.get('question', '')}",
            "",
            f"**Insight:** {comparacion.get('insight', '')}",
        ]
        salida += bloque("A7. Comparación de métodos", cuerpo)

    cuerpo = []
    for elemento in contenido.get("practice", []):
        cuerpo += item(elemento)
    salida += bloque(
        f"A8. Práctica independiente ({len(contenido.get('practice', []))} ítems)", cuerpo
    )

    cierre = contenido.get("closure") or {}
    cuerpo = [
        f"*{cierre.get('eyebrow', '')}* — **{cierre.get('title', '')}**",
        "",
        cierre.get("intro", ""),
        "",
        "| Fila | ¿Cumple? | Nota |",
        "|---|---|---|",
    ]
    for fila in cierre.get("rows", []):
        marca = {"yes": "✅", "no": "✗", "partial": "~ (ámbar)"}.get(fila.get("closed"), "?")
        cuerpo.append(f"| {fila.get('label', '')} | {marca} | {fila.get('note', '')} |")
    cuerpo += ["", cierre.get("outro", "")]

    abstraccion = contenido.get("abstraction_question") or {}
    if abstraccion:
        cuerpo += ["", "#### Pregunta de abstracción", "", abstraccion.get("prompt", "")]
        cuerpo += opciones(abstraccion)
    if contenido.get("closing_item"):
        cuerpo += ["", "#### Ítem final con protocolo de Pólya", ""]
        cuerpo += item(contenido["closing_item"])
    salida += bloque("A9. Cierre", cuerpo)

    post = contenido.get("post_diagnostic") or {}
    if post:
        cuerpo = [
            f"Compara con: `{post.get('compara_con', '')}`",
            "",
            post.get("intro", ""),
            "",
            f"- **Mejoró:** {post.get('outcome_gain', '')}",
            f"- **Igual:** {post.get('outcome_flat', '')}",
            "",
        ]
        for elemento in post.get("items", []):
            cuerpo += item(elemento)
        pie = contenido.get("footer") or {}
        cuerpo += [f"**Footer:** {pie.get('label', '')} — {pie.get('note', '')}"]
        salida += bloque("A10. Post-diagnóstico y footer", cuerpo)

    cuerpo = ["| Interacción | Opción | Tag | Feedback |", "|---|---|---|---|"]
    retro = contenido.get("feedback") or {}
    for id_regla, regla in sorted(reglas.items()):
        for id_opcion, tag in (regla.get("misconception_by_option") or {}).items():
            texto = retro.get(tag) or retro.get("default", "—")
            cuerpo.append(f"| `{id_regla}` | `{id_opcion}` | `{tag}` | {texto[:120]} |")
    salida += bloque("A12. Misconceptions → feedback", cuerpo)

    salida += bloque(
        "A13. Notas de citas", [PENDIENTE, "", "Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`."]
    )
    salida += bloque(
        "A14. Notas de handoff a Design",
        [
            PENDIENTE,
            "",
            f"Imagen de apertura declarada: `{(contenido.get('katia') or {}).get('image', '— falta')}`",
            "",
            "Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` "
            "(genérico, 5 zonas de color).",
        ],
    )

    return "\n".join(salida).rstrip() + "\n"


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    once_bloques = [m for m in NODE_MODULES if m.CONTENT.get("kind") == "eleven_block_node"]
    for modulo in once_bloques:
        (DESTINO / f"{modulo.NODE_ID}.md").write_text(spec(modulo), encoding="utf-8")
    print(f"{len(once_bloques)} specs escritas en {DESTINO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
